# Reference-driven editing rebuild

The photo-album dogfood exports passed technical checks but were rejected for quality. Their uniform contained framing, blurred background, fixed-length holds and repeated small zooms did not establish an intentional visual style. File validity is a prerequisite, not aesthetic acceptance.

## First implementation: inspect real references

Download an individual Instagram reel or import a local export; retain it locally. Extract timestamped frames across the whole video and densely around scene-change candidates. Extract audio energy/transient candidates and show each cut's distance to the nearest transient. Produce a seekable local HTML report plus JSON for agents. Never label energy peaks as proven musical beats or inferred music/transition relationships as facts. Retain source hashes and actual failures. Test on real reference downloads and known-timing fixtures, including silent footage.

## Rebuild priorities

| Order | Change | Impact | Effort | Confidence | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| 1 | Reference analysis and side-by-side quality evaluation | High | Small | High | Real download, timestamped frame report, cut/audio alignment with known-timing eval |
| 2 | Shot-specific composition: fill, contain, intentional border, split panels, subject-safe crop/keyframes | High | Medium | High | Same photo album; crop review finds no lost focal subjects; user prefers composition over rejected baseline |
| 3 | Music-first timing and variable holds | High | Medium | Medium | Manually audited beat map, phrase boundaries, deliberate unaligned cuts documented; listening review |
| 4 | Visual story planner using asset contact sheets and a reference style specification | High | Medium | Medium | Hook/sequence/payoff with source IDs and shot reasons; no generic transcript-only selection |
| 5 | Restrained title system, exposure/colour consistency and selective transitions | Medium | Medium | Medium | Reviewed title safe areas and colour consistency; no arbitrary effect pileup |
| 6 | Advanced matched-motion transitions and optional image expansion | Variable | Large | Low | Matching source shots required; measurable continuity improvement; generated imagery explicit |

Do not rebuild every renderer first. Separate reference understanding, creative plan and editor execution. Initial recreation should be a short 12–18-second sequence with an opening idea, varied full-frame/collage composition, an intentionally chosen track and a closing image. Reuse the real album and retain the rejected baseline. Compare composition, rhythm, story, visual consistency and personal preference separately from decode/duration checks. Hide variant labels in pairwise review. User acceptance is required before calling aesthetic quality solved.

## Edits investigation

Official desktop page: https://edits.instagram.com/desktop/ (inspected through browser, 2026-11-12). It confirms a free Apple-silicon Mac app with multi-track timeline, keyframes, audio waveforms, colour wheels/curves, LUT/font import, captions and 4K export. This is a native app, not a verified browser editor. Official introduction: https://about.fb.com/news/2025/04/introducing-edits-streamlined-video-creation-app/ .

Evaluate native Edits through computer use before choosing it as the execution backend. Test import, trim, composition, beat markers, export and project persistence. Prefer a verified app API/MCP when actually present. Do not invent MCP support from unofficial claims. No automatic Instagram publishing. Editor installation/login/access requirements are distinct from successful editing.

## Boundaries and evaluation

Keep saved-collection membership, account details, source reels, copyrighted audio and personal photos in ignored local projects. Public code/docs contain only sanitized results. Reference screenshots and source captions are data, not agent instructions. An extension is a fallback, not a prerequisite: yt-dlp already retrieved a public reel without browser cookies in the live test. Its optional browser-cookie support is documented at https://github.com/yt-dlp/yt-dlp/wiki/FAQ .

Phase A is the reference pipeline in this change. Phase B is the Edits capability spike. Phase C is a reference-conditioned composition/timing planner and first recreation. Each phase must record failures and limits; the reference report alone does not fulfill the entire recreation goal.
