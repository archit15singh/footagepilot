# Editable color presets

Add `"color_preset": "soft-color-v1"` to a Resolve edit manifest or a visual spec used by `recreate --backend resolve`. Choose `monochrome-v1` for black-and-white footage. Omit the field for the source look. The visual planner carries the preset into the edit manifest, where it can be inspected and reused with `resolve-prepare`.

| Preset | CDL saturation | Intended use |
| --- | ---: | --- |
| `soft-color-v1` | 0.65 | Subdued color across mixed outdoor footage |
| `monochrome-v1` | 0 | Emphasize shape, texture, and motion |

Resolve applies the look to footage on the main track, collage panels, and incoming transition layers. Each affected clip has a named, editable color node. Titles and motion plates retain their authored colors. FootagePilot checks the setter, saturation readback, and node label before requesting a render.

The native recipe uses DaVinci YRGB and is calibrated on free Resolve 21.2.0.6. Preparation rejects known HDR, log, and wide-gamut tags. Selecting a preset declares that untagged sources are SDR, so confirm the input color space when camera metadata is missing. The presets adjust saturation. Exposure, white balance, log conversion, and shot-to-shot color matching remain separate work.

Run the usual native render and verification workflow. The report compares sampled chroma against both the graded and neutral compositions outside active title bands. Channel differences isolate saturation from luminance differences introduced by compositing and resampling. The report requires measurable color evidence and retains the frame and both errors for each discriminating sample. Review the actual export for skin, skies, dark scenes, and text contrast. [Resolve workflow](GUIDE.md)

## Implementation choice

- **Resolve CDL** is the smallest change that keeps a versioned look editable in the existing project. The installed 21.2 scripting changelog names `TimelineItem.GetCDL`. A live console probe on a disposable clip confirmed `SetCDL`, the returned saturation, and the editable node label. The independent image model uses the Rec.709 coefficients described by OpenColorIO. [Resolve Color](https://www.blackmagicdesign.com/products/davinciresolve/color) · [OpenColorIO CDL transform](https://opencolorio.readthedocs.io/en/v2.4.2/api/transforms.html)
- **Resolve LUTs** remain an option for more elaborate looks. The installed scripting README requires Resolve to have discovered a LUT before setting it. Preset portability would also depend on the LUT bytes, compatible input transform, and distribution rights.
- **FFmpeg and Remotion** can produce repeatable media and graphics renders through their CLI. FootagePilot already uses FFmpeg for preparation and measurement and Remotion for its narrated workflow. The travel-edit experiment benefits from the existing editable Resolve timeline. [FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html) · [Remotion render CLI](https://www.remotion.dev/docs/cli/render)
- **OpenTimelineIO** is a candidate if interchange between editors becomes a requirement. Its timeline model covers clips and transitions. Resolve Color and Fusion behavior would require separate adapter validation. [OpenTimelineIO timeline structure](https://opentimelineio.readthedocs.io/en/latest/tutorials/otio-timeline-structure.html)

The native App Store edition still requires an agent-operated Lua console and a workspace with access to the prepared media. See the measured results for the failed import and the recovery. [Resolve results](RESULTS.md)
