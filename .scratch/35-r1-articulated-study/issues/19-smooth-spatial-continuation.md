# R1 smooth-curve spatial-interface continuation

## Contract and ownership

- Owner: this implementation worker; one bounded leaf continuing the failed standalone `R.smooth` study, not a new garment/character shape hypothesis.
- Authority: Main's current continuation authorization: medium reasoning, at most 45 minutes of active work, every shell command <=120 seconds. No recursive delegation.
- Scope: create isolated source + evidence under `.scratch/35-r1-articulated-study/evidence/vendor-smooth-spatial/`; reuse only the already implemented R.smooth construction rule and existing support/depth/line-visibility interfaces. Do not change R1 author anchors, curve design assumptions, renderer/backend/source candidate, old evidence, docs/SSOT, append-only logs, vendor files, or R1 artwork.
- Provenance: prior worker's unchanged artifact is wrongly rooted at `evidence/vendor-smooth-study/` (rather than the authorized scratch). Retain it and its existing source/ticket/manifest/check bundle; record the path deviation, hashes and source attribution in the new isolated manifest. No move/delete/overwrite.
- R1 remains resource-blocked / unverified per issue 16. This technical follow-up cannot replace or pass the R1 goal and says nothing about future art/readability.

## Objective and acceptance

Produce a real project-local spatial rendering of a sparse semantic closed Catmull-Rom-to-cubic boundary, mapped through `SupportFrame -> world -> camera -> triangles -> existing bounded depth visibility`. Include a polygon-vs-generated-curve comparison from the same <=4 authored semantic coordinate inputs; no numeric-metric tuning or new shape hypothesis. The visible authored boundary line must consume the existing `visible_segment_spans` adapter, with generated spans and actual depth determining cuts. Do not stroke mesh triangles / duplicate all mesh seams.

Required source checks: curve segments share endpoint and C1 tangent directions at every knot including the closed seam; finite nonzero area; sampled closed curve is checked for proper self-intersections, touching nonadjacent edges, zero-length/degenerate edges and is rejected if invalid (not just an area assertion); authored semantic-coordinate count <=4; same-source deterministic rerender. Required numerical integration regressions: actual support/world/camera mapping and triangle depth ordering; an occluder changes curve/fill visibility without authored cuts; raw-vs-smooth variants retain the same semantics/parameters. Use an image-absent render path. Capture actual PNG + `scripts/draw check` bundle/report image list, source hashes and commands.

## Exclusions, gates and stop

No reference image/sealed content to engine, no reference-derived/copy geometry, no Huashu character/coordinates/frame/style, no author anchor edits, no curve-grammar experiments, no repeated parameter/shape polishing, no engine/backend changes, no dependency install/network/services, no staging/commit, no changes to existing source evidence or append-only files. No visual self-verdict or R1 completion claim. Preserve existing unstaged/staged state. Stop at 45 minutes or any required unsupported/unsafe interface; checkpoint actual evidence and unresolved items, never imply PASS from missing validation.

## Inputs and interfaces

- Historical mechanism source: `vendor/huashu-art-motion/scripts/engine/lib/rig.js::R.smooth` and example callsite `scripts/engine/scenes/36_picasso_blue.js`; transfer method only, no visual/coordinate reuse.
- Prior artifact/source: `evidence/vendor-smooth-study/{study.py,test_study.py,manifest.md,ticket.md,check/report.txt,study.svg}`; its limitations explicitly include standalone SVG and absent sampled self-intersection guard.
- Project architecture: `docs/drawing/spatial-model.md`; current code interfaces `scripts/articulated_construction.py::{SupportFrame,Camera,Component,component_faces,visible_scene_regions}`, `scripts/articulated_line_visibility.py::visible_segment_spans`, `scripts/vector_visibility.py::{visible_fragments,visible_regions}`. Engine/support source is read-only for this task.

## Revision-bound evidence location

Source, tests, actual rendered SVG and PNG, `draw check` bundle, manifest, and this task's evidence ticket live only in `.scratch/35-r1-articulated-study/evidence/vendor-smooth-spatial/` (ticket may be adjacent in `issues/19-...`). Final result must name checks, exact image list and any unrun independent appearance review. This is a narrow interface demonstration, not the full R1 acceptance package.

## Execution result

- Completed the spatial interface demonstration in this isolated directory. Four authored cloth landmark inputs feed both raw polygon and sampled Catmull/cubic shapes. The contour is mapped by `component_faces` through actual affine supports and orthographic projection, then by `visible_regions`/`visible_fragments` and `visible_segment_spans`; foreground sheet suppresses both fill and semantic boundary spans using depth. No mesh seams are inked.
- Self-checks: 8 isolated `unittest` regressions pass (C1 knot/seam equality, closed sampling, sampled self-crossing/touch/degeneracy rejection, four-coordinate input, support/world/camera/depth chain, order-independent occlusion, reduced visible fill and outline length, deterministic SVG, boundary-only ink). `scripts/draw check` and explicit PNG render both pass without `--ref`; the report's sole image is `check/draft.png`. See sibling `manifest.md` for hashes/commands and prior-path provenance.
- Old-path deviation: prior standalone source remains at repository-root `evidence/vendor-smooth-study/` unchanged; the corrected artifact is not a move/overwrite. Prior source, ticket, manifest, check report and PNG hashes are captured by the new manifest. The earlier study's standalone-render gap is resolved for this technical leaf, while its source remains preserved.
- Appearance/art judgment and independent visual review were not performed; the fresh reviewer image list is ready but no verdict is claimed. This does not implement or replace R1 A/B, does not change anchors/curve hypothesis, and R1 remains resource-blocked / unverified per issue 16.
- No project engine/backend/vendor/target source, task-frozen artwork, prior evidence, docs SSOT or append-only log was edited; no dependency/network/service/staging/commit action occurred. Existing staged `.gitmodules`, `vendor/huashu-art-motion`, and `vendor/huashu-design` entries were present at kickoff and remain untouched.
