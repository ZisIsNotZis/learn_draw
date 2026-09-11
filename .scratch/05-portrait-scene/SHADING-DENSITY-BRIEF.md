# SHADING+DENSITY BRIEF — scene.yaml fidelity pass

Working file: `.scratch/05-portrait-scene/work/scene.yaml` (114 nodes, scene format — read `docs/drawing/scene-format.md` first). Reference: `image.jpg` (1024×1024, anime girl, witch hat, floating on water, translucent ribbons).

## Baselines (independently verified; do not re-derive)

overall 62.2 · hat 38.2 · face 79.0 · ribbon 63.8 · skirt 87.9 · torso 86.1 · curtain 78.8
Zones: hat 430,0,594,300 · face 580,150,250,270 · ribbon 0,380,560,450 · skirt 400,640,500,384 · torso 560,430,340,300 · curtain 790,270,234,500

## Render loop

`.venv/bin/python scripts/scene_render.py .scratch/05-portrait-scene/work/scene.yaml -o /tmp/s.png --ref image.jpg` (scene file is the FIRST positional arg)
Compare: `scripts/draw compare image.jpg /tmp/s.png --region X,Y,W,H --zoom 2` (view output). Zone probe:

```python
import cv2, numpy as np
ref=cv2.imread('image.jpg').astype(int); dr=cv2.imread('/tmp/s.png').astype(int)
print(round(np.linalg.norm(ref-dr,axis=2).mean(),1))  # per-zone: slice [y:y+h,x:x+w]
```

## Work items (priority order — shading is the biggest lever)

1. **Shading pass (light from upper-left, soft)**: add shadow nodes under the light-blocking forms: hat dome casts on face/top of bangs; hat brim casts on hair/shoulders; collar casts on neck; sleeve folds; skirt fold shadows (soft dark bands along fold creases, following the fold direction); ribbon casts soft tint where it passes over skirt/water. Implementation: `blob` or `stroke` nodes with fill = a darkened version of the underlying color (sample it), `op` 0.25-0.45, wrapped via a `blur` node (std 8-14) so edges are feathered. Shadows must FOLLOW the form: curved on rounded things (hat on face), straight-ish on fabric. One semantic node per shadow, named (`shadow: brim-on-face` etc.).
2. **Strand/fold density**: ref has 3-5× more directional elements. Add: hair strand strokes following the hair's flow direction (look at image.jpg carefully — count and direction vary by region); skirt fold strokes; curtain strand strokes; a few highlight strokes on the hat dome and ribbon (light from upper-left → highlights on upper-left surfaces). Use `stroke` nodes with taper, ink = darkened base or lightened highlight color, w 3-6, op 0.3-0.7.
3. **Ribbon taper**: the green ribbon and its tail should taper toward their free ends (widthProfile or narrower spine segments at ends). The tail end dissolves into the water — let it narrow and lighten there.

## Invariants (hard rules)

- SEMANTIC LAYER ONLY: every node named + justified by a statement about the drawing ("brim shadow falls on right cheek"), never "lower the metric".
- Metrics are signal, never target: log per-zone after each round; a change that worsens a zone >10% gets reverted, not patched blindly.
- A weird diff means upstream error — investigate, don't patch forward.
- Assert every edit landed (grep count before/after); PyYAML gotchas: quote color values; `no`/`on` values.
- View the render and side-by-side crops repeatedly; compare against image.jpg at region zoom.
- Do NOT git commit. Budget ~4-6 render-compare-fix rounds; be efficient (hard 30-min limit).

## Success targets

overall ≤ 55, no zone > +8% vs baseline, shading visibly present in a side-by-side (brim shadow on face, skirt folds, ribbon tint). Report: final zone table, node count, what you added per work item.
