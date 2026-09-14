# 09 — L2 torso: blouse, collar, bow, arms, hands

Status: ready-for-agent (blocked)
Blocked by: 08-bust

## Issue

Rung 2 of the ladder. Body below the neck: sailor collar, bow, blouse, puff sleeves, cuffs, bare arms,
hands. Each of these is a small object with its own occlusion story (arms over the curtain, hands
tucked behind the body) — the failures that dominated the portrait's `body` layer.

## Scope

Compose on top of the closed L1 bust spec: same canvas, same frame, reference-seeded values.
Arms and hands are the hard part (P17: hands sitting behind the body are a z-plane question, not a
path question — declare the relation, let the renderer occlude).

## Acceptance

- [ ] renders with the L1 bust on top of it; diagnostics clean
- [ ] occlusion stated, not hand-solved: `relations:` declares arms-over-curtain and hands-behind-body,
      and the engine raises CONTRADICTION if the layer stack disagrees
- [ ] fresh-eyes review: body reads as a body; no floating or detached limbs
- [ ] ≥1 vocabulary node added here (e.g. `sleeve`, `eye`-style family for the bow) *justified by a
      failure without it* — recorded in the ticket Comments
- [ ] iteration log + evidence composite

## Comments

- 2026-09-14 agent(pi): created as rung 2; depends on 08 for the frame and the head anchors.
