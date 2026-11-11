"""Reproducible product run. Supply a narrated recording and three owned PNGs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from footagepilot.__main__ import run, binary, render, probe, write, validate
from footagepilot.transcript import transcribe, apply_selection


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('images',nargs=3,type=Path);p.add_argument('--directory',type=Path,default=Path('projects/evaluation'));a=p.parse_args()
    a.directory.mkdir(parents=True,exist_ok=True)
    project_path=a.directory.resolve()/'project.json'
    if project_path.exists():raise ValueError('Use a fresh evaluation directory')
    source=a.source.resolve();duration=float(probe(source)['format']['duration'])
    item={'schema_version':1,'source':str(source),'keep':[[0,duration]],'brand':{'name':'FootagePilot','accent':'#e5a35d'}}
    write(project_path,item)
    started=time.monotonic();transcript=transcribe(project_path)
    # Known rejection phrase is an explicit fixture policy, not inferred editorial taste.
    rejected=[]
    for row in transcript['segments']:
        if any(phrase in row['text'].lower() for phrase in ('rejected take','discard this sentence')):row['keep']=False;rejected.append(row['id'])
    if not rejected:raise ValueError('Fixture must contain the phrase rejected take')
    write(a.directory/'transcript.json',transcript);ranges=apply_selection(project_path)
    item=json.loads(project_path.read_text());edited=sum(b-a for a,b in ranges)
    item['graphics']=True
    item['storyboard']=[{'title':title,'image':str(image.resolve()),'start':round(edited*f,2),'duration':min(5,edited*.15)} for title,image,f in zip(['Organize the material','Review the decisions','Deliver the story'],a.images,[.08,.38,.68])]
    write(project_path,item)
    records=[]
    for name,accent in [('first','#e5a35d'),('revision','#66c6ba')]:
        item['brand']={'name':'FootagePilot' if name=='first' else 'FootagePilot Revised','accent':accent};write(project_path,item)
        output=render(project_path);saved=a.directory/f'{name}.mp4';shutil.copyfile(output,saved)
        checks=json.loads((a.directory/'verification.json').read_text());checks.pop('command')
        audio=run([binary('ffmpeg'),'-v','error','-i',saved,'-map','0:a:0','-f','hash','-hash','sha256','-']).strip()
        for t in [0.1,*[c['start']+2 for c in item['storyboard']],edited-.2]:
            run([binary('ffmpeg'),'-y','-ss',str(t),'-i',saved,'-frames:v','1',a.directory/f'{name}-{t:.1f}.png'])
        records.append({'name':name,'sha256':digest(saved),'audio_hash':audio,'checks':checks})
    result={'source_sha256':digest(source),'source_duration':duration,'rejected_segments':rejected,'keep':ranges,'transcript_segments':len(transcript['segments']),'runs':records,'revision_audio_identical':records[0]['audio_hash']==records[1]['audio_hash'],'elapsed_seconds':time.monotonic()-started,'limitations':['Synthetic fixture policy removes a known phrase; no autonomous storytelling claim.','ASR segment timing and interpolated captions require review.','Frame samples and technical checks do not constitute listening.']}
    write(a.directory/'result.json',result)
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
