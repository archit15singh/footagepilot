"""Compare two native glass strengths over an unchanged film; no creative verdict."""
import argparse,copy,hashlib,json,zipfile
from pathlib import Path
from footagepilot.resolve import verify,visual_matches,plate_matches,sample_frame,expected_frame,similarity
from .planned_plates import make_no_plate_control


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def base_signature(job):
    return (job['fps'],job['width'],job['height'],job['frames'],
            [(s['start'],s['frames'],sha(s['path'])) for s in job['shots']],sha(job['music']))


def project_identity(path,name):
    with zipfile.ZipFile(path) as archive:
        if 'project.xml' not in archive.namelist() or not any(p.startswith('SeqContainer/') for p in archive.namelist()):raise ValueError('Missing native project structure')
        if archive.getinfo('project.xml').file_size>20_000_000 or name.encode() not in archive.read('project.xml'):raise ValueError('Native project identity mismatch')


def evaluate(baseline_path,medium_path,strong_path,provenance_path,output):
    if output.exists():raise ValueError('Use a fresh glass evaluation directory')
    base=json.loads(baseline_path.read_text());jobs=[json.loads(p.read_text()) for p in (medium_path,strong_path)]
    if any(base_signature(j)!=base_signature(base) for j in jobs):raise ValueError('Main footage/timing/music changed')
    if any(len(j.get('plates',[]))!=1 for j in jobs):raise ValueError('Expected exactly one glass plate')
    a,b=(copy.deepcopy(j['plates'][0]) for j in jobs)
    for row in (a,b):row.pop('opacity')
    if sha(a.pop('path'))!=sha(b.pop('path')) or a!=b:raise ValueError('Glass variants changed more than opacity')
    provenance=json.loads(provenance_path.read_text());root=provenance_path.parent
    if provenance.get('status')!='verified-local-asset' or provenance.get('license')!='CC0-1.0':raise ValueError('Missing reviewed effect provenance')
    if sha(root/'original.mp4')!=provenance['sha256'] or sha(root/'glass-impact.mp4')!=provenance['derived_sha256']:raise ValueError('Effect asset changed since fetch')
    output.mkdir(parents=True);control=make_no_plate_control(jobs[0],output/'missing-glass-control.mp4')
    absent=copy.deepcopy(jobs[0]);absent['plates']=[];control_rows=visual_matches(absent,control)
    result={'source':{'credit':provenance['credit'],'license':provenance['license'],'page':provenance['source_page'],
                      'source_sha256':provenance['sha256'],'derived_sha256':provenance['derived_sha256'],'recipe':provenance['recipe']},
            'base_invariants':'Main clip hashes, timing, canvas, FPS, total frames and prepared soundtrack identical',
            'opacity_only_pair':True,'control_base_visual_samples':len(control_rows),'variants':[],'creative_acceptance':'unreviewed'}
    for path,job in zip((medium_path,strong_path),jobs):
        media=path.parent/'resolve-output.mp4';drp=path.parent/'resolve-project.drp'
        project_identity(drp,job['project_name']);folder=output/f"opacity-{round(job['plates'][0]['opacity']*100)}";folder.mkdir()
        native=verify(path,media,folder/'native.json');plate=job['plates'][0];dense=[];activity=[]
        for n in range(plate['frames']):
            number=plate['start']+n;mae,corr=similarity(expected_frame(job,number),sample_frame(media,number,job['fps']))
            if mae>.08 or corr<.90:raise ValueError('Dense glass correspondence failed')
            dense.append({'frame':number,'mae':mae,'correlation':corr})
            pixels=sample_frame(plate['path'],n,job['fps']);activity.append(sum(pixels)/len(pixels))
        # Verify the actual prepared glass excerpt against source asset frames6..23.
        source_checks=[]
        for n in (0,plate['frames']//2,plate['frames']-1):
            mae,corr=similarity(sample_frame(root/'glass-impact.mp4',6+n,30),sample_frame(plate['path'],n,30))
            if mae>.03 or corr<.95:raise ValueError('Prepared glass source range mismatch')
            source_checks.append({'prepared_frame':n,'asset_frame':6+n,'mae':mae,'correlation':corr})
        try:plate_matches(job,control)
        except ValueError as error:control_error=str(error)
        else:raise ValueError('Missing glass control was not rejected')
        if 'active pixels' not in control_error:raise ValueError('Control did not fail for missing glass')
        peak=plate['start']+max(range(len(activity)),key=activity.__getitem__)
        incoming=next(s for s in job['shots'] if plate['start']<s['start']<plate['start']+plate['frames'])
        result['variants'].append({'opacity':plate['opacity'],'movie_sha256':native['sha256'],'drp_sha256':sha(drp),
            'visual_samples':len(native['visual_samples']),'plate_checks':native['plate_checks'],'dense_effect_frames':dense,
            'source_range_checks':source_checks,'audio':native['audio_correspondence'],
            'missing_glass_rejected':True,'control_error':control_error,
            'brightest_plate_frame':peak,'cut_frame':incoming['start'],'brightness_offset_frames':peak-incoming['start'],
            'timing_scope':'Maximum mean prepared-plate RGB intensity versus the cue-aligned cut; not an audible impact or verified beat'})
    (output/'results.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('baseline',type=Path);p.add_argument('medium',type=Path);p.add_argument('strong',type=Path);p.add_argument('provenance',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(evaluate(a.baseline,a.medium,a.strong,a.provenance,a.output),indent=2))
