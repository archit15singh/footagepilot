"""MakeMyClip timeline execution, preserving its editable composition and log."""
import json,os
from pathlib import Path
from .__main__ import run,probe,write


def clip_binary():return os.environ.get('SPLICEFORGE_CLIP',str(Path(__file__).resolve().parents[1]/'node_modules/.bin/clip'))


def export_ranges(project,output,workspace,remove_silence=False):
    workspace.mkdir(parents=True,exist_ok=True)
    env={**os.environ,'MAKEMYCLIP_WORKSPACE':str(workspace)}
    ffmpeg=os.environ.get('SPLICEFORGE_FFMPEG')
    if ffmpeg:env['PATH']=str(Path(ffmpeg).parent)+os.pathsep+env.get('PATH','')
    records=[]
    def call(args):
        import subprocess
        result=subprocess.run([clip_binary(),'timeline',*map(str,args)],env=env,capture_output=True,text=True,timeout=600)
        records.append({'args':list(map(str,args)),'status':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
        write(workspace/'operations.json',records)
        if result.returncode:raise ValueError('MakeMyClip failed: '+result.stderr[-1500:])
        return json.loads(result.stdout)
    call(['new','--width',1280,'--height',720,'--fps',30])
    cursor=0
    for start,end in project['keep']:
        added=call(['add-media',project['source'],start,end,'--start',cursor])
        if remove_silence:call(['silence',added['clipId']])
        cursor+=end-start
    call(['export',output])
    return {'engine':'makemyclip','ranges':len(project['keep']),'silence_removal':remove_silence,'workspace':str(workspace)}


def cleanup(project_path):
    project=json.loads(project_path.read_text())
    from .__main__ import validate
    duration=validate(project)
    output=project_path.parent/'cleaned.mp4'
    if Path(project['source']).resolve()==output.resolve():raise ValueError('Already uses cleaned.mp4; use a new project for another cleanup pass')
    result=export_ranges({**project,'keep':[[0,duration]]},output,project_path.parent/'cleanup-workspace',True)
    project.update(original_source=project['source'],source=str(output),keep=[[0,float(probe(output)['format']['duration'])]])
    # Preserve previous analysis, but never reuse timings against the cleaned source.
    for name in ['words.json','transcript.json','plan.json','verification.json']:
        path=project_path.parent/name
        if path.exists():path.replace(path.with_suffix('.previous.json'))
    write(project_path,project);write(project_path.parent/'cleanup.json',result);return result
