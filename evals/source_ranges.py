"""Independent decoded-source correspondence for actual fill/contain no-zoom video excerpts."""
import argparse,json
from pathlib import Path
from footagepilot.__main__ import binary,write,probe,run
from footagepilot.resolve import raw,sample_frame,similarity,verify,visual_matches


def freeze_control(job,media,target):
    if target.exists():raise ValueError('Use a new frozen-opening control path')
    count=job['shots'][0]['frames']
    filt=f'[0:v]split=2[main][reference];[main][reference]freezeframes=first=0:last={count-1}:replace=0[v]'
    run([binary('ffmpeg'),'-v','error','-n','-i',media,'-filter_complex',filt,'-map','[v]','-map','0:a?','-c:v','libx264','-crf','18','-c:a','copy',target])
    run([binary('ffmpeg'),'-v','error','-i',target,'-f','null','-'])
    try:visual_matches(job,target)
    except ValueError as error:
        if 'differs visually' not in str(error):raise
        return {'control':'frozen-opening','rejected':True,'reason':str(error),'scope':'First native shot frozen for negative-control use only; not credited as a native render'}
    raise ValueError('Frozen-opening control is not discriminative for this source')


def evaluate(manifest,job_path,media,work,freeze_opening=False):
    if work.exists():raise ValueError('Use a fresh eval directory')
    work.mkdir(parents=True);edit=json.loads(manifest.read_text());job=json.loads(job_path.read_text());rows=[];wrong=[]
    if len(edit['shots'])!=len(job['shots']):raise ValueError('Manifest/job shot counts differ')
    for index,(shot,prepared) in enumerate(zip(edit['shots'],job['shots'])):
        if shot.get('fit') not in ('contain','fill') or shot.get('zoom',0):raise ValueError('Independent eval scope is fill/contain without artificial zoom')
        source=(manifest.parent/shot['path']).resolve();meta=probe(source);stream=next(s for s in meta['streams'] if s['codec_type']=='video')
        if shot['fit']=='contain':
            if stream['width']/stream['height']<job['width']/job['height']:raise ValueError('Contain eval supports full-width picture only')
            content_height=min(64,round(64*(job['width']/job['height'])/(stream['width']/stream['height'])));lo=(64-content_height)//2+1;hi=(64+content_height)//2-1
            filt=f"scale={job['width']}:{job['height']}:force_original_aspect_ratio=decrease,pad={job['width']}:{job['height']}:(ow-iw)/2:(oh-ih)/2:black"
        else:
            lo,hi=1,63
            filt=f"scale={job['width']}:{job['height']}:force_original_aspect_ratio=increase,crop={job['width']}:{job['height']}:'max(0,min(iw-ow,iw*{shot.get('focus_x',.5)}-ow/2))':'max(0,min(ih-oh,ih*{shot.get('focus_y',.5)}-oh/2))'"
        def content(pixels):return pixels[lo*64*3:hi*64*3]
        def frame(at):
            # Output-side seek decodes/discards from the original input; preparation uses input-side seek.
            data=raw([binary('ffmpeg'),'-v','error','-i',source,'-ss',at,'-frames:v','1','-vf',filt+',scale=64:64,format=rgb24','-f','rawvideo','-'])
            if len(data)!=64*64*3:raise ValueError('Missing independent source sample')
            return [v/255 for v in data]
        rate=stream.get('r_frame_rate','0/1').split('/');source_rate=float(rate[0])/float(rate[1])
        if not 1<=source_rate<=240:raise ValueError('Source frame rate cannot bound temporal quantization')
        average=stream.get('avg_frame_rate','0/1').split('/');average_rate=float(average[0])/float(average[1])
        if not 1<=average_rate<=240:raise ValueError('Invalid average source frame rate')
        quantum=max(1/source_rate,1/average_rate,1/job['fps'])
        for offset in (1,prepared['frames']//2,prepared['frames']-2):
            actual=sample_frame(prepared['path'],offset,job['fps']);requested=shot['source_start']+offset/job['fps']
            candidates=[]
            for delta in (-quantum,0,quantum):
                at=max(0,requested+delta);mae,corr=similarity(content(frame(at)),content(actual));candidates.append((mae,corr,at))
            mae,corr,matched=min(candidates,key=lambda r:r[0])
            rows.append({'shot':index+1,'source_seconds':round(requested,5),'matched_source_seconds':round(matched,5),'maximum_quantization_seconds':round(quantum,5),'mae':round(mae,5),'correlation':round(corr,5)})
            write(work/'source-samples.json',rows)
            if mae>.04 or corr<.95:raise ValueError('Prepared excerpt differs beyond nominal source/output frame quantization')
        mae,corr=similarity(content(frame(0)),content(sample_frame(prepared['path'],0,job['fps'])))
        wrong.append({'shot':index+1,'wrong_source_start':0,'rejected':not (mae<.04 and corr>.95),'mae':round(mae,5),'correlation':round(corr,5)})
    if not any(r['rejected'] for r in wrong):raise ValueError('All wrong-start controls are nondiscriminative')
    native=verify(job_path,media,work/'native.json')
    motion=freeze_control(job,media,work/'frozen-opening.mp4') if freeze_opening else None
    result={'passed':True,'motion_control':motion,'source_samples':rows,'wrong_start_controls':wrong,'native':native,'scope':'Selected source-time correspondence within nominal source/output frame quantization and native export; no creative acceptance'};write(work/'results.json',result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('manifest',type=Path);p.add_argument('job',type=Path);p.add_argument('media',type=Path);p.add_argument('--work',type=Path,required=True);p.add_argument('--freeze-opening',action='store_true');a=p.parse_args();print(json.dumps(evaluate(a.manifest,a.job,a.media,a.work,a.freeze_opening),indent=2))
