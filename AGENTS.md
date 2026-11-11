# Working on SpliceForge

Read README.md for current executable behavior and docs/PLAN.md before changing scope. Distinguish shipped functionality from planned integrations.

Run `python3 -m unittest discover -s tests -v` after changing the project contract or renderer. For media changes, render an actual clip and inspect output evidence; mocked subprocess tests alone cannot establish a working pipeline.

Keep project media, machine paths, dependencies and secrets out of commits. Use environment overrides for external binaries. Preserve source footage. Keep subprocess arguments as arrays; do not interpolate media names into shell commands.

For evaluations, report inputs, tool versions, interventions, failures and limits. Never present precursor benchmark results as product results. Before release, verify the CLI and browser workflow on the actual implementation and publish reproducible evidence.
