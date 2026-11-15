# Editing lesson library

Use the library to carry an editing decision from one project to the next. Start with the relevant [tutorial exercises](RESEARCH-YOUTUBE-EDITING.md), then use the steps below when an actual comparison produces a result worth retaining.

1. **Recall.** Run `learn-recall --topic audio-timing` before planning an audio transition. Choose a prior lesson whose conditions fit the current footage. Read unreviewed, worse and tied results for failed approaches and open questions.
2. **Try.** Change one decision and render a baseline and candidate. State what you checked and the result, with units and scope when possible. See the [editing playbook](REFERENCE-EDITING-PLAYBOOK.md) for adaptation examples.
3. **Review.** Run `compare-edits` for technical evidence. If a person gives a preference, use their verdict and reason in the comparison. A successful decode and an analyst’s hypothesis leave the human verdict unreviewed.
4. **Record.** Write a lesson with the fields below. Keep the source, conditions, exact change, verification and result. Record failed or tied creative experiments too. For a follow-up comparison, retain the old record and explain in the new finding which condition changed.
5. **Transfer.** Before treating a result as a general practice, try it under different conditions. Promote only a sanitized recipe with enough evidence for its scope into maintained documentation. Apply retrieved lessons to the current brief as evidence.

```json
{
  "topic": "audio-timing",
  "source": "https://www.youtube.com/watch?v=RshrqjM1S_o&t=120s",
  "technique": "Start the incoming shot's sound before the picture cut.",
  "conditions": "Two cave shots, identical pictures across variants, generated cue.",
  "changed": "Cue start moved from 1.500 s to 1.300 s.",
  "check": "Decode both exports, compare picture frame hashes and measure decoded cue onset.",
  "finding": "The picture cut stayed at 1.500 s and the 200 ms cue lead survived export."
}
```

```sh
python3 -m footagepilot compare-edits projects/on-cut.mp4 projects/lead.mp4 \
  --output projects/experiments/cave-j-cut.json
python3 -m footagepilot learn-record projects/experiments/cave-lesson.json \
  --comparison projects/experiments/cave-j-cut.json
python3 -m footagepilot learn-recall --topic audio-timing
```

The default library is `projects/learning`, which Git ignores. Use `--library` to share one private directory across local worktrees. Topic filters are exact. Add `--preferred-only` to retrieve only candidates with an explicit human verdict of `better`. Omit it to retrieve technical findings and counterexamples. Each record includes a copy of the comparison with its media hashes and verdict. Recording identical inputs twice yields the same record. The commands check the comparison format and record integrity. Creative judgments and additional measurements come from the people and tools that produced the input evidence.

To reproduce the example, see the [measured cave comparison](RESEARCH-YOUTUBE-EDITING.md#first-exercise). A practical next comparison uses the incoming scene's real sound and checks whether a listener can anticipate the location change.

Two local comparisons exercised the library end to end. The audio test retained a 200 ms lead across exports with identical picture frames. The color test applied desaturation to one half of a lossless 30-frame excerpt. All decoded checksums on the untreated half matched. Both records remain unreviewed for creative preference. The color test verifies fixed region isolation and leaves mask tracking for a moving subject to a later comparison. [Advanced Color training](https://www.youtube.com/watch?v=zvwmgOeXd28)
