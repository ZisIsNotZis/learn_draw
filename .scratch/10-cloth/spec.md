# 10 — L3 cloth: skirt, pleats, folds

Status: ready-for-agent (blocked)
Blocked by: 09-torso

## Issue

Rung 3. The dark pleated skirt and the blouse folds. In the portrait these were the worst-scoring
zones (skirt 88.4, torso 86.3) and the "amount matched, arrangement drifted" failure —
flat navy fields with no fold structure.

This is the first rung where a *generator* earns its place: pleats and fold runs are regular and
should come from parameters (P15), not from hand-placed polygons.

## Scope

Skirt silhouette, pleat generator, fold shading, hem. Blouse fold runs along tension lines.
Style reference for fold *direction*: `cloth.png` / `dress.png` plates (verified redrawn — style
only, never a geometry source; P16).

## Acceptance

- [ ] pleats come from a generator with parameters (count, depth, taper, seed); changing count is a
      one-value edit with no other side effects
- [ ] fold runs follow tension lines read from the reference, not evenly-spaced stripes
- [ ] skirt silhouette is ONE shape (P8: model the mass, not an assembly of parts)
- [ ] diagnostics clean; fresh-eyes review finds no "flat / mushy / no structure" complaint
- [ ] iteration log + evidence composite

## Comments

- 2026-09-14 agent(pi): created as rung 3; T3 soft shading is deliberately NOT here — it stays last
  (rung 5) because reaching for it early is what produced the portrait's mush.
