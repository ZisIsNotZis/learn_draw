# WP03 construction self-check — implementation and interface frozen

## Scope, budget, and ownership

Continuation closes the incomplete implementation leaves from issue 07, not a new construction-rule hypothesis. R1's global two-distinct-hypothesis budget is unchanged; issue 05's prior prep cycle remains counted. This work retains semantic two-bone IK + generated taper. Sole edited project paths: `scripts/articulated_construction.py`, `scripts/tests/test_articulated_construction.py`, this WP03-owned check, WP03-owned `work/scene.yaml`, and the WP03 ticket. No WP04 artwork/render files, backend code, vendor files, source image/crop/reference/legal evidence, sealed heldout, unrelated evidence or append-only files were read/edited. No stage/commit/environment/service changes; pre-existing staged `.gitmodules` and vendor paths were preserved.

## Completed leaves

1. **World geometry and visibility adapter.** Semantic local outlines map through validated affine 3D support planes and camera projection. Simple concave contours (including sampled capped tapers) use deterministic ear clipping, not fan triangulation. `component_faces()` emits existing backend face tuples and `visible_scene()` / `visible_scene_regions()` call existing `vector_visibility` depth functions. No visibility intervals/cuts are input. Synthetic front/back reversal and order-invariance, plus actual scene projected depth spread, are tested.
2. **Collective semantic cases.** `build_study_case(case)` generates head, neck, torso, upper arm, forearm, hand, and prop with named support geometry, anchors and relation links. `validate_study_case()` verifies component completeness, anchors inside shapes, exact world-space attachment coincidence, declared semantic contact, fixed near-miss gap, bounded joint overlap radius, and rejects undeclared intersecting support planes in overlapping footprints. Baseline/variant/control render fixed `Camera()` (30° azimuth, 8° elevation); baseline uses authored raised-prop contact `(2.05,1.65)`, variant chest-rest contact `(2.00,1.45)` plus 1.08 torso-width factor, control offsets wrist by exactly `0.18*(1.65+1.35)=0.54` along final approach and has no prop attachment. Values are design inputs, not photo-derived. `work/scene.yaml` records stable interface and cases.
3. **Frozen interface and regression evidence.** WP04 seam is `build_study_case(name) -> StudyCase`; component local outlines/anchors/attachment links/support frames; `component_faces(components, camera)` emits `(projected_triangle, fill, component_id)` tuples accepted by `vector_visibility.visible_fragments`; `visible_scene` and `visible_scene_regions` expose geometry-derived results. Smoothstep profile regression checks exact widths at five parameter values and near-zero endpoint derivatives; capped contour closure/step bounds, support map, nonconvex tessellation area, depth ordering/reversal, scene determinism/contact/near-miss/collision validation are tested.

## Validation commands and source freeze

- `python -m unittest scripts.tests.test_articulated_construction`: passed, 13 tests.
- `.venv/bin/python -m unittest scripts.tests.test_articulated_construction scripts.tests.test_vector_visibility scripts.tests.test_vector_visibility_oracle`: passed, 36 tests. Existing visibility tests emitted two ResourceWarnings about unclosed temporary SVG reads; they passed and are outside this WP03 edit scope.
- `python -m compileall -q scripts/articulated_construction.py`: passed.
- `git diff --check -- scripts/articulated_construction.py scripts/tests/test_articulated_construction.py .scratch/35-r1-articulated-study/work/scene.yaml .scratch/35-r1-articulated-study/evidence/construction-self-check.md .scratch/35-r1-articulated-study/issues/07-wp03-world-binding-checkpoint.md`: passed.
- SHA-256 `scripts/articulated_construction.py`: `0d73b9614713f1ba6f67cf72519983b697f39371bc9bef1531a3f71689a5d793`.
- SHA-256 `scripts/tests/test_articulated_construction.py`: `87b8462c6523685de0d43822e8baffa6e4a492d0c466d2b7d4c9ef5914a3cbf7`.
- SHA-256 `work/scene.yaml`: `a7985a6e3ad0ee8d170ef930d8eab596fb6639ba96423c1312dfa3234b0ed491`.

## Boundaries / remaining R1 gates

WP03 geometry/interface is implemented and source-frozen, not rendered art. No artwork, reference imitation, engine image isolation rerender, visual review, qualified collision review, separate depth review, heldout compatibility/release, user feedback, or R1 acceptance is claimed. The affine plane model and bounded sampled polygon/plane checks are a compact structural interface, not full volumetric anatomy; WP05/WP06 independent review remains required before later gates. Existing visibility engine numerical/degeneracy limits remain as documented in the spatial model; this task did not patch the backend.
