"""Authenticated local Edits MCP connection; never configures global clients."""
import json
import os
from pathlib import Path
import urllib.request
import urllib.error

class EditsClient:
    def __init__(self, token_file=None):
        self.token=os.environ.get('FOOTAGEPILOT_EDITS_TOKEN','').strip()
        if token_file:self.token=Path(token_file).read_text().strip()
        if not self.token:raise ValueError('Set FOOTAGEPILOT_EDITS_TOKEN or provide --token-file (keep it private)')
        self.endpoint='http://127.0.0.1:19501/mcp';self.session=None;self.sequence=0
        self.request('initialize',{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'footagepilot','version':'0.1'}})
    def request(self,method,params):
        self.sequence+=1
        headers={'Authorization':'Bearer '+self.token,'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
        if self.session:headers['Mcp-Session-Id']=self.session
        payload={'jsonrpc':'2.0','id':self.sequence,'method':method,'params':params}
        try:
            with urllib.request.urlopen(urllib.request.Request(self.endpoint,data=json.dumps(payload).encode(),headers=headers),timeout=120) as response:
                self.session=response.headers.get('Mcp-Session-Id') or self.session;raw=response.read().decode()
        except urllib.error.URLError as e:raise ValueError('Edits local MCP connection failed; check app, automation toggle and private token') from e
        if raw.lstrip().startswith('data:'):
            raw=next(line[5:].strip() for line in raw.splitlines() if line.startswith('data:'))
        result=json.loads(raw)
        if 'error' in result:raise ValueError('Edits MCP error: '+str(result['error'].get('message','unknown')))
        return result.get('result',{})
    def tools(self):return self.request('tools/list',{}).get('tools',[])
    def call(self,name,arguments=None):
        result=self.request('tools/call',{'name':name,'arguments':arguments or {}})
        if result.get('isError'):raise ValueError('Edits tool failed: '+json.dumps(result))
        if result.get('structuredContent') is not None:return result['structuredContent']
        texts=[c['text'] for c in result.get('content',[]) if c.get('type')=='text']
        if len(texts)==1:
            try:return json.loads(texts[0])
            except json.JSONDecodeError:return {'text':texts[0]}
        return {'text':'\n'.join(texts)}


def validate_edit(data, base):
    import math
    if not isinstance(data,dict) or not isinstance(data.get('shots'),list) or not 1<=len(data['shots'])<=60:
        raise ValueError('Choose 1–60 main shots')
    if data.get('aspect','9:16') not in ('9:16','16:9','1:1','4:5'):raise ValueError('Unsupported canvas aspect')
    if data.get('fps',30) not in (24,30,60):raise ValueError('Choose 24, 30 or 60 fps')
    def number(value,low,high):return type(value) in (int,float) and math.isfinite(value) and low<=value<=high
    total=0
    for shot in data['shots']+data.get('overlays',[]):
        if not number(shot.get('duration'),.1,30):raise ValueError('Shot duration must be 0.1–30 seconds')
        path=(base/shot['path']).resolve()
        if not path.is_file():raise ValueError('Shot file missing')
        if shot.get('fit','fill') not in ('fill','contain'):raise ValueError('Unknown shot fit')
        if not number(shot.get('scale',1),.1,3) or not number(shot.get('zoom',0),0,.2):raise ValueError('Invalid scale/zoom')
        for key in ('x','y'):
            if not number(shot.get(key,.5),0,1):raise ValueError('Position must be 0–1')
    total=sum(s['duration'] for s in data['shots'])
    if total>180:raise ValueError('Recreation must be at most 180 seconds')
    for overlay in data.get('overlays',[])+data.get('titles',[]):
        if not number(overlay.get('start',0),0,total) or not number(overlay.get('duration'),.1,total) or overlay.get('start',0)+overlay['duration']>total+.001:raise ValueError('Overlay exceeds timeline')
    for title in data.get('titles',[]):
        if not isinstance(title.get('text'),str) or not 1<=len(title['text'])<=120:raise ValueError('Title must contain 1–120 characters')
    if data.get('music') and not (base/data['music']).is_file():raise ValueError('Music missing')
    if not number(data.get('music_gain',.65),0,1):raise ValueError('Music gain must be 0–1')
    for transition in data.get('transitions',[]):
        i=transition.get('after_shot')
        if type(i) is not int or not 0<=i<len(data['shots'])-1:raise ValueError('Transition needs an existing adjacent shot boundary')
        if not number(transition.get('duration',.2),.05,min(data['shots'][i]['duration'],data['shots'][i+1]['duration'])/2):raise ValueError('Transition too long for adjacent shots')
    timing=data.get('music_timing')
    if timing and (not data.get('music') or not number(timing.get('bpm'),40,240) or not number(timing.get('offset',0),0,2) or not timing.get('provenance')):raise ValueError('Music timing needs a track, finite BPM/offset and provenance')
    return total


def render_edit(manifest, output, token_file=None):
    import hashlib,time,shutil,uuid
    from .__main__ import probe,binary,run,write
    snapshot=manifest.read_bytes();data=json.loads(snapshot);total=validate_edit(data,manifest.parent)
    if output.exists():raise ValueError('Use a new output file')
    output.parent.mkdir(parents=True,exist_ok=True)
    evidence=output.with_suffix('.edits.json');calls=[]
    inputs={str((manifest.parent/s['path']).resolve()) for s in data['shots']+data.get('overlays',[])}
    if data.get('music'):inputs.add(str((manifest.parent/data['music']).resolve()))
    hashes={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in inputs}
    client=EditsClient(token_file)
    def call(name,args=None):
        result=client.call(name,args);calls.append({'tool':name,'arguments':args or {},'result':result})
        if isinstance(result,dict) and result.get('ok') is False:raise ValueError('Edits operation reported failure: '+name)
        return result
    try:
        call('closeProject');project=call('newProject');call('setTitle',{'name':data.get('title','FootagePilot recreation')});call('setCanvas',{'aspect':data.get('aspect','9:16'),'frameRate':data.get('fps',30)})
        cursor=0
        def add(shot,overlay=False):
            path=str((manifest.parent/shot['path']).resolve())
            # audioKind is listed as required but passing it for visual media mutates then errors in this version.
            result=call('addOverlay',{'path':path,'startSeconds':shot['start'],'x':shot.get('x',.5),'y':shot.get('y',.5),'scale':1}) if overlay else call('addMedia',{'path':path})
            element_id=result.get('id') or result.get('addedId') or result.get('elementId')
            if not element_id:raise ValueError('Edits did not return the inserted element ID')
            current=next(e for e in call('elements')['elements'] if e['id']==element_id)
            call('trim',{'id':element_id,'side':'right','deltaSeconds':current['duration']-shot['duration']})
            if not overlay:call('move',{'id':element_id,'toSeconds':cursor})
            pose=call('setTransform',{'id':element_id,'fitMode':shot.get('fit','fill'),'focusX':shot.get('focus_x',.5),'focusY':shot.get('focus_y',.5),'allowBeyondCanvas':False,'keyframes':'reject'})
            scale=pose.get('appliedScale',pose.get('transform',{}).get('scale',1))*shot.get('scale',1)
            call('setTransform',{'id':element_id,'x':shot.get('x',.5),'y':shot.get('y',.5),'scale':scale,'allowBeyondCanvas':False,'keyframes':'reject'})
            if shot.get('zoom'):
                start=shot['start'] if overlay else cursor
                call('setTransformKeyframe',{'id':element_id,'time':start,'scale':scale})
                call('setTransformKeyframe',{'id':element_id,'time':start+shot['duration']-1/data.get('fps',30),'scale':scale*(1+shot['zoom'])})
            return element_id
        shot_ids=[]
        for shot in data['shots']:
            shot_ids.append(add(shot));cursor+=shot['duration']
        for transition in data.get('transitions',[]):
            i=transition['after_shot'];arguments={'fromId':shot_ids[i],'toId':shot_ids[i+1],'filterId':transition.get('filter','transition_dissolve'),'durationSeconds':transition.get('duration',.2)}
            call('addTransition',arguments)
        for shot in data.get('overlays',[]):add(shot,True)
        for title in data.get('titles',[]):
            r=call('addText',{'text':title['text'],'atSeconds':title.get('start',0),'duration':title['duration']});text_id=r.get('id') or r.get('elementId')
            if not text_id:raise ValueError('No title element ID')
            call('setTextStyle',{'id':text_id,'size':title.get('size',100),'color':title.get('color','#FFE49C'),'bold':title.get('bold',False),'alignment':'center'})
            call('setTextPosition',{'id':text_id,'x':title.get('x',.5),'y':title.get('y',.5)})
            if title.get('font'):call('setTextFont',{'id':text_id,'family':title['font']})
        if data.get('music'):
            r=call('addMedia',{'path':str((manifest.parent/data['music']).resolve()),'audioKind':'music'});audio_id=r.get('id') or r.get('addedId')
            current=next(e for e in call('elements')['elements'] if e['id']==audio_id)
            if current['duration']<total:raise ValueError('Music shorter than timeline; provide a prepared track')
            call('trim',{'id':audio_id,'side':'right','deltaSeconds':current['duration']-total});call('move',{'id':audio_id,'toSeconds':0});call('setVolume',{'id':audio_id,'volume':data.get('music_gain',.65)});call('setFade',{'id':audio_id,'fadeIn':.15,'fadeOut':.8})
            timing=data.get('music_timing')
            if timing:
                beat=timing.get('offset',0)
                while beat<total:
                    call('addBeatMarker',{'id':audio_id,'seconds':round(beat,6)});beat+=60/timing['bpm']
        saved=call('saveProject')
        if saved.get('projectId')!=project.get('id'):raise ValueError('Active Edits project changed during editing')
        call('setExportSettings',{'resolution':{'9:16':'1080x1920','16:9':'1920x1080','1:1':'1080x1080','4:5':'1080x1350'}[data.get('aspect','9:16')],'resolutionType':'HD','aspectRatio':{'9:16':'nineBySixteen','16:9':'sixteenByNine','1:1':'oneByOne','4:5':'fourByFive'}[data.get('aspect','9:16')],'quality':'high','codec':'hevc','frameRate':data.get('fps',30),'dynamicRange':'SDR'})
        export_dir=Path(os.environ.get('FOOTAGEPILOT_EDITS_EXPORT_DIR',str(Path.home()/'Movies'/'Edits'/'Exports')))
        native_export=export_dir/(output.stem+'-'+uuid.uuid4().hex[:8]+'.mp4')
        call('export',{'path':str(native_export)})
        deadline=time.monotonic()+180
        while time.monotonic()<deadline:
            status=call('exportStatus')
            if native_export.is_file() and native_export.stat().st_size>0 and not (status.get('state') not in ('complete','completed') or status.get('isExporting',False)):break
            if status.get('error') or str(status.get('state','')).lower().startswith(('error','failed')):raise ValueError('Edits export failed: '+str(status.get('error') or status.get('state')))
            time.sleep(1)
        if not native_export.is_file() or status.get('state') not in ('complete','completed'):raise ValueError('Edits export timed out')
        shutil.copyfile(native_export,output)
        run([binary('ffmpeg'),'-v','error','-i',output,'-f','null','-']);metadata=probe(output);actual=float(metadata['format']['duration'])
        if abs(actual-total)>.15:raise ValueError('Edits export duration mismatch')
        if manifest.read_bytes()!=snapshot or any(hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h for p,h in hashes.items()):raise ValueError('Inputs changed during editing')
        proof={'passed':True,'project':project,'native_export':str(native_export),'duration':actual,'expected_duration':total,'source_hashes':hashes,'output_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'decode':'passed','calls':calls,'limitations':['Creative quality requires reference comparison and user review.','One-time native file import may be needed for sandbox bookmarks.']};write(evidence,proof)
        return {'output':str(output),'evidence':str(evidence),'duration':actual,'project':project}
    except Exception as error:
        write(evidence,{'passed':False,'error':str(error),'calls':calls});raise
