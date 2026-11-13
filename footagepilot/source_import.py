"""Import selected local videos with generated filenames and provenance."""
import hashlib,json,math,shutil,zipfile
from pathlib import Path
from .__main__ import probe,write

VIDEO_SUFFIXES={'.mp4','.mov','.m4v','.mkv','.webm'}
MAX_BYTES=4*1024**3


def digest(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def video_members(archive):
    members=[r for r in archive.infolist() if not r.is_dir() and Path(r.filename).suffix.lower() in VIDEO_SUFFIXES]
    if not 1<=len(members)<=20:raise ValueError('Archive must contain1–20 selected videos')
    if any(r.flag_bits&1 or not 0<r.file_size<=MAX_BYTES for r in members) or sum(r.file_size for r in members)>MAX_BYTES:raise ValueError('Encrypted, empty or over4GiB video archives are unsupported')
    return members


def media_info(path):
    meta=probe(path);video=next((s for s in meta['streams'] if s.get('codec_type')=='video'),None)
    if not video or min(video.get('width',0),video.get('height',0))<=0:raise ValueError('Imported source has no usable video dimensions')
    duration=float(video.get('duration') or meta.get('format',{}).get('duration',0))
    if not math.isfinite(duration) or duration<=0:raise ValueError('Imported source has no positive duration')
    rotation=next((s['rotation'] for s in video.get('side_data_list',[]) if 'rotation' in s),video.get('tags',{}).get('rotate',0))
    rotation=float(rotation)
    if not math.isfinite(rotation):raise ValueError('Invalid source rotation metadata')
    width,height=video['width'],video['height'];display=[height,width] if rotation%180==90 else [width,height] if rotation%180==0 else None
    return {'duration':duration,'coded_dimensions':[width,height],'rotation_degrees':rotation,'display_dimensions':display,'sample_aspect_ratio':video.get('sample_aspect_ratio','unknown'),'has_audio':any(s.get('codec_type')=='audio' for s in meta['streams']),'scope':'Probed stream metadata; display dimensions assume square pixels and quarter-turn rotation. Not full decode or quality selection.'}


def write_inventory(output, rows, total_bytes, provenance, scope):
    assets = [
        {'id': row['id'], 'path': row['path'],
         'note': 'Original selected video; inspect source windows and crop suitability before editing.'}
        for row in rows
    ]
    write(output / 'sources.json', {**provenance, 'sources': rows, 'scope': scope})
    write(output / 'assets.json', {'assets': assets})
    return {'sources': str(output / 'sources.json'), 'assets': str(output / 'assets.json'),
            'videos': len(rows), 'bytes': total_bytes, 'status': 'imported-not-quality-reviewed'}


def import_sources(inputs, output):
    paths = [path.resolve() for path in inputs]
    if len(paths) == 1 and (paths[0].suffix.lower() == '.zip' or zipfile.is_zipfile(paths[0])):
        return import_archive(paths[0], output)
    if output.exists():
        raise ValueError('Use a new source import directory')
    if not 1 <= len(paths) <= 20 or any(
        not path.is_file() or path.suffix.lower() not in VIDEO_SUFFIXES for path in paths
    ):
        raise ValueError('Expected one readable ZIP or 1–20 selected video files')
    sizes = [path.stat().st_size for path in paths]
    if not all(sizes) or sum(sizes) > MAX_BYTES:
        raise ValueError('Empty or over 4 GiB video selections are unsupported')

    output.mkdir(parents=True)
    rows = []
    try:
        for index, (source, size) in enumerate(zip(paths, sizes), 1):
            clip_id = f'clip-{index:02d}'
            target = output / f'{clip_id}{source.suffix.lower()}'
            fingerprint = digest(source)
            with source.open('rb') as src, target.open('xb') as dst:
                remaining = size
                while remaining:
                    block = src.read(min(remaining, 1024 * 1024))
                    if not block:
                        break
                    dst.write(block)
                    remaining -= len(block)
                if remaining or src.read(1):
                    raise ValueError('Source file size changed during import')
            if digest(target) != fingerprint:
                raise ValueError('Source file changed during import')
            rows.append({'id': clip_id, 'path': str(target.resolve()),
                         'original_file': str(source), 'sha256': fingerprint, **media_info(target)})
        return write_inventory(
            output, rows, sum(sizes), {},
            'Local file provenance and media inventory; no automatic semantic selection or creative acceptance',
        )
    except Exception as error:
        write(output / 'failure.json', {'error': str(error), 'status': 'incomplete-import'})
        raise


def import_archive(source,output):
    if output.exists():raise ValueError('Use a new source import directory')
    if not zipfile.is_zipfile(source):raise ValueError('Expected a readable ZIP source archive')
    fingerprint=digest(source)
    with zipfile.ZipFile(source) as archive:
        members=video_members(archive);output.mkdir(parents=True)
        rows=[]
        try:
            for i,member in enumerate(members,1):
                # Generated flat names prevent traversal, absolute-path writes and duplicate-name collisions.
                target=output/f'clip-{i:02d}{Path(member.filename).suffix.lower()}'
                with archive.open(member) as src,target.open('xb') as dst:shutil.copyfileobj(src,dst,1024*1024)
                if target.stat().st_size!=member.file_size:raise ValueError('Source archive size mismatch')
                rows.append({'id':f'clip-{i:02d}','path':str(target.resolve()),'original_member':member.filename,'sha256':digest(target),**media_info(target)})
            if digest(source)!=fingerprint:raise ValueError('Source archive changed during import')
            return write_inventory(
                output, rows, sum(r.file_size for r in members),
                {'archive': str(source.resolve()), 'archive_sha256': fingerprint},
                'Local archive provenance and media inventory; no automatic semantic selection or creative acceptance',
            )
        except Exception as error:write(output/'failure.json',{'error':str(error),'status':'incomplete-import'});raise
