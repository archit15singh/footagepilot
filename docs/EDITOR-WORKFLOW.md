# Choosing between Resolve and Instagram Edits

Use DaVinci Resolve for the master. Use Instagram Edits for a separate social cut when its text, caption, effect, or template tools serve the brief. Decide what the variant adds before duplicating the edit.

| Work | Editor | Output |
| --- | --- | --- |
| Select footage and stills, preserve people in group shots, arrange scenes, match color within a scene, and mix the score with location sound | Resolve | Edit manifest, editable DRP, and master export |
| Try a different opening, shorter cut, vertical crop, or platform-native caption or effect | Edits | Separate local project and export |
| Reuse pacing, crops, or title choices | FootagePilot manifest | Reproducible settings with replaceable source assets |
| Reuse an Edits treatment | Edits, when the installed build supports saving and reapplying it | Verified reusable template with a local record of its settings and limits |

## From master to social cut

1. Review the source by scene and identify the people, reactions, activities, and details each section should cover. Choose framing that keeps the relevant people visible. Group coverage can justify a wider canvas.
2. Build and verify the Resolve master. For reference-driven work, pass `--backend resolve` to `recreate`. For an authored manifest, run `resolve-prepare`, render in Resolve, and run `resolve-verify`. Keep the manifest, job report, and DRP together. [Resolve guide](resolve/GUIDE.md)
3. Start a new Edits project with a copy of the verified master for overlays or finishing. For changes to shot order or source trims, use the selected source clips in the new project. A rendered master imports as one clip. Its Resolve tracks, grades, and titles stay editable in the DRP. Use the current app’s supported local import and export path. [Edits guide](edits/GUIDE.md)
4. Check the exported file for playback, duration, framing, text readability, audio, and any unwanted gaps. Compare it with the master using `compare-edits` and record human preference only after review. Keep both exports with their project evidence.

## When to retain a template

Retain a treatment after it improves a reviewed export and works with replacement media. Record its canvas, shot slots and timing, text positions, effect and color settings, audio assumptions, and the app build used for the test. Keep a FootagePilot manifest when it can reproduce the treatment. For a native Edits template, verify that the installed build can save or reuse it and test the result with different clips. If the native path is unavailable, retain the settings in the manifest or project notes.

The existing Edits integration has tested local import, trims, crops, transforms, overlays, text styling, audio, transitions, and export. Desktop template reuse still needs a live test. The CLI retains its existing backend default. Specify `--backend resolve` for this workflow’s master and `--backend edits` when deliberately choosing the Edits recreation pipeline. [Edits capabilities and evidence](edits/GUIDE.md)

Keep private source media, albums, credentials, editor projects, and review exports in local project storage. Track reusable code, settings examples, documentation, and sanitized verification evidence in Git.
