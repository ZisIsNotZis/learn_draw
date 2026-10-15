# WP03/WP04 coordinate-chain repair ticket

Authority: Main/integrator explicitly authorized one bounded repair of the numerically confirmed cross-WP coordinate interface, thawing only WP03 support/camera convention and WP04 stroke mapping. No milestone change, new shape-rule assumption, sealed inputs, unrelated scope, append-only changes, staging, dependency/environment changes, or overwrite/deletion of failed evidence. Single writer: this worker, serial across both owners/seams.

## Interpretation and contract

Preserve semantic local component and stroke anchors. Every local point follows its owning support `local_to_world` → explicit camera horizontal/vertical/depth basis → panel fit. Camera vertical must agree with support local `v`; depth is independently world `z` so the existing bounded world-XY collision projection stays nonsingular. Keep two-view/case scene geometry, attachments/contact/baseline/variant/control semantic parameters unchanged. Art strokes remain semantic artwork, not depth-visible fill geometry/manual occlusion cuts; clip only as panel containment protection. Preserve old failed SVG/PNG/reports/hashes, and write replacement render/check/manifest in a new evidence directory only.

WP03 seam owner: Camera/support coordinate interface plus numerical axis, bbox, collision, and case tests. WP04 seam owner: named projected stroke mapping through support-camera-panel plus projected/emitted-anchor checks and panel clip. Scope excludes appearance judgment and R1/milestone acceptance.

## Acceptance and budget

Single repair pass, bounded unit/render/check commands (each ≤120s), total ≤40 minutes. Check orthogonal vertical/horizontal/depth sign projection, upright component bbox proportion, baseline/variant/control build-validation/attachments/contact and finite collision, stroke projection/emitted coordinates, clip/title containment, render all original panels and `scripts/draw check` against no reference. Record final hashes, tests, region coordinates, new-image-only reviewer list. Tests/render checks are self-evidence only; fresh review is required before downstream verdicts. Older WP05/WP06 PASS cannot be inherited after coordinate change. Do not call art or R1 PASS.

Initial repo status has extensive unrelated staged/unstaged/untracked work; preserve it. Existing failed evidence remains at `evidence/check*` unchanged.

## Result / proof boundary

Implemented world X horizontal / world Y up / world Z depth camera basis, retained support axes and XY collision contract, projected all semantic strokes through owning support and camera, and clipped only artwork content to panel interior. `python -m unittest scripts.tests.test_articulated_construction` PASS (15 tests). Baseline/variant/control each passed `validate_study_case`, produced 274 faces and visible fragments; torso bbox ratios 1.333/1.235/1.333, head 1.127. All three fresh `scripts/draw check` bundles passed; explicit rendered neckline anchor and clip containment assertions passed. New reviewer-only PNG list, hashes and source interface freeze are in `evidence/coordinate-repair-v1/render-manifest.md`.

Evidence exception: old PNGs/reports/hashes preserved; old manifest copied. Diagnosis-reported original failed SVG hash was not backed up before renderer regenerated outputs, so original SVG bytes cannot be preserved. Downstream WP05/WP06 require fresh review after coordinates change; no art/R1 verdict. Unrelated existing staged/dirty files remain untouched.
