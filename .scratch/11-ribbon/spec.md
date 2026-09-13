# 11 — L4 ribbon: the generated band

Status: ready-for-agent (blocked)
Blocked by: 09-torso

## Issue

Rung 4. The ribbon is the reference's signature element and the portrait's most embarrassing
failure: the `ring` generator produced a rainbow zigzag annulus that reads as a flower, not cloth.
The generator exists and is tested; what was missing was the *structure statement* and a way to
describe its path in relations rather than a fitted ellipse.

## Scope

One ribbon, from relations: a path that sweeps across the frame, wraps behind the figure and re-emerges,
with tapered ends and a colour walk. Reuse `wave` + `ring` (P17 z-plane split for the wrap), but
re-express the placement in `docs/drawing/abstraction.md` terms instead of fitted absolute geometry.

## Acceptance

- [ ] ribbon reads as *cloth* under fresh-eyes review: a band of roughly constant width with taper at
      the ends and a visible near/far edge, not a wheel/fan
- [ ] the ring's teeth/zigzag depth is a stated parameter justified by the reference, or removed
- [ ] wrap-around is two complementary arcs sharing geometry + seed, declared as a relation, never
      pre-split paths (P17)
- [ ] diagnostics clean; iteration log + evidence composite
- [ ] if a `ribbon` vocabulary node is added, its parameters are documented in `abstraction.md`

## Comments

- 2026-09-14 agent(pi): created as rung 4; depends on 09 only for the torso silhouette to wrap behind.
