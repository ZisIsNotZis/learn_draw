# 8_DETAIL — module internals: coordinate and transform conventions, generator mechanics, the resolver tier ladder, diagnostics

This file owns the inside of a module. It does not own the formats those modules produce (`7_INTERFACE.md`),
the language they serve (`5_PRODUCT.md`), or the commands that run them (`9_IMPLEMENTATION.md`).

# INFERRED

## Head expression and inspection

The head's expression preset changes brows, mouth and optional eye-lid factors in the existing eye
generator. Gentle keeps its original values; a raised lower lid makes a curved smiling aperture,
and curiosity coordinates the raised brow with a more open eye. Bounds reject lid crossings. Head
containment clips iris/pupil/glints to the resulting aperture. Feature guides include the real lash
band as well as the sclera: the aperture alone omitted the moving outer wing in a locality check.
Gaze is conjugate in head-local horizontal space. These controls do not change the head support.
Magnified viewboxes can extend outside the document. A separate neutral opaque workspace fills that
margin while the original paper rectangle still marks the canvas; transparent pixels previously
appeared black in the image viewer and obscured that distinction. Normal artwork is unchanged.

## Scenic support and opaque artwork

`scripts/studio/components.py` dispatches the implemented flat recipes and supplies their depth
anchor/scale. `scenery.py` creates a sky gradient and deterministic subordinate stars; hills sample
two low-frequency harmonics into three filled ridges. Their support is the union of those polygons.
Optional foreground pines derive their feet from the actual near ridge, so horizon/relief changes
cannot detach them. Their crown/trunk unions join the hill's opaque support.
The crescent is a circle minus an offset circle, then tilted about its center; fullness changes the
offset. A sun unions its attached ray crown with the disc. Its support follows the actual outline,
preserving transparent space between tips under exact visibility clipping. Geometry is computed from
semantic controls, never seeded by a reference or hidden bitmap. These recipes are replaceable art
choices, not universal physical models. Object moves alter relative placement and preserve shape.

## Editable lock implementation

`scripts/studio/geometry.py` sweeps a smooth gesture from a semantic frame anchor. A continuous
root/fullness/tip width field gives a rounded narrow root, broad upper-middle and convergent tip.
Generated boundary samples support compact cosine-window pushes. Both the push and its first
derivative vanish at the influence boundary; endpoints remain outside the interval. Tone regions
interpolate the edited left/right boundaries, so they follow local changes without separate patching.
Sampled section orientation and proper segment-intersection checks reject clear collapses/crossings.

`render.py` triangulates the generated outline with the existing articulated-construction utility.
It assigns planar depth and calls the existing `vector_visibility.visible_regions`; visible union
paths become clips for fill, designed tonal regions and contour ink. Mesh diagonals are never ink.
Larger depth is closer. Coplanar overlaps retain the existing engine's deterministic tie behavior;
avoid relying on ties to describe spatial order. Finite stroke width is clipped within its owner.

`model.py` validates inputs and binds selection/preview to canonical JSON SHA256. Accept stores the
previous scene under `<scene-stem>.history/` and appends the operation journal. Individual file writes
replace a temporary file atomically. Multi-file accept/undo is not crash-transactional; no claim of
process-kill recovery is made yet. Undo detects external scene edits and hash damage.

`head.py` is the sole frontal-head recipe; the old example script is a thin reproduction wrapper.
It reuses legacy face/eye generation, preserves the accepted style, unions same-material front hair,
and applies aperture clips. Artwork curves are explicit recipe choices. A sampled opaque footprint
and namespaced SVG form the planar component. Semantic feature paths and child-lock rows provide
selection locations; parent 2D tilt is inverted when converting a screen-direction child push.

The renderer proves a global order only for the current planar families whose complete linear depth
intervals do not overlap. Vertex extrema establish that conservative condition. It paints those
components in derived depth order, preserving ordinary vector antialiasing; no authored order or
visibility cut is consumed. Crossing intervals use the existing triangle depth engine. Its regions
are reused across unchanged full/alignment/crop views. Tests include a crossing-plane negative case,
two heads with independent clip IDs, and actual raster checks. This shortcut is not used for curved
or wrapping surfaces. A scene view begins with an empty in-progress report so failed rasterization
cannot advertise a stale image list as current.

## Coordinate and transform conventions

`frame.w`/`frame.h` size the canvas and the resolver's SVG is `viewBox="0 0 w h"`: a coordinate is a
frame pixel, x right, y down. Angles are screen degrees — 0 right, 90 down. `rot` turns a shape about
its own centre. Resolution runs in declaration order into one environment of absolute
`<id>.<handle>` values later nodes read; painting is a second pass. Language is `5_PRODUCT.md`'s,
format `7_INTERFACE.md`'s.

## Generators (`wave`, `strands`, `ring`)

Generated nodes replace hand-placed stroke fragments (P15: generate from parameters) and are the
engine, not the teacher: needing no reference, they survive the image being deleted, so they are
preferred for anything regular. Field lists are `7_INTERFACE.md`'s; mechanics are here. Tuning knobs
are per-node parameters; never hand-edit generated output.

- `wave` resamples the spine to 40 points by arc length, displaces each perpendicular by
  `amp`·sin(2π · arc-fraction · chord/`len`), droops it in +y by `sag` × 100 × progress along x, and
  closes the ribbon path, width constant or tapered to nothing at `end` or `both`.
- `strands` draws `n` seeded strokes: start uniform inside `region`, direction `dir` ± `spread`,
  length `len` × U(0.8, 1.2), width `w` × U(1−`wj`, 1+`wj`), a quadratic bow, an ink cycling through
  the `ink` list.
- `ring` slices an annulus arc into `nseg` filled segments, walking hue `h0`→`h1`; the outer edge is
  a triangle wave with tooth index floor(angle·`zn`/2π) and depth `zig`·`w`, jittered per tooth from
  `seed`; both depend on absolute angle only: two complementary arcs sharing geometry and `seed`
  meet teeth-aligned, a z-plane split, not a path split.

All deterministic: same scene, same bytes, covered by `scripts/tests/test_scene.py` (placement,
determinism, unknown-key refusal).

## Resolver tier ladder (`T1`–`T4`)

- **`T1` line art** — the `stroke` node: a stroked path, no fill. Its hardest sub-skill is spatial
  relationship — occlusion, where a curve terminates — with unexplainable diff hints (invariant 3).
  The reference has no uniform black line art: only 12.6% of its pixels sit below gray 95, and the
  figure reads from flat-colour boundaries plus compact dark regions, so structure comes from region
  decomposition and traced boundaries, a stroke on the boundary that matters; XDoG extraction is a
  dead end here (P10: it turns anime interiors into noise). Evidence:
  `.scratch/05-portrait-scene/evidence/diagnosis/`.
- **`T2` flat colour** — `fill` on a shape, swatches from a k-means palette of the reference.
- **`T3` soft fields** — gradients, blurred blobs, opacity. Available: the layered flat blob under a
  shared silhouette, painted bottom-up, every layer nameable. The clipping-mask idiom — hard
  silhouette clip, blurred blobs inside, `mix-blend-mode` — is absent from the back end (no
  `clipPath`, no blend mode), so a spec must not need it. Soft fields come last (rung 12). The scene
  format carries all three (`grad`, `blur`, `op`); the resolver emits `op` and no `<defs>`, so
  gradients and blur need `scene_render.py`.
- **`T4` photo realism** — stacked blurred-blob decomposition, feathered silhouettes, texture.
  Research tier: it needs field-decomposition tooling (gradient direction and extent hints) no module
  provides; not scheduled.

## Diagnostics

A model cannot check whether a number is off-canvas, so the resolver reports facts as sentences:

- `OFF-CANVAS` / `CLIPPED` — the resolved box lies entirely outside the frame or crosses its edge,
  with coordinates.
- `SUB-PIXEL` — under 3 px in either dimension: invisible.
- `CONTRADICTION` — a declared `relations:` intent (`front: hat, behind: hair`) disagrees with the
  `layers` order of the legacy 2D resolver, not geometric depth testing; one node with no layer
  gives `UNKNOWN-Z` instead.
- `TEACHER` — geometry computed from the reference raster: legal while the reference is open,
  forbidden in a reference-free spec (P18).
- anchor table (`--anchors`) — every resolved handle.

Silence is the informative case: no note means intent and paint order agree.

## Studio hand construction and numerical scope

scripts/studio/hand.py uses separate knuckle locations and computed phalanges. A C1 Hermite
centerline carries a continuous width field and rounded terminal cap. Palm, short wrist, opposed
thumb and fingers form one union with small soft-tissue closing; creases are intentional clipped
art lines, not mesh edges. Collision above the palm host refuses a pose that would fuse free fingers.
Disconnected polygons/holes are refused; choosing the largest component is not a repair.

All construction inputs use a 0.0001 palm-unit precision grid before union/closing. This removes
subgrid numerical chips, not real gaps. The mechanism follows the official
[Shapely set_precision contract](https://shapely.readthedocs.io/en/stable/reference/shapely.set_precision.html).
A fixed nominal ruler prevents edited extents from changing every other feature's placement.
Screen tip motion is inverted through handedness, tilt and anisotropic width; a similarity about
the selected knuckle yields length and lean, which are validated before rendering.

Untouched digit geometry/knuckles are exact invariants. A shared outline can be re-tessellated after
a local union, producing subpixel contour/antialias differences away from the selected finger.
The regression bounds nonlocal contour displacement by the construction grid; it does not promise
byte-identical unrelated pixels within the same skin shape. The initial exact-pixel assumption was
withdrawn after diagnosis, rather than patched with pixel-specific code.
