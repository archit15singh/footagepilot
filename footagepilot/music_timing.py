"""Explicit timing coordinates: authored tempo or source-bound audio cue candidates."""
import array,hashlib,math,subprocess,sys
from decimal import Decimal
from pathlib import Path
from .__main__ import binary,probe,write


def analysis_options(spec,backend):
    """Explicit opt-in; an analysis request never silently replaces authored timing."""
    if 'music_analysis' not in spec:return None
    request=spec['music_analysis']
    if backend!='resolve':raise ValueError('Automatic music analysis requires Resolve')
    if 'music_timing' in spec:raise ValueError('Choose music_analysis or music_timing, not both')
    if not isinstance(request,dict) or set(request)-{'max_duration','min_gap'}:raise ValueError('Unknown music_analysis options')
    duration=request.get('max_duration',spec.get('max_seconds',20));gap=request.get('min_gap',.3)
    if type(duration) not in (int,float) or not math.isfinite(duration) or not 1<=duration<=600 or type(gap) not in (int,float) or not math.isfinite(gap) or not .15<=gap<=2:raise ValueError('Music analysis duration1–600s and minimum gap.15–2s required')
    if duration<spec.get('max_seconds',20):raise ValueError('Music analysis must cover max_seconds')
    return {'max_duration':duration,'min_gap':gap}


def validate_timing(timing,music=None,zero=False):
    def number(v):return type(v) in (int,float) and math.isfinite(v)
    if not isinstance(timing,dict) or not isinstance(timing.get('provenance'),str) or not timing['provenance'].strip():raise ValueError('Music timing needs provenance')
    if 'cues' in timing:
        cues=timing['cues']
        if timing.get('mode') not in ('onset_candidates','reviewed_cues','reference_changes') or not isinstance(cues,list) or not 3<=len(cues)<=1201 or any(not number(v) or not 0<=v<=600 for v in cues) or cues[0]!=0 or any(b-a<.099999 for a,b in zip(cues,cues[1:])):raise ValueError('Use 3–1201 ordered audio cues starting at zero, at least .1s apart')
        if 'bpm' in timing or timing.get('offset',0)!=0:raise ValueError('Cue timing cannot also specify BPM or an offset')
        digest=timing.get('source_sha256')
        if not isinstance(digest,str) or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):raise ValueError('Audio cues need the source music SHA256')
        if timing.get('mode')=='reference_changes':
            evidence=timing.get('reference_analysis_sha256')
            if not isinstance(evidence,str) or len(evidence)!=64 or any(c not in '0123456789abcdef' for c in evidence):raise ValueError('Reference timing needs its analysis fingerprint')
        if music is not None and hashlib.sha256(Path(music).read_bytes()).hexdigest()!=digest:raise ValueError('Audio cues belong to a different or changed music file')
    elif timing.get('mode','authored_grid')!='authored_grid' or not number(timing.get('bpm')) or not 40<=timing['bpm']<=240 or not number(timing.get('offset',0)) or not 0<=timing.get('offset',0)<=2 or (zero and timing.get('offset',0)!=0):raise ValueError('Music timing needs finite BPM40–240 and supported offset')
    return timing


def position(timing,index):
    if type(index) not in (int,float) or not math.isfinite(index) or index<0:raise ValueError('Invalid timing index')
    if 'cues' in timing:
        if int(index)!=index or index>=len(timing['cues']):raise ValueError('Timing index exceeds available audio cues')
        return timing['cues'][int(index)]
    return timing.get('offset',0)+index*60/timing['bpm']


def span(timing,start,length):
    if type(length) not in (int,float) or not math.isfinite(length) or length<=0:raise ValueError('Invalid timing span')
    # Preserve decimal cue coordinates before the native frame quantization.
    return float(Decimal(str(position(timing,start+length)))-Decimal(str(position(timing,start))))


def marker_times(timing,duration):
    if 'cues' in timing:
        if duration>timing['cues'][-1]+1e-6:raise ValueError('Timeline exceeds source-bound audio cue extent')
        return [t for t in timing['cues'] if t<duration]
    first=timing.get('offset',0);step=60/timing['bpm']
    return [first+i*step for i in range(max(0,math.ceil((duration-first)/step)))]


def extract_cues(source,output,max_duration=30.,min_gap=.3):
    from .reference import audio_events
    if output.exists():raise ValueError('Use a new cue evidence file')
    if not math.isfinite(max_duration) or not 1<=max_duration<=600 or not math.isfinite(min_gap) or not .15<=min_gap<=2:raise ValueError('Cue duration1–600s and minimum gap.15–2s required')
    digest=hashlib.sha256(source.read_bytes()).hexdigest();meta=probe(source)
    if not any(s['codec_type']=='audio' for s in meta['streams']):raise ValueError('Music has no audio stream')
    duration=min(max_duration,float(meta['format']['duration']))
    result=subprocess.run([binary('ffmpeg'),'-v','error','-i',str(source),'-t',str(duration),'-map','0:a:0','-ac','1','-ar','8000','-f','f32le','-'],capture_output=True,timeout=180)
    if result.returncode:raise ValueError(result.stderr.decode(errors='replace')[-2000:])
    samples=array.array('f');samples.frombytes(result.stdout)
    if sys.byteorder!='little':samples.byteswap()
    _,events=audio_events(samples);cues=[0.];selected=[]
    for event in events:
        at=event['time']
        if at-cues[-1]>=min_gap and duration-at>=min_gap:cues.append(at);selected.append(event)
    cues.append(round(duration,6))
    timing={'mode':'onset_candidates','cues':cues,'source_sha256':digest,'provenance':'Measured 10ms RMS energy novelty candidates; zero/end are boundaries, interior points are transients, not verified beats or phrases.'}
    validate_timing(timing,source)
    if hashlib.sha256(source.read_bytes()).hexdigest()!=digest:raise ValueError('Music changed during cue extraction')
    output.parent.mkdir(parents=True,exist_ok=True);write(output,{'music_timing':timing,'onsets':selected,'analysis_rate':8000,'minimum_gap':min_gap,'limits':['No listening, song identification, tempo or downbeat claim.','Soft music may lack useful onsets; speech/SFX can produce candidates.','Review candidates and musical fit; automated cuts may use a subset.']})
    return {'evidence':str(output),'cue_count':len(cues),'duration':duration,'music_timing':timing}
