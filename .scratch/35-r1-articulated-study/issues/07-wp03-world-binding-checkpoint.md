# Ticket — WP03 world binding and scene interface

## Authority, remaining budget, and ownership

This ticket records completion of the previously incomplete WP03 implementation after review. It continues the already selected IK/taper method; no new rule hypothesis was opened. R1's two-distinct-hypothesis budget is unchanged, with issue 05's code-preparation cycle already counted. P1 from the independent review was incompleteness, not a method rejection; P2 was a missing quantitative smoothness assertion, now covered by regression tests.

Exclusive edited WP03 paths: `scripts/articulated_construction.py`, `scripts/tests/test_articulated_construction.py`, `work/scene.yaml`, `evidence/construction-self-check.md`, and this ticket. WP04 artwork/render files, backend, vendor, image/crop/reference/legal evidence, sealed heldout, unrelated/pre-existing evidence, and append-only facts were not edited. All commands were bounded to 120 seconds. No staging, commits, environment/service use, or dirty-tree cleanup. Pre-existing staged `.gitmodules` and vendor paths were preserved.

## Implementation and source choices

- Keep semantic two-bone IK and generated smoothstep taper with sampled semicircular caps. `taper_profile()` makes the width law directly testable. Regression asserts exact values at `t=0,.25,.5,.75,1`, endpoint slopes near zero, contour closure and bounded sample step. No authored long contour or vendor character coordinates/art/frames.
- `SupportFrame.local_to_world()` maps local coordinates through actual origin and two axes. Camera projection creates `(x,y,depth)` triangles from triangulated world geometry. Nonconvex contours use bounded deterministic ear clipping and reject non-simple input rather than fan triangulating.
- `component_faces`, `visible_scene`, and `visible_scene_regions` feed the existing opaque triangle depth implementation. Depth reversal and face-order invariance are tested. No manually authored visibility cuts, backend changes or pixel tuning.
- Scene API/cases: `build_study_case("baseline"|"variant"|"control")` emits head/neck/torso/upper_arm/forearm/hand/prop components with named local anchors, support frames and relation links. `validate_study_case()` checks shape anchor membership, exact linked world coordinates, successful contact, near-miss separation, joint-overlap radius <=0.90 local units, and nonattached support-plane intersections over overlapping XY footprints. Frozen details and handoff API live in `work/scene.yaml`.
- Baseline/variant/control use fixed azimuth 30°, elevation 8°. Variant changes contact semantic and torso width to 1.08× baseline. Control wrist offset is exactly 0.18×(1.65+1.35)=0.54 along final approach; it has no hand/prop attachment and retains a positive gap. Values are authored design choices, not reference observations.

## Validation and artifact hashes

- `python -m unittest scripts.tests.test_articulated_construction`: 13 passed.
- `.venv/bin/python -m unittest scripts.tests.test_articulated_construction scripts.tests.test_vector_visibility scripts.tests.test_vector_visibility_oracle`: 36 passed; two existing ResourceWarnings in raster-test helpers noted in self-check.
- `python -m compileall -q scripts/articulated_construction.py`: passed.
- `git diff --check -- scripts/articulated_construction.py scripts/tests/test_articulated_construction.py .scratch/35-r1-articulated-study/work/scene.yaml .scratch/35-r1-articulated-study/evidence/construction-self-check.md .scratch/35-r1-articulated-study/issues/07-wp03-world-binding-checkpoint.md`: passed.
- Final immutable SHA-256 values are recorded in `evidence/construction-self-check.md` and configured handoff report.

## Completion boundary

WP03 geometry and the stable WP04 source interface are implemented and frozen. Independent WP05 construction/contact/collision review, WP06 depth review, WP04 authored artwork/render, and all reference/art/heldout/user gates remain separate and unpassed. No future art or R1 PASS is implied. The scene contract is a compact set of generated planar support surfaces with bounded collision tests, not full volumetric anatomy; reviewers should assess the stated interface and limitations.
