"""Native progressive layout positive plus a decodable missing-tile negative control."""
import argparse,hashlib,json
from pathlib import Path
from footagepilot.__main__ import binary,run,write
from footagepilot.layout import rectangle
from footagepilot.resolve import visual_matches


def evaluate(job_path,media,positive_path,work):
    if work.exists():raise ValueError('Use a fresh evaluation directory')
    work.mkdir(parents=True);job=json.loads(job_path.read_text());positive=json.loads(positive_path.read_text())
    if not positive.get('technical_pass') or positive.get('sha256')!=hashlib.sha256(media.read_bytes()).hexdigest():raise ValueError('Supply the actual verified native movie/report pair')
    panel=job['overlays'][-1];left,top,right,bottom=rectangle(panel);start=panel['start']/job['fps'];end=(panel['start']+panel['frames'])/job['fps']
    removed=work/'missing-final-panel.mp4'
    filt=f"drawbox=x={round(left*job['width'])}:y={round(top*job['height'])}:w={round((right-left)*job['width'])}:h={round((bottom-top)*job['height'])}:color=black:t=fill:enable='between(t,{start},{end})'"
    run([binary('ffmpeg'),'-v','error','-n','-i',media,'-vf',filt,'-c:v','libx264','-preset','fast','-crf','18','-c:a','copy',removed])
    # Decodes and retains the native output timing/audio; only the final tile is erased.
    run([binary('ffmpeg'),'-v','error','-i',removed,'-f','null','-'])
    try:visual_matches(job,removed)
    except ValueError as error:
        if not any(s in str(error) for s in ('differs visually','differs from its planned asset')):raise
        negative={'control':'erased-final-panel','rejected':True,'reason':str(error),'construction':'FFmpeg modification for negative-control use only; not credited as a native render'}
    else:raise ValueError('Missing-panel control was accepted')
    result={'passed':True,'native_sample_count':len(positive['visual_samples']),'minimum_correlation':min(r['correlation'] for r in positive['visual_samples']),'panels':len(job['overlays']),'distinct_arrivals':len({r['start'] for r in job['overlays']}),'background_spans':len(job.get('backgrounds',[])),'negative_control':negative,'scope':'Native layout correspondence and missing-layer rejection; no creative acceptance'};write(work/'results.json',result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('job',type=Path);p.add_argument('media',type=Path);p.add_argument('positive',type=Path);p.add_argument('--work',type=Path,required=True);a=p.parse_args();print(json.dumps(evaluate(a.job,a.media,a.positive,a.work),indent=2))
