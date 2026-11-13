# Edits knowledge and operating guide

For the division of work between Resolve and Edits, including how to carry a master into a social cut, see the [editor workflow](../EDITOR-WORKFLOW.md).

Research date: 2026-11-12. Tested Mac build: 455.0.0.32.104. This guide can go stale: Edits changes frequently, catalogs vary, and mobile tutorials do not establish desktop parity. Start with `python3 -m footagepilot learn-check`; use `--fetch` to compare current official pages. A changed/unavailable source or stale date requires renewed research. Fetching a page never renews its human-reviewed verification date.

## Sources and feature map

The [official home page](https://edits.instagram.com/) links 14 tutorials; all were retrieved and reviewed for this inventory. [Desktop documentation](https://edits.instagram.com/desktop/) confirms Apple-silicon Mac support, free download, Instagram sign-in, multitrack timeline, keyframes, layered audio, colour controls, LUT/font import, captions and watermark-free 4K export. It describes a native app; no browser editor was verified.

| Official guide | Workflow and useful practice | Verification scope |
| --- | --- | --- |
| [Ideas](https://edits.instagram.com/tutorials/ideas/) | Revisit saved Instagram references and annotate the specific idea worth adapting. | Documentation; browser saved collections inspected separately |
| [Creative inspiration](https://edits.instagram.com/tutorials/creative-copilot/) | Inspect inspiration, audio and template suggestions; save notes on why a reference works. | Documentation; not a verified Mac MCP feature |
| [Storyboards](https://edits.instagram.com/tutorials/storyboards/) | Define sections and attach existing footage; identify missing shots before recording. | Documentation |
| [Templates](https://edits.instagram.com/tutorials/template/) | Choose an inspiration template, replace its media, then revise its timing/text/audio for the new story. | Documentation; template library availability on Mac not verified |
| [Camera](https://edits.instagram.com/tutorials/enhanced-camera/) | Select capture quality and frame rate deliberately; preview takes before continuing. | Mobile documentation, not a desktop camera test |
| [Teleprompter](https://edits.instagram.com/tutorials/teleprompter/) | Draft script, set scroll pace and text size, position it outside important framing. | Documentation; Mac tool advertised, not live-tested |
| [Keyframes](https://edits.instagram.com/tutorials/keyframes/) | Use motion to emphasise a focal detail; animate overlays when the story calls for it. | Native transform keyframes applied and exported |
| [Cinematic framing](https://edits.instagram.com/tutorials/cinematic-filters-crop/) | Choose a coherent look and intentional crop; subject separation can support selective blur. Avoid applying one look blindly to all exposures. | Fill/contain and transforms tested; subject cutout not tested |
| [Effects](https://edits.instagram.com/tutorials/effects/) | Select effects that direct attention to an object or person. | Catalog tools discovered; no claim every effect works |
| [Restyle](https://edits.instagram.com/tutorials/restyle/) | Optional generated alterations of short clips. Preserve original media and label generated content. | Documentation; tutorial says up to 10 seconds; recheck before use |
| [Audio tools](https://edits.instagram.com/tutorials/advanced-audio-editing-tools/) | Import music/voice/SFX, evaluate enhancement, fade at deliberate boundaries and audit the mix. | Local score imported, gain/fades set; listening quality unverified |
| [Captions](https://edits.instagram.com/tutorials/captions/) | Generate after editing, then correct text and style for readability. | Documentation and tool discovery |
| [Caption editor](https://edits.instagram.com/tutorials/caption-generator/) | Bulk-correct, split and merge captions; check timing against speech. | Documentation |
| [Text styling](https://edits.instagram.com/tutorials/text-styling/) | Control line spacing, outline and contrast; retain approved styles for reuse. | Fonts, size, colour, position and durations tested; wrapping failure caught and revised |

For ongoing changes, revisit the [official blog](https://edits.instagram.com/blog/) and [Meta's product introduction](https://about.fb.com/news/2025/04/introducing-edits-streamlined-video-creation-app/). Mobile features, regional availability and an advertised feature are not proof of a working Mac automation path. No claim that this inventory covers future/hidden features.

## Local setup, observed through computer use

1. Download from the official desktop page. Verify the Instagram developer signature/notarization; install and sign in. Do not use unrelated “Edits online/PC” download sites.
2. In Settings → Automation, enable the local server only with the user's approval. The inspected endpoint is `http://127.0.0.1:19501/mcp`. Treat the access token as a credential; never commit, screenshot, print or put it in a public issue.
3. Supply `FOOTAGEPILOT_EDITS_TOKEN` or a private `--token-file`. FootagePilot connects directly; it does not modify global Codex/Claude settings. Turn automation off when the user requests it.
4. Import the chosen asset folder through the native Media → Import picker. macOS security bookmarks matter: an MCP import by path can fail before this grant. Do not bypass the sandbox. Importing a directory makes its media available without granting unrelated home-folder access.
5. Native UI discovery: double-click a library thumbnail to open its source preview, then Add to timeline. Clicking an accessibility text label alone did not reliably open the source; the thumbnail did.
6. Audio selection exposes Beats with Off/Less/More density and manual markers. Clip selection exposes Transform/Keyframe/Crop, Sound, Speed curves, Opacity, Mask and Adjust. Inspect current state rather than assume old element IDs.
7. Export stays local. The native export button renders to Edits' export directory; Share to Instagram is a separate operation and is outside this workflow.

## MCP execution and known traps

[`capabilities.json`](capabilities.json) contains all 274 discovered tools and schemas, dated and versioned. Rediscover `tools/list` before assuming a tool or catalog item exists. Read-only, mutation and publishing operations are distinct; the product adapter uses a fixed set of editing calls and never publishes or deletes projects.

Tested: initialize/list, state/elements, fresh projects, title/canvas, media import, trim/move, fill/contain transforms, keyframes, four-panel composition via overlays, text styling, music/gain/fades, save and export. Also ran native `audioOnsets` and `detectShots` on a downloaded reel; results are candidates, not semantic truth.

Observed incompatibilities in this build:

- `addMedia` advertises `audioKind` as required, but visual imports require omitting it. Supplying it can insert the visual element and then report an error. Never blindly retry a mutating failed call: inspect state first.
- `setTransform.keyframes` accepts `reject`, `offsetAll` or `clear`, not a JSON array. Prefer explicit keyframe calls for motion.
- Export settings need a complete preset row: e.g. resolution `1080x1920`, resolutionType `HD`, aspectRatio `nineBySixteen`, quality `high`, codec `hevc`, frameRate `30`, dynamicRange `SDR`. The inspected exporter rejects H.264. Actual media still requires probing.
- Export to an arbitrary repo path failed with permission error. The adapter exports to the app's writable native folder (default `~/Movies/Edits/Exports`, configurable with `FOOTAGEPILOT_EDITS_EXPORT_DIR`) using a fresh unique filename, then copies locally and decodes it.
- Oversized title text wrapped across lines. A tool success response cannot replace rendered-frame review.

## Reference → recreation loop

Use computer use to browse the user's chosen saved collection; record selected reel URLs locally. Do not assume collection enumeration is a supported public API. `reference` downloads one reel through yt-dlp, or ingests a local browser download, and creates dense cut frames plus an audio-energy map. Use the local video to listen when available. FFmpeg energy peaks and Edits tempo/onsets help align cuts numerically; neither proves musical intent or emotional fit.

Create a manifest with a clear opening, varied holds/composition and an ending. `edits-render` always creates a new project and preserves existing ones. The adapter supports sequential visual shots from their beginning, photo/video overlays, limited title styles and a prepared music track. Trim desired source in-points into prepared assets first. It does not yet turn an arbitrary reference into an automatically excellent shot plan.

Review output frames at the start, every layout change and crop boundary. Decode/probe/hash output separately. Compare against the rejected baseline and ask for preference. Retain losing attempts, notes and input hashes. Change one creative factor per iteration. `compare-edits` defaults to unreviewed and cannot promote a result from technical checks alone.

Native transition support: manifests may supply `transitions: [{"after_shot": 8, "filter": "transition_dissolve", "duration": 0.2}]`. Use a current transition catalog ID and durations short enough for both neighbouring shots. This build's addTransition dryRun path failed with ArgumentParser.CommandError; direct application succeeded and the transition readback confirmed it. The adapter does not use the broken dry-run path.

For a known timing grid, add `music_timing: {"bpm": 120, "offset": 0, "provenance": "timing from the source score"}`. This inserts explicit native beat markers; it is not a claim that every transient is a beat. The live original score had a half-second authoring grid, and the revised shot boundaries were planned on that grid. Use listening or trusted annotations to establish phrasing. For an estimated BPM, retain the estimate and uncertainty in your plan instead of calling it verified.

Refresh the live automation inventory with `python3 -m footagepilot edits-tools --token-file /private/path/token --output projects/capabilities-new.json`. Compare that snapshot with the checked-in version before using untested tools. The current GUI remains the fallback for setup, sandbox imports and unsupported parameters.

## Visual planner and end-to-end command

`visual-plan` runs headless Codex `gpt-6.1-sol` at low reasoning with the reference contact sheet and a thumbnail of each identified asset. It receives scene/audio-candidate metadata and an explicit music grid, not an alleged listening experience. Its output contains observations, uncertainties, asset IDs, beat-count holds, reasons, cut/dissolve choices and optional simultaneous quadrant panels. Compilation rejects unknown assets, overlapping/incomplete collages and invalid durations before Edits mutates a project. Model output is never executable shell code.

```sh
python3 -m footagepilot visual-plan projects/visual-spec.json --output projects/new-plan
python3 -m footagepilot recreate projects/visual-spec.json --token-file /private/path/token --output projects/new-recreation
```

Use [visual-spec.json](../../examples/visual-spec.json) as a starting point. Paths resolve relative to the spec. `reference` points to an existing analysis.json; alternatively `reference_url` makes `recreate` download/analyse that reel first. Keep the track's tempo provenance honest: estimates need review, and fixed tempo cannot represent tempo changes. The current planner requires a zero-offset grid and 2–20 visual assets. It plans still-image grammar; selected clips can be supplied as prepared visual assets, but motion-aware source in/out selection is not implemented.

`recreate` writes a run ledger with freshness, optional download/analysis, visual planning and native-render stages. A failed stage remains failed; rerun into a fresh directory after correcting the cause. It never promotes creative preference automatically. This is a full one-run path, not a cache/resume engine.

To revisit a chosen private collection, add `saved_collection_url` to your local spec and run `python3 -m footagepilot inspiration-open projects/visual-spec.json`. It opens the collection in Brave; the agent then uses computer use to select references and records `reference_url` locally. Neither authentication nor saved collection membership is guessed or scraped automatically. No URLs from a user's saved list belong in public examples.
