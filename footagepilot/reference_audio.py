"""Inspect one reference excerpt with a user-started local audio model."""
import base64
import hashlib
import io
import json
import math
import os
import wave
from urllib.error import URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from .__main__ import binary
from .reference import execute


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def listen(analysis_path, output, start, end, port=8080):
    if not (math.isfinite(start) and math.isfinite(end) and 0 <= start < end and end - start <= 15):
        raise ValueError('Choose a finite audio excerpt of up to 15 seconds')
    if not 1 <= port <= 65535:
        raise ValueError('Choose a valid local server port')

    analysis = json.loads(analysis_path.read_text())
    if end > float(analysis['duration']):
        raise ValueError('Excerpt ends beyond the reference duration')
    if not analysis['audio']['present']:
        raise ValueError('Reference has no audio stream')
    media = analysis_path.parent / 'media.mp4'
    source_hash = analysis['source_sha256']
    if output.exists():
        raise ValueError('Use a fresh audio note path')
    with media.open('rb') as handle:
        if hashlib.file_digest(handle, 'sha256').hexdigest() != source_hash:
            raise ValueError('Reference media has changed since analysis')
    # Trim in sample space after using the reference report's zero-based audio clock.
    sample_start = round(start * 16000)
    sample_end = round(end * 16000)
    if sample_end <= sample_start:
        raise ValueError('Excerpt is shorter than one audio sample')
    pcm = execute([
        binary('ffmpeg'), '-v', 'error', '-i', media, '-map', '0:a:0',
        '-af', f'aresample=16000:async=1:first_pts=0,apad=whole_len={sample_end},'
               f'atrim=start_sample={sample_start}:end_sample={sample_end}',
        '-ac', '1', '-c:a', 'pcm_s16le', '-f', 's16le', '-',
    ]).stdout
    if len(pcm) != (sample_end - sample_start) * 2:
        raise ValueError('Audio excerpt length does not match its sample bounds')
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as handle:
        handle.setparams((1, 2, 16000, 0, 'NONE', 'not compressed'))
        handle.writeframes(pcm)
    wav = buffer.getvalue()

    prompt = (
        'Describe only what is audible in this clip. Distinguish music, speech, singing and sound effects '
        'when supported. Describe how the sound changes. Say when the source is unclear or the clip '
        'is silent. Use at most three short sentences. Avoid guessing a song, instrument identity, exact timestamps, tempo or downbeats.'
    )
    payload = {
        'messages': [{'role': 'user', 'content': [
            {'type': 'text', 'text': prompt},
            {'type': 'input_audio', 'input_audio': {
                'data': base64.b64encode(wav).decode('ascii'), 'format': 'wav',
            }},
        ]}],
        'temperature': 0,
        'max_tokens': 256,
    }
    headers = {'Content-Type': 'application/json'}
    if api_key := os.environ.get('FOOTAGEPILOT_AUDIO_API_KEY'):
        headers['Authorization'] = f'Bearer {api_key}'
    request = Request(
        f'http://127.0.0.1:{port}/v1/chat/completions',
        data=json.dumps(payload).encode(),
        headers=headers,
    )
    opener = build_opener(ProxyHandler({}), NoRedirect())
    try:
        with opener.open(request, timeout=180) as response:
            reply = json.load(response)
    except (URLError, TimeoutError) as error:
        raise ValueError(f'Local audio model request failed on port {port}: {error}') from error

    choices = reply.get('choices') or []
    description = choices[0].get('message', {}).get('content') if choices else None
    if choices and choices[0].get('finish_reason') == 'length':
        raise ValueError('Local audio model description was truncated')
    if not isinstance(description, str) or not description.strip():
        raise ValueError('Local audio model returned no description')
    note = {
        'source_sha256': source_hash,
        'audio_sha256': hashlib.sha256(wav).hexdigest(),
        'start': sample_start / 16000,
        'end': sample_end / 16000,
        'model': reply.get('model'),
        'status': 'model_hypothesis',
        'description': description.strip(),
    }
    with output.open('x') as handle:
        json.dump(note, handle, indent=2)
        handle.write('\n')
    return note
