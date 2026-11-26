"""Render reviewed photo selections into a reproducible local film."""
import hashlib,json,math,shutil,tempfile,time
from pathlib import Path
from .__main__ import binary,probe,run,write


def validate_photo_film(data):
    width,height=data.get('width',720),data.get('height',1280)
    if any(type(x) is not int or x<240 or x>3840 or x%2 for x in (width,height)):raise ValueError('Photo-film dimensions must be even integers between 240 and 3840')
    photos=data.get('photos')
    if not isinstance(photos,list) or not 2<=len(photos)<=100:raise ValueError('Choose 2–100 reviewed photos')
    fade=data.get('transition',.35)
    if type(fade) not in (int,float) or not math.isfinite(fade) or not 0<=fade<=2:raise ValueError('Transition must be finite and between 0 and 2 seconds')
    for item in photos:
        path=Path(item['path']);seconds=item.get('duration',3)
        if not path.is_file() or path.suffix.lower() not in ('.jpg','.jpeg','.png','.webp'):raise ValueError('Missing or unsupported photo')
        if type(seconds) not in (int,float) or not math.isfinite(seconds) or not 1<=seconds<=20 or seconds<=2*fade:raise ValueError('Each photo needs 1–20 seconds and more than twice the transition')
        if item.get('motion','push') not in ('push','pull','still'):raise ValueError('Unknown photo motion')
    return width,height,sum(p.get('duration',3) for p in photos)-fade*(len(photos)-1)


def render_photo_film(manifest,output):
    manifest_bytes=manifest.read_bytes();data=json.loads(manifest_bytes)
    for item in data.get('photos',[]):
        if not Path(item['path']).is_absolute():item['path']=str((manifest.parent/item['path']).resolve())
    if data.get('music') and not Path(data['music']).is_absolute():data['music']=str((manifest.parent/data['music']).resolve())
    width,height,expected=validate_photo_film(data)
    if output.exists():raise ValueError('Use a new output path to preserve previous exports')
    output.parent.mkdir(parents=True,exist_ok=True)
    photos=data['photos'];fade=data.get('transition',.35);started=time.monotonic();sources=[]
    for item in photos:
        path=Path(item['path']);sources.append({'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    music_hash=hashlib.sha256(Path(data['music']).read_bytes()).hexdigest() if data.get('music') else None
    with tempfile.TemporaryDirectory(prefix='footagepilot-photos-') as temp:
        root=Path(temp);segments=[]
        for i,item in enumerate(photos):
            duration=item.get('duration',3);frames=round(duration*30);motion=item.get('motion','push')
            zoom={'push':f'1+0.025*on/{frames-1}','pull':f'1.025-0.025*on/{frames-1}','still':'1'}[motion]
            graph=(f'[0:v]split=2[back][front];[back]scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},gblur=sigma=24,eq=brightness=-0.18[bg];'
                   f'[front]scale={int(width*.9)//2*2}:{int(height*.84)//2*2}:force_original_aspect_ratio=decrease[fg];'
                   f'[bg][fg]overlay=(W-w)/2:(H-h)/2,zoompan=z=\'{zoom}\':x=\'iw/2-iw/zoom/2\':y=\'ih/2-ih/zoom/2\':d=1:s={width}x{height}:fps=30,setsar=1,format=yuv420p[v]')
            target=root/f'{i:03d}.mp4'
            run([binary('ffmpeg'),'-v','error','-y','-loop','1','-framerate','30','-i',item['path'],'-filter_complex',graph,'-map','[v]','-frames:v',str(frames),'-an','-c:v','libx264','-preset','fast','-crf','19',target]);segments.append(target)
        # Chain pairwise fades. All inputs have identical geometry, rate and timebase.
        command=[binary('ffmpeg'),'-v','error','-y']
        for segment in segments:command+=['-i',segment]
        if fade:
            filters=[];previous='0:v';cursor=photos[0].get('duration',3)
            for i in range(1,len(segments)):
                label=f'x{i}';filters.append(f'[{previous}][{i}:v]xfade=transition=fade:duration={fade}:offset={cursor-fade}[{label}]');previous=label;cursor+=photos[i].get('duration',3)-fade
            graph=';'.join(filters);label='['+previous+']'
        else:
            graph=''.join(f'[{i}:v]' for i in range(len(segments)))+f'concat=n={len(segments)}:v=1:a=0[film]';label='[film]'
        silent=root/'film.mp4'
        run(command+['-filter_complex',graph,'-map',label,'-an','-c:v','libx264','-preset','fast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',silent])
        result=root/'final.mp4'
        if data.get('music'):
            music=Path(data['music'])
            if not music.is_file():raise ValueError('Music file missing')
            gain=data.get('music_gain',.7)
            if type(gain) not in (int,float) or not math.isfinite(gain) or not 0<=gain<=1:raise ValueError('Music gain must be between 0 and 1')
            run([binary('ffmpeg'),'-v','error','-y','-i',silent,'-stream_loop','-1','-i',music,'-map','0:v:0','-map','1:a:0','-af',f'volume={gain},afade=t=in:d=1,afade=t=out:st={max(0,expected-2)}:d=2','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(expected),'-movflags','+faststart',result])
        else:shutil.copyfile(silent,result)
        run([binary('ffmpeg'),'-v','error','-i',result,'-f','null','-']);metadata=probe(result)
        actual=float(metadata['format']['duration'])
        if abs(actual-expected)>.15:raise ValueError(f'Photo film duration mismatch: {actual} vs {expected}')
        if manifest.read_bytes()!=manifest_bytes:raise ValueError('Photo manifest changed during render')
        for item,snapshot in zip(photos,sources):
            if hashlib.sha256(Path(item['path']).read_bytes()).hexdigest()!=snapshot['sha256']:raise ValueError('Photo changed during render')
        if data.get('music') and hashlib.sha256(Path(data['music']).read_bytes()).hexdigest()!=music_hash:raise ValueError('Music changed during render')
        shutil.copyfile(result,output)
    proof={'passed':True,'kind':'photo-film','photos':sources,'manifest_sha256':hashlib.sha256(manifest_bytes).hexdigest(),'music_sha256':music_hash,'expected_duration':expected,'actual_duration':actual,'width':width,'height':height,'decode':'passed','output_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'elapsed_seconds':time.monotonic()-started,'limitations':['Photo selection and ranking are reviewed editorial judgments.','No automatic face/subject detection or music preference score.']}
    write(output.with_suffix('.verification.json'),proof);return proof
