# Reference review and bounded revisions

Technical export checks cannot decide whether an edit resembles a reference. `review-reference` compares timestamped reference/candidate images and records frame-cited model suggestions separately from human feedback.

```sh
python3 -m footagepilot review-reference SPEC.json ACTUAL-EXPORT.mp4 --output projects/review-001
# In a new local specification, add:
# "model_reviews": ["/absolute/path/projects/review-001/review.json"]
python3 -m footagepilot visual-plan NEW-SPEC.json --output projects/revised-plan-001
```

Candidate analysis is bounded to60seconds. The reviewer is Codex gpt-6.1-sol/low with a bounded JSON schema and no requested tool use. It receives up to18frames per film from six distributed before/at/after cut windows, with timestamps and separate evidence IDs. Findings cover layout, typography, source selection and inferred pacing. It may return no findings when evidence is insufficient. Each proposed change must cite both films, name uncertainty and use supported editing controls. The tool does not hear music or certify continuous motion, exact camera paths or aesthetic quality.

Original candidate, extracted frames, failure logs and output remain local. The report binds the reference analysis, candidate and sampled evidence with hashes. Changing candidate/reference/evidence makes a reused record fail before planner usage. Source-spec changes are allowed for the next iteration. `recreate` resolves model-review paths alongside human feedback paths. The visual planner receives suggestions labelled as unverified model notes; recorded human notes take precedence. Neither the tool nor the loader can turn a model record into human acceptance. Keep the previous native project/export and verify the new one independently. Different plans do not support a controlled creative ranking.

Frame-citation validation checks IDs and epistemic labels, not semantic truth. Inspect decisive cited frames before relying on a suggestion. Distributed sampling can miss important layouts or reveal states; expand evidence rather than confidently applying a diagnosis based on missing images. Do not create an endless revision cycle: stop when grounded changes are exhausted, or ask for human judgment on unresolved taste.

Blackmagic's [official training](https://www.blackmagicdesign.com/products/davinciresolve/training) includes refining rough cuts with trimming, match frame, shot replacement and audio/effects work. Reviewed12November2026. That supports learning the native editing operations; this model-review algorithm is FootagePilot implementation, not a vendor quality-assurance feature. Recheck official guides after app changes and retain actual native execution evidence.

For an opening-type finding, use [title-only refinement](TYPOGRAPHY-REVIEW.md) to preserve a verified film’s non-title edit. It compares actual exports with reference frames and retains both successful technical checks and visible failed attempts.
