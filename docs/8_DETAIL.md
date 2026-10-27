# 8_DETAIL — module internals: coordinate and transform conventions, generator mechanics, the resolver tier ladder, diagnostics

This file owns the inside of a module. It does not own the formats those modules produce (`7_INTERFACE.md`),
the language they serve (`5_PRODUCT.md`), or the commands that run them (`9_IMPLEMENTATION.md`).

# INFERRED

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
  `05-portrait-scene/evidence/diagnosis/`.
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
