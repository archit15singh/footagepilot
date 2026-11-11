# Active implementation scope — real end-to-end pipeline

User supersedes UI/branding work: implement functional code and real-footage runs first. No synthetic-demo or packaging work.

- Word-level local alignment, cuts and timestamp-based captions.
- Headless Codex story planning returning validated source-word edit ranges.
- MakeMyClip cleanup adapter with retained editable state.
- HyperFrames and Remotion exports using shared selected footage/captions.
- Music/SFX mixing with retained narration and levels verification.
- Automatically generate real-footage variations, retain actual outputs and intervention/timing/cost evidence, publish gallery and results to the public repository.
- At the end open the local HTML video gallery. User requests no additional final chat write-up.

Real source: public-domain White House weekly address, source provenance to be saved in evals. This is a natural human performance but already-produced footage; do not represent it as raw takes or a general editorial benchmark.

All listed functional stages ran on real archival footage and produced four committed gallery variations. Eleven regression tests pass. Codex planner, MakeMyClip, both renderers and mixing were live-tested. Codex is the sole supported planner. See docs/REAL-E2E-RESULTS.md and gallery/evidence.json for results and explicit limits.
