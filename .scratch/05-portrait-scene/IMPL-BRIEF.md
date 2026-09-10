# IMPLEMENT BRIEF — scene format renderer + portrait migration

Read first: `docs/drawing/scene-format.md` (the spec — authoritative). Then implement, migrate, test.

## Phase 1 — implement renderer (`scripts/scene_render.py`, ~250-350 lines)

- CLI: `render scene.yaml -o out.png [--svg out.svg] [--ref image.jpg] [--size WxH]` (uses `.venv` python; reuses `scripts/draw.py`'s render approach: compile SVG → chrome-headless-shell screenshot; import or duplicate the CHROME path logic).
- YAML parse: top-level list of dicts (PyYAML safe_load; add PyYAML to .venv via uv).
- Schema validation: unknown keys/types = hard error with the node's line number (yaml.compose gives line info; or track manually).
- Compile order: resolve `grad:` refs → z-sort (layers list + document order) → emit SVG (ids preserved, comments → `<desc>`) → screenshot.
- Node compilers per spec table: rect, ellipse, stroke (spine→smooth quadratic path; taper via widthProfile → emit as filled outline path: offset the spine by width perpendicular at each anchor), blob (closed smooth path), petal (n rotated blobs), ribbon (stroked spine w/ width+gradient), region (paint-bucket: cv2.floodFill on the `on` raster from seed with tolerance; external contour → smooth path), trace (color-class mask in region → contour; reuse the established method), blur (wrap targets in filter group).
- Taper implementation hint: for widthProfile, compute per-anchor perpendicular offsets (left/right side point lists), build one closed polygon (left side + reversed right side), smooth_path it, fill with ink.
- Unit smoke tests (write `scripts/tests/test_scene.py`, runnable with `.venv/bin/python`): (a) ellipse renders at exact position/size (probe pixels), (b) z-order: red rect over blue rect → center pixel red, (c) stroke taper: width at ends ~0, (d) petal count: n=5 → 5 lobes visible (probe 5 directions), (e) region: flood-fill on a synthetic 3-color image stays within boundary, (f) determinism: two renders byte-identical, (g) unknown key raises with line number.

## Phase 2 — migrate the portrait

- Write `.scratch/05-portrait-scene/work/scene.yaml`: re-express v20 (`.scratch/05-portrait-scene/work/v20.svg` — read it; it is the verified assembly) as nodes. One node per semantic shape; long spines stay; layers: [bg, ribbon, skirt, body, hair, hat, overlays].
- Gradients: move v20's defs into `grad:` nodes (bgGrad, ribbonGrad, tailGrad, greenOvGrad, pinkOvGrad).
- Where v20 has pre-split occlusion (head arc breaks, tucked path ends), UN-split: draw whole shapes in z-order — that's the point.
- Blur node for the overlays.
- Render with `--ref image.jpg`; iterate until acceptance (below) passes: fix node params (positions/sizes/grads), NOT by adding hand-paths.

## Acceptance (from spec; verify each with real numbers)

1. Zone distances vs v20: every zone within +15%, overall ≤65 (zones: hat 430,0,594,300 · face 580,150,250,270 · ribbon 0,380,560,450 · skirt 400,640,500,384 · torso 560,430,340,300 · curtain 790,270,234,500 — use the established probe snippet).
2. Node count ≤ 80.
3. Parameter demo: change flower curl + move 2 skirt points → re-render → view → confirm the change showed and nothing else moved.
4. Smoke tests all green.

## Pitfalls (each cost a session — obey)

- PyYAML: `on:`/`off:`/`yes:`/`no:` keys or values parse as booleans — quote them (`on: "ref"` is a VALUE so fine, but a key `on` is fine; beware values like `no`).
- Inline flow style: `{...}` must be one line per node.
- chrome render: absolute paths for `--screenshot`.
- After every generated-attribute edit: assert it landed (count before/after) or parse-verify.
- Region/traces: tight region boxes or masks leak into bg (pale colors ≈).

## Protocol

View image.jpg and rendered frames repeatedly. Iterate Phase 1 tests until green, then Phase 2 acceptance. Report: test results, zone distance table, node count, changelog. Do NOT git commit.
