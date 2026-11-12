# Title-only reference refinement

Use a verified Resolve recreation to adapt opening typography while keeping the selected footage, ranges, crop, effects, music and shot timing fixed:

```sh
python3 -m footagepilot refine-typography projects/verified-run \
  --words Small days big memories --output projects/type-review-001
python3 -m footagepilot resolve-prepare projects/type-review-001/edit.json \
  --output projects/type-job-001 --render
# Execute the generated Lua through Resolve and observe actual queue completion.
python3 -m footagepilot resolve-verify projects/type-job-001/job.json \
  projects/type-job-001/resolve-output.mp4 --output projects/type-job-001/verification.json
```

Supply 1–8 original words or short lines, each 1–28 printable characters. They remain in exactly that order, one per consecutive opening timing interval. This command currently requires explicit cue coordinates and a run with `verified-export`; it is not a general free-form title editor. Changing-word titles appear with hard cuts, not character animation, and the coordinates are not asserted to be musical beats.

The reviewer compares reference frames with actual exported candidate frames at the opening interval midpoints. It receives the old native title’s contrast/size measurements as empirical scale evidence. It chooses an allowed installed font, weight, white/dark colour, logical size from 8/12/16/20/24/28, and per-word y positions. Positions remain .15–.85; each event stays inside its one interval. The original supplied words cannot be invented, reordered, merged or replaced with creator wording. The compiler preserves all non-title manifest content, rebases media paths and validates the new titles. Inputs and attached images are fingerprinted before/after model review; stale verified movie, job, planning spec, source or prepared media reject before model usage.

The old title's entire phrase width is not a useful font-size target when the new title contains fewer letters. Compare character height relative to frame width. The measurements are contrast-change bounding boxes, not OCR or exact glyph metrics; compression, backgrounds and font case affect them. Inspect rendered words and reject an undersized or poor-contrast result even when technical checks pass. Native Text+ font/style/text/size readbacks are checked during construction, with separate contrast/size/timing checks on the export.

Evidence, model log, original wording and the revised edit stay local. The refinement record remains `creative_acceptance: unreviewed`. It does not overwrite the previous run, export, DRP or human feedback. Do not keep cycling through arbitrary font choices: use decisive frame evidence for a bounded correction, then ask for human taste when supported changes are exhausted.

`python3 -m evals.typography_refinement BEFORE.json AFTER.json OLD-JOB.json NEW-JOB.json NATIVE.mp4 PROJECT.drp --old-media OLD-NATIVE.mp4 --output NEW-DIRECTORY` checks title-only structure, unchanged shot timing, actual native correspondence, matching DRP and a visually discriminative old-title control. It does not prove exact reference typography, OCR accuracy, listening or a preferred edit. See [results](RESULTS.md) for the actual undersized attempt and corrected comparison.
