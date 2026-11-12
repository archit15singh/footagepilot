"""Verify transferred reference change coordinates against a native rendered film."""
import argparse,copy,json
from decimal import Decimal,ROUND_HALF_UP
from pathlib import Path
from footagepilot.__main__ import write
from footagepilot.reference_rhythm import validate_reference_timing
from footagepilot.resolve import verify,visual_matches


def check_coordinates(timing,job):
    expected=[int((Decimal(str(t))*job['fps']).quantize(Decimal(1),rounding=ROUND_HALF_UP)) for t in timing['cues']]
    actual=[s['start'] for s in job['shots']]+[job['frames']]
    if job.get('timing_mode')!='reference_changes' or expected!=actual:raise ValueError('Native shot boundaries differ from transferred reference coordinates')
    return expected


def evaluate(analysis,rhythm,job_path,media,output):
    if output.exists():raise ValueError('Use a fresh reference rhythm evaluation directory')
    timing=json.loads(rhythm.read_text())['music_timing'];validate_reference_timing(timing,analysis,analysis.parent/'media.mp4')
    job=json.loads(job_path.read_text());coordinates=check_coordinates(timing,job)
    report=verify(job_path,media,output/'native.json')
    control=copy.deepcopy(job)
    # Wrong source at the first rapid section must not pass mere timing/decode checks.
    index=min(4,len(job['shots'])-1);control['shots'][index]['path']=control['shots'][index-1]['path']
    try:visual_matches(control,media)
    except ValueError as exc:error=str(exc)
    else:raise ValueError('Wrong-shot control was not visually discriminative')
    result={'shot_count':len(job['shots']),'reference_coordinates':timing['cues'],'native_frame_boundaries':coordinates,
        'maximum_quantization_seconds':max(abs(f/job['fps']-t) for f,t in zip(coordinates,timing['cues'])),
        'native_visual_samples':len(report['visual_samples']),'wrong_shot_control_rejected':error,
        'audio':report['audio_correspondence'],'movie_sha256':report['sha256'],'creative_acceptance':'unreviewed',
        'limits':['Scene changes remain candidates; missed or false boundaries are possible.','Sampled correspondence is not continuous visual or listening verification.','Transferred pacing does not recreate the reference subject, performance or grade.']}
    write(output/'results.json',result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('analysis',type=Path);p.add_argument('rhythm',type=Path);p.add_argument('job',type=Path);p.add_argument('media',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(evaluate(a.analysis,a.rhythm,a.job,a.media,a.output),indent=2))
