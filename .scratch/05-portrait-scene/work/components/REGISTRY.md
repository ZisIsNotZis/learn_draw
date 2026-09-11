# Component registry (Phase 0 output, 2026-09-11)

Source plates: repo-root 2048x2048 opaque PNGs, flat grey bg. Extracted to
`work/components/{name}-plate.png` (bg→transparent) + `{name}-mask.png` (binary fg),
both 1024-space. Extractor: `work/extract-components.py` (bg-diff + morphology + largest-CC).

Alignment = cv2 TM_SQDIFF w/ mask, scale scan 1.7–2.3. Scale 2.0 ⇔ 1:1 with ref.

| plate | visual content | scene role (layer) | ref alignment | usable as |
|---|---|---|---|---|
| hat | wide-brim blue hat + peaches | `hat` | 1:1 at (0,0) | position-true ref |
| head | head + blue→green hair gradient | face/hair ref | off-scale (illustrative) | color/shape ref only |
| head_hat | head+hat combined | z-order proof (#5/#7) | 1:1 at (0,0) | position-true ref |
| dress | **dark pleated skirt w/ teal ruffle trim** | `dress-black` (#4) | REDRAWN — no ref match | style ref (draw from it, not trace) |
| cloth | white blouse + red bow, no skirt | `dress-white` folds (#2) | REDRAWN — no ref match | style ref |
| ribbon | rainbow swirl energy | `ribbon-back`/`ribbon-front` (#6) | 1:1 at (0,0) | position-true ref |
| cutout | grey silhouette base | n/a (asset artifact) | off | ignore |

Ambiguity from REBUILD-v2-BRIEF resolved: dress.png = skirt (dress-black), cloth.png = blouse only.
