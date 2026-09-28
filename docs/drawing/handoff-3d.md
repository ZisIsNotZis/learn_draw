# Handoff — 3D model session (2026-09-17)

This project draws an anime-girl portrait as a relational 2D SVG spec
(`.scratch/13-assembly/work/spec.yaml`, resolved by `scripts/relate.py` — see
`docs/drawing/abstraction.md`). After nine slices, one defect resists every 2D approach, and the
user has decided to attack it in 3D. This file is the handoff brief for the 3D-model session.

## What the user has decided

Build a **3D model** (any representation — mesh, sculpt, posed mannequin, even a physically
posed figure photo-set) of the seated girl, so that:

1. **The hair** can be understood as ONE 3D sheet attached at the head: the BLUE side is the
   outer face (crown, fringe, the long fall down the figure's right), the MINT/GREEN side is the
   inner face — the underside that the wind lifts, which sweeps up behind the head and streams
   down across the whole lower-left, off the frame. Reference: `head.png` (the user's structural
   exemplar) and `image.jpg` (the target).
2. **The magenta ribbon** can be understood as ONE CONTINUOUS RING around/behind the seated
   body: it leaves the bow knot at the chest, its far half passes BEHIND the body (occluded), and
   its near half re-emerges in front across the bottom-left. The current 2D draft places this ring
   wrongly and the user cannot describe the correct 3D path in words — that is exactly what the
   3D model is for.

## Why 2D failed (nine slices of evidence, `13-assembly/log.md` M3d–M4j)

Every 2D measurement reached reference parity (contour profile within ~10–50px, attachment gap
2px = the reference's ink line, off-frame flow), yet independent reviewers kept reading the mint
as "a separate cape/blanket behind the girl" — and gave contradictory reasons. The user's model
(one region, interior partition, ribbon ring) is now implemented literally in the spec and the
user accepts the HAIR result; only the ribbon ring's spatial position is unresolved. The
hypothesis for the 3D session: a 3D understanding gives a consistent PROJECTION to derive the 2D
anchors from, ending the guesswork.

## How the 3D model maps back to the spec

- The spec is relational: shapes are built from measured anchors and family instances
  (`hair-region` = smooth closed spline; `ribbon` = spine + width; see
  `docs/drawing/vocabulary.md`). A 3D model contributes **projected 2D anchor sets**: pick a
  viewpoint matching `image.jpg`, project the hair sheet's outline (one closed curve) and its
  interior partition curve, and the ribbon ring's centreline with its occlusion intervals —
  those become the spec's `anchors`/`spine` values (measure → fill → close the image, per
  `docs/drawing/method.md`; the 824-hand-typed-coordinates failure is about hand-typing, not
  about measured values).
- Occlusion order comes free: the 3D model tells which parts of the ring/sheet pass behind the
  body — the spec already has the layer machinery (`z:`, `layers:`) to express it.

## Hard constraints the 3D session must respect

1. **The reference is `image.jpg`; the structure exemplar is `head.png`.** The 3D model must
   reproduce THEIR pose and sheet layout, not a generic figure.
2. `image.jpg` facts already measured (trust these): mint right edge ≈x718; blue→mint gap at the
   head = 2–8px (an ink line); the mint has NO bottom edge in the left half (runs to y1023); the
   sheet pales toward the lower-left ((173,213,177) at (100,650)); the blue fall occupies
   x847–1024 y400–793; the ring's re-emergence fills the bottom-left cloth.
3. Output spec must keep: G7 (zero traced nodes — the 3D projection values enter as authored
   anchors with provenance, then any 3D artifacts are closed away), P18 (renders with
   `image.jpg` deleted), invariant 5 (≤4 hand-typed coords per shape — spline anchors are
   measured points).
4. The face/expression is DEMOTED by the user; hair + ribbon are the only open defects.

## Current state (2026-09-17)

- Front artifact: M4j (commit `bf5f4d5`), spec `.scratch/13-assembly/work/spec.yaml`.
- M3 exited (rubric B 4.5 / E 4). M4's F axis reached 4/4 in M4d/M4e; G2 coverage alarm closed at
  M4h (0.591); M4j sits at 0.559 (−0.012, the recorded cost of the user-ordered restructure).
- Reviewer history for the mint read: M3d→M4j in `.scratch/13-assembly/log.md` (nine rounds).
