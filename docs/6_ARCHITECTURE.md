# 6_ARCHITECTURE — subsystem boundaries, support surfaces, the visibility principle, and the open design choices

This file owns the intended component/depth architecture: what a component is, what the engine
computes, which subsystem carries which responsibility, the minimum scene schema still to be proved,
and what remains an open design choice. Decision source: the person's clarification of the target architecture.

It does not own formats, algorithms or commands: the compiled node format, the spec fields that cross
a boundary and the renderer contract are `docs/7_INTERFACE.md`; relation resolution, materialization,
visibility clipping, generators and coordinate conventions are `docs/8_DETAIL.md`; the toolchain,
commands and record areas are `docs/9_IMPLEMENTATION.md`; milestones and gates are `docs/0_ROADMAP.md`;
why the work matters is `docs/1_PROBLEM.md`. What the author can express is `docs/5_PRODUCT.md`. The
current 2D resolver and renderer are not this architecture.

# EXPLICIT

## Current editing boundary — 2026-11-12

Keep component artwork, support/depth, line selection and colour distinct. Add an author-facing
editing layer that selects stable semantic features, exposes compiled geometry in an alignment view,
applies local operations and binds preview/accept/undo to exact scene revisions. Direct 2D contour
editing and spatial routing are different operations. A simple planar support is sufficient for the
first editable part; it does not establish curved support, attachment or whole-figure capability.
Existing `vector_visibility.py` remains the depth authority. Optional 3D construction guides are a
future drawing aid, not an immediate replacement for authored vector shapes.

## Component, support surface, engine

**Component = 2D artwork + a support surface in 3D.** The artwork has its own local 2D coordinates
(u, v), outline and interior marks. The support may be a plane or a curved surface; a camera projects
its painted points into the final canvas. Components remain separately editable. A ribbon is one
continuous strip in its local coordinates, even when its support bends back and forth through depth.

The scene declares component attachment and coarse spatial relations (bow on chest; ribbon loops
around body), not manually clipped visible paths. **The engine** projects components, compares depth at
overlaps and hides covered portions. A ribbon vanishes because another surface is physically closer to
the camera there; it reappears wherever it is closer again. No author-provided `visible_ranges`,
back/front copy, or paint-layer split is required. Transparent materials and intersections need
explicit later treatment; this first contract is for opaque surfaces.

# INFERRED

## Goal and boundary

This architecture supports the learning goal: progress from reference study and imitation through
variation/transfer toward bounded reference-free original creation. A useful capability is
recognizable components with plausible attachments and front/back relationships without manually
drafting hundreds of coordinates or naming occlusion intervals; that capability alone is not an
artwork milestone. Models may read images but output text/code only: no native image/video generation
or generated sprites may substitute for constructing components. A reference teaches, but neither
runtime geometry nor reference-free tests read it. `docs/0_ROADMAP.md` owns the milestones; `docs/5_PRODUCT.md`
owns which vendor methods are adopted, in its curriculum coverage; unavailable actual visual evidence leaves its gate open. Runtime repair is not a product
goal.

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
legacy drawings; do not present them as the new visibility engine. `P17` in
`docs/3_REQUIREMENT.md` records the old workaround, not the target contract.

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

## The visibility implementation today

A bounded structural sketch (`scripts/spatial_sketch.py`) places one continuous striped ribbon
around a coarse torso and projects two viewpoints. It uses approximate triangle painter sorting, not
an exact vector visibility implementation. It does not reproduce the target portrait.

## Open design choices (not silently decided)

Exact support parameterization, line-art rules and how much of the existing 2D spec to migrate
require experiments. Whole-surface painter sorting is insufficient. The current SVG implementation
computes vector fragments from triangular depth planes, but does not yet handle every degeneracy,
intersection or performance case; triangle seam artefacts remain. It is not production-ready, and the
generic scaffold's ribbon route is not the reference's intended route.

## Adopted projected mount boundary — 2026-11-13

The Studio now resolves an authored single-parent pin graph into an ephemeral placement copy before
component rendering, selection, crop/depth analysis and report generation. Nodes expose only known
geometry-derived mounts. The relation preserves one projected point with optional normal inset and
screen offset; angle, size and depth remain independent. It is not the full spatial joint/solid
contract above. Missing targets/cycles are refused, and node-level compilation requires resolved
input to prevent nominal positions masquerading as current geometry. Interface and algorithms are
owned by 7_INTERFACE and 8_DETAIL. The independent cactus and parent-edit studies are indexed at
../evidence/studio-attachment/README.md; their contour/art limitations remain open.

## Editable gesture and feature mounts

Studio stroke construction owns a sampled analytic centerline and a normal-width paint strip,
with round/flat caps and optional material colour plane. It reuses component depth projection;
true depth crossings continue through the vector visibility solver. A colour plane is authored
artwork, not a new illumination solver or an inferred physical fold.

Head chin and hand wrist mounts come from the actual component construction. Shape side@fraction
mounts interpolate nominal boundary stations and outward normals continuously. The author inspects
that exact address before pinning a child; the graph still derives placement only. Selection crops
follow the proposed edited feature while the candidate remains bound to the original selection.
Detailed schema/algorithms and validity checks remain in 7_INTERFACE and 8_DETAIL.

## Stroke endpoint dependency graph

The legacy mount graph remains one parent per whole-object pin. Stroke endpoints add up to two
named target dependencies within the same acyclic resolver. Raw constraints remain semantic; the
compiler derives root placement and the two-target chord without feeding absolute coordinates
back into authoring. Selection, depth compilation and reports consume that resolved copy.
Deletion traverses both links and releases only affected endpoints by baking the current chord.
The source/target visual inspection and optimistic transaction boundary remain unchanged.
