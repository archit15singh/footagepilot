# Progressive native layouts

Researched and live-tested 12 November 2026 on free Mac App Store Resolve 21.2.0.6. Recheck after app/API changes and use the existing official-source freshness gate.

## Why this changed

Frame-cited reference inspection showed three top-row tiles arriving progressively, with later partial/asymmetric rows over black. The previous compiler forced all four quadrants to appear together. That restriction imposed a different layout even when the model understood the reference.

Resolve plans now support up to 36 non-overlapping rectangular panels with normalized center x/y and independent width/height (0.1–1). A panel can arrive before the rest of its row, leave gaps, or occupy an asymmetric arrangement. Bounds and temporal overlap are checked before rendering and again after conversion to frames. At most 24 black layout spans cover the underlying main footage when a title card or incomplete collage requires empty space. Edits keeps the tested quadrant contract and rejects these Resolve-specific fields before native mutation.

Native manifests use overlays with start/duration in seconds, width/height in canvas fractions, and optional layout_backgrounds with start/duration and black colour. The headless Resolve schema accepts width/height per panel, black background beat spans, title_start_beat/title_beats, title_y and title_color. The title can therefore occupy a delayed black card rather than always overlaying the opening photo. Existing manifests with scale=0.5 remain supported.

## Crop and native geometry

Each panel source is reframed to its requested box aspect, then normalized into a full-canvas proxy. The proxy can look stretched when opened alone; independent native X/Y scaling restores the intended final proportions. Cropping/source processing is prepared per clip, while the delivered layout is assembled from separately editable native tracks. Backgrounds are separate native clips, not a baked collage movie.

Blackmagic's [Editor’s Guide](https://documents.blackmagicdesign.com/UserManuals/DaVinci-Resolve-17-Editors-Guide.pdf) describes unlinking Zoom X/Y for independent transforms. Exact scripting properties were checked against the installed API and actual runtime. The first native attempt caught an axis-link problem: requesting 0.31 × 0.30 produced 0.31 × 0.31 with ZoomGang=true. Both GetProperties and the deprecated GetProperty returned the same values; the getter was not broken. Setting ZoomGang=false before applying the transform produced the requested independent scales. The adapter keeps the readback assertion and the separate rendered-image checks.

## Real run and failure controls

The first live plan selected progressive tiles but exposed a separate compiler limitation: title timing was fixed to zero, while its black card followed the opening hook. Explicit title timing was added before execution. A fresh Codex gpt-6.1-sol / low call (56.424 seconds) then generated the final 14-second plan from timestamped reference frames and the private photo pool:

- Opening full-frame image, then gold original title centered on black at 2–4 seconds.
- Full-frame travel photos followed by a black collage stage at 9–13 seconds.
- Seven unequal-axis panels arriving at half-second intervals, retaining incomplete rows and empty black space.
- A final full-frame sea image. The supplied authored score is preserved; reference music was not interpreted by listening.

After the axis-link correction, actual native Deliver showed Completed in two seconds (render time only). The editable DRP was exported. All 55 composition/panel samples, title contrast/size and soundtrack checks pass without relaxed thresholds; minimum visual correlation is 0.94401. The retained earlier quadrant export also passes the revised verifier. A fully decodable control erasing the final panel, with timing/audio retained, is rejected by the individual panel check.

```sh
python3 -m evals.progressive_layout JOB.json NATIVE.mp4 VERIFICATION.json --work NEW_DIR
```

The control uses FFmpeg only to make a bad test movie; it is never credited as native output. Private native files, plan, probe projects and contact sheets remain local. Sanitized evidence is in evals/results/progressive-layout.json. Fifty-nine unit tests and compilation pass.

## Qualitative findings

The output now reproduces the reference's visible progression and empty-space layout more closely than the previous simultaneous four-quadrant adaptation. The title is also a delayed black card rather than an opening overlay. These are inspected structural differences, not a human quality ranking.

Typography still differs from the reference's ornate serif, source photos do not reproduce camera movement, and the authored soundtrack/grid is not the reference song. Panel crops, timing density and story still need taste review. Native geometry and missing-layer rejection do not establish creative acceptance. Keep the previous variations for comparison and record user feedback separately from model observations.
