# Ribbon family — teaching card

## Ability and boundary

A ribbon is **one connected local strip** on a computed 3D support. Its local artwork domain is
`u ∈ [0,1]` along the length and `v ∈ [-1,1]` across the width. The support is sampled into
triangles only for projection and opaque depth tests. Those triangles are not line art. The compiler
chooses the front or back fill from each triangle's winding-derived normal and camera direction; an
author does not paint a front/back interval or split a ribbon where it goes behind something.

A rendered fragment is a visible part of the one complete component, not a second ribbon. The
local artwork includes one narrow longitudinal band `v ∈ [-0.18,0.18]`; it follows the whole local
strip, including its twist and bends. The band is deep plum on the front fill and warm cream on the
back fill, chosen for contrast against the listed default base colours. Custom `front`/`back`
palettes may reduce or eliminate this contrast; the stripe palette is fixed, not adaptive, and
custom-colour readability must be reviewed separately. Its front/back color still follows the same
winding-based face selection as the base material. A support card is another opaque surface that may
cover the component. `origin` and `heading` are the root attachment frame; changes to bend, width
taper and twist do not move the root centre or its initial direction.

## Compact spec

The runnable public input is JSON; the complete teaching input is
[`../work/teaching-example.json`](../work/teaching-example.json). The fixed stripe is a small
renderer-side artwork treatment, not another author parameter or a visibility/line engine.

| diagnostic fill | color | relative contrast |
|---|---|---:|
| front ribbon base | `#e68aa4` | — |
| front stripe | `#472639` | 5.32:1 |
| back ribbon base | `#7188bd` | — |
| back stripe | `#fff1b8` | 3.11:1 |
| support-card display fill | `#526a60` | display-only color; card geometry/depth unchanged |

| field | meaning / units | supported values |
|---|---|---|
| `name` | semantic component name; also used in deterministic output IDs | 1–48 ASCII letters, digits, `_`, `-` |
| `length` | local centreline length scale, world units | 0.25–8 |
| `width` | full root width, measured perpendicular to the centreline/frame, world units | 0.03–1.5 |
| `tip_ratio` | tip width divided by root width; width interpolates linearly along `u` | 0.15–1.5 |
| `bend` | smooth side displacement scale, world units | absolute value ≤ 1.5 × length |
| `depth` | smooth depth displacement scale, world units | absolute value ≤ 1.5 × length; `crossback`: also ≥ 2 × width |
| `twist` | total rotation of the transverse frame from root to tip, radians | −4π to +4π |
| `family` | one of `arch`, `s-curve`, `crossback` | fixed three-family vocabulary |
| `origin` | attached root centre `[x,y,z]`, world units | each coordinate within ±100 |
| `heading` | root direction in the x/y plane, radians | −4π to +4π |
| `front`, `back` | six-digit hex fill for the two material sides | e.g. `#e68aa4`, `#7188bd` |
| `segments` | number of length intervals used for the generated support | integer 12–128; default 40 |

`arch` moves along x while `bend` makes a rounded one-sided arc. `s-curve` uses a smooth
alternating side displacement. `crossback` makes a deliberately bounded backward run in projected x;
its side displacement uses the squared smooth envelope `bend × sin⁴(πu)`, which gives more side
slope through the reverse run than the broad arch and avoids the original finite-width local fold.
It requires `abs(bend) ≥ 0.05` and `abs(depth) ≥ 2 × width` to separate the principal projected
crossing sections. For every family the local centreline begins at `origin` and its initial tangent
follows `heading`.

The crossback's principal front-camera crossing has matching projected centreline positions near
`u=0.19735` and `u=0.80265`. At that pair, the centreline depth gap is about
`0.63858 × abs(depth)`. With `tip_ratio ≤ 1.5`, the two transverse half-widths can extend together
by at most `1.25 × width` in depth, so the `2 × width` bound separates these paired local sections.
The corrected frozen crossback mesh had no nonlocal triangle/triangle edge hit in sampled meshes
at 32, 48, 64, and 96 length intervals. That is a bounded check of this one input and triangulation
sequence, **not** a continuous-surface collision proof or guarantee for other specs/cameras.
The `2 × width` rule is not a guarantee against collision elsewhere on the surface.

The centreline frame begins with a perpendicular transverse axis and is parallel-transported along the
path; the twist is then distributed linearly over `u`. Full width at `u` is
`width × (1 + (tip_ratio − 1) × u)`. The surface point at `(u,v)` is the centreline plus `v` times
half that local width along the transported-and-twisted transverse axis. Computed mesh vertices and
SVG paths are outputs, not author coordinates.

## Commands

Render the teaching component in one camera (writes deterministic SVG and Chromium PNG):

```bash
.venv/bin/python scripts/ribbon_family.py render \
  .scratch/19-ribbon-family/work/teaching-example.json \
  --name front --yaw 0 --pitch 0 \
  -o .scratch/19-ribbon-family/evidence/teaching-example
```

Rebuild the frozen, six-case/two-camera board and its labelled/unlabelled companions:

```bash
.venv/bin/python scripts/ribbon_family.py board \
  .scratch/19-ribbon-family/work/cases.json \
  --out-dir .scratch/19-ribbon-family/evidence
```

For a camera change, change `--yaw`/`--pitch`, not the component geometry. The preselected board uses
`front` (yaw 0°, pitch 0°) and `oblique` (yaw 38°, pitch 22°).

## Causal examples

- **Good: `teaching-arch`** is a single evenly wide, gently bent, untwisted strip. The root stays
  attached while the two camera views change projected silhouette and front/back paint.
- **Good: `tapered-tip`** changes only `tip_ratio` from 1.0 to 0.22. It narrows toward the free end;
  the root width, centreline and attachment remain unchanged.
- **Good: `twisted-two-sided`** changes only total twist. As the surface turns through the camera
  facing direction, the visible fill switches because its normal changes—not because a per-view
  colour flag was authored. A pink/blue boundary is this facing/material boundary, not drawn ink;
  its sampled edge may be faceted at low tessellation.
- **Good: `awkward-crossing`** uses the one continuous `crossback` strip and its local stripe.
  Two distant `u` sections overlap in the front camera at different depths; the near stripe continues
  through the projected crossing, and the far stripe is hidden by depth. The renderer receives one
  whole strip with UV artwork, never manually split near/far paths.
- **Bad input:** `{"name":"too-thin","length":3,"width":0}` is rejected because zero width
  destroys the strip. Use a small positive width in the declared range.
- **Bad input:** `{"name":"singular","length":3,"width":0.3,"family":"crossback","bend":0}`
  is rejected because this crossback route would have a singular support frame. Choose another
  family or provide a nonzero side bend.
- **Bad input:** `{"name":"flat-crossing","length":3,"width":0.3,"family":"crossback","bend":0.5,"depth":0}`
  is rejected: the reverse run then crosses itself at the principal paired sections. A depth of
  `0.5` is also too small for width `0.3`; crossback requires `abs(depth) ≥ 0.6` here.
- **Bad input:** `{"name":"manual-cut","length":3,"width":0.3,"visible_ranges":[[0,0.4]]}`
  is rejected as an unknown field. Visibility ranges are not part of the authoring interface.
- **Bad input:** `tip_ratio: 0` is rejected instead of hiding a collapsed tip or changing the
  component into a point.

## Tessellation and limitations

At 48 intervals, the tested centreline midpoint/chord deviation stayed below 0.04 world units for
all three families at length 6 and the maximum tested bend/depth of 9. This is a bounded centreline
approximation check, not a universal surface, line-art or high-twist error guarantee. Increase
`segments` for a smoother structural preview; do not add hand-written contours to patch the mesh.

The board uses a muted green-gray `#526a60` for the body card solely to distinguish its support
surface in this diagnostic; the card's frozen bounds, plane and depth are unchanged. This display
color is not part of the ribbon spec or a body-material rule.

The component is a ribbon, not proof of hair silhouette/grouping. It has no chosen line art, folds,
transparent materials, collision solver, perspective camera or unrestricted self-intersection
support. Crossback's depth/width rule separates its principal paired sections only; the sampled
triangle checks are not a universal nonintersection solver. Other self-intersections remain
unsupported. The reused visibility engine handles bounded opaque
triangles and has documented limits at exact coplanar ties and some different-fill seams. The
unlabelled board is still a diagnostic structural drawing; it is not a finished illustration or a
reference-ribbon route fit.
