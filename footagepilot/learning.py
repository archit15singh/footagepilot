"""Evidence and freshness gates for deliberate improvement, not self-modifying policy."""
from datetime import datetime,timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import urllib.request
from .__main__ import binary,probe,run,write

class PageText(HTMLParser):
    def __init__(self):super().__init__();self.parts=[];self.skip=0
    def handle_starttag(self,tag,attrs):
        if tag in ('script','style'):self.skip+=1
    def handle_endtag(self,tag):
        if tag in ('script','style'):self.skip=max(0,self.skip-1)
    def handle_data(self,text):
        if not self.skip and text.strip():self.parts.append(text.strip())

def text_hash(body):
    parser=PageText();parser.feed(body)
    return hashlib.sha256(' '.join(parser.parts).encode()).hexdigest()

def check_sources(registry,fetch=False,now=None):
    now=now or datetime.now(timezone.utc);results=[]
    for source in json.loads(registry.read_text())['sources']:
        age=(now-datetime.fromisoformat(source['verified_at'])).total_seconds()/86400
        status='stale' if age>source.get('max_age_days',7) else 'current'
        row={'url':source['url'],'age_days':round(age,2),'status':status,'fetched':False}
        if fetch:
            if not source['url'].startswith('https://edits.instagram.com/'):raise ValueError('Research registry only fetches official Edits HTTPS pages')
            try:
                body=urllib.request.urlopen(source['url'],timeout=15).read().decode();digest=text_hash(body);row.update(fetched=True,observed_sha256=digest)
                if digest!=source.get('text_sha256'):row['status']='changed-needs-review'
            except Exception as e:row.update(status='unavailable',error=type(e).__name__)
        results.append(row)
    return {'needs_research':any(r['status']!='current' for r in results),'sources':results,'note':'Fetching never renews verification; review changed guides and rerun live capabilities before updating the registry.'}

def compare_edits(baseline,candidate,output,verdict='unreviewed',notes=''):
    if verdict not in ('unreviewed','better','worse','tie'):raise ValueError('Unknown human verdict')
    if output.exists():raise ValueError('Use a new comparison file to preserve history')
    if verdict!='unreviewed' and not notes.strip():raise ValueError('A preference verdict needs an explanation')
    evidence=[]
    for label,path in [('baseline',baseline),('candidate',candidate)]:
        before=hashlib.sha256(path.read_bytes()).hexdigest();run([binary('ffmpeg'),'-v','error','-i',path,'-f','null','-']);metadata=probe(path)
        if hashlib.sha256(path.read_bytes()).hexdigest()!=before:raise ValueError('Media changed during comparison')
        evidence.append({'kind':label,'sha256':before,'duration':float(metadata['format']['duration']),'decode':'passed'})
    result={'evaluated_at':datetime.now(timezone.utc).isoformat(),'media':evidence,'technical_pass':True,'human_verdict':verdict,'review_notes':notes,'promote':verdict=='better','next_step':'Retain failed candidates; change one creative factor, render, compare and seek explicit preference.','limits':'Decode does not establish rhythm, crop quality, music fit or story. No code, model, instructions or publishing settings are automatically changed.'}
    output.parent.mkdir(parents=True,exist_ok=True);write(output,result);return result
