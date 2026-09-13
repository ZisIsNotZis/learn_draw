# 13 — L6 assembly: the whole figure, from relations only

Status: ready-for-agent (blocked)
Blocked by: 12-fields

## Issue

Rung 6. Compose L1–L5 into one figure at 1024², and make the composition itself a relational
statement — the thing the portrait could never do because every part was absolute coordinates that
had to be hand-fitted against every other part.

## Scope

One spec that composes the rungs by reference (head/torso/cloth/ribbon/fields), declares the whole
layer stack, and states the occlusion intent for every overlap. Re-tuning composition = editing
relations, not re-fitting geometry.

Validation of the frame itself: the subject's placement is a relation to the frame (`frame.w*0.60`),
never an eyeballed number.

## Acceptance

- [ ] whole figure renders from one relational spec; diagnostics clean
- [ ] `relations:` states every overlap in words and the engine raises none as CONTRADICTION
- [ ] a composition change demo: move the figure and scale the hat by editing ≤3 expressions, with the
      rest of the drawing following correctly (this is the acceptance test 05 scene-format migration
      wrote for itself and never passed)
- [ ] fresh-eyes review on the whole frame: reads as a proper artwork in the reference's style (P14) —
      the primary criterion, not zone distance
- [ ] node count ≤ ~80; no node carries more than 4 hand-typed coordinates
- [ ] evidence composite + final log row; principles distilled

## Comments

- 2026-09-14 agent(pi): created as rung 6. This is the rung that replaces frozen 05.
- Follow-on work (separate tickets, not here): redraw the assembled figure from its own spec with the
  image closed, then draw a new subject from intent alone (the no-reference goal).
