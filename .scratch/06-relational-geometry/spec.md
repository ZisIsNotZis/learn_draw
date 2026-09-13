# 06 — relational geometry: the drawing language

Status: done — agent(pi) 2026-09-14 (prototype scope; see Acceptance deviation note)
Blocked by: —

## Issue

The portrait failed because the only way to place geometry was absolute coordinates (824 hand-typed
vertices across 58 polygons in `05-portrait-scene/work/scene.yaml`; `trace` used 0 times). The
high-level abstraction we actually want does not exist yet: there is no way to say *"the brim is
about twice the head wide, tilted ~20°, sitting on top of the head"* and get resolved geometry.

Design constraint (user, 2026-09-14): **the engine must never depend on the target image.** Tracing
a reference is the *teacher* for a scene file, not the engine. The end goal is drawing without a
reference, so the resolver must be able to produce a whole drawing from high-level intent alone.

## Scope

Minimum relational layer that L1 (bust) needs — not a general constraint solver.

Three tiers:

1. **Anchors** — canvas frame + per-shape handles (`head.rx`, `brim.right`, `brim@0.35`).
2. **Relations** — expressions over anchors: `between(a,b,t)`, `on(shape,t)`, `off(p,angle,d)`,
   `at(shape)`, arithmetic with units (`1.8*head.rx`, `frame.w*0.62`).
3. **Vocabulary** — parametric object families with drawing-sane defaults (`sunhat`, later `eyeball`,
   `strand-mass`, `sleeve`) so the model names an object instead of deriving its structure.

Plus **semantic diagnostics** — the resolver reports derived facts in words (off-canvas, invisible
behind, unintended gap, z-order contradicted by declared relation), because the model has no
numeric sense of a 1024² canvas.

## Acceptance

- [x] `relate.py` resolves a spec with **zero numeric coordinate literals** to absolute geometry.
      *Deviation, recorded honestly:* it emits absolute nodes through its own small emitter rather
      than routing into `scene_render.compile_scene`. The node schema is identical, so integration is
      available, but it is **deferred to the first drawing that needs it** (L1 wants `region`/`trace`
      for computed geometry, and generators for cloth) — per this ticket's own last criterion, no
      speculative generality.
- [x] `along(shape, t)` works for rotated ellipses (poms placed at t=0.62/0.88 on a −14° brim).
- [x] Diagnostics implemented and exercised: OFF-CANVAS, CLIPPED, SUB-PIXEL, CONTRADICTION (z-order
      intent vs layer stack). Two fired on bust v1 — my own wrong layer order, and shoulders 68px past
      the frame edge.
- [x] Anchor table printed (`--anchors`) — the model's substitute for numeric intuition.
- [x] Proof render: a readable sun hat + head from a 10-node spec whose hat is ONE relational line.
- [x] Every addition justified by a spec that needed it: `vars:` (the spec referenced `head_half`),
      `sunhat` (the hat itself), `along`/`host` (YAML 1.1 turns `on`/`off` into booleans — now a named,
      diagnosed error rather than a cryptic KeyError).

## Result

`work/relate.py` + `work/bust.yaml` → `evidence/bust-v1.png` (2 diagnostics, both real defects) and
`evidence/bust-v2.png` (diagnostics clean). Loop cost: three word-level edits → re-render in ~2s.
Doc: `docs/drawing/abstraction.md`. Principles: P18–P21.

## Comments

- 2026-09-14 agent(pi): ticket created after diagnosis (`.scratch/05-portrait-scene/evidence/diagnosis/`).
  Prototype first, grow only from L1's needs.
