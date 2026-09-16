# The rubric — contextual assessment of a drawing

Pixel metrics cannot tell whether a drawing **reads**. They measure edge coincidence and colour
distance against a reference, so a traced copy scores well and a good drawing of a *different*
subject scores badly. This project's own P14 already says the primary criterion is *looking* — this
file makes that judgement **specific, actionable and comparable across iterations**, so it can be done
by an independent subagent and used as a gate.

**Refined 2026-09-16** (user direction): more axes, each with explicit and checkable scoring rules, so
that two independent reviewers land within ±1 — and so a reviewer's disagreement is diagnosable rather
than vague. Version **2**, replacing the six-axis version. Version 2's first use is the M3b review.

The pixel metrics stay, but **demoted to alarms** (roadmap G2): they catch deletion and breakage, and
they never decide what is good. The rubric decides.

## How to run a rubric review

1. **Independent reviewer, no context.** A fresh subagent is given the target and the draft and
   *nothing else* — no history, no intent, no suspected verdict, and no sight of previous scores. It
   reads `rubric.md` only.
2. **Sight must be proven first** (D18). The reviewer's first output is **three** checkable facts, and
   each is compared against a measurement already in the repo:
   - the colour of the large field shape left of centre, and roughly where its right edge stops
     (mint `#7dccc1`, right edge ≈ x718);
   - where the subject sits in the frame (seated, right of centre, head upper-right);
   - one named shape in the target's lower half (the salmon shard at ≈ x250–400, y700–950).
   A reviewer that cannot answer is not sighted: its scores are **void, not low**, and the review is
   recorded as *not run*.
3. **Two independent reviewers, always.** A single review is recorded as *provisional*. If the harness
   replays a previous result (it has done), that is **not** a second opinion — dispatch again and say
   so in the log.
4. **Agreement rule:** axes differing by ≥2 between reviewers are **contested**, and a contested axis
   cannot be used to pass or fail a milestone until it is settled (measurement, or a third review).
   Axes differing by ≤1 are recorded as the mean and stand.
5. Record the vector in the exercise's `log.md` with the bundle it was scored from.

## What the reviewer is given

- the target (`image.jpg`) — or, for a region milestone, the target crop;
- the draft: the **1:1 draft first** (a downscaled pane destroys exactly the detail being judged —
  07's finding), then the whole-frame side-by-side;
- for a region milestone, the **region crop at full resolution** (the target's and the draft's side by
  side), because the milestone is judged on the region it owns;
- nothing else.

## Part I — the six axes (0–5)

Anchors are the contract. Score the anchor, not the effort.

### A · Subject identity
*Does it read as this character?* Score on **tokens**, and require ≥3 of the 4:
`[1]` blue hair, `[2]` a wide-brimmed sun hat with pom-poms, `[3]` a pale dress with a large chest bow,
`[4]` the seated pose with a dark mass across the lap.
- **0** ≤1 token. **2** 2 tokens. **3** 3 tokens. **4** all 4 tokens, but the pose, scale or framing
  differs from the target. **5** all 4 tokens *and* the pose, scale and framing match the target.
- Deduct 1 if the **face** reads as blank or dead-eyed rather than the target's shy downcast look.

### B · Human figure
Score on the checklist `[1] neck`, `[2] both arms`, `[3] at least one hand with fingers`, `[4] a
connected lower body (torso reaching the skirt/lap)`, `[5] a leg or knee below the hem`,
`[6] head-to-body proportion plausible for a seated figure (~1:3–1:4)`:
- **0** ≤1 item. **1** 2 items. **2** 3 items. **3** 4 items. **4** 5 items. **5** all 6.
- A limb that is drawn but **floats unattached** does not count.

### C · Silhouette coherence
The figure must be **one connected mass**. Score on `[1]` head connects to the torso (no background
band at the neck), `[2]` the torso connects to the skirt/lap (no background band at the hem),
`[3]` the arms connect at the shoulder, `[4]` no floating bar/shape with no anatomical source,
`[5]` no shape crossing the frame edge that the reference does not also cross:
- **0** ≤1 item. **1** 2. **2** 3. **3** 4. **4** all 5. **5** all 5 *and* the outer contour reads as
  one intentional shape.

### D · Feature legibility
Score on `[1]` the eyes read as layered (white, iris, pupil, dark lash), `[2]` the eyes are correctly
sized and aligned, `[3]` a mouth and a nose are each present *and* readable as marks rather than
scratches, `[4]` the hat reads as one hat (crown and brim in their correct relationship, not disjoint
primitives), `[5]` the hands read as hands:
- **0** ≤1 item. **1** 2. **2** 3. **3** 4. **4** all 5. **5** all 5 *and* the features match the
  target's expression (shy, downcast).

### E · Occlusion correctness
Score on the target's own overlap relationships: `[1]` the hat's brim passes **behind** the skull,
`[2]` the **crown** is visible above the hair (hair does not paint over the crown), `[3]` the hair
falls **over** the shoulders, `[4]` the arm is **in front of** the dress and skirt, `[5]` the bow sits
**over** the blouse, `[6]` the chest panels/hand sit **in front of** the skirt mass (their outlines
cross the skirt's edge, rather than floating inside it):
- **0** ≤1 item. **1** 2. **2** 3. **3** 4. **4** 5. **5** all 6.
- A relationship that is *absent* (the shapes do not touch) does **not** score; and if it is absent,
  say so — that is missing structure, not a correct occlusion.

### F · Style and composition
Score on `[1]` flat cel style (no gradients where the reference is flat), `[2]` the palette is in the
reference's family (list the families you see), `[3]` the subject's place in the frame, `[4]` the
subject's scale, `[5]` the background masses are in the reference's places *and shapes* (the mint field
is a **sweeping wave**, not an ellipse), `[6]` the mid-frame composition is not deleted (ribbon tails,
the chair/skirt detail, the field's swirl tails):
- **0** ≤1 item. **1** 2. **2** 3. **3** 4. **4** all 5 but one major shape is simplified. **5** all 6.

## Part II — the two free-text fields (the most valuable output)

- **Biggest single defect** — one sentence, concrete and checkable.
- **The one change that would most improve it** — one sentence. This is the field the next iteration
  works from.

## Part III — the contextual similarity alarm (instrument, not a gate)

`scripts/similarity.py` computes a CLIP image-embedding cosine similarity between the draft and the
target (model: OpenAI `ViT-B-32`, 151M params, cached at `~/.cache/clip`). It is **contextual**, not
pixel-level, and it separates the project's own history cleanly:

| | cos to target |
| --- | --- |
| M3b (current) | **0.836** |
| M2 flat bust | 0.732 |
| M1 flat blobs | 0.637 |
| Starry probe (different subject) | 0.591 |
| random noise | 0.489 |

It is a **secondary alarm, never a gate** — the same reason the pixel metrics are alarms. A scalar
invites optimisation (P25), and a CLIP score is far easier to game than `edge_f1`: it measures
*semantic neighbourhood*, so a drawing can drift toward "anime girl with a hat" generally and the
number will rise while the drawing becomes less like the target. Use it to **catch regressions between
rubric rounds**, and to record history. Record the value in the log with each rubric review.

## How the scores are used

- **Progress** = the vector moving up, axis by axis. The verdict is the *whole vector*: raising one
  axis by wrecking another is not progress.
- **Milestone exit** = the milestone's **named axes** reaching their targets, **plus** the alarm gates
  (G0 admissible, G2 no deletion/breakage, G4 diagnostics, G5 budget, G6 determinism, G7 no traces,
  and the similarity alarm not having fallen by more than 0.02 since the last review). For example
  M3 (the body) exits when **B ≥ 4** and **E ≥ 4** hold across two independent reviewers.
- **Never** tune a drawing to raise a rubric number or the similarity score. The rubric is a *reading*,
  like the pixel metrics, and invariant 4 applies in full: a drawing changed to move a score, rather
  than for a stated drawing reason, is the same regression one level up (P25).
