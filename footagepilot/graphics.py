"""Render a reviewed storyboard and captions over the selected recording."""
import json
import math
import os
from pathlib import Path
import re
import shutil
import tempfile
import textwrap
from .__main__ import run


def captions_for_cut(segments, ranges):
    captions, offset = [], 0
    for start, end in ranges:
        for row in segments:
            left, right = max(start,row['start']), min(end,row['end'])
            if not row.get('keep',True) or right <= left:continue
            words = row['text'].split()
            # Approximate timings, explicitly not word alignment.
            first = int((left-row['start'])/(row['end']-row['start'])*len(words))
            last = math.ceil((right-row['start'])/(row['end']-row['start'])*len(words))
            chunks = textwrap.wrap(' '.join(words[first:last]), width=64, break_long_words=True, break_on_hyphens=False)
            if not chunks:continue
            for i, text in enumerate(chunks):
                captions.append({'text':text,'start':offset+left-start+(right-left)*i/len(chunks),'end':offset+left-start+(right-left)*(i+1)/len(chunks)})
        offset += end-start
    return captions


def word_captions_for_cut(words,ranges):
    """Partition each retained interval into readable, phrase-aware cues.

    Optimize the whole interval so a greedy seven-word chunk cannot strand a
    one-word tail. Never borrow time from removed speech or bridge long pauses.
    Dense speech can remain unreadable; report that rather than hide words.
    """
    captions=[];offset=0
    for start,end in ranges:
        selected=[w for w in words if w['start']>=start-.001 and w['end']<=end+.001]
        count=len(selected);best=[None]*(count+1);best[count]=(0,None)
        for first in range(count-1,-1,-1):
            for last in range(first,min(count,first+7)):
                group=selected[first:last+1];text=' '.join(w['text'] for w in group)
                if len(text)>64 and last>first:break
                if last>first and selected[last]['start']-selected[last-1]['end']>.6:break
                duration=group[-1]['end']-group[0]['start']
                if duration<=0:continue
                bad=duration<1 or len(text)/duration>22
                crossings=sum(w['text'].endswith(('.', '!', '?')) for w in group[:-1])
                cost=1000*bad+100*crossings+1
                # Prefer punctuation boundaries when readability is otherwise equal.
                if last<count-1 and not group[-1]['text'].endswith(('.', '!', '?', ',', ';', ':')):cost+=.1
                if best[last+1] is None:continue
                cost+=best[last+1][0]
                if best[first] is None or cost<best[first][0]:best[first]=(cost,last)
        if count and best[0] is None:raise ValueError('Caption words need positive display duration')
        first=0
        while first<count:
            last=best[first][1]
            group=selected[first:last+1]
            captions.append({'text':' '.join(w['text'] for w in group),'start':offset+group[0]['start']-start,'end':offset+group[-1]['end']-start})
            first=last+1
        offset+=end-start
    return captions


def render_graphics(project_path, cut, output, project):
    duration = sum(b-a for a,b in project['keep'])
    brand = project.get('brand',{})
    if not isinstance(brand.get('name'),str) or not 0 < len(brand['name']) <= 50:raise ValueError('Brand name must contain 1–50 characters')
    if not re.fullmatch(r'#[0-9a-fA-F]{6}',brand.get('accent','')):raise ValueError('Brand accent must be a six-digit hex color')
    transcript_path = project_path.parent/'transcript.json'
    rows = json.loads(transcript_path.read_text())['segments'] if transcript_path.exists() else []
    aligned=project.get('word_captions',False)
    if aligned:
        alignment=json.loads((project_path.parent/'words.json').read_text())
        if alignment['source']!=project['source']:raise ValueError('Word caption source mismatch')
        captions=word_captions_for_cut(alignment['words'],project['keep'])
    else:captions = captions_for_cut(rows,project['keep'])
    cards = []
    with tempfile.TemporaryDirectory(prefix='footagepilot-film-') as tmp:
        public = Path(tmp);shutil.copyfile(cut,public/'cut.mp4')
        for i, card in enumerate(project.get('storyboard',[])):
            start, length = card['start'],card['duration']
            if not all(isinstance(x,(int,float)) and math.isfinite(x) for x in (start,length)) or not 0 <= start < start+length <= duration:raise ValueError('Storyboard timing is outside edited duration')
            if not isinstance(card['title'],str) or len(card['title'])>60:raise ValueError('Storyboard titles must be at most 60 characters')
            image = Path(card['image']).expanduser().resolve()
            if image.suffix.lower() not in ('.png','.jpg','.jpeg','.webp'):raise ValueError('Storyboard image must be PNG, JPEG or WebP')
            asset = f'card-{i}{image.suffix.lower()}';shutil.copyfile(image,public/asset)
            cards.append({'title':card['title'],'start':start,'duration':length,'asset':asset})
        props={'duration':duration,'brand':brand,'captions':captions,'cards':cards}
        executable = os.environ.get('FOOTAGEPILOT_REMOTION') or str(Path(__file__).resolve().parents[1]/'node_modules/.bin/remotion')
        run([executable,'render',Path(__file__).parent/'render/film.jsx','FootagePilot',output,'--public-dir',public,'--props',json.dumps(props),'--concurrency','2','--log','error'])
    return {'engine':'remotion','caption_groups':len(captions),'storyboard_cards':len(cards),'caption_timing':'ASR word timestamps; review required' if aligned else 'ASR-segment interpolation; review required','caption_warnings':[{'group':i,'reason':'Fast reading rate or short display'} for i,c in enumerate(captions) if c['end']-c['start']<1 or len(c['text'])/(c['end']-c['start'])>22]}
