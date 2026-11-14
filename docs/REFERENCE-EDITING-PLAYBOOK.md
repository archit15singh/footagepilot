# Editing patterns for short-form video

Use this when planning an original edit from a reference. Identify the relationship that makes the reference work, then reproduce that relationship with the new story, footage and sound. For example, a recurring subject position can connect unrelated locations. A held opening can make a faster sequence feel like a release.

## Build the sequence

| Pattern | How to apply it | What to check |
| --- | --- | --- |
| Hook, escalation and payoff | Establish a simple question, action or promise. Escalate with new information, closer scale or faster holds. Give the reveal enough time to register. | A viewer can describe the promise before the reveal and identify the moment that resolves it. |
| Visual rhyme | Hold one feature across cuts, such as a wheel position, eye line, silhouette, center of rotation, color or direction of travel. Change the surroundings or the subject's scale. | Compare outgoing and incoming frames at playback size. The eye should land in the same area unless disorientation serves the story. |
| A long hold with internal movement | Lock the camera or framing and let a gesture, crowd, weather or a change in scale supply motion. Follow with a faster section only when the story calls for it. | At least one visible change rewards attention during the hold. Leave room around the action and keep the ending readable. |
| Travel montage with a through line | Start from an anchor such as a person, vehicle, recurring pose or point of view. Alternate establishing views with action and details. Use transit shots to communicate movement. | Replace any two shots that do the same job. Match light, palette or subject placement across spatial jumps. |
| Before and after | Reuse the same framing for the source and the treatment. Let the viewer see the effect of one important change at a time. Hold the result. | Check edge integrity, lighting and texture at the join. The result remains legible on a phone. |
| Reveal by reframing | Use a tight composition to withhold context and a wide one to expose it, or show a behind-the-scenes setup before the finished perspective. | Match the subject's pose, position and action across the reveal. Check both crops for intentional negative space. |
| Loop with a return | Plan the first and last image together. Repeat a framing, performed action, text rhythm or motif. Bring the transition back to the opening state. | Play two consecutive cycles and check the first sharp frame, exposure, motion direction and audio tail at the seam. |

## Arrange the picture and text

1. **Choose a focal point before the crop.** Use symmetry for deliberate balance, leading lines for direction, or an off-center subject when the remaining space carries meaning. Use fill for immersion and an inset for a designed border or room for another element. Inspect the actual export for accidental bars and clipped actions.
2. **Design the collage as a sequence of states.** Start with an anchor shot. Give each panel its own bounds, source crop, entry, hold and exit. Use contrast between rows and columns, a strip that opens into a wider image, or a composition that accumulates around the anchor. In a grid swap, hold a landmark steady and replace cells independently. Avoid giving every panel equal visual weight unless the design is intentionally uniform.
3. **Make titles do one job at a time.** Use whole phrases for context, short word events for vocal emphasis, and a stable title for a destination or chapter. Establish a consistent zone and hierarchy, then adjust contrast and placement against individual backgrounds. Test the longest word and the brightest frame at delivery size. Leave a clean hold after a scramble, type-on or other animated entrance.
4. **Match motion before adding a transition.** For a spin, camera cover, hand wipe or foreground occlusion, shoot a comparable action on both sides. Match the axis, direction, subject position and speed. Test a cut inside the blur or full cover. For a generated extension, anchor it to the actual junction frame and inspect deformation in the last generated and first real frames.
5. **Make effects respond to a visible cause.** Establish the action, show the effect at its point of contact and give the reaction room. Scope the plate, mask or light treatment to the intended subject and check occlusion. Use flashes, inversion and layered graphics when they mark a transition or change in energy.

## Edit with the soundtrack

- **Pick the musical passage for the scene's job.** Audition the actual section for its entrance, vocal density, tension, release and exit. Keep a version in which dialogue can carry the scene by itself. Source music and effects appropriate to the finished project.
- **Mark phrases, useful accents and important words on separate tracks.** Set the major change in pace at a meaningful cue. Subdivide only where images remain legible. Give performance, visual punch lines and dense text independent holds when their timing calls for it.
- **Choose the sound for each visible action.** Keep narration, music, ambience and effects independently editable. Use ambience to join spaces, a short transient to emphasize contact and a tail to communicate scale. Check whether effects are audible and whether the voice remains intelligible.
- **Inspect visual changes and audio events independently.** Energy novelty flags candidates that may come from speech, percussion, effects or noise. A scene score can miss titles, small panels, fades or motion, and can overcount flashes. Compare the visual frame or affected region with the audible cue before calling a moment beat-synced.
- **Finish the mix in context.** Play through the scene change and across the ending, then check the loop or fade at listening volume. Test a version with fewer synchronized edits. A long hold, silence or an intentional late cut can create the contrast that makes the next cue deliver.

## What changed at the cue

| Observation | Rebuild implication |
| --- | --- |
| In a mountain montage, the picture holds for about 3 s before a run of changes roughly 0.71 s apart. On the shared timeline, nine of 12 candidates are within 50 ms of an RMS onset. The median is two after circularly shifting the onset series 16 times. | Try a sustained opening, a short run on repeated musical accents and a longer closing image. Confirm the actual accents against your track. |
| In a layered room portrait, low-band peaks repeat about 0.64 s apart while a single frame accumulates several panels. The whole-frame detector registered zero candidate changes. | Time changes by panel, then inspect each crop around the cue. A sequence can have sound-led changes without any full-frame cuts. |
| In a rapid vehicle montage, recognizable wheels stay in roughly the same place across visual changes about 0.1 s apart. Visual changes outnumber the detected RMS events. | Match subject geometry before increasing cut rate. Leave some visual subdivisions independent of audible transients. |
| In a perspective-reveal clip, the setup switches to the finished view around 4.42 s and the low-band energy rises around 4.35 s. The finished angle then holds. | Test whether the reveal reads better slightly before, at or after a cue. This measured offset gives one example to compare. |

For a dense sequence, compare the measured match count with a few shifts of the same onset series. If a similar count survives those shifts, annotate only the individual cues supported by the picture and audio evidence. An action recap had 18 of 67 candidates within 50 ms, compared with a shifted median of 21.5. Its visible acceleration remains a useful editing pattern. The offset measurements describe the delivered mixes. Listening is needed to distinguish music, speech, effects and coincident energy.

Check localized changes at their actual boundaries. The whole-frame detector missed a spin match that passed from a blurred building outline to a clear figure against the sky. An animated return to an opening composition produced several detections in less than half a second. For reconstruction, mark the spin join and annotate the animated return as one effect sequence with several visual states.

## Keep the grade and tutorial editable

- Set the project color-management assumptions first. On a representative frame, establish white balance and exposure, shape contrast, then decide what saturation and look the scene needs. Keep a technical color-space transform and a creative LUT independently inspectable. Follow the transform order and expected color space for the actual footage and project.
- For a local grade, establish the base look, isolate the subject, then shape the background where needed. Feather or track the isolation and check moving edges. Compare before and after with the same frame and exposure context. Scopes can reveal clipping, hue shifts and balance changes across the cut.
- Give reusable node presets names that describe their purpose and expose the adjustment that actually varies by shot. A recipe from a tutorial is a starting point. Viewer settings, color science, camera profile, exposure and lighting all affect the result.
- To teach a technique, show the outcome, isolate the control and replay the exact change. Use a known image while swapping one variable. For a shortcut or timeline operation, show its visible result and verify the binding against the active preset. Keep recurring assets in shared bins and make ripple or grade changes within the intended clip or track scope.

## Rebuild one technique at a time

| Starting exercise | Draft | Review |
| --- | --- | --- |
| A postcard sequence | Hold a hero shot, build a few asymmetric panels on selected cues, contract to a title and reopen into a clean montage. | Inspect the intended region at every panel entry and exit. Read the title against its hardest background and check the last panel for subject clipping. |
| A matched move | Shoot the same turn or lens cover in two places and use a hard cut at peak blur. Keep a straight-cut version for comparison. | Check orientation and sharp bookend frames. Play both versions with and without their audio to identify what is carrying the seam. |
| An action montage | Start with a sustained wide or a short spoken premise. Move into tighter holds at the musical release. Let the closing reaction or wide frame settle. | Compare the first and last moments with the premise. Check for duplicate shot roles, intelligible voice and a clear change in pace. |
| A grade demonstration | Show the same frame ungraded, balanced and with the look applied. Use one shot whose lighting differs to test the preset. | Inspect scopes, skin or a known neutral, mask edges and shot-to-shot consistency. Check that the grade is still editable in the native project. |

Record the new footage, crop, intended story role, hold duration, transition reason and cue for each shot. Keep reference observations, the adapted plan, the rendered result and any human feedback distinct. A native project and a technically correct export demonstrate execution. Creative review determines whether the adaptation succeeds.

## Evidence and limits

The 14 November 2026 review covered 50 short videos, totaling 25,914 decoded video frames and 49 audio tracks. One reel had no audio in either the player or the local copy. Every decoded video frame received a timestamped change score. Visual interpretation used sampled frames and selected boundaries. Audio evidence combined waveform and band-energy measurements, machine transcription where informative, and visible or creator-supplied cues. Direct listening and individual musical-phrase verification were unavailable in the analysis session. These are patterns to try. Their effect on creative preference or audience performance has not been tested.

The existing tooling and evidence conventions are described in [frame-cited reference planning](REFERENCE-EVIDENCE.md), [music cues](resolve/MUSIC-CUES.md), [reference rhythm](resolve/REFERENCE-RHYTHM.md), [layouts](resolve/LAYOUTS.md), [transitions](resolve/TRANSITIONS.md) and [typography review](resolve/TYPOGRAPHY-REVIEW.md).
