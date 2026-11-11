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
