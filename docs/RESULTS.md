# SpliceForge qualitative evaluation — in progress

SpliceForge already supports a local workflow from recording import through ASR, explicit speech selections, branded captions and image-card composition, export and technical checks. Its strongest property is reviewability: the transcript, selected ranges and design are editable files shared by CLI and workbench. Its weakest property is editorial autonomy: ASR timestamps and explicit selection rules do not infer the best story.

## Evidence collected

- Real CLI renders and local whisper.cpp transcription completed on narrated demos.
- Workbench saved a brand revision, started and completed a graphics render, and played/paused the revised export in Brave. Playback advanced to9.718seconds.
- API failure recovery succeeded: hide source, observe failed job, restore source, retry successfully. Missing token rejected; invalid design rejected; byte-range response verified. See evals/API-RESULTS.json.
- Fresh npm ci in a separate dependency directory plus copied product source rendered a1-second graphics export. This establishes a clean Node dependency run on this Mac, not cross-platform support. See evals/results/fresh-install.json.
- The initial46.92-second fixture became41.92seconds of selected footage. First/revision renders took36.26/36.60seconds, excluding setup. Decoded audio was identical. These are single runs on one local machine, not performance claims.

## Strengths and weaknesses

| Area | Observed strength | Current weakness |
| --- | --- | --- |
| Speech cleanup | Explicit ASR segment selection is inspectable and reproducible. | Segment boundaries are coarse, internal pauses remain, and a rejection phrase can span segments. |
| Captions | Derived from retained speech and rebased onto the cut; character-limited groups now handle long tokens. | Timing is interpolated, not word-aligned. Fast reading warnings need human review. |
| Graphics | Timed cards, source pane, branding and deterministic frame animation render successfully. | A fixed template and simple entrances offer much less visual variety than a human motion designer. |
| Revision | Brand changes preserve selected ranges and identical decoded audio in the baseline. | Embedded screenshot branding is not rewritten; supply revised screenshots yourself. |
| Reliability | Failed jobs expose errors and permit correction/retry. | No persisted queue or restart recovery. CLI and UI must not write the same project concurrently. |
| Agent use | Standard CLI, JSON projects and shared AGENTS.md/CLAUDE.md avoid mouse-only automation. | No integrated LLM planner; autonomous editing requires a coordinating agent or explicit policies. |
| Verification | Decode, duration, API checks, frame samples and actual browser playback catch concrete failures. | They cannot establish natural speech, good pacing or storytelling. No listening assessment is claimed. |

## Failure retained

The owned synthetic fixture exposed a selection-policy failure: Whisper split the known rejection into two segments. Matching only “rejected take” left “Please discard this sentence” in the output. The technical checks still passed. Evidence is preserved in evals/results/segmentation-failure.json. The corrected two-phrase fixture policy dropped both segments; output re-transcription recovered the intended narration with neither rejected phrase. Corrected renders took30.61/30.38seconds with34.539seconds exported and14caption groups, no reading-rate warnings, and identical decoded audio. See evals/results/corrected.json. This is not a general story-selection model.

## Limits of this report

This remains a pre-release report until caption stress frames, the full fresh-project browser flow, narrow layout, and final source/evidence audit finish. Synthetic speech and simple owned screens do not establish real talking-head editorial quality. No blind human panel, subjective numeric quality score, broad speed comparison or universal unattended editing claim is supported.
