# 05 — portrait-scene: ribbons/background T3 + full assembly

Status: FROZEN 2026-09-14 — superseded. Kept for evidence only; do not continue this exercise.

Why frozen: this exercise was one ticket doing several things at once (learn T3 soft fields *and*
assemble the whole figure *and* rebuild *and* introduce a layer stack), which is why it accumulated
8 briefs, 29 work files, and never closed. Diagnosis + the computed-geometry comparison live in
`evidence/diagnosis/`. Replaced by `.scratch/06-relational-geometry/` (the authoring language) and
the L1–L6 ladder (08-bust → 13-assembly), per `docs/drawing/abstraction.md` and principles P18–P21.

## Scope

bg gradient, giant green ribbon body, purple tail curl, white ribbon strips, translucent pink/yellow/green overlays on skirt, pink ring curl, hair-wall strand detail, full-assembly integration of all regions.

## Result

`work/v6.svg` (render: `evidence/v6-render.png`). Gradients + opacity via SVG defs; shapes contour-extracted or scanned.

## Acceptance

- [x] T3 techniques working: linearGradient, opacity, soft translucency
- [x] ribbon family present and roughly placed
- [x] cross-region fix: face width +40px right side (assembly revealed it)
- [x] critic: self-critique (subagent 429) — findings applied (curtain notches, ribbon flow, tail, bow)
- [ ] polish backlog: strand micro-detail depth, ribbon top wave line, pom fluffiness, bow fold shading

## Knowhow

- Attribute-surgery bug class: coordinate-pair regex replacement must preserve attribute syntax — verify render after any generated-attribute edit.
- Degenerate notches: a V notch needs lateral apex offset from the tip midpoint, else fill reads solid.
- Assembly-time review catches seam errors invisible per-region.

## Comments

- 2026-09-10 agent(pi): 6 iterations; face/hair/torso/scene regions integrated.

## Critique (fresh-eyes delegate, v14, 2026-09-10)

Full critique verified in task artifacts (de2a05464fa9a578ee385e0b2f24e9699). Themes:

1. Detail density (hair walls, ribbon body, dress = empty flat fields) — most damaging
2. Translucency: overlays opaque with hard borders → need feathered edges (blur) + alpha gradients
3. Ribbon: needs tapered ends + wave; water band has hard top edge (should be atmospheric)
4. Shading: no light-direction modeling anywhere; bg flat
5. Smaller: bow crisper, brim sweep, face slightly wide, neck junction
Applied already in v15: pink flower, arm shadow tint, neck (v9), dome down (v4).
Backlog: soft-edge pass, density pass, ribbon taper/wave, water atmospheric, bow/brim nudges.
