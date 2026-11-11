"""Real narration with a probe tone: ducking effectiveness and voice retention.

The tone is a diagnostic signal, not a demo or a music-preference evaluation.
"""
import argparse,array,hashlib,json,math,subprocess,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from footagepilot.__main__ import binary,run,probe
from footagepilot.audio import mix_audio


def rms(path,filter):
    result=subprocess.run([binary('ffmpeg'),'-v','error','-i',str(path),'-vn','-af',filter,'-ac','1','-ar','48000','-f','f32le','-'],capture_output=True,check=True)
    values=array.array('f');values.frombytes(result.stdout)
    return math.sqrt(sum(x*x for x in values)/len(values))


def evaluate(source,work):
    if work.exists():raise ValueError('Use a new work directory')
    work.mkdir(parents=True);duration=float(probe(source)['format']['duration']);tone=work/'probe.wav'
    run([binary('ffmpeg'),'-v','error','-y','-f','lavfi','-i',f'sine=frequency=6000:sample_rate=48000:duration={duration}','-c:a','pcm_s16le',tone])
    records={}
    for name,settings in [('before',{'music_ducking':False,'music_fade_seconds':0}),('after',{})]:
        output=work/(name+'.mp4');details=mix_audio(source,output,{'music':str(tone),'music_gain':1,**settings},duration)
        run([binary('ffmpeg'),'-v','error','-i',output,'-f','null','-'])
        records[name]={'probe_rms':rms(output,'atrim=start=2:end=18,bandpass=f=6000:t=h:w=100'),'voice_band_rms':rms(output,'atrim=start=2:end=18,lowpass=f=1500'),'opening_probe_rms':rms(output,'atrim=end=0.1,bandpass=f=6000:t=h:w=100'),'mix':details,'sha256':hashlib.sha256(output.read_bytes()).hexdigest()}
    attenuation=20*math.log10(records['after']['probe_rms']/records['before']['probe_rms'])
    voice_delta=20*math.log10(records['after']['voice_band_rms']/records['before']['voice_band_rms'])
    opening_delta=20*math.log10(records['after']['opening_probe_rms']/records['before']['opening_probe_rms'])
    assert attenuation<-3,('Insufficient ducking',attenuation)
    assert abs(voice_delta)<.5,('Voice changed',voice_delta)
    assert opening_delta<-3,('Opening fade missing',opening_delta)
    assert float(records['after']['mix']['loudness']['true_peak_dbtp'])<0,'Clipped output'
    return {'gate':'passed','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'probe_attenuation_db':attenuation,'voice_band_delta_db':voice_delta,'opening_probe_delta_db':opening_delta,'records':records,'scope':'Technical masking/fade proxies on one real narration; not a human listening or music suitability score.'}

BASELINE_REVISION='bfa6c91284693b45807c2d28d9aad2a7abc70608'
BASELINE_SHA256='d692dbae9ff7e84285474c72dc68e1295bc70f812c0fed5b589f666c8f093a4b'


def materialize_baseline(directory):
    root=Path(__file__).resolve().parents[1]
    try:
        data=subprocess.check_output(['git','show',BASELINE_REVISION+':gallery/videos/remotion-narration.mp4'],cwd=root,stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as error:
        raise ValueError('Reference media unavailable; fetch full repository history or provide an explicit source') from error
    if hashlib.sha256(data).hexdigest()!=BASELINE_SHA256:raise ValueError('Reference media hash mismatch')
    source=directory/'reference.mp4';source.write_bytes(data);return source


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path,nargs='?');p.add_argument('--baseline',action='store_true',help='Use the original, hash-verified reference clip from Git history');p.add_argument('--work',required=True,type=Path);a=p.parse_args()
    if bool(a.source)==a.baseline:p.error('Choose one source or --baseline')
    if a.baseline:
        with tempfile.TemporaryDirectory(prefix='footagepilot-audio-reference-') as temp:
            result=evaluate(materialize_baseline(Path(temp)),a.work)
        result['reference_commit']=BASELINE_REVISION
    else:result=evaluate(a.source,a.work)
    print(json.dumps(result,indent=2))
