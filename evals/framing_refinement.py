"""Evaluate a controlled focus-only revision and reject unchanged framing as a control."""
import argparse,copy,hashlib,json,zipfile
from pathlib import Path
from footagepilot.resolve import verify,visual_matches


def normalized(path):
    data=json.loads(path.read_text())
    for row in data['shots']+data.get('overlays',[]):row['path']=str((path.parent/row['path']).resolve())
    if data.get('music'):data['music']=str((path.parent/data['music']).resolve())
    return data


def evaluate(before,after,old_job,new_job,media,drp,output):
    if output.exists():raise ValueError('Use a new framing evaluation directory')
    baseline=normalized(before);candidate=normalized(after);restored=copy.deepcopy(candidate);changes=[]
    if len(baseline['shots'])!=len(candidate['shots']):raise ValueError('Shot count changed')
    for i,(a,b) in enumerate(zip(baseline['shots'],candidate['shots'])):
        for key in ('focus_x','focus_y'):
            if a.get(key,.5)!=b.get(key,.5):changes.append({'shot':i+1,'field':key,'before':a.get(key,.5),'after':b.get(key,.5)})
            if key in a:restored['shots'][i][key]=a[key]
            else:restored['shots'][i].pop(key,None)
    if restored!=baseline or not changes:raise ValueError('Expected a nonempty focus-only revision')
    old=json.loads(old_job.read_text());new=json.loads(new_job.read_text())
    if old.get('manifest_sha256')!=hashlib.sha256(before.read_bytes()).hexdigest() or new.get('manifest_sha256')!=hashlib.sha256(after.read_bytes()).hexdigest():raise ValueError('Native job belongs to a different manifest')
    if [(s['start'],s['frames']) for s in old['shots']]!=[(s['start'],s['frames']) for s in new['shots']]:raise ValueError('Native shot timing changed')
    with zipfile.ZipFile(drp) as archive:
        if 'project.xml' not in archive.namelist() or not any(p.startswith('SeqContainer/') for p in archive.namelist()):raise ValueError('Missing native project structure')
        if archive.getinfo('project.xml').file_size>20_000_000 or new['project_name'].encode() not in archive.read('project.xml'):raise ValueError('Native project identity mismatch')
    output.mkdir(parents=True)
    report=verify(new_job,media,output/'native.json')
    control=copy.deepcopy(new)
    for change in changes:
        i=change['shot']-1;control['shots'][i]['path']=old['shots'][i]['path']
    rejected=False;error=None
    try:visual_matches(control,media)
    except ValueError as exc:rejected=True;error=str(exc)
    if not rejected:raise ValueError('Unchanged-framing control was not visually discriminative')
    result={'focus_only_changes':changes,'native_visual_samples':len(report['visual_samples']),'control_rejected':rejected,'control_error':error,'audio':report['audio_correspondence'],'movie_sha256':report['sha256'],'drp_sha256':hashlib.sha256(drp.read_bytes()).hexdigest(),'creative_acceptance':'unreviewed','scope':'Focus-only structure and sampled rendered correspondence; not subject detection or a creative score'}
    (output/'results.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('old_job',type=Path);p.add_argument('new_job',type=Path);p.add_argument('media',type=Path);p.add_argument('drp',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(evaluate(a.before,a.after,a.old_job,a.new_job,a.media,a.drp,a.output),indent=2))
