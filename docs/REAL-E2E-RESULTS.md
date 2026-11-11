# Real-footage end-to-end results

The product ran automatically from a real human recording through MakeMyClip silence cleanup, local word alignment, a headless Codex story plan, word-level selection, MakeMyClip timeline export, Remotion and HyperFrames composition, and music/SFX mixing. The four exported videos are committed in [the gallery](../gallery/index.html). This is an engineering evaluation of an archival recording, not an endorsement or a newly generated speech.

## Run and evidence

Input: the first60seconds of the White House's September2016 weekly address. This is real talking-head footage with an existing edit and title sequence, not raw retakes. MakeMyClip reduced it to38.282seconds by removing silence. Local MLX Whisper estimated131word timestamps. Codex selected two ordered word ranges, preserving complete source sentences. The final selected timeline is21.32seconds.

| Stage | Seconds |
| --- | ---: |
| MakeMyClip silence cleanup | 15.38 |
| Local word alignment | 2.23 |
| Headless Codex planning | 9.29 |
| Apply validated word plan | 0.03 |
| MakeMyClip + Remotion export | 22.51 |
| MakeMyClip + HyperFrames export | 18.99 |
| Both mixes plus four full decode checks | 0.98 |
| Total measured stages | 69.40 |

These are single sequential runs on an Apple M6 Mac, excluding dependency installation, source downloads, implementation/debugging and reviewer time. They do not establish general rendering-speed rankings. The planner used the locally configured CLI default model, reported as gpt-6.1-sol; the CLI reported24,385tokens used. No separate API-key billing or paid media purchase occurred. Subscription usage was consumed; the run's dollar cost, electricity and cached-token billing are not known. Do not interpret this as a zero-cost service.

All four outputs fully decode and contain audio/video. Durations: Remotion narration21.334s, Remotion mixed21.333s, HyperFrames narration21.333s, HyperFrames mixed21.320s. The gallery's evidence.json records each output hash and size. Mixed audio measured mean−29.3dBFS and maximum−5.7/−5.9dBFS. The limiter is set to0.95. These checks establish no detected clipping; they do not establish a pleasing or intelligible mix.

Re-transcription of the mixed HyperFrames output recovered82of83normalized expected words, with a single substitution (“jobs” versus “job”), normalized WER1.20%. This is another ASR pass, not an independent human transcript or a listening assessment. Timing is model-estimated word timing, not guaranteed phoneme-accurate alignment.

## Qualitative findings

| Capability | Result | Strength | Weakness or required review |
| --- | --- | --- | --- |
| Story planning | Actual headless Codex run produced two valid source-word ranges. | Selects a complete excerpt and records a rationale without writing arbitrary edit commands. | The brief still requires judgment. A valid range is not proof of an unbiased, faithful or compelling story; read the retained text in context. |
| Word cuts | Actual selected ranges were exported by MakeMyClip. | Finer control than segment selections; padding is bounded by neighboring word timestamps. | Estimated boundaries can clip consonants or retain breath sounds. No cut-boundary listening claim is made. |
| Silence cleanup | MakeMyClip removed21.72seconds from the60-second input. | Removes the title silence and internal pauses before planning. | This already-produced address is an easy case compared with messy takes. Removing pauses can change rhetorical pacing. |
| Captions | Both engines rendered the retained word-timestamp captions. | Source words and edited timeline share explicit timestamps; no segment-duration interpolation is required. | Captions can split clauses or flash briefly. Reading-rate diagnostics are advisory; inspect the final video. |
| Remotion | Narration-only and mixed variants exported and decoded. | Frame-driven source composition and clear programmatic controls. | Longer measured render in this run; local font fallback can vary. |
| HyperFrames | Narration-only and mixed variants exported and decoded. | HTML/GSAP path worked with the same cut and captions. | Different typography/encoding; the sampled archived run's header color differs from Remotion. Current adapter explicitly applies accent color. |
| Music/SFX | Two real external audio assets mixed at explicit gains. | Preserves narration at unity gain before limiting; timed effects are reproducible. | The music/bell combination is a technical stress test, not a recommended aesthetic treatment of this address. Listening, ducking quality and musical fit are unverified. |
| Agent compatibility | Codex exec worked live and is the sole supported planner. | Planner output is validated data; invalid IDs, reordered ranges and stale word files are rejected. | Provider portability is intentionally outside the current scope. |

Sampled real-footage frames preserve the source's face and framing, and captions fit the inspected frame. No face, performance or voice was generated. The initial template's left-biased crop would have harmed framing; the source renderer was corrected to use the full recording when no image cards are supplied. This was a functional fidelity correction, not UI polishing.

## Interventions and failures

The real run itself required no manual timestamp editing after its brief. Inputs, the brief, music/SFX choices and gains were supplied explicitly. During implementation: the first aligner invocation could not locate FFmpeg, so the adapter now passes the configured binary directory; the source crop was corrected; per-output decode/hash evidence and stale-input checks were added. A previous synthetic policy failure remains documented in the earlier report, but it is not evidence for the new planner.

The two successful Codex plans in separate runs chose the same word ranges on the cleaned source, with slightly different rationale wording. This is limited repeatability evidence, not a broad planner benchmark. There are no independent human ratings or blinded listening scores. A separate-context model review would still not replace a human listening assessment.

## Reproduce

Set FFmpeg/ffprobe overrides if needed, authenticate Codex CLI, and configure a Python runtime with mlx-whisper for Apple Silicon:

```sh
npm ci
export SPLICEFORGE_ALIGN_PYTHON=/path/to/python-with-mlx-whisper
# Optional: point to an already downloaded compatible model or cache.
export SPLICEFORGE_ALIGN_MODEL=mlx-community/whisper-base.en-mlx
python3 evals/real_pipeline.py --work projects/my-real-run --gallery gallery
```

The first model/browser use may download weights/Chromium. The runner downloads the declared real sources, prepares only the first60seconds, runs the product's `produce` command path, and publishes four checked outputs. Use a new work directory to preserve prior evidence. The planner receives transcript text through the authenticated CLI's provider; it is not an offline language model. For private footage, that transcript transmission must be appropriate for your data policy.

For your own recording, initialize a project, add optional audio settings, then run:

```sh
python3 -m spliceforge produce projects/my-film/project.json --brief 'Your editorial brief'
```

`--skip-cleanup` skips the optional initial silence pass. The alignment adapter currently requires MLX Whisper on Apple Silicon; a cross-platform alignment backend has not been verified.

## Source provenance

- Video: [The White House archival weekly address](https://commons.wikimedia.org/wiki/File:20160917_POTUS_Weekly_Address_HD.webm), identified as a public-domain U.S. federal work. Original SHA256:a5b7f6f37a055651b3014e6954d83d18f2516903ae817736e536d148f1b5aa7f.
- Music: [Londonderry Air, Jon Hall](https://commons.wikimedia.org/wiki/File:Londonderry_Air.ogg), author-released public domain. SHA256:df88fb0243150090776bcb50c4bdf7db687d1c85e47993cf14c69c78f8187fd3.
- SFX: [Dingdingding, IOII-IOIO-IIOI](https://commons.wikimedia.org/wiki/File:Dingdingding.wav), CC0. SHA256:53b462aba98704d034a703892d0eba2bbd1bb5d65d4c7441894fc57c800a60cf.

## Practical conclusion

The expanded product now executes the requested pipeline on real footage. It is strongest as an agent-operated, inspectable editing system: explicit source words, reproducible cuts and interchangeable renderers. It still needs human editorial/listening review for story quality, rhetoric, cut continuity and sound design. The evidence does not support arbitrary unattended professional editing, raw-retake quality claims.

## Final checks

Eleven regression tests pass, including invalid word IDs, overlapping plans, cut-caption rebasing and stale evidence rejection. A fresh npm ci of the expanded dependencies completed; a fresh-directory MakeMyClip+HyperFrames2-second real-footage render decoded successfully. The transitive undici dependency is overridden to7.30.2; the final npm audit reports0known vulnerabilities. This is a package-audit result, not a security guarantee. No UI files were changed for the expanded pipeline.
