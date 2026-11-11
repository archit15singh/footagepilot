"""Dependency-free project CLI. External media tools are discovered explicitly."""
import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


def binary(name):
    path = os.environ.get('FOOTAGEPILOT_' + name.upper()) or shutil.which(name)
    if not path:
        raise ValueError(f'{name} missing; set FOOTAGEPILOT_{name.upper()} or add it to PATH')
    return path


def run(args):
    result = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    if result.returncode:
        raise ValueError(result.stderr[-4000:] or f'Command failed: {args[0]}')
    return result.stdout


def probe(path):
    return json.loads(run([binary('ffprobe'), '-v', 'error', '-show_format', '-show_streams', '-of', 'json', path]))


def validate(project):
    if not isinstance(project, dict) or project.get('schema_version', 1) != 1:
        raise ValueError('Expected a schema version 1 project object')
    if not isinstance(project.get('source'), str) or not project['source']:
        raise ValueError('Source must be a file path')
    from .duration import validate_budget
    validate_budget(project.get('duration_budget'))
    source = Path(project['source'])
    if not source.is_file():
        raise ValueError('Source file does not exist')
    duration = float(probe(source)['format']['duration'])
    ranges = project.get('keep', [])
    if not isinstance(ranges,list) or not ranges:
        raise ValueError('At least one keep range is required')
    previous = 0
    for pair in ranges:
        if not isinstance(pair,list) or len(pair)!=2:
            raise ValueError('Each keep range must contain start and end seconds')
        start, end = pair
        if not all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in (start, end)):
            raise ValueError('Range timestamps must be finite numbers')
        if not 0 <= start < end <= duration or start < previous:
            raise ValueError('Keep ranges must be ordered, disjoint and within the source')
        previous = end
    if 'graphics' in project and type(project['graphics']) is not bool:
        raise ValueError('Graphics must be a boolean')
    if project.get('renderer','remotion') not in ('remotion','hyperframes'):raise ValueError('Unknown renderer')
    if project.get('cut_engine','ffmpeg') not in ('ffmpeg','makemyclip'):raise ValueError('Unknown cut engine')
    if project.get('graphics'):
        import re
        brand=project.get('brand',{})
        if not isinstance(brand.get('name'),str) or not 0<len(brand['name'])<=50:raise ValueError('Brand name must contain 1–50 characters')
        if not isinstance(brand.get('accent'),str) or not re.fullmatch(r'#[0-9a-fA-F]{6}',brand['accent']):raise ValueError('Invalid accent color')
        edited=sum(b-a for a,b in ranges)
        for card in project.get('storyboard',[]):
            if not all(type(card.get(k)) in (int,float) and math.isfinite(card[k]) for k in ('start','duration')) or not 0<=card['start']<card['start']+card['duration']<=edited:raise ValueError('Invalid storyboard timing')
            if not isinstance(card.get('title'),str) or len(card['title'])>60:raise ValueError('Invalid card title')
            image=Path(card['image'])
            if not image.is_file() or image.suffix.lower() not in ('.png','.jpg','.jpeg','.webp'):raise ValueError('Missing or unsupported card image')
    return duration


def write(path, data):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2) + '\n')
    temp.replace(path)


def render(path):
    (path.parent / 'verification.json').unlink(missing_ok=True)
    project = json.loads(path.read_text())
    validate(project)
    from .duration import require_duration
    require_duration(sum(b-a for a,b in project['keep']),project.get('duration_budget'))
    from .evidence import input_revision, file_revision
    revision = input_revision(path)
    target = path.parent / 'output.mp4'
    temporary = path.parent / 'output.partial.mp4'
    if Path(project['source']).resolve() in (target.resolve(), temporary.resolve()):
        raise ValueError('Source must not be the output file')
    streams = probe(project['source'])['streams']
    audio = any(s['codec_type'] == 'audio' for s in streams)
    filters, inputs = [], []
    for i, (start, end) in enumerate(project['keep']):
        filters.append(f'[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{i}]')
        inputs.append(f'[v{i}]')
        if audio:
            filters.append(f'[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{i}]')
            inputs.append(f'[a{i}]')
    filters.append(''.join(inputs) + f'concat=n={len(project["keep"])}:v=1:a={int(audio)}[v]' + ('[a]' if audio else ''))
    command = [binary('ffmpeg'), '-y', '-i', project['source'], '-filter_complex', ';'.join(filters), '-map', '[v]']
    if audio:
        command += ['-map', '[a]', '-c:a', 'aac']
    command += ['-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', temporary]
    started = time.monotonic()
    try:
        cut_engine=project.get('cut_engine','ffmpeg')
        if cut_engine=='makemyclip':
            from .cleanup import export_ranges
            export_ranges(project,temporary,path.parent/'cut-workspace')
        elif cut_engine=='ffmpeg':run(command)
        else:raise ValueError('Unknown cut engine')
        graphics = None
        if project.get('graphics', False):
            from .graphics import render_graphics
            styled = path.parent / 'styled.partial.mp4'
            try:
                if project.get('renderer','remotion')=='hyperframes':
                    from .hyperframes import render_hyperframes
                    graphics=render_hyperframes(path,temporary,styled,project)
                else:graphics = render_graphics(path, temporary, styled, project)
                styled.replace(temporary)
            finally:
                styled.unlink(missing_ok=True)
        audio_mix = None
        if project.get('audio'):
            from .audio import mix_audio
            mixed=path.parent/'mixed.partial.mp4'
            try:
                audio_mix=mix_audio(temporary,mixed,project['audio'],sum(b-a for a,b in project['keep']))
                mixed.replace(temporary)
            finally:mixed.unlink(missing_ok=True)
        run([binary('ffmpeg'), '-v', 'error', '-i', temporary, '-f', 'null', '-'])
        metadata = probe(temporary)
        actual = float(metadata['format']['duration'])
        require_duration(actual,project.get('duration_budget'),tolerance=1/30)
        expected = sum(b-a for a,b in project['keep'])
        if abs(actual - expected) > .15:
            raise ValueError(f'Output duration mismatch: {actual} versus {expected}')
        if input_revision(path) != revision:
            raise ValueError('Project inputs changed during render; rerender the current edit')
        temporary.replace(target)
        write(path.parent / 'verification.json', {'passed': True, 'input_revision': revision, 'output_revision': file_revision(target), 'expected_duration': expected, 'actual_duration': actual, 'decode': 'passed', 'graphics': graphics, 'audio_mix': audio_mix, 'elapsed_seconds': time.monotonic()-started, 'limitations': ['No aesthetic, speech continuity or listening assessment'], 'command': [str(x) for x in command]})
    finally:
        temporary.unlink(missing_ok=True)
    return target


def main():
    parser = argparse.ArgumentParser(description='FootagePilot — Make the cut. Show the evidence.')
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init'); init.add_argument('source', type=Path); init.add_argument('directory', type=Path)
    for name in ('validate', 'render', 'transcribe', 'apply-transcript', 'align', 'apply-plan', 'cleanup'):
        sub = commands.add_parser(name); sub.add_argument('project', type=Path)
    production = commands.add_parser('produce'); production.add_argument('project',type=Path); production.add_argument('--brief',required=True); production.add_argument('--skip-cleanup',action='store_true'); production.add_argument('--engine',action='append',choices=('remotion','hyperframes'),help='Render only this engine; repeat for both (default: both)')
    planner = commands.add_parser('plan'); planner.add_argument('project',type=Path); planner.add_argument('--brief',required=True)
    commands.add_parser('doctor')
    web = commands.add_parser('serve'); web.add_argument('directory', type=Path); web.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    try:
        if args.command == 'serve':
            from .server import serve
            serve(args.directory, args.port)
        elif args.command == 'doctor':
            print(json.dumps({name: binary(name) for name in ('ffmpeg', 'ffprobe')}, indent=2))
        elif args.command == 'init':
            source = args.source.resolve()
            duration = float(probe(source)['format']['duration'])
            args.directory.mkdir(parents=True, exist_ok=True)
            path = args.directory / 'project.json'
            if path.exists():
                raise ValueError('Project already exists')
            write(path, {'schema_version': 1, 'source': str(source), 'keep': [[0, duration]], 'brand': {'name': 'FootagePilot', 'accent': '#e5a35d'}})
            print(path)
        elif args.command == 'produce':
            from .pipeline import produce
            print(json.dumps(produce(args.project.resolve(),args.brief,not args.skip_cleanup,args.engine),indent=2))
        elif args.command == 'cleanup':
            from .cleanup import cleanup
            print(json.dumps(cleanup(args.project.resolve()),indent=2))
        elif args.command == 'align':
            from .alignment import align
            print(json.dumps(align(args.project.resolve()),indent=2))
        elif args.command == 'plan':
            from .planner import plan
            print(json.dumps(plan(args.project.resolve(),args.brief),indent=2))
        elif args.command == 'apply-plan':
            from .planner import apply_plan
            print(json.dumps(apply_plan(args.project.resolve())))
        elif args.command == 'transcribe':
            from .transcript import transcribe
            print(json.dumps(transcribe(args.project.resolve()), indent=2))
        elif args.command == 'apply-transcript':
            from .transcript import apply_selection
            print(json.dumps(apply_selection(args.project.resolve())))
        elif args.command == 'validate':
            validate(json.loads(args.project.read_text())); print('Valid')
        else:
            print(render(args.project.resolve()))
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
