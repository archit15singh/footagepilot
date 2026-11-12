# Music cue timing without a listening claim

Verified12November2026. Existing BPM grids remain supported. Resolve can also plan cuts, title entries, black spans and progressive panels against source-bound, uneven timing coordinates.

```sh
python3 -m footagepilot music-cues music.wav --output projects/cues.json --max-duration 30 --min-gap .3
```

Copy the result's `music_timing` object into the local visual specification, keep `music` pointing to that exact source file, and select Resolve. Run `visual-plan` or `recreate --backend resolve` normally. The cue object contains zero, selected interior RMS novelty peaks and the analysed endpoint. `min-gap` applies between all selected points, including boundaries; close transients are deliberately omitted. The source music SHA256 binds the coordinates to the analysed recording. A different/replaced file fails before planning/native execution. `mode=reviewed_cues` also accepts explicit reviewed coordinates with source hash and provenance; changing the label alone is not evidence of review.

For cue specifications, legacy schema names `start_beat` and `beats` mean **cue index** and **number of cue intervals**. They do not mean musical beats. A shot starting at index2 and spanning3intervals runs from `cues[2]` to `cues[5]`. The model can choose longer holds across several candidates. Cue indices must be integers, all ranges must fit, and duration budgets still apply. Coordinates must start at zero, increase by at least.1seconds and cover the delivered timeline. Edits cue execution is rejected before opening its client; the live path here is Resolve.

Resolve receives actual rounded frame positions as timeline markers, explicitly labelled onset candidates when appropriate. Layer duration is the rounded absolute endpoint minus rounded start, preventing independent rounding from shifting exits or creating overlaps. Timing evidence reports cut/title offsets against these coordinates. It verifies coordinate correspondence, not whether those coordinates are true beats or whether the film feels musical.

The extractor uses decoded mono8kHz PCM and the existing10ms RMS energy-novelty detector. [FFmpeg's official CLI documentation](https://ffmpeg.org/ffmpeg.html) and [raw format documentation](https://ffmpeg.org/ffmpeg-formats.html) describe the conversion primitives; the novelty heuristic is FootagePilot code, not an FFmpeg or Blackmagic beat detector. Blackmagic's [Resolve20 feature guide](https://documents.blackmagicdesign.com/SupportNotes/DaVinci_Resolve_20_New_Features_Guide.pdf) documents Studio automatic music-beat detection. That is distinct from this tested free-edition workflow and does not establish availability in the installed AppStore build. Sources reviewed12November2026; recheck after app/tool changes.

## Limits

RMS transients may be speech, effects or loud attacks. Soft or sustained music may produce no usable cue map; silence is rejected. Early/late boundaries are editing bounds, not onsets. Novelty peaks can lag the musical attack and do not identify tempo, downbeats, song sections or emotional fit. Listen/review the candidate film before accepting musical quality. The planner must preserve these labels rather than claim it heard the recording. Reference analysis and supplied music are separate; coordinates from one track must not be copied onto another.

Run `python3 -m evals.music_cues --output NEW_DIRECTORY` for known uneven-pulse recovery, silence and different-track controls. This diagnostic measures transient extraction, not real-song beat-tracking accuracy. The actual native comparison and retained interventions are in [RESULTS.md](RESULTS.md).
