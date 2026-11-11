# Setup

Python 3.11+, Node.js22+, FFmpeg and ffprobe are required. The Python application uses the standard library and runs directly from the checkout.

1. Clone the repository and run `npm ci` in its root to install the pinned Remotion renderer.
2. Install FFmpeg using your OS package manager. Confirm `ffmpeg -version` and `ffprobe -version`.
3. Build or install whisper.cpp from its official repository and download an English model using its documented model downloader. No model weights are bundled here.
4. Set local paths for the ASR executable and model:

```sh
export SPLICEFORGE_WHISPER=/absolute/path/to/whisper-cli
export SPLICEFORGE_WHISPER_MODEL=/absolute/path/to/ggml-base.en.bin
# Optional if FFmpeg tools are not on PATH:
export SPLICEFORGE_FFMPEG=/absolute/path/to/ffmpeg
export SPLICEFORGE_FFPROBE=/absolute/path/to/ffprobe
python3 -m spliceforge doctor
python3 -m spliceforge serve projects/my-film
```

Visit http://127.0.0.1:8765. Import a video, transcribe locally, review segment checkboxes, apply selections, configure the design, save, render and play the result. Start with a short disposable recording to verify your toolchain.

The first graphics render downloads Chromium if needed. ASR and rendering then run locally. Remotion's license is separate from this application's code; check the upstream terms for commercial deployment. FFmpeg and whisper.cpp retain their respective licenses. No paid API keys are required for this local workflow.

## Troubleshooting

- Missing executable: set its SPLICEFORGE_* override or PATH, then restart the workbench so it inherits that environment.
- Model missing: point to a downloaded whisper.cpp model, not a model repository name.
- No speech: inspect the source audio; ASR cannot supply a reliable transcript for silent footage.
- Job fails: read the status error, correct the input or design and retry. The server serializes UI operations. Avoid editing project files from the CLI while a browser job runs.
- Graphics timing error after cutting: update card start/duration values against the edited timeline.
- Different fonts across machines: the renderer currently uses local fallback fonts. Cross-platform pixel parity has not been established.
- Browser media error: reload and play; byte-range serving is supported. Verify the export with FFmpeg if the error persists.

## Expanded pipeline requirements

Run npm ci for pinned MakeMyClip, HyperFrames, GSAP and Remotion. Install/authenticate Codex CLI to live-run the planner; Claude Code is an alternative supported command but was not installed/tested in this evaluation. Use SPLICEFORGE_CODEX/SPLICEFORGE_CLAUDE for executable overrides. Install mlx-whisper into an isolated Python runtime and point SPLICEFORGE_ALIGN_PYTHON at it. SPLICEFORGE_ALIGN_MODEL overrides the compatible local/Hugging Face model path; model download is separate. These components use their own licenses. See REAL-E2E-RESULTS.md for one-command real-footage reproduction and limits.
