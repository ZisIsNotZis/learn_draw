# 2_GOAL — what success means: the acceptance questions, the rubric's six axes and their anchors, alarms versus gates

This file owns the definition of success: the product goal and the invariants that keep it honest, the
rule that a milestone is an artwork, the four acceptance questions, the rubric's six axes with their
anchors and thresholds, how the score vector is read, why metrics are alarms rather than gates, the
alarm gates, and the similarity alarm as an instrument.

It does not own how a review is run (see `4_USECASE.md`), how anything is built (`5_PRODUCT.md`
through `9_IMPLEMENTATION.md`), milestone promises, gate definitions and current state
(`0_ROADMAP.md`), or the binding rules `P1`–`P40` (`3_REQUIREMENT.md`).

# EXPLICIT

## The rubric's scoring rules are explicit and checkable, so two independent reviewers land within ±1

The axes of the rubric each carry explicit and checkable scoring rules, so that two independent
reviewers land within ±1, and so that a reviewer's disagreement is diagnosable rather than vague.

# INFERRED

## The product goal

Learn by reference study, imitation and deliberate variation to create explainable, readable,
artistically coherent programmatic illustrations, eventually making reasonable original work without a
reference (including a Starry-Night-like challenge). Treat local vendor examples as a curriculum to
systematically assess and absorb all useful non-image-generation methods, combining proven methods
with existing primitives, 3D support surfaces and depth visibility. Vendor content is not presumed
correct or already learned. Models may inspect references but author text/code only; no generated
images, sprites or pixel-metric optimisation. A reference teaches, it is not runtime geometry.

## A milestone is an artwork, not an engine

A milestone is a user-perceivable artwork or newly demonstrated visual capability, not an engine, test
suite or document. The artifact must be current, reviewable, and ready for the user's judgment. After
each delivery, stop dependent work at the user feedback gate. Internal study, methods, work-package
sequencing and technical replanning are project-autonomous; the user is not asked to decide internal
plans. Internal checks are never represented as the user's judgment, and art success is never promised
in advance.

## Four acceptance questions, kept distinct

1. **Construction/attachment/pose:** do named parts form plausible connected objects and attach in a
   readable pose?
2. **Physical geometry and visibility:** are solids/surfaces free of illegal intersections (or is a
   designed bend/contact explained), and does depth independently hide the physically farther surface?
   Correct occlusion does not excuse interpenetration; a hair strand entering a head/body must be
   plausibly divided/deformed or routed clear.
3. **Drawing/art:** does the actual rendered image read clearly and feel compositionally/artfully
   coherent, with intentional line and colour treatment?
4. **Object cohesion:** does every named object read, in the actual rendered image, as one connected
   visible thing, with any intentionally split object documented as a deliberate split? This is
   separate evidence from construction, geometry and art, because a drawing can pass all three while
   one object still renders as two detached pieces and only the image shows whether it reads as one
   thing.

## Each gate requires its own evidence

Each relevant gate requires its own evidence. Geometry/code cannot establish visual quality.
Experience checks use real rendered visual artifacts and a qualified sight-capable independent
reviewer; actual experience is not runtime-enforced. Missing modality is BLOCKED/UNVERIFIED, never
PASS. Metrics are alarms only.

## The rubric, and why pixel metrics are only alarms

Pixel metrics cannot tell whether a drawing **reads**. They measure edge coincidence and colour
distance against a reference, so a traced copy scores well and a good drawing of a *different* subject
scores badly. `P14` already makes *looking* the primary criterion; the rubric makes that judgement
specific, actionable and comparable, so it can be done by an independent subagent and used as a gate.
The pixel metrics remain as alarms (`0_ROADMAP.md` G2): they catch deletion and breakage, and they
never decide what is good. The rubric decides.

## The six axes (0–5)

Each axis is scored 0–5. Anchors are the contract: score the anchor, not the effort.

## A · Subject identity

*Does it read as this character?* Score on **tokens**, and require ≥3 of the 4: `[1]` blue hair, `[2]`
a wide-brimmed sun hat with pom-poms, `[3]` a pale dress with a large chest bow, `[4]` the seated pose
with a dark mass across the lap.

- **0** ≤1 token. **2** 2 tokens. **3** 3 tokens. **4** all 4 tokens, but the pose, scale or framing
  differs from the target. **5** all 4 tokens *and* the pose, scale and framing match the target.
- Deduct 1 if the **face** reads as blank or dead-eyed rather than the target's shy downcast look.

## B · Human figure

Score on the checklist `[1]` neck, `[2]` both arms, `[3]` at least one hand with fingers, `[4]` a
connected lower body (torso reaching the skirt/lap), `[5]` no phantom limb below the hem, `[6]`
head-to-body proportion plausible for a seated figure (~1:3–1:4):

- **0** ≤1 item. **1** 2 items. **2** 3 items. **3** 4 items. **4** 5 items. **5** all 6.
- A limb that is drawn but **floats unattached** does not count.

The reference's lower silhouette is skirt cloth and streamers only: there is no knee or leg in
that region of the original, and tan or pale blobs there read as skirt and ribbon. A limb drawn
below the hem is the defect item `[5]` scores, not a feature.

## C · Silhouette coherence

The figure must be **one connected mass**. Score on `[1]` head connects to the torso (no background
band at the neck), `[2]` the torso connects to the skirt/lap (no background band at the hem), `[3]`
the arms connect at the shoulder, `[4]` no floating bar/shape with no anatomical source, `[5]` no shape
crossing the frame edge that the reference does not also cross:

- **0** ≤1 item. **1** 2. **2** 3. **3** 4. **4** all 5. **5** all 5 *and* the outer contour reads as
  one intentional shape.

## D · Feature legibility

Score on `[1]` the eyes read as layered (white, iris, pupil, dark lash), `[2]` the eyes are correctly
sized and aligned, `[3]` a mouth and a nose are each present *and* readable as marks rather than
scratches, `[4]` the hat reads as one hat (crown and brim in their correct relationship, not disjoint
primitives), `[5]` the hands read as hands:

- **0** ≤1 item. **1** 2. **2** 3. **3** 4. **4** all 5. **5** all 5 *and* the features match the
  target's expression (shy, downcast).

## E · Occlusion correctness

Score on the target's own overlap relationships: `[1]` the hat's brim passes **behind** the skull,
`[2]` the **crown** is visible above the hair (hair does not paint over the crown), `[3]` the hair
falls **over** the shoulders, `[4]` the arm is **in front of** the dress and skirt, `[5]` the bow sits
**over** the blouse, `[6]` the chest panels/hand sit **in front of** the skirt mass (their outlines
cross the skirt's edge, rather than floating inside it):

- **0** ≤1 item. **1** 2. **2** 3. **3** 4. **4** 5. **5** all 6.
- A relationship that is *absent* (the shapes do not touch) does **not** score; and if it is absent,
  say so — that is missing structure, not a correct occlusion.

## F · Style and composition

Score on `[1]` flat cel style (no gradients where the reference is flat), `[2]` the palette is in the
reference's family (list the families you see), `[3]` the subject's place in the frame, `[4]` the
subject's scale, `[5]` the background masses are in the reference's places *and shapes* (the mint field
is a **sweeping wave**, not an ellipse), `[6]` the mid-frame composition is not deleted (ribbon tails,
the chair/skirt detail, the field's swirl tails):

- **0** ≤1 item. **1** 2. **2** 3. **3** 4. **4** all 5 but one major shape is simplified. **5** all 6.

## How the vector is read

- **Progress** = the vector moving up, axis by axis. The verdict is the *whole vector*: raising one
  axis by wrecking another is not progress.

## Milestone exit and the alarm gates

- **Milestone exit** = the milestone's **named axes** reaching their targets, **plus** the alarm gates
  (G0 admissible, G2 no deletion/breakage, G4 diagnostics, G5 budget, G6 determinism, G7 no traces,
  and the similarity alarm not having fallen by more than 0.02 since the last review). For example M3
  (the body) exits when **B ≥ 4** and **E ≥ 4** hold across two independent reviewers.
- The gates are named and owned in `0_ROADMAP.md`.

## The similarity alarm is an instrument, never a gate

`scripts/similarity.py` computes a CLIP image-embedding cosine similarity between the draft and the
target. It is **contextual**, not pixel-level, and it separates the project's own history cleanly.

It is a **secondary alarm, never a gate** — the same reason the pixel metrics are alarms. A scalar
invites optimisation (`P25`), and a CLIP score is far easier to game than `edge_f1`: it measures
*semantic neighbourhood*, so a drawing can drift toward "anime girl with a hat" generally and the
number will rise while the drawing becomes less like the target. Use it to **catch regressions between
rubric reviews**, and to record history: the value is recorded in the log with each rubric review.
How to run the instrument, and its reference values, belong to `9_IMPLEMENTATION.md`.

## Never tune for a number

**Never** tune a drawing to raise a rubric number or the similarity score. The rubric is a *reading*,
like the pixel metrics, and invariant 4 applies in full: a drawing changed to move a score, rather than
for a stated drawing reason, is the same regression one level up (`P25`).
