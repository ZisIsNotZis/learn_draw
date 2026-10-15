# S1b composition — bounded first slice

## Before changes: interpretation, scope, proof plan

Interpretation: construct one reference-independent, coarse seated-figure composition from semantic components using the existing spatial scaffold and opaque depth visibility, and show one changed pose through a named pose parameter rather than edited projected coordinates.

Scope: one exercise record only. Reuse `scripts/figure_scaffold.py`, `scripts/vector_visibility.py`, and the accepted component construction/interface lessons in [S1a construction and learner-card interface](../31-s1a-teaching-artifact/spec.md). The scaffold pose, ribbon route, hair shape, and recognition are hypotheses. No reference fitting, S1a readability claim, learner run, line art, finish, new backend, renderer repair, baseline change, vendor/staged/raw-evidence/principles edits, or review claim. Coarse silhouette and component attachment precede face detail; use the existing coarse component geometry and do not expand facial detail.

Proof plan: produce a deterministic two-view baseline and a second pose using a compact pose angle applied consistently to the right arm/hand; use the same named component surfaces and `visible_fragments` depth behavior. Run existing figure scaffold and vector visibility tests, render the exercise, verify outputs and local links, inspect source for named components and absence of author visibility cuts, and record exact commands/results. These are construction/render integrity checks only. Recognition, pose, front/back and attachment visual review is delegated to a fresh reviewer; S1a readability remains OPEN and learner transfer UNRUN.

## Construction rule and interface

The existing scaffold supplies coarse parametric ellipsoids for head, torso, lap/skirt, arms, hand, bow, and hat/hair, plus one continuous ribbon mesh and head-attached hair sheet. Ellipsoid center/radii and mesh subdivisions compute surface geometry; the hair sheet root z is derived from the head ellipsoid's upper surface at each root point, not hand-authored contours. Component identities are names on triangles. Depth resolution comes exclusively from the reused `visible_fragments` call. The added composition runner varies the right arm and hand together by a shoulder-relative angle in world geometry before either view is projected; it does not alter screen coordinates or declare visibility ranges.

Run from repository root:

```sh
.venv/bin/python .scratch/32-s1b-composition/work/compose.py --out-dir .scratch/32-s1b-composition/evidence
```

It emits `two-view.svg` and `pose-variation.svg`, each with the same two cameras (0° and 43°); the second drawing changes the right-arm shoulder-relative pose angle by a fixed semantic amount. The ribbon remains a single support component and its route is an unvalidated hypothesis, not the reference route.

## Limits / gates

This is a bounded composition construction, not an accepted drawing or reconstructed pose. Parametric ellipsoids are intentionally coarse and cannot establish anatomical plausibility or recognition. Bow/ribbon contact, hair attachment and near/far ordering require fresh independent visual review. The resolver is an opaque-triangle bounded reference implementation with documented degeneracy/coplanar limitations. S1a visual/readability is formally OPEN; learner transfer is UNRUN. No style/colour finish or semantic line design is attempted.

## Evidence

- Prior construction hypothesis: [`scripts/figure_scaffold.py`](../../scripts/figure_scaffold.py); depth implementation: [`scripts/vector_visibility.py`](../../scripts/vector_visibility.py).
- Reused component construction/learner-card rules and limits: [accepted S1a artifact](../31-s1a-teaching-artifact/spec.md).
- Runner: [`work/compose.py`](work/compose.py).
- Render outputs: [`evidence/two-view.svg`](evidence/two-view.svg), [`evidence/pose-variation.svg`](evidence/pose-variation.svg).
- Required independent recognition/pose/front-back review remains pending; learner transfer UNRUN.
