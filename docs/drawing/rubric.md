# The rubric — contextual assessment of a drawing

Pixel metrics cannot tell whether a drawing **reads**. They measure edge coincidence and colour
distance against a reference, so a traced copy scores well and a good drawing of a *different*
subject scores badly. This project's own P14 already says the primary criterion is *looking* — this
file makes that judgement **specific, actionable and comparable across iterations**, so it can be
done by an independent subagent and used as a gate.

The pixel metrics stay, but **demoted to alarms** (roadmap G2): they catch deletion and breakage, and
they never decide what is good. The rubric decides.

## How to run a rubric review

1. **Independent reviewer, no context.** A fresh subagent is given the target and the draft and
   *nothing else* — no history, no intent, no suspected verdict, and no sight of previous scores.
2. **Sight must be proven first** (D18). The reviewer's first output is one fact only a sighted agent
   could state, checkable against a measurement already in the repo — e.g. *"the target has a large
   field shape left of centre; what colour is it, and roughly where does its right edge stop?"*
   (mint `#7dccc1`, right edge ≈ x718). A reviewer that cannot answer is not sighted: its scores are
   **void, not low**, and the review is recorded as *not run*.
3. **Rank unchanged inputs the same way.** Same target, same draft, same instructions → the scores
   should land within ±1. If they do not, the axis wording is the problem, not the drawing.
4. **Two reviewers.** If they differ by ≥2 on an axis, that axis is **contested**: record it as
   contested and settle it by measurement or a third review. Never average away a disagreement.
5. Record the vector in the exercise's `log.md` with the bundle it was scored from.

## What the reviewer is given

- the target (`image.jpg`) — or, for a region milestone, the target crop;
- the draft: the whole-frame side-by-side from `draw check`, **and the 1:1 draft** (a downscaled pane
  destroys exactly the detail being judged — 07's finding);
- nothing else.

## The axes

Score each **0–5** against the target. Anchors are the contract; use them, not vibes.

### A · Subject identity
- **0** unrecognisable as anything.
- **2** a generic figure; wrong character entirely.
- **4** recognisably this *kind* of character (blue hair, wide sun hat, pale dress).
- **5** unmistakably this subject.

### B · Human figure
- **0** no body, or disconnected blobs where a body should be.
- **2** a torso mass, no limbs, nothing attached.
- **4** torso, both arms, hands and neck present and attached at plausible places.
- **5** reads as a seated person with believable proportions.

### C · Silhouette coherence
- **0** shapes floating apart.
- **2** masses touch but do not form one figure.
- **4** one continuous figure.
- **5** a clean, intentional silhouette.

### D · Feature legibility
- **0** no features.
- **2** eyes/mouth present but malformed, mis-scaled or mis-placed.
- **4** eyes read as layered (white / iris / pupil / dark lash), mouth and nose present, and the hat
  reads as a hat (crown **and** brim).
- **5** features read cleanly at a glance.

### E · Occlusion correctness
- **0** overlaps wrong — things float, or the wrong thing is in front.
- **2** mostly right with obvious errors.
- **4** the target's key overlaps hold (brim passes behind the skull, hair over the shoulders, arm
  behind the body).
- **5** consistent everywhere.

### F · Style and composition
- **0** wrong palette and layout.
- **2** palette near, subject misplaced or wrongly scaled.
- **4** flat cel style and a palette in the reference's family, subject in roughly the target's place
  and scale.
- **5** matches the target's look and framing.

## What the reviewer must also write

- **Biggest single defect** — one sentence, concrete.
- **The one change that would most improve it** — one sentence. (This is the field the next iteration
  works from; it is worth more than the scores.)
- Anything they are **unsure about**, flagged as such.

## How the scores are used

- **Progress** = the vector moving up, axis by axis. The verdict is the *whole vector*: raising one
  axis by wrecking another is not progress, and a reviewer asked to justify a rising total will say so.
- **Milestone exit** = the milestone's **named axis** reaching its target, **plus** the alarm gates
  (G0 admissible, G2 no deletion/breakage, G4 diagnostics, G5 budget, G6 determinism, G7 no traces).
  For example M3 (the body) exits when **B · Human figure ≥ 4** and E · Occlusion ≥ 4 hold.
- **Never** tune a drawing to raise a rubric number. The rubric is a *reading*, like the pixel
  metrics, and invariant 4 applies to it in full: a drawing changed to move a score, rather than for a
  stated drawing reason, is the same regression one level up (P25).

## Why not a learned similarity metric instead

A pretrained embedding distance (CLIP-like, or LPIPS) would give a scalar that is contextual rather
than pixel-level — genuinely better than `edge_f1` at "does this read as the same thing". Two reasons
it is not the primary instrument here:

1. **It is a black box, and this project's whole method is explainability.** A rubric tells you *which*
   axis is weak and *what* to change; a scalar tells you a number moved. The reviewer's free-text
   "one change that would most improve it" field is the most valuable output of a review, and a
   distance metric has no equivalent.
2. **A scalar invites exactly the failure this file exists to prevent.** `edge_f1` was optimised until
   the drawing got worse (P25); a contextual scalar would be optimised the same way, just more
   convincingly.

If the rubric proves too coarse to separate two drafts, the answer is to make an axis more specific —
not to import a score nobody can explain. (A contextual metric may still be worth having as a
*secondary* alarm, the way `coverage` is; that is a decision for the user.)
