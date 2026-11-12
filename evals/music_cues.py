"""Known uneven pulse and silence controls for candidate onset extraction."""
import argparse,array,hashlib,json,math,sys,wave
from pathlib import Path
from footagepilot.music_timing import extract_cues,validate_timing
from footagepilot.__main__ import write


def evaluate(output):
    if output.exists():raise ValueError('Use a new evaluation directory')
    output.mkdir(parents=True);rate=8000;times=[.35,.9,1.6,2.9,4.2];duration=5.
    def score(path,pulses):
        values=array.array('h')
        for n in range(round(duration*rate)):
            at=n/rate;value=sum(.65*math.exp(-(at-t)*30)*math.sin(2*math.pi*700*(at-t)) for t in pulses if 0<=at-t<.2)
            values.append(round(max(-1,min(1,value))*32767))
        if sys.byteorder!='little':values.byteswap()
        with wave.open(str(path),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(values.tobytes())
    music=output/'uneven.wav';score(music,times);extract_cues(music,output/'cues.json',duration,.3)
    timing=json.loads((output/'cues.json').read_text())['music_timing'];found=timing['cues'][1:-1]
    offsets=[min(abs(t-c) for c in found) for t in times]
    if len(found)!=len(times) or max(offsets)>.12:raise ValueError('Known uneven pulse recovery failed')
    silence=output/'silence.wav';score(silence,[])
    try:extract_cues(silence,output/'silence-cues.json',duration,.3)
    except ValueError:silence_rejected=not (output/'silence-cues.json').exists()
    else:raise ValueError('Silence produced a usable cue map')
    try:validate_timing(timing,silence)
    except ValueError:changed_music_rejected=True
    else:raise ValueError('Wrong music accepted by cue map')
    result={'passed':True,'known_pulses':times,'candidate_onsets':found,'maximum_error_seconds':round(max(offsets),4),'silence_rejected_without_output':silence_rejected,'different_track_rejected':changed_music_rejected,'scope':'Known transient recovery and source binding; not real-song beat/phrase accuracy'};write(output/'results.json',result);return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();print(json.dumps(evaluate(a.output),indent=2))
