# Scene format & renderer — high-level drawing DSL

Purpose: authoring drawings at *object* level (semantic nodes with parameters) instead of hand-written SVG coordinates. The renderer compiles a scene file to SVG (rendered via the existing chrome pipeline, so all compare/probe tooling works unchanged). This kills the three biggest pain points from the portrait project: manual occlusion surgery, fragmented shape soup, and coordinate-level iteration.

## File format

`scene.yaml` — top level is directly a list of nodes, one per line, inline flow style:

```yaml
# comment per shape = the explainability contract
- {layer: bg, rect: full, fill: grad:sky}
- {ellipse: pom-1, at: [660,45], rx: 45, ry: 26, fill: "#df9199", z: hat}
- {stroke: hair-s3, spine: [[612,248],[648,231],[676,238]], w: 5, taper: both, ink: "#26354a", z: hair}
- {blob: ribbon-main, spine: [[20,390],[560,380],[520,570],[392,772]], w: 120, grad: ribbonGrad, z: ribbon}
- {petal: flower-1, at: [880,740], n: 5, len: 90, wid: 40, curl: 0.4, spread: 180, fill: "#f2b8c4", z: scene}
- {region: hem-light, seed: [560,930], tol: 28, fill: "#cbdfd3", on: ref, z: skirt}
- {trace: hair-mass, from: image.jpg, class: hair, fit: outline, z: hair}
- {blur: [pink-overlay, yellow-overlay], std: 6}
```

Rules: top level = YAML list; nodes are flat dicts (inline flow style preferred; block style allowed for long spines); comments free; every node has an `id`-bearing key (its type as key, value = id); `z` = layer name; missing `z` = `default`.

## Layers & occlusion

`layers:` is an optional first node (list of layer names, bottom→top). Renderer paints by layer order, then document order within a layer. **Occlusion is the renderer's job** — shapes are drawn whole, never pre-split. No path may encode "avoid another shape".

## Node types

| type | keys | compiles to |
| --- | --- | --- |
| `rect` | at+[w,h] or `full`, fill | `<rect>` |
| `ellipse` | at, rx, ry, rot?, fill, stroke?, sw? | `<ellipse>` |
| `stroke` | spine (list of [x,y]), w (or widthProfile [[t,w]...]), taper both | start | end | none, ink, cap round | `<path>` stroked, Bézier-smoothed spine, width via taper or multiple offset paths |
| `blob` | poly (list) OR spine+w, fill, stroke?, sw?, blur? | closed `<path>`, smooth_path |
| `petal` | at, n, len, wid, curl (0-1), spread (deg), angle0, fill, stroke? | n rotated blob instances around `at` |
| `ribbon` | spine, w, grad | fill, op | stroke with width, gradient along bbox |
| `wave` | spine, w, amp, len (wavelength), sag, taper?, fill | grad? | spine displaced by sin wave + gravity droop, compiled to closed ribbon path |
| `strands` | region [x0,y0,x1,y1], n, dir (deg), spread, w, wj (width jitter), len, ink (color or list), seed | n seeded flowing hair/fold strokes inside region; deterministic per seed |
| `ring` | at, r OR rx/ry, rot?, w, a0/a1 (deg, arc range; default full circle), zig (depth as fraction of w), zn (teeth/revolution), zq (jitter 0-1), seed, hue [h0,h1] (deg walk along arc), sat, val, nseg | color-walking annulus arc with zigzag outer edge; slices into nseg filled segments. Back/front scene split = two complementary ring nodes sharing geometry+seed (teeth line up at seam — z-plane split, not path split) |
| `region` | seed, tol, on (ref | layers-below), fill, grow? | paint-bucket on the rasterized `on` target; contour→smooth path |
| `trace` | from (image path), class (anchor colors), fit (outline | spine+width), z | contour extract (existing method) → blob/stroke |
| `grad` | dir or at/r (linear | radial), stops [[off,color]...] | named `<linearGradient>`; referenced as `grad:name` in fills |
| `blur` | ids or layer, std | wraps targets in `<g filter>` |

Defaults: `z: default`, `op: 1`, `cap: round`, `taper: none`. Unknown key = hard error (renderer validates schema; no silent ignores).

## Generators (`wave`, `strands`, `ring`)

Generated nodes replace hand-placed stroke fragments (P15: generate from parameters). All are seeded and deterministic — same scene → same pixels, byte-identical. Tuning knobs are per-node parameters; never hand-edit generated output. Regression tests in `scripts/tests/test_scene.py` cover placement, determinism, and schema of each generator.

## Renderer contract

- CLI: `scripts/scene render scene.yaml -o out.png [--size 1024x1024]` (+ `--svg out.svg` to keep the compiled SVG).
- Compile: YAML → validate schema → resolve grads/filters → z-sort → emit SVG → chrome render (existing pipeline).
- `region`/`trace` need the reference raster: `--ref image.jpg`.
- Determinism: same input → same output bytes (no randomness unless a `jitter` key seeds explicitly).
- Errors: line-numbered (YAML source line), unknown keys/types fail loudly.

## Explainability contract (unchanged)

Every node carries an id and (optionally) a comment stating intent. The compiled SVG keeps ids as `id` attributes and node comments as adjacent `<desc>` elements. A human reads scene.yaml top-to-bottom as the drawing's description.

## Migration acceptance (portrait)

1. Scene render vs v20 render: every zone's color distance within +15% of v20's (no regression), overall ≤ 65.
2. Node count ≤ ~80 for the whole portrait (vs ~150 paths).
3. A parameter change demo: adjust `flower-1 curl` 0.4→0.7 and `skirt` poly by moving 2 points — re-render shows the intended change without touching anything else (proves object-level iteration).
4. All probe scripts (pixel checks) unchanged and passing.
