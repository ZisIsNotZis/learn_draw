# Roadmap — spatial drawing, then line art

`STATUS.md` owns the current state. [`spatial-model.md`](spatial-model.md) owns the component/depth
architecture. This file owns forward milestones and acceptance, not historical iteration details.
The original M0–M5 record survives in `history/status-before-spatial-model.md` and
`.scratch/13-assembly/log.md`; it is not a license to claim the new architecture works.

## Goal and non-negotiables

A smaller, ordinary VLM should compose a recognizable, approximately placed person with plausible
occlusion using **2D artwork per component on 3D plane/curve supports**. The engine, not the author,
computes which portions are visible. Separate structural correctness from pleasing line design,
colour and texture. The final spec must render without the reference (P18); provenance and
transferability matter more than a copied contour. The reference may teach values but not serve as
runtime geometry. Preserve unrelated work and the recorded best; no automatic promotion on metrics.

## Gates common to experiments

- **Topology:** each named component remains connected in its local 2D domain; attachment points
  and near/far crossings are explained. No arbitrary split art or manual visibility intervals.
- **Visibility:** change camera or geometry and verify that covered portions update automatically.
  Check self-occlusion, crossing and re-emergence against independently chosen cases. Painter
  ordering of whole components does not pass.
- **Reference-free/deterministic:** render with `image.jpg` unavailable twice and compare outputs.
  No trace-derived final shapes at milestone exit (G7); distinguish sketch-proven concepts from a
  learned transferable family.
- **Perception:** inspect structure with labelled views/depth diagnostics, then ask sight-proven
  fresh reviewers (including smaller VLMs) to identify the figure and front/back relations. Treat
  reviewer locations as hypotheses to verify; user feedback is authoritative on intended design.
  Pixel metrics are breakage/omission alarms, not targets.
- **Claims:** a clean resolver or a high score cannot prove readability. Keep the former 2D
  baseline as a comparison artifact, not a gate that forces spatial sketches to imitate finished art.

## S0 — Structural proof (CURRENT)

One uncut 2D ribbon on a 3D curved support, one torso/lap occluder and two cameras. The
reference implementation `scripts/vector_visibility.py` clips projected SVG polygons at the
interpolated depth intersection (not whole-triangle painter sorting). Tests cover both paint orders
and a crossing whose depth flips inside a triangle; `spatial_sketch.py` exercises two views of the
same complete strip. **S0 proof met for tested opaque triangles**, not certified for all tangencies,
intersections or production-scale scenes. No finished character or attractive line quality required.

## S1 — Coarse figure layout

Add head/torso/arms/skirt as coarse supported components, a head-attached hair sheet whose blue/mint
faces are two sides of one sheet, and a continuous ribbon around the figure. A first rough figure
exists in `scripts/figure_scaffold.py`; its hair sheet *does* twist and choose blue/mint from
projected face orientation, but its shape has not been validated, and the ribbon route is not
reference-faithful. Match major attachment,
scale, pose, projected silhouette and negative spaces of `image.jpg` without manually painting
occlusion. **Exit:** two reviewers can identify a person and the main front/back relations; test
camera variation and reference-free reproduction. Compare with M4j as historical evidence, not a
requirement to preserve its guessed ribbon placement.

## S2 — Line-art design

Extract candidate visible contours, contact and fold/colour boundaries from the spatial scene, then
apply explicit **artistic** line selection/weight/curve rules. A mesh's every edge is not a line.
**Exit:** line-only renders read correctly without colour and without a depth-debug overlay; the
same object does not acquire accidental seams merely because its support is tessellated.

## S3 — Colour, style and withdrawal

Paint the components in their local 2D coordinates; style visible line/fill output. Test another
pose/subject, then a reference-free prompt with a smaller VLM. **Exit:** structural correctness
transfers beyond the original target, followed by visual review of finish. Whole-artifact baseline
promotion remains a separate blind preference decision, never a metric optimization.

## Stop conditions

Park rather than guess if (1) expression requires a flood of manual coordinates or visibility
exceptions, (2) the next change cannot be justified structurally, or (3) reviewers cannot see or
resolve the relevant distinction. Record artifact, evidence, blocker and next experiment in `STATUS.md`.
