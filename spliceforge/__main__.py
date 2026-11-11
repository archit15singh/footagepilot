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
    path = os.environ.get('SPLICEFORGE_' + name.upper()) or shutil.which(name)
    if not path:
        raise ValueError(f'{name} missing; set SPLICEFORGE_{name.upper()} or add it to PATH')
    return path


def run(args):
    result = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    if result.returncode:
        raise ValueError(result.stderr[-4000:] or f'Command failed: {args[0]}')
    return result.stdout


def probe(path):
    return json.loads(run([binary('ffprobe'), '-v', 'error', '-show_format', '-show_streams', '-of', 'json', path]))


def validate(project):
    source = Path(project['source'])
    if not source.is_file():
        raise ValueError('Source file does not exist')
    duration = float(probe(source)['format']['duration'])
    ranges = project.get('keep', [])
    if not ranges:
        raise ValueError('At least one keep range is required')
    previous = 0
    for start, end in ranges:
        if not all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in (start, end)):
            raise ValueError('Range timestamps must be finite numbers')
        if not 0 <= start < end <= duration or start < previous:
            raise ValueError('Keep ranges must be ordered, disjoint and within the source')
        previous = end
    return duration


def write(path, data):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2) + '\n')
    temp.replace(path)


def render(path):
    project = json.loads(path.read_text())
    validate(project)
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
        run(command)
        run([binary('ffmpeg'), '-v', 'error', '-i', temporary, '-f', 'null', '-'])
        metadata = probe(temporary)
        actual = float(metadata['format']['duration'])
        expected = sum(b-a for a,b in project['keep'])
        if abs(actual - expected) > .15:
            raise ValueError(f'Output duration mismatch: {actual} versus {expected}')
        temporary.replace(target)
        write(path.parent / 'verification.json', {'passed': True, 'expected_duration': expected, 'actual_duration': actual, 'decode': 'passed', 'elapsed_seconds': time.monotonic()-started, 'limitations': ['No aesthetic, speech continuity or listening assessment'], 'command': [str(x) for x in command]})
    finally:
        temporary.unlink(missing_ok=True)
    return target


def main():
    parser = argparse.ArgumentParser(description='SpliceForge — Make the cut. Show the evidence.')
    commands = parser.add_subparsers(dest='command', required=True)
    init = commands.add_parser('init'); init.add_argument('source', type=Path); init.add_argument('directory', type=Path)
    for name in ('validate', 'render'):
        sub = commands.add_parser(name); sub.add_argument('project', type=Path)
    commands.add_parser('doctor')
    args = parser.parse_args()
    try:
        if args.command == 'doctor':
            print(json.dumps({name: binary(name) for name in ('ffmpeg', 'ffprobe')}, indent=2))
        elif args.command == 'init':
            source = args.source.resolve()
            duration = float(probe(source)['format']['duration'])
            args.directory.mkdir(parents=True, exist_ok=True)
            path = args.directory / 'project.json'
            if path.exists():
                raise ValueError('Project already exists')
            write(path, {'schema_version': 1, 'source': str(source), 'keep': [[0, duration]], 'brand': {'name': 'SpliceForge', 'accent': '#e5a35d'}})
            print(path)
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
