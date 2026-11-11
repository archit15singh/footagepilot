# Current pipeline

The functional pipeline is implemented in footagepilot/pipeline.py. It runs MakeMyClip cleanup, alignment.py, planner.py, word-level apply_plan, both renderer adapters and audio.py. See [the real run](REAL-E2E-RESULTS.md) for current verification and limits. The CLI is the primary interface; the earlier browser workbench remains available without further UI changes.

# Architecture and boundaries

The editable project.json stores source, ordered keep ranges, brand, graphics toggle and storyboard cards. transcript.json records local whisper.cpp segments and explicit keep decisions. FFmpeg trims and concatenates selected audio/video; Remotion composes a source pane, reviewed captions and timed image cards. verification.json records full decode, expected/actual duration and graphics diagnostics.

The HTTP workbench exposes the same operations as the CLI and serializes background jobs. It serves only its page and project output, binds to loopback, checks Host and mutation tokens, and supports byte-range playback. This is a trusted local tool, not a multi-user server.

This version uses whisper.cpp plus FFmpeg plus Remotion. It does not yet integrate MakeMyClip or HyperFrames; their benchmark results informed the staged design. It has no LLM planner or autonomous story-selection model. A coding agent can edit the project and run the CLI; a human can use the workbench. These are two interfaces to the same explicit decisions.

Current limitations: segment-level rather than word-level edits, approximate caption timing, pauses within retained segments, fixed source-pane layout, user-authored storyboard cards, no audio mixing interface, no persistent job queue, no multi-project browser switcher. Output verification does not establish aesthetic quality or natural speech. The qualitative evaluation must describe these limits directly.
