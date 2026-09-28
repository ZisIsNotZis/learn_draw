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

`scripts/spatial_sketch.py` creates `.scratch/13-assembly/evidence/spatial-sketch.svg`: one continuous
2D-striped ribbon mapped to a 3D loop around a coarse torso, shown from two viewpoints. Its
triangle painter sort is only an approximate instructional sketch, **not** a proven exact vector
visibility engine or a reconstruction of `image.jpg`. Next: inspect it, test near/far ordering and
viewpoint changes, then choose an accurate visibility representation before migrating the assembly.
See the proof criteria and limits in `docs/drawing/spatial-model.md`.

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

Check the structural sketch's two views and its component connectivity; make a minimal test where
moving the camera changes which part of the *same* ribbon is occluded by the torso, with no visibility
flags. Fix painter-sort artifacts by designing/testing correct vector visibility rather than drawing
manual front/back paths. Only then add head, seated pose and hair-sheet supports and test comprehension
with a smaller VLM. The reference is a teacher, never a runtime dependency (P18).
