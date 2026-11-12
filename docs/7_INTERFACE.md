# 7_INTERFACE — the contracts that cross a boundary: the compiled node format, the traced-data sidecar, the renderer and explainability contracts

This file owns exact shapes — field names, file formats, error strings and renderer guarantees. It does not
own why the language is designed as it is (`5_PRODUCT.md`), how any of it is computed (`8_DETAIL.md`), or
the commands that write it (`9_IMPLEMENTATION.md`).

# INFERRED

## Studio-1 scene and edit contract

The current editable slice is `python -m scripts.studio`. Scene `format` is
`learn-draw/studio-1`; `canvas` defaults to [640,640], `background` to warm paper, `nodes` is required.
Each node requires `id`, `kind` (`head`, `hand`, `hair-lock`, `sky`, `hills`, `moon`, `sun`), `intent`.
`new --kind landscape` instantiates sky and hills on a 960×640 canvas; `add --kind moon` adds a
celestial preset. Insertion is journaled and undoable. Existing names are never overwritten.
`new --size WIDTHxHEIGHT --background '#rrggbb'` optionally sets the canvas and paper at creation.
Every object selection exposes `intent` as a text control. Stock intent describes the component's
purpose without duplicating mutable colour or hairstyle values; custom author intent is never
silently rewritten when changing a parameter.
Foreground insertion (`add --kind head|hand|hair-lock`) starts on a plane beyond the existing
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

On an `object` selection, `preview --move left --amount .1` translates a head, standalone lock,
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
