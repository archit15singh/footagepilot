"""Run cleanup → word alignment → headless story plan → both renderers and mix."""
import json,time,shutil,hashlib
from .__main__ import write,render,run,binary,probe
from .alignment import align
from .cleanup import cleanup
from .planner import plan,apply_plan
from .audio import mix_audio


def produce(project_path,brief,remove_silence=True,engines=None):
    engines=list(engines) if engines is not None else ['remotion','hyperframes']
    if not engines or len(set(engines))!=len(engines) or any(e not in ('remotion','hyperframes') for e in engines):raise ValueError('Choose unique render engines: remotion, hyperframes')
    directory=project_path.parent;state={'status':'running','engines':engines,'stages':[],'outputs':[]}
    state_path=directory/'pipeline-run.json'
    def stage(name,action):
        started=time.monotonic();record={'name':name,'status':'running'};state['stages'].append(record);write(state_path,state)
        try:
            result=action();record.update(status='passed',elapsed_seconds=time.monotonic()-started);write(state_path,state);return result
        except Exception as error:
            record.update(status='failed',error=str(error),elapsed_seconds=time.monotonic()-started);state['status']='failed';write(state_path,state);raise
    def verify_output(target):
        run([binary('ffmpeg'),'-v','error','-i',target,'-f','null','-'])
        metadata=probe(target)
        return {'full_decode':'passed','duration':float(metadata['format']['duration']),'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'streams':[s['codec_type'] for s in metadata['streams']]}
    if remove_silence:stage('makemyclip-cleanup',lambda:cleanup(project_path))
    stage('word-alignment',lambda:align(project_path))
    stage('story-plan-codex',lambda:plan(project_path,brief))
    stage('apply-word-plan',lambda:apply_plan(project_path))
    project=json.loads(project_path.read_text());has_audio='audio' in project;audio=project.pop('audio',None)
    try:
        for engine in engines:
            project.update(graphics=True,word_captions=True,cut_engine='makemyclip',renderer=engine)
            write(project_path,project)
            stage('render-'+engine,lambda:render(project_path))
            target=directory/f'{engine}-narration.mp4';shutil.copyfile(directory/'output.mp4',target)
            proof=json.loads((directory/'verification.json').read_text());proof.pop('command',None);write(directory/f'{engine}-verification.json',proof)
            state['outputs'].append({'name':engine+' narration','path':target.name,'engine':engine,'mixed':False,'verification':stage('verify-'+engine,lambda:verify_output(target))})
            if audio:
                mixed=directory/f'{engine}-mixed.mp4';duration=sum(b-a for a,b in project['keep'])
                details=stage('mix-'+engine,lambda:mix_audio(target,mixed,audio,duration));write(directory/f'{engine}-mix.json',details)
                state['outputs'].append({'name':engine+' music and SFX','path':mixed.name,'engine':engine,'mixed':True,'verification':stage('verify-mix-'+engine,lambda:verify_output(mixed))})
    finally:
        if has_audio:
            current=json.loads(project_path.read_text());current['audio']=audio;write(project_path,current)
    final=directory/state['outputs'][-1]['path'];shutil.copyfile(final,directory/'output.mp4')
    from .evidence import input_revision,file_revision
    proof=json.loads((directory/'verification.json').read_text());proof.update(actual_duration=float(probe(directory/'output.mp4')['format']['duration']),input_revision=input_revision(project_path),output_revision=file_revision(directory/'output.mp4'),audio_mix=json.loads((directory/f'{engines[-1]}-mix.json').read_text()) if audio else None)
    write(directory/'verification.json',proof)
    state['status']='passed';write(state_path,state)
    return state
