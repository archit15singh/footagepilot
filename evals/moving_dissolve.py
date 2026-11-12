"""Independent source-handle samples for an actual native moving dissolve."""
import argparse,json
from pathlib import Path
from footagepilot.__main__ import binary,probe,write,run
from footagepilot.resolve import raw,sample_frame,similarity,verify,visual_matches


def frozen_control(job,media,output):
    t=next(t for t in job['transitions'] if t.get('filter')=='transition_moving_dissolve');frozen=output/'frozen-handle.mp4'
    run([binary('ffmpeg'),'-v','error','-n','-i',t['path'],'-vf',f"trim=end_frame=1,loop=-1:1:0,setpts=N/({job['fps']}*TB)",'-an','-frames:v',t['frames'],'-c:v','libx264','-crf','18','-pix_fmt','yuv420p',frozen])
    run([binary('ffmpeg'),'-v','error','-i',frozen,'-f','null','-'])
    mae,corr=similarity(sample_frame(t['path'],t['frames']-1,job['fps']),sample_frame(frozen,t['frames']-1,job['fps']))
    if not (mae>.04 or corr<.95):raise ValueError('Frozen-handle source control is nondiscriminative')
    wrong={**job,'transitions':[{**r,'path':str(frozen)} if r is t else r for r in job['transitions']]}
    try:visual_matches(wrong,media)
    except ValueError as error:
        if 'differs visually' not in str(error):raise
        result={'decoded':True,'source_control_rejected':True,'last_frame_mae':mae,'correlation':corr,'frozen_reference_rejected':True,'reason':str(error),'scope':'Frozen proxy replaces only the expected handle; actual native film stays unchanged, no alternate movie credited as native'}
        write(output/'frozen-control.json',result);return result
    raise ValueError('Native QA accepted frozen expected handle')


def evaluate(manifest,job_path,media,output):
    if output.exists():raise ValueError('Use a new evaluation directory')
    output.mkdir(parents=True);edit=json.loads(manifest.read_text());job=json.loads(job_path.read_text());rows=[]
    transitions=[t for t in job['transitions'] if t.get('filter')=='transition_moving_dissolve']
    if len(transitions)!=1:raise ValueError('Source-handle evaluation requires exactly one moving dissolve')
    for t in transitions:
        shot=edit['shots'][t['after_shot']+1];main=job['shots'][t['after_shot']+1];source=(manifest.parent/shot['path']).resolve()
        if shot.get('fit','fill')!='fill' or shot.get('zoom',0):raise ValueError('Independent eval supports fill without artificial zoom')
        stream=next(s for s in probe(source)['streams'] if s['codec_type']=='video')
        def rate(value):a,b=value.split('/');return float(a)/float(b)
        quantum=max(1/job['fps'],1/rate(stream['avg_frame_rate']),1/rate(stream['r_frame_rate']))
        filt=f"scale={job['width']}:{job['height']}:force_original_aspect_ratio=increase,crop={job['width']}:{job['height']}:'max(0,min(iw-ow,iw*{shot.get('focus_x',.5)}-ow/2))':'max(0,min(ih-oh,ih*{shot.get('focus_y',.5)}-oh/2))',scale=64:64,format=rgb24"
        def original(at):
            data=raw([binary('ffmpeg'),'-v','error','-cpuflags','0','-i',source,'-ss',at,'-frames:v','1','-vf',filt,'-f','rawvideo','-'])
            if len(data)!=64*64*3:raise ValueError('Missing original-source sample')
            return [v/255 for v in data]
        for label,proxy,start,numbers in [('handle',t['path'],t['source_start'],[0,t['frames']//2,t['frames']-1]),('main',main['path'],main['source_start'],[0,1])]:
            for number in numbers:
                at=start+number/job['fps'];actual=sample_frame(proxy,number,job['fps']);choices=[]
                for delta in (-quantum,0,quantum):
                    when=max(0,at+delta);mae,corr=similarity(original(when),actual);choices.append((mae,corr,when))
                mae,corr,matched=min(choices,key=lambda x:x[0]);rows.append({'part':label,'frame':number,'requested_source_seconds':at,'matched_source_seconds':matched,'tolerance_seconds':quantum,'mae':mae,'correlation':corr});write(output/'source-samples.json',rows)
                if mae>.04 or corr<.95:raise ValueError('Moving handle/main differs from original source beyond frame quantization')
        first=sample_frame(t['path'],0,job['fps']);last=sample_frame(t['path'],t['frames']-1,job['fps']);mae,corr=similarity(first,last)
        frozen={'last_handle_vs_frozen_first_mae':mae,'correlation':corr,'rejected_at_existing_source_threshold':mae>.04 or corr<.95}
        if abs(t['source_start']+t['frames']/job['fps']-main['source_start'])>1e-6:raise ValueError('Source handle does not meet main excerpt')
    native=verify(job_path,media,output/'native.json')
    result={'passed':True,'source_samples':rows,'frozen_first_frame_diagnostic':frozen,'frozen_control':frozen_control(job,media,output),'native_visual_samples':len(native['visual_samples']),'scope':'Nominal source-time continuity and native sampled compositing, not exact PTS identity or creative smoothness'};write(output/'results.json',result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('manifest',type=Path);p.add_argument('job',type=Path);p.add_argument('media',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(evaluate(a.manifest,a.job,a.media,a.output),indent=2))
