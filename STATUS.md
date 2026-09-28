# STATUS — current project state

**Architecture SSOT:** [`docs/drawing/spatial-model.md`](docs/drawing/spatial-model.md).
**Goal:** an ordinary VLM composes a recognizable, roughly correctly placed figure using separate
2D-art components supported by 3D planes/curves; the engine computes occlusion from depth. Line
beauty and colour come later. The current SVG resolver does **not** implement this architecture.

## State

- The user says the hair in M4j is **much better**. The ribbon is conceptually continuous, but its
  position is wrong. No further 2D anchor adjustment is authorized by that observation.
- Current 2D assembly: `.scratch/13-assembly/work/spec.yaml`; M4j render:
  `.scratch/13-assembly/evidence/m4j-final.png` (commit `bf5f4d5`). It is a study artifact, not an
  accepted final drawing. The global `layers` and `front/behind` workaround currently splits the
  ribbon into front/back pieces: it is **not** the intended automatic depth engine.
- Historical best/ratchet: `.scratch/00-tooling/baseline/`; promotion still requires the applicable
  visual gate. No promotion was made for M4j. Metric alarms are not drawing objectives.
- M3 body rubric exited previously; M4 is open. Do not infer that the previous milestone sequence
  validates the new spatial architecture. `docs/drawing/roadmap.md` owns forward gates.
- The user explicitly corrected the architecture: each component is independently drawn in 2D on
  a plane or 3D-curved support; the renderer determines visibility using actual component depths.
  The model **must not** manually label where a ribbon disappears/reappears.

## Current experiment

**S0 geometry proof implemented (not an art gate):** `scripts/vector_visibility.py` projects
opaque triangles, clips overlap by their *interpolated depth planes*, and outputs surviving SVG
polygons. Tests cover opposite declaration orders, a crossing whose depth changes inside one
triangle, strip closure and a viewpoint change. `scripts/spatial_sketch.py` renders the same
unbroken 2D-striped ring around a torso in two views:
`.scratch/13-assembly/evidence/spatial-sketch.svg` / `.png`. No author visibility intervals.
This is a slow reference implementation, not a production-quality renderer: SVG anti-alias cracks
at triangle seams and intersecting/coplanar surfaces still need harder tests.

**S1 exploratory figure:** `scripts/figure_scaffold.py` creates two views of a coarse seated
figure, head-attached hair sheet, bow and one continuous ribbon. Preview:
`.scratch/13-assembly/evidence/figure-scaffold.png`. Bow/ribbon contact and geometric strip closure
have tests. The pose and ribbon route are *hypotheses*, not a fit to `image.jpg`. Hair now uses a
single twisting support whose projected face orientation chooses blue vs mint; this is a real
two-sided *mechanism*, but its twist/layout are **not yet validated against the reference**. No
independent visual reviewer or small-VLM comprehension gate has passed. Do not call the figure
accepted or migrate it into the 2D assembly yet. The triangle mesh is visible in the preview;
line art remains unsolved.

## Source map

- **Product/architecture decision:** `docs/drawing/spatial-model.md` (canonical)
- **Forward milestones/gates:** `docs/drawing/roadmap.md`
- **Current 2D implementation contracts:** `docs/drawing/abstraction.md`, `scene-format.md`,
  `vocabulary.md` (legacy where they contradict the spatial model)
- **Method and transferable observations:** `docs/drawing/method.md`, `principles.md`
- **Iteration evidence:** `.scratch/13-assembly/log.md`; archival former status including D1–D33:
  `docs/drawing/history/status-before-spatial-model.md` (**historical, not current instructions**)
- `docs/drawing/handoff-3d.md` is a superseded interpretation; read the spatial model instead.

## Next executable step

Finish S1 by verifying image-layout and attachments against `image.jpg`, assessing the current
two-sided sheet's *shape* (rather than its merely functioning orientation rule), and testing
small-VLM comprehension on the two views. Resolve triangle seam artifacts in the vector SVG
without masking real occlusion errors. The **ribbon's correct route is still unknown**; do not
claim that this generic elliptical scaffold solved the user's specific placement complaint.
The reference is a teacher, never a runtime dependency (P18).
