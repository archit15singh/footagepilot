"""Check a title-only native revision and reject the former title treatment."""
import argparse,json,zipfile,hashlib
from pathlib import Path
from .framing_refinement import normalized
from footagepilot.__main__ import write
from footagepilot.resolve import verify,title_matches


def evaluate(before,after,old_job,new_job,media,drp,output,old_media):
    if output.exists():raise ValueError('Use a fresh typography evaluation directory')
    a=normalized(before);b=normalized(after)
    if a.get('titles')==b.get('titles') or {k:v for k,v in a.items() if k!='titles'}!={k:v for k,v in b.items() if k!='titles'}:raise ValueError('Expected a title-only revision')
    old=json.loads(old_job.read_text());job=json.loads(new_job.read_text())
    if old['manifest_sha256']!=hashlib.sha256(before.read_bytes()).hexdigest() or job['manifest_sha256']!=hashlib.sha256(after.read_bytes()).hexdigest():raise ValueError('Native jobs belong to different manifests')
    if [(s['start'],s['frames']) for s in old['shots']]!=[(s['start'],s['frames']) for s in job['shots']]:raise ValueError('Native shot timing changed')
    with zipfile.ZipFile(drp) as archive:
        if 'project.xml' not in archive.namelist() or archive.getinfo('project.xml').file_size>20_000_000 or job['project_name'].encode() not in archive.read('project.xml') or not any(p.startswith('SeqContainer/') for p in archive.namelist()):raise ValueError('Native DRP identity mismatch')
    report=verify(new_job,media,output/'native.json')
    try:title_matches(job,old_media)
    except ValueError as exc:error=str(exc)
    else:raise ValueError('Old-title control was not visually discriminative')
    result={'title_only':True,'native_visual_samples':len(report['visual_samples']),'titles':len(report['title_checks']),'title_timing_checks':len(report['title_timing_checks']),'old_title_control_rejected':error,'old_movie_sha256':hashlib.sha256(old_media.read_bytes()).hexdigest(),'audio':report['audio_correspondence'],'movie_sha256':report['sha256'],'drp_sha256':hashlib.sha256(drp.read_bytes()).hexdigest(),'creative_acceptance':'unreviewed','scope':'Native title contrast/size/timing and editable construction; not OCR, exact reference typography or human preference.'}
    write(output/'results.json',result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('before','after','old_job','new_job','media','drp'):p.add_argument(name,type=Path)
    p.add_argument('--old-media',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(evaluate(a.before,a.after,a.old_job,a.new_job,a.media,a.drp,a.output,a.old_media),indent=2))
