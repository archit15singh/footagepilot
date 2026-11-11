"""Generate an owned narrated evaluation input on macOS using native speech."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from spliceforge.__main__ import binary,run,probe
out=Path('projects/demo-input').resolve();out.mkdir(parents=True,exist_ok=True)
text='This is a rejected take. Please discard this sentence. A useful video starts with a clear story. Bring your recordings, notes, and screenshots into one place. Start by organizing the material you actually need, so every scene has a purpose. Next, review the cut. Remove mistakes and check the words that remain. Give each visual one job. Highlight a decision, explain a change, or show the product in action. Finally, deliver a video that is easy to revise. Keep narration clear, captions readable, and graphics consistent. When the brand changes, update the design without rebuilding the story.'
run(['say','-v','Samantha','-r','166','-o',out/'speech.aiff',text])
duration=float(probe(out/'speech.aiff')['format']['duration'])+.5
run([binary('ffmpeg'),'-y','-f','lavfi','-i','color=c=0x17252c:s=1280x720:r=30','-i',out/'speech.aiff','-t',str(duration),'-af','apad','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',out/'source.mp4'])
for i,title in enumerate(['ORGANIZE','REVIEW','DELIVER']):
    run([binary('ffmpeg'),'-y','-f','lavfi','-i','color=c=0x17252c:s=1200x700','-vf',f"drawtext=text='{title}':fontsize=72:fontcolor=white:x=80:y=90,drawbox=x=80:y=300:w={250+i*250}:h=32:color=0xe5a35d:t=fill",'-frames:v','1',out/f'screen-{i}.png'])
(out/'provenance.json').write_text(json.dumps({'kind':'synthetic','text':text,'speech':'macOS Samantha,166words/minute','visuals':'original FFmpeg color and text'},indent=2))
print(out)
