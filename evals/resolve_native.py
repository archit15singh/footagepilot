"""Actual export positive control plus wrong-visual and shifted-audio negative controls."""
import argparse
import json
from pathlib import Path
from footagepilot.__main__ import binary,run,write
from footagepilot.resolve import verify


def evaluate(job_path, export, work):
    if work.exists():raise ValueError('Use a fresh evaluation directory')
    work.mkdir(parents=True);job=json.loads(job_path.read_text());ff=binary('ffmpeg');duration=job['frames']/job['fps']
    positive=verify(job_path,export,work/'positive.json')
    if not job.get('music'):raise ValueError('Audio negative control requires a music job')
    wrong=work/'wrong-shots.mp4'
    run([ff,'-v','error','-n','-stream_loop','-1','-i',job['shots'][0]['path'],'-i',job['music'],'-t',duration,'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','20','-c:a','aac',wrong])
    shifted=work/'shifted-audio.mp4'
    run([ff,'-v','error','-n','-i',export,'-i',job['music'],'-t',duration,'-map','0:v:0','-map','1:a:0','-c:v','copy','-af','adelay=200:all=1','-c:a','aac',shifted])
    negatives=[]
    for name,path,expected in [('wrong-shots',wrong,'differs visually'),('shifted-audio',shifted,'waveform does not match')]:
        try:verify(job_path,path,work/(name+'-verification.json'))
        except ValueError as error:
            if expected not in str(error):raise ValueError('Negative failed for the wrong reason: '+str(error)) from error
            negatives.append({'control':name,'rejected':True,'reason':str(error)})
        else:raise ValueError('Verifier accepted negative control: '+name)
    result={'passed':True,'positive':positive,'negative_controls':negatives,'scope':'Native export technical/correspondence verification, not taste, listening or exhaustive frame inspection'}
    write(work/'results.json',result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('job',type=Path);p.add_argument('export',type=Path);p.add_argument('--work',type=Path,required=True);a=p.parse_args()
    print(json.dumps(evaluate(a.job,a.export,a.work),indent=2))
