"""Local ASR and explicit transcript selections; no hidden editorial decisions."""
import json
import os
from pathlib import Path
import tempfile
from .__main__ import binary, probe, run, validate, write


def transcribe(project_path, language='en'):
    project = json.loads(project_path.read_text())
    validate(project)
    whisper = binary('whisper')
    model = os.environ.get('FOOTAGEPILOT_WHISPER_MODEL')
    if not model or not Path(model).is_file():
        raise ValueError('Set FOOTAGEPILOT_WHISPER_MODEL to a local whisper.cpp model')
    with tempfile.TemporaryDirectory(prefix='footagepilot-asr-') as directory:
        audio = Path(directory) / 'speech.wav'
        output = Path(directory) / 'transcript'
        run([binary('ffmpeg'), '-y', '-i', project['source'], '-vn', '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', audio])
        run([whisper, '-m', model, '-f', audio, '-l', language, '-oj', '-of', output])
        raw = json.loads(output.with_suffix('.json').read_text())
    duration = float(probe(project['source'])['format']['duration'])
    segments = []
    for item in raw['transcription']:
        start, end = item['offsets']['from']/1000, item['offsets']['to']/1000
        text = item['text'].strip()
        if text and start < duration and end > start:
            segments.append({'id': len(segments), 'start': max(0, start), 'end': min(end, duration), 'text': text, 'keep': True})
    if not segments:
        raise ValueError('No speech segments found')
    result = {'source': project['source'], 'engine': 'whisper.cpp', 'language': language, 'segments': segments, 'review_required': True}
    write(project_path.parent / 'transcript.json', result)
    return result


def selection_ranges(segments, duration, padding=.08):
    if not 0 <= padding <= .5:
        raise ValueError('Padding must be between 0 and .5 seconds')
    ranges = []
    previous = 0
    for segment in segments:
        start, end = segment['start'], segment['end']
        if not 0 <= start < end <= duration or start < previous:
            raise ValueError('Transcript segments must be ordered and within source duration')
        previous = end
        if not isinstance(segment['keep'], bool):
            raise ValueError('Transcript keep values must be boolean')
        if segment['keep']:
            start, end = max(0, start-padding), min(duration, end+padding)
            if ranges and start <= ranges[-1][1]:
                ranges[-1][1] = max(ranges[-1][1], end)
            else:
                ranges.append([start, end])
    if not ranges:
        raise ValueError('Select at least one speech segment')
    return ranges


def apply_selection(project_path):
    project = json.loads(project_path.read_text())
    transcript = json.loads((project_path.parent/'transcript.json').read_text())
    if transcript['source'] != project['source']:
        raise ValueError('Transcript belongs to a different source')
    duration = validate(project)
    project['keep'] = selection_ranges(transcript['segments'], duration)
    validate(project)
    write(project_path, project)
    # Selection changes invalidate prior verification until rendered again.
    (project_path.parent/'verification.json').unlink(missing_ok=True)
    return project['keep']
