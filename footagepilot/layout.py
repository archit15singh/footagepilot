"""Normalized rectangular panel bounds and temporal collision checks."""
import math


def rectangle(row):
    width=row.get('width',row.get('scale',1));height=row.get('height',row.get('scale',1));x=row.get('x',.5);y=row.get('y',.5)
    if any(type(v) not in (int,float) or not math.isfinite(v) for v in (width,height,x,y)) or not .1<=width<=1 or not .1<=height<=1:raise ValueError('Panel width/height must be finite fractions in 0.1–1')
    box=(x-width/2,y-height/2,x+width/2,y+height/2)
    if min(box)<-1e-6 or max(box)>1+1e-6:raise ValueError('Panel rectangle exceeds canvas')
    return box


def validate_panels(rows):
    if len(rows)>36:raise ValueError('Use at most 36 panels')
    boxes=[rectangle(row) for row in rows]
    for i,row in enumerate(rows):
        for j,other in enumerate(rows[:i]):
            if max(row['start'],other['start'])>=min(row['start']+row['duration'],other['start']+other['duration'])-1e-6:continue
            a,b=boxes[i],boxes[j]
            if min(a[2],b[2])-max(a[0],b[0])>1e-6 and min(a[3],b[3])-max(a[1],b[1])>1e-6:raise ValueError('Panel rectangles overlap during their shared duration')
    return boxes
