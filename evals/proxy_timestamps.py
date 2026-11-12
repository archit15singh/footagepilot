"""Check zero-origin prepared media and reject a known shifted native precursor."""
import argparse,json
from pathlib import Path
from footagepilot.__main__ import probe,write
from footagepilot.resolve import plate_matches,verify


def evaluate(job_path,media,precursor,output):
    if output.exists():raise ValueError('Use a fresh evaluation output directory')
    job=json.loads(job_path.read_text());paths={r['path'] for key in ('shots','overlays','backgrounds','transitions','plates') for r in job.get(key,[])}
    origins=[]
    for path in sorted(paths):
        stream=next(s for s in probe(Path(path))['streams'] if s['codec_type']=='video')
        start=float(stream.get('start_time',0))
        if abs(start)>1e-6:raise ValueError('Prepared video has a nonzero timestamp origin')
        origins.append(start)
    report=verify(job_path,media,output/'native.json')
    # The rejected output is supplied explicitly; never hide a failed run.
    try:plate_matches(job,precursor)
    except ValueError as exc:error=str(exc)
    else:raise ValueError('Shifted precursor unexpectedly passed the plate gate')
    result={'zero_origin_proxy_count':len(origins),'origins':origins,'prior_native_rejected':error,
        'native_visual_samples':len(report['visual_samples']),'plate_checks':report['plate_checks'],
        'audio':report['audio_correspondence'],'movie_sha256':report['sha256'],
        'creative_acceptance':'unreviewed','scope':'Sampled native plate correspondence and proxy timestamps; not continuous subject safety or listening.'}
    write(output/'results.json',result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('job',type=Path);p.add_argument('media',type=Path);p.add_argument('precursor',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(evaluate(a.job,a.media,a.precursor,a.output),indent=2))
