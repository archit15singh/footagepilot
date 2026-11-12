# Native Screen motion plates

Verified 12 November 2026 on free Mac App Store Resolve 21.2.0.6. Recalibrate after app updates. The current native script rejects plates outside version 21.2 rather than assuming the numeric enum still maps to Screen.

A dense local reference interval showed a glass-like shard/light texture across a cut. It was not adequately described by a white flash. That observation motivated reusable moving-plate support; it does not identify the creator's plugin, asset or exact compositing recipe.

## Manifest

Add `plates` to a Resolve edit manifest:

```json
{
  "plates": [{
    "path": "original-light-overlay.mp4",
    "start": 2.8666666667,
    "duration": 0.4,
    "source_start": 0,
    "blend": "screen",
    "opacity": 0.75
  }]
}
```

This fragment supplements required main `shots`. Use a legally available black-backed visual plate. Screen leaves black transparent in the ideal RGB model and brightens underlying imagery. This is not alpha-channel preservation. At most sixteen plates are supported, with finite opacity 0–1 and ranges inside the timeline. Fields are deliberately limited to the example; unsupported transforms/modes reject. Source media remain unchanged. Plates fill the canvas through preparation, so supply matching aspect to avoid cropping. `source_start` selects an excerpt; still images cannot use a nonzero source start.

Run the usual `resolve-prepare`, execute the generated `console.lua`, inspect the actual native queue, then `resolve-verify`. Each plate becomes an editable native track above backgrounds/panels/transitions and below titles; later plates sit above earlier ones. Source preparation never composites the delivered movie. Native `SetProperties` applies Screen/opacity and checks readback. Edits rejects this feature before connecting. Direct manifests may author this field explicitly; the optional reference-conditioned catalog below enables planner selection.

## Runtime and source evidence

The installed vendor `Developer/Scripting/README.md` documents `TimelineItem:GetProperties` / `SetProperties`, numeric enum readback and validating all supplied property values before applying them. In an isolated native project, the default read `CompositeEnabled=true`, `CompositeMode=0`, `Opacity=100`. Setting `CompositeMode=5` returned true/readback5, and the selected clip's native Inspector displayed **Screen**. Native job readback additionally validates enabled state and fractional opacity. The enum is runtime-calibrated, not inferred from menu ordering.

Blackmagic's [Editor's Guide](https://documents.blackmagicdesign.com/UserManuals/DaVinci-Resolve-17-Editors-Guide.pdf) explains Edit composite modes; the [Fusion tool reference](https://documents.blackmagicdesign.com/UserManuals/Fusion9_Tool_Reference.pdf) documents Screen in Merge. Those older primary sources explain the technique, not compatibility with every current edition. Installed current FusionToolReference.md also documents `Merge.ApplyMode="Screen"`; this implementation uses the tested Edit composite control instead of Fusion Merge.

## Reproducible checks

```sh
python3 -m evals.screen_plates make-plate projects/plate.mp4
# Add the plate to a real edit; prepare and execute native Resolve export.
python3 -m evals.screen_plates evaluate JOB.json NATIVE.mp4 PROJECT.drp --output projects/plate-eval
```

The generator creates original diagonal moving light bands on black with a sine intensity envelope. It is a calibration fixture, not glass-shatter simulation, reference extraction or an aesthetic preset. QA computes Screen independently (`base + opacity × plate × (1-base)`), compares all twelve effect frames in this trial, checks decode/geometry/audio, and rejects missing-plate and Normal-blend expected-image controls. Neither control is an alternative native render. RGB sampling, codec/range conversion and colour management introduce differences; retained thresholds are MAE≤.08 and correlation≥.90. This does not validate HDR/linear-light workflows, arbitrary grades, every mode, exact reference reconstruction, music fit or human taste.

## Reference-conditioned plate planning

A Resolve visual spec may supply a separate `plate_assets` catalog (up to eight moving clips). These are user-provided, legally available black-backed assets; FootagePilot does not download stock assets automatically or infer a license. Catalog entries use `id`, `path`, optional `note` and optional `preview_windows`, as with source footage:

```json
{
  "plate_assets": [
    {"id": "soft-light", "path": "effects/soft-light.mp4", "note": "Original soft light streak; no refraction"}
  ]
}
```

Both `visual-plan` and the full `recreate --backend resolve` path normalize and hash these files, produce retained timestamped source strips and attach them after main-source evidence to Codex. Effect IDs are separate from shot IDs in the output schema. The planner may return `plates=[]`; effects are not mandatory. It must cite known reference evidence or acknowledge an authored adaptation. `motion_plate` is always an inferred temporal interpretation, never proof of an exact creator asset or plugin.

A chosen event contains an asset ID, a zero-based outgoing `after_shot` index, integer `pre_frames` and `post_frames` (each1–30, at least three total), `source_start` seconds, opacity greater than0 and at most1, reference IDs and reasoning. The compiler places it around the actual cumulatively rounded30FPS cut, preserves the main timeline/music, verifies source and timeline bounds, and permits at most four events at unique cut boundaries. These frame counts are not musical beats or onset indices. Invalid choices fail before native preparation; there is no invented fallback effect or silent filename acceptance. No catalog leaves the previous planner schema unchanged.

For an original softer engineering asset, `python3 -m evals.screen_plates make-glare projects/glare.mp4` creates a one-second moving soft light streak on black. Screen blending can brighten underlying imagery; it cannot distort/refract it. This asset is an adaptation candidate, not a reconstruction of a glass transition. Layer quality depends on supplied artwork and source content; the planner does not establish creative acceptance.


### Subtle plate verification

Whole-frame similarity can overlook a low-opacity layer. The native verifier now adds `plate_checks` at quarter/middle/three-quarter effect samples. It independently composites the expected image with and without each plate, excludes title bands and selects channels with an expected increase greater than.02. At least64 distinguishable channels in one sampled frame are required. Regional MAE must stay below half the expected contribution, bounded to.015–.08, and correlation must be at least.90. This relative check is calibrated on the retained strong and subtle exports, not a universal perceptual metric. Weak, hidden, black or effectively disabled plates can return insufficient evidence rather than an asserted verification. Very brief peaks outside the three samples and other colour workflows remain limitations.

The actual subtle trial is reproduced with `python3 -m evals.planned_plates RUN_DIRECTORY --output projects/NEW_EVALUATION`. It rechecks the native export and builds a separately labelled **FFmpeg no-plate control**, concatenating the exact main-shot proxies with square SAR. That control is never delivered or credited as native Resolve output. The original control construction failed on differing proxy SARs; the helper now explicitly normalizes SAR for control construction. The failed attempt remains local.

For a reviewed real photographed-glass recording and automatic preset acquisition, read [plate sources](PLATE-SOURCES.md). Source/licensing evidence, crop/upscale/fade recipe and current comparison results are separate from the Screen blend contract.
