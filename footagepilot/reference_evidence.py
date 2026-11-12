"""Bounded timestamped frame evidence for visual planning; observations remain model claims."""
import math,re
from pathlib import Path


def select_frames(reference,root,windows=6,times=None):
    duration=reference['duration'];frames=reference.get('frames',[])
    if type(duration) not in (int,float) or not math.isfinite(duration) or duration<=0:raise ValueError('Invalid reference duration')
    if not frames:raise ValueError('Reference needs timestamped frame evidence')
    times=[] if times is None else times
    if not isinstance(times,list) or len(times)>2 or any(type(t) not in (int,float) or not math.isfinite(t) or not 0<=t<=duration for t in times):raise ValueError('Use at most two reference focus times within duration')
    rows=[]
    for i,row in enumerate(frames):
        at=row.get('time');name=row.get('file','')
        if type(at) not in (int,float) or not math.isfinite(at) or not 0<=at<=duration or not re.fullmatch(r'frames/\d+\.jpg',name):raise ValueError('Invalid reference frame record')
        path=(root/name).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():raise ValueError('Reference evidence frame missing or outside its analysis directory')
        rows.append({'id':f'ref-{i:04d}','time':at,'file':name,'kind':row.get('kind','sample')})
    cuts=reference.get('scene_changes',[])
    if any(type(t) not in (int,float) or not math.isfinite(t) or not 0<=t<=duration for t in cuts):raise ValueError('Invalid reference cut candidate')
    selected={}
    for n in range(windows):
        target=duration*n/max(1,windows-1)
        centre=min(cuts,key=lambda t:abs(t-target)) if cuts else target
        for offset in (-.08,0,.08):
            row=min(rows,key=lambda r:abs(r['time']-(centre+offset)))
            selected[row['id']]=row
    for target in times:
        row=min(rows,key=lambda r:abs(r['time']-target));selected[row['id']]=row
    return sorted(selected.values(),key=lambda r:r['time'])


def validate_observations(payload,frames):
    known={r['id']:r for r in frames};observations=payload.get('reference_techniques')
    if not isinstance(observations,list) or not 1<=len(observations)<=12:raise ValueError('Use 1–12 frame-cited reference observations')
    for row in observations:
        ids=row.get('frame_ids',[])
        if not isinstance(ids,list) or not 1<=len(ids)<=6 or any(i not in known for i in ids):raise ValueError('Reference observation cites unknown frames')
        if row.get('technique') not in ('title','collage','full_frame','cut','dissolve','mask_reveal','camera_motion','motion_plate','unknown') or row.get('confidence') not in ('visible','inferred'):raise ValueError('Invalid reference observation classification')
        if row['technique'] in ('cut','dissolve','mask_reveal','camera_motion','motion_plate') and row['confidence']!='inferred':raise ValueError('Temporal techniques require an inferred label from sparse frames')
        if not isinstance(row.get('adaptation'),str) or not 1<=len(row['adaptation'])<=1000:raise ValueError('Reference adaptation needs concise reasoning')
    for group in ('shots','panels','plates'):
        for row in payload.get(group,[]):
            ids=row.get('reference_ids')
            if not isinstance(ids,list) or len(ids)>6 or any(i not in known for i in ids):raise ValueError('Planned shot/panel/plate cites unknown reference evidence')
    return {'status':'frame-citations-validated','frame_count':len(frames),'observation_count':len(observations),'scope':'Checks citations and epistemic labels, not semantic truth or creative fidelity'}
