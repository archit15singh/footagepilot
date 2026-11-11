"""HyperFrames adapter for the same selected footage and word captions."""
import html,json,os,shutil,tempfile
from pathlib import Path
from .__main__ import binary,run
from .graphics import word_captions_for_cut,captions_for_cut


def render_hyperframes(project_path,cut,output,project):
    duration=sum(b-a for a,b in project['keep']);root=Path(__file__).resolve().parents[1]
    brand=project['brand'];captions=[]
    if project.get('word_captions'):
        aligned=json.loads((project_path.parent/'words.json').read_text());captions=word_captions_for_cut(aligned['words'],project['keep'])
    elif (project_path.parent/'transcript.json').exists():captions=captions_for_cut(json.loads((project_path.parent/'transcript.json').read_text())['segments'],project['keep'])
    project_dir=project_path.parent/'hyperframes-project';assets=project_dir/'assets';assets.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(cut,assets/'cut.mp4');shutil.copyfile(root/'node_modules/gsap/dist/gsap.min.js',assets/'gsap.min.js')
    rows=[]
    for i,c in enumerate(captions):rows.append(f'<div class="clip caption" data-start="{c["start"]}" data-duration="{c["end"]-c["start"]}" data-track-index="10">{html.escape(c["text"])}</div>')
    animations=[]
    for i,card in enumerate(project.get('storyboard',[])):
        image=Path(card['image']);asset=f'card-{i}{image.suffix}';shutil.copyfile(image,assets/asset)
        rows.append(f'<section id="card-{i}" class="clip card" data-start="{card["start"]}" data-duration="{card["duration"]}" data-track-index="{i+1}"><h2>{html.escape(card["title"])}</h2><img src="assets/{asset}"></section>')
        animations.append(f'tl.fromTo("#card-{i}",{{y:24,opacity:0}},{{y:0,opacity:1,duration:.5}}, {card["start"]});')
    side=bool(project.get('storyboard'))
    style='left:50px;top:140px;width:350px;height:390px;object-fit:cover' if side else 'inset:0;width:1280px;height:720px;object-fit:contain'
    page='''<!doctype html><html><head><meta charset="utf-8"><style>body{margin:0;background:#101c17;color:#eee8dc;font-family:sans-serif}*{box-sizing:border-box}#root{position:relative;width:1280px;height:720px;overflow:hidden}header{position:absolute;left:50px;top:35px;font:30px Georgia;z-index:20}.source{position:absolute;object-position:center center}.caption{position:absolute;z-index:30;bottom:35px;left:110px;width:1060px;padding:14px 20px;background:#08110d;font-size:30px;text-align:center;border-radius:8px;overflow-wrap:anywhere}.card{position:absolute;left:455px;top:145px;width:760px}.card h2{font-size:28px;font-weight:normal}.card img{width:760px;height:405px;object-fit:contain}</style></head><body>'''
    page+=f'<div id="root" data-composition-id="main" data-width="1280" data-height="720" data-duration="{duration}"><header style="color:{brand["accent"]}">{html.escape(brand["name"])}</header><video class="clip source" style="{style}" data-start="0" data-duration="{duration}" data-track-index="0" src="assets/cut.mp4" muted playsinline></video>'+''.join(rows)+'</div><script src="assets/gsap.min.js"></script><script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});'+''.join(animations)+'window.__timelines.main=tl;</script></body></html>'
    (project_dir/'index.html').write_text(page)
    env={**os.environ,'HYPERFRAMES_NO_TELEMETRY':'1','HYPERFRAMES_FFMPEG_PATH':binary('ffmpeg'),'HYPERFRAMES_FFPROBE_PATH':binary('ffprobe'),'PATH':str(Path(binary('ffmpeg')).parent)+os.pathsep+os.environ.get('PATH','')}
    browser=os.environ.get('FOOTAGEPILOT_BROWSER')
    if not browser:
        candidates=list((root/'node_modules/.remotion/chrome-headless-shell').rglob('chrome-headless-shell'))
        browser=next((str(p) for p in candidates if p.is_file()),None)
    if browser:env['HYPERFRAMES_BROWSER_PATH']=browser
    import subprocess
    silent=project_path.parent/'hyperframes-silent.mp4'
    result=subprocess.run([str(root/'node_modules/.bin/hyperframes'),'render',str(project_dir),'--output',str(silent),'--fps','30','--workers','2','--quality','standard'],env=env,capture_output=True,text=True,timeout=600)
    (project_path.parent/'hyperframes-render.log').write_text(result.stdout+'\n'+result.stderr)
    if result.returncode:raise ValueError('HyperFrames render failed: '+result.stderr[-1500:])
    run([binary('ffmpeg'),'-y','-i',silent,'-i',cut,'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-shortest',output])
    return {'engine':'hyperframes','caption_groups':len(captions),'storyboard_cards':len(project.get('storyboard',[])),'caption_timing':'ASR word timestamps' if project.get('word_captions') else 'ASR segment interpolation'}
