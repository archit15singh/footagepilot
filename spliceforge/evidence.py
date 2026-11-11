"""Bind verification to the exact project inputs and output file revision."""
import hashlib
import json
from pathlib import Path


def file_revision(path):
    stat=Path(path).stat()
    return [stat.st_size,stat.st_mtime_ns]


def input_revision(project_path):
    raw=project_path.read_bytes()
    item=json.loads(raw)
    transcript=project_path.parent/'transcript.json'
    payload={'project':raw.decode(),'source':file_revision(item['source']),
             'transcript':transcript.read_text() if transcript.exists() else None,
             'words':(project_path.parent/'words.json').read_text() if (project_path.parent/'words.json').exists() else None,
             'audio_files':[file_revision(p) for p in ([item.get('audio',{}).get('music')] if item.get('audio',{}).get('music') else [])+[s['path'] for s in item.get('audio',{}).get('sfx',[])]],
             'images':[file_revision(card['image']) for card in item.get('storyboard',[])]}
    return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()


def current_verification(project_path):
    try:
        result=json.loads((project_path.parent/'verification.json').read_text())
        if result.get('input_revision')!=input_revision(project_path):return None
        if result.get('output_revision')!=file_revision(project_path.parent/'output.mp4'):return None
        return result
    except (OSError,ValueError,KeyError,TypeError):return None
