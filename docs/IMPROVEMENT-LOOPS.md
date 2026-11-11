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

## Loop 3 — enforce explicit duration budgets

Projects may declare `duration_budget` with `min_seconds` / `max_seconds`. Planning validates padded selected ranges before saving; application rechecks the current budget; rendering rejects an invalid selection before running media commands and checks encoded length with one 30-fps frame tolerance. Impossible source-length minimums fail before calling Codex. An unmet budget fails clearly rather than silently truncating speech. No automatic model retry or semantic guarantee is implied.

Evaluation: `python3 evals/duration_quality.py`. On four real-transcript plan selections, the old structural-only gate accepts three invalid durations; the new gate rejects all three and preserves the valid one. One invalid selection fits before padding but exceeds its budget afterward. See [duration-quality.json](../evals/results/duration-quality.json).

Live Codex 6.1 Sol / low returned a 21.32-second plan for the explicit 20–35-second budget. MakeMyClip plus HyperFrames produced a fully decoded 21.333-second export. Tightening the maximum to 21.25 seconds made actual `apply-plan` and `render` CLI calls fail without modifying the project or creating an output. See [duration-live.json](../evals/results/duration-live.json). Twenty tests pass, including invalid budgets and rejection before media execution; compile and whitespace checks pass. Existing natural-language-only briefs remain advisory when no explicit budget is configured.

## Loop 4 — voice-first music and measurable levels

Music now ducks from the narration sidechain and fades in/out over 0.25 seconds by default. Voice stays at unity gain; SFX timing/gain stays independent. Explicit controls restore legacy fixed-gain/no-fade behavior. Evidence additionally reports input integrated LUFS, true peak and loudness range from FFmpeg analysis; no automatic loudness normalization was added.

Evaluation: `python3 evals/audio_quality.py gallery/videos/remotion-narration.mp4 --work projects/new-audio-eval`. A 6-kHz probe tone mixed under actual narration makes music-energy change measurable without conflating it with speech. Compared with fixed gain/no fades, the candidate attenuates probe energy by 3.05 dB across seconds 2–18, changes voice-band RMS by −0.02 dB, and reduces opening probe energy by 13.45 dB. Both outputs decode, and candidate true peak stays below 0 dBTP. See [audio-quality.json](../evals/results/audio-quality.json). This is a diagnostic signal on one voice, not representative music or listening preference evidence.

Also mixed the actual gallery music/SFX with the actual narration, fully decoded it, and reran MLX Whisper: one substitution in 83 expected words, matching the prior baseline error count. Measured −27.06 LUFS integrated / −5.70 dBTP. SFX-only mix also fully decodes without a music sidechain. See [audio-real.json](../evals/results/audio-real.json). Twenty-one tests pass plus compile/whitespace checks. Thresholds are conservative engineering gates; no human listening, pumping assessment or aesthetic improvement percentage is claimed.


## Loop 5 — preserve audio configuration on failure

Evaluation uncovered a concrete reliability defect: production temporarily removes audio settings while rendering narration, but renderer/mixer failure exits before restoring them. Five injected failure cases fail on main 3ac6919: first renderer, second renderer, mixer, and empty audio configuration on either renderer. The candidate restores only the original audio field in a finally block, retaining current source/selection and failure-stage evidence. All five cases then pass; twenty-two tests pass in total. These fault-injection tests exercise orchestration rather than claim real media execution.

An actual CLI failure run also passed the recovery gate: local MLX alignment and Codex 6.1 Sol / low planning succeeded, then the configured MakeMyClip executable deliberately returned nonzero during `render-remotion`. The CLI failed, the run manifest retained its failed stage, the audio settings survived unchanged, and no output was created. Evidence: [failure-preservation.json](../evals/results/failure-preservation.json). This is a real failure-path check, not a successful rendering claim.


## Loop 6 — reject wider fixed cut handles

Tested 120-ms leading / 140-ms trailing handles against the existing 40-ms / 60-ms handles on the actual cleaned recording. Both clamp to neighboring word estimates. The candidate adds 0.24 seconds but leaves two of four source-audio edges active under a fixed −45 dBFS / 10-ms RMS review proxy. It does not meet the improvement gate and was not shipped. Reproduce with `python3 evals/boundary_candidate.py <cleaned-source.mp4>`; exit 2 means rejection. Measurements: [boundary-candidate.json](../evals/results/boundary-candidate.json).

An active edge is not an annotated clipped phoneme. Adaptive alignment still needs stronger onset/offset evidence; this experiment does not establish that the existing cuts are safe or that all boundary algorithms fail. No arbitrary padding increase or new dependency was promoted on weak evidence.

## Integrated run after the five accepted fixes

Main `0fd2f20622cb6932d7e8e259b6ee3bbce1c10e23` completed all twelve stages from the original prepared 60-second recording: MakeMyClip cleanup, MLX alignment, Codex 6.1 Sol / low planning, budget application, both renderers, both mixes and all four decode/hash checks. The selected ranges remain unchanged at 21.32 seconds. Both mixed outputs re-transcribe with the same one substitution in 83 tokens as the baseline. A sampled frame at four seconds from each final engine was inspected for face/caption visibility and fit. All four outputs and posters have been refreshed in the gallery; no interface redesign. See [integrated-improvements.json](../evals/results/integrated-improvements.json) and [gallery evidence](../gallery/evidence.json).

Stage total is about 75.8 seconds on this single run. This is not a speedup result against the historical 69.4-second run: system conditions vary and added audio analysis has cost. Engine selection avoids an unwanted renderer, but both-engine production is not claimed to be faster. Quality benefits are the specific caption, budget, audio-proxy and recovery measurements above, not an overall quality percentage.

Regression evaluation inputs are now frozen under `evals/fixtures/weekly-address-words.json`, independent of future gallery refreshes. The frozen input exactly preserves the earlier benchmark hash. Twenty-two tests pass. Remaining limits: one already-produced archival speaker, no independent listening or preference scores, no proven phoneme-safe automatic boundary adjustment, no semantic story critic, stage cache or new visual-planning system. These are outstanding candidates, not shipped features.


## Loop 7 — reject inputs changed while the planner runs

Final review found a freshness race: the model read one transcript, but the saved plan hash was calculated by rereading the file after the response. A concurrent alignment update could therefore bind old word IDs to new transcript content. The candidate hashes the exact captured bytes and checks transcript, project bytes and source file revision before accepting a response. Detected changes fail clearly and do not save a new plan. This is a before/after freshness check, not an atomic filesystem transaction.

Three injected concurrent changes (words, project, source) are accepted by the baseline and rejected by the candidate; an unchanged control remains accepted. Twenty-four tests pass. This is a planner acceptance change, not a media-rendering algorithm change; integrated gallery exports remain those tested at 0fd2f20.

A real Codex 6.1 Sol / low call on the unchanged archival transcript also passes, with the saved hash matching the exact input bytes. Evidence: [planner-snapshot.json](../evals/results/planner-snapshot.json).
