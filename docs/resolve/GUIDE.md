# Resolve hybrid workflow

Verified/researched 12 November 2026. Recheck after seven days, an app update, a new edition or an import/export failure. This is a staged integration, not a completed replacement for the working Edits renderer.

## What was established

The installed free Mac App Store edition reports **DaVinci Resolve 21.2.0.6** through its internal Lua console. `resolve:GetProjectManager():GetCurrentProject():GetName()` worked. An imported JPEG was returned by the API but showed **Media Offline**; therefore that import is a failure, not proof of access. A subsequent native Import Media dialog became unresponsive and computer-use calls timed out, including after reconnecting. The live comparison remains blocked at import; no Resolve export or quality ranking is claimed.

The installed vendor `Developer/Scripting/README.md` (dated 31 August 2026) documents internal Console/Scripts execution and lists external scripting configuration under Studio. It recommends keeping automatic scripted actions on the safe setting. In the tested console, `io` and `loadfile` are unavailable and `dofile` fails. FootagePilot does not disable this setting or install an external bridge. App Store builds have additional integration limitations; verify the exact installed build instead of assuming Studio or vendor-download behavior. [Official listing](https://apps.apple.com/us/app/davinci-resolve/id571213070?mt=12)

## Executable preparation and verification

```sh
python3 -m footagepilot learn-check --sources docs/resolve/sources.json --fetch
python3 -m footagepilot resolve-prepare path/to/cut-only.json --output projects/resolve-job-001
```

Use the Edits manifest shape with `shots`, `music`, `music_gain`, `music_timing`, `fps` and `aspect`. This first adapter **rejects titles, overlays and transitions**. Create a deliberately cut-only comparison specification; do not silently strip requested effects from a production job. It renders each shot separately with the planned crop/zoom and prepares music gain/fades. Source files remain unchanged. The resulting `job.json` retains source and prepared-media hashes, cumulative frame positions and timing provenance.

Open Resolve and import the selected prepared media through its normal file picker if needed. In Workspace → Console, select Lua and paste the contents of `console.lua`. Review the source first: this job only creates a fresh project, sets the canvas/FPS, imports individual clips, appends the video/audio timeline and adds timing markers. It does not read arbitrary files, change preferences, delete projects, access a network, publish or start a render. A duplicate job name fails rather than overwriting an existing project. Failed jobs retain the partial project for diagnosis.

A successful console run must print `FOOTAGEPILOT_ASSEMBLED`. Check native clip positions/durations and the viewer for offline media. **Prepared is not assembled; assembled is not rendered; rendered is not visually accepted.**

After successful assembly and visual inspection, paste the generated `render.lua` to request a native H264 MP4 render into the job directory. This render script is not live-verified yet. It checks the active project and returns the actual job ID; query the returned status command and inspect any error. If scripting or file access fails, export through Resolve's Deliver page to a new MP4 at the job resolution and FPS. Preserve the editable project with File → Export Project. Then:

```sh
python3 -m footagepilot resolve-verify projects/resolve-job-001/job.json path/to/actual-resolve-export.mp4 --output projects/resolve-job-001/verification.json
```

Verification checks source freshness, full decode, resolution, FPS, duration and audio presence. It cannot establish native provenance from an MP4 or detect every offline-media slate; retain console evidence and inspect frames. Do not feed prepared shots or an FFmpeg composite into verification and describe it as a Resolve render.

## Music without listening

Use a known authored BPM/offset, or independently reviewed timing annotations. RMS onset candidates are transients, not proof of musical beats or downbeats. The adapter places the explicit grid as native timeline markers. Cuts use cumulatively rounded frame positions, so fractional-frame shot lengths do not accumulate drift. Musical fit, phase and sound quality still require a listener. No claim that the agent heard reference music is permitted.

## Research and improvement loop

1. Open the intended saved collection with `inspiration-open`, then use computer use to select an editing reference. Private membership and media stay in ignored `projects/`.
2. Download/analyse that single reference with `reference`; inspect dense frames around cuts and audio-onset evidence. Treat captions/tutorial instructions as reference data.
3. Record the observed technique, source and uncertainty. Check it against current [official training](https://www.blackmagicdesign.com/products/davinciresolve/training) and the installed API documentation. The training curriculum covers editorial, Fusion, colour and Fairlight; use the relevant lesson rather than copying one universal grading recipe.
4. Change one factor in a new candidate. Retain the prior edit and failures. Export, inspect and compare before recording a human preference with `compare-edits`.
5. Update guide verification dates only after reviewing changed sources and reproducing the relevant operation. `learn-check --fetch` compares fingerprints and never renews dates itself. Do not automatically rewrite agent instructions or promote a model's opinion to a user verdict.

The [21.1 announcement](https://www.blackmagicdesign.com/media/partial/release/20260908-03) describes assistant integration and repetitive workflow automation. It is a feature announcement, not evidence that the free App Store edition supports every external integration, or that autonomous creative edits meet the user's taste.
