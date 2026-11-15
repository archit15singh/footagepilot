---
name: footagepilot-saved-reel-delta
description: Review newly saved Instagram reels in Video Ideas and Tutorials, retry unfinished reviews, and turn timestamped picture and sound evidence into reusable editing practices.
---

# Review changes in saved reels

1. **Find the baseline.** Reuse the local baseline for this Instagram profile and its review notes. Keep membership, reel IDs and URLs, media, frame/audio evidence, and notes in an ignored project directory or an existing private workspace. To migrate a prior inventory, plan it against a fresh baseline and mark only reels backed by existing review notes. With no prior review, use the first inventory as the initial queue.
2. **Capture both folders.** Open the signed-in profile's Saved page in the user's authorized browser and open **Video Ideas** and **Tutorials**. Collect reel shortcodes from the visible post links, preserving case. Scroll through each collection and accumulate IDs across pages because off-screen tiles may be unmounted. Set a collection's capture to complete after verifying the end of the grid and resolving whether ambiguous post tiles are videos. Use an incomplete capture for blocked pages, uncertain tiles, or an unverified end. Separate each profile's baseline.
3. **Plan the delta.** Write the capture using the example below and run `saved-reel-delta`. Report additions and confirmed removals per folder. Work from `review_queue`, which includes unfinished reels and deduplicates cross-folder saves. A removed reel keeps its prior review history. An empty queue requires no new reel analysis.
4. **Review each queued reel.** Run `python3 -m footagepilot reference SOURCE --output FRESH_DIR` on the individual URL or an authorized local copy. Read the [tool guide](../footagepilot-reels/references/tools.md) when retrieval or browser playback needs a fallback. Use the decoded frame timeline and adjacent frames around cuts, crops, titles, masks and panel changes. Inspect opening, progression, payoff and loop. Sample contiguous frames around fast or localized changes and record actual coverage. For Tutorials, capture the visible control or operation, its prerequisite and its result. For Video Ideas, capture the creative mechanism and the footage needed to reproduce it.
5. **Check sound on the same clock.** Listen around key edits where supported. Use the seekable spectrogram, cue table and verified frames to compare picture boundaries with sound events. Use `reference-listen` on relevant excerpts when a local audio model is available. Distinguish heard sound, measured events, creator statements, and model hypotheses. A nearby transient alone cannot establish a beat, lyric, instrument, or editing intent. If a downloaded copy lacks audio, check the signed-in player before calling the source silent. Record any unresolved access or evidence gaps.
6. **Write and advance.** Save a durable `SHORTCODE.md` for each completed review with source link, timestamped observations, sound evidence and limits, and a rebuild recipe with inputs, ordering, and a check. Compare findings with the [editing playbook](../../../docs/REFERENCE-EDITING-PLAYBOOK.md) and previous notes. Record what the new evidence adds, corroborates or qualifies. Include a concrete adaptation and a failure mode when supported. Keep inaccessible reels queued and report the blocker. Advance with only the IDs whose notes and synthesis you verified. Re-run the plan to confirm the remaining queue. Publish only sanitized practices when the current request calls for repository updates.

## Local files and commands

Set `run` to the absolute directory of the private review workspace. Keep `baseline.json` across runs and capture a fresh `snapshot.json` for each comparison. Example capture:

```json
{
  "collections": {
    "video-ideas": {"complete": true, "reels": ["Example_01"]},
    "tutorials": {"complete": false, "reels": []}
  }
}
```

```sh
python3 -m footagepilot saved-reel-delta "$run/baseline.json" "$run/snapshot.json" > "$run/plan.json"
python3 -m footagepilot saved-reel-advance "$run/baseline.json" "$run/plan.json" \
  --notes-dir "$run/notes" --reviewed Example_01
```

Advance uses a local file lock on macOS or Linux. Omit `--reviewed` to save observed membership while retaining the unreviewed queue. For incomplete captures, `removed: null` indicates unknown removals and previously seen membership is retained. A stale plan requires a fresh capture and comparison before advancing.
