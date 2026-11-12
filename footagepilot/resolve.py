"""Portable Resolve console jobs. No daemon, credentials or unsafe Lua filesystem access."""
import hashlib
import copy
import json
import math
import array
import subprocess
import sys
import uuid
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from .__main__ import binary, probe, run, write
from .edits import validate_edit
from .layout import rectangle,validate_panels
from .music_timing import marker_times


def lua(value):
    """Serialize data, including hostile filenames, without producing executable source."""
    if isinstance(value, str):
        return '"'+''.join(chr(b) if 32 <= b < 127 and b not in (34,92) else '\\%03d'%b for b in value.encode())+'"'
    if value is None:return 'nil'
    if type(value) is bool:return 'true' if value else 'false'
    if type(value) in (int,float) and math.isfinite(value):return str(value)
    if isinstance(value,list):return '{'+','.join(lua(v) for v in value)+'}'
    if isinstance(value,dict):return '{'+','.join('['+lua(k)+']='+lua(v) for k,v in value.items())+'}'
    raise ValueError('Unsupported Lua data')


def console_program(source):
    # Fusion's single-line input must not turn a leading comment into the entire program.
    return ' '.join(line.strip() for line in source.splitlines() if line.strip() and not line.lstrip().startswith('--'))


def prepare(manifest, output, render=False):
    """Prepare sources; native Resolve constructs cuts, layers, Text+ and dissolves."""
    import re
    from .learning import check_sources
    registry=Path(__file__).resolve().parent.parent/'docs/resolve/sources.json'
    if not registry.exists() or check_sources(registry)['needs_research']:raise ValueError('Resolve research is missing or stale; review official guides and installed API before preparing a job')
    snapshot=manifest.read_bytes();data=json.loads(snapshot);validate_edit(data,manifest.parent)
    if output.exists():raise ValueError('Use a fresh Resolve job directory')
    fps=data.get('fps',30);w,h={'9:16':(1080,1920),'16:9':(1920,1080),'1:1':(1080,1080),'4:5':(1080,1350)}[data.get('aspect','9:16')]
    def frames(seconds):return int((Decimal(str(seconds))*fps).quantize(Decimal(1),rounding=ROUND_HALF_UP))
    def layer_frames(row):return frames(Decimal(str(row.get('start',0)))+Decimal(str(row['duration'])))-frames(row.get('start',0))
    validate_panels(data.get('overlays',[]))
    validate_panels([{**r,'start':frames(r['start']),'duration':layer_frames(r)} for r in data.get('overlays',[])])
    for row in data['shots']:
        if row.get('scale',1)!=1 or row.get('x',.5)!=.5 or row.get('y',.5)!=.5:raise ValueError('Main shots must use full-frame placement; use collage overlays for positioned panels')
    if len(data.get('titles',[]))>16:raise ValueError('Use at most sixteen native titles')
    for title in data.get('titles',[]):
        if type(title.get('size',28)) not in (int,float) or not math.isfinite(title.get('size',28)) or not 8<=title.get('size',28)<=72:raise ValueError('Title size must be 8–72 logical units')
        if not isinstance(title.get('font','Helvetica Neue'),str) or not 0<len(title.get('font','Helvetica Neue'))<=80 or type(title.get('bold',False)) is not bool:raise ValueError('Title font/bold values are invalid')
        if not re.fullmatch(r'#[0-9a-fA-F]{6}',title.get('color','#FFFFFF')):raise ValueError('Title colour must be RGB hex')
        if any(type(title.get(k,.5)) not in (int,float) or not math.isfinite(title.get(k,.5)) or not 0<=title.get(k,.5)<=1 for k in ('x','y')):raise ValueError('Title position must be 0–1')
    for transition in data.get('transitions',[]):
        if transition.get('filter','transition_dissolve') not in ('transition_dissolve','transition_wipe_left','transition_moving_dissolve') or frames(transition.get('duration',.2))<2:raise ValueError('Resolve supports dissolve/wipe-left/moving-dissolve transitions of at least two frames')
    shots=[];cursor=0;inputs={};pending=[];elapsed=Decimal(0)
    def source(row,count,target,panel=False):
        path=(manifest.parent/row['path']).resolve();inputs[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
        meta=probe(path);video=next((s for s in meta['streams'] if s['codec_type']=='video'),None)
        if not video:raise ValueError('Shot has no video stream')
        still=path.suffix.lower() in ('.jpg','.jpeg','.png','.webp')
        source_start=row.get('source_start',0)
        if still and source_start:raise ValueError('Still images cannot have a nonzero source start')
        if not still and float(video.get('duration') or meta['format']['duration'])+.5/fps<source_start+count/fps:raise ValueError('Video source range exceeds available duration')
        fit=row.get('fit','fill');zoom=row.get('zoom',0)
        rw=max(2,round(w*row.get('width',row.get('scale',1))/2)*2) if panel else w
        rh=max(2,round(h*row.get('height',row.get('scale',1))/2)*2) if panel else h
        if fit=='contain' and zoom:raise ValueError('Contain with zoom is not supported by Resolve preparation')
        if fit=='fill':filt=f"scale={rw}:{rh}:force_original_aspect_ratio=increase,crop={rw}:{rh}:'max(0,min(iw-ow,iw*{row.get('focus_x',.5)}-ow/2))':'max(0,min(ih-oh,ih*{row.get('focus_y',.5)}-oh/2))'"
        else:filt=f'scale={rw}:{rh}:force_original_aspect_ratio=decrease,pad={rw}:{rh}:(ow-iw)/2:(oh-ih)/2:black'
        if panel:filt+=f',scale={w}:{h},setsar=1'
        if zoom:filt+=f",zoompan=z='1+{zoom}*on/{max(1,count-1)}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={w}x{h}:fps={fps}"
        pending.append([binary('ffmpeg'),'-v','error','-n']+(['-loop','1'] if still else ['-ss',source_start])+['-i',path,'-an','-vf',filt+',setpts=PTS-STARTPTS','-r',fps,'-frames:v',count,'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',target])
        return str(target)
    for i,row in enumerate(data['shots']):
        elapsed+=Decimal(str(row['duration']));end=int((elapsed*fps).quantize(Decimal(1),rounding=ROUND_HALF_UP));count=end-cursor
        if count<1:raise ValueError('Shot rounds below one frame')
        shots.append({'path':source(row,count,output/f'shot-{i+1:03d}.mp4'),'start':cursor,'frames':count,'source_start':row.get('source_start',0),'source_path':str((manifest.parent/row['path']).resolve())});cursor=end
    overlays=[]
    for i,row in enumerate(data.get('overlays',[])):
        count=layer_frames(row)
        if frames(row['start'])+count>cursor:raise ValueError('Rounded collage exceeds timeline')
        overlays.append({'path':source(row,count,output/f'panel-{i+1:03d}.mp4',panel=True),'start':frames(row['start']),'frames':count,'x':row['x'],'y':row['y'],'width':row.get('width',row.get('scale',1)),'height':row.get('height',row.get('scale',1))})
    backgrounds=[]
    if len(data.get('layout_backgrounds',[]))>24:raise ValueError('Use at most 24 layout backgrounds')
    for i,row in enumerate(data.get('layout_backgrounds',[])):
        start,count=frames(row['start']),layer_frames(row)
        if row.get('color','#000000')!='#000000' or count<1 or start<0 or start+count>cursor:raise ValueError('Layout background must be black and fit the timeline')
        target=output/f'layout-background-{i+1:03d}.mp4'
        pending.append([binary('ffmpeg'),'-v','error','-n','-f','lavfi','-i',f'color=black:s={w}x{h}:r={fps}','-an','-frames:v',count,'-c:v','libx264','-pix_fmt','yuv420p',target])
        backgrounds.append({'path':str(target),'start':start,'frames':count})
    transitions=[]
    for i,row in enumerate(data.get('transitions',[])):
        incoming=shots[row['after_shot']+1];count=frames(row.get('duration',.2));target=output/f'dissolve-{i+1:03d}.mp4'
        extra={}
        if row.get('filter')=='transition_moving_dissolve':
            original=data['shots'][row['after_shot']+1];path=(manifest.parent/original['path']).resolve()
            handle=float(Decimal(str(original.get('source_start',0)))-Decimal(count)/fps)
            if path.suffix.lower() in ('.jpg','.jpeg','.png','.webp') or original.get('zoom',0) or handle<0:raise ValueError('Moving dissolve needs an incoming video without artificial zoom and sufficient pre-cut source handles')
            source({**original,'source_start':handle},count,target)
            extra={'source_start':handle,'source_path':str(path),'continuity':'pre-cut source frames continue into unchanged main excerpt'}
        else:pending.append([binary('ffmpeg'),'-v','error','-n','-i',incoming['path'],'-an','-vf',f'trim=end_frame=1,loop=-1:1:0,setpts=N/({fps}*TB)','-r',fps,'-frames:v',count,'-c:v','libx264','-crf','18','-pix_fmt','yuv420p',target])
        transitions.append({'path':str(target),'start':incoming['start']-count,'frames':count,'after_shot':row['after_shot'],'filter':row.get('filter','transition_dissolve'),**extra})
    plates=[]
    for i,row in enumerate(data.get('plates',[])):
        start,count=frames(row.get('start',0)),layer_frames(row)
        if count<1 or start+count>cursor:raise ValueError('Rounded plate exceeds timeline')
        plates.append({'path':source(row,count,output/f'plate-{i+1:03d}.mp4'),'start':start,'frames':count,'blend':'screen','opacity':row.get('opacity',1)})
    titles=[]
    for i,row in enumerate(data.get('titles',[])):
        count=layer_frames(row)
        if frames(row.get('start',0))+count>cursor:raise ValueError('Rounded title exceeds timeline')
        target=output/f'title-carrier-{i+1:03d}.mp4'
        pending.append([binary('ffmpeg'),'-v','error','-n','-f','lavfi','-i',f'color=black:s={w}x{h}:r={fps}','-an','-frames:v',count,'-c:v','libx264','-pix_fmt','yuv420p',target])
        colour=row.get('color','#FFFFFF');titles.append({'path':str(target),'start':frames(row.get('start',0)),'frames':count,'text':row['text'],'size':row.get('size',28),'x':row.get('x',.5),'y':row.get('y',.5),'font':row.get('font','Helvetica Neue'),'bold':row.get('bold',False),'color':[int(colour[n:n+2],16)/255 for n in (1,3,5)]})
    music=None
    if data.get('music'):
        path=(manifest.parent/data['music']).resolve();inputs[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
        if float(probe(path)['format']['duration'])+.5/fps<cursor/fps:raise ValueError('Music is shorter than timeline')
        music=output/'music.wav';pending.append([binary('ffmpeg'),'-v','error','-n','-i',path,'-t',cursor/fps,'-af',f'volume={data.get("music_gain",.65)},afade=t=in:d=0.1,afade=t=out:st={max(0,cursor/fps-.3)}:d=0.3','-c:a','pcm_s16le',music])
    output.mkdir(parents=True)
    job={'project_name':'FootagePilot-'+output.name[:32]+'-'+uuid.uuid4().hex[:8],'schema_version':2,'status':'prepared-not-executed','fps':fps,'width':w,'height':h,'frames':cursor,'shots':shots,'overlays':overlays,'plates':plates,'backgrounds':backgrounds,'titles':titles,'transitions':transitions,'music':str(music) if music else None,'beats':[],'inputs':inputs,'manifest_sha256':hashlib.sha256(snapshot).hexdigest(),'limits':['Source crop/zoom and audio gain/fades are prepared per clip. Resolve constructs editable layers, Text+ and animated-opacity dissolves or rectangle-mask reveals.','Panel proxies are reframed to box aspect then normalized to the canvas; native independent-axis scaling restores their intended proportions.','Transition begins before the cut and reaches full incoming image on the last pre-cut frame. Moving dissolve uses source handles; legacy dissolve/wipe pre-roll freezes its first frame.','Screen plates are full-canvas black-backed layers above transitions and below titles; list order defines stacked blending. Native enum 5 was calibrated on Resolve 21.2 only.','Preparing a job does not prove native execution or creative acceptance.']}
    timing=data.get('music_timing')
    if timing:
        job['beats']=sorted({frames(t) for t in marker_times(timing,float(elapsed))})
        job['timing_mode']=timing.get('mode','authored_grid')
        job['timing_label']='Audio onset candidates; not verified beats or a listening verdict' if timing.get('mode')=='onset_candidates' else 'Supplied timing coordinates; not a listening verdict'
        job['timing_provenance']=timing['provenance']
    try:
        for cmd in pending:run(cmd)
        for path,digest in inputs.items():
            if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=digest:raise ValueError('Source changed during preparation')
        if manifest.read_bytes()!=snapshot:raise ValueError('Manifest changed during preparation')
        paths=[Path(s['path']) for group in (shots,overlays,backgrounds,titles,transitions,plates) for s in group]+([music] if music else [])
        job['prepared_hashes']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths};write(output/'job.json',job)
        template=(Path(__file__).parent/'resolve_job.lua').read_text();payload={k:job[k] for k in ('fps','width','height','frames','shots','music','beats','overlays','titles','transitions','backgrounds','plates')}
        payload.update(timing_label=job.get('timing_label'),name=job['project_name'],target=str(output),custom_name='resolve-output',render=render)
        (output/'console.lua').write_text('do local cfg='+lua(payload)+'; '+console_program(template)+' end\n');(output/'render.lua').write_text(console_program((Path(__file__).parent/'resolve_render.lua').read_text())+'\n')
        return {'job':str(output/'job.json'),'console':str(output/'console.lua'),'status':job['status'],'next':'Run console.lua inside Resolve; inspect native queue/output and run resolve-verify. Native render requested.' if render else 'Run console.lua inside Resolve, inspect, then run render.lua and resolve-verify.'}
    except Exception as error:
        write(output/'failure.json',{'stage':'prepare','error':str(error)});raise


def similarity(expected, actual):
    if len(expected)!=len(actual) or not expected:raise ValueError('Incomparable media samples')
    left=sum(expected)/len(expected);right=sum(actual)/len(actual)
    xx=sum((x-left)**2 for x in expected);yy=sum((y-right)**2 for y in actual)
    mae=sum(abs(a-b) for a,b in zip(expected,actual))/len(expected)
    correlation=sum((a-left)*(b-right) for a,b in zip(expected,actual))/math.sqrt(xx*yy) if xx*yy>1e-15 else (1. if mae<1e-6 else 0.)
    return mae,correlation


def raw(command):
    result=subprocess.run([str(x) for x in command],capture_output=True)
    if result.returncode:raise ValueError(result.stderr.decode(errors='replace')[-2000:] or f'Media command exited with status {result.returncode}')
    return result.stdout


def sample_frame(path, number, fps, width=64, height=64):
    # Tiny RGB panel scaling exposed nondeterministic pixels/allocator aborts in
    # the tested ARM64 FFmpeg build. Use its scalar path for bounded QA samples.
    data=raw([binary('ffmpeg'),'-v','error','-cpuflags','0','-ss',number/fps,'-i',path,'-frames:v','1','-vf',f'scale={width}:{height},format=rgb24','-f','rawvideo','-'])
    if len(data)!=width*height*3:raise ValueError('Missing verification frame')
    return [v/255 for v in data]


def expected_frame(job, number, width=64, height=64):
    """Independent RGB compositor for QA only; never used as a delivered movie."""
    shot=next(s for s in job['shots'] if s['start']<=number<s['start']+s['frames'])
    result=sample_frame(shot['path'],number-shot['start'],job['fps'],width,height)
    for row in job.get('backgrounds',[]):
        if row['start']<=number<row['start']+row['frames']:result=[0.]*(width*height*3)
    for row in job.get('overlays',[]):
        if row['start']<=number<row['start']+row['frames']:
            left,top,right,bottom=rectangle(row);x,y=round(left*width),round(top*height);pw,ph=round(right*width)-x,round(bottom*height)-y
            panel=sample_frame(row['path'],number-row['start'],job['fps'],pw,ph)
            for yy in range(ph):result[((y+yy)*width+x)*3:((y+yy)*width+x+pw)*3]=panel[yy*pw*3:(yy+1)*pw*3]
    for row in job.get('transitions',[]):
        if row['start']<=number<row['start']+row['frames']:
            alpha=(number-row['start'])/(row['frames']-1);incoming=sample_frame(row['path'],number-row['start'],job['fps'],width,height)
            if row.get('filter','transition_dissolve')=='transition_wipe_left':
                result=[incoming[i] if (i//3)%width<alpha*width else v for i,v in enumerate(result)]
            else:result=[a*(1-alpha)+b*alpha for a,b in zip(result,incoming)]
    for row in job.get('plates',[]):
        if row['start']<=number<row['start']+row['frames']:
            if row['blend']!='screen':raise ValueError('Unsupported plate blend in job')
            plate=sample_frame(row['path'],number-row['start'],job['fps'],width,height)
            opacity=row['opacity']
            result=[a+opacity*b*(1-a) for a,b in zip(result,plate)]
    return result


def plate_matches(job, media):
    """Check changed pixels, so a subtle missing plate cannot hide in the whole frame."""
    rows=[];resolution=128
    for index,plate in enumerate(job.get('plates',[])):
        control=copy.deepcopy(job);control['plates'].pop(index);checked=0
        numbers={plate['start']+round((plate['frames']-1)*f) for f in (.25,.5,.75)}
        for number in sorted(numbers):
            expected=expected_frame(job,number,resolution,resolution)
            absent=expected_frame(control,number,resolution,resolution)
            bands=title_band(job,number,resolution)
            keep=[i for i,(a,b) in enumerate(zip(expected,absent)) if a-b>.02 and not any(lo<=(i//3)//resolution<=hi for lo,hi in bands)]
            if len(keep)<64:continue
            strength=sum(expected[i]-absent[i] for i in keep)/len(keep)
            actual=sample_frame(media,number,job['fps'],resolution,resolution)
            mae,corr=similarity([expected[i] for i in keep],[actual[i] for i in keep])
            limit=min(.08,max(.015,strength*.5))
            if mae>limit or corr<.90:raise ValueError(f'Screen plate {index+1} differs in its active pixels at frame {number}')
            rows.append({'plate':index+1,'frame':number,'active_channels':len(keep),'expected_contribution':strength,
                         'mean_absolute_error':mae,'maximum_error':limit,'correlation':corr})
            checked+=1
        if not checked:raise ValueError(f'Screen plate {index+1} has insufficient distinguishable pixels for verification')
    return rows


def title_band(job, number, height):
    bands=[]
    for t in job.get('titles',[]):
        if t['start']<=number<t['start']+t['frames']:
            centre=t['y']*height;radius=max(2,3*t['size']/job['height']*height)
            bands.append((centre-radius,centre+radius))
    return bands


def visual_matches(job, media):
    rows=[];samples=set()
    for shot in job['shots']:
        samples.update(shot['start']+n for n in {min(1,shot['frames']-1),shot['frames']//2,max(0,shot['frames']-2)})
    for row in job.get('overlays',[])+job.get('transitions',[])+job.get('backgrounds',[])+job.get('plates',[]):
        samples.update(row['start']+round((row['frames']-1)*fraction) for fraction in (0,.25,.5,.75,1))
    for number in sorted(samples):
        expected=expected_frame(job,number);actual=sample_frame(media,number,job['fps']);bands=title_band(job,number,64)
        keep=[i for i in range(len(actual)) if not any(lo<=(i//3)//64<=hi for lo,hi in bands)]
        mae,corr=similarity([expected[i] for i in keep],[actual[i] for i in keep])
        rows.append({'frame':number,'mean_absolute_error':round(mae,5),'correlation':round(corr,5)})
        if mae>.08 or corr<.90:raise ValueError(f'Export differs visually from prepared composition at frame {number}; inspect offline media, order, layout, transition and colour')
    for index,row in enumerate(job.get('overlays',[])):
        resolution=256
        number=row['start']+row['frames']//2;actual=sample_frame(media,number,job['fps'],resolution,resolution);left,top,right,bottom=rectangle(row)
        x,y=round(left*resolution),round(top*resolution);pw,ph=round(right*resolution)-x,round(bottom*resolution)-y
        expected=sample_frame(row['path'],number-row['start'],job['fps'],pw,ph)
        if any(p['start']<=number<p['start']+p['frames'] for p in job.get('plates',[])):
            composited=expected_frame(job,number,resolution,resolution)
            expected=[v for yy in range(ph) for v in composited[((y+yy)*resolution+x)*3:((y+yy)*resolution+x+pw)*3]]
        bands=title_band(job,number,resolution);region=[];reference=[]
        # Exclude the resampling edge; verify the actual panel interior.
        for yy in range(1,ph-1):
            if not any(lo<=y+yy<=hi for lo,hi in bands):
                region+=actual[((y+yy)*resolution+x+1)*3:((y+yy)*resolution+x+pw-1)*3];reference+=expected[(yy*pw+1)*3:((yy+1)*pw-1)*3]
        mae,corr=similarity(reference,region)
        if mae>.08 or corr<.90:raise ValueError(f'Collage panel {index+1} differs from its planned asset')
        rows.append({'panel':index+1,'sample_resolution':resolution,'frame':number,'mean_absolute_error':round(mae,5),'correlation':round(corr,5)})
    return rows


def title_matches(job, media):
    rows=[];width=320;height=round(width*job['height']/job['width'])
    # Keep even dimensions so 2x2 expected-layout boundaries remain exact.
    height+=height%2
    for index,t in enumerate(job.get('titles',[])):
        number=t['start']+t['frames']//2;expected=expected_frame(job,number,width,height);actual=sample_frame(media,number,job['fps'],width,height)
        centre=t['y']*height;radius=max(4,4*t['size']/job['height']*height);points=[]
        for y in range(max(0,int(centre-radius)),min(height,int(centre+radius+1))):
            for x in range(width):
                i=(y*width+x)*3
                if sum(abs(expected[i+k]-actual[i+k]) for k in range(3))/3>.2:points.append((x,y))
        if not points:raise ValueError(f'Title {index+1} is missing or has insufficient contrast')
        x0=min(x for x,y in points);x1=max(x for x,y in points);y0=min(y for x,y in points);y1=max(y for x,y in points)
        target=t['size']*2.4*height/job['height']
        if y1-y0+1<target*.55 or len(points)<max(3,len(t['text'].strip())*2):raise ValueError(f'Title {index+1} is too small or unreadable in the export')
        rows.append({'title':index+1,'frame':number,'changed_pixels':len(points),'bbox':[x0,y0,x1,y1],'expected_minimum_height':round(target*.55,2),'scope':'Contrast/size evidence; native text readback is checked during construction, not OCR'})
    return rows


def title_timing_band(job,index,height,number=None):
    """Partition simultaneous title regions at their planned centre midpoints."""
    title=job['titles'][index];centre=title['y']*height;radius=max(3,4*title['size']*height/job['height'])
    top=max(0,math.floor(centre-radius));bottom=min(height,math.ceil(centre+radius)+1)
    for i,other in enumerate(job['titles']):
        overlap=max(title['start'],other['start'])<min(title['start']+title['frames'],other['start']+other['frames'])
        active=number is not None and other['start']<=number<other['start']+other['frames']
        if i==index or not (overlap or active):continue
        other_centre=other['y']*height
        if abs(other_centre-centre)<1:return None
        midpoint=math.ceil((centre+other_centre)/2)
        if other_centre>centre:bottom=min(bottom,midpoint)
        else:top=max(top,midpoint)
    if not top<=centre<bottom or bottom-top<max(3,1.32*title['size']*height/job['height']):return None
    return top,bottom


def title_timing_matches(job, media):
    """Check entry/exit frames in isolated title bands, not speech or OCR."""
    width=160;height=round(width*job['height']/job['width']);height+=height%2
    rows=[]
    for index,t in enumerate(job.get('titles',[])):
        for number in sorted({max(0,t['start']-1),t['start'],t['start']+t['frames']//2,t['start']+t['frames']-1,min(job['frames']-1,t['start']+t['frames'])}):
            band=title_timing_band(job,index,height,number)
            if band is None:
                rows.append({'title':index+1,'frame':number,'status':'ambiguous-nonisolated-title-region'});continue
            expected=expected_frame(job,number,width,height);actual=sample_frame(media,number,job['fps'],width,height)
            changed=sum(sum(abs(expected[(y*width+x)*3+k]-actual[(y*width+x)*3+k]) for k in range(3))/3>.2 for y in range(*band) for x in range(width))
            active=t['start']<=number<t['start']+t['frames'];minimum=max(3,len(t['text'].strip()))
            if active and changed<minimum:raise ValueError(f'Title {index+1} missing at planned frame {number}')
            if not active and changed>=minimum:raise ValueError(f'Title {index+1} band appears outside planned timing at frame {number}')
            rows.append({'title':index+1,'frame':number,'expected_active':active,'changed_pixels':changed,'region_y':list(band),'status':'passed'})
    return rows


def audio_match(expected, media):
    def samples(path):
        values=array.array('f');values.frombytes(raw([binary('ffmpeg'),'-v','error','-i',path,'-map','0:a:0','-ac','1','-ar','1000','-f','f32le','-']))
        if sys.byteorder!='little':values.byteswap()
        return values
    a,b=samples(expected),samples(media);length=min(len(a),len(b))
    if abs(len(a)-len(b))>50 or length<100:raise ValueError('Soundtrack duration differs from prepared audio')
    mae,corr=similarity(a[:length],b[:length])
    reference_rms=math.sqrt(sum(v*v for v in a[:length])/length);actual_rms=math.sqrt(sum(v*v for v in b[:length])/length)
    gain_ratio=actual_rms/reference_rms if reference_rms>1e-6 else (1. if actual_rms<1e-5 else math.inf)
    if corr<.90 or not .8<=gain_ratio<=1.25:raise ValueError('Soundtrack waveform does not match prepared music; inspect timing, gain and audio routing')
    return {'sample_rate':1000,'correlation':round(corr,5),'rms_gain_ratio':round(gain_ratio,5),'mean_absolute_error':round(mae,6),'scope':'Numerical soundtrack correspondence; not a listening or musical taste verdict'}


def timing_evidence(job):
    """Frame-domain alignment to an explicit grid; never infer musical beats."""
    grid=job.get('beats',[])
    cuts=[]
    for shot in job['shots'][1:]:
        frame=shot['start'];nearest=min(grid,key=lambda x:abs(x-frame)) if grid else None
        cuts.append({'cut_frame':frame,'nearest_grid_frame':nearest,'offset_frames':frame-nearest if nearest is not None else None})
    title_events=[]
    for title in job.get('titles',[]):
        nearest=min(grid,key=lambda x:abs(x-title['start'])) if grid else None
        title_events.append({'start_frame':title['start'],'end_frame_exclusive':title['start']+title['frames'],'nearest_grid_frame':nearest,'offset_frames':title['start']-nearest if nearest is not None else None})
    return {'provenance':job.get('timing_provenance'),'mode':job.get('timing_mode','authored_grid'),'title_events':title_events,'cuts':cuts,'transitions':[{'filter':r.get('filter','transition_dissolve'),'start_frame':r['start'],'last_effect_frame':r['start']+r['frames']-1,'cut_frame':job['shots'][r['after_shot']+1]['start']} for r in job.get('transitions',[])],'scope':'Supplied timing-coordinate correspondence only; onset candidates are not verified beats. No listening, downbeat or musical-fit verdict'}


def verify(job_path, media, output):
    job=json.loads(job_path.read_text())
    if output.exists():raise ValueError('Use a fresh verification file')
    for path,digest in {**job['inputs'],**job['prepared_hashes']}.items():
        if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=digest:raise ValueError('Job inputs changed')
    digest=hashlib.sha256(media.read_bytes()).hexdigest()
    run([binary('ffmpeg'),'-v','error','-i',media,'-f','null','-']);meta=probe(media)
    stream=next(s for s in meta['streams'] if s['codec_type']=='video');duration=float(meta['format']['duration'])
    rate=stream.get('avg_frame_rate','0/1').split('/');fps=float(rate[0])/float(rate[1])
    if (stream['width'],stream['height'])!=(job['width'],job['height']) or abs(fps-job['fps'])>.01 or abs(duration-job['frames']/job['fps'])>1.5/job['fps']:raise ValueError('Export dimensions, FPS or duration differ from job')
    if job.get('music') and not any(s['codec_type']=='audio' for s in meta['streams']):raise ValueError('Music missing from export')
    if hashlib.sha256(media.read_bytes()).hexdigest()!=digest:raise ValueError('Export changed during verification')
    frames=visual_matches(job,media)
    plates=plate_matches(job,media)
    titles=title_matches(job,media)
    audio=audio_match(job['music'],media) if job.get('music') else None
    if hashlib.sha256(media.read_bytes()).hexdigest()!=digest:raise ValueError('Export changed during correspondence checks')
    result={'timing_evidence':timing_evidence(job),'visual_samples':frames,'plate_checks':plates,'title_checks':titles,'title_timing_checks':title_timing_matches(job,media),'audio_correspondence':audio,'technical_pass':True,'sha256':digest,'frames_expected':job['frames'],'duration':duration,'fps':fps,'decode':'passed','native_origin':'Requires retained console evidence and project inspection; cannot be established from an MP4 alone.','creative_verdict':'unreviewed','limits':['Sampled correspondence is not exhaustive perceptual review, listening or storytelling acceptance.']}
    output.parent.mkdir(parents=True,exist_ok=True);write(output,result);return result
