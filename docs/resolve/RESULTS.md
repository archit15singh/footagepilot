# Resolve integration evidence

12 November 2026. Same private album assets and the 14-second visual-planner shot selection used by the Edits trial. Personal media and machine-specific logs remain local.

| Stage | Observed result |
| --- | --- |
| Install and launch | Free App Store Resolve opened; native Lua reported 21.2.0.6 and product name DaVinci Resolve |
| Internal project API | Current project name query succeeded |
| Raw image import | API returned one item; native viewer showed Media Offline. Failed |
| GUI recovery | Import Media dialog stopped responding; repeated computer-use timeouts after reconnection. User assistance requested |
| FootagePilot preparation | Ten separate 1080×1920/30 image clips plus prepared WAV generated for a deliberately cut-only 14-second comparison |
| Native assembly/export | Not completed; generated job is labelled prepared-not-executed |
| Creative comparison | No Resolve ranking or user preference verdict available |

Edits has a verified full native export including titles, collage and a transition in the preceding trial; this Resolve v1 adapter rejects those features. Comparing those different outputs as equivalent would be misleading. The cut-only job is a narrower test of timeline assembly, marker timing and delivery. Baked crop/zoom/audio preparation is disclosed; it is not native keyframe or Fairlight automation.

Resume by recovering Resolve, running the generated console job, checking native timeline properties, exporting and inspecting both positive and negative controls. A final decode check alone cannot detect an offline-media render. Keep the first failed import evidence instead of removing it from the report.

The selected public masking reel was downloaded successfully (13.211 seconds, 1272×720). Its initial analysis failed on limited-range JPEG encoding, then on a sample after the last decodable video frame. Explicit full-range JPEG conversion and conservative video-end clamping fixed both failures. The corrected run produced 15 frames, three visual-change candidates and 48 RMS-onset candidates; the contact sheet was inspected. These onsets are not musical beat labels.

All ten prepared shot clips independently decode and contain exactly 420 frames in total (14 seconds at 30 FPS). The same deliberately cut-only manifest also produced an actual Edits export of 14.0 seconds. The Resolve native side remains pending. Unit suite: 39 passing tests, including Lua data escaping, unsupported-effect rejection, input-change rejection and cumulative frame rounding.
