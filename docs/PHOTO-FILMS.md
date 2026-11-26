# Photo films

Render a reviewed selection of local photos with subtle motion, optional dissolves and a local music track:

```sh
python3 -m footagepilot photo-film /path/to/selection.json --output /path/to/new-film.mp4
```

Example manifest (paths resolve relative to the manifest):

```json
{
  "width": 720,
  "height": 1280,
  "transition": 0.35,
  "music": "score.wav",
  "music_gain": 0.65,
  "photos": [
    {"path": "first.jpg", "duration": 3, "motion": "push"},
    {"path": "second.jpg", "duration": 3, "motion": "pull"}
  ]
}
```

Music is optional. Set transition to zero for hard cuts. Motion accepts push, pull or still. Photos are fitted inside a blurred background to preserve the complete image. Output is H.264 at 30 fps, with AAC when music is supplied. Use a fresh output filename; existing exports are preserved.

The verification sidecar records source, manifest, music and output hashes, duration, geometry and a complete decode check. Source changes during rendering fail verification. This command renders an editorial selection supplied by a human or agent; it does not automatically select photos, detect subjects or synchronise cuts to music.

Keep private source albums, manifests containing private paths, exported videos and review galleries under ignored `projects/`. Do not add personal media to the public sample gallery.

Live dogfood validation: three local album exports (portrait dissolves, portrait hard cuts and landscape dissolves) fully decoded with expected dimensions, durations and audio. Browser playback and exclusive-play/pause controls were checked in the private review gallery. Editorial preferences and audio listening quality are not automated metrics.
