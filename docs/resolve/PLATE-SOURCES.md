# Reviewed glass preset and repeatable source evidence

Reviewed 12 November 2026. Recheck the publisher and pinned download before changing this preset, and after the 30-day source-review gate expires. App capabilities keep their separate seven-day research check. Asset identity and renderer compatibility are different checks.

## Source and preparation

[OpenStudioMarburg at Philipps-Universität Marburg](https://www.uni-marburg.de/en/fb12/research-groups/grafikmultimedia/research/studio) publishes a real breaking-glass recording against black and explicitly releases that sequence under CC0. Its glass section links the [MP4 recording](https://www.mathematik.uni-marburg.de/~thormae/misc/breaking_glass_overlay_h264.mp4). Credit: OpenStudioMarburg, Philipps-Universität Marburg. This is the publisher's stated license, retained with the download; the source is not identified as the reference creator's exact asset.

```sh
python3 -m footagepilot fetch-plate marburg-glass --output projects/glass
```

The command accepts a reviewed preset ID, not an arbitrary download URL. It fetches bounded publisher evidence, checks the glass license section and a pinned 8,769,929-byte file hash, preserves `original.mp4`, probes and fully decodes it, then creates a separate derived overlay. Changes to the evidence, reviewed file, size, recipe output geometry/FPS/duration or source freshness reject with a retained failure record. Source review dates are not renewed automatically.

The current source is 1280×720 at25FPS,12.04seconds. The derived one-second asset crops a640×360 region atx480/y120, scales to1920×1080 at30FPS and fades in/out around the first fracture. This is upscaling of a bounded region, not new HD detail. Original bytes remain untouched. `provenance.json` records source/derived hashes, recipe, license-page fingerprint and output metadata. `plate-assets.json` can supply the existing visual planner's separate `plate_assets` list. Media and snapshots remain under the chosen local output directory.

## Automatic recreation

A Resolve recreation spec can instead include:

```json
{"plate_presets": ["marburg-glass"]}
```

`recreate SPEC.json --backend resolve --output projects/RUN` fetches the reviewed preset as a recorded stage, merges its asset into the separate plate catalog, and passes timestamped evidence to Codex. Unknown/duplicate preset IDs, duplicate manual catalog IDs, more than eight combined assets and unsupported backends reject. `visual-plan` accepts already fetched `plate_assets`; use `recreate` for automatic preset acquisition. The normal native Console/export/finish steps still apply. Read [Screen plate semantics and verification](PLATES.md).

The preset provides photographed crack/shard texture. Native Screen blending adds it over the source imagery; it does not refract/distort the trip footage underneath. The publisher describes additive compositing; FootagePilot uses its separately calibrated native Screen mode, so the blend is an adaptation. Brightness peaks and measured soundtrack transients provide numerical timing coordinates, not a claim to hear an impact or establish a true musical beat.

## Controlled comparison and framing lesson

`python3 -m evals.glass_plate BASE_JOB MEDIUM_JOB STRONG_JOB PROVENANCE.json --output projects/EVAL` checks an unchanged main edit and a pair differing only in glass opacity. It verifies both actual native movies/DRPs, all effect frames, selected source-range samples, soundtrack correspondence and a separately labelled no-glass control. Its range comparison is scoped to source frames6–23 of this derived preset at30FPS. The control is FFmpeg output used for rejection testing, never a native product export.

The automatic trial's planner claimed a retained traveler in its ending. An actual rendered frame showed mostly sky and bridge. The run was retained as a precursor, then bounded framing alternatives were inspected and a focus-only correction rendered and checked. Use [framing refinement](FRAMING.md) for such observed failures, preserving effects and timing. The framing command now rebases and fingerprints plate paths as well as footage/music when moving the manifest to a new directory. A model description of subject visibility remains a hypothesis until the actual rendered samples support it.
