# Moving footage and source excerpts

Verified 12 November 2026. The earlier visual planner saw one thumbnail per asset and prepared video from its beginning. That was insufficient for selecting moments from moving footage. Resolve planning now accepts bounded source ranges and sparse temporal previews.

## Use

Provide your source clips as visual-spec assets and select Resolve with `recreate --backend resolve`, or set `native_backend` to `resolve` for `visual-plan`. The planner receives each video's actual duration and bounded temporal frame strips, grouped by asset ID. Up to three windows cover the beginning, middle and end; each spans at most four seconds and contains five ordered frames. Short clips use one window. Still assets receive one image. Preview timestamps and metadata are retained in plan.json alongside source hashes.

Resolve's structured plan includes `source_start` seconds for shots and panels. The compiler checks that the start is finite/nonnegative and start + planned hold fits the actual video duration. Stills require zero. A prepared visual manifest can also request it directly:

```json
{"shots":[{"path":"my-clip.mp4","source_start":8,"duration":2,"fit":"contain"}]}
```

Preparation validates the frame-rounded range again, accurately seeks into the original, and transcodes only the requested excerpt. Source timestamp/path provenance is retained for main shots; all source and prepared hashes are retained. Original files stay unchanged. The timeline contains separately editable prepared clips, not handles back to the original untrimmed footage. Source audio is currently discarded in this visual pipeline; the supplied music is prepared separately. Use the speech pipeline for narration-oriented editing.

Edits currently rejects nonzero source ranges before starting its native client. Its schema omits range choices. This is explicit unsupported execution, not a fallback to frame zero. Nonzero native Edits trimming needs a separate runtime test before enabling it.

## Actual live evidence

A retained real moving Instagram masking reference was used locally as a range diagnostic, not as a finished personal film or a new creative recreation. An explicit brief requested exactly the 2–4s and 8–10s excerpts. Codex gpt-6.1-sol / low selected both with six asset previews; the call took 13.520 seconds. This verifies following bounded range instructions, not autonomous selection of the best moments.

The inherited dark travel-title settings were unsuitable for the chosen letterbox. Before native preparation, the title was changed to white and moved onto the black letterbox. That intervention is recorded; the selected source ranges were unchanged. Resolve's existing native job body was executed with the prepared job parameters and exported four seconds, two moving clips, title, supplied score and an editable DRP. Deliver showed Completed in one second (render-only time).

An independent evaluator uses output-side seeking that decodes/discards from the original; preparation uses input-side seeking. [FFmpeg's official documentation](https://ffmpeg.org/ffmpeg.html) describes accurate seeking during transcoding. Six source timestamp samples match prepared excerpts, with minimum correlation 0.99981. Both wrong-start-at-zero controls are rejected. Native frame/title/audio correspondence passes separately. Fifty-three unit tests and compilation pass.

The first independent test included black letterboxing and failed to distinguish one wrong-start control. That failure was retained. The revised test isolates the actual picture rows for full-width contained material; it is not a general crop/motion metric. Generic native QA still uses sampled correspondence, so large uniform regions can weaken it. The evaluator reports weak controls honestly and rejects an evaluation with no discriminative wrong-start control.

```sh
python3 -m evals.source_ranges MANIFEST.json JOB.json NATIVE.mp4 --work NEW_DIR
```

See [sanitized measurements](../../evals/results/source-ranges.json). Personal source paths, reference video, previews, generated manifests and native project remain local.

## Limits and next quality work

The earlier three-frame previews were sparse evidence. The current bounded strips improve local temporal context but still leave gaps. They can miss a subject's action, a flash frame, a transition, or a better range between samples. The planner must not claim continuous motion direction or camera matching from them. Range selection currently follows the supplied music grid; it does not listen to reference music. More faithful recreation needs suitable original moving footage, denser analysis of candidate ranges, and visual/human review of continuity. The rejected slideshow feedback is not resolved by this diagnostic. No creative preference is inferred from technical success.


## Bounded source windows

A visual-spec asset may supply `preview_windows`, a list of1–3 objects such as `[{"start":8,"end":10}]`. Each interval must fit before the final.1second safety margin and span at most four seconds. Otherwise beginning/middle/end windows are chosen deterministically. These are previews for selection, not mandatory excerpt bounds: the compiler still validates the selected source range against actual video duration. Prefer ranges supported by previews; unseen intervals remain unverified.

For each video window, `visual-plan` retains a horizontal JPEG strip and its constituent frames under `source-previews/`. `plan.json` records each window's requested source sample times, left-to-right layout and image hashes. These are requested seek coordinates, not claimed exact decoded-frame PTS. Original source hashes are checked again after planning. The model sees one strip per window, preserving the previous maximum of three image attachments per video while providing up to fifteen temporal samples. It must not infer continuous motion or exact camera trajectories from gaps. This does not automatically rank every action in a long clip.

The implementation uses sequential FFmpeg accurate seeks and aspect-preserving scale/pad, then stacks retained still frames for analysis. The [official filter documentation](https://ffmpeg.org/ffmpeg-filters.html) describes scale/pad and frame mosaics; frame-window choice is FootagePilot logic, not a claim of vendor semantic analysis. Reviewed12November2026; recheck after decoder/app changes. Padding here is preview-only; the native deliverable follows the shot's independent fill/contain decision.


The range evaluator also supports full-frame fill/no-zoom excerpts. For variable-rate material it compares output-side decoded source samples within a nominal source/output frame quantum while retaining the existing MAE/correlation thresholds. It reports requested and matched times, tolerance and partial samples before a failure. This is bounded temporal correspondence, not exact original PTS identity. FFmpeg documents [`r_frame_rate`](https://ffmpeg.org/doxygen/8.1/structAVStream.html) as a guessed base rate; it can differ substantially from average frame rate. The evaluator considers both plus the output rate. Large variable-frame gaps remain outside this nominal tolerance and may require PTS-based analysis. Do not widen tolerance to obtain a pass.


For a source with visible movement, add `--freeze-opening` to `evals.source_ranges` to generate a decodable first-shot freeze control and require visual rejection. A nondiscriminative source fails that evaluation instead of earning a motion claim. In the actual original-video recreation, the independent evaluator checked21source samples and rejected7wrong starts plus the frozen opening; see [results](RESULTS.md).
