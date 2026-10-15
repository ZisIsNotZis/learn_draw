# Spatial drawing model — architecture SSOT

**Decision source:** user's clarification in the current session. This document owns the intended
component/depth architecture. `abstraction.md` describes the *current* 2D resolver;
`scene-format.md` describes the *current* renderer. Neither is the target architecture.

## Goal and boundary

This architecture supports the learning goal in [`roadmap.md`](roadmap.md): progress from reference
study and imitation through variation/transfer toward bounded reference-free original creation. A
useful capability is recognizable components with plausible attachments and front/back relationships
without manually drafting hundreds of coordinates or naming occlusion intervals; that capability
alone is not an artwork milestone. Models may read images but output text/code only: no native
image/video generation or generated sprites may substitute for constructing components. A reference
teaches, but neither runtime geometry nor reference-free tests read it. Roadmap owns milestones and
vendor learning; unavailable actual visual evidence leaves its gate open. Runtime repair is not a
product goal.

**Component = 2D artwork + a support surface in 3D.** The artwork has its own local 2D coordinates
(u, v), outline and interior marks. The support may be a plane or a curved surface; a camera projects
its painted points into the final canvas. Components remain separately editable. A ribbon is one
continuous strip in its local coordinates, even when its support bends back and forth through depth.

The scene declares component attachment and coarse spatial relations (e.g. bow on chest; ribbon
loops around body), not manually clipped visible paths. **The engine** projects components, compares
depth at overlaps and hides covered portions. A ribbon vanishes because another surface is physically
closer to the camera there; it reappears wherever it is closer again. No author-provided
`visible_ranges`, back/front copy, or paint-layer split is required. Transparent materials and
intersections need explicit later treatment; this first contract is for opaque surfaces.

## Representations and responsibilities

| stage | input / output | responsibility |
| --- | --- | --- |
| Component author | named 2D artwork in (u,v), local attachment points | identity, shape, intentional interior marks; no frame coordinates or occlusion cuts |
| Spatial scaffold | camera, simple body volumes, plane/curved supports, attachment constraints | plausible depth and pose; not photorealistic anatomy |
| Projector / visibility | transformed surfaces and artwork → projected visible regions | depth testing, self-occlusion, crossings and disappearance/reappearance; deterministic |
| Line-art designer | visible projected boundaries + object semantics | chooses external contour, contact/overlap line, fold/colour boundary, or omitted edge; 3D edges alone are NOT finished line art |
| Colour / style | visible authored regions | palette and finish, after structural acceptance |

The existing `layers:` and `front/behind` relations are temporary **global painter ordering**. They
cannot resolve alternating depth along the same ribbon or two crossing surfaces. Preserve them for
legacy drawings; do not present them as the new visibility engine. P17 in `principles.md` records the
old workaround, not the target contract.

## Minimum scene schema to prove, not yet implemented

- `camera`: orthographic initially, matching the reference's framing; perspective optional later.
- `body`: a few pose volumes/surfaces (head, torso, skirt/lap), with scale and attach points.
- `component`: `artwork`, `surface`, `attachment`, optional `material` and semantic edge types.
- `surface`: plane, curved strip or coarse mesh parameterized continuously by (u,v), including
  thickness/backside where relevant; the 2D art does **not** become a set of independent pieces.
- `visibility`: generated from projected surface depth, including self-occlusion and body occlusion;
  provenance links each visible fragment back to its original component and (u,v) interval.

Geometry and depth may be approximate; **topology and attachment must be correct first**. A single
stylized image cannot uniquely determine 3D, so the scaffold is a testable interpretation, not
recovered ground truth. The final 2D line designer may deliberately depart from the projection.

## Historical S0/S1 sketch and assembly sequence (archival; not current workflow)

The former S0 technical exercise used a simple torso/lap occluder, one continuous bent ribbon
surface with a recognizable 2D stripe, and two camera views (reference-like and side/oblique); its
input represented the whole strip once. The retained `spatial_sketch.py` and `vector_visibility.py`
artifacts demonstrate bounded opaque-triangle visibility cases. `figure_scaffold.py` was a coarse S1
pose probe, not an approved reconstruction. Its technical success condition was automatic near/far
visibility change with viewpoint, no per-view redraw/manual visibility cuts, and preservation of the
strip's local `(u,v)` continuity. The historical sequence proposed adding a two-sided hair sheet and
coarse seated figure next, and cautioned against detailed character work at that stage. This records
the old technical sketch and its limited evidence; it is not a current R1 prerequisite, completed art
milestone, or direction to expand the old scaffold.

The associated former validation plan asked for separate attachment, projected silhouette,
crossing, generated-depth and object-identity inspection, plus small-VLM descriptions on held-out
views; it then proposed using the sketch to inform the legacy 2D assembly. That workflow is archival:
it does **not** authorize automatic progression from sketch to assembly, and it does not establish a
small-VLM, S1a readability, learner-transfer, or user-art acceptance pass. Record ambiguity about
reference-derived depth rather than claim unique recovered 3D truth. For current milestone work,
follow [`roadmap.md`](roadmap.md) and its linked concrete R1 contract for package ordering and gates;
actual-image readability/art review and user feedback remain separate, explicit gates. The spatial
architecture described above remains current: components are 2D art on support surfaces and engine
depth determines visibility. Reference is a teacher, not runtime geometry; retain compact,
explainable authored construction rather than traced contours or a one-off fitted mesh.

## Open design choices (not silently decided)

Exact support parameterization, line-art rules and how much of the existing 2D spec to migrate
require experiments. Whole-surface painter sorting is insufficient. The current SVG implementation
computes vector fragments from triangular depth planes, but does not yet handle every degeneracy,
intersection or performance case; triangle seam artefacts remain. Do not call that production-ready
or mistake the generic scaffold's ribbon route for the reference's intended route.
