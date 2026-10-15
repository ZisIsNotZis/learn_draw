# A cloth construction v2 — construction contract

**Status:** one newly authored A construction-family candidate; not A-art or R1 acceptance. No parameter search, pixel optimization, self-image judgment, teacher expansion, or B/heldout work is included. Thresholds below were frozen before the final construction tests and are topology/source-supported self-proofs, not visual-quality objectives.

## Observation and authority boundary

Inputs are the frozen root `image.jpg` (SHA-256 `322ad77c0cfd28fa040c625c55c592a54b3052ac4bea61fc31d967d8acff81fb`) and its registered `(500,320)-(900,800)` exclusive 400×480 crop (SHA-256 `52e01f5e75e5d98fcd9a0a4ac63be91ed09b8a18ca0f62e7e0348a021b2dd87d`). Crop-local coordinates are y-down; the scene adapter converts them to the existing y-up `Point` frame. The builder itself takes only `--out`, reads its local `semantic-parameters.json`, and has no reference, crop, trace, region, patch, RGB, landmark, or teacher path parameter.

- **Finite teacher-supported field/neighborhood evidence only:** neck skin `NS2` plus opening neighborhood `NO2`; unequal pale collar fields `CLI2`/`CRI2`; bodice field/visible-edge neighborhoods `BOL2`, `BPI2`, `BPI3`, `BHE2`; sleeve field `SPI2`/`SC2`, with `SBO2`/`SC3` only adjacency/approach; dark band interior `CU1`; bow gather/loop fields `BK1`, `BL1`, `BR1`, with `LFE2`/`RFE2` only local free-edge neighborhoods; downward strip interior `DTI2`; `TBE2` only a local pink-band station/edge neighborhood; `LTA2` only pink/blue contact neighborhood.
- **Forbidden/unknown:** original `N1`, `BD1`, `BD4`, `TD1`; `LTI2` as pink interior; the whole leftward-tail-centerline trace as a verified axis/width; `DTO2` terminal; exact boundary pixels, hidden closure/seam/armhole, full body hem/cuff circumference, hidden routes and blue-band identity. The pink local-band route/width and blue field do not claim teacher-resolved topology, and no attachment connects them.
- **Separate visible context:** the two small hair context roles are `visible_context`, seeded from crop observation, not added to the teacher garment whitelist: one neck curlband and one right-shoulder sheet. Their four authored center stations each are artist choices for only crop-local visible context; hidden endpoints, roots and depth are hypotheses. They cannot conceal or justify a wrong collar/body/sleeve construction. No face, full hair, hand, body pose, or full portrait is added.
- **Every non-observed construction value:** authored family hypothesis, including root/expansion stations, all width/profile/bend values, sleeve/bodice join, support depths, waist band, crop continuations, return folds, tail route and support, blue-band curvature/width/support/overlap, and hair closure/depth. The drawing is a reference-inspired construction hypothesis, not recovered true 3D.

## Causal chain and shape families

| named art layer | accepted observation/topology | low-dimensional family rule | support/contact and semantic line policy |
|---|---|---|---|
| neck skin / opening | NS2 skin field; NO2 is an opening neighborhood, not a boundary | shared Q and left/right collar-root stations define the lower opening; skin continues to a declared out-of-crop upper continuation, never a standalone rounded cap | skin is an actual `Component`; opening-edge/contact choice is authored, and hidden upper closure is `closure`, fill-only |
| left/right collar leaves and trim | CLI2/CRI2 are unequal pale fields; no exact endpoints/hidden seam | independent R-Q inner folded edge plus R-S-E outer free edge; finite local corner radius, edge tangent stays broken at fold station; each side is independent, not mirrored | `silhouette`, `free_edge`, `fold_edge`, `contact`, `closure` are distinct; dark trim is derived from each leaf's own Q→E edge, not the old U-line; closure is not automatically inked |
| bodice upper / waist band / continuation | BOL2/BPI2/BPI3/BHE2 support only local cloth fields and edge intervals; no complete hem | `C(t)=lerp(C0,Cw,t)`, normal cross sections, asymmetric `L/R` smoothstep+beta width field; Eleft constrains the left width at its projected axis station. Cross sections at t=.82/.88 derive a narrow band; continuation uses the same axis/section law to t=1.82 with closure below the crop | one shared support and exact section contacts; continuation is the only bodice part allowed to close outside the crop; no in-frame hem line or full hidden silhouette is asserted |
| continuous puff sleeve / transverse cuff | SPI2/SC2 continuous sleeve field, SC3 approach, CU1 band interior | parent-derived shoulder S and authored cuff approach C; `axis(t)=lerp(S,C,t)+skew*beta(t,2,2)n`; `r(t)=lerp(rs,rc,H(t))+fullness*beta(t,1.2,2.2)`; cap cubic protrudes along `-e`; short cuff sides derive from C/e/n | sleeve is one outline with no cap-to-tube seam; shoulder attaches to bodice at the shared generated S; cuff shares C, aligned support/world contact, and has transverse—not ellipse—band edges |
| bow gather and two loops | BK1/BL1/BR1 fields plus LFE2/RFE2 local free-edge neighborhoods | one short gather wrap at G; each unequal loop uses inherited G and one independent E, gather width g, free width W, bend and return indentation. Outbound free edge and return fold are separate formula-generated curves | gather/loop contact shares G; choose free/fold lines only; root closure is not an automatic artline |
| down-tail / local left pink band | DTI2 local interior; TBE2 local station/edge; LTA2 contact only | down-tail cubic tension centerline is generated from G/root tangent and gravity with below-crop continuation; local left strip is an explicitly artist-routed local band through the two observation neighborhoods, not a recovered trace | down strip is gathered at G; no tip is rendered inside crop. Left strip has no attachment to blue. Cross-support visibility is computed, not manually cut |
| anonymous blue band | LTA2 only identifies a local pink/blue contact neighborhood; blue identity unknown | broad C-like cubic strip has both ends outside crop and passes near the contact neighborhood; it is neither a balloon nor a closed local chip | separate `Component`, `attachments=()`; no pink attachment; complete support closure remains outside view and `closure` is not a line |
| neck curlband / right shoulder sheet | newly authorized, crop-local visible context only; not a garment whitelist extension | open cubic centerline and four-station scalar-width field per context piece | real support surfaces/depth; local overlap is an artist hypothesis, not a way to hide garment errors |

Generated sample vertices are compiler outputs, not an authored dense coordinate table. Each part carries a `FamilyGeometry` complete outline, named generated stations, typed edges with owner/intent, and the exact consumed direct coordinate inputs. Generated closed outlines go through `validate_closed_contour` and existing `triangulate_polygon`. Fills use `component_faces` + `visible_regions`; each selected authored/generated semantic edge is transformed through its owner's support and clipped with `visible_segment_spans` against the same faces. No hand visibility interval, alternate renderer, new engine or reference runtime path exists.

## Actual direct coordinate budget

The tests derive counts from `FamilyGeometry.authored_inputs`—the fields actually consumed by each generator—not `Component.anchors`. Parent-derived Q, collar roots, body cross-sections, shoulder S, bow gather G and band/cuff stations are labeled as inherited and are not counted twice.

| scene component | directly consumed crop coordinate inputs |
|---|---:|
| each collar wedge | 3 (R, S, E); Q inherited once from opening |
| neck skin | 1 (upper continuation); Q/R roots inherited |
| bodice upper | 3 (C0, Cw, Eleft); Q/roots inherited |
| waist band / bodice continuation | 0; both are generated from parent body sections |
| continuous sleeve | 1 (C); shoulder S inherited from bodice section |
| cuff | 0; derived from sleeve terminal section |
| bow gather | 1 (G) |
| each loop | 1 (E); G inherited |
| down tail | 0; root/tangent/destination derived from G and scalar force/length |
| local left pink band | 3 local neighborhood/exit stations, each explicitly an artist-hypothesis route input |
| anonymous blue band | 4 (two off-crop endpoints and two cubic controls) |
| each visible hair context | 4 centerline stations, with scalar width profile |

Artline-only fold cues each use at most three authored stations. No part exceeds four direct coordinate inputs.

## Frozen identity/self-proof thresholds

These tests are intentionally relational/topological, not metric fit scores:

- Shared opening Q equality is exact as a common source value; the three opening probes `(201,101)`, `(198,110)`, `(204,110)` remain in the skin candidate and outside both collar fields and bodice. Skin's generated upper continuation has y<0, so a closed in-frame neck ellipse cannot pass.
- Each wedge has a finite non-straight fold station (distinct incoming/outgoing directions), a visible Q→E edge-derived trim, and is not a full-cycle ellipse. The construction tests fail a rounded full-cycle outline that lacks the shared Q/free-edge/fold-corner behavior.
- Bodice action-axis `Δx/Δy` is between −0.35 and −0.12; upper/waist widths contract by construction. Waist and continuation joins are section-identical within `1e-8`; the continuation closure y>480. A visible closed bag bottom cannot pass.
- Sleeve peak radius is at least 1.08× the larger endpoint radius and occurs at t∈[.15,.65]; cap protrudes at least 20 px opposite action direction. Shared cuff center is exact and its cross-cuff edge has absolute direction dot sleeve tangent <.15. Taper-strip/capped-ellipse laws fail these family conditions.
- Each loop has `g/W <= .30`, a generated inward return and both turn signs; a convex ellipse cannot pass. Gather is a short wrap patch, not an oval knot.
- Tail tangent is nonzero/downward and passes within 18 px of DTI2 interior solely as a qualitative local seed; no terminal test treats DTO2 as a point. Blue route passes near LTA2 within 35 px as a broad neighborhood, has both support ends at x<0, has no pink attachment, and has no in-frame end cap.
- Every final part passes finiteness, closed-contour/self-intersection guard and triangulation. Attachment anchors map to the same world position within `1e-8`; all selected lines flow through depth spans. Runtime determinism is byte-checked in reproduction; only local parameters are read.

No threshold is changed in response to image metrics. No metric-driven or pixel-parameter sweep is permitted.
