# Visibility fragmentation study — scratch candidate result

## Scope and disposition

This is a bounded upstream diagnostic for the `.scratch/22-visibility-fragmentation/spec.md` S1a continuation. Canonical `scripts/vector_visibility.py`, historical tests/plans/images, art, learner, and docs were not edited. The candidate is an isolated copy for evaluation only; parent integration, provenance changes, full camber rerender, and the visual gate remain pending. No S0/S1a/art/readability claim is made.

## Cause supported by geometry and browser output

The canonical resolver enters `subtract_convex` when projected triangle **bounding boxes** overlap, even if the two triangle interiors have zero-area intersection. On the generated planar `4x3` fractional mesh, 12 face pairs pass that bbox gate while sharing only edges. A representative pair is faces 0/1: both bboxes are `[31.25,27.375,62.375,58.5]`; the triangle interiors touch only along `(31.25,27.375)`–`(62.375,58.5)`. Equal depth plus existing tie bias submits one whole triangle as a cutter. `line_clip`'s existing EPS then yields repeated-vertex, zero-area polygons at `(62.375,58.5)` and `(31.25,27.375)`; this is actual fragment output, not merely a white-speckle interpretation.

On the generated mesh, canonical returns 48 fragments for 24 input faces, including 24 zero-area pieces; the isolated candidate returns 24 and the same compound path and Chromium pixels as the 24 source triangles. Canonical differs at four 1-level partially covered silhouette pixels on the last row/column. This minimized case demonstrates the touching/cut/raster interaction, not the full interior defect by itself.

The fixed fine96x12 parent arch independently reproduces the interior effect with matching geometry, camera, view, fit and barycentric depth mask: source raw compound fill has 0 nonmatching pixels in the 8,495 safe interior samples; canonical resolution has 44; candidate has 0. None are background-colour holes; the sampled deviations are within 0.42 px of an internal projected mesh edge. Canonical emits 29,464 polygons (20,472 zero-area, 201 positive polygons with area <=1e-10, 334 <=1e-7) and 8,992 serialized paths; candidate emits 9,681 polygons (5,151 zero-area, 23 <=1e-10, 24 <=1e-7) and 4,530 paths. Candidate total polygon area tracks source to floating summation precision. It does not suppress all subdivision: the remaining fragments include actual positive-area depth visibility.

## Candidate rule and safety

`work/vector_visibility_candidate.py` adds one strict SAT positive-area triangle-intersection gate after the existing bbox fast rejection. Edge-only/point-only contacts are excluded; any represented positive interval overlap on all triangle-edge axes is retained. Existing depth planes, interpolated cuts, tie bias, grouping, serialization, opaque API, and order are unchanged. No tolerance/precision sweep, hidden-surface expansion, stroke, blur, painter reorder, component/self skip, or per-image mask is used.

Scratch regressions cover bbox-overlapping edge contact versus a tiny positive-area overlap; the generated mesh Chromium negative control; crossing/changing depth and declaration reversal away from ties; same-component self-occlusion; unchanged first-declared exact coplanar tie; and camera-dependent real ring/body occlusion. The candidate retains camera-dependent occlusion (strip visible-area fractions: yaw 0 = 0.8699601; yaw 55 = 0.7559248).

## Existing-suite result and known incompatibility

The explicit candidate-import run exercised 68 tests across the relevant historical vector-visibility, ribbon-family, support-surface, ribbon-drawing and spatial-sketch suites, plus five new scratch tests. 67 passed. One historical exact-area check failed: `test_same_whole_strip_updates_visibility_in_two_cameras` expects yaw-55 fraction `.7968 ± .01`; candidate yields `.7559248` (difference `-.0408752`). Its yaw-0 expectation and camera-difference assertion pass. The scratch camera regression confirms camera-dependent self-occlusion remains, but this material change in a prior reference value needs independent parent review; historical source/test was not changed.

## Browser/check artifacts

- `evidence/fine/study.json` records fixed source/plan/canonical/candidate hashes, deterministic repeated candidate PNG hash, full source/current/candidate raster counts, fragment areas/vertices and near-edge locations.
- `evidence/fine/minimal-4x3-{source,canonical,candidate}.{svg,png}` are the computed small geometry and actual Chromium outputs.
- `evidence/fine/arch-{source,canonical,candidate}.{svg,png}` are exact-geometry source/current/candidate images; candidate repeat PNG is byte-identical.
- Labelled and unlabelled three-panel boards are `evidence/fine/arch-labelled.png` and `arch-unlabelled.png`. Reference-free draw-check bundles are `evidence/check-labelled/report.txt` and `evidence/check-unlabelled/report.txt`; each report's exact image list is its `draft.png` only.

## Next gate

Do not integrate from this worker result alone. Fresh independent review must resolve the changed oblique ring-area assertion and inspect these actual image lists. Only the parent may then decide whether the candidate is acceptable for canonical integration and rerun the broader approved validation. No full support matrix or learner was rebuilt here.
