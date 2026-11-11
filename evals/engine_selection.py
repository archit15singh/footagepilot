"""Verify an actual selected-engine produce run, including decoded outputs."""
import argparse,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from spliceforge.__main__ import binary,run,probe


def evaluate(work,engine):
    state=json.loads((work/'pipeline-run.json').read_text())
    assert state['status']=='passed' and state['engines']==[engine]
    renders=[s['name'] for s in state['stages'] if s['name'].startswith('render-')]
    assert renders==['render-'+engine],renders
    assert state['outputs'] and all(o['engine']==engine for o in state['outputs'])
    results=[]
    for item in state['outputs']:
        path=work/item['path'];run([binary('ffmpeg'),'-v','error','-i',path,'-f','null','-'])
        digest=hashlib.sha256(path.read_bytes()).hexdigest();assert digest==item['verification']['sha256']
        metadata=probe(path);assert {'audio','video'}<={s['codec_type'] for s in metadata['streams']}
        results.append({'name':item['name'],'sha256':digest,'duration':float(metadata['format']['duration']),'decode':'passed'})
    planner=json.loads((work/'plan.json').read_text());assert planner['model']=='gpt-6.1-sol' and planner['reasoning_effort']=='low'
    return {'gate':'passed','requested_engine':engine,'render_stages':renders,'planner':{k:planner[k] for k in ['model','reasoning_effort']},'stages':state['stages'],'outputs':results,'scope':'One live pipeline run on already-cleaned real speech. No controlled wall-clock speedup claim.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('work',type=Path);p.add_argument('--engine',required=True,choices=['remotion','hyperframes']);a=p.parse_args()
    print(json.dumps(evaluate(a.work,a.engine),indent=2))
