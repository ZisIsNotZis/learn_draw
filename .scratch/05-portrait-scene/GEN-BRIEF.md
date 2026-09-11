# GEN BRIEF — generator nodes + holistic re-expression

Read first: docs/drawing/scene-format.md, docs/drawing/principles.md (esp. P14, P15). Reference: image.jpg.

## Phase A — two generator node types in scripts/scene_render.py (schema + compilers + 2-3 smoke tests each)
1. `wave`: keys = wave (id), spine (few control points, 2-5), w (base width), amp (wave amplitude px), len (wavelength px), sag (gravity droop px per horizontal px of spine), taper (end|both|none), fill|grad, op, z.
   Compiler: resample the control spine into a smooth curve, displace points perpendicular by amp*sin(2π s/len), add sag = sag * (x_progress) droop (gravity down = +y), then build a ribbon via perpendicular offset by width profile (taper at ends). Emit as closed filled path (like taper_outline).
2. `strands`: keys = strands (id), region ([x0,y0,x1,y1]), n (count), dir (degrees, flow direction), spread (deg jitter range), w (base width), wj (width jitter 0-1), ink (base color, or [color1,color2] alternating), op, len (strand length px, follow dir), z, seed (int; deterministic via np.random.default_rng(seed)).
   Compiler: n strands seeded inside region, each: start point uniform in region, direction = dir ± spread jitter, length = len ± 20%, slightly curved (small perpendicular bow), width = w ± wj jitter, emit as stroked paths. Deterministic given seed (smoke test: two renders byte-identical).

## Phase B — re-express .scratch/05-portrait-scene/work/scene.yaml holistically
- Green ribbon body → ONE wave node (spine ~[[20,390],[560,380],[520,570],[392,772]], amp ~15, len ~250, sag ~0.15, w ~110, grad ribbonGrad, op 0.9). Ribbon tail → ONE wave (taper end, lighter toward tail end via grad or lighter fill).
- Hair: keep the masses; replace hand-placed hair-strand-* strokes with 2-3 strands generators (region = right hair area / left curtain area, dir following the visible flow — LOOK at image.jpg, n ~8-12 each, seed fixed).
- Curtain (right wall of hair): strands generator, dir ~80-100°.
- Skirt fold shadows: keep semantic folds; consider 1 strands generator for crease direction if it reads better.
- Delete the point-soup polylines that these replace. Every node keeps semantic name + intent comment.
- Render + view the FULL frame repeatedly against image.jpg; the drawing must read as whole objects, not fragments. Keep zone metrics as weak regression signal only (overall should stay ≤ ~65); do NOT tune parameters against metrics — tune by looking (P14).

## Acceptance
1. New smoke tests green; all old tests green (adapt any broken by the schema additions).
2. scene.yaml ≤ ~70 nodes, no node with >30-point poly except where genuinely needed.
3. Render viewed and judged: ribbon reads as one flowing ribbon with sag; hair strands flow naturally; no fragment-patch artifacts.
4. Parameter demo: change ribbon amp 15→30 and sag 0.15→0.3 → visibly wavier/droopier ribbon, nothing else moves.
Report: test results, node count, what you replaced, before/after overall (weak signal), and your own visual judgment of the result. Do NOT git commit.
