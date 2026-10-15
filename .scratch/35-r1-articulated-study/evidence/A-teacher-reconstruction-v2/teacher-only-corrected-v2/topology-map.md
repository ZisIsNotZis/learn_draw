# A-only teacher reconstruction v2 — corrected source-visible evidence map

**Gate:** `NOT RUN / NOT PASS` — fresh semantic review required. This current v2 evidence package supersedes the v1 corrected sibling for rebuild/provenance consistency only; it does not revise any prior gate or accept artwork. Analysis evidence only; no fit, final-art render, or runtime geometry.

**Correction:** Independent review contradicts `LTI2` crop `(104,222)` / source `(604,542)` as pink interior (pale clothing). It is typed `unknown` and excluded from fit. The whole `leftward-tail-centerline-visible` trace is withdrawn as source-backed centerline/width/axis, including `(116,220)` / source `(616,540)`. Retain only qualitative leftward pink-band presence and pink/blue contact at `LTA2`; no endpoint or blue identity is inferred. See [`fit-correction.md`](fit-correction.md) for explicit whitelist/forbidden fields. `teacher-overlay.png` is regenerated evidence visualization, not final art; withdrawn LTI2 is unknown-styled and the withdrawn whole left-tail centerline is not drawn.

## Authority and input integrity

Main's current scope is narrower than the historical teacher PASS. Required independent visual source: `/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/6662b1a6-2806-4bc7-adfd-3eef79ef311b/r1/teacher-landmark-independent-crosscheck.md`. Required numeric context: [`numeric-audit.json`](../../A-teacher-landmark-audit-v1/numeric-audit.json), [`numeric-audit.csv`](../../A-teacher-landmark-audit-v1/numeric-audit.csv), and [`findings.md`](../../A-teacher-landmark-audit-v1/findings.md). The cross-model review is the semantic role authority; the numeric audit is registration/neighborhood evidence only.

- Source `image.jpg`: SHA-256 `322ad77c0cfd28fa040c625c55c592a54b3052ac4bea61fc31d967d8acff81fb`, 1024×1024 RGB.
- Source rectangle `(500,320)-(900,800)` with exclusive upper bound; output [`pristine-fullcrop.png`](pristine-fullcrop.png) is 400×480 and exact source pixels, SHA-256 `52e01f5e75e5d98fcd9a0a4ac63be91ed09b8a18ca0f62e7e0348a021b2dd87d`.
- Every crop point `(x,y)` maps to source `(500+x,320+y)`. `rebuild_teacher_evidence.py` (in this v2 package; not the historical teacher writer) reopens `image.jpg`, recomputes the crop, checks every RGB byte against the preserved old registered crop, verifies both hashes, emits point RGB plus 8 local neighbor samples at ±3 pixels, and exports raw unscaled pixel patches with hashes. Re-run command is recorded in issue 42.
- [`teacher-overlay.png`](teacher-overlay.png) enlarges the exact crop 2× for annotation. Its boxes indicate review windows only; labels locate samples; open dashed strokes are rough, manual teacher pointers over visible intervals. None is a mask, complete boundary, or fit geometry.

## What the point evidence means

[`landmarks.csv`](landmarks.csv) gives point type, crop/source pair, point RGB, raw 11×11 patch path/hash, observation limit and lineage. [`landmarks-and-neighbors.json`](landmarks-and-neighbors.json) adds exact eight-neighbor samples (3 px offsets); these numerics allow lookup/contrast checks, **not identity-by-color**. A semantic reading is a contextual visual claim about the full source crop and its neighbor geometry, not a frequency or isolated ROI verdict. [`raw-regions/`](raw-regions/) contains four unresampled contextual windows and each matching crop/source bound/hash is in [`regions.json`](regions.json). [`raw-patches/`](raw-patches/) contains each individual source-pixel point patch. Automated segmentation was unstable/unnecessary and is not represented as achieved; approximate open polylines in [`manual-traces.json`](manual-traces.json) are labeled teacher annotations with explicit visible-interval/unknown stops.

Types:
- `interior`: this sample is within a visibly identified colored/material field; not a contour anchor.
- `boundary-neighborhood`: nearby source pixels show a visible edge/transition neighborhood; not an exact shared-boundary coordinate.
- `adjacency-neighborhood`: two or more objects/fields meet or occlude nearby; not a seam/contact geometry assertion.
- `unknown`: location is supplied only to point to ambiguous overlap/terminal context; no geometry/role is asserted there.

## Reconstructed visible topology, with limits

1. **Neck and collar opening.** New `NS2` points inside the visible pink neck field; new `NO2` locates only the lower opening/termination neighborhood. The pink field lies between partial lower face/hair and the pale collar surfaces, but its full anatomical boundary is obscured. New `CLI2` and `CRI2` are distinct pale field samples; the leaves are visibly unequal. No symmetry, hidden attachment, full neck contour, or exact collar endpoints are derived. Dark curved collar trim is an observed transition, not proof of internal leaf seams.
2. **Bodice.** New `BOL2` marks a locally visible exposed left torso silhouette interval and `BPI2`/`BPI3` sample visible pale cloth. Supported old `BD3` (`SEED-BD3`) remains only a pale torso field observation; nearby lines stay fold/unknown. New `BHE2` and open trace identify a source-visible lower edge interval inside the crop; portions are overlapped/continued by other forms, so this is not a complete hem or evidence for crop-cut garment termination. The visible cloth is narrower through the lower torso than across the shoulder/chest region and its exposed left edge shifts inward with descent; exact full silhouette and any hidden right/armhole boundary are not recoverable here.
3. **Right sleeve/cuff.** New `SPI2` and supported `SC2` sample one visually continuous pale sleeve field from rounded upper mass toward the narrower lower approach. `SBO2`/supported `SC3` are adjacency/approach neighborhoods only. `CU1` is a visible dark band field. No source-visible cap-to-tube seam is asserted; far cuff circumference and covered sleeve side are unknown. Visible free silhouette intervals are locally reviewable but partially hidden by hair/background; no hidden arm anatomy or precise band geometry is invented.
4. **Bow and tails.** Supported `BK1`, `BL1`, and `BR1` remain gather/loop-field seeds. New `LFE2`/`RFE2` point to short visible loop-edge neighborhoods, not closed contours. `LTI2` is WITHDRAWN: its sample is pale clothing, not pink strip interior. The entire `leftward-tail-centerline-visible` trace is WITHDRAWN as source-backed centerline, width or axis (including `(116,220)`); it is historical only. Retain only the qualitative leftward pink-band presence and contact/overlap neighborhood `LTA2`; whether pink ends, continues under/behind, and what the blue band represents are unknown. `TBE2` supports a local pink-band station and edge neighborhood only, not an exact edge coordinate. `DTI2` samples the downward pink strip. `DTO2` is `unknown`: no point-tip or crop/hem claim. No hidden knot wraps or remote continuation.

## Disposition of all v1 landmarks and claims

The v1 19-point CSV remains byte-preserved, but these former roles do not carry an inherited semantic PASS into future fits:

| Legacy ID / old role | Current disposition |
|---|---|
| N1 neck-skin interior | **WITHDRAWN — contradicted.** Its location is blue hair/outline neighborhood; not skin. New `NS2` is separately observed and has its own patch; it is not a repaired/relabelled N1. |
| N2 opening low point | Retain only visible lower-opening neighborhood; exact shared-boundary pixel is unknown. |
| CL1 left collar outer point | Retain outer-edge neighborhood only; exact leaf endpoint/attachment unknown. |
| CL2 left leaf lower/front point | **WITHDRAWN — UNKNOWN.** Old point does not establish left-leaf identity. New `CLI2` is a separately verified interior sample. |
| CR1 right collar leaf interior | Retain right pale collar-field observation only; no internal seam. |
| CR2 outer/trim transition | Retain trim-transition neighborhood; no hidden outer continuation. |
| BD1 pale exposed shoulder | **WITHDRAWN — contradicted.** Old point is background. New `BOL2`/`BPI2` carry separate source-backed contour/field evidence. |
| BD2 shoulder/sleeve attachment | **WITHDRAWN — UNKNOWN.** No isolated armhole or seam evidence. |
| BD3 right bodice patch | Retain pale torso-cloth interior only; crease/seam uncertain. |
| BD4 lower waist/edge | **WITHDRAWN — contradicted.** Old point is background. New `BHE2` marks a different visible in-crop lower-edge neighborhood only. |
| SC1 sleeve-cap exterior | **WITHDRAWN — UNKNOWN.** Old point is hair/garment occlusion neighborhood, not a verified cap start. New `SPI2` is an interior sample; `SBO2` is adjacency only. |
| SC2 right sleeve interior | Retain continuous pale sleeve-field evidence only; not cap/tube split. |
| SC3 sleeve/cuff approach | Retain cuff-approach neighborhood only; exact outer edge unknown. |
| CU1 cuff band | Retain visible dark band interior only; far side/full circumference unknown. |
| BK1 knot center | Retain pink gathered/overlap neighborhood; not hidden knot construction. |
| BL1 left loop interior | Retain visible lobe field only; no exact width/outline from this point. |
| BR1 right loop interior | Retain visible lobe field only; no precise width ratio or exact outline. |
| TL1 tail/band zone | Retain contact/overlap neighborhood only; no pink endpoint/continuation or blue-band identity. |
| TD1 visible tail tip | **WITHDRAWN — contradicted.** Down-tail existence is supported, but its terminal type/location is UNKNOWN (`DTO2`); no inherited “tip” claim. |

Consequently, the old broad teacher PASS does **not** support any of these specific claims anymore: N1 skin interior, BD1 exposed bodice at its marked point, BD4 lower waist edge at its marked point, TD1 tapering to a visible point, CL2 left-leaf ownership, BD2 sleeve/bodice seam/attachment, or SC1 sleeve-cap exterior start. Even unchallenged supported points only support their limited field/neighborhood roles above, not exact shape boundaries.

## Unknowns explicitly carried forward

- No neck anatomy beyond the visible patch, full neckline contour, hidden collar join, or symmetric leaves.
- No sleeve cap seam, armhole seam, shared seam that cannot be seen, or hidden garment/sleeve continuation.
- No complete bodice silhouette or crop-external hem. The lower visible line is an in-crop edge neighborhood, not a crop boundary interpreted as a garment edge.
- No precise loop width ratio from isolated interiors; no hidden bow wrap.
- No blue-band identity, pink left-tail endpoint/continuation, or down-tail exact terminal/tip.
- No subpixel boundary claim. Where raw patches plus source context leave object/edge ambiguous, preserve `unknown` instead of substituting a nearby label.

The original package PASS is not repaired or retroactively rewritten. Current fit eligibility is only the explicit whitelist in [`fit-correction.md`](fit-correction.md); unknowns remain unknown and artist parameterization must not be inherited as source facts. The fresh semantic gate remains `NOT RUN / NOT PASS`. Numeric hashes, sample RGB, raw patch existence, and annotations do not self-qualify it.
