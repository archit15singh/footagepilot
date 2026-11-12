# Bounded framing refinement

A valid native export can still crop an important subject badly. `refine-framing` compares actual crop alternatives for selected main shots before preparing a new Resolve job:

```sh
python3 -m footagepilot refine-framing EDIT.json --shots 8 --axis y --output projects/framing-001
python3 -m footagepilot resolve-prepare projects/framing-001/edit.json --output projects/job-001 --render
# Execute the generated job through Resolve, observe queue completion, then verify the actual export.
python3 -m footagepilot resolve-verify projects/job-001/job.json projects/job-001/resolve-output.mp4 --output projects/job-001/verification.json
```

Shot numbers are one-based; choose 1–3 unique main shots. The selected shots must use fill without artificial zoom. Specify `--axis x` or `--axis y`; the other axis stays fixed. Each shot gets its current focus and up to four alternatives at ±0.15/±0.30, clamped to 0–1 and deduplicated. Three source times sample the beginning, middle and last nominal frame of the original excerpt. Each sheet’s top row shows the whole source; following rows show crop options. Columns refer to the same times in every row.

Codex gpt-6.1-sol/low chooses only an existing option ID per shot, with a reason and uncertainty. It can keep the current crop. The compiler changes focus coordinates only: source windows, shot durations/order, effects, titles, music and cue map stay fixed. Media paths are made absolute so the new manifest works from its new directory. The original manifest/media stay unchanged. Input and attached-sheet hashes are checked after the call; stale inputs or unknown/duplicate/missing choices reject. Images, evidence, model log and refinement record stay in the requested output directory, which should be ignored for private media.

Resolve recreation can also opt into the same review before native preparation by adding `"framing_review": {"shots": "bookends", "axis": "y"}` to its spec. Bookends selects the first and last unique main shots; contained bookends are skipped because they retain the whole source. Alternatively, `shots` accepts 1–3 explicit one-based shot numbers. Selected fill shots with artificial zoom reject. Omit `framing_review` to keep the existing workflow. Review failure stops preparation, and the run retains the initial plan plus reviewed manifest, choices and evidence under `framing-review/`. Native completion checks the reviewed manifest fingerprint before and after export verification. This stage does not approve the edit creatively.

The separate command remains useful for an observed framing failure: inspect the proposed crop and run a new native export. The sheets show source crops without composited titles or overlays; inspect the native composition separately. Three samples do not establish continuous subject safety, tracking, identity, a best crop or human creative acceptance. A static crop may not retain a moving subject throughout; suitable footage or a future tracking implementation may be required. It cannot repair source blur or invent missing content.

Research checked 12 November 2026: Blackmagic’s [Beginner’s Guide to Resolve 18](https://documents.blackmagicdesign.com/UserManuals/DaVinci-Resolve-18-Beginners-Guide.pdf), “Changing Shot Framing,” describes reframing with Position X/Y. The [Editor’s Guide](https://documents.blackmagicdesign.com/UserManuals/DaVinci-Resolve-18-Editors-Guide.pdf), “Reframing Shots,” distinguishes animated positioning/Smart Reframe from a static adjustment. FootagePilot’s option selection uses FFmpeg’s [scale/crop filters](https://ffmpeg.org/ffmpeg-filters.html), then its existing prepared-clip/native Resolve pipeline. It does not invoke or claim to reproduce Resolve Smart Reframe. Recheck manuals and installed behavior after updates.

## Controlled evaluation

`python3 -m evals.framing_refinement BEFORE.json AFTER.json OLD-JOB.json NEW-JOB.json NATIVE.mp4 PROJECT.drp --output NEW-DIRECTORY` requires a nonempty focus-only change, unchanged shot timing, matching native project identity, full native QA, and rejection of the unchanged-framing proxy as an expected-image control. This proves a sampled rendered change, not automatic subject detection. An unchanged or visually nondiscriminative choice fails this particular controlled-change evaluation; it need not be a product failure when the model legitimately keeps the existing crop. Actual findings are in [RESULTS.md](RESULTS.md).
