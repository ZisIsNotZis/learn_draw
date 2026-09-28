# Spatial drawing model — architecture SSOT

**Decision source:** user's clarification in the current session. This document owns the intended
component/depth architecture. `abstraction.md` describes the *current* 2D resolver;
`scene-format.md` describes the *current* renderer. Neither is the target architecture.

## Goal and boundary

An ordinary VLM should be able to compose a recognizable figure with roughly correct placement
and front/back relationships without manually drafting hundreds of coordinates or naming every
occlusion interval. Attractive line quality and colour are later problems. A reference illustration
teaches a scene, but neither the production engine nor its reference-free tests read that image.

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

## Bounded structural sketch / proof

Start with a simple torso/lap occluder, one continuous bent ribbon surface carrying a recognizable
2D stripe, and two camera views (reference-like and side/oblique). Input the entire strip ONCE.
`spatial_sketch.py` and `vector_visibility.py` now demonstrate this for tested opaque triangles;
`figure_scaffold.py` is a deliberately coarse S1 pose probe, not an approved reconstruction.
Passing proof: its near/far portions and the body's occlusion change automatically with viewpoint;
no per-view redraw, manually cut path, or visibility flags. Inspect the whole strip in an unobstructed
view and verify it stays connected in its own (u,v) domain. Then add a head-attached hair sheet with
blue outer and mint inner faces, and a coarse seated figure. Do not start with a detailed character.

Validation at each stage: inspect attachments, projected silhouette, crossings, generated depth and
object identities separately; ask a small VLM to describe pose, attachments and front/back on held-out
views before judging beauty. Record uncertainty where the reference cannot disambiguate depth.
Only after the sketch explains the layout should it inform the 2D assembly. Compare against
`image.jpg` for teaching, then render with that file unavailable (P18). No traced contours at
milestone exit (G7); a one-off fitted mesh alone is not transferable knowledge.

## Open design choices (not silently decided)

Exact support parameterization, line-art rules and how much of the existing 2D spec to migrate
require experiments. Whole-surface painter sorting is insufficient. The current SVG implementation
computes vector fragments from triangular depth planes, but does not yet handle every degeneracy,
intersection or performance case; triangle seam artefacts remain. Do not call that production-ready
or mistake the generic scaffold's ribbon route for the reference's intended route.
