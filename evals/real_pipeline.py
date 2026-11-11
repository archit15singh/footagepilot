"""Reproduce the real-footage pipeline and publish its four-video gallery."""
import argparse,hashlib,json,sys,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from spliceforge.__main__ import binary,run,write
from spliceforge.pipeline import produce

SOURCES={
 'original.webm':'https://upload.wikimedia.org/wikipedia/commons/d/d9/20160917_POTUS_Weekly_Address_HD.webm',
 'music.ogg':'https://upload.wikimedia.org/wikipedia/commons/3/31/Londonderry_Air.ogg',
 'effect.wav':'https://upload.wikimedia.org/wikipedia/commons/6/64/Dingdingding.wav'}
EXPECTED={'original.webm':'a5b7f6f37a055651b3014e6954d83d18f2516903ae817736e536d148f1b5aa7f','music.ogg':'df88fb0243150090776bcb50c4bdf7db687d1c85e47993cf14c69c78f8187fd3','effect.wav':'53b462aba98704d034a703892d0eba2bbd1bb5d65d4c7441894fc57c800a60cf'}
BRIEF='Create a coherent 20–35 second excerpt about the speaker reflecting on delivering weekly addresses. Preserve complete sentences, context and chronology. Exclude title silence and greeting; do not invent speech or assertions.'

def main():
    p=argparse.ArgumentParser();p.add_argument('--work',type=Path,default=Path('projects/real-run'));p.add_argument('--brief',default=BRIEF);p.add_argument('--gallery',type=Path,default=Path('gallery'));a=p.parse_args()
    if a.work.exists():raise ValueError('Use a new working directory to preserve previous evidence')
    a.work.mkdir(parents=True);work=a.work.resolve();provenance=[]
    for name,url in SOURCES.items():
        target=work/name
        with urllib.request.urlopen(url,timeout=60) as response:target.write_bytes(response.read())
        if hashlib.sha256(target.read_bytes()).hexdigest()!=EXPECTED[name]:raise ValueError('Source content changed: '+name)
        provenance.append({'file':name,'url':url,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    write(work/'downloads.json',provenance)
    run([binary('ffmpeg'),'-y','-i',work/'original.webm','-t','60','-vf','scale=1280:720','-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac',work/'source.mp4'])
    project=work/'project.json';write(project,{'schema_version':1,'source':str(work/'source.mp4'),'keep':[[0,60]],'brand':{'name':'Word-aligned editorial test','accent':'#e5a35d'},'audio':{'music':str(work/'music.ogg'),'music_gain':.045,'sfx':[{'path':str(work/'effect.wav'),'start':.2,'gain':.03}]}})
    produce(project,a.brief)
    run([sys.executable,Path(__file__).parent/'publish_gallery.py',work,'--output',a.gallery])
if __name__=='__main__':main()
