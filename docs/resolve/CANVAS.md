# Reference-driven canvas and optional titles

Visual specs accept `aspect` (`9:16`, `16:9`, `1:1`, `4:5`) and boolean `show_titles`. Defaults remain portrait and titles enabled. The validated canvas reaches the visual compiler and native job instead of forcing 9:16. A disabled title is project metadata only: no native title layers are emitted, and a nonempty progressive title sequence rejects. Unused title duration may be zero; it is not validated as a visible effect.

```json
{"aspect":"16:9","show_titles":false}
```

Keep the existing reference, assets, timing/music and duration fields, then use `recreate --backend resolve`. `aspect` controls output geometry, not source orientation. There is no automatic rotation, subject tracking or reframing guarantee. Portrait sources can need severe landscape crops; inspect subjects and framing. A reference encoded sideways in a portrait container can inspire an upright landscape adaptation, but the output is not an exact orientation/frame match. The brief must distinguish the intended presentation from encoded dimensions.

The second local reference had full-frame travel imagery encoded sideways, varied shot holds and no observed title/collage sequence in extracted samples. That exposed two prior assumptions: mandatory portrait output and a forced title. The added controls express that direction without removing titles or collages from other projects. Existing footage limits still apply: this does not invent drone shots, spins, speed ramps or colour grading.

Research checked 12 November 2026: Blackmagic’s [Editor’s Guide to Resolve18](https://documents.blackmagicdesign.com/UserManuals/DaVinci-Resolve-18-Editors-Guide.pdf), “Reformatting a Timeline for Different Aspect Ratios,” describes timeline resolution presets/custom dimensions and vertical inversion. This older manual informs the canvas model; actual installed 21.2 export evidence establishes runtime behavior. The [21.1 announcement](https://www.blackmagicdesign.com/media/partial/release/20260908-03) also distinguishes source-viewer aspect from timeline orientation. Recheck after app changes; reading a guide does not establish crop quality. Prior native portrait trials and the current landscape trial are documented in RESULTS.md; square/4:5 are accepted dimensions, not new live claims in this trial.

Optional `min_shots`/`max_shots` constrain both the model schema and compiler (integers 2–30, inclusive and ordered; defaults 2/30). Counts control edit density, not semantic distinction or musical quality. Duration and source-window constraints still apply. Infeasible requests fail rather than silently relaxing a budget.
