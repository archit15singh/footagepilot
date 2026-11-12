# Resolve integration evidence

12 November 2026. Same private album assets, ten-shot selection, 14-second target and authored 120 BPM score used for the matched Edits cut-only trial. Media, operation details and DRP remain local.

| Stage | Observed result |
| --- | --- |
| Native application | Free Mac App Store DaVinci Resolve 21.2.0.6 |
| Initial failure | JPEG import returned Media Offline; native picker became unresponsive |
| Recovery | macOS Force Quit/relaunch; import prepared MP4 through picker; grant only the job folder |
| API correction | Dictionary import returned nil; path-list import succeeded. Full prepared-clip append preserved exact duration |
| Timeline | Ten separately editable video clips, one audio clip, 28 native timing markers; 420 frames |
| Native render | Deliver queue showed Completed in 00:00:02; this is native render time only, not end-to-end time |
| Export | 14.0 seconds, 1080×1920, 30 FPS, H264 video and audio; full decode passed |
| Editable artifact | Native DRP exported locally; project also saved in Resolve |
| Visual correspondence | 30 samples across all shots; minimum correlation 0.99957, maximum normalized mean absolute error 0.01179 |
| Audio correspondence | Correlation 0.99958; RMS ratio 0.99986 versus prepared track; no listening assessment |
| Negative controls | Repeated first shot rejected for wrong visual content; 200 ms delayed music rejected for waveform mismatch |
| Tests | 41 passing unit tests, compile/diff checks; known-cut/onset and silence diagnostic also passes |

Reproduce preparation checks with `evals/resolve_preparation.py`; test an actual native export and its negative controls with `evals/resolve_native.py`. Sanitized results are in `evals/results/resolve-native.json`. An MP4 does not establish native provenance alone: the native timeline, queue completion and DRP were separately observed.

## Earlier cut-only evaluation

The table above records the earlier cut-only milestone. Its 41-test count and 30 samples are historical. Current styled results below use 47 tests and 42 samples.

## Qualitative comparison

| Dimension | Edits | Resolve hybrid |
| --- | --- | --- |
| Current implemented readiness | Higher: verified native photos, titles, collage, keyframes and dissolve | Native titles, four-panel collage, Fusion dissolve, music and DRP now verified |
| Matched cut-only output | 14.0-second native export | 14.0-second native export |
| Editable representation | Native elements and project | Individual native clips, collage tracks, editable TextPlus/Fusion nodes, audio and markers; DRP |
| Animation in this trial | Native Edits transforms | Crop/zoom baked into separate prepared clips |
| Automation friction observed | Local MCP executes the native workflow directly | GUI bootstrap/folder grant/console required; recovery and API mismatches added substantial setup effort |
| Creative quality | Awaiting user review | Awaiting user review; no superiority claim |

For implemented readiness on this task: **Edits first, Resolve second**. This is an engineering judgment about shipped scope and interventions, not a scored creative benchmark or a ranking of the editors’ professional capabilities. No comparable end-to-end timing was retained, so the two-second Resolve queue result cannot support a speed ranking.

The current local review contains three actual styled outputs: the first Resolve styling of the retained Edits plan, a fresh reference-conditioned Codex/Resolve plan with corrected source focal points, and the earlier styled Edits variation. All are 14 seconds from the same private source pool and score. Different plans/hold lengths mean this is a creative variation review, not a controlled renderer-quality benchmark.

## Current native graphics and complete pipeline

| Evidence | Observed result |
| --- | --- |
| Native layers | Ten main clips, four separate collage tracks, one TextPlus title, one Fusion opacity dissolve, one music track and 28 markers |
| Full live pipeline | Reference download → frame/audio analysis → Codex gpt-6.1-sol / low → prepared Resolve job → GUI execution → actual native export/DRP → verified-export |
| Planner time | 36.309 seconds, one call; not end-to-end editing time |
| Final crop correction | Reused that retained plan, regenerated source-coordinate crops, rendered the exact generated job natively and passed the final fingerprint-bound finish gate |
| Composition QA | 42 samples including quadrant content and transition frames; minimum correlation 0.99888 |
| Title QA | At 320-pixel review width, changed glyph region 184×21 pixels and 1,101 contrasting pixels; native text readback asserted during construction |
| Audio QA | Waveform correlation 0.99958, RMS ratio 0.99986; no listening judgment |
| Editable output | Native DRP automatically exported with project identity checked |
| Negative controls | Real earlier tiny-title export rejected; native cut-only export rejected for missing collage/layers |
| Checks | 47 unit tests pass; compilation and diff checks pass; browser playback, exclusive play, pause and reset checked |

Reproduce the actual styled positive and retained failure controls with `python3 -m evals.resolve_graphics JOB EXPORT --tiny-title FAILED_NATIVE.mp4 --missing-layers CUT_ONLY_NATIVE.mp4 --work NEW_DIRECTORY`. These files must come from actual local native runs; the evaluator does not ship private source media. Public sanitized measurements: [resolve-graphics.json](../../evals/results/resolve-graphics.json). Earlier wrong-shot and shifted-audio controls remain in resolve-native.json.

The first native title used a conversion that produced 17-pixel glyphs at full resolution; calibration to the shared logical size made it readable. The earlier failed export is retained as the tiny-title negative control. A separate source review found that focal points were being treated as alignment fractions; cropping now centers the specified source point with edge clamping. Native dissolve frame samples measured incoming opacity 0, .25, .5, .749 and 1 across its five frames. These are concrete correction loops; no creative preference was inferred from the fixes.

Preparation leaves passed=false / awaiting-native-render. Finishing requires the unchanged specification and retained job fingerprint, a matching native DRP archive, full decode and correspondence gates. A foreign DRP or modified job is rejected. MP4/DRP files alone cannot prove which app rendered them; native queue completion was separately observed. The full live run preceded the final fingerprint strengthening; the corrected retained-plan run exercised the final gate with actual media and DRP.

### Qualitative findings and next experiments

- **Resolve strength:** the edit stays legible as native tracks and Fusion nodes, with editable titles and automatic DRP delivery. Layer timing and composition can now be verified against a plan.
- **Edits strength:** its local MCP completes assembly/export directly. Resolve still needs a native GUI bootstrap/console and occasional app restart; external safe scripting remains unchanged.
- **Shared weakness:** current outputs adapt still photos with full-frame crops, a short collage, restrained zoom and a dissolve. They do not recreate moving-camera spin choreography or the reference's music feel. No tasteful-output or editor-superiority score is justified yet.
- **Highest-value next step:** obtain human comparison notes on the open styled gallery, feed confirmed notes into a fresh plan, then test one specific mask/reveal or source-aware colour adjustment. Compare one change at a time with prior exports retained.

Feedback support is implemented: optional visual-spec.feedback loads local compare-edits records only when a human verdict and notes exist. Unreviewed records are ignored and input fingerprints include review files. Official-source freshness checks still gate preparation; changed/stale guides require review rather than automatically upgrading verification dates. This improves future decisions while preserving human authorship and the current agent instructions.

## Research-driven correction

The public masking reference downloaded successfully (13.211 seconds, 1272×720). Its initial analysis failed on limited-range JPEG encoding, then on a sample after the last decodable video frame. Full-range JPEG conversion and video-end clamping fixed both. The corrected run produced 15 frames, three visual-change candidates and 48 RMS-onset candidates; the contact sheet shows local grading masks. Those onsets are not musical beat labels. Retained sanitized reference evidence is in `evals/results/resolve-reference.json`.

## Follow-up spatial reveal experiment

A native RectangleMask reveal now works as a controlled adaptation; the same retained plan was rendered with only the ending transition recipe changed. The actual 14-second native export passes 43 composition samples and audio checks. Both a wrong dissolve hypothesis and the earlier native dissolve export are rejected against the reveal plan. [Technique, primary-source research and qualitative limits](TRANSITIONS.md); [sanitized measurements](../../evals/results/resolve-reveal.json). Fifty tests pass. This is additional editing capability, not evidence of creative approval.
