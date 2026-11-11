"""Compare caption grouping on committed real speech; fail on regression."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from spliceforge.graphics import word_captions_for_cut


def baseline(words,ranges):
    captions=[];offset=0
    for start,end in ranges:
        group=[]
        def emit(group):
            captions.append({'text':' '.join(w['text'] for w in group),'start':offset+group[0]['start']-start,'end':offset+group[-1]['end']-start})
        for word in [w for w in words if w['start']>=start-.001 and w['end']<=end+.001]:
            if group and (len(group)>=7 or len(' '.join(w['text'] for w in group+[word]))>64):emit(group);group=[]
            group.append(word)
        if group:emit(group)
        offset+=end-start
    return captions


def metrics(captions):
    return {'groups':len(captions),'short_or_fast':sum(c['end']-c['start']<1 or len(c['text'])/max(.001,c['end']-c['start'])>22 for c in captions),'sentence_crossings':sum(any(token.endswith(('.', '!', '?')) for token in c['text'].split()[:-1]) for c in captions)}


def evaluate():
    path=Path(__file__).resolve().parents[1]/'evals/fixtures/weekly-address-words.json';words=json.loads(path.read_text())['words']
    cases={'published_edit':[[.82,9.92],[16.12,28.34]],'full_recording':[[0,words[-1]['end']]],'alternate_excerpt':[[words[20]['start'],words[65]['end']]]}
    results={};improvements=0
    for name,ranges in cases.items():
        before=baseline(words,ranges);after=word_captions_for_cut(words,ranges)
        assert ' '.join(c['text'] for c in before)==' '.join(c['text'] for c in after),'Speech changed'
        limits=[];offset=0
        for start,end in ranges:limits.append((offset,offset+end-start));offset+=end-start
        assert all(any(a-.001<=c['start']<c['end']<=b+.001 for a,b in limits) for c in after),'Crossed cut'
        assert all(a['end']<=b['start']+.001 for a,b in zip(after,after[1:])),'Overlapping cues'
        assert all(len(c['text'])<=64 or len(c['text'].split())==1 for c in after),'Oversize grouping'
        old,new=metrics(before),metrics(after)
        assert new['short_or_fast']<=old['short_or_fast'],name+' readability regression'
        assert new['sentence_crossings']<=old['sentence_crossings'],name+' sentence regression'
        improvements+=new['short_or_fast']<old['short_or_fast'] or new['sentence_crossings']<old['sentence_crossings']
        results[name]={'before':old,'after':new,'captions':after}
    assert improvements,'No measured benefit'
    return {'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'cases':results,'gate':'passed','scope':'Grouping metrics on real ASR timestamps, not human readability or listening ratings'}

if __name__=='__main__':print(json.dumps(evaluate(),indent=2))
