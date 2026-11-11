"""Loopback workbench; one project and one background operation at a time."""
import json
import mimetypes
from pathlib import Path
import secrets
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .evidence import current_verification
from .__main__ import probe, render, validate, write
from .transcript import transcribe, apply_selection, selection_ranges


def serve(directory, port=8765):
    directory = directory.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    project = directory / 'project.json'
    token = secrets.token_urlsafe(32)
    lock = threading.Lock()
    state = {'status': 'idle'}

    def job(action):
        try:
            action()
            state.update(status='succeeded', error=None)
        except Exception as error:
            state.update(status='failed', error=str(error))
        finally:
            lock.release()

    class Handler(BaseHTTPRequestHandler):
        def reply(self, code, data):
            body = json.dumps(data).encode()
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers(); self.wfile.write(body)

        def allowed(self):
            return self.headers.get('Host') in (f'127.0.0.1:{port}', f'localhost:{port}')

        def do_GET(self):
            if not self.allowed():
                return self.reply(403, {'error': 'Invalid host'})
            if self.path == '/api/state':
                data = {'job': dict(state), 'token': token}
                for name, path in [('project',project),('transcript',directory/'transcript.json')]:
                    if path.exists():data[name] = json.loads(path.read_text())
                proof=current_verification(project)
                if proof:data['verification']=proof
                return self.reply(200, data)
            if self.path.split('?')[0]=='/output.mp4' and not current_verification(project):return self.reply(409, {'error':'Export is stale; render the current project'})
            paths = {'/': Path(__file__).parent/'web/index.html', '/output.mp4':directory/'output.mp4'}
            path = paths.get(self.path.split('?')[0])
            if not path or not path.is_file():return self.reply(404, {'error':'Not found'})
            size = path.stat().st_size
            start, end = 0, size-1
            partial = self.headers.get('Range')
            if partial:
                import re
                match = re.fullmatch(r'bytes=(\d*)-(\d*)',partial)
                if not match or not any(match.groups()):return self.reply(416, {'error':'Invalid byte range'})
                left,right = match.groups()
                if left:start=int(left);end=min(int(right),end) if right else end
                else:start=max(0,size-int(right))
                if start>end or start>=size:return self.reply(416, {'error':'Range outside file'})
            self.send_response(206 if partial else 200)
            self.send_header('Accept-Ranges','bytes')
            if partial:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
            self.send_header('Content-Type', mimetypes.guess_type(path)[0] or 'application/octet-stream')
            self.send_header('Content-Length', str(end-start+1))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            try:
                with path.open('rb') as file:
                    file.seek(start)
                    remaining=end-start+1
                    while remaining:
                        chunk=file.read(min(1024*1024,remaining))
                        if not chunk:break
                        self.wfile.write(chunk);remaining-=len(chunk)
            except (BrokenPipeError, ConnectionResetError):pass

        def do_POST(self):
            if not self.allowed() or self.headers.get('X-FootagePilot-Token') != token:
                return self.reply(403, {'error':'Invalid request token or host'})
            if not lock.acquire(blocking=False):return self.reply(409, {'error':'An operation is already running'})
            handed_off = False
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 1024*1024:raise ValueError('Request size must be 1 byte–1 MB')
                data = json.loads(self.rfile.read(size))
                if self.path == '/api/import':
                    if project.exists():raise ValueError('Project exists; launch a different project directory to import another recording')
                    source = Path(data['source']).expanduser().resolve()
                    duration = float(probe(source)['format']['duration'])
                    item = {'schema_version':1,'source':str(source),'keep':[[0,duration]],'brand':{'name':'FootagePilot','accent':'#e5a35d'}}
                    validate(item);write(project,item)
                elif self.path == '/api/selection':
                    transcript_path = directory/'transcript.json'
                    transcript = json.loads(transcript_path.read_text())
                    choices = data['keep']
                    if len(choices) != len(transcript['segments']) or any(type(x) is not bool for x in choices):raise ValueError('One boolean required per segment')
                    for row, keep in zip(transcript['segments'], choices):row['keep'] = keep
                    item = json.loads(project.read_text())
                    selection_ranges(transcript['segments'], validate(item))
                    write(transcript_path,transcript);apply_selection(project)
                elif self.path == '/api/design':
                    item = json.loads(project.read_text())
                    import re
                    brand = data['brand']
                    if not isinstance(brand['name'],str) or not 0 < len(brand['name']) <= 50:raise ValueError('Brand name must contain 1–50 characters')
                    if not re.fullmatch(r'#[0-9a-fA-F]{6}',brand['accent']):raise ValueError('Use a six-digit hex color')
                    duration = sum(b-a for a,b in item['keep'])
                    cards = data['storyboard']
                    if not isinstance(cards,list) or len(cards)>20:raise ValueError('Use at most 20 storyboard cards')
                    for card in cards:
                        if not 0 <= card['start'] < card['start']+card['duration'] <= duration:raise ValueError('Card timing is outside the edited video')
                        if not isinstance(card['title'],str) or len(card['title'])>60:raise ValueError('Card title is too long')
                        if not Path(card['image']).is_file():raise ValueError('Card image does not exist')
                    item.update(brand=brand,storyboard=cards,graphics=bool(data['graphics']))
                    write(project,item)
                    (directory/'verification.json').unlink(missing_ok=True)
                elif self.path in ('/api/transcribe','/api/render'):
                    action = transcribe if self.path.endswith('transcribe') else render
                    state.update(status='running', operation=self.path.rsplit('/',1)[-1], error=None)
                    handed_off = True
                    threading.Thread(target=job,args=(lambda:action(project),),daemon=True).start()
                    return self.reply(202, dict(state))
                else:raise ValueError('Unknown operation')
                self.reply(200, {'ok':True})
            except (ValueError, KeyError, TypeError, OSError) as error:
                self.reply(400, {'error':str(error)})
            finally:
                if not handed_off:lock.release()

        def log_message(self, *args):pass

    server = ThreadingHTTPServer(('127.0.0.1',port),Handler)
    print(f'FootagePilot: http://127.0.0.1:{port}',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
