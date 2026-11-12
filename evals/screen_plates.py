"""Generate an original calibration plate and evaluate a native Screen export.

The diagonal light bands are an engineering fixture, not extracted reference VFX.
"""
import argparse,copy,hashlib,json,zipfile
from pathlib import Path
from footagepilot.__main__ import binary,run
from footagepilot.resolve import verify,expected_frame,sample_frame,similarity,visual_matches


def make_plate(target,frames=12,fps=30):
    if target.exists():raise ValueError('Use a fresh plate path')
    if type(frames) is not int or frames<3 or fps not in (24,30,60):raise ValueError('Plate needs at least three frames and supported FPS')
    target.parent.mkdir(parents=True,exist_ok=True)
    # Original moving diagonal light bands; black endpoints avoid a hard overlay edge.
    intensity=f'220*pow(sin(PI*N/{frames-1}),2)*lt(mod(X+2*Y+19*N,180),60)'
    run([binary('ffmpeg'),'-v','error','-n','-f','lavfi','-i',f'color=black:s=480x270:r={fps}',
         '-vf',f"geq=lum='{intensity}':cb=128:cr=128,gblur=sigma=1,scale=1920:1080",
         '-frames:v',frames,'-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',target])
    return {'frames':frames,'fps':fps,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'kind':'original procedural light-band calibration fixture; not a shard simulation or reference extraction'}


def make_glare(target):
    """An original soft moving light streak; no underlying refraction simulation."""
    if target.exists():raise ValueError('Use a fresh plate path')
    target.parent.mkdir(parents=True,exist_ok=True)
    intensity='16+205*pow(sin(PI*N/29),2)*exp(-pow((X+0.6*Y-12*N-60)/35,2))'
    run([binary('ffmpeg'),'-v','error','-n','-f','lavfi','-i','color=black:s=480x270:r=30',
         '-vf',f"geq=lum='{intensity}':cb=128:cr=128,scale=1920:1080",
         '-frames:v',30,'-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',target])
    return {'frames':30,'fps':30,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
            'kind':'original soft light streak; Screen light overlay, not glass refraction'}


def evaluate(job_path,media,drp,output):
    if output.exists():raise ValueError('Use a fresh plate evaluation directory')
    job=json.loads(job_path.read_text())
    if len(job.get('plates',[]))!=1:raise ValueError('This controlled evaluation needs exactly one plate')
    with zipfile.ZipFile(drp) as archive:
        if 'project.xml' not in archive.namelist() or not any(p.startswith('SeqContainer/') for p in archive.namelist()):raise ValueError('Missing native project structure')
        if archive.getinfo('project.xml').file_size>20_000_000 or job['project_name'].encode() not in archive.read('project.xml'):raise ValueError('Native project identity mismatch')
    output.mkdir(parents=True)
    report=verify(job_path,media,output/'native.json');plate=job['plates'][0];samples=[]
    for number in range(plate['start'],plate['start']+plate['frames']):
        mae,corr=similarity(expected_frame(job,number),sample_frame(media,number,job['fps']))
        if mae>.08 or corr<.90:raise ValueError('Dense plate correspondence failed')
        samples.append({'frame':number,'mean_absolute_error':mae,'correlation':corr})
    control=copy.deepcopy(job);control['plates']=[]
    try:visual_matches(control,media)
    except ValueError as exc:missing_error=str(exc)
    else:raise ValueError('Missing-plate control was not discriminative')
    # Test a distinct wrong blend model at peak: normal opaque plate over the base.
    number=plate['start']+plate['frames']//2
    base=expected_frame(control,number);layer=sample_frame(plate['path'],number-plate['start'],job['fps'])
    wrong=[a*(1-plate['opacity'])+b*plate['opacity'] for a,b in zip(base,layer)]
    mae,corr=similarity(wrong,sample_frame(media,number,job['fps']))
    if mae<=.08 and corr>=.90:raise ValueError('Normal-blend control was not discriminative')
    result={'native_visual_samples':len(report['visual_samples']),'all_plate_frame_samples':samples,'missing_plate_rejected':True,'missing_plate_error':missing_error,'normal_blend_control':{'mean_absolute_error':mae,'correlation':corr,'rejected':True},'audio':report['audio_correspondence'],'movie_sha256':report['sha256'],'drp_sha256':hashlib.sha256(drp.read_bytes()).hexdigest(),'creative_acceptance':'unreviewed','scope':'One controlled native Screen plate at fractional opacity; sampled RGB model, not all blend modes, reference matching or musical judgment'}
    (output/'results.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    gen=sub.add_parser('make-plate');gen.add_argument('target',type=Path)
    glare=sub.add_parser('make-glare');glare.add_argument('target',type=Path)
    check=sub.add_parser('evaluate');check.add_argument('job',type=Path);check.add_argument('media',type=Path);check.add_argument('drp',type=Path);check.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(make_plate(a.target) if a.command=='make-plate' else make_glare(a.target) if a.command=='make-glare' else evaluate(a.job,a.media,a.drp,a.output),indent=2))
