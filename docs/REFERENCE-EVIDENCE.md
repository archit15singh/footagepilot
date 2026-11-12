# Frame-cited reference planning

The reference analyser already extracts dense frames around scene-change candidates. The planner previously received only the overview contact sheet, leaving that evidence unused. It now receives the overview followed by a bounded set of timestamped reference frames, then the separate source-asset previews.

Six temporal targets across the reference select nearby change candidates; each supplies nearest before/at/after frames. Duplicates are removed and frames are sorted by time. At most eighteen frames are attached. Without change candidates the same targets sample the timeline directly. This is deterministic coverage, not a claim that the selected events are the most interesting or are real edit boundaries.

Each reference frame has a stable local ID, timestamp, kind and relative image path. Selected files must exist inside their analysis directory and are bound into the planner's input hashes. The plan retains the exact evidence mapping. Asset IDs and reference frame IDs are separate namespaces.

The structured response includes technique observations with frame citations, visible/inferred labels and adaptation reasoning. Planned shots and panels cite reference frame IDs, or use an empty list for original choices. Unknown citations are rejected. Camera motion, cuts, dissolves and mask reveals are always labelled inferred when derived from sparse frames. A title or collage can be described as visible, but the validator does not check whether that description is true.

These guards establish traceability and honest uncertainty, not reference fidelity. A model can cite a real frame and still misinterpret it. Review its cited images, adaptation reasoning and resulting output. A successful evidence gate cannot record human preference or promote a variation as creatively accepted.

## Reproduce and iterate

Run visual-plan or recreate with a completed reference analysis. Older saved plans remain inspectable; new live plans require frame-cited evidence. Run `python3 -m evals.reference_grounding PLAN.json --output NEW_RESULT.json` against an actual plan to check its ledger and reject fabricated citations/temporal overclaims.

Keep source reels, selected frames, private source assets and full plans local. Public findings may report counts, technique categories, observed failures and limitations. If analysis frames were moved or deleted, regenerate a completed reference analysis rather than claiming the evidence still exists.

The full still-photo run caught a preview regression introduced with video excerpt support: seeking to zero on a still image could exit successfully without creating a preview. Still previews now omit seeking; actual frame existence remains a gate. The failed run stays local, and the corrected real planner run is recorded separately. See resolve/RESULTS.md for current evidence.
