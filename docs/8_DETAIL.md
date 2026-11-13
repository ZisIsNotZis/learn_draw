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

The renderer proves a global order for the current planar families by checking complete linear
depth intervals and painted projections. Vertex extrema bound each depth interval. Every pair with
overlapping depth intervals must have disjoint painted projections; all potentially overlapping
pairs are checked, not just neighboring intervals. Disjoint projections commute, so two separate
parts can share a support plane without unnecessary self-clipping. Components paint in derived
depth order, preserving ordinary vector antialiasing; no authored order or visibility cut is
consumed. Unresolved overlapping projections/depths use the existing triangle depth engine. Its regions
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

## Generic editable mass

scripts/studio/shape.py constructs a superellipse in a named nominal rectangle, optionally tapered
by a linear width field. Four named quadrant arcs are resampled by their nominal arc length;
an angular parameter alone produced a nonuniform edit footprint on square-like forms. Each arc
has 64 stations, 256 total; the closed mass is computed, not hand-specified contour coordinates.
Subsequent compact cosine edits retain their nominal arc coordinates instead of moving old handles
when the bounds change. Screen moves are inverted to shape-local displacement and applied through
the object's rotation at compile time. Adjacent arc joins and nonselected stations remain exact.

The painted footprint is the filled polygon plus half the explicit outline width. This lets the
existing depth machinery occlude both fill and ink correctly. Local edits retain one simple
polygon; self-intersection/collapse refuses the proposal. This contour editor deliberately offers
fewer degrees of freedom than SVG path editing; it currently has no holes, arbitrary corner
insertion, booleans between scene objects or articulated attachment.

## Independent flat-fill defect and renderer proof boundary

The grouped-creation rocket exposed 24 nonuniform pixels more than two pixels inside the visible
right fin, despite an untextured flat fill. Both disjoint fins had depth -1. The previous interval
check forced all components through a compound triangle clip mask; a separately proved noncrossing
render removed every diagnosed interior fleck without changing the scene. The conservative order
proof now admits disjoint projections even when depth intervals overlap. The regression fails
before this change and passes after it; a second raster case checks a real nonadjacent depth crossing.
This avoids unnecessary compound-mask raster seams for the proved noncrossing class. It does not
establish that all genuinely intersecting clip masks are free of numerical/antialias artifacts.
Original author output, source snapshot, coordinate/color facts and clean-render comparison are
retained in evidence/studio-parameters/. No geometry, depth or pixel-specific repair is authored.

## Derived placement without feeding compiler coordinates back into authoring

attachment.py resolves the single-parent graph after intrinsic typed geometry validation. A child
is compiled at its nominal free placement to locate its self mount, then translated by the target
mount difference and optional normal inset/screen offset. The relation is removed only from the
compiler copy and replaced with a computed at. Parent resolution is recursive, cached per traversal,
order-independent and cycle-checked. Shapes expose nominal-arc midpoint anchors on current sculpted
boundaries; the local tangent gives an outward normal and the paint point includes half the ink.
The source midpoint and tangent stations of a pinned edge are protected during local pushes.

Selection, drawing, crop extents, scene faces, depth order and reports resolve the same raw scene.
Hand-tip inversion uses the resolved hand before writing semantic digits back to the raw node.
Detaching copies its computed free placement, retaining the rendered image. Parent edits may move
related descendants; there is no implicit angle/size inheritance or material union. Early joint
measurements show why this boundary matters: the old lamp elbow already overlaps, and the old
cliff footing already rests on the top patch. Their volume/join critiques are not placement-gap
proof. Actual figures and images are retained in evidence/studio-attachment/.

## Gesture geometry and a colour plane

stroke.py adapts the established swept-normal strip method (legacy relate.ribbon/taper_band) with
a quadratic nominal gesture, analytic tangent and analytic compact-cosine edit derivative. This
keeps both terminals, widths and all stations outside influence fixed during local pushes. It
uses the existing Row/window/path conventions, not a new coordinate authoring language. Thickness
is independent of chord length. Smoothstep width interpolation has zero endpoint derivative;
round semicircular caps therefore join smoothly even under optional taper. Invalid/self-crossing
paint and ink cavities are refused. The default is an unshaded round capsule.

A side colour plane follows the generated spine, one boundary and matching cap halves over the
same full fill. It is graphic colour organization, not lighting or a physical fold solver. Ink
is a separate explicit outer path. Its footprint includes the actual half-ink buffer for depth.
Endpoint movement solves the new chord while retaining the opposite world endpoint, then writes
only semantic length/angle and a computed free root or retained attachment. Head chin comes from
intersection with its semantic face median; choosing an incidental lowest sampled vertex shifted
that mount off-axis and failed the new check. Hand wrist reuses its existing construction constant.

Positioned shape mounts interpolate between generated arc stations and interpolate the tangent
normal. This removes hidden quantization without changing default midpoint mounts. Inspecting one
exact address and candidate-region cropping make its actual action visible. Free-text XML failure
was reproduced before centralizing safe comment construction; raw author intent remains intact.

## Removal with retained descendant placement

The compiler resolves the complete old graph before deletion. Default removal bakes only surviving
direct children's derived free placements; their intrinsic geometry and deeper raw relations remain
unchanged. Cascade computes the transitive closure independently of author order. The operation
keeps the original inspection binding, plus ordered impact IDs and union bounds of removed paint.
Preview guides read removed outlines from the original resolved scene and retained children from
the new resolved scene, while clean artwork compiles only the candidate. Empty node lists take the
normal background-only depth fast path, requiring no synthetic invisible placeholder object.

An actual reuse probe exposed operation-only guide metadata leaking into a later proposal: after
declining removal, parameter editing could retain the old deletion labels; an attachment preview
could similarly retain its old target during a different operation. current_selection now rejects
these impact views as new inspections. The original inspected selection remains usable at the same
base. This is a provenance correction, not a geometric change. The pre-fix failure and the exact
creator source are retained in evidence/studio-removal/.

## Endpoint graph resolution

The resolver visits both endpoint target dependencies before compiling a stroke, using the same
cycle stack as legacy attachment. Each target point uses actual generated mount geometry, normal
inset and retained screen offset. With one pin the intrinsic gesture translates unchanged. With
two, the endpoint difference yields chord length and atan2(dx,dy) angle; root placement and those
values exist only in the compiler copy. Geometry validation runs on that resolved stroke. Node-level
compilation refuses unresolved endpoint input rather than quietly using nominal coordinates.

Screen-direction spine pushes use the resolved chord angle, preserving their material-axis meaning
under target motion. Release/deletion bake the resolved chord before removing links, so a surviving
pin reconstructs the same world geometry. Reports and selection filters hide derived controls.
Depth clipping remains unchanged; projected endpoint equality is not 3D contact or fluid physics.

## Compact illustrative grip construction

scripts/studio/grip.py builds a rounded palm/wrist, four short capsule pads and a bent thumb from
a hand ruler. A three-joint Hermite gesture supplies the thumb; no generated vertices are author
inputs. Width changes skin, while handle span/thickness remain separate controls. Constant-depth
surface subtraction decides internal visibility. Fold ink drops isolated sub-pad fragments and
omits the tissue-root seam; the exterior obeys the same visibility as fills. Placement, mirror
and screen angle transform shapes, focus, mounts and normals together about a stable host point.
The actual union must stay one valid solid polygon and both handle ends must remain exposed.
Compiled dimensions report wrist/handle widths for matching adjacent authored strokes.

Pending placement (studio/placement.py) copies the validated base, appends exactly one preset,
applies exposed semantic changes together, then resolves optional screen correction or observed
mount attachment. Revision validates readiness, engine/base/result and an exact canonical remainder
after removing the added id. The final anchor impact view is bound to the working base for rendering
and acceptance. It has no old contour because that object is absent from the working base; compare
separate pending previews to inspect successive corrections. Rendering completion precedes ready.
