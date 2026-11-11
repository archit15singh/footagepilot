"""Known-timing cuts and transient/silent-audio negative controls. No aesthetic claim."""
import argparse,json,os,subprocess
from pathlib import Path
from footagepilot.__main__ import binary
from footagepilot.reference import analyze_reference

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--work',type=Path,required=True);args=parser.parse_args();args.work.mkdir(parents=True,exist_ok=False)
    ff=binary('ffmpeg');source=args.work/'fixture.mp4'
    subprocess.run([ff,'-v','error','-y','-f','lavfi','-i',"color=black:s=320x240:r=30:d=1[black];color=white:s=320x240:r=30:d=1[white];color=black:s=320x240:r=30:d=1[black2];color=white:s=320x240:r=30:d=1[white2];[black][white][black2][white2]concat=n=4:v=1:a=0",'-f','lavfi','-i',"aevalsrc=if(lt(mod(t\\,1)\\,.02)\\,.5*sin(2*PI*880*t)\\,0):s=8000:d=4",'-c:v','libx264','-pix_fmt','yuv420p','-c:a','aac','-shortest',str(source)],check=True,capture_output=True)
    analyze_reference(str(source),args.work/'analysis',interval=1)
    result=json.loads((args.work/'analysis/analysis.json').read_text());cuts=result['scene_changes'];events=result['audio']['onsets']
    assert all(any(abs(t-expected)<.04 for t in cuts) for expected in (1,2,3)),cuts
    assert all(any(abs(e['time']-expected)<.05 for e in events) for expected in (1,2,3)),events
    silent=args.work/'silent.mp4';subprocess.run([ff,'-v','error','-y','-i',str(source),'-an','-c:v','copy',str(silent)],check=True)
    analyze_reference(str(silent),args.work/'silent-analysis',interval=1)
    negative=json.loads((args.work/'silent-analysis/analysis.json').read_text());assert not negative['audio']['present'];assert not negative['audio']['onsets'];assert all(r['nearest_onset'] is None for r in negative['cut_audio_alignment'])
    print(json.dumps({'passed':True,'known_cuts':cuts,'known_onsets':[e['time'] for e in events],'silent_negative_control':'passed','scope':'Technical timing only'},indent=2))
if __name__=='__main__':main()
