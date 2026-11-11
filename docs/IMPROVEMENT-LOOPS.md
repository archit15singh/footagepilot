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
