# 02 — portrait-face: face region of image.jpg (T1+T2)

Status: done (hair-strand micro-detail deferred to hair exercise)

## Scope
Face region crop (image.jpg @ x580,y150, 250x270 → 2x = 500x540): skin, eyes (8-layer stacks), brows, nose/mouth marks, occluding hair as flat regions, neck/collar, bg, hat corner.

## Result
`work/v7.svg` — semantic groups: scene/face/eye-left/eye-right/hair; all paths named + commented. Evidence per iteration in `evidence/`, reflections in `log.md`.

## Acceptance
- [x] eyes: correct layering (sclera/lid-band/iris/green/glints/lash), shape close to ref
- [x] hair: one zigzag silhouette from traced boundaries; pockets correct
- [x] marks: nose tick + mouth dash located and drawn (identity confirmed by zoom)
- [x] occlusion semantics: strand over left eye, jaw behind curl, waterline n/a
- [x] principles P8-P12 distilled

## Deferred
- hair internal strand detail, curl micro-shape → hair exercise (next region)
- T3 soft shading not in scope for face crop yet

## Knowhow
Boundary tracer (scanline color-classification) = the decisive tool this exercise; promoted to inline use, consider `measure --trace` promotion later. XDoG ref unusable for eyes (P10).

## Comments
- 2026-09-10 agent(pi): 7 iterations. Key pivots: eye study via 3.5x crops (v1), silhouette-model realization (v3), seam discipline (v4), hat/teal correction (v6-v7).
