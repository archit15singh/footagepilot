"""Decode every prepared clip and check independent frame counts; not a native render eval."""
import argparse
import hashlib
import json
from pathlib import Path
from footagepilot.__main__ import binary,probe,run,write


def evaluate(path):
    job=json.loads(path.read_text());rows=[]
    for shot in job['shots']:
        media=Path(shot['path'])
        if hashlib.sha256(media.read_bytes()).hexdigest()!=job['prepared_hashes'][str(media)]:raise ValueError('Prepared media changed')
        run([binary('ffmpeg'),'-v','error','-i',media,'-f','null','-'])
        stream=next(s for s in probe(media)['streams'] if s['codec_type']=='video')
        if int(stream['nb_frames'])!=shot['frames']:raise ValueError('Prepared frame count differs from plan')
        rows.append({'frames':shot['frames'],'decoded':True})
    return {'stage':'individual-clip preparation only','native_export':False,'shots':rows,'frames':sum(s['frames'] for s in rows),'fps':job['fps'],'width':job['width'],'height':job['height'],'limits':job['limits']}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('job',type=Path);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():parser.error('Use a fresh evidence path')
    result=evaluate(args.job);args.output.parent.mkdir(parents=True,exist_ok=True);write(args.output,result)
    print(json.dumps(result,indent=2))
