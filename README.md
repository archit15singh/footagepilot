# SpliceForge

Working agent-operated video editing: MakeMyClip cleanup → local word alignment → headless Codex story planning → validated word cuts → HyperFrames/Remotion → music/SFX mixing.

[Video variations](gallery/index.html) · [Real end-to-end findings](docs/REAL-E2E-RESULTS.md) · [Setup](docs/SETUP.md)

The committed gallery contains four automatically generated edits of real archival footage. Codex is the only planner and was live-tested. Word timestamps are model estimates and listening remains unverified. No UI polish or synthetic demo is needed to reproduce this run.

```sh
npm ci
# Configure FFmpeg/ffprobe and a Python runtime containing mlx-whisper.
export SPLICEFORGE_ALIGN_PYTHON=/path/to/python-with-mlx-whisper
python3 evals/real_pipeline.py --work projects/real-run --gallery gallery
```

For your own footage:

```sh
python3 -m spliceforge init recording.mp4 projects/my-film
python3 -m spliceforge produce projects/my-film/project.json --brief 'Select a coherent 30-second excerpt, preserve meaning and source order.'
```

Use an authenticated `codex` CLI. The planner pins `gpt-6.1-sol` with low reasoning effort. The planner sends transcript text to that provider. The local alignment adapter currently uses MLX Whisper on Apple Silicon. Both renderers and MakeMyClip use the pinned Node dependencies; FFmpeg/ffprobe must be available on PATH or configured using SPLICEFORGE_FFMPEG and SPLICEFORGE_FFPROBE. Models, local project media and credentials are ignored by Git.

Optional project audio configuration:

```json
{"audio":{"music":"/absolute/path/music.ogg","music_gain":0.045,"sfx":[{"path":"/absolute/path/effect.wav","start":0.2,"gain":0.03}]}}
```

Place those fields alongside source, keep and brand. The pipeline generates narration-only and mixed versions for both renderers. Effects use edited-timeline seconds. Listening and legal suitability of your own media remain your responsibility.

The CLI also provides cleanup, align, plan, apply-plan, transcribe, apply-transcript, render, validate and doctor. `serve` retains the earlier local workbench; the expanded pipeline is CLI-first. See [architecture](docs/ARCHITECTURE.md), [original findings](docs/RESULTS.md), and [agent instructions](AGENTS.md).

Checks: `python3 -m unittest discover -s tests -v`. Real-footage reproduction is in evals/real_pipeline.py; prior synthetic evaluations are retained as historical evidence and are not substituted for real-footage results.
