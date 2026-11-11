"""Word timestamps from a local MLX Whisper runtime, with explicit provenance."""
import json,os,subprocess,time
from pathlib import Path
from .__main__ import validate,write,binary


def align(project_path):
    project=json.loads(project_path.read_text());duration=validate(project)
    python=os.environ.get('FOOTAGEPILOT_ALIGN_PYTHON','python3')
    model=os.environ.get('FOOTAGEPILOT_ALIGN_MODEL','mlx-community/whisper-base.en-mlx')
    script='''import json,sys,mlx_whisper
r=mlx_whisper.transcribe(sys.argv[1],path_or_hf_repo=sys.argv[2],word_timestamps=True,language="en")
open(sys.argv[3],"w").write(json.dumps(r))
'''
    raw=project_path.parent/'alignment-raw.json';started=time.monotonic()
    env={**os.environ,'PATH':str(Path(binary('ffmpeg')).parent)+os.pathsep+os.environ.get('PATH','')}
    result=subprocess.run([python,'-c',script,project['source'],model,str(raw)],capture_output=True,text=True,timeout=600,env=env)
    (project_path.parent/'alignment.log').write_text(result.stderr)
    if result.returncode:raise ValueError('Local word alignment failed: '+result.stderr[-2000:])
    data=json.loads(raw.read_text());words=[]
    for segment in data['segments']:
        for word in segment.get('words',[]):
            start,end=max(0,float(word['start'])),min(duration,float(word['end']))
            if end<=start:continue
            words.append({'id':len(words),'text':word['word'].strip(),'start':start,'end':end})
    if not words:raise ValueError('Aligner produced no timed words')
    output={'source':project['source'],'engine':'mlx-whisper','model':model,'elapsed_seconds':time.monotonic()-started,'words':words,'limitations':['Model-estimated word boundaries require cut-boundary review.']}
    write(project_path.parent/'words.json',output);return output
