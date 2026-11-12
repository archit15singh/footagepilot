"""Transfer measured reference change coordinates without calling them musical beats."""
import hashlib,json,math
from decimal import Decimal
from .__main__ import write
from .music_timing import validate_timing


def rhythm_options(spec,backend):
    if 'reference_rhythm' not in spec:return None
    value=spec['reference_rhythm']
    if backend!='resolve' or not isinstance(value,dict) or set(value)-{'duration','min_gap'}:raise ValueError('reference_rhythm requires Resolve and duration/min_gap options')
    if 'music_analysis' in spec or 'music_timing' in spec or spec.get('music_from_reference') is not True:raise ValueError('Reference rhythm requires reference music and no competing timing request')
    duration=value.get('duration',spec.get('max_seconds',20));gap=value.get('min_gap',.15)
    if type(duration) not in (int,float) or not math.isfinite(duration) or not 1<=duration<=180 or type(gap) not in (int,float) or not math.isfinite(gap) or not .1<=gap<=2:raise ValueError('Reference rhythm needs duration1–180 and minimum gap.1–2 seconds')
    if duration!=spec.get('max_seconds',20) or duration!=spec.get('min_seconds',10):raise ValueError('Reference rhythm duration must equal both duration budget endpoints')
    return {'duration':duration,'min_gap':gap}


def extract_rhythm(analysis,music,output,duration,min_gap=.15):
    if output.exists():raise ValueError('Use a fresh reference rhythm evidence file')
    snapshot=analysis.read_bytes();reference=json.loads(snapshot);digest=hashlib.sha256(music.read_bytes()).hexdigest()
    if reference.get('decode')!='passed' or digest!=reference.get('source_sha256'):raise ValueError('Reference rhythm needs unchanged analyzed reference media as music')
    if type(duration) not in (int,float) or not math.isfinite(duration) or not 1<=duration<=180 or duration>reference['duration']:raise ValueError('Reference rhythm exceeds analyzed duration')
    if type(min_gap) not in (int,float) or not math.isfinite(min_gap) or not .1<=min_gap<=2:raise ValueError('Invalid reference minimum gap')
    cuts=reference.get('scene_changes')
    if not isinstance(cuts,list) or any(type(t) not in (int,float) or not math.isfinite(t) or not 0<t<reference['duration'] for t in cuts) or any(b<=a for a,b in zip(cuts,cuts[1:])):raise ValueError('Reference scene candidates must be finite and strictly ordered')
    cues=[0.];omitted=[]
    for at in cuts:
        if at>=duration:continue
        if Decimal(str(at))-Decimal(str(cues[-1]))<Decimal(str(min_gap)) or Decimal(str(duration))-Decimal(str(at))<Decimal(str(min_gap)):omitted.append(at)
        else:cues.append(at)
    cues.append(duration)
    if not 2<=len(cues)-1<=30:raise ValueError('Reference rhythm must yield2–30shots; choose another duration or gap')
    timing={'mode':'reference_changes','cues':cues,'source_sha256':digest,'reference_analysis_sha256':hashlib.sha256(snapshot).hexdigest(),
        'provenance':'Measured reference scene-change candidates with explicit gap filtering; not verified cuts, musical beats, phrases or transition classifications.'}
    validate_timing(timing,music)
    if analysis.read_bytes()!=snapshot or hashlib.sha256(music.read_bytes()).hexdigest()!=digest:raise ValueError('Reference changed during rhythm extraction')
    result={'music_timing':timing,'shot_count':len(cues)-1,'omitted_close_candidates':omitted,'duration':duration,'min_gap':min_gap,'creative_acceptance':'unreviewed'}
    write(output,result);return result


def validate_reference_timing(timing,analysis,music):
    if timing.get('mode')!='reference_changes':return
    validate_timing(timing,music)
    data=analysis.read_bytes();reference=json.loads(data)
    if hashlib.sha256(data).hexdigest()!=timing.get('reference_analysis_sha256') or reference.get('decode')!='passed' or reference.get('source_sha256')!=timing['source_sha256']:raise ValueError('Reference rhythm belongs to different or changed analysis')
    if timing['cues'][-1]>reference['duration'] or any(at not in reference['scene_changes'] for at in timing['cues'][1:-1]):raise ValueError('Reference timing contains unsupported change coordinates')
