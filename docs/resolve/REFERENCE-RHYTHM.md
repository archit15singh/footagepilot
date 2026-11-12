# Transfer a reference's change rhythm

Resolve recreation can use the reference's measured visual-change coordinates instead of planning around audio onsets:

```json
{
  "reference_rhythm": {"duration": 14, "min_gap": 0.15},
  "music_from_reference": true,
  "min_seconds": 14,
  "max_seconds": 14
}
```

Keep the existing reference and asset fields. This requires Resolve and unchanged analyzed reference media as the music source. It cannot be combined with `music_analysis` or `music_timing`. Duration must equal both duration-budget endpoints. If an explicit shot budget cannot accommodate the result, recreation fails rather than overriding it.

The extraction stage retains zero, candidate change times before the requested end, and the end boundary. Candidates too close to the preceding retained boundary or end are omitted and listed in the evidence. There must be 2–30 resulting intervals. The schema and compiler require exactly one shot per interval; the model chooses footage, source windows and composition, but cannot merge intervals to turn a rapid montage into long holds. Interior timing coordinates must remain supported by the hash-bound analysis; changed analysis/music or unsupported coordinates reject. Native cut positions use the existing cumulative decimal-to-frame rounding.

`reference_changes` is an explicit timing mode. Its marker label says visual-change candidates, not beats. Legacy planner fields named `beats` represent one timing interval here. The schedule is visual rhythm from the reference; it is not a tempo estimate, verified phrase map or automatic proof of musical fit. It works from time zero only and does not time-stretch media or align a different song.

The analyzer uses FFmpeg scene-score threshold candidates. The [official select documentation](https://ffmpeg.org/ffmpeg-filters.html#select_002c-aselect) describes a scene-change score; it does not establish semantic cut classification. Flashes, movement and gradual changes may cause extra or missing boundaries. Inspect before/at/after samples before relying on the rhythm. Research checked 12 November 2026; recheck after analyzer or FFmpeg changes.

Use `python3 -m evals.reference_rhythm ANALYSIS.json RHYTHM.json JOB.json NATIVE.mp4 --output NEW-DIRECTORY` for coordinate/frame-rounding checks, actual native correspondence, soundtrack correspondence and a wrong-shot control. Native queue completion and editable DRP inspection remain separate required evidence. Pacing transfer alone does not reproduce camera work, grade, performances, story or human taste.
