"""Independent decoded-source correspondence for actual contain/no-zoom video excerpts."""
import argparse,json
from pathlib import Path
from footagepilot.__main__ import binary,write,probe
from footagepilot.resolve import raw,sample_frame,similarity,verify


def evaluate(manifest,job_path,media,work):
    if work.exists():raise ValueError('Use a fresh eval directory')
    work.mkdir(parents=True);edit=json.loads(manifest.read_text());job=json.loads(job_path.read_text());rows=[];wrong=[]
    if len(edit['shots'])!=len(job['shots']):raise ValueError('Manifest/job shot counts differ')
    for index,(shot,prepared) in enumerate(zip(edit['shots'],job['shots'])):
        if shot.get('fit')!='contain' or shot.get('zoom',0):raise ValueError('Independent eval scope is contain/no-zoom')
        source=(manifest.parent/shot['path']).resolve();meta=probe(source);stream=next(s for s in meta['streams'] if s['codec_type']=='video')
        if stream['width']/stream['height']<job['width']/job['height']:raise ValueError('Eval supports full-width contained video only')
        content_height=min(64,round(64*(job['width']/job['height'])/(stream['width']/stream['height'])));lo=(64-content_height)//2+1;hi=(64+content_height)//2-1
        def content(pixels):return pixels[lo*64*3:hi*64*3]
        def frame(at):
            # Output-side seek decodes/discards from the original input; preparation uses input-side seek.
            data=raw([binary('ffmpeg'),'-v','error','-i',source,'-ss',at,'-frames:v','1','-vf',f"scale={job['width']}:{job['height']}:force_original_aspect_ratio=decrease,pad={job['width']}:{job['height']}:(ow-iw)/2:(oh-ih)/2:black,scale=64:64,format=rgb24",'-f','rawvideo','-'])
            if len(data)!=64*64*3:raise ValueError('Missing independent source sample')
            return [v/255 for v in data]
        for offset in (1,prepared['frames']//2,prepared['frames']-2):
            actual=sample_frame(prepared['path'],offset,job['fps']);mae,corr=similarity(content(frame(shot['source_start']+offset/job['fps'])),content(actual))
            if mae>.04 or corr<.95:raise ValueError('Prepared excerpt does not match original source timestamp')
            rows.append({'shot':index+1,'source_seconds':round(shot['source_start']+offset/job['fps'],5),'mae':round(mae,5),'correlation':round(corr,5)})
        mae,corr=similarity(content(frame(0)),content(sample_frame(prepared['path'],0,job['fps'])))
        wrong.append({'shot':index+1,'wrong_source_start':0,'rejected':not (mae<.04 and corr>.95),'mae':round(mae,5),'correlation':round(corr,5)})
    if not any(r['rejected'] for r in wrong):raise ValueError('All wrong-start controls are nondiscriminative')
    native=verify(job_path,media,work/'native.json')
    result={'passed':True,'source_samples':rows,'wrong_start_controls':wrong,'native':native,'scope':'Actual selected source-time correspondence and native export; not a finished creative recreation'};write(work/'results.json',result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('manifest',type=Path);p.add_argument('job',type=Path);p.add_argument('media',type=Path);p.add_argument('--work',type=Path,required=True);a=p.parse_args();print(json.dumps(evaluate(a.manifest,a.job,a.media,a.work),indent=2))
