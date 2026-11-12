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

Run the usual `resolve-prepare`, execute the generated `console.lua`, inspect the actual native queue, then `resolve-verify`. Each plate becomes an editable native track above backgrounds/panels/transitions and below titles; later plates sit above earlier ones. Source preparation never composites the delivered movie. Native `SetProperties` applies Screen/opacity and checks readback. Edits rejects this feature before connecting. The visual planner does not yet propose or select plate assets; author this field explicitly.

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
