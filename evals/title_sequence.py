"""Negative controls for actual native title-sequence timing; never a renderer."""
import argparse,json
from pathlib import Path
from footagepilot.__main__ import binary,run,write
from footagepilot.resolve import title_timing_matches


def evaluate(job_path,media,output):
    if output.exists():raise ValueError('Use a new evaluation directory')
    job=json.loads(job_path.read_text());titles=job.get('titles',[])
    if len(titles)<2 or not any(t['start']>0 for t in titles):raise ValueError('Needs staggered native titles')
    positive=title_timing_matches(job,media)
    if any(r['status']!='passed' for r in positive):raise ValueError('Ambiguous positive title timing')
    output.mkdir(parents=True)
    title=next(t for t in reversed(titles) if t['start']>0)
    if not any(b['start']==0 and b['start']+b['frames']>=title['start']+title['frames'] for b in job.get('backgrounds',[])):raise ValueError('Controls need an opening black card covering the selected title')
    centre=round(title['y']*job['height']);radius=round(4*title['size']);top=max(0,centre-radius);height=min(job['height']-top,2*radius)
    start=title['start']/job['fps'];end=(title['start']+title['frames'])/job['fps']
    missing=output/'missing-line.mp4'
    run([binary('ffmpeg'),'-v','error','-n','-i',media,'-vf',f"drawbox=x=0:y={top}:w=iw:h={height}:color=black:t=fill:enable='gte(t,{start})*lt(t,{end})'",'-c:v','libx264','-crf','18','-c:a','copy',missing])
    crop=output/'line.png'
    run([binary('ffmpeg'),'-v','error','-n','-ss',(start+end)/2,'-i',media,'-vf',f'crop=iw:{height}:0:{top}','-frames:v','1',crop])
    early=output/'early-line.mp4'
    run([binary('ffmpeg'),'-v','error','-n','-i',media,'-loop','1','-i',crop,'-filter_complex',f"[0:v][1:v]overlay=0:{top}:enable='lt(t,{start})':shortest=1[v]",'-map','[v]','-map','0:a?','-c:v','libx264','-crf','18','-c:a','copy',early])
    controls=[]
    for label,path in [('missing-line',missing),('early-line',early)]:
        run([binary('ffmpeg'),'-v','error','-i',path,'-f','null','-'])
        try:title_timing_matches(job,path)
        except ValueError as error:controls.append({'control':label,'rejected':True,'error':str(error)})
        else:raise ValueError('Title timing accepted '+label)
    result={'passed':True,'positive_samples':len(positive),'negative_controls':controls,'limits':['Changed pixels establish timing in isolated bands, not OCR, exact typeface or musical taste.','Controls use FFmpeg only to alter a retained actual native export.']};write(output/'results.json',result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('job',type=Path);p.add_argument('media',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(evaluate(a.job,a.media,a.output),indent=2))
