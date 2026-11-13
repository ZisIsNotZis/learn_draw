# 7_INTERFACE — the contracts that cross a boundary: the compiled node format, the traced-data sidecar, the renderer and explainability contracts

This file owns exact shapes — field names, file formats, error strings and renderer guarantees. It does not
own why the language is designed as it is (`5_PRODUCT.md`), how any of it is computed (`8_DETAIL.md`), or
the commands that write it (`9_IMPLEMENTATION.md`).

# INFERRED

## Studio-1 scene and edit contract

The current editable slice is `python -m scripts.studio`. Scene `format` is
`learn-draw/studio-1`; `canvas` defaults to [640,640], `background` to warm paper, `nodes` is required.
Each node requires `id`, `kind` (`stroke`, `shape`, `head`, `hand`, `hair-lock`, `sky`, `hills`, `moon`, `sun`), `intent`.
`new --kind landscape` instantiates sky and hills on a 960×640 canvas; `add --kind moon` adds a
celestial preset. Insertion is journaled and undoable. Existing names are never overwritten.
`new --size WIDTHxHEIGHT --background '#rrggbb'` optionally sets the canvas and paper at creation.
Every object selection exposes `intent` as a text control. Stock intent describes the component's
purpose without duplicating mutable colour or hairstyle values; custom author intent is never
silently rewritten when changing a parameter.
Foreground insertion (`add --kind head|hand|hair-lock|shape|stroke`) starts on a plane beyond the existing
components' maximum support depth. `--depth NUMBER` overrides it. Scenic kinds retain their semantic
background/celestial defaults. Insertion and explicit depth edits remain undoable; visibility still
comes from support depth rather than the node list.

### Hand — front-view open-palm preset

`new hand.json --kind hand` requires no path points. This is a simple flat cartoon palm with four
knuckle-based long fingers and an opposed thumb; it is not a general 3D hand/closed-grip model.

| field | meaning / default |
| --- | --- |
| at | nominal open-hand box center: {anchor: center, offset: [0,0]} |
| length / width | .64 of shorter canvas dimension / 1 horizontal proportion |
| angle | 0; same 2D tilt convention as the head, positive toward right along the downward axis |
| handedness | right (thumb on the viewer's left before tilt); alternative left |
| spread | 1; long-finger fan, .25–1.6 |
| digits | optional index/middle/ring/little/thumb objects with length multiplier (.7–1.25) and lean (−12..12°) |
| palette | optional skin, ink, crease; skin changes derive a related crease tone |
| depth / depth_slope | 0 / 0, linear support anchored at nominal center |

Inspect `object` for placement, scale, handedness, spread, palette and depth. Inspect a named digit
for `finger_length` / `finger_lean`, or simply use `preview --move left --amount .04` on that digit.
The white handle is the center of its fingertip pad; the green knuckle remains fixed. Amount is a
fraction of the selected digit's nominal span. Screen-direction moves are inverted through tilt,
mirror and width before computing length/lean, so the author need not calculate joint angles.
Digit numeric lean is head-on hand-local; screen moves are preferable when that distinction matters.

The nominal ruler does not recenter when a finger changes. Other digits' compiled geometry stays
fixed. The shared skin contour uses a declared construction precision; exact pixel identity of
its antialiasing is not promised across an edit. Intersecting free fingers are refused for this open
pose rather than merged into a misleading shape. Root/tip protection of lock-edge pushes is a
different operation: a hand's tip handle is deliberately movable, with its knuckle protected.
The orange isolated-digit guide includes its buried root; it is not an extra line in clean artwork.

### Scenic presets and composition

All scenic objects select `object`; they expose semantic controls rather than editable path points.

| kind | defaults and optional controls |
| --- | --- |
| sky | dusk (or day); seeded stars, seed, top_color, bottom_color, stars_color; depth −20 |
| hills | three smooth receding ridges; horizon .64, relief .11, seed 4, far/middle/near_color; optional trees (0–5), tree_scale .18, tree_side left/right; depth 10 |
| moon | upper_right plus [0,.10], diameter .22 of shorter canvas dimension, angle −20, fullness .42, fill_color; depth 0 |
| sun | same placement, diameter .20, angle 0, 12 attached rays, fill_color/rays_color; depth 0 |

Fullness is a graphic crescent-width control (.08–1), not an astronomical phase model. Sun rays
belong to its actual connected opaque silhouette; no invisible bounding disc masks their gaps.
Hills' support is the union of actual ridge polygons. Celestial visibility behind hills follows
support depth independently of node-list order. A sky is opaque, not a transparent gradient overlay.
Styles supply related defaults; explicit palette/star overrides remain deliberate overrides.
Sky/hills allow depth_slope; their length unit is one shorter canvas dimension.

On an `object` selection, `preview --move left --amount .1` translates a shape, head, hand, standalone lock,
moon or sun by .1 of the shorter canvas dimension in screen space. Size, tilt and child edits remain
unchanged. It uses the same revision guard, preview, accept and undo as local pushes. Sky/hills fill
the canvas and use horizon/relief controls instead. On a local lock selection, amount still means
nominal lock widths; semantic eye/face/hair features cannot accidentally translate an object.
`report.json` includes alignment colour meanings and movement units.

### Head — simple flat-cartoon preset

`new scene.json --kind head` creates the user-accepted preset direction. No path data is required.

| field | meaning / default |
| --- | --- |
| at | face center: {anchor: center, offset: [0,-.06]}; explicit placements use their own offsets |
| length / width | .55 of shorter canvas dimension / .79 of that head height |
| angle | 0; 2D tilt, positive toward screen right along the head's downward axis |
| eye_scale / jaw | 1 / .42; eye size and cheek-to-jaw station, with the head ruler fixed |
| expression | gentle (unchanged default), neutral, smile, curious; coordinated brows, mouth and eyelids |
| gaze | 0; −1..1 looks left/right in the head's local frame; both eyes move together |
| hair | side-part; alternatives bob / none |
| palette | optional hair, skin, iris, shade, ink; a new hair/iris colour derives related tones, including bob and side-part internal hair lines |
| hair_edits | generated left/right child edit lists; root/tip remain protected |
| depth / depth_slope | 0 / 0; linear support anchored at face center |

Inspect features `object`, `eyes`, `face`, `hair`, `expression`, `left-lock`, `right-lock`. A single scene object is
inferred when `--object` is omitted. Semantic features expose their permitted controls in the report.
`preview ... --set eye_scale --value .92 --reason "..."` sets a selected control. Colour aliases are
hair_color, skin_color, iris_color, ink_color. Select a child lock for `--move`; its screen direction
is converted through the parent's tilt before changing local geometry. A bare head retains dormant
hair edits but exposes no editable lock until a hairstyle is active. Multi-head SVG IDs are namespaced.
`expression` highlights brows, mouth and the actual eye/lash contours; `eyes` exposes gaze alongside
eye_scale/iris_color. A smile raises the lower lids; curiosity opens one eye with its raised brow.
These are small flat-cartoon presets, not a complete facial rig or a guaranteed emotional reading.
Closeups show neutral opaque workspace outside the document rather than transparent black margins.

The head is one flat artwork component with an opaque support footprint. Internal face/hair drawing
order is recipe artwork, not a 3D head or a head-turn model. Child geometry remains editable.

### Hair-lock controls

| field | meaning / default |
| --- | --- |
| at | {anchor: upper_center, offset: [0,0]}; offset is a canvas fraction |
| length | .68 of the shorter canvas dimension |
| width | .19 of lock length, nominal full width |
| width_side | both; left/right grows width only on that side of root-to-tip travel |
| angle | -8 screen degrees from down, positive toward right |
| sweep | .16 lock lengths of lateral gesture bow; independent of width |
| depth / depth_slope | 0 / 0; larger is closer; slope changes depth per screen-y lock length |
| palette | optional fill, shade, light, ink hex colours |
| edits | operation records, generated by preview/accept |

`inspect` emits a `selection.json` with canonical scene SHA256, implementation fingerprint, object ID, side, arc parameter `at`,
influence `radius`, actual region/object bounds and locked root/tip. Left/right **edge names** follow
root-to-tip travel; move left/right/up/down always means **screen direction**. `at` follows the
generator's root-to-tip parameter, not exact arc length. The overlay is the authoritative way to align.

`preview` accepts that selection, a positive amount in nominal full widths and a drawing reason.
It produces candidate scene, source/result hashes and operation, plus artwork/alignment/crops.
The working scene is unchanged. `accept` refuses a stale base, changed implementation or tampered result hash. `undo` restores
the previous accepted scene and refuses to overwrite an out-of-band change. Local edits require their
influence interval strictly inside (0,1), preserving root/tip. Unknown fields, nonfinite values and
crossed contours are errors. A 2D push retains the support's depth function; it is not a spatial-route
edit. Current geometric checks are sampled, not a proof for all continuous deformation.

`report.txt` lists actual PNGs; `report.json` binds them to the canonical scene revision, implementation
fingerprint and renderer. The implementation hash covers the studio sources and depth/renderer
dependencies. Undo restores input data; visual identity across implementation upgrades is not promised.
Image SHA256 values and a `ready` status distinguish completed views from failed/in-progress rendering.
An unfinished CLI preview cannot be accepted. A new request first marks its proposal `preparing`,
clearing the image list; even a pre-render pose refusal cannot leave an old candidate acceptable.
Alignment and closeups are author aids; `artwork`
contains no handles. No reference image is read.
No articulated head attachment, curved support or universal object capability is implied by studio-1.
The explicit portrait context adapter is a bounded existing-scene integration experiment.


## Scope: the current flat 2D back end

Purpose: the node format a drawing compiles down to — semantic nodes with parameters that compile to
SVG, rendered through the existing chrome pipeline, so all compare/probe tooling works unchanged.

This is the current SVG compiler, not the planned depth-aware renderer. Global `z` layers and
manually complementary ring arcs are legacy workarounds of this back end; the engine that derives
visible fragments from 3D support depth without requiring an author to split the artwork is
`docs/6_ARCHITECTURE.md`, not this format.

Authoring happens one level above this. A drawing is described in relations (`docs/5_PRODUCT.md`) and
the resolver emits these nodes with absolute geometry; coordinates are not hand-written here. This
format's job is z-ordered painting with occlusion as the renderer's problem, not the author's.

## File format

A scene file is a YAML list of nodes, one per line, inline flow style — **but these are the resolver's
*output*, not something a human writes** (invariant 5). Hand-authoring this format is the failure mode
that produced 824 hand-typed vertices in the frozen portrait. Read this format to understand what the
engine does and to debug what it emitted.

```yaml
  # comment per shape = the explainability contract
- {layers: [bg, hair, body, hat, hat-front]}
- {rect: bg-sky, full: true, fill: grad:sky}
- {ellipse: pom-1, at: [660,45], rx: 45, ry: 26, fill: "#df9199", z: hat}
- {stroke: hair-s3, spine: [[612,248],[648,231],[676,238]], w: 5, taper: both, ink: "#26354a", z: hair}
- {blob: ribbon-main, spine: [[20,390],[560,380],[520,570],[392,772]], w: 120, grad: ribbonGrad, z: ribbon}
- {petal: flower-1, at: [880,740], n: 5, len: 90, wid: 40, curl: 0.4, spread: 180, fill: "#f2b8c4", z: scene}
- {region: hem-light, seed: [560,930], tol: 28, fill: "#cbdfd3", z: skirt}   # always floods the reference raster
- {trace: hair-mass, from: image.jpg, class: hair, z: hair}             # contour extract, computed
- {blur: [pink-overlay, yellow-overlay], std: 6}
```

Rules: top level = YAML list; nodes are flat dicts (inline flow style preferred; block style allowed
for long spines); comments free; every node has an `id`-bearing key (its type as key, value = id); `z`
= layer name; missing `z` = `default`.

**Coordinate budget, restated for this layer:** a node emitted by a relation or a generator may carry
hundreds of resolved points — that is fine, the machine computed them. A node a human *typed* may not
exceed ~4 coordinates (invariant 5 / P19). The budget limits authoring, not resolution.

## Layers and occlusion

`layers:` is an optional first node (list of layer names, bottom→top). The renderer paints by layer
order, then document order within a layer. This renderer uses **global painter order**, not geometric
depth. It can hide a whole shape behind another but cannot correctly alternate depth along one
continuous bent surface. The intended engine must do that without author-defined cuts — that
obligation is `docs/6_ARCHITECTURE.md`'s.

## Node types

Two kinds of row, and the difference matters (P18): rows marked **computed** take their geometry from
the reference raster or from layers below, so they are the *teacher* — they cannot appear in a
reference-free drawing. Everything else resolves from relations alone.

| type | keys | compiles to |
| --- | --- | --- |
| `rect` | at+[w,h] or `full`, fill | `<rect>` |
| `ellipse` | at, rx, ry, rot?, fill, stroke?, sw? | `<ellipse>` |
| `stroke` | spine (list of [x,y]), w (or widthProfile [[t,w]...]), taper both \| start \| end \| none, ink, cap round | `<path>` stroked, Bézier-smoothed spine, width via taper or multiple offset paths |
| `blob` | poly (list) OR spine+w, fill, stroke?, sw?, blur? | closed `<path>`, smooth_path |
| `petal` | at, n, len, wid, curl (0-1), spread (deg), angle0, fill, stroke? | n rotated blob instances around `at` |
| `ribbon` | spine, w, grad \| fill, op | stroke with width, gradient along bbox |
| `wave` | spine, w, amp, len (wavelength), sag, taper?, fill \| grad? | spine displaced by sin wave + gravity droop, compiled to closed ribbon path |
| `strands` | region [x0,y0,x1,y1], n, dir (deg), spread, w, wj (width jitter), len, ink (color or list), seed | n seeded flowing hair/fold strokes inside region; deterministic per seed |
| `ring` | at, r OR rx/ry, rot?, w, a0/a1 (deg, arc range; default full circle), zig (depth as fraction of w), zn (teeth/revolution), zq (jitter 0-1), seed, hue [h0,h1] (deg walk along arc), sat, val, nseg | color-walking annulus arc with zigzag outer edge; slices into nseg filled segments. Back/front scene split = two complementary ring nodes sharing geometry+seed (teeth line up at seam — z-plane split, not path split) |
| `region` | seed, tol, fill, grow? | **computed** paint-bucket on the *reference raster* (there is no layers-below source yet); contour→smooth path |
| `trace` | from (image path), class (anchor colors), region?, z | **computed** colour-class contour (outline only; no spine+width fit) → blob/stroke; teacher only, never in a reference-free scene |
| `grad` | dir or at/r (linear \| radial), stops [[off,color]...] | named `<linearGradient>`; referenced as `grad:name` in fills |
| `blur` | ids or layer, std | wraps targets in `<g filter>` |

Defaults: `z: default`, `op: 1`, `cap: round`, `taper: none`. Unknown key = hard error (renderer
validates schema; no silent ignores).

How the generator types (`wave`, `strands`, `ring`) produce geometry from these keys is
`docs/8_DETAIL.md`.

## Renderer contract

- CLI: `.venv/bin/python scripts/scene_render.py scene.yaml -o out.png [--size 1024x1024]` (+ `--svg out.svg` to keep the compiled SVG).
- Compile: YAML → validate schema → resolve grads/filters → z-sort → emit SVG → chrome render (existing pipeline).
- `region`/`trace` need the reference raster: `--ref image.jpg`. Their presence makes a scene
  teacher-dependent — see the computed rows above.
- Determinism: same input → same output bytes (no randomness unless a `jitter` key seeds explicitly).
- Errors: node-indexed (`node#idx: …`) with unknown keys/types failing loudly (YAML source-line
  numbers are pending; `relate.py` `SpecError` messages do not include them yet).

## Explainability contract

Every node carries an id and (optionally) a comment stating intent. The compiled SVG keeps ids as `id`
attributes and node comments as adjacent `<desc>` elements. A human reads the scene top-to-bottom as
the drawing's description — which is why a scene file written from a reference is itself the
compressed, transferable record of what the drawing *is* (see `docs/5_PRODUCT.md`, the teacher role).

## Traced data: materializing a teacher measurement (the only way to use the raster)

Invariant 6 / P18: **the engine never sees the target.** A live `region` node breaks that — the spec
would not render with `image.jpg` deleted. The teacher step is therefore a **materialization**, in
four steps:

1. `scripts/draw freeze <spec>.yaml --ref image.jpg` — resolve once with the reference open.
2. The computed outlines land in `<spec-dir>/traced/<node>.json` WITH provenance (image path +
   sha256, seed, tol, eps, method, vertex_count).
3. The spec's `region` nodes are rewritten as `traced` nodes pointing at that data.
4. The spec now renders with the image deleted — and the original region form survives in the
   sidecar's seed/tol/eps, so it can be re-frozen when the reference changes.

The sidecar keeps the original region form as `seed`/`tol`/`eps` in that same file; the authoring forms
that point at the data are `docs/5_PRODUCT.md`'s (`region` and `traced`).

Staleness is loud: if `image.jpg`'s sha256 no longer matches what the sidecar recorded, resolution
raises `SpecError` rather than silently using stale geometry.

Why a sidecar and not inline vertices: the authoring file must stay a *description* a human can read.
A `poly` of two thousand coordinates inline would look like the 824-hand-typed-coordinate failure even
though it is machine output; a named `traced` node keeps the generated data clearly marked as
**computed** (invariant 5 is about what a human types).

Why a frozen contour is not a canon, how a trace is used to fit a family and then discarded, and
the honesty hinge that forbids fitting to an evaluation metric are `docs/5_PRODUCT.md`'s — they are
rules about the language, not about this format.

## Generic colour mass (shape)

new/add --kind shape creates a coordinate-free rounded block. Node fields: id/kind/intent;
at/length/width/angle/depth/depth_slope as on other parts; profile block|oval; rounding [0,1]
(default .65; block exponent 2+22*(1-rounding), oval exponent 2); taper [-.98,.98]
(default 0, positive narrows the top, negative the bottom); stroke [0,.1] (default .008 of height);
palette fill/ink; edits. Height length is [.005,1.6] of the shorter canvas dimension; width [.001,6]
is width/height. Rotate a tall thin mass to make a long horizontal mark. This is an editable
silhouette, not raw SVG, an automatic solid or an attachment rig.

object exposes the shape parameters, intent and palette. left/right/top/bottom expose bounded
contour pushes with --at/--radius. The four arcs run clockwise with at=0..1 (top left-to-right,
right top-to-bottom, bottom right-to-left, left bottom-to-top). The interval must remain strictly
inside its two diagonal joins. Selection lists current focus, protected joins and actual bounds.
Amount is a fraction of the nominal shorter extent. Edits store side/at/radius/dx/dy/reason;
dx/dy are in shape-local axes after the preview converts the requested screen motion. Thus later
whole-object rotation rotates the sculpt too. Invalid self-intersecting/collapsed silhouettes
are refused before accepting. Existing shape placement defaults to center; insertion is foreground.

Inspection and preview refuse an output file that aliases a working scene or selection input,
before writing any candidate/report. Choose separate VIEW/TRY directories. The lower-level bundle
API receives a scene value and cannot know its source filename; script callers must keep input
paths separate from exported scene.json/candidate.json/report.json and images.

## Grouped semantic parameter proposal

preview --change NAME=VALUE accepts repeated changes as one proposal on the selected feature.
It is mutually exclusive with --set/--value and --move. Split only at the first equals sign,
so an intent may contain equals signs; duplicate names, empty values and unexposed controls are
refused. Numbers/colours/enums follow the single-control rules. All assignments are made to an
isolated candidate, then the completed state is validated. Failure leaves the working scene
unchanged and invalidates an earlier candidate in the reused TRY directory. Rendering failure
also leaves no ready candidate. Successful accept journals one operation.parameters object;
one undo restores the complete prior scene. Model API: parameters_preview(scene,selection,changes,reason).
Legacy parameter_preview retains its existing operation.parameter/value journal format.

## Geometry-derived attachment pins

A movable node may replace at with attachment. Fields: to (existing object ID), self and target
(named mounts, both default center), inset (default 0, -2..2 of target nominal shorter extent),
offset (optional [dx,dy], each -2..2 of shorter canvas dimension in screen axes). at and attachment
are exclusive. Sky/hills cannot be attached children. Shape mounts are center plus arc-midpoint
paint edges top/right/bottom/left; side names follow local geometry under rotation. Edge points
include half the explicit outline width and current sculpt tangent. center has no normal, so nonzero
inset is refused there. Other current component macros offer center; a standalone lock also offers
root/tip. Inspect anchors is the authoritative availability surface.

Whole-object relations form an acyclic single-parent graph; stroke endpoint constraints below add
a second target dependency. Whole-object pins translate the child's selected mount onto the
current target mount, minus outward target normal times inset times target scale, plus the retained
screen offset. The child retains its own screen angle and size. Changing a parent resolves its
whole descendant chain; raw authoring data carries relations, not baked per-child frame coordinates.
Node-level component compilation requires a resolved node; attachment.resolve_scene(scene) supplies
an ephemeral compiler copy. Rendering, selected feature paths, magnification, depth and reports all
use that same resolved placement. Report geometry remains bound to the raw scene revision.

preview --attach TARGET_SELECTION requires current --feature anchors selections for both objects;
--self-anchor/--target-anchor infer a single exact inspected mount, otherwise default center;
--inset defaults 0. It uses the existing preview,
accept and undo contract. Target selection inputs join scene/source inputs in output-alias refusal.
preview --detach requires anchors selection and preserves current placement as a generated free at.
Object --move on an attached node changes its retained screen offset. A local shape edit that
changes the actual pinned point or its outward normal is refused. Parent edits may
move related descendants deliberately; unrelated objects remain independent.

This is one point mount, not an inherited transform, edge-fit, boolean union or full solid rig.
Depth fields remain independent; attachment never specifies a visibility cut or guarantees a
pleasing seam. Typed intrinsic geometry is checked before graph resolution; missing targets,
unknown anchors, illegal inset and cycles refuse the candidate without changing working data.

## Gesture stroke node

kind stroke has id/kind/intent, optional at or attachment or endpoints (defined below), length, thickness, angle, bend,
start_width/end_width, start_cap/end_cap, shade, ink_width, depth/depth_slope, palette and edits.
At places the root; absent it, root is canvas center plus [0,-.2]. Length is root-to-tip chord / min
canvas (default .4, .005..2); thickness / min canvas is independent (default .045, .001..1).
Angle 0 points down and 90 right. Bend is sideways chord fraction (-1..1), default 0. Width
multipliers default 1 (0..4); caps round|flat default round. Shade none|left|right defaults none.
Ink_width is canvas fraction (default 0, 0.. .1). Palette fill/shade/ink; fill defaults #496b73,
shade derives at .78 value, ink #304950. Edits carry at/radius/dx/dy/reason in material axes and
nominal thickness units, with the same strict interior influence bounds as lock pushes.

Object exposes those semantic controls; spine exposes a bounded midline push. Root/tip are terminal
handles using screen movement / min canvas, opposite terminal fixed. Mounted free-terminal moves
require the opposite terminal as the self pin; center/moving-terminal pins refuse that operation.
Length/angle updates preserve thickness. A center-pinned spine window cannot displace its midpoint.
Frame position/depth use the same resolver and visibility contract as other parts. Root/tip mounts
are cap-center joints, not the outer ink extremes. No target/image/browser is read to compile it.

## Exact inspected mounts and current closeups

Head adds chin at the rendered face's own median-axis lower boundary, including outline half-width;
hand adds wrist from the shared WRIST_BASE construction value. Other kind-specific mounts remain.
Shapes additionally address a side position as top|right|bottom|left@fraction, fraction 0..1 along
its nominal clockwise arc. Point position and adjacent normals interpolate continuously; default
named side mounts remain exact midpoint values. Inspect anchors --anchor NAME focuses that exact
point and records anchor in selection. An attachment may infer self/target names from exact
inspections; without them it defaults center. Explicit positioned addresses require an exact
matching inspection. Stored relation fields remain the same named strings, not baked coordinates.
Local contour protection compares the actual pinned point and normal before/after, including
adjacent-arc corner cases. Single-point mounts do not impose size or angle inheritance.

Edit closeups recompute the selected region at the candidate scene, so a moved endpoint or exact
mount is magnified where it landed. Original selection/base data remains bound to the prior scene.
Author text stays unchanged in raw data; SVG comments escape markup and normalize double hyphens.
That also preserves valid IDs containing double hyphens without creating invalid XML comments.

## Remove an inspected component

Scene nodes now accepts 0..24 entries. An empty scene is valid paper; new --kind blank creates it.
Inspect without an object/feature on empty paper exports a canvas bundle; selecting a part requires
an added node. Adding a foreground part to empty paper starts at depth 1 and remains undoable.

preview --remove requires a current whole-object selection and a drawing reason. Default deletion
removes only that node. Each surviving direct child loses attachment and receives the old resolved
free at, preserving its projected geometry. Further descendants retain their original relations.
--cascade removes the selected node and all transitive descendants; unrelated nodes/order remain.
It is refused with other operations. Removing the last node is valid; accept/undo restore the whole
scene and graph through the normal revision-bound journal. No work is silently discarded.

Operation records action remove, object, ordered removed IDs, detached_children, cascade and reason.
The candidate selection carries removal impact metadata. Clean artwork shows only surviving paint;
alignment/closeups use the previous geometry for red dashed removed outlines and blue current
retained-child outlines/labels. Reports list those affected IDs and current surviving nodes.
Removal alignment needs the original scene; it never treats a missing current object as selectable.
Replacing a part is currently separate remove/add/configure/attach edits, not an atomic transaction.

A preview selection carrying removal or attachment_target describes an operation impact view, not
a new part inspection. Reusing it for another proposal is refused with an explicit re-inspect
message. Declining a proposal leaves its original inspection usable while that base stays current;
accepting any edit requires inspecting the new revision.

## Named stroke endpoint constraints

A stroke may use endpoints instead of attachment or free at. endpoints is a nonempty object with
root and/or tip keys. Each relation has to, target (default center), inset (-2..2 target nominal
shorter extent, default 0) and offset (two screen/min-canvas values in -2..2, default [0,0]).
These are projected points; support depth remains independent. Existing attachment forms are valid.

One endpoint pin translates the ordinary authored chord like a legacy root/tip pin. Two endpoint
pins derive chord length/angle; those fields must be omitted in raw authoring, and disappear from
exposed controls. The remaining stroke controls and protected spine edits remain available. The
derived chord must satisfy existing .005..2 length bounds and geometric validity. No clamping or
silent shape replacement occurs for coincident/crossing/invalid target configurations.

Inspect the source with feature root or tip and the target with feature anchors (optionally one
exact --anchor). Preview --bind-end TARGET_SELECTION, optional --target-anchor/--inset, and reason.
It preserves an existing legacy terminal pin and converts it to endpoints; an unrelated center pin
must be detached first. Exact positioned targets must have been explicitly inspected. A ready
preview shows both actual pin rings, old/new geometry and target callout. Target inputs join the
existing output-alias preflight. Reports include endpoints and derived_chord, not false editable
length/angle controls. Constraints may depend on two parents; all dependencies must be acyclic.

A pinned end refuses terminal dragging; two pins refuse whole-object translation. A single pin
can retain a screen offset. Preview --unbind-end from a root/tip inspection releases only that pin
and bakes the current chord so paint stays unchanged. Anchors/--detach releases all pins in place.
Default deletion releases only affected endpoint links while preserving visible paint and any
remaining pin; cascade follows either dependency. The removal impact reports released_endpoints
where relevant. These operations use the existing stale/ready/history/undo contract.
# Compact grip vocabulary — candidate scope, 2026-11-13

`kind: "grip"` is a compact flat illustrated closed hand with an owned handle segment. It is
separate from the open `hand` preset and does not solve arbitrary 3D hand/prop contact. It uses
the same placement/attachment, support depth, revision-bound inspect/preview/accept/undo contract.
No runtime teaching SVG, mesh or image is loaded.

Required node fields are id/kind/intent. Defaults: length .38 (nominal hand height / shorter
canvas), width 1, angle/depth/depth_slope 0, thumb_side "right", fold_length 1, thumb_reach .9,
thumb_thickness .10, handle_span 1.8, handle_thickness .08. Thumb thickness, handle span and
handle thickness are hand-ruler values; thumb_reach and fold_length are factors. Handle span is full end-centre span.
Bounds: length .04–1.2, width .75–1.25, fold_length .8–1.15, thumb_reach .55–1.1,
thumb_thickness .08–.13, handle_span 1.2–3, handle_thickness .04–.18. Angle/depth/slope follow
the other movable components. Combinations that conceal either handle end or break the single
solid projection are refused. Palette keys are skin/ink/handle/handle_ink.

Features: object (all controls); thumb (reach/thickness/skin/ink); fingers (fold_length/skin/ink);
palm (width/skin/ink); handle (span/thickness/handle colours). Colours use skin_color, ink_color,
handle_color, handle_ink_color aliases. These features use semantic --set/--change, not a free
digit-tip or contour drag. thumb_side is left/right in the unrotated preset. The component centre
is a stable host point, distinct from its grip mount.

Mounts: wrist, grip, handle_left, handle_right, handle_top, handle_bottom. Names follow the
component through angle/mirror changes; inspect actual positions. Top/bottom carry outward normals;
centre/end/wrist pins carry no normal. Attachments translate one pin and keep authored angle;
external two-target strokes can follow both a grip endpoint and a separate vessel/flag support.
`report.nodes[ID].dimensions_pixels` and `.dimensions_canvas` expose wrist_width,
handle_thickness and nominal_hand_height; the latter values divide by the shorter canvas extent.

The internal palm, handle, pads and thumb have declared constant depths. Visibility comes from
those planes; intentional fold/exterior ink is separate and clipped by that visibility. The whole
compound has the normal component support depth when meeting other scene objects. Blind image
criticisms and purpose-aware operational review remain separate claims (4_USECASE).
