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


def preview_filter(aspect=None):
    whole='scale=224:320:force_original_aspect_ratio=decrease,pad=224:320:(ow-iw)/2:(oh-ih)/2:black,setsar=1'
    if aspect is None:return whole
    heights={'9:16':398,'16:9':126,'1:1':224,'4:5':280}
    if aspect not in heights:raise ValueError('Unsupported crop preview aspect')
    h=heights[aspect]
    crop=f'scale=224:{h}:force_original_aspect_ratio=increase,crop=224:{h}:(iw-ow)/2:(ih-oh)/2,setsar=1'
    return f'split=2[whole][crop];[whole]{whole}[top];[crop]{crop}[bottom];[top][bottom]vstack=inputs=2'


def window_sheet(source,window,target,aspect=None):
    target=Path(target);frames=[]
    filt=preview_filter(aspect)
    for i,at in enumerate(window['sample_times']):
        frame=target.with_name(target.stem+f'-{i+1}.jpg')
        run([binary('ffmpeg'),'-v','error','-n','-ss',at,'-i',source,'-frames:v','1','-vf',filt,frame])
        if not frame.is_file():raise ValueError('Missing source-window preview frame')
        frames.append(frame)
    inputs=[v for frame in frames for v in ('-i',frame)]
    stack=''.join(f'[{i}:v]' for i in range(len(frames)))+f'hstack=inputs={len(frames)}[v]' if len(frames)>1 else '[0:v]null[v]'
    run([binary('ffmpeg'),'-v','error','-n',*inputs,'-filter_complex',stack,'-map','[v]','-frames:v','1',target])
    layout={'canvas_preview_aspect':aspect,'rows':['Full source, padded within224x320','Centre fill crop at canvas aspect; focus0.5/0.5, no zoom'], 'scope':'Crop alternative for selection, not final shot framing or continuous motion'} if aspect else {}
    return {**window,**layout,'sheet':str(target),'sheet_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'frame_sha256':[hashlib.sha256(p.read_bytes()).hexdigest() for p in frames]}
