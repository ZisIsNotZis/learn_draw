# 04 — portrait-torso: torso/dress region (T2)

Status: done (polish deferred to T3 pass)

## Scope
Collar flaps + trim, bow with flowing tail, blouse with jabot ruffles, puffy sleeves, navy cuffs, bare arms with hand-on-hip, navy skirt blown left with pale overskirt and white zigzag hem.

## Result
`work/v4.svg` — the living assembly (bg → hat-underside → TORSO → face-group → curtain → ARMS → hat). All shapes named + commented.

## Acceptance
- [x] outfit reads as ref's: sailor collar, crimson bow+tail, jabot, puff sleeves, cuffs, hand-on-hip, navy skirt blown left
- [x] occlusion: torso under all hair; arms over curtain
- [x] colors sampled from ref
- [ ] polish: bow proportions, shading wrinkles → T3 pass

## Knowhow
- Clothing silhouette = body pose underneath: the skirt reads wrong unless its mass follows the wind/pose, not symmetry.
- Assembly grows in one file; regions splice in via ElementTree extraction (face group) or direct blocks.

## Comments
- 2026-09-10 agent(pi): 4 iterations. Key fix: skirt billow direction + organic hem zigzag (v3-v4).
