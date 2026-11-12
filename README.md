# FootagePilot

Agent-driven video editing for real footage: clean up speech, plan cuts, add captions and graphics, then verify the exports.

Working agent-operated video editing: MakeMyClip cleanup → local word alignment → headless Codex story planning → validated word cuts → HyperFrames/Remotion → music/SFX mixing.

[Naming and migration](docs/NAMING.md) · [Video variations](gallery/index.html) · [Real end-to-end findings](docs/REAL-E2E-RESULTS.md) · [Setup](docs/SETUP.md)

The committed gallery contains four automatically generated edits of real archival footage. Codex is the only planner and was live-tested. Word timestamps are model estimates and listening remains unverified. No UI polish or synthetic demo is needed to reproduce this run.

```sh
npm ci
# Configure FFmpeg/ffprobe and a Python runtime containing mlx-whisper.
export FOOTAGEPILOT_ALIGN_PYTHON=/path/to/python-with-mlx-whisper
python3 evals/real_pipeline.py --work projects/real-run --gallery gallery
```

For your own footage:

```sh
python3 -m footagepilot init recording.mp4 projects/my-film
python3 -m footagepilot produce projects/my-film/project.json --brief 'Select a coherent 30-second excerpt, preserve meaning and source order.'
```

To render one variation, append `--engine remotion` or `--engine hyperframes` to `produce`. Repeat `--engine` to choose both; omitting it preserves the default of both engines. The run manifest lists only outputs from the requested engines.

Use an authenticated `codex` CLI. The planner pins `gpt-6.1-sol` with low reasoning effort. The planner sends transcript text to that provider. The local alignment adapter currently uses MLX Whisper on Apple Silicon. Both renderers and MakeMyClip use the pinned Node dependencies; FFmpeg/ffprobe must be available on PATH or configured using FOOTAGEPILOT_FFMPEG and FOOTAGEPILOT_FFPROBE. Models, local project media and credentials are ignored by Git.

For a hard length constraint, add `"duration_budget": {"min_seconds": 20, "max_seconds": 35}` to the project. The planner receives it, and planning/application/rendering reject edits outside it, including cut padding. Final encoded output permits one 30-fps frame of rounding. An impossible or unmet budget fails clearly; it does not silently truncate speech or automatically retry the model. Without this field, the brief remains advisory about duration.

Optional project audio configuration:

```json
{"audio":{"music":"/absolute/path/music.ogg","music_gain":0.045,"sfx":[{"path":"/absolute/path/effect.wav","start":0.2,"gain":0.03}]}}
```

Place those fields alongside source, keep and brand. The pipeline generates narration-only and mixed versions for both renderers. Effects use edited-timeline seconds. Music now ducks under narration and fades over 0.25 seconds at each end. Set `music_ducking: false` and `music_fade_seconds: 0` inside `audio` to retain fixed-gain behavior. Mix evidence reports integrated LUFS and true peak; it does not automatically normalize loudness. Listening and legal suitability of your own media remain your responsibility.

The CLI also provides cleanup, align, plan, apply-plan, transcribe, apply-transcript, render, validate and doctor. `serve` retains the earlier local workbench; the expanded pipeline is CLI-first. See [architecture](docs/ARCHITECTURE.md), [original findings](docs/RESULTS.md), and [agent instructions](AGENTS.md).

Checks: `python3 -m unittest discover -s tests -v`. Real-footage reproduction is in evals/real_pipeline.py; prior synthetic evaluations are retained as historical evidence and are not substituted for real-footage results.

## Reference-driven editing with Instagram Edits

Read the [Edits guide and official tutorial map](docs/edits/GUIDE.md) and [rebuild plan](docs/REFERENCE-PLAN.md). Native Edits for Mac can be controlled through its authenticated local MCP; computer use handles saved-post browsing, setup and file-picker access.

```sh
# Requires yt-dlp (or FOOTAGEPILOT_YT_DLP), FFmpeg and ffprobe.
python3 -m footagepilot reference 'https://www.instagram.com/reel/SHORTCODE/' --output projects/reference-01
# A browser-downloaded local video is also accepted as the source.
python3 -m footagepilot edits-render projects/recreation.json --token-file /private/path/token --output projects/recreation-01.mp4
python3 -m footagepilot learn-check --fetch
python3 -m footagepilot compare-edits projects/baseline.mp4 projects/recreation-01.mp4 --output projects/comparison-01.json
```

Reference reports contain timestamped frames, dense before/after cut samples, audio-energy/onset candidates, and seekable local playback. Onsets are not guaranteed musical beats. Saved collections are selected through the signed-in browser, not scraped by the CLI. Optional `reference --browser brave` uses the existing authenticated browser session; no cookie file is exported. Keep references, personal media and authentication local. See [recreation manifest](examples/edits-recreation.json) for the executable format; replace its paths with your own imported media.

`learn-check` exits 2 when research is stale, changed or unavailable. It never silently renews verified dates. `compare-edits` retains hashes and technical checks; only an explicit `--verdict better --notes 'reason'` records a preferred candidate. These are evidence/feedback loops, not model training or unattended policy/code changes.

For reference-conditioned planning, use [visual-spec.json](examples/visual-spec.json): `visual-plan <spec> --output projects/new-plan` produces a validated native-edit manifest. `recreate <spec> --token-file /private/path/token --output projects/new-run` chains research freshness, optional Instagram download/analysis (`reference_url`), visual Codex planning and native export with a retained stage ledger. `inspiration-open <spec>` opens its private `saved_collection_url` in Brave for computer-use selection. This workflow preserves an unreviewed preference state until the user evaluates the result.

## Resolve hybrid work (experimental)

`resolve-prepare EDIT.json --output projects/JOB` renders individual media and generates an internal Lua assembly job. `resolve-verify JOB/job.json EXPORT.mp4 --output CHECK.json` checks an actual exported file. This first adapter is cut-only: it rejects titles, collages and transitions, and discloses baked crop/zoom and audio preparation. Free Resolve 21.2 completed a verified native 14-second export and editable DRP after folder-access/API corrections. Add `--render` to request export after assembly. Verification compares sampled frames and soundtrack waveforms; wrong-shot and shifted-audio negative controls were rejected. Creative quality remains unreviewed. See [workflow and research](docs/resolve/GUIDE.md), [technique priorities](docs/resolve/IDEAS.md) and [current evidence](docs/resolve/RESULTS.md).
