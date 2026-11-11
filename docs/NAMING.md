# FootagePilot naming decision

Chosen 2026-11-12. FootagePilot describes an agent-operated editor for recorded footage, with reviewable edits and technical verification. It does not imply that footage, voice or a professional final story is generated automatically.

## Similar tools

| Tool | Naming signal | Lesson for this product |
|---|---|---|
| [Auto-Editor](https://auto-editor.com/) | Describes automated editing directly; audio, motion and subtitle analysis | Make the activity recognizable without explaining a metaphor. |
| [CutAgent](https://www.cutagent.ai/) | Editing action plus agent; works with DaVinci Resolve | Signal agent operation, while accurately describing our own CLI-first pipeline. |
| [OpenChatCut](https://openchatcut.com/) | Open distribution, conversational interface and cutting | Avoid implying chat is our primary interface; our strongest workflow is the CLI. |
| [WeftCut](https://weftcut.com/) | Craft metaphor plus explicit editing word | An editing word helps, but a less metaphorical name needs less explanation. |

FootagePilot puts the input first: existing footage. Pilot communicates directed automation and review rather than a guarantee of unattended editorial judgment.

## Shortlist and checks

| Candidate | Clarity | Finding |
|---|---|---|
| FootagePilot | Clearly suggests assistance operating on footage | Selected; no exact-name web result or GitHub repository found in this check. |
| CutPilot | Clear editing/agent association | Already used by [an AI editing service](https://cutpilot.ai/en/) and [an open-source project](https://github.com/lablup/cutpilot). |
| TakeCut | Clear for recorded takes | Already used by [an AI video-editor app](https://apps.apple.com/cd/app/takecut-ai-video-editor/id6815343744). |
| FootageFlow | Clear input/workflow association | Already used by [a footage-management product](https://www.footageflow.app/). |
| Clipwright | Suggests crafted clips | Already used by [an AI-assisted browser editor](https://www.clipwright.app/) and [an agent video backend](https://clipwright.io/). |

On the check date, the PyPI `/pypi/footagepilot/json` and npm `/footagepilot` registry endpoints returned HTTP 404; GitHub repository-name search returned zero matches and `archit15singh/footagepilot` returned HTTP 404. These are bounded checks, not reservations or a guarantee against every naming conflict. No package or domain was purchased/published.

## Migration

| Surface | Previous | Current |
|---|---|---|
| Product | SpliceForge | FootagePilot |
| Python distribution/module/CLI | `spliceforge` | `footagepilot` |
| Environment overrides | `SPLICEFORGE_*` | `FOOTAGEPILOT_*` |
| Workbench request header | `X-SpliceForge-Token` | `X-FootagePilot-Token` |
| Remotion composition | `SpliceForge` | `FootagePilot` |
| GitHub repository | `archit15singh/spliceforge` | `archit15singh/footagepilot` |
| Main local workspace | `/Users/singh/projects/spliceforge` | `/Users/singh/projects/footagepilot` |

Update commands, imports and exported environment variables to the current names. No legacy module or environment aliases are introduced. Project JSON schema and media formats remain unchanged. Historical Git commits, screenshots, media and measured evidence are retained as originally recorded; hashes referring to an older lockfile are historical measurements, not rewritten claims about the renamed lockfile.

The previous name appears in this migration record intentionally. Archived linked worktree branches retain their historical source snapshots. Naming changes do not authorize rewriting sent messages, old releases or unrelated personal profiles.

## Verification

[Rename verification](RENAME-VERIFICATION.json) records 27 passing tests, an isolated wheel/CLI check, live workbench HTTP checks and an actual twelve-stage real-footage run producing four fully decoded/hash-verified videos. Both renderer frames were inspected for the new visible name. Codex selected a different valid 27.80-second excerpt; re-transcription is evaluated against its 101 actual selected tokens, not the old gallery text. Source model and reasoning settings remain Codex 6.1 Sol / low. Packaging discovery is explicitly limited to the Python package; local media and Node dependencies are excluded from the wheel. GitHub and workspace migration are verified after the source change passes CI.
