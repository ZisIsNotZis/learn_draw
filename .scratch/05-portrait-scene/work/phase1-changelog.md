# Phase 1 — layer-stack restructure (REBUILD v2 defect #7)

Layer order BEFORE (bottom→top): bg, ribbon, skirt, body, hair, hat, overlays
Layer order AFTER (user-mandated): bg, hair-behind, ribbon-back, dress-black,
  dress-white, body, hair-front, hat, ribbon-front

Changes:
- green-behind/green-overlay moved overlays→hair-behind (defect #5: hair mass behind body)
- pink-overlay → ribbon-back (rear ribbon glow); yellow-overlay → ribbon-front (front arc glow)
- skirt-* blobs promoted to dress-black (dark navy: 5 blobs) + dress-white (light apron + creases)
- all hair nodes → hair-front; ribbon nodes → ribbon-back (front arc lands in Phase 2)
- fold shadows retargeted to dress-black/dress-white
- render: color_dist 60.8 → 66.2 (green no longer front-blanks body; metrics are signal not target per P14)
