"""Exercise real HTTP failure/recovery and range handling on a disposable project."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request
import urllib.error
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from spliceforge.__main__ import binary,run,write
root=Path('projects/api-evaluation').resolve();root.mkdir(parents=True,exist_ok=True)
source=root/'source.mp4'
run([binary('ffmpeg'),'-y','-f','lavfi','-i','color=c=blue:s=320x240:r=30','-t','1','-c:v','libx264','-pix_fmt','yuv420p',source])
write(root/'project.json',{'schema_version':1,'source':str(source),'keep':[[0,1]],'brand':{'name':'Demo','accent':'#e5a35d'}})
server=subprocess.Popen([sys.executable,'-m','spliceforge','serve',str(root),'--port','8767'],stdout=subprocess.DEVNULL)
base='http://127.0.0.1:8767'
def state():return json.load(urllib.request.urlopen(base+'/api/state'))
def post(route,data,token):
    request=urllib.request.Request(base+'/api/'+route,data=json.dumps(data).encode(),headers={'Content-Type':'application/json','X-SpliceForge-Token':token})
    try:
        r=urllib.request.urlopen(request);return r.status,json.load(r)
    except urllib.error.HTTPError as e:return e.code,json.load(e)
def wait_job():
    deadline=time.monotonic()+60
    while time.monotonic()<deadline:
        s=state()['job']
        if s['status']!='running':return s
        time.sleep(.1)
    raise RuntimeError('Job did not finish')
try:
    for _ in range(100):
        try:s=state();break
        except OSError:time.sleep(.05)
    token=s['token'];checks={}
    checks['unauthorized_rejected']=post('render',{},'bad')[0]==403
    hidden=root/'source-hidden.mp4';source.rename(hidden)
    assert post('render',{},token)[0]==202
    checks['failed_job_visible']=wait_job()['status']=='failed'
    hidden.rename(source)
    assert post('render',{},token)[0]==202
    checks['corrected_retry_succeeds']=wait_job()['status']=='succeeded'
    checks['invalid_design_rejected']=post('design',{'brand':{'name':'Demo','accent':'invalid'},'storyboard':[],'graphics':True},token)[0]==400
    r=urllib.request.urlopen(urllib.request.Request(base+'/output.mp4',headers={'Range':'bytes=0-99'}))
    checks['range_playback']=r.status==206 and len(r.read())==100
    checks['proof_survives_invalid_design']='verification' in state()
    assert all(checks.values()),checks
    Path('evals/API-RESULTS.json').write_text(json.dumps(checks,indent=2)+'\n');print(checks)
finally:
    server.terminate();server.wait(timeout=10)
