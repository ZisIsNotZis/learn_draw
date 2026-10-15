# WP03 scoped geometry repair

## Interpretation, scope, proof

Authorized one scoped repair cycle for construction overlap validation and triangulation coverage. Preserve R1 geometry/contact acceptance; this is not full volumetric-solid validation. No sealed material, renderer/backend changes, reference search, staged/committed files, or edits to prior evidence.

### Independent evidence disposition

- WP05 BLOCK: accepted. `scripts/articulated_construction.py::_overlap_samples` missed identical/coincident and collinear overlaps; undeclared coplanar pairs could pass. WP05 specifically verified validator attachment behavior and warned collision scope is not full solid legality. Repair exact contour overlap and disclose planar scope.
- WP06 BLOCK: accepted for triangulation test gaps and actual support-based depth. Triangulation is now checked for coverage, pairwise interior disjointness and orientation, including reverse winding, concavity and invalid input. `depth_ref` is historical opaque metadata: code uses `SupportFrame.origin/u_axis/v_axis` in `local_to_world`, then camera projection produces actual depth; scene contract `work/scene.yaml` states this as `depth_rule` and coordinate flow. Therefore no duplicate depth registry/truth added; metadata alone does not produce visibility.

## Implemented and validated

- Polygon overlap now uses positive-area intersections of triangulated boundaries, detecting identical, contained and partial collinear overlap while allowing shared-edge-only contact.
- Validation transforms each outline into shared world XY before overlap checks, reconstructs each support's world Z there, and fails closed when its projection into XY is singular. Scope is explicitly planar support-surface intersection, not volumetric solids or arbitrary 3D frames.
- Existing declared attachment overlap radius remains in force; samples/anchors are compared in common world XY. It is not a claim of unrestricted penetration.
- `triangulate_polygon` rejects non-simple contours. Tests cover concavity, reversed winding, coverage, area, pairwise interior disjointness, orientation, self-crossing and zero-area inputs.
- `depth_ref` remains an opaque, non-resolved label. Actual depth is derived from mapped world vertex z and camera projection (`component_faces`); `visible_scene` supplies resulting depth-bearing triangles to existing opaque visibility backend. No duplicate depth binding is introduced.

Commands: `python -m unittest scripts.tests.test_articulated_construction` PASS (14 tests); direct baseline/variant/control build+validate+component_faces+visible_scene PASS (274 faces each; visible fragments 1177/1202/1193 respectively); `git diff --check -- scripts/articulated_construction.py scripts/tests/test_articulated_construction.py .scratch/35-r1-articulated-study/issues/08-wp03-scoped-geometry-repair.md` PASS.

Frozen interfaces/self-check SHA-256: `scripts/articulated_construction.py` `70dc400036cad0a7f695d30a4ca8bc6799307311e35f2291553f5c0f134aa7f4`; `scripts/tests/test_articulated_construction.py` `7d9b4f2a472869f0b0252f814824c88aa122012a59d257a3c5ff8fb6d62aca24`.

## Acceptance boundary

WP03 scoped overlap/triangulation code checks PASS. This is not whole WP05 physical-solid PASS, WP06 independently reviewed depth PASS, rendered art PASS, or R1 PASS. Depth adapter implementation/test is present, but independent WP06 verdict remains BLOCK pending review of repair. Whole-object collision reasoning remains limited to simple contours and common XY-projectable planar support surfaces; no general 3D solid collision guarantee. Existing worktree has unrelated pre-existing staged `.gitmodules` and vendor entries; this repair did not stage or alter them.
