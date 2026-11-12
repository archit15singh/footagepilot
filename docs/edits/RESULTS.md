# Reference and Edits live findings

Observed 2026-11-12, Edits Mac 455.0.0.32.104. Private media and full local logs are excluded from Git.

Before this change, the product could render transcripts and simple photo sequences, but it had no executable reference-inspection command or Edits backend. A real album run was rejected by the user despite passing technical checks. Its positive technical results remain valid; its creative quality did not pass.

## What ran

- Downloaded a public saved reference through existing yt-dlp without an extension or browser cookies. A 13.837-second reference was fully decoded and converted into 175 timestamped frames (regular samples and dense scene-change samples), with 58 visual-change candidates and 46 RMS-novelty audio candidates. Dense collages can create many scene changes; those counts are not semantic edit counts.
- Inspected playback from five selected videos through native browser computer use. One additional photo-animation reference stayed on one frame and was excluded as playback evidence. No reliable listening channel was available. Detailed saved membership and URLs remain private.
- Installed the official signed/notarized Edits Mac app with user approval. Inspected the example project, native imports, source preview, timeline, transforms, audio beat-density controls and settings. Enabled local automation with separate user approval and discovered 274 tools.
- Built a fresh native project from 10 personal photos, four panel overlays, two titles and an original local score. Trimmed/reordered clips, applied full-frame transforms and keyframes, set text/font/position and audio gain/fades, saved and exported. The 14.0-second output fully decodes at 1080×1920/30 fps with HEVC video and AAC audio. Output hash and sanitized evidence are in [edits-native.json](../../evals/results/edits-native.json).
- Probed native audioOnsets/detectShots. Native tempo estimation returned 117.5 BPM for a score whose authoring grid is 120 BPM. This discrepancy is a reason to preserve provenance and verify timing, not treat a model estimate as ground truth.
- Retrieved and read all 14 tutorials linked from the official home page plus home/desktop/blog. All 17 normalized text hashes matched on a subsequent live fetch. Capability availability remains version/platform-specific.

## Failures and fixes

1. MCP import by path was rejected for missing sandbox access. Native folder import established access. No sandbox bypass.
2. Passing the schema's required audioKind for a photo mutated the timeline then errored. Visual imports now omit this parameter; a failed mutation is never blindly retried.
3. Export preset guesses were rejected. Verified a complete HD/HEVC preset with the app's native enum values.
4. An oversized title wrapped badly in the first native export. Sampled-frame inspection caught it; font size/contrast were revised and the extra subtitle removed.
5. Direct export into the repo failed with native permission error. Export now uses a fresh filename in Edits' writable export directory, then copies and verifies locally. Failed attempts and native projects were retained.

## Evaluations

`PYTHONPATH=. python3 evals/reference_quality.py --work projects/new-reference-eval` exercises actual FFmpeg commands. The known-cut fixture detects cuts at 1/2/3 seconds and audio pulses within 50 ms; a silent negative control has no audio candidates or cut/audio associations. [Timing evidence](../../evals/results/reference-timing.json).

34 regression tests cover existing behavior, URL restrictions, pulse/silence behavior, stale research detection and rejected manifests before project mutation. Real native rendering is a separate live check, not mocked proof. See the local sidecars for full operation readbacks; no personal media is published.

## What this does not establish

The new output has full-frame composition, a collage and variable holds. It has not received a user preference verdict. `compare-edits` therefore records unreviewed and promote=false. There is no claim that a numerical beat estimate understands music, that screenshots capture every transition, or that photo motion can reproduce cinematography. Fully automatic reference-to-shot planning, broader transition evaluation and reliable listening review remain work for the active rebuild goal.

Additional failure controls: a URL run initially skipped a reel because its metadata omitted duration. The downloader now allows unknown duration during extraction and enforces the limit with ffprobe afterward (download still bounded by 150 MB). A native transition dry-run failed before mutation; transitions readback confirmed no insertion, and direct insertion/readback succeeded. Failures remain recorded locally rather than erased.

## Visual planner and integrated run

A live headless Codex 6.1 Sol / low run received the actual reference contact sheet and ten asset thumbnails. It produced source-ID shot reasons, observations/uncertainties, beat-count holds and a complete quadrant collage. The compiled plan rendered through native Edits. A subsequent `recreate` run chained freshness → Instagram download/analysis → visual Codex planning → native export successfully in one command, producing another 14-second edit. All intermediate plans, operation readbacks and failures remain local. [Sanitized integrated evidence](../../evals/results/visual-recreation.json).

36 unit tests pass, including rejection of unknown asset IDs, incomplete/overlapping collages, out-of-budget timing and zero tempo. The model cannot hear the reference; it uses sampled visual grammar and supplied timing provenance. It can propose crops and cut/dissolve choices, but its rationale is a hypothesis that requires rendered review. The source score uses a fixed 120 BPM grid; this does not establish arbitrary-song beat tracking or phrase understanding. User creative preference remains unreviewed.

The `inspiration-open` entry point was also run against the local private collection configuration; native computer use verified the intended Video ideas collection opened in Brave. Reference selection stays a computer-use step. The source URLs and collection membership are not published.
