"""Narration-preserving music and timed SFX mixing with measured peak levels."""
import json,math,re
from pathlib import Path
import subprocess
from .__main__ import binary,run


def mix_audio(video,output,settings,duration):
    duck=settings.get('music_ducking',True);fade=settings.get('music_fade_seconds',.25)
    if type(duck) is not bool:raise ValueError('music_ducking must be a boolean')
    if type(fade) not in (int,float) or not math.isfinite(fade) or not 0<=fade<=10:raise ValueError('music_fade_seconds must be finite and between 0 and 10')
    fade=min(fade,duration/2)
    tracks=[]
    if settings.get('music'):tracks.append({'path':settings['music'],'start':0,'gain':settings.get('music_gain',.08),'loop':True})
    tracks.extend(settings.get('sfx',[]))
    if not tracks:raise ValueError('Audio mix needs music or SFX tracks')
    command=[binary('ffmpeg'),'-y','-i',video];filters=['[0:a]aresample=48000'+(',asplit=2[narration][sidechain]' if duck and settings.get('music') else '[narration]')];labels=['[narration]']
    for i,track in enumerate(tracks,1):
        path=Path(track['path']).expanduser().resolve();start=track.get('start',0);gain=track.get('gain',.2)
        if not path.is_file():raise ValueError('Mix audio file missing')
        if not all(type(x) in (int,float) and math.isfinite(x) for x in (start,gain)) or not 0<=start<duration or not 0<=gain<=1:raise ValueError('Invalid audio timing or gain')
        if track.get('loop'):command+=['-stream_loop','-1']
        command+=['-i',path]
        chain=f'[{i}:a]aresample=48000,volume={gain},adelay={round(start*1000)}:all=1,apad,atrim=duration={duration}'
        if i==1 and settings.get('music'):
            if fade:chain+=f',afade=t=in:d={fade},afade=t=out:st={duration-fade}:d={fade}'
            if duck:
                filters.append(chain+f'[bed{i}]')
                chain=f'[bed{i}][sidechain]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=250:makeup=1'
        filters.append(chain+f'[m{i}]');labels.append(f'[m{i}]')
    filters.append(''.join(labels)+f'amix=inputs={len(labels)}:duration=first:normalize=0,alimiter=limit=0.95:level=false[mix]')
    run(command+['-filter_complex',';'.join(filters),'-map','0:v:0','-map','[mix]','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(duration),'-movflags','+faststart',output])
    analysis=subprocess.run([binary('ffmpeg'),'-i',str(output),'-vn','-af','volumedetect','-f','null','-'],capture_output=True,text=True)
    if analysis.returncode:raise ValueError('Mixed audio level verification failed')
    loudness=subprocess.run([binary('ffmpeg'),'-i',str(output),'-vn','-af','loudnorm=print_format=json','-f','null','-'],capture_output=True,text=True)
    match=re.search(r'\{\s*"input_i".*?\}',loudness.stderr,re.S)
    if loudness.returncode or not match:raise ValueError('Mixed audio loudness verification failed')
    measured=json.loads(match.group())
    return {'music_ducking':duck if settings.get('music') else False,'music_fade_seconds':fade if settings.get('music') else 0,'loudness':{'integrated_lufs':measured['input_i'],'true_peak_dbtp':measured['input_tp'],'range_lu':measured['input_lra']},'tracks':len(tracks),'level_measurements':[line.strip() for line in analysis.stderr.splitlines() if 'mean_volume:' in line or 'max_volume:' in line],'limiter':.95,'listening_verified':False}
