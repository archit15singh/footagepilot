# Import selected original videos

Use computer use to inspect your signed-in media library and download selected original videos through its normal UI. FootagePilot can then import the resulting ZIP without manual filename/path repair:

```sh
python3 -m footagepilot import-sources /path/to/selected-videos.zip --output projects/source-pool
```

The command accepts 1–20 MP4/MOV/M4V/MKV/WebM members, with up to 4 GiB of declared uncompressed video data. It skips other files, rejects encrypted/empty/oversized members, streams each video to a generated flat `clip-NN` name, and probes its video metadata. Member directories and original filenames never become output paths; duplicate names receive distinct generated names. It preserves the original ZIP. A new output directory is required; failures retain partial files plus `failure.json`, without claiming a completed source pool.

`sources.json` retains the archive fingerprint, original member names, extracted hashes, durations, coded dimensions, rotation metadata and audio presence. Quarter-turn display dimensions assume square pixels; arbitrary rotation is marked unknown rather than guessed. Probing does not prove full decode or visual quality. `assets.json` contains ready-to-copy visual-spec assets with absolute paths. Merge those entries into a spec (rename IDs if combining pools), inspect their temporal/canvas crop previews, then run `recreate --backend resolve`. Import does not automatically select the best source windows, authenticate to Photos, or bypass library download controls.

Keep output under ignored `projects/` for personal sources. Original names, private source membership, downloaded media and generated native artifacts stay local; publish sanitized findings only.

Research checked 12 November 2026: Python’s [ZIP file documentation](https://docs.python.org/3/library/zipfile.html#zipfile.ZipFile.open) supports reading a member as a stream and passing `ZipInfo` for duplicate names. FootagePilot deliberately writes generated names rather than extracting member paths. The 20-video/4-GiB limits are product bounds, not ZIP format limits. Orientation metadata is an inventory aid; native framing still needs actual image review.
