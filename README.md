# SpliceForge

**Make the cut. Show the evidence.**

A local video editing workbench for creators and coding agents. Currently under construction: the first executable slice creates a project, validates explicit keep ranges, renders cuts with FFmpeg, and records decode and duration checks. Local transcription and explicit segment selection are available. Motion graphics and the browser workbench remain planned.

## Run without installation

Requires Python 3.11+, FFmpeg and ffprobe on PATH. Override tool locations with `SPLICEFORGE_FFMPEG` and `SPLICEFORGE_FFPROBE`.

```sh
python3 -m spliceforge doctor
python3 -m spliceforge init recording.mp4 projects/demo
# Edit projects/demo/project.json: keep contains ordered [start, end] seconds.
python3 -m spliceforge validate projects/demo/project.json
python3 -m spliceforge render projects/demo/project.json
python3 -m unittest discover -s tests -v
```

The source stays intact. Each successful render replaces the project's output.mp4 and verification.json. Decode checks do not prove good pacing, natural speech cuts or visual quality.

See [the build plan](docs/PLAN.md). The precursor [benchmark](https://github.com/archit15singh/video-editing-agent-bench) motivates separating speech cleanup from motion graphics. Its results are not evaluations of this product.

## Transcript review

Use a local whisper.cpp CLI and model; set `SPLICEFORGE_WHISPER` to its executable and `SPLICEFORGE_WHISPER_MODEL` to the model file. No remote transcription service is called.

```sh
python3 -m spliceforge transcribe projects/demo/project.json
# Review transcript.json and change unwanted segments' keep values to false.
python3 -m spliceforge apply-transcript projects/demo/project.json
python3 -m spliceforge render projects/demo/project.json
```

Selections use ASR segment timestamps with 80ms padding and merge adjacent regions. They can retain pauses within a segment and are not word-accurate. Review cut boundaries before delivery. Reapplying selections invalidates old verification evidence.

## Local workbench

```sh
python3 -m spliceforge serve projects/demo
```

Visit http://127.0.0.1:8765. Import a recording by absolute path, transcribe, select segments, apply the selection, render and play the output. Configure the same media and ASR environment variables before starting the server. Jobs run one at a time and expose errors in the interface. Keep the terminal running; job state is in memory and unfinished jobs do not resume after restart. The server binds to loopback and requires a per-session request token for mutations. It is intended for a trusted local machine, not remote hosting.

## Captioned motion graphics

Install the pinned renderer with `npm ci` (Node.js 22+). Set `graphics` to `true` in project.json to render the cut through Remotion. A reviewed transcript supplies captions; their timing is interpolated within ASR segments and needs review. Add storyboard cards using edited-timeline seconds:

```json
{"graphics": true, "brand": {"name": "Your brand", "accent": "#e5a35d"}, "storyboard": [{"title": "A clear decision", "image": "/absolute/path/screen.png", "start": 3, "duration": 6}]}
```

These fields belong alongside source and keep in your project. Each card shows its image, title, animated entrance and progress line. The source remains in a side pane; narration is retained. The first Remotion render may download a compatible Chromium browser. Remotion has its own licensing terms; review them before commercial deployment. Currently the workbench does not edit graphics settings: use project.json, then render from CLI or workbench.
