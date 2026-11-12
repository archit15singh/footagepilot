# Resolve integration evidence

12 November 2026. Same private album assets, ten-shot selection, 14-second target and authored 120 BPM score used for the matched Edits cut-only trial. Media, operation details and DRP remain local.

| Stage | Observed result |
| --- | --- |
| Native application | Free Mac App Store DaVinci Resolve 21.2.0.6 |
| Initial failure | JPEG import returned Media Offline; native picker became unresponsive |
| Recovery | macOS Force Quit/relaunch; import prepared MP4 through picker; grant only the job folder |
| API correction | Dictionary import returned nil; path-list import succeeded. Full prepared-clip append preserved exact duration |
| Timeline | Ten separately editable video clips, one audio clip, 28 native timing markers; 420 frames |
| Native render | Deliver queue showed Completed in 00:00:02; this is native render time only, not end-to-end time |
| Export | 14.0 seconds, 1080×1920, 30 FPS, H264 video and audio; full decode passed |
| Editable artifact | Native DRP exported locally; project also saved in Resolve |
| Visual correspondence | 30 samples across all shots; minimum correlation 0.99957, maximum normalized mean absolute error 0.01179 |
| Audio correspondence | Correlation 0.99958; RMS ratio 0.99986 versus prepared track; no listening assessment |
| Negative controls | Repeated first shot rejected for wrong visual content; 200 ms delayed music rejected for waveform mismatch |
| Tests | 41 passing unit tests, compile/diff checks; known-cut/onset and silence diagnostic also passes |

Reproduce preparation checks with `evals/resolve_preparation.py`; test an actual native export and its negative controls with `evals/resolve_native.py`. Sanitized results are in `evals/results/resolve-native.json`. An MP4 does not establish native provenance alone: the native timeline, queue completion and DRP were separately observed.

## Qualitative comparison

| Dimension | Edits | Resolve hybrid |
| --- | --- | --- |
| Current implemented readiness | Higher: verified native photos, titles, collage, keyframes and dissolve | Cut-only first version, now native export verified |
| Matched cut-only output | 14.0-second native export | 14.0-second native export |
| Editable representation | Native elements and project | Individual native clips, audio and timeline markers; DRP |
| Animation in this trial | Native Edits transforms | Crop/zoom baked into separate prepared clips |
| Automation friction observed | Local MCP executes the native workflow directly | GUI bootstrap/folder grant/console required; recovery and API mismatches added substantial setup effort |
| Creative quality | Awaiting user review | Awaiting user review; no superiority claim |

For implemented readiness on this task: **Edits first, Resolve second**. This is an engineering judgment about shipped scope and interventions, not a scored creative benchmark or a ranking of the editors’ professional capabilities. No comparable end-to-end timing was retained, so the two-second Resolve queue result cannot support a speed ranking.

The earlier fully styled Edits variation has titles/collage/transitions; the matched cut-only variation deliberately omits them on both sides. Do not describe the styled variation and Resolve v1 as equivalent. The full requested Resolve rebuild still needs native titles/layers/transitions, planner routing, and recreation/quality iteration against saved references. The rejected slideshow feedback remains valid; a successful native roundtrip does not resolve taste.

## Research-driven correction

The public masking reference downloaded successfully (13.211 seconds, 1272×720). Its initial analysis failed on limited-range JPEG encoding, then on a sample after the last decodable video frame. Full-range JPEG conversion and video-end clamping fixed both. The corrected run produced 15 frames, three visual-change candidates and 48 RMS-onset candidates; the contact sheet shows local grading masks. Those onsets are not musical beat labels. Retained sanitized reference evidence is in `evals/results/resolve-reference.json`.
