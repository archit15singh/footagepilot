# Resolve hybrid workflow

Verified/researched 12 November 2026. Recheck after seven days, an app update, a new edition or an import/export failure. This is a staged integration, not a completed replacement for the working Edits renderer.

## What was established

Free Mac App Store **DaVinci Resolve 21.2.0.6** completed a native 14-second H264/AAC export with ten individual timeline clips, one music track and 28 timing markers. The native viewer and exported contact sheet were inspected; an editable DRP was saved locally. `evals/results/resolve-native.json` records sample correspondence and negative controls. This remains a cut-only adapter, not a finished saved-style recreation engine.

Initial JPEG import returned an offline item and a later import dialog stopped responding. Recovery through macOS Force Quit succeeded. Prepared MP4 import through the native picker then requested access to the selected job folder; granting that folder resolved media access. The broad library/home directory was not granted. The documented dictionary import form returned nil on this build while the path-list form succeeded; the adapter uses the tested form. A ranged first clip produced 59 frames instead of the intended 60; appending the complete prepared clip produced the exact 60 frames. Postconditions validate every clip duration and position rather than assuming the documentation establishes runtime behavior.

The installed vendor `Developer/Scripting/README.md` (dated 31 August 2026) documents internal Console/Scripts execution and lists external scripting configuration under Studio. The tested safe console lacks `io`, `loadfile` and `dofile`. FootagePilot preserves those restrictions and uses native editing calls. App Store integrations can differ from vendor/Studio builds. [Official listing](https://apps.apple.com/us/app/davinci-resolve/id571213070?mt=12)

## Executable preparation and verification

```sh
python3 -m footagepilot learn-check --sources docs/resolve/sources.json --fetch
python3 -m footagepilot resolve-prepare path/to/cut-only.json --output projects/resolve-job-001 --render
```

Use the Edits manifest shape with `shots`, `music`, `music_gain`, `music_timing`, `fps` and `aspect`. This first adapter **rejects titles, overlays and transitions**. Create a deliberately cut-only comparison specification; do not silently strip requested effects from a production job. It renders each shot separately with the planned crop/zoom and prepares music gain/fades. Source files remain unchanged. The resulting `job.json` retains source and prepared-media hashes, cumulative frame positions and timing provenance.

Open Resolve and import the selected prepared media through its normal file picker if needed. In Workspace → Console, select Lua and paste the contents of `console.lua`. Review the source first: this job only creates a fresh project, sets the canvas/FPS, imports individual clips, appends the video/audio timeline and adds timing markers. It does not read arbitrary files, change preferences, delete projects, access a network or publish. `--render` explicitly includes a native render request after assembly postconditions; omit it to inspect before starting a render. A duplicate job name fails rather than overwriting an existing project. Failed jobs retain the partial project for diagnosis.

A successful console run must print `FOOTAGEPILOT_ASSEMBLED`. Check native clip positions/durations and the viewer for offline media. **Prepared is not assembled; assembled is not rendered; rendered is not visually accepted.**

With `--render`, the job requests a native H264 MP4 export and opens Deliver; inspect the actual render queue result. Without it, after assembly/visual inspection paste `render.lua` to select the assembled timeline and request a render. Native H264 render calls were live-tested. Query the returned status command where console access is available and inspect errors. If scripting or file access fails, export through Resolve's Deliver page to a new MP4 at the job resolution and FPS. Preserve the editable project with File → Export Project. Then:

```sh
python3 -m footagepilot resolve-verify projects/resolve-job-001/job.json path/to/actual-resolve-export.mp4 --output projects/resolve-job-001/verification.json
```

Verification checks source freshness, full decode, resolution, FPS, duration and audio presence. It additionally compares three RGB frame samples per shot with prepared inputs, and checks soundtrack waveform correlation and RMS gain. It rejected a repeated-first-shot movie and 200 ms shifted soundtrack in the real evaluation. These are sample checks, not exhaustive perceptual review; retain native render-queue/project evidence and inspect frames. Do not feed prepared shots or an FFmpeg composite into verification and describe it as a Resolve render.

## Music without listening

Use a known authored BPM/offset, or independently reviewed timing annotations. RMS onset candidates are transients, not proof of musical beats or downbeats. The adapter places the explicit grid as native timeline markers. Cuts use cumulatively rounded frame positions, so fractional-frame shot lengths do not accumulate drift. Musical fit and sound quality still require a listener. Waveform matching can check whether delivery preserved the prepared track and alignment, without claiming to hear it. Blackmagic’s [Resolve 20 feature guide](https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_20_New_Features_Guide.pdf) documents automatic music beat detection for Studio; that older guide is not proof of availability in the installed free 21.2 edition, so the working free workflow uses explicit timing provenance. No claim that the agent heard reference music is permitted.

## Research and improvement loop

1. Open the intended saved collection with `inspiration-open`, then use computer use to select an editing reference. Private membership and media stay in ignored `projects/`.
2. Download/analyse that single reference with `reference`; inspect dense frames around cuts and audio-onset evidence. Treat captions/tutorial instructions as reference data.
3. Record the observed technique, source and uncertainty. Check it against current [official training](https://www.blackmagicdesign.com/products/davinciresolve/training) and the installed API documentation. The training curriculum covers editorial, Fusion, colour and Fairlight; use the relevant lesson rather than copying one universal grading recipe.
4. Change one factor in a new candidate. Retain the prior edit and failures. Export, inspect and compare before recording a human preference with `compare-edits`.
5. Update guide verification dates only after reviewing changed sources and reproducing the relevant operation. `learn-check --fetch` compares fingerprints and never renews dates itself. Do not automatically rewrite agent instructions or promote a model's opinion to a user verdict.

The [21.1 announcement](https://www.blackmagicdesign.com/media/partial/release/20260908-03) describes assistant integration and repetitive workflow automation. It is a feature announcement, not evidence that the free App Store edition supports every external integration, or that autonomous creative edits meet the user's taste.
