# Run the evaluation

Requirements: project setup from README, FFmpeg and ffprobe, whisper.cpp CLI and a local English model. Export the four FOOTAGEPILOT_* tool/model variables documented in README. Python evaluations use only the standard library.

On macOS, generate original inputs with native speech:

```sh
python3 evals/make_demo.py
python3 evals/run.py projects/demo-input/source.mp4 projects/demo-input/screen-0.png projects/demo-input/screen-1.png projects/demo-input/screen-2.png --directory projects/eval-demo
```

Other systems can supply their own narrated video containing the phrase “rejected take” in a disposable segment, plus three owned screenshots. The evaluation explicitly drops matching ASR segments, rather than claiming to infer the best story. Inspect the saved transcript before relying on that policy for real work.

The runner refuses to overwrite existing evaluation projects. It produces first.mp4, revision.mp4, sampled frames, transcript, editable project, verification and result.json. It compares decoded audio hashes across branding revisions. Copy only sanitized result files and owned review artifacts to public reports.

Run the regression suite with `python3 -m unittest discover -s tests -v`. See PROTOCOL.md for browser, robustness and qualitative checks that require additional review.
