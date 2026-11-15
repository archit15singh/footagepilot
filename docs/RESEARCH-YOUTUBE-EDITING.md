# Learning editing techniques from YouTube

The Instagram reviews identify effects worth recreating. Use YouTube tutorials to discover the controls, source material and decisions behind those effects. Start with a question from an edit in progress. Select the chapter or example that demonstrates the answer, then try it on a short clip with one variable changed at a time.

| Question | First-party lesson | Exercise and evidence |
| --- | --- | --- |
| How can sound announce the next shot? | [James Bonanno’s J-cut demonstration on Adobe Live](https://www.youtube.com/watch?v=RshrqjM1S_o&t=120s). The published chapters cover J-cuts at 2:00, sound elements at 7:00 and level changes at 11:50. Adobe defines the J-cut as incoming sound starting before the picture switches. [Adobe’s split-edit instructions](https://helpx.adobe.com/ca/premiere/desktop/edit-projects/trim-clips/perform-j-cuts-and-l-cuts.html) | Keep the picture fixed. Compare an incoming sound starting at the cut and starting slightly before it. Measure the exact offset, then listen for whether the lead helps the viewer anticipate the reveal. |
| How should sound layers be planned and checked? | [Blackmagic Design’s Introduction to Sound Design](https://www.youtube.com/watch?v=n4uTGns2z7c) covers a spotting list, markers, effects placement and clip and track levels. The official training page includes a lesson project. [Fairlight training and project files](https://www.blackmagicdesign.com/products/davinciresolve/training) | Pick three visible actions. Mark their times and build the bed, action sounds and transition cues on separate tracks. Compare the bed alone with the full mix and check whether each effect adds something identifiable. |
| How do we reproduce a grade across different footage? | [Blackmagic Design’s Color Management lesson](https://www.youtube.com/watch?v=CTAzjAReZvs) covers the available color management systems. [Advanced Color](https://www.youtube.com/watch?v=zvwmgOeXd28) covers organizing grades with nodes and isolating regions. | Use a matched shot for the before/after. Record its input and output color spaces, keep the technical transform and creative adjustments inspectable, and try the look on a second shot under different lighting. Check a known neutral, highlights and the mask edge. |

The source notes above come from published chapter lists, video descriptions and supporting vendor material. Use the timestamped transcript and inspect the demonstrated frames or lesson project when extracting an actual recipe. Capture what changed, what must be true for it to work, and where the method failed on different footage. Identify direct audio observations, measured timing and model suggestions separately.

## First exercise

Used two shots from an existing cave reel and made two temporary three-second exports. Both contained the same 90 picture frames at 30 fps and cut from the entrance to the interior at 1.500 s. The first export started a generated test tone at 1.500 s. The second started the same tone at 1.300 s. Full decoding passed, frame checksums matched between versions, and decoded audio measurements confirmed the 200 ms difference.

This exercise confirms that the sound lead survives export independently of the picture. An editorial check still needs real incoming ambience or effects and a listening comparison. The chosen 200 ms offset is a test value. Save any lesson as a recipe with a source, prerequisites, an adjustable timing range and a check. Keep untested ideas in research notes, and add a recipe to the playbook once a practical comparison supports it. Update a skill when the recipe changes a decision it makes repeatedly.

## Exercises that build judgment

| Method | Editing exercise | What to retain |
| --- | --- | --- |
| Isolate one decision | Keep the picture identical and move only the incoming sound. For a crop exercise, keep timing and sound identical and move only the framing. | The changed setting, the measured result and the part of the edit that stayed fixed during the comparison. |
| Test a counterexample | Try the same audio lead on a scene with dialogue that must finish before the reveal. Try a timeline cut where a nearby transient belongs to an unrelated sound. | The condition that made the technique fail and the earlier version so it can be compared later. |
| Transfer to different footage | Rebuild a fixed-anchor montage on a different subject, or try the same grade on a daylight shot and an interior. | Which prerequisites transferred, which had to change and one concrete example for each. |
| Rebuild from memory | Write the intended steps, then reconstruct the effect on a fresh clip before reopening the tutorial. Check the source to resolve any differences. | The step or prerequisite that was easy to miss and a check that catches it on the next edit. |
| Review without revealing the settings | Play equally loud variants in randomized order, with the same headphones or speakers. Ask what changed and which cut best serves the scene. | The reviewer’s reason and verdict. Keep ties and worse variants so the same idea can be evaluated in a different context. |

Keep a research question tied to the actual edit. Use a timing check for timing and a listening comparison for the experience of hearing the cue. A technique can pass the first check while its creative result remains open.
