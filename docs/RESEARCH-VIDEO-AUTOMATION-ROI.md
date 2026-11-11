# Video automation research: smallest changes with the best expected return

Research date: 2026-11-12. Product reviewed: FootagePilot main `bfa6c91284693b45807c2d28d9aad2a7abc70608`.

## Recommendation

Keep the current Codex `gpt-6.1-sol` / low planner and existing rendering adapters. First improve speech boundaries, captions and audio balance. Add selective rendering and stage reuse when iteration speed is the priority. These address visible gaps in the shipped pipeline without replacing its architecture.

This is a research ranking, not a measured improvement benchmark. Effort estimates assume one developer familiar with the code; media regression work can exceed the estimate. No product changes, installations or new pipeline evaluations were performed during this research.

## Method and evidence limits

Used bounded recursive discovery: YouTube walkthrough → creator description and linked tools/repositories → upstream documentation and selected implementation → comparison with local product code. Stopped expanding branches when they repeated the same ideas. This is not an exhaustive YouTube survey.

Read four newly retrieved English video transcripts, plus Ali Abdaal’s transcript retrieved earlier. The four new transcripts contain 1,839 segments and approximately 13,105 words. Metadata came from the actual YouTube pages; transcripts were retrieved through the existing CLI environment. Automatic captions can misrecognize names. This was transcript/documentation research, not a visual review of every demonstrated edit. Repository inspection establishes implementation patterns, not successful execution on our machine. Creator time savings and quality percentages remain self-reports.

Local raw research material is ignored under `projects/research-youtube/` and `projects/research-sources/`. The links below are the public source trail.

## The most useful YouTube builds

| Build | Useful section | Transferable lesson | Qualification |
|---|---|---|---|
| [Guney Topcu: Claude Code + Remotion Edited this Entire Video](https://www.youtube.com/watch?v=QYUV9FjR5-M) | [Pilot scene, about 5:15](https://www.youtube.com/watch?v=QYUV9FjR5-M&t=315), [timing failure, about 8:06](https://www.youtube.com/watch?v=QYUV9FjR5-M&t=486) | Approve one scene before building the rest; preserve the time map when footage speed changes. He describes lost audio and graphics drifting after a 5% speed adjustment. | Guided workflow with corrections, not unattended reliability evidence. |
| [Guney Topcu: I Quit Remotion After Claude Made These Motion Graphics](https://www.youtube.com/watch?v=fvvRCpCFJYk) | Frame audit around 4:00; kit around 6:38 | Judge actual motion and holds, not merely whether an MP4 renders; encode reusable visual constraints. | Preference for HyperFrames is from this creator’s examples, not a general renderer benchmark. |
| [Aidan Stanik: How I Edit Videos with Claude Code](https://www.youtube.com/watch?v=BNPlUj-CxB0) | [Asset organization 7:39](https://www.youtube.com/watch?v=BNPlUj-CxB0&t=459); [reusable skills 23:52](https://www.youtube.com/watch?v=BNPlUj-CxB0&t=1432) | Organize assets and reuse working animation instructions; inspect and revise in Remotion Studio. | Manual creative direction remains part of the process. |
| [Adam Goodyer: How to Edit Videos Properly With Claude and Remotion](https://www.youtube.com/watch?v=bDCLT4Je6WA) | Pipeline around 0:50; architecture around 11:40 | Separate audio analysis, transcription, edit planning and graphics. | Includes external services; it is not evidence of a wholly local open-source stack. |
| [Ali Abdaal: I Tried Fully Automating My Video Editing With AI](https://www.youtube.com/watch?v=C0jOKDJtK9s) | [Rethink 22:42](https://www.youtube.com/watch?v=C0jOKDJtK9s&t=1362); [motion plates 27:38](https://www.youtube.com/watch?v=C0jOKDJtK9s&t=1658); [verdict 44:20](https://www.youtube.com/watch?v=C0jOKDJtK9s&t=2660) | Clean speech edit and short animation compositions are separate tasks; storyboard before rendering. | He refilmed and manually cleaned speech. Six hours and “97%” are subjective reports, not an autonomous editing benchmark. |

Most tutorial agents are Claude-based. Their useful contribution here is the file contracts, stage boundaries and checks; none requires adding a Claude backend to FootagePilot.

## Open-source trail and what to reuse

- [paulduplessis/agentic-video-editor](https://github.com/paulduplessis/agentic-video-editor), MIT: waveform-informed boundaries, bounded handles, unified A/V rendering, and incremental revision. Inspected [plan_cut.py](https://github.com/paulduplessis/agentic-video-editor/blob/main/.claude/skills/rough-cut/scripts/plan_cut.py): reads an audio envelope and limits boundary movement against neighboring removed words. Reuse the design after testing on our footage; the README’s timestamp-error figures are not measurements of our transcriber.
- [kingbootoshi/video-alchemy](https://github.com/kingbootoshi/video-alchemy), MIT: explicit JSON edits and remapping source word times onto the edited timeline. Particularly useful as an invariant across captions and B-roll. Its advertised transcription speed/accuracy was not reproduced here.
- [hcsum/video-editor](https://github.com/hcsum/video-editor): separate the base cut from Remotion composition and inspect stills before a full render. Reuse the workflow concept; verify licensing before copying source.
- [0xSero/video-edit](https://github.com/0xSero/video-edit), MIT: output verification and a Mac-focused local workflow, including privacy checks for screen recordings. Its Apple Vision dependencies limit portability; privacy detection is valuable when screen capture becomes an input class.
- [Silero VAD](https://github.com/snakers4/silero-vad): optional local speech-activity gate. VAD identifies speech regions; it does not decide which take is semantically correct or locate every consonant perfectly.
- [WhisperX](https://github.com/m-bain/whisperX): optional forced-alignment fallback when measured timing errors justify it. Its documented limits include unaligned dictionary-external tokens, overlapping speech and imperfect diarization. Do not replace the functioning MLX path simply to add another dependency.
- [Auto-Editor](https://github.com/WyattBlue/auto-editor): configurable edit margins are a useful reference for keeping breathing room. Aggressive silence removal is not synonymous with good pacing.
- [Guney motion kit](https://github.com/GTAI-1/guney-motion-kit), GPL-3.0 as reported by GitHub: useful public authoring examples. Treat license compatibility as a separate decision before incorporating kit code; use original templates for a minimal patch.
- [FFmpeg filters](https://www.ffmpeg.org/ffmpeg-filters.html): existing executable already provides crossfades, ducking, loudness measurement/normalization and black/freeze checks. Most first-sprint improvements need no additional service.

## Top seven implementation opportunities

Impact scores are engineering judgments from 1 (small) to 5 (large), not measured quality scores. Ranking balances expected editing benefit, existing implementation gaps, effort and new dependencies; it is not an arithmetic precision claim. Runtime column describes added processing, not promised savings.

| Rank | Minimal change | Quality | Reliability | Estimated effort | Added runtime / dependencies | Confidence |
|---|---|---:|---:|---|---|---|
| 1 | Speech-safe boundaries with bounded handles and short audio joins | 5 | 5 | 1–2 days | Low local audio analysis; optional VAD later | Medium-high; exact benefit needs messy footage |
| 2 | Phrase-aware captions and short-tail repair | 4 | 4 | Half–1 day | Negligible; use existing word times | High that current warning cases can be reduced |
| 3 | Voice-first music ducking, fades and measured loudness | 4 | 4 | Half–1 day | One local audio pass; FFmpeg | High for controllability; listening needed |
| 4 | Enforced planner duration budget and meaning-preservation checks | 4 | 5 | Half–1 day for budget; 1–2 more for semantic review | Deterministic budget gate; optional bounded extra Codex call | High for budget; medium for semantics |
| 5 | Boundary-focused output QA with failing negative controls | 3 | 5 | 1–2 days | Short local checks; optional ASR pass | High for detecting specified defects |
| 6 | Resume by stage fingerprint; render only requested backend | 2 | 4 | 1–2 days | Reduces repeated work; no new service | High for avoiding known redundant stages |
| 7 | Small reusable visual vocabulary, storyboard and pilot scene | 5 | 3 | 2–4 days | Cheap still previews, then selected renders | Medium; visual taste needs review |

### 1. Speech-safe boundaries

Current `footagepilot/planner.py:apply_plan` uses fixed word padding (40 ms before, 60 ms after), bounded by neighboring word times. Start with an RMS-envelope check close to each boundary, conservative limits on movement, and room-tone-aware audio joins. Do not shift video independently or extend into rejected words. Silence cleanup must also preserve its source-to-cleaned time map; planner-only fixes cannot repair consonants already deleted upstream.

Accept when adversarial clips retain quiet word attacks and endings, exclude rejected filler, keep A/V aligned within one output frame, and sound preferable in blind listening. Include breaths, quiet initial consonants, retakes and background noise. A zero-crossing alone is not proof of a safe speech boundary.

### 2. Readable captions

Current `graphics.py:word_captions_for_cut` groups by seven words or 64 characters, resetting at cuts; short/fast groups only generate warnings. Split at phrase punctuation, merge tiny tails where time permits, enforce line fit, and use configurable minimum duration/reading-rate gates. Never extend a caption across a removed word or unrelated shot merely to pass a timing threshold. If a range is too dense, flag it for a shorter caption or revised edit.

Accept when known short-tail cases are repaired, timings remain within the retained speech interval, and text fits both renderers. The existing 22 characters/second warning is a project heuristic, not a universal accessibility standard.

### 3. Voice-first audio

Current `audio.py` uses fixed gains, summation and a peak limiter. Add narration-driven music ducking, start/end fades, and integrated loudness plus true-peak reporting. Normalize once at the final stage with a configurable delivery target; avoid independently processing every segment. Keep SFX opt-in until event timing is deliberate.

Accept on both loud and quiet narration, with no clipped peaks, obvious pumping or obscured words. Loudness meters cannot establish musical fit; listen to final exports. No universal platform loudness target is claimed here.

### 4. A planner contract beyond valid JSON

Current `planner.py:validate_plan` enforces ordered, disjoint, valid word ranges, but not a requested output-duration budget. Add explicit min/max seconds and calculate padded duration before render; retry once or fail clearly. Then surface incomplete sentences, lost negations, unexplained pronouns and duplicate takes for semantic review using source context. These are heuristic/LLM checks, not deterministic guarantees.

Accept when over-budget and malformed plans fail before expensive rendering; adversarial meaning-changing edits must be flagged. Keep the user-selected model and reasoning setting.

### 5. Verify the risky moments

Current `pipeline.py` verifies full decode, metadata and hashes. These prove technical integrity, not editorial quality. Generate short A/V review clips around every join; sample first/last frames around overlay intervals; detect unexpected black/frozen frames; compare output speech with selected source text. A legitimate still frame must not automatically fail a freeze check.

Accept when deliberately introduced missing words, wrong overlays, black flashes and audio dropouts are detected. WER alone misses prosody and some meaning errors. Keep human listening and a small blind preference review.

### 6. Reuse expensive stages

Current `produce` runs both renderers sequentially and rebuilds stages. Add an engine selection option, reuse one canonical base cut, then cache stage outputs by source content, settings, tool versions and upstream artifacts. A changed brief should invalidate planning onward, not transcription; a music change should invalidate only mixing onward. Validate cached outputs before reuse and retain failure evidence.

The recorded run spent about 22.51 s in the Remotion stage and 18.99 s in HyperFrames, within a 69.40 s run. These are historical pipeline-stage timings, not a new speed benchmark or pure renderer comparison. Selective rendering can avoid an unwanted stage; exact end-to-end savings need measurement.

### 7. Visual quality from constraints

Existing renderers have basic captions/cards but no semantic shot-planning stage. Add only a few original components: product screenshot with controlled zoom, comparison, number/chart callout, and picture-in-picture. Create a timed shot manifest tied to retained word IDs and inspect one representative scene plus contact sheet before rendering everything. Source real assets and avoid invented product UI.

Accept when overlays match spoken claims, text remains readable, face visibility follows the brief, and no flash frames or stale assets appear after a branding revision. Still previews cannot verify animation pacing; inspect short motion previews too.

## Evaluation before claiming improvement

Use the same real recordings and locked briefs before/after each patch. The current gallery source is already-produced archival speech, not a raw retake stress test; it is insufficient to establish cleanup quality.

Create a small real-footage set spanning quiet consonants, retakes, numbers/names, breaths, noisy rooms and screen capture. Preserve source media and timestamped ground truth for specific checks. Include intentional bad outputs as negative controls.

Report: cut word-loss/contamination, caption timing and reading-rate violations, duration-budget compliance, integrated loudness/true peak, speech coverage, A/V drift, detected versus missed defects, cold/warm runtime and retries. Blindly compare listening quality and visual preference with human reviewers. Do not combine all of these into an unsupported single quality percentage.

## Defer until evidence justifies the cost

New planner models, another NLE/MCP migration, elaborate multi-agent orchestration, person segmentation/matting, automatic vertical reframing, a general stock-footage agent and UI polish. They may have value for particular use cases, but they address the current proven gaps less directly. Prioritize speaker tracking only when vertical delivery is required, and forced alignment only after timing error measurements.

Suggested order: captions for the quickest isolated patch; boundaries for the strongest speech-quality protection; audio next; then duration gates and targeted QA. For repeated iteration today, selective rendering can move ahead of these as a small separate performance patch.
