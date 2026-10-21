# The joint is what fails, not the object — hypothesis, replacement route, experiment

State: proposal, written 2026-10-21 by the owner of the `go` package at root's contract
`inbox/2026-10-21-method-contract.md` (read, landed, deleted). It changes no gate: R1a's exit is the
person's judgement of a picture. It names the one thing the next R1a package tests, so that the fifth
attempt is not the fifth attempt of the same idea.

## Why this document exists

Four image verdicts across two subjects — bow v1/v2/v3, hand v1-r1 (twice) — and each pass cured the
mechanical class the previous verdict named and the picture still did not read: the specs converge, the
pictures do not. Both subjects' failures are statements of the same shape:

- bow v2 (J): *no edge crosses any other*; capsules stacked on the lobe; the knot a closed pouch.
- bow v3: *nothing in the picture threads*; a complete horizontal capsule drawn on top of the left
  lobe and the down-tail; both lobe contours close all the way round with no mouth opening.
- hand v1-r1 (K, K2): *no flesh crosses the plate's near outline*; the fingers' first unbroken row lies
  below the rim and narrows downwards, so the picture is "a dish in front of straps".

Every one of those is a claim about a relation **between two masses in the picture's plane**. Every
measurement the packages were green on is a claim about **one mass against a surface in space**: pad
1.60–4.26 px from the dish, palm 1.50 px, occlusion break 91/91, 15/15 and 25/25 suites. The gate reads
the first kind; the work verified the second. That gap, not any single object's geometry, is what four
verdicts have been re-discovering.

## 1. The hypothesis now under test (H1)

> **H1 —** in this project's method a joint is built as *tangency*: each part is solved to terminate
> **at** the other body's boundary (distance-to-surface, abutting, stacking). A joint built that way can
> never read, because a drawn joint reads only where **exactly one** of the two contours terminates on
> the other and the other continues unbroken — a T-junction with a front/rear order. Under H1 no further
> per-object precision changes the reading, because precision at tangency sharpens the wrong relation.

Two species, both observed in the tree, both instances of the one class:

- **merge** — the two contours both complete and touching, so the rear edge and the front edge smear
  into a single dark scar (bow v3: the ~12 px scar where the lobe contour meets the capsule edge; the
  capsule lying *on top of* the lobe rather than passing through it).
- **uniform order** — one order holds across the whole joint, so the occlusion is real but says the
  wrong thing: every pixel of the hand is behind the dish, so the picture says "in front of" and never
  "holding" (hand v1-r1: measured on `check/draft-fullres.png`, sha256 `e66d7218…` — at bottom centre
  x=450 the near-rim band runs y 414–482 and flesh begins at y=483; **52 of 317** flesh-bearing columns
  have rim directly above their topmost flesh pixel, i.e. the flesh is cut by the dish, never over it).
  A grip needs the opposite: **mixed** order across one joint — at least one digit in front of the near
  rim, the rest behind it.

Prediction H1 makes, and that is cheap to falsify: mechanical contact accuracy and image-space *order*
are independent. On both current packages the first is green to 1.5–4 px while the second carries one
order only.

**H0, the alternative that has to die for H1 to be worth a package:** the crossing exists in the geometry
and the renderer drops it. It is now nearly dead by the same measurement: the hand's picture *does* show
occlusion — flesh terminating exactly at the rim in 52 columns — so the renderer applies depth order to
this pair; what it never gets is a reason to put a digit on the other side. What the experiment in §4
still settles is the remaining sliver of H0: whether a declared front digit is actually drawn in front at
a crossing of a few tens of pixels. If the pixels disagree with the declaration, the class is the
renderer's, not the drawing's, and it is escalated as such.

## 2. The replacement route: solve the contact in the picture's plane

The change is at the level of what a joint *is*, so it applies to both subjects and to R1b after them.
Four rules, each with the check that refuses it:

1. **A joint is declared before it is built.** Front piece, rear piece, and the region in which the
   front piece's projection lies inside the rear piece's outline. A joint without a declared crossing
   region is not a joint, it is two objects near each other, and the package is not accepted.
2. **The crossing has an area floor, in pixels, on the rendered image:** front-piece fill inside the
   rear piece's outline ≥ **1 % of the rear piece's projected area** and ≥ 10 × stroke-width². The floor
   is relative to the object, so it does not invent an absolute number, and it scales with framing.
3. **Exactly one contour breaks.** Across the crossing span the front piece's contour is unbroken and
   the rear piece's contour terminates on it, with no spur and no smear; a junction where both contours
   survive is a *merge* and fails, and one where neither touches is a *miss* and fails.
4. **The pose is chosen so the crossing exists before rendering.** For the hand this means at least one
   digit is solved against the surface it *presses* (the dish's upper/inner surface over the near rim),
   not against the surface it hangs under: an underside-only contact is, by this construction's own
   measured result, always behind the plate and therefore never depictable as a grip.

The check lands in the package's own `check` report as pixel counts on the shipped PNG, produced by the
documented command, so the evidence sits where the gate is judged rather than a plane away from it. The
class this kills is the one named in the acceptance ledger as the drift class — evidence that can drift
from the thing it judges — extended to the joint: a joint's evidence is now a measurement of the picture.

## 3. Which subject is cheapest

**The hand.** Ranked on the decisive axis — how much of the existing package survives the route change:

- Its contact solver already terminates against a real surface with a measured error (`contact.py`,
  palm and pads solved against `util.underside_surface`); H1's change for it is *which* surface the
  digit presses, which is one parameter of one solver, not a new construction.
- It has the mature harness: 25/25 suite, a negative-control record that cannot drift, a 1:1 check
  report, a verified manifest, byte-identical rebuild. The new pixel test plugs into it.
- Its rear piece is one large legible silhouette (the dish) with a wide near-rim band, so a crossing is
  large and easy to measure. The digit to move is one of five, ≈ a quarter of the pose code.

The bow is the more expensive one and not by a little: its crossing is *intra-strip* self-occlusion, so
front/rear must be resolved inside a single mesh, and the occluder is the knot — the exact thing three
verdicts failed at. It has no second body that can be in front. It is not refused forever, only after
the route has been shown to work on the cheap subject.

## 4. The bounded experiment: package `B-hand-study-v2-rimwrap`

- **goal** — one digit wraps the dish's near rim so that its pad rests on the dish's inner surface and
  its fill occupies ≥ 1 % of the dish's projected area inside the dish's outline; hand, dish, palette,
  framing and every other digit unchanged from `B-hand-study-v1-r1` at `3fc2311`.
- **scope** — the pose/route of one digit and its contact solve against the inner surface; the joint
  audit added to `check/report.txt` and one test that measures it; no palette, tessellation or stroke
  weight change; a new package directory copied from the frozen r1, which stays untouched.
- **accept** — `.venv/bin/python scripts/draw.py check …/B-hand-study-v2-rimwrap/artwork.svg` reports
  `cross_px` ≥ the floor of §2 rule 2, `contour_breaks` 0 across the crossing span, and lists both
  numbers on line 1 beside the 1:1 image; the suite is green and the new test **fails on r1's geometry**
  (the negative control that makes the test mean something); rebuild byte-identical; manifest verified;
  and a fresh image-only reviewer answers the one question — *is any flesh visibly over or inside the
  near rim, and does it read as holding the dish?* The reviewer's verdict, not the counts, decides the
  art gate; R1a's exit stays the person's judgement of the picture.
- **paths** — `.scratch/35-r1-articulated-study/evidence/B-hand-study-v2-rimwrap/`; `scripts/` and
  `scripts/tests/` for the shared solver only if the solve cannot stay local.
- **spend** — machine_time, idle class; no device held exclusively; no money; one writer ~25 min
  wall-clock, one fresh reviewer ~12 min; nothing for the person.
- **stop** — attempts 1, review rounds 1, no-progress rounds 1; writer wall-clock 25 min, and it lands
  what exists at 20.
- **failure routes** — (a) `cross_px` reaches the floor and the picture still fails ⇒ H1 is refuted at
  the joint route; the next hypothesis is the crossing's *shape and placement* (whether the crossing sits
  where the silhouette is most legible), and no third variant is attempted before that is written down
  and reported with its cost. (b) The pixels contradict a declared front/rear order ⇒ H0 is alive and
  the class is the renderer's; it is escalated as a renderer class, not repaired inside a drawing.
  (c) The digit cannot be posed to press the inner surface without breaking an existing surface
  contract ⇒ report the blocker with the measurement, do not widen the package.

## 5. What this proposal does not do

It does not move R1a's gate, does not re-attempt either study along the route that failed (no bow v4; no
underside-only hand), and does not claim a picture is good. It spends no writer: this document is the
proposal, the experiment is cut and unlaunched, awaiting the word that opens the next session.
