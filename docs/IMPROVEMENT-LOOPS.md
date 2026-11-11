# Evaluation-gated improvement loops

Each accepted change must improve a declared metric without violating preservation gates, pass regression tests and actual media checks where relevant, then pass PR CI before merge. A rendered MP4 or a green unit suite alone does not establish editorial quality. Rejected candidates remain local; evidence must not be rewritten into success claims.

## Loop 1 — phrase-aware captions

Baseline: main bfa6c91, greedy seven-word / 64-character caption groups. Candidate: bounded interval partitioning that minimizes short/fast groups, then sentence crossings; retains ASR word times, text and cut boundaries. No transcription/model change or extra dependency.

Evaluation: `python3 evals/caption_quality.py`. Three selections from the committed real archival alignment, input hash and full cue output in [caption-quality.json](../evals/results/caption-quality.json). Same limits before/after: <1 second or >22 characters/second counts as a warning. These are project heuristics.

| Selection | Short/fast before → after | Sentence-crossing groups before → after |
|---|---|---|
| Published edit | 3 → 2 | 3 → 2 |
| Full recording | 6 → 1 | 6 → 5 |
| Alternate excerpt | 1 → 0 | 3 → 2 |

All three preserve exact selected text, cue ordering and retained-range bounds. The improvement gate fails on the unmodified baseline (no measured benefit), and passes on the candidate. Additional regressions cover removed speech, long pauses, dense speech and oversized individual tokens. Unavoidable fast speech still produces warnings; this does not establish accessibility compliance or a human preference score.

Live render checks: both Remotion and HyperFrames rendered the actual 21.32-second selection through MakeMyClip, fully decoded with video/audio present, and met the existing duration tolerance. A frame at 4 seconds from each engine was visually inspected: face and caption remain visible and text fits. This is a sampled-frame check, not a listening or complete animation review. Fifteen tests pass; compile and whitespace checks pass. No human quality score is claimed.


## Loop 2 — selective engine production

`produce --engine remotion` or `--engine hyperframes` now requests only that renderer; omitted selection still produces both. Selection is validated before writing run state. The final mixed proof follows the actual last engine rather than assuming HyperFrames.

Before: every run invoked two renderer stages. After: the live Remotion-only run invoked exactly one and emitted narration/mixed Remotion outputs, with no HyperFrames stage. Actual local MLX alignment and headless Codex 6.1 Sol / low ran on the existing cleaned archival speech. This is a full downstream production run; silence cleanup was explicitly skipped because its input was already cleaned. Both exports independently decode, contain audio/video and match recorded hashes. See [engine-selection.json](../evals/results/engine-selection.json) for actual timings and checks. Different runs can select different speech; do not interpret these timings against the earlier gallery run as a controlled speedup measurement.

Seventeen regression tests pass, including default/both, each single engine, reversed engine order, invalid selections and final mixed-proof ownership. The branch also passes compile/whitespace checks. This change avoids an unwanted render; it does not yet cache or resume stages.
