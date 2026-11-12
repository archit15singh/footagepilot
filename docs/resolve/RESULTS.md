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

## Frame-cited reference review and revision

`review-reference` now produces model suggestions from actual reference/candidate frames, with explicit uncertainty and hashes, and optional visual-spec `model_reviews` feeds those suggestions into a new plan. Human feedback stays separate. The first real review used four distributed windows and omitted the reference collage; its uncertainty disclosed that gap. Six-window sampling then supplied18reference and12candidate frames. Codex gpt-6.1-sol/low took31.322seconds and returned four findings. The decisive layout citation was inspected directly: reference tiles occupy the top row while the candidate tiles form a centered strip.

A new explicit brief prioritized that confirmed layout mismatch. The review-bound Codex plan took65.825seconds and returned a top-aligned three-column row plus a later second-row tile. Other plan choices also changed, so this is an iteration, not a controlled single-factor quality experiment. No model-plan edits were made before native preparation. Resolve exported14seconds/420frames and a DRP; its queue completed in2seconds(render only).43composition/panel samples,10title timing samples and audio/decode pass. The rendered collage frame was inspected and shows the planned top row/second-row structure.

The missing-panel control ultimately was rejected at frame287. Two earlier checks threw H264/empty decoder exceptions on unchanged prepared panels; neither was credited as successful negative rejection. Panel hashes/full decodes were rechecked, and an instrumented check of the same control produced the expected visual mismatch without regenerating any movie. This intermittent decoder behavior remains a reliability limitation, not a creative-quality result. Initial evaluation logs and recheck record remain local.

69unit tests verify citation/temporal labels, stale-evidence rejection and preventing model records from asserting human acceptance; compilation/whitespace pass. See `evals/results/reference-review.json` and [usage/limits](REFERENCE-REVIEW.md). The reviewer cannot verify semantic truth, continuous camera paths or listening quality. Its typography-weight suggestion exceeded the current visual-plan controls and was not implemented; future prompts now state that limitation. The model has not acquired human taste, and no acceptance or beauty score is inferred from this loop.


## Automatic selected-track analysis inside recreation

`music_analysis` now replaces manual cue copying in `recreate --backend resolve`. The run retains `analyze-selected-music`, `music-cues.json` and a generated specification with source-bound coordinates before invoking Codex. Mixed explicit/automatic timing and non-Resolve backends fail before run creation. Analysis failure remains a failed stage; it never substitutes a guessed BPM grid.

The live run used the same six moving trip clips, retained reference and authored score. It measured29coordinates, planned with Codex gpt-6.1-sol/low in64.617seconds, prepared and executed a new native14-second/420-frame Resolve project, saved itsDRP and passed `recreate-finish`. The queue showedCompleted00:00:02(render only).42composition samples,10title timing samples and audio correlation.99958pass. All seven cut offsets are0frames relative to the measured coordinates. This is timing-coordinate correspondence, not a musical-beat or creative-quality verdict. Separate silence and short-track runs stopped at the analysis stage without creating a plan or native job; known-pulse/source-binding diagnostics also pass.72unit tests, compilation and whitespace checks pass.

The first invocation retained a `reference_url` and failed on a missing yt-dlp binary. A new spec explicitly selected the already-retained reference analysis; it did not claim a new download. No manual model-plan edits were made. Native console focus required restart of the agent-owned project; setting the AX input worked after a coordinate click failed. These interventions remain local.

The first two verification attempts failed in the existing tiny-panel frame sampler. Diagnostics reproduced allocator aborts and nondeterministic RGB pixels with thisARM64 FFmpeg9.0build; both input seek and decode-from-start paths failed, and single-thread decoding also failed. FFmpeg’s scalar path (`-cpuflags 0`) produced48stable diagnostic samples. Resolve QA now uses that path for bounded frame samples, with no silent retry, movie regeneration or pixel-threshold changes. A subsequent real-panel regression made72calls across24frame/size groups with identical repeat hashes; the native export then passed. The unchanged retained missing-panel control still rejected at frame287. Empty-stderr subprocess failures now report the exit status. Exact underlying decoder/scaler fault isolation is not claimed, and the observed remedy is not a universal decoder guarantee. Run `python3 -m evals.frame_sampling JOB.json --output NEW_DIRECTORY` against real prepared panels after changing FFmpeg builds. See [FFmpeg CPU flag and seeking documentation](https://ffmpeg.org/ffmpeg.html).

Sanitized result: `evals/results/automatic-music.json`. Music feel, continuous-motion continuity and human creative acceptance remain open. This iteration automates existing evidence plumbing and stabilizes the observed QA path; it does not establish a better-looking film.

The first short-track diagnostic mistakenly used a42-second score against a20-second budget and correctly reached planning. That worker was stopped and its failure retained. A corrected5-second source against the14-second budget then rejected before planning. The initial fixture was not credited as a successful negative control.


## Recreation with the selected reference soundtrack

`music_from_reference: true` now selects the exact analyzed reference media as the local audio source, excluding a separate `music` path. Resolve recreation records selection fingerprints, measures that recording’s cues and binds it into the planner/native-job inputs. Completed analysis, audio presence and an unchanged reference-media hash are required. It uses the whole audio mix from time zero, not an isolated/identified song. [Usage and limits](MUSIC-CUES.md).

The initial13.5-second run037selected25coordinates and prepared an8-shot plan, but inspection found one cut atframe91rather than92against a3.05-second cue. Binary floating subtraction yielded1.7299999999999998for3.05minus1.32; the existing half-up frame converter therefore rounded the cumulative boundary down. A regression first failed with `[40,91,156]`; decimal endpoint subtraction now produces `[40,92,156]`. Prepared037was retained unrendered, not credited as a native success. No rounding policy or QA threshold changed.

A new complete run038planned with Codex gpt-6.1-sol/low in67.241seconds, then prepared and rendered13.5seconds/405frames in freeResolve21.2.0.6. The actual queue showedCompleted00:00:01(render only); DRPand movie retained. `recreate-finish` passed44composition samples,10title-timing samples and audio correlation.99992with gain ratio.99992. All seven cut offsets are0framesagainst the measured reference-audio coordinates. Source selection, analysis, cue map, planner inputs and native inputs agree on the exact reference-media hash. No model-plan edits were made.75unit tests, compile and whitespace checks pass; replacement/missing-audio/ambiguous reference-source requests reject in tests. A temporary-path test expectation was corrected for macOS resolved `/var`paths; the implementation was unchanged.

The rendered contact sheet was inspected: walking opening, progressive gold title card, fields/garden, a three-column top row and later second-row tile, followed by cave-boat entry/interior. Sparse1FPScontact samples missed the short second title line; dedicated title entry/exit checks cover it. The regular serif title is still visually modest; source previews and continuous-motion analysis remain limited. Reusing the exact audio improves source fidelity, but this is not proof of musical feel, beat/phrase detection or creative superiority. The fresh plan differs from prior films, and no human preference is recorded. Public evidence is `evals/results/reference-soundtrack.json`; reference/audio/native artifacts stay local.


## Reference-focused title scale and weight

Resolve visual plans now choose bounded `title_size` and `title_bold`; the compiler carries them into every native title line and assembly asserts Style/Size readback. Old recorded plans retain28/regular. Planning/review also accept up to two `reference_times` to include important retained frames missed by distributed cut-neighbour sampling. [Contract/research/limits](TYPOGRAPHY.md).

The reference’s1-second frame was inspected: bold gold serif text on black. It was missing from the distributed close-up evidence (though present in the broad contact sheet). Initial039planned56/bold in66.481seconds; it remains prepared/unrendered. Fresh040included the focus frame and Codex chose40/bold Baskerville in66.628seconds. The installed native TextPlus readback assertions passed, Resolve’s queue completed in2seconds(render only), and `recreate-finish` verified13.5seconds/405frames with45composition samples, two contrast/size checks and audio correlation.99992. No manual model-plan edits. Actual title frame/playback inspected.

At320-wide sampling, the same word“Follow” grew from60×17pixels/294changedpixels in the earlier28/regular render to101×23pixels/1054changedpixels at40/bold. Both samples precede their second line. This measures the local title change, not whole-film superiority; the fresh plan changed other choices. Four title-timing samples pass and five are explicitly ambiguous because conservative title bands overlap; none of those five is credited as passed. The glyphs appear separated in the inspected frame, but exhaustive entry/exit verification remains unproven. An extra attempted reference gold-component diagnostic failed to decode the reference still with the video QA sampler; no reference pixel metric is credited.78unit tests, compilation and whitespace pass. `evals/results/planned-typography.json` retains sanitized findings. Creative acceptance remains unreviewed.


## Title-region timing follow-up

The five ambiguous samples on the unchanged bold040export exposed overly broad title bands. Timing QA now splits potentially simultaneous regions at planned vertical-centre midpoints, retaining the original contrast/ink thresholds and minimum glyph-height requirement. Regions without enough room, or indistinguishable same-centre titles, remain ambiguous. Actual active neighbours at sequential handoff boundaries are included, preventing a valid successor title from being falsely treated as an overlong prior title.

All9sampled title boundaries on the same native movie now pass. The movie hash is unchanged; no new render or creative variant is credited. Decodable controls derived from that native export reject a missing second line atframe27and an early second line atframe26. Control stills were inspected: the first line remains in both; the second is absent/early respectively. The first attempt to extract an inspection still used an invalid`.4`time literal; changing it to`0.4`fixed that inspection command, without changing the movies or evaluator. Prior native023and038title sequences pass14and10samples. Full native QA passes45composition samples,2title-size checks and audio correspondence.81unit tests, compile/whitespace pass. Same-centre simultaneous and adjacent sequential cases are covered by region tests.

See `evals/results/title-regions.json`. The regions establish sampled visual timing presence, not OCR, exhaustive temporal correctness or musical/creative acceptance. Incorrect glyph placement can cross regions and still needs inspection. This closes the observed ambiguity for this film without claiming every possible layout is separable.


## Real incoming motion during a dissolve

The prior dissolve recipe held the incoming first frame during its pre-roll. `transition_moving_dissolve` now decodes incoming source frames before the main excerpt, then uses the existing native Fusion opacity ramp. Source handles are mandatory; still/insufficient-handle/artificial-zoom cases reject before encoding. Main shot starts/cuts and soundtrack stay unchanged. Optional Resolve `moving_transitions: true` exposes the choice to visual planning; this controlled trial did not run a new headless planner. [Recipe/research/limits](TRANSITIONS.md).

The retained040manifest was copied with exactly one change: a0.4-second moving dissolve before the cave-interior shot. The real pre-roll covers nominalsource32.873167–33.273167seconds,12frames at30FPS. Its timeline span324–335ends immediately before the existingcut336; the main excerpt still begins atsource33.273167. Resolve exported13.5seconds/405frames and an editableDRP; the actual queue showed Completed 2 seconds(render only). Native QA passes50composition/transition samples,9title-timing samples and audio correlation.99992. Five independent original-source samples cover the handle’s first/middle/last frames and the main excerpt’s first two frames; minimumcorrelation.999839within nominalsource/output framequantum. This does not prove exact originalPTS continuity.

A decodable frozen-handle control differs from the moving last frame withMAE.05256/correlation.81243and fails the existing source thresholds. Replacing only the expected handle with that frozen proxy makes native visual QA reject the unchanged actual movie atframe332. The frozen proxy is a control, not an alternative native export. Source/native evaluation completed first; the added frozen helper was then called separately. Six rendered frames spanning324–336were inspected and show a coherent cave-entry/interior blend in this engineering judgment; no human preference or general smoothness ranking follows.84unit tests, compile/whitespace pass. The first new unit fixture omitted the binary mock; fixing that test setup exposed the intended handle gate without changing implementation.

Public evidence: `evals/results/moving-dissolve.json`. Reproduce source/native/control evaluation with `python3 -m evals.moving_dissolve MANIFEST.json JOB.json NATIVE.mp4 --output NEW_DIRECTORY`. It is scoped to one moving dissolve, fill framing and no artificial zoom. Slow original-source decoding was allowed to finish; no timeout restart or threshold relaxation was used. Actual media remain local. Musical fit, camera matching and creative acceptance remain unproven.


## Second reference: landscape, no titles, denser cuts

A second selected local reference showed full-frame travel imagery delivered sideways inside a portrait container, varied holds and a faster late sequence, without visible title cards/collages in extracted samples. The old planner always emitted portrait output and a title. Specs now explicitly choose canvas aspect and whether titles render; optional shot-count bounds constrain both the model schema and compiler. [Contract and source research](CANVAS.md).

Actual precursor 044 failed because the model supplied zero unused title duration for a disabled title; the compiler still tried to calculate a visible span. The regression was reproduced and fixed: disabled title timing is metadata, while a nonempty title sequence still rejects. Fresh 045 prepared six shots without titles but was not rendered; its sparse pacing motivated an authored 10–14 shot budget. These failed/prepared attempts remain local, not native successes.

Fresh 046 used Codex gpt-6.1-sol/low (60.656 seconds) and selected 12 excerpts from six original moving clips. No manual model-plan edits. Resolve 21.2 rendered 1920×1080,30 FPS, 14 seconds/420 frames with an editableDRP; the actual queue showed Completed 2 seconds(render only). `recreate-finish` passed 36 composition samples and full decode. All 11 cut coordinates have 0 frame offset against the measured audio-transient map; soundtrack correlation .99982/gain ratio .99968. No titles, panels or transitions were emitted.87 unit tests pass. `evals/results/landscape-canvas.json` contains sanitized evidence.

The rendered 1 FPS contact sheet was inspected: walking courtyard opening, fields/architecture/garden, then cave boats into a dark interior. Removing forced text/layout matches the observed full-frame direction better in this engineering judgment. Several people are partially cropped by portrait-to-landscape reframing, some source windows have motion blur, and the source pool repeats locations. The later cave holds do not reproduce every rapid reference cut. There is no matched camera choreography, speed ramp, flash/bloom or colour-grade implementation. The intentional upright landscape adaptation is not an exact orientation match. Audio transients are not verified beats, and no listening or human acceptance is claimed. Sparse frame inspection cannot establish smooth continuous pacing.


## Crop-aware source evidence and a bounded second-reference revision

The 046 film’s frame-cited model review took 23.868 seconds and proposed reducing adjacent cave-entrance repetition. Cited reference/candidate frames were inspected; the similar boat/rock compositions supported that specific diagnosis. Its pacing observation remains inferred. The planner previously received only uncropped source strips, so optional `canvas_previews: true` now adds a centre-fill crop row below each whole-source row. Times align by column; labels/hashes are retained. [Usage and official filter/scaling research](VIDEO.md).

Fresh run 049 received that review, the two-row previews and an authored brief reserving cave material mainly for the last three seconds. Codex gpt-6.1-sol/low planned in 65.062 seconds, with 18 strips/90 temporal source samples across six clips. It chose 12 excerpts without titles, panels, transitions or manual model-plan edits. Boat-source duration changed from 5.933 to 2.867 seconds; this measures the manifest, not musical feel or storytelling. Resolve Console initially failed to appear. After saving/reopening the app, a cuts-only Lua dispatch used the exact retained job counts/timing/music/project identity; no model choices changed. Native queue showed Completed in 2 seconds (render only), with 1920×1080/30 FPS/14 seconds/420 frames plus DRP. Full decode, 36 composition samples, all 11 cut coordinates and audio correlation .99982/gain .99968 pass. 89 unit tests, compilation and whitespace checks pass.

Rendered source strip/contact sheet inspected: the whole/cropped rows expose lost source content, and the film has more architectural/scenic material before the shorter cave ending. However, the park visitor remains badly cropped and source blur/repeated locations remain. Preview availability does not prove better framing decisions; this trial does not establish overall superiority. Both preview mode and revision instructions changed, so no causal claim is made about either alone. No matching grade, flash/bloom, camera choreography or listening verdict. Human creative preference remains unreviewed. Public measurements: `evals/results/canvas-previews.json`; all media/reviews/native artifacts stay local.

A follow-up model review took 28.454 seconds. Its sampled evidence could not establish 12 excerpts or late acceleration; the authoritative timeline does contain 12 shots, so that uncertainty is not treated as a missing-shot defect or used to trigger another identical revision. Its cited roof samples were inspected and are visibly soft; architectural legibility remains a supported weakness. No further improvement is credited from that review alone. More suitable source moments or footage are the next concrete need.
