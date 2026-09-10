# v20 rebuild changelog (13 rounds)

- r1: clean rebuild from salvage + measured geometry; base structure well-formed
- r2: skirt dark mass enlarged (hem extended); yellow overlay repositioned (480-615, 872-1024)
- r3: DIAGNOSIS: petals at op 0.75 covered ~30k px of skirt center -> shrunk + op 0.4
- r4: celadon piece shrunk; skirt navy 49.2k (near target)
- r5: pink/yellow overlays softened (op .45/.42 + blur) — class map still wrong at hem
- r6: pink overlay MOVED to measured hem band (424-544, 880-1010) per class map; ribbon pulled in
- r7: left zigzag triangles shrunk (ref shows pink there, not white)
- r8: CLASS-MAP DISCOVERY: ref dark skirt fills bottom-LEFT (x100-400) — dark blob extended left-down
- r9: white skirt body left edge pulled right (fringe stays dark); petals shrunk
- r10: petals moved up (still wrong zone)
- r11: zigzag triangles right of x570 removed (ref hem is dark there)
- r12: white hem up-right; petals deleted (misread - ref shows GREEN behind girl); green-behind wedge added
- r13-14 (v13/v14 earlier): ribbon rebuilt from grid anchors
- Final: all 7 success criteria pass programmatically; class agreement 69% overall

## Orchestrator verification round (v21)
- Independent probes: skirt navy 32.9k vs REF 32.0k (same zone) PASS; brim 6.5k vs REF 5.8k PASS
- Original 50k/8k targets were miscalibrated (ref itself measures 32k/5.8k) — corrected
- Root causes fixed: dome/band self-intersecting polygon split into two clean paths; old light-layer stack (celadon/white/zigzag) deleted; pink overlay clamped out of skirt zone
- Residual: detail density + shading (critic backlog), overall color_dist 62.6 (v17: 74)
