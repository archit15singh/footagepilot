# Resume FootagePilot

Session retired at the user's request on 12 November 2026. The long-running build goal is **paused**, not completed. This document is a snapshot; follow the next user's instructions and inspect current Git/app state before resuming implementation. The retirement change is documentation only.

## Intended end state

Recreate the visual grammar of videos selected from the user's saved Instagram ideas using their footage, with Codex directing native DaVinci Resolve editing. Preserve reference selection/download, timestamped frame analysis, honest music/transition evidence, editable native projects, actual export verification, qualitative comparisons and an iterative research/revision loop. Keep building through reviewed, tested PRs while authorized. Technical export validity does not establish that the result resembles a reference or that the user prefers it.

## What is shipped and where to read

| Area | Implemented behavior | Authority / limits |
| --- | --- | --- |
| Product setup and speech pipeline | MakeMyClip cleanup, word alignment, Codex planning, HyperFrames/Remotion, music/SFX variants | [README](../README.md), [setup](SETUP.md), [earlier real run](REAL-E2E-RESULTS.md). Earlier evidence; the latest session focused on Resolve. |
| Saved inspiration | Open the configured private collection in Brave; computer use selects a reel; CLI downloads one reel or ingests a local file | [Reference plan](REFERENCE-PLAN.md). Collection enumeration is not an automatic public API. No Instagram publishing. |
| Reference understanding | Timestamped frames, dense before/at/after change samples, source hashes, audio-energy/onset candidates, seekable report | [Evidence contract](REFERENCE-EVIDENCE.md). No listening, semantic transition classification or verified musical-beat claim. |
| Visual story planning | Headless Codex `gpt-6.1-sol`, low reasoning; validated asset IDs, source excerpts, canvas/layout/title choices and frame citations | [Resolve guide](resolve/GUIDE.md), [video evidence](resolve/VIDEO.md). Source previews are sparse; model reasoning can be wrong. Codex is the only product planner. |
| Native editing | Free Resolve 21.2 internal safe Lua; editable cuts, TextPlus, progressive panels, black spans, dissolves, mask reveals and Screen plates | [Layouts](resolve/LAYOUTS.md), [transitions](resolve/TRANSITIONS.md), [plates](resolve/PLATES.md). Crop/zoom/audio preprocessing uses prepared media; the final credited movie renders in Resolve. |
| Music and pacing | Authored timing, source-bound RMS-onset candidates, reference soundtrack selection and opt-in exact reference change rhythm | [Music cues](resolve/MUSIC-CUES.md), [reference rhythm](resolve/REFERENCE-RHYTHM.md). Transients and visual changes are candidates, not automatically beats or phrases. |
| Reviewed effects | Pinned, provenance-recorded photographed glass preset, optional automatic acquisition and bounded model selection | [Plate source](resolve/PLATE-SOURCES.md). Not the creator's identified asset and not refraction of underlying footage. |
| Crop revisions | Bounded focus alternatives; optional recreation bookend review; original brief retained to preserve intended subject/action | [Framing](resolve/FRAMING.md). Static, three-sample evidence; no continuous subject tracking. |
| Typography revisions | Title-only review of a verified export using actual reference/candidate frames and measured native title boxes | [Typography review](resolve/TYPOGRAPHY-REVIEW.md). Fixed original words/order and opening intervals; no OCR or exact font-match guarantee. |
| Learning and comparisons | Freshness checks, hash-bound reference reviews, explicit human feedback and retained losing attempts | [Reference review](resolve/REFERENCE-REVIEW.md), [results](resolve/RESULTS.md). Model suggestions never become user preference automatically. |

`CLAUDE.md` routes agents to `AGENTS.md`; that does not enable a Claude planner backend.

## Latest verified milestones

Implementation baseline before the retirement docs: `6da5733d08bc93cf55b376f0186dbfee1b04f285` ([PR #42](https://github.com/archit15singh/footagepilot/pull/42)). Earlier changes and their detailed evidence remain in [Resolve results](resolve/RESULTS.md).

| Change | Evidence |
| --- | --- |
| [PR #38](https://github.com/archit15singh/footagepilot/pull/38): real-glass acquisition and native comparisons | [Real-glass results](../evals/results/real-glass.json); 45%/75% treatments and a later corrected crop. |
| [PR #39](https://github.com/archit15singh/footagepilot/pull/39): integrated crop review and zero-origin proxy timestamps | [Integrated-framing evidence](../evals/results/integrated-framing.json). A fractional-start plate caused a one-frame mismatch; the rejected precursor stays retained. |
| [PR #40](https://github.com/archit15singh/footagepilot/pull/40): creative brief propagated into crop review; absolute native output paths | [Framing-intent evidence](../evals/results/framing-intent.json). The controlled ending retains the walker while losing the arch apex. Relative output previously caused an empty native import. |
| [PR #41](https://github.com/archit15singh/footagepilot/pull/41): a third saved reference and measured rhythm transfer | [Rhythm evidence](../evals/results/reference-rhythm.json). A fresh 14-second, 25-shot vertical adaptation reached `verified-export`, with 75 composition samples and a wrong-shot control. |
| [PR #42](https://github.com/archit15singh/footagepilot/pull/42): title-only refinement | [Typography evidence](../evals/results/typography-refinement.json). Native four-word revision retains all 25 shots, passes 75 composition / 4 title / 19 timing checks, and rejects the original one-title movie against the new requirements. |

The latest implementation suite passed **133 unit tests**, compilation, CLI help and whitespace checks; each implementation PR above also passed its CI checks. Native queue completion was visually observed for the credited exports, and matching editable DRPs were retained. These are concrete execution results, not general performance benchmarks or creative-acceptance scores.

The initial size-12 typography attempt passed technical checks but was visibly undersized. The final refinement uses actual export measurements and chose size 28. An intermediate plan was prepared but never executed. A former title control was nondiscriminative because height/contrast cannot identify wording; the replacement tests the explicit original movie against the new multi-event requirements. Preserve those failures and qualifications.

## What remains incomplete

- No user-approved overall aesthetic result. The latest variations remain `creative_acceptance: unreviewed`.
- Repeated road/cave/architecture sources, softness/tilt, fewer distinct performances and unmatched grade still limit resemblance to the athletic reference. Its first 14 seconds were adapted, not the entire film.
- Typography scale/changing-word treatment is closer in category; per-background placement differs, and exact font identity is unproven.
- No reliable listening verdict, automatic phrase/downbeat understanding, continuous subject-safety guarantee or universal matched-motion transition recreation.
- Native console access still needed the documented saved-workspace restart/bootstrap recovery. GUI integration is agent-operated, not a restart-free unattended service.
- The user can choose saved references through computer use, but collection scraping and Instagram publication are outside the implemented workflow.

## Paused investigation: native color grading

Only research and an **unexecuted local capability sketch** exist. No grading implementation, native setter/readback result, graded export, evaluator or PR was completed. No existing film was graded by this investigation.

The [official Color overview](https://www.blackmagicdesign.com/products/davinciresolve/color) and [training catalog](https://www.blackmagicdesign.com/products/davinciresolve/training) were consulted. The installed 21.2 scripting changelog mentions CDL inspection; its README references API `.pyi` definitions that were not found in the inspected bundle. Method signatures, free-edition behavior, color-management assumptions and rendered transform math still require direct verification. Search snippets or third-party API mirrors are not sufficient proof.

After explicit resumption, a useful next experiment is a **controlled native saturation adjustment** on a fresh project, keeping the established edit/titles/music fixed. First verify the installed API and readbacks on a copy, then confirm editable native state, actual render, independent image expectations and a no-grade failure control. Inspect real before/after frames beside the reference. A statistical palette match across different scenes is not proof of a matching look. Do not weaken safe scripting, buy Studio, install new tools or change existing projects merely to make the experiment work.

## Restart procedure

1. Read `AGENTS.md`, this snapshot and the relevant guide above. Inspect the current branch, status and remote before editing. Do not reimplement merged features from old conversation summaries.
2. If present, read the **ignored local** `projects/SESSION-HANDOFF.md` for exact worktree, media, evaluation, gallery, binary and checkpoint locations. It contains no authorization to resume work by itself. Private media is intentionally absent from a fresh clone; do not invent it or publish it.
3. Verify whichever existing baseline/export will be used. Inspect retained failures as well as passing reports. Run `learn-check` against the relevant source registry; re-research changed/stale sources instead of renewing dates automatically.
4. Reinspect the current Resolve/browser UI; element indices and console variables expire. Preserve app projects and source media. Preparing a job is not assembly, rendering or creative acceptance.
5. When implementation is authorized again, isolate the change, run appropriate tests and actual media checks, retain negative controls and qualitative limitations, then push/PR/merge within current authorization. Keep the full objective intact.

For contract/renderer changes: `python3 -m unittest discover -s tests -v`; also use the relevant real-media evaluator and native observation. Documentation retirement does not require a new video render. At handoff the local review gallery contains 36 videos/reference players, including losing attempts; it is not a public hosted gallery.
