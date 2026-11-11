"""Publish verified real pipeline outputs and a static comparison gallery."""
import argparse,hashlib,html,json,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from spliceforge.__main__ import binary,probe,run

def main():
    parser=argparse.ArgumentParser();parser.add_argument('run',type=Path);parser.add_argument('--output',type=Path,default=Path('gallery'));args=parser.parse_args()
    state=json.loads((args.run/'pipeline-run.json').read_text())
    if state['status']!='passed' or len(state['outputs'])!=4:raise ValueError('A successful four-output pipeline run is required')
    args.output.mkdir(exist_ok=True);media=args.output/'videos';media.mkdir(exist_ok=True)
    cards=[];evidence={'pipeline':state,'planner':json.loads((args.run/'plan.json').read_text()),'artifacts':[]}
    for item in state['outputs']:
        source=args.run/item['path'];target=media/source.name
        run([binary('ffmpeg'),'-v','error','-i',source,'-f','null','-'])
        if hashlib.sha256(source.read_bytes()).hexdigest()!=item['verification']['sha256']:raise ValueError('Output changed after verification')
        shutil.copyfile(source,target)
        poster=media/(target.stem+'.jpg');run([binary('ffmpeg'),'-y','-ss','3','-i',target,'-frames:v','1',poster])
        evidence['artifacts'].append({'file':str(target.relative_to(args.output)),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'duration':float(probe(target)['format']['duration'])})
        cards.append(f'<article><h2>{html.escape(item["name"])}</h2><video controls preload="metadata" poster="videos/{poster.name}" src="videos/{target.name}"></video><p>MakeMyClip cleanup + local word alignment + Codex story plan + {html.escape(item["engine"])}. '+('Music and SFX added; listening review unverified.' if item['mixed'] else 'Original narration, no added music or effects.')+'</p></article>')
    # Machine paths and full operational logs remain in the local run directory.
    for item in evidence['pipeline']['outputs']:item['path']=Path(item['path']).name
    (args.output/'evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Real footage · Automated video variations</title><style>body{max-width:1400px;margin:40px auto;padding:0 20px;background:#151515;color:#eee;font:17px/1.5 sans-serif}h1{font-size:32px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,500px),1fr));gap:24px}article{border:1px solid #444;padding:18px}video{width:100%}a{color:#9dcafa}p{color:#bbb}button{padding:10px 16px;margin-right:12px}</style><h1>Real footage · Automatically generated variations</h1><p>Same real recording, different render and audio paths. These are engineering evaluation edits of an archival 2016 White House weekly address, not an endorsement or a contemporary statement. No face, voice or performance was generated.</p><p><button onclick="document.querySelectorAll('video').forEach(v=>v.pause())">Pause all</button><a href="evidence.json">Run evidence</a> · <a href="../docs/REAL-E2E-RESULTS.md">Findings and limits</a></p><main>'''+''.join(cards)+'''</main><footer><p>Source: <a href="https://commons.wikimedia.org/wiki/File:20160917_POTUS_Weekly_Address_HD.webm">The White House, September 2016, public-domain U.S. federal work</a>. Music: <a href="https://commons.wikimedia.org/wiki/File:Londonderry_Air.ogg">Londonderry Air, Jon Hall, public domain</a>. SFX: <a href="https://commons.wikimedia.org/wiki/File:Dingdingding.wav">Dingdingding, IOII-IOIO-IIOI, CC0</a>. Selection and timing are model-generated estimates. Listening quality and general autonomous storytelling are not established by decode checks.</p></footer></html>'''
    (args.output/'index.html').write_text(page)
    print(args.output.resolve()/'index.html')
if __name__=='__main__':main()
