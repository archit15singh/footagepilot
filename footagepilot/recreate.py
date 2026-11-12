"""Retained stage evidence for reference → visual plan → native Edits export."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
from urllib.parse import urlsplit
from .__main__ import write
from .reference import analyze_reference
from .visual import plan_visual
from .edits import render_edit
from .learning import check_sources


def open_saved(spec_path):
    spec=json.loads(spec_path.read_text());url=spec['saved_collection_url'];parsed=urlsplit(url)
    if parsed.scheme!='https' or parsed.hostname not in ('instagram.com','www.instagram.com') or parsed.username or parsed.password or parsed.port or not re.fullmatch(r'/[A-Za-z0-9_.]+/saved/(?:[A-Za-z0-9_-]+/\d+/)?',parsed.path):raise ValueError('Expected an Instagram saved collection URL')
    if sys.platform!='darwin':raise ValueError('Saved-collection opening currently supports Brave on macOS')
    subprocess.run(['open','-a','Brave Browser','https://www.instagram.com'+parsed.path],check=True)
    return {'opened':'saved collection','next':'Use computer use to review/select reels; save chosen reference_url in the local spec. No collection scraping or account changes.'}


def recreate(spec_path,output,token_file=None):
    if output.exists():raise ValueError('Use a new recreation directory; previous evidence is preserved')
    snapshot=spec_path.read_bytes();spec=json.loads(snapshot);base=spec_path.parent;output.mkdir(parents=True)
    state={'passed':False,'stages':[],'preference':'unreviewed'}
    def stage(name,operation):
        row={'name':name,'status':'running'};state['stages'].append(row);write(output/'run.json',state)
        try:
            result=operation();row.update(status='passed',result=result);write(output/'run.json',state);return result
        except Exception as e:
            row.update(status='failed',error=str(e));write(output/'run.json',state);raise
    registry=Path(__file__).resolve().parent.parent/'docs/edits/sources.json'
    if registry.exists():
        def require_fresh():
            result=check_sources(registry)
            if result['needs_research']:raise ValueError('Edits research is stale; re-research official guides and current capabilities before recreation')
            return result
        stage('research-freshness',require_fresh)
    if spec.get('reference_url'):
        stage('download-analyze-reference',lambda:analyze_reference(spec['reference_url'],output/'reference'))
        spec['reference']=str(output/'reference/analysis.json')
    else:spec['reference']=str((base/spec['reference']).resolve())
    for asset in spec['assets']:asset['path']=str((base/asset['path']).resolve())
    spec['music']=str((base/spec['music']).resolve());local=output/'visual-spec.json';write(local,spec)
    planned=stage('visual-codex-plan',lambda:plan_visual(local,output/'plan'))
    rendered=stage('native-edits-render',lambda:render_edit(Path(planned['manifest']),output/'recreation.mp4',token_file))
    if spec_path.read_bytes()!=snapshot:raise ValueError('Recreation spec changed during run; rerun current input')
    state.update(passed=True,spec_sha256=hashlib.sha256(snapshot).hexdigest(),output=rendered['output'],limits=['Technical success is not creative acceptance.','No reliable listening assessment is available in this agent session.']);write(output/'run.json',state)
    return state
