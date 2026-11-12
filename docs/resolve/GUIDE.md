# Resolve hybrid workflow

Verified/researched 12 November 2026. Recheck after seven days, an app update, a new edition or an import/export failure. This is a staged integration, not a completed replacement for the working Edits renderer.

## What was established

Free Mac App Store **DaVinci Resolve 21.2.0.6** completed a native 14-second H264/AAC export with ten individual timeline clips, one music track and 28 timing markers. The native viewer and exported contact sheet were inspected; an editable DRP was saved locally. `evals/results/resolve-native.json` records sample correspondence and negative controls. The current adapter also exports native editable TextPlus titles, four-panel collage tracks and Fusion opacity dissolves. See RESULTS.md for the full reference-to-Codex-to-Resolve run and its limits.

Initial JPEG import returned an offline item and a later import dialog stopped responding. Recovery through macOS Force Quit succeeded. Prepared MP4 import through the native picker then requested access to the selected job folder; granting that folder resolved media access. The broad library/home directory was not granted. The documented dictionary import form returned nil on this build while the path-list form succeeded; the adapter uses the tested form. A ranged first clip produced 59 frames instead of the intended 60; appending the complete prepared clip produced the exact 60 frames. Postconditions validate every clip duration and position rather than assuming the documentation establishes runtime behavior.

The installed vendor `Developer/Scripting/README.md` (dated 31 August 2026) documents internal Console/Scripts execution and lists external scripting configuration under Studio. The tested safe console lacks `io`, `loadfile` and `dofile`. FootagePilot preserves those restrictions and uses native editing calls. App Store integrations can differ from vendor/Studio builds. [Official listing](https://apps.apple.com/us/app/davinci-resolve/id571213070?mt=12)

## Executable preparation and verification

```sh
python3 -m footagepilot learn-check --sources docs/resolve/sources.json --fetch
python3 -m footagepilot resolve-prepare path/to/edit.json --output projects/resolve-job-001 --render
```

Use the shared Edits manifest shape. Full-frame shots use source-coordinate focal points and optional prepared zoom. Resolve panels now support non-overlapping rectangles with independent width/height and staggered timing, plus black layout spans and delayed title cards; see [progressive layouts](LAYOUTS.md). Legacy quadrant manifests remain supported. Titles support text, RGB colour, position, logical size, installed font and bold. Transitions support legacy dissolves, moving-source dissolves with real incoming handles, and left-to-right rectangle-mask reveals of at least two frames. See [native transitions and timing evidence](TRANSITIONS.md) for the tested recipe and limitations. Moving clips can use source_start seconds; see [source excerpts](VIDEO.md) for temporal planning, bounds and live evidence. Unsupported layouts and transforms fail explicitly. Source files remain unchanged; job.json retains source/prepared hashes and cumulative frame positions.

Preparation creates separate shot/panel proxies and blank title carriers. Legacy dissolves/wipes use frozen incoming-frame pre-roll; the explicit moving-source dissolve decodes real incoming pre-cut handles. Resolve constructs the actual layers: each panel gets its own native video track/transform; TextPlus connects directly to MediaOut for alpha; Fusion Merge opacity ramps from zero to one across the pre-roll. At the cut the incoming main clip starts normally. The legacy recipe is a frozen incoming preview; the moving-source variant overlays actual incoming handle frames over the outgoing shot. Crop/zoom and soundtrack gain/fades remain prepared outside Resolve; titles, collage placement and dissolve compositing are native. The title size conversion was calibrated against actual exports; missing fonts can change results.

Open Resolve and import the selected prepared media through its normal file picker if needed. In Workspace → Console, select Lua and paste the contents of `console.lua`. Review the source first: this job creates a fresh project, sets the canvas/FPS, imports clips, constructs the video/audio timeline and graphics, adds timing markers, saves and exports an editable DRP. It does not read arbitrary files, change preferences, delete projects, access a network or publish. `--render` explicitly includes a native render request after assembly postconditions; omit it to inspect before starting a render. A duplicate job name fails rather than overwriting an existing project. Failed jobs retain the partial project for diagnosis.

A successful console run must print `FOOTAGEPILOT_ASSEMBLED`. Check native clip positions/durations and the viewer for offline media. **Prepared is not assembled; assembled is not rendered; rendered is not visually accepted.**

With `--render`, the job requests a native H264 MP4 export and opens Deliver; inspect the actual render queue result. Without it, after assembly/visual inspection paste `render.lua` to select the assembled timeline and request a render. Native H264 render calls were live-tested. Query the returned status command where console access is available and inspect errors. If scripting or file access fails, export through Resolve's Deliver page to a new MP4 at the job resolution and FPS. The generated job exports resolve-project.drp automatically before requesting a render. File → Export Project is a manual fallback. Then:

```sh
python3 -m footagepilot resolve-verify projects/resolve-job-001/job.json path/to/actual-resolve-export.mp4 --output projects/resolve-job-001/verification.json
```

Verification checks source freshness, full decode, resolution, FPS, duration and audio presence. It additionally compares three RGB samples per shot, up to five samples per feature and individual collage quadrants against an independent single-frame expected compositor. That compositor is QA only; it never delivers a movie. Titles have a separate contrast/glyph-size check plus native text readback during construction. The gate is not OCR or an aesthetic judgment. Soundtrack waveform correlation and RMS gain check routing and timing. It rejected a repeated-first-shot movie and 200 ms shifted soundtrack in the real evaluation. These are sample checks, not exhaustive perceptual review; retain native render-queue/project evidence and inspect frames. Do not feed prepared shots or an FFmpeg composite into verification and describe it as a Resolve render.

## Music without listening

Use a known authored BPM/offset, independently reviewed timing annotations, or explicitly labelled source-bound [audio onset candidates](MUSIC-CUES.md). RMS onset candidates are transients, not proof of musical beats or downbeats. The adapter places the explicit grid as native timeline markers. Cuts use cumulatively rounded frame positions, so fractional-frame shot lengths do not accumulate drift. Musical fit and sound quality still require a listener. Waveform matching can check whether delivery preserved the prepared track and alignment, without claiming to hear it. Blackmagic’s [Resolve 20 feature guide](https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_20_New_Features_Guide.pdf) documents automatic music beat detection for Studio; that older guide is not proof of availability in the installed free 21.2 edition, so the working free workflow uses explicit timing provenance. No claim that the agent heard reference music is permitted.

## Research and improvement loop

1. Open the intended saved collection with `inspiration-open`, then use computer use to select an editing reference. Private membership and media stay in ignored `projects/`.
2. Download/analyse that single reference with `reference`; inspect dense frames around cuts and audio-onset evidence. Treat captions/tutorial instructions as reference data.
3. Record the observed technique, source and uncertainty. Check it against current [official training](https://www.blackmagicdesign.com/products/davinciresolve/training) and the installed API documentation. The training curriculum covers editorial, Fusion, colour and Fairlight; use the relevant lesson rather than copying one universal grading recipe.
4. Change one factor in a new candidate. Retain the prior edit and failures. Export, inspect and compare before recording a human preference with `compare-edits`.
5. Update guide verification dates only after reviewing changed sources and reproducing the relevant operation. `learn-check --fetch` compares fingerprints and never renews dates itself. Do not automatically rewrite agent instructions or promote a model's opinion to a user verdict.

The [21.1 announcement](https://www.blackmagicdesign.com/media/partial/release/20260908-03) describes assistant integration and repetitive workflow automation. It is a feature announcement, not evidence that the free App Store edition supports every external integration, or that autonomous creative edits meet the user's taste.

## Reference-to-native pipeline

```sh
python3 -m footagepilot recreate path/to/visual-spec.json --backend resolve --output projects/run-001
# Execute projects/run-001/resolve-job/console.lua through the native Lua console.
# Observe the actual Deliver queue completion, then:
python3 -m footagepilot recreate-finish projects/run-001 \
  --media projects/run-001/resolve-job/resolve-output.mp4 \
  --native-project projects/run-001/resolve-job/resolve-project.drp
```

The first command downloads/analyses the chosen reference, plans with Codex gpt-6.1-sol at low reasoning, validates the plan and prepares the native job. It returns passed=false / awaiting-native-render. The finish command requires an unchanged specification, a DRP archive matching the expected project identity and a verified media export before writing verified-export. Files alone do not authenticate native provenance; keep the separately observed queue/timeline evidence. User creative acceptance stays unreviewed.

For a new iteration, optional visual-spec.feedback lists local compare-edits JSON files. Only recorded human verdicts (better/worse/tie) with concise notes enter the planner; unreviewed comparisons are ignored. Review files are bound into the planner input hashes. Preserve prior outputs and ask the human to compare variations; model critique cannot become a human preference. Native scripts are generated as one console line because a leading Lua comment pasted into Fusion's single-line input can swallow a multiline program.
