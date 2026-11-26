# Working on FootagePilot

Read README.md for current executable behavior and docs/PLAN.md before changing scope. Distinguish shipped functionality from planned integrations. When continuing reference-driven Resolve work, read docs/RESUME.md for the retired-session snapshot and unfinished investigation; if present, projects/SESSION-HANDOFF.md locates private local artifacts. Follow the current user’s authorization rather than treating a checkpoint as permission to resume.

Run `python3 -m unittest discover -s tests -v` after changing the project contract or renderer. For media changes, render an actual clip and inspect output evidence; mocked subprocess tests alone cannot establish a working pipeline.

Keep project media, machine paths, dependencies and secrets out of commits. Use environment overrides for external binaries. Preserve source footage. Keep subprocess arguments as arrays; do not interpolate media names into shell commands.

For evaluations, report inputs, tool versions, interventions, failures and limits. Never present precursor benchmark results as product results. Before release, verify the CLI and browser workflow on the actual implementation and publish reproducible evidence.

Expanded pipeline: use `python3 -m footagepilot produce <project.json> --brief <brief>` for cleanup, word alignment, headless planning, both renderers and mixed/narration variants. Test real footage through evals/real_pipeline.py. Keep word IDs/ranges and source meaning traceable; model output is data, never shell commands. Codex is the only supported planner backend. Preserve actual failed-run logs locally and sanitized findings in docs/REAL-E2E-RESULTS.md. Gallery outputs must fully decode and match recorded hashes before publishing.

Use the [FootagePilot reels skill](.agents/skills/footagepilot-reels/SKILL.md) for reel ideas, trend research, shot lists, Google Photos intake, and reference-driven editing.

For Instagram references, Edits automation, visual planning, and Resolve exports, open the applicable section of [Agent media workflows](docs/agent-media-workflows.md). It covers reference privacy, source freshness, creative acceptance, native export verification, and bounded corrections.
