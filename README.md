# SpliceForge

**Make the cut. Show the evidence.**

A local video editing workbench for creators and coding agents. Currently under construction: the first executable slice creates a project, validates explicit keep ranges, renders cuts with FFmpeg, and records decode and duration checks. Transcription, motion graphics and the browser workbench are planned; they are not shipped yet.

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
