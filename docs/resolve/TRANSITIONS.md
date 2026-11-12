# Native transitions and timing evidence

Researched and live-tested 12 November 2026 on free Mac App Store Resolve 21.2.0.6. Recheck the installed Fusion reference and actual exports after an app update or failure. This extends the existing seven-day official-source review gate; it does not automatically refresh source verification dates.

## Primary-source basis

Blackmagic's [Fusion 18.6 reference](https://documents.blackmagicdesign.com/UserManuals/Fusion18_Manual.pdf) documents Merge's effect-mask input as a way to restrict its compositing region. Direct web retrieval exceeded the tool's PDF size limit; indexed primary-source text was available. Exact implementation details were checked against the installed vendor `Developer/Fusion/FusionToolReference.md`, updated 4 October 2026: Common Controls → Effect masks, Connecting tools, and Rectangle Mask. The installed guide describes width/center animation for a rectangle reveal and specifies the mask output ID `Mask`. The current runtime test, rather than the older online manual, establishes compatibility with this free app build.

The inspected Instagram selective-colour masking example in IDEAS.md motivated researching spatial masks. A left-to-right reveal is an engineering adaptation of the mask technique; it is not a claim that the creator used this transition or that it recreates camera motion.

## Executable recipe

A shared visual manifest can request:

```json
{"transitions":[{"after_shot":8,"filter":"transition_wipe_left","duration":0.4}]}
```

The boundary must exist and the effect must fit the adjacent shots. `wipe_left` means the incoming image is revealed **from left to right**. Existing `transition_dissolve` remains supported. Preparation makes a frozen incoming first-frame pre-roll; actual spatial masking happens in native Fusion, not FFmpeg. A rectangle grows across the frame with its left edge fixed, connected through `Mask` to a transparent-background Merge's `EffectMask`. The job asserts that connection exists before rendering. Each effect is a separately editable native track/comp.

`recreate --backend resolve` supplies Resolve capabilities to the visual planner. The schema and compiler permit `wipe_left` only for Resolve; Edits planning keeps cut/dissolve choices. A direct `visual-plan` spec can set `native_backend` to `resolve`. The prompt permits a reveal only when motivated by an explicit brief or observed visual grammar. It cannot establish that a model's interpretation matches the reference. The first shot must use a cut because there is no outgoing shot.

## Frame-domain music alignment

Resolve jobs carry a timing grid with explicit provenance. Verification now reports each cut's nearest grid marker and signed frame offset, plus each transition's start, last effect frame and following cut. An off-grid cut is reported honestly rather than silently snapped. Without a grid, offsets remain unknown. This does not identify reference music, find downbeats, or substitute for listening.

In the real 14-second trial the ending reveal spans frames 348–359; the next main clip starts at 360 (12 seconds), exactly on the supplied authored 120 BPM grid. Thus the effect reaches full coverage on the frame immediately before the beat-aligned cut. It does not imply the reference song has the same grid or that this is the best musical choice.

## Actual evaluation

The retained Codex plan and source pool were reused; only the ending transition recipe changed from a five-frame dissolve to a twelve-frame spatial reveal. Native Deliver showed Completed, and the editable DRP was exported. Five extracted frames show the reveal progressing from the night scene to the sea from left to right. All 43 composition/quadrant samples pass; minimum correlation is 0.98750. The slight boundary mismatch is consistent with downsampled mask edges; that explanation is an inference from the frame samples. Audio waveform correlation remains 0.99958, RMS ratio 0.99986.

Two controls were rejected at frame 351: interpreting the actual reveal as a global dissolve, and testing the earlier native dissolve movie against the reveal plan. These establish discrimination on this material, not universal transition classification. Reproduce locally:

```sh
python3 -m evals.resolve_reveal JOB.json NATIVE_REVEAL.mp4 \
  --baseline EARLIER_NATIVE_DISSOLVE.mp4 --work NEW_DIRECTORY
```

Sanitized results are in [resolve-reveal.json](../../evals/results/resolve-reveal.json). Private frames, native project and four-video review stay local. The planner capability has contract tests; this controlled variant reused an earlier live plan and does not claim a fresh LLM chose the reveal.

Qualitatively, the mask is spatially correct and a clear scene boundary, but the hard vertical edge is conspicuous on still photos. Prefer it selectively, not at every cut. Creative preference and music fit remain unreviewed. Motion matching, subject tracking and local colour masks remain separate experiments requiring suitable source material and their own evidence.


## Moving-source dissolve

A Resolve manifest can opt into a real incoming handle:

```json
{"transitions":[{"after_shot":5,"filter":"transition_moving_dissolve","duration":0.4}]}
```

This keeps every main shot/cut and the soundtrack unchanged. The incoming source must be video, have no artificial zoom, and supply at least the **frame-rounded** transition duration before its `source_start`. Preparation decodes those earlier source frames into a moving pre-roll proxy with the same framing as the main excerpt. Resolve fades that proxy over the outgoing native shot with the existing Fusion Merge opacity ramp; the proxy’s nominal endpoint meets the main excerpt’s unchanged source start. No footage is fabricated to fill missing handles. Stills, insufficient handles and artificial-zoom incoming clips reject before encoding. Edits execution rejects this filter before opening its client.

For Codex visual planning, set `moving_transitions: true` with `native_backend: resolve` (or use `recreate --backend resolve`). The opt-in adds `moving_dissolve` to allowed `transition_in` values. The prompt requires incoming video/zoom0/at least0.2seconds of source handle for its short planned transitions. Unsupported choices still fail native preparation; model suggestions are not automatic proof of useful motion. Legacy dissolve/wipe behavior remains explicitly frozen pre-roll.

This is a moving-source opacity-layer recipe, not a call to Resolve’s built-in transition preset API. Blackmagic’s [Fusion18.6 reference](https://documents.blackmagicdesign.com/UserManuals/Fusion18_Manual.pdf) describes Fusion transitions with outgoing/incoming MediaIn nodes and mixing; it supports the compositing principle, not this adapter’s exact recipe. Sources checked12November2026; reproduce on the installed app after updates. Source excerpts here may be variable frame rate, so nominal source-time agreement within the original/output frame quantum does not establish exact source PTS identity or universally smooth camera continuity. Do not describe the effect as a matched-camera transition or a listening verdict.
