"""Retained stage evidence for reference → visual plan → selected native editor."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
from urllib.parse import urlsplit
from .__main__ import write
from .reference import analyze_reference
from .visual import plan_visual,plate_catalog
from .edits import render_edit
from .learning import check_sources
from .music_timing import analysis_options,extract_cues
from .plate_fetch import PLATES,fetch_plate


def reference_soundtrack(analysis_path):
    """Select only the exact media retained by a completed reference analysis."""
    analysis=json.loads(analysis_path.read_text());media=analysis_path.parent/'media.mp4'
    if analysis.get('decode')!='passed' or not analysis.get('audio',{}).get('present'):raise ValueError('Reference soundtrack needs completed analysis with audio')
    digest=hashlib.sha256(media.read_bytes()).hexdigest()
    if digest!=analysis.get('source_sha256'):raise ValueError('Reference media changed since analysis')
    return {'media':str(media.resolve()),'source_sha256':digest,'analysis_sha256':hashlib.sha256(analysis_path.read_bytes()).hexdigest(),'scope':'Existing reference audio from time zero; not separated music, an identified song or listening evidence'}


def open_saved(spec_path):
    spec=json.loads(spec_path.read_text());url=spec['saved_collection_url'];parsed=urlsplit(url)
    if parsed.scheme!='https' or parsed.hostname not in ('instagram.com','www.instagram.com') or parsed.username or parsed.password or parsed.port or not re.fullmatch(r'/[A-Za-z0-9_.]+/saved/(?:[A-Za-z0-9_-]+/\d+/)?',parsed.path):raise ValueError('Expected an Instagram saved collection URL')
    if sys.platform!='darwin':raise ValueError('Saved-collection opening currently supports Brave on macOS')
    subprocess.run(['open','-a','Brave Browser','https://www.instagram.com'+parsed.path],check=True)
    return {'opened':'saved collection','next':'Use computer use to review/select reels; save chosen reference_url in the local spec. No collection scraping or account changes.'}


def recreate(spec_path,output,token_file=None,backend="edits"):
    if backend not in ("edits","resolve"):raise ValueError("Unknown native editor backend")
    if output.exists():raise ValueError('Use a new recreation directory; previous evidence is preserved')
    snapshot=spec_path.read_bytes();spec=json.loads(snapshot);base=spec_path.parent
    catalog=plate_catalog({**spec,'native_backend':backend})
    presets=spec.get('plate_presets',[])
    if not isinstance(presets,list) or any(not isinstance(n,str) or n not in PLATES for n in presets) or len(set(presets))!=len(presets):raise ValueError('Use unique known reviewed plate_presets')
    if presets and backend!='resolve':raise ValueError('Reviewed plate presets require Resolve')
    if len(catalog)+len(presets)>8 or set(presets)&{a['id'] for a in catalog}:raise ValueError('Combined plate catalog exceeds eight assets or has duplicate IDs')
    use_reference='music_from_reference' in spec
    if use_reference and (spec['music_from_reference'] is not True or 'music' in spec or backend!='resolve'):raise ValueError('Use music_from_reference=true with Resolve and no separate music path')
    music_options=analysis_options(spec,backend)
    output.mkdir(parents=True)
    state={'passed':False,'backend':backend,'stages':[],'preference':'unreviewed','spec_path':str(spec_path),'spec_sha256':hashlib.sha256(snapshot).hexdigest()}
    def stage(name,operation):
        row={'name':name,'status':'running'};state['stages'].append(row);write(output/'run.json',state)
        try:
            result=operation();row.update(status='passed',result=result);write(output/'run.json',state);return result
        except Exception as e:
            row.update(status='failed',error=str(e));write(output/'run.json',state);raise
    registry=Path(__file__).resolve().parent.parent/f'docs/{backend}/sources.json'
    if registry.exists():
        def require_fresh():
            result=check_sources(registry)
            if result['needs_research']:raise ValueError(f'{backend} research is stale; re-research official guides and current capabilities before recreation')
            return result
        stage('research-freshness',require_fresh)
    if spec.get('reference_url'):
        stage('download-analyze-reference',lambda:analyze_reference(spec['reference_url'],output/'reference'))
        spec['reference']=str(output/'reference/analysis.json')
    else:spec['reference']=str((base/spec['reference']).resolve())
    for asset in spec['assets']+catalog:asset['path']=str((base/asset['path']).resolve())
    if use_reference:
        soundtrack=stage('select-reference-soundtrack',lambda:reference_soundtrack(Path(spec['reference'])))
        spec['music']=soundtrack['media'];del spec['music_from_reference']
    else:spec['music']=str((base/spec['music']).resolve())
    if music_options is not None:
        def analyze_music():
            result=extract_cues(Path(spec['music']),output/'music-cues.json',**music_options)
            if result['duration']+1e-6<spec.get('max_seconds',20):raise ValueError('Source music is shorter than max_seconds; choose a shorter duration budget or longer track')
            return result
        measured=stage('analyze-selected-music',analyze_music)
        spec['music_timing']=measured['music_timing']
        del spec['music_analysis']
    if spec.get('feedback'):spec['feedback']=[str((base/p).resolve()) for p in spec['feedback']]
    if spec.get('model_reviews'):spec['model_reviews']=[str((base/p).resolve()) for p in spec['model_reviews']]
    for name in presets:
        fetched=stage('fetch-reviewed-plate-'+name,lambda name=name:fetch_plate(name,output/'reviewed-plates'/name))
        catalog+=json.loads(Path(fetched['plate_catalog']).read_text())['plate_assets']
    if presets:spec['plate_assets']=catalog
    spec.pop('plate_presets',None)
    spec['native_backend']=backend
    local=output/'visual-spec.json';write(local,spec)
    planned=stage('visual-codex-plan',lambda:plan_visual(local,output/'plan'))
    if backend=='resolve':
        from .resolve import prepare
        prepared=stage('prepare-native-resolve',lambda:prepare(Path(planned['manifest']),output/'resolve-job',render=True))
        if spec_path.read_bytes()!=snapshot:raise ValueError('Recreation spec changed during preparation')
        state.update(status='awaiting-native-render',native_job=prepared['job'],native_job_sha256=hashlib.sha256(Path(prepared['job']).read_bytes()).hexdigest(),console=prepared['console'],next='Execute the generated Lua through Resolve computer use, observe queue completion, then recreate-finish with the exported movie and native DRP. Preparation is not completion.')
        write(output/'run.json',state);return state
    rendered=stage('native-edits-render',lambda:render_edit(Path(planned['manifest']),output/'recreation.mp4',token_file))
    if spec_path.read_bytes()!=snapshot:raise ValueError('Recreation spec changed during run; rerun current input')
    state.update(passed=True,spec_sha256=hashlib.sha256(snapshot).hexdigest(),output=rendered['output'],limits=['Technical success is not creative acceptance.','No reliable listening assessment is available in this agent session.']);write(output/'run.json',state)
    return state


def finish_resolve(run_directory,media,native_project):
    """Finish a retained Resolve run only with actual output and matching editable project."""
    import zipfile
    from html import escape
    from .resolve import verify
    state_path=run_directory/'run.json';state=json.loads(state_path.read_text())
    if state.get('backend')!='resolve' or state.get('status')!='awaiting-native-render':raise ValueError('Run is not awaiting a Resolve export')
    if hashlib.sha256(Path(state['spec_path']).read_bytes()).hexdigest()!=state['spec_sha256']:raise ValueError('Recreation spec changed; start a new run for the current edit')
    project_hash=hashlib.sha256(native_project.read_bytes()).hexdigest()
    job_path=Path(state['native_job']);job_snapshot=job_path.read_bytes()
    if hashlib.sha256(job_snapshot).hexdigest()!=state.get('native_job_sha256'):raise ValueError('Native job changed or has no retained fingerprint; prepare a fresh run')
    job=json.loads(job_snapshot)
    if not zipfile.is_zipfile(native_project):raise ValueError('Expected an actual native DRP project archive')
    with zipfile.ZipFile(native_project) as archive:
        names=archive.namelist()
        if 'project.xml' not in names or not any(n.startswith('SeqContainer/') for n in names):raise ValueError('Native project has no expected project/timeline structure')
        if archive.getinfo('project.xml').file_size>20_000_000:raise ValueError('Native project metadata exceeds inspection limit')
        project_data=archive.read('project.xml')
        if escape(job['project_name'],quote=False).encode() not in project_data:raise ValueError('DRP belongs to a different native project')
    report=verify(job_path,media,run_directory/'native-verification.json')
    if job_path.read_bytes()!=job_snapshot or hashlib.sha256(native_project.read_bytes()).hexdigest()!=project_hash or hashlib.sha256(Path(state['spec_path']).read_bytes()).hexdigest()!=state['spec_sha256']:raise ValueError('Native project or source specification changed during verification')
    state['stages'].append({'name':'verify-native-resolve','status':'passed','result':report})
    state.update(passed=True,status='verified-export',output=str(media),native_project_sha256=hashlib.sha256(native_project.read_bytes()).hexdigest(),preference='unreviewed',limits=['Native DRP identity/archive and rendered correspondence checked; no exhaustive native node-state parser.','Native queue completion must be observed separately; MP4 and DRP files alone cannot authenticate which app rendered them.','No reliable listening or creative acceptance verdict.'])
    write(state_path,state);return state
