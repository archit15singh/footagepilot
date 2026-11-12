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

## Moving source-range follow-up

The visual planner now receives multiple timestamped previews per video and emits bounded source in-points for Resolve. An actual Codex call selected explicitly requested 2–4s and 8–10s excerpts from retained real moving footage. Native Resolve exported both as a four-second diagnostic. Six independent decoded-source samples pass; both zero-start controls are rejected after excluding letterboxing from the independent comparison. The inherited title needed a contrast/position correction before native execution. [Full evidence and limits](VIDEO.md); [sanitized metrics](../../evals/results/source-ranges.json). This is source-range execution evidence, not a finished creative recreation.

## Frame-cited reference follow-up

The real still-photo planner run now inspected 18 timestamped reference frames, returned five cited technique observations and cited source evidence for all nine planned shots. Manual inspection supported the cited title card and partial/asymmetric tile observations. Fabricated-frame and motion-as-visible controls were rejected. The actual 15.5-second native Resolve follow-up exported and passed composition/title/audio checks; see evals/results/reference-grounding.json. The inferred mask progression remains uncertain. The model explicitly converts asymmetric reference tiles into four quadrants because the current compiler forces that layout; this remains a fidelity gap, not a solved match. Fifty-five tests pass. The earlier missing still preview was a real regression caught by this run and corrected by omitting image seeking.

## Progressive reference-layout follow-up

The quadrant restriction is removed for Resolve. A fresh frame-cited Codex plan and native 14-second export now implement a delayed gold title on black and seven unequal-axis tiles arriving progressively, with incomplete rows/empty space. A real axis-link failure was caught and corrected by disabling ZoomGang before setting width/height. All 55 composition/panel samples pass; erasing only the last tile in an otherwise decodable control is rejected. The legacy quadrant export still verifies. [Primary-source research, exact workflow and qualitative limits](LAYOUTS.md); [sanitized results](../../evals/results/progressive-layout.json). Fifty-nine tests pass. This fixes a demonstrated structural mismatch; typography, camera motion and musical feel are not claimed equivalent or creatively accepted.

## Reference title families

The visual planner previously discarded font choice and defaulted to Helvetica Neue. Resolve specifications can now supply installed `title_fonts`; the JSON schema constrains selection and the compiler preserves it. Native TextPlus asserts family input readback. The controlled Didot variant used the retained progressive plan, changed only its title family, and passed55visual samples, full decode, title contrast/height and soundtrack correspondence checks. Queue completion was observed at2seconds(render only). A separate real Codex gpt-6.1-sol/low call took57.421seconds and selected Baskerville, citing the reference title frames; the new14-second plan compiled successfully but has not yet been natively rendered. These are separate experiments. See `evals/results/reference-typography.json` and [layout/typography instructions](LAYOUTS.md). Current suite:60tests.

Visual inspection showed the controlled candidate's gold serif lettering on black. Exact reference typeface, animation, music feel and human preference are still unverified. No fonts were installed. Local preparatory failures (missing FFprobe environment, relative output paths) were retained; corrected environment and absolute job paths produced the successful native job. An extra wrapper `end` in the interactive paste was rejected by Lua before execution and corrected; product-generated console script was unaffected.


## Progressive title sequence

A4FPS reference-opening contact sheet showed staged title lines between rapid cuts. The next brief explicitly requested three original lines on the supplied authored half-second grid and a later collage. Actual Codex gpt-6.1-sol/low returned a14-second plan in71.719seconds: three Baskerville lines entering at0,.5,1seconds, all ending2seconds; eight main shots and six staggered independent rectangular panels. No model-plan edits were made before native preparation. Resolve assembled12video tracks plus music, exported a DRP and completed its native render queue in2seconds(render only).

The exported opening contact sheet was inspected: one, then two, then three gold serif lines on black. Full decode,53composition/panel samples(minimum correlation.96837), three title size/contrast checks,14title entry/exit samples and soundtrack correspondence pass. Each title enters exactly on the supplied grid. This establishes timing correspondence, not hearing the reference song. The prior single-title export also passes the new timing checker.

One initial full verification failed on the detailed final tile: at64×64 whole-canvas sampling, the panel was only20pixels wide and its correlation was.88993. Inspecting the native crop showed correct content. Increasing individual-panel sampling to256×256 yielded.96837 without changing thresholds. The revised full check passed; the actual missing-panel control is still rejected. The failure log is retained locally. This is a verifier resolution correction, not a modified film.

`python3 -m evals.title_sequence JOB.json NATIVE.mp4 --output NEW_DIRECTORY` checks the actual native movie and creates two decodable black-card controls: erase the last line, and show it before its planned entry. Both are rejected (missing at frame30; early at frame29). The controls use FFmpeg solely to alter the native export for evaluation. See `evals/results/title-sequence.json`. Current suite:62tests.

The sequence recreates progressive line appearances rather than a single fixed title. It does not implement character write-on, camera matching or solve source-footage suitability. Music feel, continuity and exact reference style still need creative review. No human preference is inferred.

## Uneven audio-cue timing

`music-cues` measured27interior RMS novelty candidates in the14-second supplied score, retaining0/end as boundaries. Unlike the earlier120BPM grid, the resulting29coordinates are uneven. An actual Codex gpt-6.1-sol/low call took50.996seconds and chose seven main shots with cue spans4/4/3/4/3/6/4, progressive serif lines and four staggered panels. No changes were made to the model plan before native preparation. Resolve exported14seconds/420frames and an editable DRP; its native queue completed in2seconds(render only). Native marker notes explicitly identify onset candidates, not verified beats.

Full decode,46composition/panel samples,14title timing samples and soundtrack waveform correspondence pass. All six selected cut positions and three title entries align with the selected rounded cue frames. The repeated-first-shot control is rejected for visual mismatch; the200ms shifted-audio control is rejected for waveform mismatch. Cue/source hash checks reject different music, invalid coordinates and ambiguous mixed BPM/cue inputs. Layer durations now use rounded absolute end minus rounded start; the old adjacent-panel rounding regression preserves adjacency instead of rejecting a valid pair.

A separate known uneven-pulse diagnostic recovered five synthetic attacks at their exact10ms bins; silence produced no usable cue file and different-source binding was rejected. The initial diagnostic pulse at.2seconds was deliberately filtered by the requested.3second boundary gap, so the expected fixture was corrected to honour that setting; the first failed fixture is retained locally. This diagnostic is not evidence of real-song beat/phrase accuracy.65unit tests pass. See [music-cue usage](MUSIC-CUES.md) and `evals/results/music-cues.json`.

The contact sheet shows staged serif lines, longer scenic holds, a top-row collage followed by a larger lower panel, and an uncluttered sea ending. The new movie and prior grid-based movie use different plans, so no controlled creative superiority is claimed. RMS peaks can lag musical attacks; listening, phrase-level fit, moving-source suitability and human acceptance remain unresolved. The native cut/panel/title execution is now driven by the measured track rather than assuming a constant tempo.


## Original moving-source recreation

Six portrait travel clips were selected through the signed-in Google Photos UI and downloaded locally. They replace the earlier still-photo pool; original files, archive metadata and identities stay private. The planner now saw90timestamped samples in18bounded frame strips rather than18widely separated individual frames. Each of the six sources contributed three windows; retained strip hashes were checked. Actual Codex gpt-6.1-sol/low took70.235seconds and chose seven nonzero main excerpts across all six clips, three moving panels and progressive Baskerville titles. All artificial zoom values were zero. No plan edits were made before native preparation.

Resolve assembled seven main clips, three independent panel tracks, two black spans, three TextPlus clips, music and source-bound cue markers. The native queue completed in2seconds(render only), exporting14seconds/420frames and an editable DRP.38native composition samples,15title timing samples and waveform/decode checks pass.21independent source-time samples match prepared excerpts at minimum correlation.99976; all seven wrong-start-at-zero controls are rejected. A decodable control freezing only the opening native shot is rejected at frame31. See `evals/results/moving-sources.json`.

The first exact-time range evaluation failed during conversion from variable-rate sources to30FPS. A base-rate-only nominal tolerance still failed on a source reporting120as its guessed base rate but approximately30averageFPS. The corrected evaluator uses the larger nominal source/base/output frame quantum, reporting each requested/matched time and tolerance (maximum.04167seconds in this run). Pixel thresholds were unchanged. Both failures and partial samples remain local. This is bounded temporal correspondence, not exact original PTS identity; large variable gaps may require further analysis.

The contact sheet was inspected: a walking opening, a mid-film progressive title, trees/fields/gardens, a moving three-panel sequence and a cave-boat ending. The frozen-opening rejection establishes that delivery checks distinguish visible movement for this opening. It does not establish smooth continuity, an exact camera match or subjective storytelling quality. This is a new source pool, so no controlled superiority over photo variants is claimed.67unit tests, compile and whitespace checks pass. Musical feel and human acceptance remain unreviewed.
