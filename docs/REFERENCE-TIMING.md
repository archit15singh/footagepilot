# Inspect a reference frame by frame

```sh
python3 -m footagepilot reference path/to/reel.mp4 --output projects/reel-timing
```

The same command accepts an individual Instagram reel URL when yt-dlp can retrieve it. Use a local download for other sources. Open `index.html` from the output folder. Click a candidate to seek to it, then step through neighboring frames. Play the reference to hear whether a change lands on a musical accent, a vocal, an effect or silence. The video supplies every frame. The report also retains JPEGs for regular samples and the actual decoded neighbors of each change candidate.

`analysis.json` version 2 adds:

- `frame_timeline` with zero-based decoded ordinals, presentation timestamps in seconds, mean absolute frame difference and FFmpeg's scene-change score. Timestamps use the input timeline at microsecond precision and retain variable frame intervals.
- `transitions` with exact candidate frame indices and signed offsets to the closest measured onset and, when supported, to an estimated pulse. Positive values mean the visual change follows the audio marker.
- `audio.pulse` with a fixed-period estimate when repeated transients support one. It can remain inconclusive. The fit searches 67–200 BPM in 10 ms period increments. Tempo changes, sparse music and mixed audio can defeat the fit. A regular source effect can produce a pulse. Confirm beats and musical phrases by listening.

Existing sample, cut and audio fields remain available. `visual-plan` passes neighboring frame images and signed timing evidence for the cited changes to Codex, then keeps that evidence in `plan.json`. The planner uses the chosen output soundtrack's own timing when building the edit. See [frame citations](REFERENCE-EVIDENCE.md).

## Research and implementation

[FFmpeg's scene-change and audio-resampling filters](https://ffmpeg.org/ffmpeg-filters.html) give us decoded frame timestamps and audio aligned to the shared media timeline using dependencies the project already has. The existing scene detector still selects the abrupt-change candidates. Frame difference also surfaces motion and gradual changes for inspection. Camera movement, flashes and overlays can trigger a candidate. Classifying a dissolve, match cut or mask still requires inspecting the neighboring images and continuous playback.

[PySceneDetect's adaptive detector](https://www.scenedetect.com/docs/head/api/detectors.html) compares frame change against a rolling average to reduce false positives during sustained motion. [librosa's beat tracker](https://librosa.org/doc/main/api/generated/librosa.beat.beat_track.html) uses onset strength, tempo estimation and dynamic programming. Both are useful comparisons for more difficult references. The current implementation uses local FFmpeg, existing RMS onset detection and a conservative constant-period fit with no additional Python dependencies.

## Verified runs

- The six-second generated regression fixture has uneven video frame intervals and an audio stream delayed by 200 ms. FFmpeg 9.0 and ffprobe 4.4.1 yielded 129 frame timestamps, the three authored cuts at 1.200, 2.760 and 4.200 seconds, a 120 BPM pulse, and cut-to-pulse offsets of 0, +60 and 0 ms. The regression also verifies that JPEG pixels change on the expected frame.
- A 30.439-second Instagram-derived reference yielded 758 frames and 65 visual-change candidates. Three opening candidate intervals were about 1.5 seconds, followed by a sequence around 0.4 seconds. Twenty candidates fell within 50 ms of an onset. The frames show a shift from quiet scene-setting and details into varied angles of swimming, cycling and running. The shift offers a specific editing pattern to try with footage that covers the action. The constant pulse was inconclusive, so the onset count alone cannot establish beat sync.
- A second 14.372-second Instagram-derived reference yielded 424 frames and 15 candidates. Three candidates fell within 50 ms of an onset. The pulse fit was also inconclusive.
- A live Codex planning run on the generated fixture produced a five-second validated edit manifest. It retained all three signed offsets and cited the neighboring frames when proposing hard cuts. The assets were colored placeholders for the timing check.
- Brave 157.1.99.57 played the first reference from the local report. Selecting its first candidate and stepping backward and forward traversed the expected 1.200, 1.160 and 1.200 second frames. The automated browser check used a user gesture to enable playback.

Private sources, extracted frames and reports are retained locally. These runs validate timing evidence and inspection. Creative quality, semantic transition accuracy and musical intent require review.
