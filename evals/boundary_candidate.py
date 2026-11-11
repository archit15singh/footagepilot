"""Screen wider fixed handles against actual source audio before shipping them.

An active edge is a review proxy, not a phoneme-error label. Exit 2 rejects
this candidate when it does not reduce active boundaries on the locked edit.
"""
import argparse,array,hashlib,json,math,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from spliceforge.__main__ import binary


def evaluate(source):
    root=Path(__file__).resolve().parents[1];words=json.loads((root/'evals/fixtures/weekly-address-words.json').read_text())['words']
    pcm=subprocess.run([binary('ffmpeg'),'-v','error','-i',str(source),'-vn','-ac','1','-ar','16000','-f','f32le','-'],capture_output=True,check=True)
    audio=array.array('f');audio.frombytes(pcm.stdout)
    def energy(a,b):
        chunk=audio[int(a*16000):int(b*16000)]
        return 20*math.log10(max(1e-9,math.sqrt(sum(v*v for v in chunk)/max(1,len(chunk)))))
    rows={}
    for name,head,tail in [('before',.04,.06),('candidate',.12,.14)]:
        ranges=[]
        for first,last in [(2,35),(57,100)]:
            ranges.append([max(words[first-1]['end'],words[first]['start']-head),min(words[last+1]['start'],words[last]['end']+tail)])
        edges=[{'time':a,'kind':'start','dbfs':energy(a,a+.01)} for a,b in ranges]+[{'time':b,'kind':'end','dbfs':energy(b-.01,b)} for a,b in ranges]
        rows[name]={'ranges':ranges,'duration':sum(b-a for a,b in ranges),'active_edges':sum(e['dbfs']>-45 for e in edges),'edges':edges}
    promote=rows['candidate']['active_edges']<rows['before']['active_edges']
    return {'decision':'investigate further' if promote else 'reject','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'quiet_proxy_threshold_dbfs':-45,'rows':rows,'scope':'Ten-ms source RMS at four edit edges. Does not establish clipped phonemes, listening preference or safe adaptive alignment.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('cleaned_source',type=Path);a=p.parse_args();r=evaluate(a.cleaned_source);print(json.dumps(r,indent=2));sys.exit(2 if r['decision']=='reject' else 0)
