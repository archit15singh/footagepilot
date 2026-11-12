"""Retained planner/native plate evaluation; FFmpeg output is a negative control only."""
import argparse,copy,hashlib,json
from pathlib import Path
from footagepilot.__main__ import binary,run
from footagepilot.resolve import verify,plate_matches,visual_matches


def make_no_plate_control(job,missing):
    if any(job.get(k) for k in ('titles','backgrounds','overlays','transitions')):raise ValueError('No-plate control needs a cuts-only base')
    inputs=[v for shot in job['shots'] for v in ('-i',shot['path'])]
    normalize=';'.join(f'[{i}:v]setsar=1,setpts=PTS-STARTPTS[s{i}]' for i in range(len(job['shots'])))
    graph=normalize+';'+''.join(f'[s{i}]' for i in range(len(job['shots'])))+f"concat=n={len(job['shots'])}:v=1:a=0[v]"
    run([binary('ffmpeg'),'-v','error','-n',*inputs,'-filter_complex',graph,'-map','[v]','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',missing])
    return missing


def evaluate(directory,output):
    if output.exists():raise ValueError('Use a fresh planned-plate evaluation directory')
    state=json.loads((directory/'run.json').read_text());plan=json.loads((directory/'plan/plan.json').read_text())
    job_path=directory/'resolve-job/job.json';job=json.loads(job_path.read_text())
    if state.get('status')!='verified-export' or not state.get('passed'):raise ValueError('Recreation is not a completed verified export')
    if len(job.get('plates',[]))!=1 or len(plan.get('plates',[]))!=1:raise ValueError('This controlled evaluation needs exactly one planned/native plate')
    if any(job.get(k) for k in ('titles','backgrounds','overlays','transitions')):raise ValueError('No-plate control currently supports a cuts-only base')
    output.mkdir(parents=True);media=Path(state['output'])
    native=verify(job_path,media,output/'native.json')
    missing=make_no_plate_control(job,output/'missing-plate-control.mp4')
    absent=copy.deepcopy(job);absent['plates']=[]
    control_samples=visual_matches(absent,missing)
    try:plate_matches(job,missing)
    except ValueError as error:control_error=str(error)
    else:raise ValueError('Missing subtle plate was not rejected')
    if 'active pixels' not in control_error:raise ValueError('Control failed for a reason other than a missing plate')
    # Preserve evidence of the original broad-sampling weakness without altering thresholds.
    try:visual_matches(absent,media);broad_control_passed=True
    except ValueError:broad_control_passed=False
    plate=job['plates'][0];choice=plan['plates'][0];outgoing=job['shots'][choice['after_shot']]
    cut=outgoing['start']+outgoing['frames']
    if plate['start']!=cut-choice['pre_frames'] or plate['frames']!=choice['pre_frames']+choice['post_frames']:raise ValueError('Native plate is not anchored to the planned rounded cut')
    result={'planner':{'backend':plan['backend'],'model':plan['model'],'reasoning_effort':plan['reasoning_effort'],
                      'elapsed_seconds':plan['elapsed_seconds'],'main_asset_count':len(plan['asset_media']),
                      'plate_asset_count':len(plan['plate_media']),'chosen_plate':choice['asset_id'],
                      'cut_after_shot':choice['after_shot'],'pre_frames':choice['pre_frames'],'post_frames':choice['post_frames'],
                      'opacity':choice['opacity'],'source_start':choice['source_start']},
            'native':{'shots':len(job['shots']),'frames':job['frames'],'fps':job['fps'],'resolution':[job['width'],job['height']],
                      'plate_start':plate['start'],'cut_frame':cut,'plate_frames':plate['frames'],
                      'visual_samples':len(native['visual_samples']),'plate_checks':native['plate_checks'],
                      'audio':native['audio_correspondence'],'movie_sha256':native['sha256'],
                      'drp_sha256':state['native_project_sha256']},
            'broad_missing_expectation_passed':broad_control_passed,
            'no_plate_control_visual_samples':len(control_samples),
            'actual_no_plate_control_rejected':True,'control_error':control_error,
            'control_kind':'FFmpeg concatenation of the exact prepared main shots with no plate; negative control only, not a native product export',
            'creative_acceptance':'unreviewed','scope':'One supplied-asset choice and native Screen export; not automatic stock acquisition, refraction recreation or listening/creative acceptance'}
    (output/'results.json').write_text(json.dumps(result,indent=2)+'\n');return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(json.dumps(evaluate(a.directory,a.output),indent=2))
