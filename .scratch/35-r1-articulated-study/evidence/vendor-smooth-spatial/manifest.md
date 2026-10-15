# R1 `R.smooth` spatial-interface study manifest

## Scope and disposition

- This is the continuation of the earlier unfinished interface study, not a new curve/garment-shape hypothesis or R1 art candidate. It proves a narrowly scoped technical route: four authored local semantic controls generate either a raw polygon or closed sampled Catmull-Rom/cubic contour; both map through a real support frame, world coordinates, camera projection, polygon triangulation, bounded depth fills, and depth-clipped semantic boundary lines.
- The cloth and a separate foreground sheet each have four authored local points. Curve samples and the backend's triangles are generated, not authored anchor tables. `polygon` and `smooth` conditions share the same controls, support, camera, depth occluder and style; the comparison isolates the curve rule.
- Both contour-fill visibility and the one authored outer semantic line use the project backend/adapters. The SVG strokes only `*-cloth-boundary-*` paths; no triangle/mesh edges are stroked. Occlusion has no authored/manual spans or visibility splits.
- No target or sealed image is read or supplied to the engine. No Huashu character/art, coordinate, frame, pose, or composition was copied. No visual/art quality, R1, reference imitation, readability, or future success verdict is made.

## Provenance and attribution

- Earlier worker artifact, preserved unchanged at incorrect repository-root location `evidence/vendor-smooth-study/`: prior `study.py`, `test_study.py`, `study.svg`, `ticket.md`, `manifest.md`, and `check/{report.txt,draft.png}`. That worker's manifest already documents its standalone-SVG limitation and initial tests' lack of a true sampled-contour intersection guard. This new evidence corrects location and spatial integration only; it neither moves nor deletes the old work.
- Method source: `vendor/huashu-art-motion/scripts/engine/lib/rig.js`, `R.smooth`, lines 56–64: cyclic Catmull-Rom neighboring-point tangents become cubic Bezier handles, with `k / 3` handles and a closed seam. The generated function `cubic_segments` applies only that construction rule. Example instance: `scripts/engine/scenes/36_picasso_blue.js`, lines 89–92, where semantic anchors feed a smoothed shawl; it is cited only as an instance of the method. No points/designs from that scene were reused.
- Attribution for vendor method source: Copyright (c) 2026 alchaincyf (花叔 · 花生), MIT License, retained at `vendor/huashu-art-motion/LICENSE`. The present work is an independent Python implementation of the mathematical rule. For notice completeness, the MIT notice is reproduced here:

  > MIT License. Copyright (c) 2026 alchaincyf (花叔 · 花生). Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Implemented interfaces and checks

- `smooth_spatial.py::SEMANTIC_CONTROLS`: four original local `(u,v)` landmarks. `OCCLUDER_CORNERS` is a separate four-point foreground component.
- `cubic_segments` and `sample_closed_curve` transfer closed `R.smooth`; endpoint derivative vectors match at all joins including the wrap seam. Sampled contours are actively rejected for non-finite/too-short values, zero-length edges, degenerate area, proper self-crossing, nonadjacent touching, and collinear overlap before triangulation.
- `build_components` produces raw polygon or sampled curve `Component`s on named `SupportFrame`s. `component_faces` resolves local surface points through `SupportFrame.local_to_world` and `Camera.project` into the existing bounded triangle engine (`visible_fragments`/`visible_regions`). `visible_boundary_spans` sends each projected authored contour segment to `visible_segment_spans`; only geometry-derived spans are stroked.
- Test suite: 8 isolated `unittest` checks cover four-control input, cubic C1 continuity and closed seam, actual sampled invalid-contour rejection, support/world/camera/depth mapping, depth-order independent visibility, an occluder reducing both visible filled area and boundary length, deterministic generation, reference absence, and absence of mesh-seam strokes.
- `scripts/draw check` ran without `--ref`; its report list is deliberately only the rendered image below. This work has not been independently judged visually.

## Image-list artifact and revision hashes

`check/report.txt` image list (supply only this image to a fresh reviewer):

- `.scratch/35-r1-articulated-study/evidence/vendor-smooth-spatial/check/draft.png` — the drawing; SHA-256 `3f3ebc75c4b70603ef31f5b46676f2168d2c2701a6847b790f752d3ab67d048a`.

Direct project render: `spatial-study.png` (860×390); SHA-256 `3f3ebc75c4b70603ef31f5b46676f2168d2c2701a6847b790f752d3ab67d048a` (same pixels as `check/draft.png`). SVG source render `spatial-study.svg`; SHA-256 `01df624b62e5165e14e1e55efd05331ee9104d56e3f8001e69d286cd81d66dd7`.

Current source hashes:

- `smooth_spatial.py`: `e1497e8ecf06a9e79cb32a9f18fe293f8f3b904a6d1ec373b46fb83d8d4b57ad`
- `test_smooth_spatial.py`: `576254e1d256bb8b585aff133c7b095df81a29e107b6afe1c944653da446c3a8`
- `check/report.txt`: `c9c7f72a9af7befdc47f6b7fee3c35cdf13b87ec7cb5cf38b0e06465bb807777`
- `issues/19-smooth-spatial-continuation.md`: `d8b9dade7ea544ce97170000e1390d10b5526d90ea38e0103134a9de70f90d3c`

Prior-path immutable provenance hashes (existing `evidence/vendor-smooth-study/`):

- `study.py`: `3514dc858f25c9703e8fad41d3de037e3c495aaebe061763b540b7ff116f8317`
- `study.svg`: `dd660be22152d84569814902657d7cf6587468f0cdc6441d363a101e5c2fb8aa`
- `test_study.py`: `0da7d419493f05b87cbfc7374440cc098123ee625dd863a02d3b5ac4ef648fd1`
- `ticket.md`: `5754eff748d24850988b224d095d0613cf42aafa603b5a58a14d8fac12bdf73f`
- `manifest.md`: `e24f11f8c715b8b18776f576d0ab0c92dbb99c34befdcd6e15101c1ce603a197`
- `check/report.txt`: `8240f625f8b0497322d0c9e64840b7404e1470719417d2da661635f59ac49deb`
- `check/draft.png`: `d7a3467245e9f8485e3c4bf21980e40167dbc9f6809ab8b9f35e087c08bc5a11`

Source/license hashes:

- `vendor/huashu-art-motion/scripts/engine/lib/rig.js`: `88c4df6dc105cafdc7249a5f31c79928db6c05b372f04e2e0f14059e8620f17f`
- `vendor/huashu-art-motion/scripts/engine/scenes/36_picasso_blue.js`: `10023147e1e31afc162e1cfe51356867ef83595b41bbd5cc824d55532297ce09`
- `vendor/huashu-art-motion/LICENSE`: `6d6a2a9caf2e6d2b76974050427053b2892d8aa4c33fd168ce63a537fcee9d96`

## Commands executed

The successful validation commands below were bounded below 120 seconds; no network, install, service, or reference access was used.

```text
PYTHONPATH=. .venv/bin/python -m unittest discover -s .scratch/35-r1-articulated-study/evidence/vendor-smooth-spatial -p 'test_smooth_spatial.py'  # PASS: 8 tests
PYTHONPATH=. .venv/bin/python .scratch/35-r1-articulated-study/evidence/vendor-smooth-spatial/smooth_spatial.py  # PASS: deterministic SVG generated
scripts/draw check .scratch/35-r1-articulated-study/evidence/vendor-smooth-spatial/spatial-study.svg --outdir .scratch/35-r1-articulated-study/evidence/vendor-smooth-spatial/check  # PASS; no --ref, one image listed
scripts/draw render .scratch/35-r1-articulated-study/evidence/vendor-smooth-spatial/spatial-study.svg -o .scratch/35-r1-articulated-study/evidence/vendor-smooth-spatial/spatial-study.png  # PASS: 860x390
python - <<'PY'  # PASS: trailing whitespace / final newline checked on 5 task text files
from pathlib import Path
root = Path('.scratch/35-r1-articulated-study')
paths = [root/'issues/19-smooth-spatial-continuation.md', root/'evidence/vendor-smooth-spatial/smooth_spatial.py', root/'evidence/vendor-smooth-spatial/test_smooth_spatial.py', root/'evidence/vendor-smooth-spatial/manifest.md', root/'evidence/vendor-smooth-spatial/spatial-study.svg']
for path in paths:
    data = path.read_text(encoding='utf-8')
    assert data.endswith('\n'), f'{path}: missing final newline'
    assert all(line == line.rstrip(' \t') for line in data.splitlines()), f'{path}: trailing whitespace'
print(f'PASS: whitespace/final-newline checks for {len(paths)} task text artifacts')
PY
```

## Residual limits

This is technical integration evidence only. `draw check` itself has no verdict; no independent visual reviewer inspected the PNG here. No R1 drawing, reference-based observation, B mechanism-transfer illustration, physical-intersection gate, user/art gate, or user feedback is supplied. R1 remains resource-blocked / unverified; no hypothesis count, anchors, geometry candidate, backend or source candidate was changed.
