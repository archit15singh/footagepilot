"""Local reference evidence: frames, scene changes and audio transients."""
import array
import hashlib
import html
import json
import math
import os
import re
import shutil
import statistics
import subprocess
import sys
from bisect import bisect_left
from pathlib import Path
from urllib.parse import urlsplit
from .__main__ import binary, probe, write
from .reference_timing import decoded_frames, estimate_pulse, frame_selection, transition_timing


def execute(args, timeout=180):
    result = subprocess.run([str(x) for x in args], capture_output=True, timeout=timeout)
    if result.returncode:
        raise ValueError(result.stderr.decode(errors='replace')[-3000:])
    return result


def instagram_url(value):
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or parsed.hostname not in ('instagram.com', 'www.instagram.com') or parsed.username or parsed.password or parsed.port:
        raise ValueError('Use an HTTPS instagram.com reel/post URL or a local video')
    if not re.fullmatch(r'/(?:[A-Za-z0-9_.]+/)?(?:reel|reels|p)/[A-Za-z0-9_-]+/?', parsed.path):
        raise ValueError('Expected one Instagram reel/post, not a feed or collection')
    return 'https://www.instagram.com' + parsed.path


def audio_events(samples, rate=8000):
    """Energy novelty candidates, NOT a musical beat tracker."""
    hop = rate // 100
    energy = [math.sqrt(sum(v*v for v in samples[i:i+hop])/len(samples[i:i+hop])) for i in range(0,len(samples),hop)]
    novelty = [max(0, v-statistics.mean(energy[max(0,i-10):i] or [v])) for i,v in enumerate(energy)]
    selected=[]
    for i in range(1,len(novelty)-1):
        local=novelty[max(0,i-50):min(len(novelty),i+51)]
        threshold=max(.008,statistics.mean(local)*2.5)
        if novelty[i]>threshold and novelty[i]>=novelty[i-1] and novelty[i]>novelty[i+1]:
            event={'time':round(i*.01,3),'strength':round(novelty[i],5)}
            if selected and event['time']-selected[-1]['time']<.16:
                if event['strength']>selected[-1]['strength']:selected[-1]=event
            else:selected.append(event)
    return energy,selected


def cut_alignment(cuts, events):
    return [{'time':t,'nearest_onset':min((e['time'] for e in events),key=lambda x:abs(x-t),default=None),
             'offset_seconds':round(min((abs(e['time']-t) for e in events),default=math.inf),4) if events else None} for t in cuts]


def make_report(root, data):
    # Only generated numeric timestamps and escaped strings enter markup.
    tiles=''.join(f'<button class="frame" data-time="{f["time"]}"><img loading="lazy" src="{f["file"]}" alt="Frame at {f["time"]:.2f} seconds"><span>{f["time"]:.2f}s · {html.escape(f["kind"])}</span></button>' for f in data['frames'])
    def offset(value):
        return '—' if value is None else f'{value*1000:+.0f} ms'
    rows=''.join(f'<tr><td><button data-time="{c["time"]}">{c["time"]:.3f}s</button></td><td>{c["frame_index"]+1}</td>'
                 f'<td>{offset(c["cut_minus_onset_seconds"])}</td><td>{offset(c["cut_minus_pulse_seconds"])}</td></tr>'
                 for c in data['transitions'])
    timeline=data['frame_timeline']
    audio=data['audio'];energy=audio['energy'];maximum=max(energy,default=1) or 1;duration=data['duration']
    points=' '.join(f'{i*.01/duration*1000:.2f},{100-v/maximum*90:.2f}' for i,v in enumerate(energy))
    change_max=max(row['change'] for row in timeline) or 1
    changes=' '.join(f'{row["time"]/duration*1000:.2f},{100-row["change"]/change_max*90:.2f}' for row in timeline)
    marks=''.join(f'<line x1="{t/duration*1000:.2f}" x2="{t/duration*1000:.2f}" y1="0" y2="100" stroke="#ffbb79"/>' for t in data['scene_changes'])
    onsets=''.join(f'<circle cx="{e["time"]/duration*1000:.2f}" cy="95" r="3" fill="#a8d7ff"/>' for e in audio['onsets'])
    pulse=audio['pulse']
    pulses=''.join(f'<circle cx="{t/duration*1000:.2f}" cy="85" r="3" fill="#e6afff"/>' for t in pulse['times'])
    pulse_label=f'Estimated pulse {pulse["bpm"]} BPM' if pulse['status']=='estimated' else 'No reliable constant pulse'
    body='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FootagePilot reference analysis</title><style>:root{color-scheme:dark;font:16px/1.5 system-ui;background:#101512;color:#e9eee9}body{max-width:1200px;margin:30px auto;padding:0 20px}video{width:100%;max-height:550px;background:#000}h1{font-size:36px}button,a{color:#d6eeb9}button{background:#243126;border:1px solid #52634a;border-radius:6px;padding:8px;cursor:pointer}button:focus-visible{outline:3px solid #fff}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}.frame{padding:0;overflow:hidden}.frame img{display:block;width:100%;height:210px;object-fit:contain;background:#080a08}.frame span{display:block;padding:5px;font-size:12px}svg{width:100%;height:130px;background:#1d261f}table{border-collapse:collapse}td,th{padding:8px;border-bottom:1px solid #435342;text-align:left}.muted{color:#b3c0b4}details{margin:25px 0}</style><h1>Reference → editing evidence</h1><p class="muted">Local media · Scene changes are candidates · Audio peaks can include music, speech and effects</p><video id="video" controls preload="metadata" src="media.mp4"></video>'''
    body+=f'<p>{duration:.2f}s · {data["width"]}×{data["height"]} · {len(timeline)} decoded frames · {pulse_label}</p>'
    body+='<p><button id="prev">Previous frame</button> <button id="next">Next frame</button> <output id="frame-status" aria-live="polite"></output></p>'
    body+='<h2>Timing map</h2><p>Orange lines mark change candidates. The amber curve shows frame difference. Blue dots mark audio onsets, purple dots mark estimated pulses, and the green curve shows RMS energy.</p><svg id="map" viewBox="0 0 1000 100" preserveAspectRatio="none" role="img" aria-label="Frame changes and audio timing"><polyline fill="none" stroke="#a5c985" points="'+points+'"/><polyline fill="none" stroke="#bb8e4f" points="'+changes+'"/>'+marks+onsets+pulses+'</svg>'
    body+='<h2>Visual changes and audio timing</h2><p>Positive offsets mean the frame change follows the audio marker. Review neighboring frames and listen before attributing a change to music.</p><table><tr><th>Visual change</th><th>Frame</th><th>From onset</th><th>From pulse</th></tr>'+rows+'</table>'
    body+='<h2>Frame samples</h2><p>Regular samples and neighboring decoded frames around change candidates.</p><div class="grid">'+tiles+'</div><p><a href="analysis.json">Machine-readable analysis</a> · <a href="contact.jpg">Overview contact sheet</a></p>'
    body+='<script id="timeline" type="application/json">'+json.dumps([row['time'] for row in timeline],separators=(',',':'))+'</script>'
    body+='''<script>
const v = document.querySelector("video");
const frames = JSON.parse(document.querySelector("#timeline").textContent);
const status = document.querySelector("#frame-status");
let pendingFrame;
function seek(time) {
    pendingFrame = undefined;
    v.currentTime = time;
}
function frameAt(time) {
    let low = 0, high = frames.length;
    while (low < high) {
        const mid = (low + high) >>> 1;
        if (frames[mid] <= time + 0.000001) low = mid + 1;
        else high = mid;
    }
    return Math.max(0, low - 1);
}
function showFrame(i) {
    status.textContent = 'Frame ' + (i + 1) + ' / ' + frames.length + ' · ' + frames[i].toFixed(6) + ' s';
}
function step(direction) {
    if (!v.readyState) return;
    v.pause();
    const current = pendingFrame ?? frameAt(v.currentTime);
    const i = Math.min(frames.length - 1, Math.max(0, current + direction));
    pendingFrame = i;
    // Seek inside the frame's presentation interval to avoid timestamp rounding at its edge.
    v.currentTime = frames[i] + Math.max(0, Math.min(0.002, ((frames[i + 1] ?? v.duration) - frames[i]) / 2));
    showFrame(i);
}
v.addEventListener('seeked', () => { pendingFrame = undefined; showFrame(frameAt(v.currentTime)); });
v.addEventListener('timeupdate', () => showFrame(pendingFrame ?? frameAt(v.currentTime)));
document.querySelector('#prev').onclick = () => step(-1);
document.querySelector('#next').onclick = () => step(1);
document.querySelectorAll('[data-time]').forEach(b => b.onclick = () => {
    seek(Number(b.dataset.time));
    v.scrollIntoView({block: 'center', behavior: 'smooth'});
});
document.querySelector('#map').onclick = e => {
    const bounds = e.currentTarget.getBoundingClientRect();
    if (v.readyState) seek((e.clientX - bounds.left) / bounds.width * v.duration);
};
showFrame(0);
</script></html>'''
    (root/'index.html').write_text(body)


def analyze_reference(source, output, interval=1., threshold=.28, max_duration=180., browser=None):
    if not math.isfinite(interval) or not .25<=interval<=10:raise ValueError('Frame interval must be 0.25–10 seconds')
    if not math.isfinite(threshold) or not .05<=threshold<=.9:raise ValueError('Scene threshold must be 0.05–0.9')
    if not math.isfinite(max_duration) or not 1<=max_duration<=600:raise ValueError('Maximum duration must be 1–600 seconds')
    url=instagram_url(source) if '://' in source else None
    local=Path(source).resolve() if not url else None
    if local and not local.is_file():raise ValueError('Local video missing')
    if output.exists():raise ValueError('Use a new reference output directory to preserve earlier evidence')
    output.mkdir(parents=True);(output/'frames').mkdir()
    try:
        media=output/'media.mp4'
        if url:
            downloader=os.environ.get('FOOTAGEPILOT_YT_DLP') or shutil.which('yt-dlp')
            if not downloader:raise ValueError('yt-dlp missing; set FOOTAGEPILOT_YT_DLP or add yt-dlp to PATH')
            args=[downloader,'--ignore-config','--no-playlist','--no-progress','--no-overwrites','--max-filesize','150M','--match-filter',f'duration <=? {max_duration}','-f','best[ext=mp4]/best','-o',media]
            if browser:args+=['--cookies-from-browser',browser]
            result=execute(args+[url],timeout=180);(output/'download.log').write_bytes(result.stdout+result.stderr)
            if not media.exists():raise ValueError('Downloader produced no media (possibly duration/size limit)')
        else:shutil.copyfile(local,media)
        snapshot=hashlib.sha256(media.read_bytes()).hexdigest();meta=probe(media)
        duration=float(meta['format']['duration']);video=next(s for s in meta['streams'] if s['codec_type']=='video')
        if not 0<duration<=max_duration:raise ValueError('Reference exceeds configured duration limit')
        ff=binary('ffmpeg')
        execute([ff,'-v','error','-i',media,'-f','null','-'])
        frame_log=execute([ff,'-v','error','-i',media,'-map','0:v:0','-an','-vf',
                           'scale=160:-2,settb=1/1000000,scdet,metadata=mode=print:file=-:direct=1',
                           '-fps_mode','passthrough','-f','null','-']).stdout.decode()
        timeline=decoded_frames(frame_log)
        result=execute([ff,'-hide_banner','-i',media,'-map','0:v:0','-an','-vf',f"settb=1/1000000,select='gt(scene,{threshold})',showinfo",'-fps_mode','passthrough','-f','null','-'])
        cuts=sorted(set(int(x)/1_000_000 for x in re.findall(r'\bpts:\s*(-?\d+)',result.stderr.decode(errors='replace'))))
        cuts=[t for t in cuts if 0<t<duration]
        # Bounded reports: select strongest scope by limiting count, never silently drop cuts.
        if len(cuts)>150:raise ValueError('More than 150 scene candidates; raise scene threshold')
        fps_text=video.get('avg_frame_rate','30/1').split('/');fps=float(fps_text[0])/float(fps_text[1]) if len(fps_text)==2 and float(fps_text[1]) else 30
        audio={'present':any(s['codec_type']=='audio' for s in meta['streams']),'energy':[],'onsets':[],'method':'10 ms RMS energy novelty; not musical beat tracking'}
        if audio['present']:
            raw=execute([ff,'-v','error','-i',media,'-map','0:a:0','-af','aresample=8000:async=1:first_pts=0','-ac','1','-ar','8000','-f','f32le','-']).stdout
            samples=array.array('f');samples.frombytes(raw)
            if sys.byteorder!='little':samples.byteswap()
            values,onsets=audio_events(samples);audio.update(energy=[round(x,5) for x in values],onsets=onsets)
        audio['pulse']=estimate_pulse(audio['onsets'])
        transitions=transition_timing(cuts,timeline,audio['onsets'],audio['pulse'])
        timestamps=[row['time'] for row in timeline]
        selected={min(len(timeline)-1,bisect_left(timestamps,i*interval)):'regular'
                  for i in range(math.ceil(duration/interval))}
        for row in transitions:
            index=row['frame_index']
            for offset,kind in [(-1,'before cut'),(1,'after cut'),(0,'at cut')]:
                if 0<=index+offset<len(timeline):
                    selected[index+offset]=kind
        for row in transitions:
            selected[row['frame_index']]='at cut'
        # Use decoded ordinals so JPEGs correspond to the recorded source PTS, including VFR.
        indices=sorted(selected)
        selection=frame_selection(indices)
        execute([ff,'-v','error','-y','-i',media,'-map','0:v:0','-an','-vf',
                 f"select='{selection}',scale=320:-2:out_range=full,format=yuvj420p",
                 '-fps_mode','passthrough','-start_number','0',output/'frames/%04d.jpg'])
        frames=[]
        for i,index in enumerate(indices):
            filename=f'frames/{i:04d}.jpg'
            if not (output/filename).is_file():raise ValueError(f'No sample for decoded frame {index}')
            frames.append({'time':timestamps[index],'file':filename,'kind':selected[index],'frame_index':index})
        execute([ff,'-v','error','-y','-i',media,'-vf',f'fps=1/{max(duration/24,.25)},scale=160:-2:out_range=full,format=yuvj420p,tile=6x4','-frames:v','1',output/'contact.jpg'])
        if hashlib.sha256(media.read_bytes()).hexdigest()!=snapshot:raise ValueError('Reference changed during analysis')
        data={'schema_version':2,'source_kind':'instagram' if url else 'local','source_url':url,'source_sha256':snapshot,'duration':duration,'width':video['width'],'height':video['height'],'fps':fps,'scene_threshold':threshold,'scene_changes':cuts,'frame_timeline':timeline,'transitions':transitions,'audio':audio,'cut_audio_alignment':cut_alignment(cuts,audio['onsets']),'frames':frames,'decode':'passed','tools':{'ffmpeg':execute([ff,'-version']).stdout.decode().splitlines()[0]},'limitations':['Sampled frames can miss fast actions.','Scene changes are candidates, not transition classifications.','Audio onsets may be speech/SFX; beat and phrase interpretation needs listening.']}
        write(output/'analysis.json',data);make_report(output,data);write(output/'complete.json',{'passed':True,'source_sha256':snapshot,'frames':len(frames),'report':'index.html'})
        return {'report':str(output/'index.html'),'duration':duration,'frames':len(frames),'cuts':len(cuts),'audio_onsets':len(audio['onsets']),'decoded_frames':len(timeline),'pulse_status':audio['pulse']['status']}
    except Exception as error:
        write(output/'failure.json',{'passed':False,'error':str(error)});raise
