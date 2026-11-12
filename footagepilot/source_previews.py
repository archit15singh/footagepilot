"""Retained, bounded temporal frame strips for source selection; not motion estimation."""
import hashlib,math
from pathlib import Path
from .__main__ import binary,run


def preview_windows(duration,requested=None):
    if type(duration) not in (int,float) or not math.isfinite(duration) or duration<=0:raise ValueError('Invalid source duration')
    end=max(0,duration-.1);length=min(4.,end)
    if requested is None:bounds=[{'start':s,'end':min(end,s+length)} for s in sorted({round(v,6) for v in (0,(end-length)/2,end-length)})]
    else:
        if not isinstance(requested,list) or not 1<=len(requested)<=3:raise ValueError('Use 1–3 source preview windows')
        bounds=requested
    rows=[]
    for i,row in enumerate(bounds):
        start,stop=row.get('start'),row.get('end')
        if any(type(v) not in (int,float) or not math.isfinite(v) for v in (start,stop)) or not 0<=start<=stop<=end+1e-6 or stop-start>4.000001:raise ValueError('Source preview window must fit source and be at most four seconds')
        times=sorted({round(start+(stop-start)*n/4,6) for n in range(5)})
        rows.append({'id':f'window-{i+1}','start':start,'end':stop,'sample_times':times,'layout':'left-to-right temporal samples; gaps are not continuous footage'})
    return rows


def window_sheet(source,window,target):
    target=Path(target);frames=[]
    for i,at in enumerate(window['sample_times']):
        frame=target.with_name(target.stem+f'-{i+1}.jpg')
        run([binary('ffmpeg'),'-v','error','-n','-ss',at,'-i',source,'-frames:v','1','-vf','scale=224:320:force_original_aspect_ratio=decrease,pad=224:320:(ow-iw)/2:(oh-ih)/2:black,setsar=1',frame])
        if not frame.is_file():raise ValueError('Missing source-window preview frame')
        frames.append(frame)
    inputs=[v for frame in frames for v in ('-i',frame)]
    filt=''.join(f'[{i}:v]' for i in range(len(frames)))+f'hstack=inputs={len(frames)}[v]' if len(frames)>1 else '[0:v]null[v]'
    run([binary('ffmpeg'),'-v','error','-n',*inputs,'-filter_complex',filt,'-map','[v]','-frames:v','1',target])
    return {**window,'sheet':str(target),'sheet_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'frame_sha256':[hashlib.sha256(p.read_bytes()).hexdigest() for p in frames]}
