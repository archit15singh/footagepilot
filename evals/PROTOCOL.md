# Product evaluation protocol

Evaluate SpliceForge itself. Benchmark inputs may be reused, but all outputs must be rendered by the product. Keep run data under ignored projects/, publish sanitized checks and selected original demo frames.

## Cases and criteria

1. Narrated demo with a deliberately rejected take: import, local ASR, deselect the take, retain intended narration, apply captions and three timed image cards, render. Check full decode, duration, streams, transcript coverage, and sample every cut/card. Record approximations in ASR timing; listen if audio is available.
2. Brand revision: change brand/color through workbench, rerender. Check intended visual changes, identical selected ranges and decoded audio content (allow codec changes only if documented).
3. Robustness: reject missing source, reversed/overlapping/out-of-bounds ranges, invalid brand, missing card image, card outside duration, all segments deselected. A failed job must expose an error and permit a corrected retry.
4. Caption stress: long text, narrow screens, long unbroken words. Check text fit and reading duration; never call a technically successful render a readable one without inspection.
5. Browser journey: import, ASR, toggle selection, apply, edit design, render, play/pause and seek. Verify busy state and stale export invalidation. Check narrow layout.
6. Reproduction: fresh dependency tree with npm ci, CLI help, unittest suite, documented environment setup. No absolute developer-machine paths in tracked configuration.

## Reporting

Report actual timings and versions, machine context, interventions and defects. Score qualitatively with concrete examples across speech cleanup, captions, visual control, revision effort, setup, reliability and autonomy. Explicitly distinguish machine checks, visual inspection and listening. Synthetic narration is useful for regressions but insufficient to establish real talking-head editorial quality or autonomous storytelling.

Do not mark the product complete until every required case has evidence or a clearly resolved implementation limitation accepted by the task scope. An optional renderer is not a prerequisite for the default renderer's release, but do not advertise unimplemented adapters.
