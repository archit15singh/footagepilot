"""Portable Resolve console jobs. No daemon, credentials or unsafe Lua filesystem access."""
import hashlib
import json
import math
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from .__main__ import binary, probe, run, write
from .edits import validate_edit


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


def prepare(manifest, output):
    """Render individual image shots, then generate a checked native assembly job.

    First version deliberately supports straight cuts and full-frame footage only.
    Unsupported effects fail before rendering, rather than disappearing from the export.
    """
    from .learning import check_sources
    registry=Path(__file__).resolve().parent.parent/'docs/resolve/sources.json'
    if not registry.exists() or check_sources(registry)['needs_research']:raise ValueError('Resolve research is missing or stale; review official guides and installed API before preparing a job')
    snapshot=manifest.read_bytes();data=json.loads(snapshot);validate_edit(data,manifest.parent)
    if data.get('overlays') or data.get('titles') or data.get('transitions'):
        raise ValueError('Resolve assembly v1 requires a cut-only manifest; overlays, titles and transitions are not yet implemented')
    if output.exists():raise ValueError('Use a fresh Resolve job directory')
    fps=data.get('fps',30);w,h={'9:16':(1080,1920),'16:9':(1920,1080),'1:1':(1080,1080),'4:5':(1080,1350)}[data.get('aspect','9:16')]
    shots=[];cursor=0;inputs={};pending=[];elapsed=Decimal(0)
    for i,shot in enumerate(data['shots']):
        path=(manifest.parent/shot['path']).resolve();inputs[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
        meta=probe(path);video=next((s for s in meta['streams'] if s['codec_type']=='video'),None)
        if not video:raise ValueError('Shot has no video stream')
        elapsed+=Decimal(str(shot['duration']));end=int((elapsed*fps).quantize(Decimal(1),rounding=ROUND_HALF_UP));frames=end-cursor
        if frames<1:raise ValueError('Shot rounds below one frame')
        still=path.suffix.lower() in ('.jpg','.jpeg','.png','.webp')
        if not still and float(meta['format']['duration'])+.5/fps<frames/fps:raise ValueError('Video source is shorter than planned shot')
        target=output/f'shot-{i+1:03d}.mp4'
        # Per-shot preparation is disclosed; timeline edits and markers remain native.
        fit=shot.get('fit','fill');zoom=shot.get('zoom',0)
        if fit=='contain' and zoom:raise ValueError('Contain with zoom is not supported by Resolve preparation')
        if fit=='fill':
            filt=f'scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}:(iw-ow)*{shot.get("focus_x",.5)}:(ih-oh)*{shot.get("focus_y",.5)}'
        else:filt=f'scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black'
        if zoom:
            filt+=f",zoompan=z='1+{zoom}*on/{max(1,frames-1)}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={w}x{h}:fps={fps}"
        command=[binary('ffmpeg'),'-v','error','-n']+(['-loop','1'] if still else [])+['-i',path,'-an','-vf',filt,'-r',fps,'-frames:v',frames,'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',target]
        pending.append(command);shots.append({'path':str(target),'start':cursor,'frames':frames});cursor=end
    music=None
    if data.get('music'):
        path=(manifest.parent/data['music']).resolve();inputs[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
        if float(probe(path)['format']['duration'])+.5/fps<cursor/fps:raise ValueError('Music is shorter than timeline')
        music=output/'music.wav'
        pending.append([binary('ffmpeg'),'-v','error','-n','-i',path,'-t',cursor/fps,'-af',f'volume={data.get("music_gain",.65)},afade=t=in:d=0.1,afade=t=out:st={max(0,cursor/fps-.3)}:d=0.3','-c:a','pcm_s16le',music])
    output.mkdir(parents=True)
    job={'schema_version':1,'status':'prepared-not-executed','fps':fps,'width':w,'height':h,'frames':cursor,'shots':shots,'music':str(music) if music else None,'beats':[],'inputs':inputs,'manifest_sha256':hashlib.sha256(snapshot).hexdigest(),'limits':['Image crop/zoom and audio gain/fades are baked into separate prepared media. Native Resolve retains individual clips, cuts, audio track and markers.','Cut-only v1: rejects titles, overlays and transitions.','Preparing a job does not prove Resolve executed or rendered it.']}
    timing=data.get('music_timing')
    if timing:
        n=0
        while timing.get('offset',0)+n*60/timing['bpm']<cursor/fps:
            job['beats'].append(round((timing.get('offset',0)+n*60/timing['bpm'])*fps));n+=1
        job['timing_provenance']=timing['provenance']
    try:
        for cmd in pending:run(cmd)
        for path,digest in inputs.items():
            if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=digest:raise ValueError('Source changed during preparation')
        if manifest.read_bytes()!=snapshot:raise ValueError('Manifest changed during preparation')
        job['prepared_hashes']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*(Path(s['path']) for s in shots),*([music] if music else [])]}
        write(output/'job.json',job)
        template=(Path(__file__).parent/'resolve_job.lua').read_text()
        payload={k:job[k] for k in ('fps','width','height','frames','shots','music','beats')}
        payload.update(name='FootagePilot-'+output.name,target=str(output),custom_name='resolve-output')
        (output/'console.lua').write_text('do local cfg='+lua(payload)+'; '+template+' end\n')
        (output/'render.lua').write_text((Path(__file__).parent/'resolve_render.lua').read_text())
        return {'job':str(output/'job.json'),'console':str(output/'console.lua'),'status':job['status'],'next':'Paste console.lua into Resolve Workspace > Console (Lua). Inspect native media, then render. Run resolve-verify on the actual output.'}
    except Exception as error:
        write(output/'failure.json',{'stage':'prepare','error':str(error)});raise


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
    result={'technical_pass':True,'sha256':digest,'frames_expected':job['frames'],'duration':duration,'fps':fps,'decode':'passed','native_origin':'Requires retained console evidence and project inspection; cannot be established from an MP4 alone.','creative_verdict':'unreviewed','limits':['No listening, beat perception, crop or storytelling verdict. A decodable Media Offline slate can still pass technical checks; inspect output frames.']}
    output.parent.mkdir(parents=True,exist_ok=True);write(output,result);return result
