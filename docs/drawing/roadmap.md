# Roadmap — from here to the goal

`STATUS.md` (repo root) says where we are **today**. This file says what "forward" means and what
must be true at each step. On facts, STATUS wins; on direction, this file wins.

## How to read this file (this is the robustness property)

Two layers, deliberately different in stability:

| layer | stability | contents |
| --- | --- | --- |
| **the spine** | fixed — changes only by a decision recorded in `STATUS.md` → Decisions | the goal, the invariants, milestones M0–M5, and each milestone's exit gate |
| **the work items** | provisional — reorder, merge, split, replace freely, without ceremony | the slices listed under each milestone |

New information changes the work items; it does not change the target. **A milestone is reached when
its gate passes — never when its slice list is exhausted.** Slices are today's best guess at a route,
which is why they are allowed to be wrong.

## Goal

Learn to draw. Recreate reference images as explainable, readable vector graphics; first with the
reference available, then with it closed, then with no reference at all — ending at Starry-Night-class
complexity. Never diffusion or pixel generation.

## Invariants (hold at every milestone, under any change)

- **R1 — The assembly is the artifact.** One drawing grows across the milestones, at
  `.scratch/13-assembly/work/spec.yaml` (designated home; seeded by M1's first work item). Every
  milestone patches *it*. A probe (a side experiment, a new family, a new subject) is allowed, but it
  merges into the assembly or is discarded **in the
  same milestone** — it never becomes the deliverable. This is what made the night session's work
  non-accumulating: three probes, zero patches to a drawing.
- **R2 — No milestone may regress the baseline.** Every milestone's exit includes the gate below.
  A refactor that regresses the artifact is a regression, not progress.
- **R3 — Gates before claims.** "Final", "readable", "done" are claims and require the gate's
  evidence. A completion claim without the gate is false, however clean the diagnostics are (P22).
- **R4 — Docs-first for the change itself.** A new family, relation, or invariant lands in
  `vocabulary.md` / `abstraction.md` / `principles.md` in the same session that it lands in code.
- **R5 — Engine growth is demand-first.** A relation, family, or generator is added only when the
  *current* milestone's drawing fails without it. No speculative generality (the 05 lesson).
- **R6 — Metrics are floors and alarms, never targets.** `coverage` is a floor (you may not delete
  content) and `color_dist`/`edge_f1` are alarms (a jump means something broke). Tuning *against* a
  metric is optimizer regression and is forbidden — including "improve coverage" as a goal in itself.
- **R7 — One writer per tree.** Concurrent work uses `git worktree`, never a shared checkout.

## The gate (identical at every milestone)

Run **all six**; each produces evidence, and the milestone report cites them.

**Two different things are being measured here, and conflating them caused a bad gate:** an
*alarm* catches deletion and breakage and applies at every milestone; a *detail floor* tests
correspondence of line and colour, which only makes sense once the milestone's job includes detail.
M1 is defined as flat masses, so gating it on `edge_f1` would have failed it for doing exactly what
it is for — and would have pressured M1 into smuggling in M2/M3 work (the "one ticket doing several
things at once" failure that got 05 frozen). Renegotiated 2026-09-15; see `STATUS.md` D7.

**THE PRIMARY GATE IS THE RUBRIC, NOT THE METRICS (added 2026-09-15, D30).** The pixel metrics are
*pixel* measures: they compare edge coincidence and colour distance against a reference, so a traced
copy scores well and a good drawing of a slightly different subject scores badly. This file's own P14
said the primary criterion is *looking*; `docs/drawing/rubric.md` now makes that specific, actionable
and comparable, and it is what decides whether a drawing is good. The metrics stay as **alarms** on G2
(catch deletion and breakage) and as **diagnostics** on G3 (tell you *where* to work). Tuning a
drawing to a metric — or to a rubric number — is invariant 4's regression (P25).

| # | gate | command / method | passes when |
| --- | --- | --- | --- |
| **G8** | **the rubric (PRIMARY)** | `draw check` bundle → an independent, sight-proven reviewer scores the six axes in `docs/drawing/rubric.md`, two reviewers, contested axes recorded | the milestone's **named axis** reaches its target, and no axis fell by ≥2 where it had been ≥3. The vector is the verdict, never a total |
| **G0** | **admissibility (check this FIRST)** | render the judged artifact **without** `--ref` | it renders. An artifact that needs the reference raster is **teacher-dependent** and any comparison result on it is **void** — not a pass and not a failure of the drawing, but a failure of its admissibility (`STATUS.md` D21). Use the reference to **materialize** geometry into the spec (trace once, freeze the vertices, close the image — D20), never to compute geometry at render time |
| G1 | render + bundle | `scripts/draw check <assembly-render> --ref image.jpg` | bundle written; `draft-fullres.png` is in the reviewer image list |
| G2 | **alarm** — nothing deleted, nothing broken | the `vs recorded floor:` line in `report.txt` | `coverage` ≥ floor − 0.01 (deletion floor) and `color_dist` ≤ floor + 15 (breakage). Applies at **every** milestone. **Not a quality measure** — see G8 |
| G2b | **detail diagnostic** | as above, **restricted to the region the milestone owns** | `edge_f1` reported, and its movement explained. **Demoted 2026-09-15 (D30): as a *floor* it was false** — it was calibrated on a hand-fitted artifact, so clearing it needed near-contour accuracy (proved: D26), which is tracing. It tells you where the drawing is thin; it does not decide whether the drawing is good |
| G3 | placement check | per-element mass measurement (centroid + area% of the reference's main colour masses) against the reference, plus the region-scoped colour-mass distance | each mass present, and its centroid within ~0.05 of the reference's. This is the composition instrument; it is what caught reviewer error in M1 |
| **G7** | **transferable share** | `.venv/bin/python .scratch/13-assembly/work/measure-trace-debt.py` | at a **milestone exit**, the traced share of the artifact's painted pixels is **0** — every shape comes from a family or a relation. A `traced` node may exist *during* work (it is the teacher's measurement) but may not be in the artifact a milestone exits on. **Added 2026-09-15 (D24, approved):** M2 was passing this gate set while 81% of its head was a frozen copy of the reference. A gate that cannot tell a drawing from a copy is not a gate, and a frozen contour is not a **canon** — `vocabulary.md` defines a canon as proportion knowledge that *transfers to a new subject*, and a traced outline transfers to nothing |
| G4 | diagnostics | resolver output in `report.txt` | clean, or each firing is stated and justified |
| G5 | authoring budget | inspect the spec | no shape carries > 4 hand-typed coordinates **per outline**; a mass may carry ≤ 4 spine points + a width (the sanctioned gesture form, `scene-format.md`); every node has an intent `desc:` |
| G6 | determinism | re-render, compare `sha256` | byte-identical |

**Promotion is a separate act, not a milestone exit, and it takes the WHOLE artifact, which must be
admissible (G0).** The baseline
moves **only** on a blind A/B preference over the whole drawing: hand a fresh-context reviewer the
target plus the two renders under neutral names in randomized order, asking "which is the better
drawing of this target, and what is wrong with each?" Never promote on metrics; never promote because
a milestone passed; and **never promote on a region** — a render whose head improved while its body
stayed cruder would move the floor *down* in disguise (see `STATUS.md` D10).

A **region-scoped** comparison (the head crop in M2, the blouse in M3) is milestone **evidence**: it
can fail the milestone and it tells you where to work, but it cannot promote. `scripts/draw baseline
<render> --ref image.jpg --note "…"`. **The baseline only ever moves up.**

If two reviewers disagree, do not pick a verdict — measure (P7: observations are reliable, locations
are not). The coarse-grid colour-mass distance and the per-element table are the tie-breakers; that
is how M1's split verdict was resolved.

**A reviewer must prove it can see before its verdict counts (D18).** Vision is not stable across
subagent instances in this environment — some are sighted, some return "model does not support
images", and the orchestrator has no vision at all. Ask the reviewer first for one fact only a sighted
agent could state, checkable against a measurement already in the repo. An unsighted verdict is
**void, not negative**, and the record must say the visual half was not run. A fabricated visual
verdict is the worst possible outcome.

## When to stop — the standing stop conditions (D31)

A run continues autonomously **until one of these fires**, and then stops and reports rather than
grinding. They are not failure states; they are the method reporting its own limit, and each one is a
finding worth more than another iteration.

- **S1 · Abstraction failure.** Describing what to draw starts to need a flood of numbers instead of
  high-level terms. The litmus is already in `abstraction.md`: *if expressing an idea needs
  coordinates, the abstraction has failed — add the relation or the vocabulary, never the numbers.*
  Reaching for a coordinate is the signal; reaching for it repeatedly is the stop.
- **S2 · Comprehension failure.** You can no longer say what change would move the drawing closer to
  the reference — you are guessing at edits rather than understanding the difference. Guessing is the
  stop; **name what you cannot understand**, because that is a missing vocabulary item or a missing
  measurement.
- **S3 · Perception failure.** The review pipeline cannot report, or cannot distinguish two drafts:
  no sighted reviewer available (D18), or two reviewers' verdicts land on the same score for visibly
  different work. Without perception the loop is open, and continuing is writing without looking.

On a stop: park with **status, next step, blocker** (R-SES.2), leave the round's artefacts and numbers
committed, and report — do not keep iterating to look busy.

## Milestones

### M0 — Baseline recorded ✅ (2026-09-15)

Intent: make regression *visible*, because it was invisible and that cost a session.

Exit: a recorded best artifact with provenance, and `check` reporting a delta against it.
Done: `.scratch/00-tooling/baseline/` (best.png + best.json) holds the 2026-09-11 full-figure
assembly — coverage 0.514, edge_f1 0.252, color_dist 62.8; byte-identical reproduction verified.

### M1 — Recover the baseline's composition (the whole figure, coarsely)

Intent: stop being *below* the project's own bar again, and give every later milestone a frame that
is measured-correct. The measured deficit that opened M1 was coverage (0.514 → 0.091), i.e. missing
subject mass — so this milestone is **placement and mass**, drawn flat.

Entry: M0. **Status: exit criteria met 2026-09-15** (see `STATUS.md` D8); baseline *not* promoted.

Exit AC:
- A1 the subject sits where the reference's sits and fills the frame the way the reference does —
  verified by G3's per-element measurement, plus a reviewer statement;
- A2 the masses the reference has are present *as flat shapes*: figure, hat, hair sweep, blouse,
  bow, dark skirt mass, pale overskirt, and the left background field + ribbon sweep;
- A3 coverage ≥ the recorded best (nothing deleted);
- A4 G1, G2, G3, G4, G5, G6 pass.

**Not an M1 exit: beating the baseline as a drawing.** With flat masses and no line work, M1 loses
G2b and loses any blind A/B on finish — by construction, not by failure. Requiring it here would
have made the milestone unreachable. That bar belongs to M4, whose job is the finished figure.

*Not in M1:* face detail, folds, shading, gradients. Flat fills only.

Note on invariant 2 (soft fields last): M1 draws the field's **silhouette** flat, because coverage
counts its presence. Its *soft treatment* (gradients, blur, translucency) is M4 and stays deferred.

Provisional work items:
1. Seed `.scratch/13-assembly/work/spec.yaml` from `14/work/final/final-full.yaml`.
2. Measure the reference's composition (colour-component bboxes/centroids) and put the numbers in
   `vars:` with provenance — never eyeball placement (P19).
3. Fix the figure's position, scale and mass placement against those measurements.
4. Add the field + ribbon sweep as flat relational shapes.
5. Record the milestone in `13-assembly/log.md` with the gate evidence.

### M2 — Beat the baseline on the head

Intent: the face is the hardest small part and the ladder's L1 discipline; the night session's eye
family and canons are already built and finally get applied to a drawing that is not below the bar.

Entry: M1 gate passed. **Status: in progress — attempt 1 failed its gate (2026-09-15).** See
`.scratch/13-assembly/log.md` → M2 and `STATUS.md` D11. M2 cannot promote (D10), so its exit *is* the
head-crop comparison.

Exit AC:
- A1 the head **region** is preferred, or tied, against the same region of the baseline **by blind
  reviewers AND by region-scoped measurement** (`edge_f1`, coverage, colour-mass distance) — and where
  those disagree, the measurement decides (attempt 1 is the worked example: reviewers split 1–1, the
  measurement said baseline, so the baseline won);
- A2 a reviewer confirms, at 2x: non-circular jaw/chin, layered eyes with iris/pupil/glints, tapered
  one-sided lash, mouth/nose marks present, hair tapered (no constant-width tubes);
- A3 the hat reads as a hat — crown volume plus tilt, and **one continuous brim**, not "a disc with a
  ball" and not two detached lobes;
- A4 G1, G2, **G2b on the head region**, G3, G4, G5, G6, **G7**.
- A5 **the head's geometry is families, not traces** (G7): the brim is a `sunhat` instance whose
  parameters were *extracted* from the reference, the face is a `face` instance, the hair a
  `hair-mass` instance — with the extracted **canon values written into `vocabulary.md`**, because
  those values are the transferable knowledge and the whole point of the exercise.

Provisional work items: `face` host family ✅ (attempt 1); two eyes placed independently rather than
`mirror-of` ✅; fringe + cheek locks ✅; **`sunhat` fold-over rim band ✅ (attempt 2 — the chord split
was the real cause of the detached brim)**; **seed the head's geometry from the reference instead of
re-deriving it coarsely (D15) ← next**; a brim shape that can droop like the reference's crescent;
a fringe that does not cover the mid-brim; taper-first-class for hair.

**What attempt 2 learned that matters more than the milestone.** The baseline's head wins on
measurement because it was *hand-fitted to the reference*; the from-scratch relational head is more
coherent but less accurate. The lesson is not "try harder" — it is that the assembly should **seed
values from the reference** (measure → fill the spec → close the image, which `abstraction.md`
sanctions) while the *structure* stays relational. M1/M2 re-derived badly what was already measured
accurately. See `STATUS.md` D15.

**What attempt 3 learned, and why G7 exists.** Seeding via live raster floods passed the bar and
violated P18; materializing them into `traced` sidecars made it admissible — and measured, the head
came out **81% copied**. So the ladder was drifting from *learn to draw* toward *learn to trace*: the
gate could not distinguish a drawing from a copy. The fix, approved as D24, is the teacher loop
`abstraction.md` actually describes — **use the trace as ground truth to fit the families to, then
discard the trace**, so the artifact is family instances carrying measured canons and M5 has something
that can transfer. Honesty hinge: **fit to the teacher's measurement, never to the evaluation
metric** — fitting `sunhat` to a traced brim mask is parameter extraction; nudging `brim` until
`edge_f1` rises is invariant 4's optimizer regression.

### M3 — Beat the baseline on body and cloth

Entry: M2 gate passed. Exit AC: collar, bow, puff sleeves, arms + hands, placket present and
occluding per declared relations (P17 z-split); cloth reads as cloth (folds via generators, not
hand-laid strokes); G1–G6. Families demanded: `sleeve`, `bow`, `collar`, `hand`, `pleats`.

### M4 — Beat the baseline on the fields (soft tier, last)

Entry: M3 gate passed. Exit AC: backdrop, curtain and the ribbon sweep use the soft tier
(gradient/blur/translucency) *without* touching structure; a one-line justification exists for every
soft shape (method.md T3 rule); G1–G6. This is where the deferred 12-fields capability (clip/blend)
is allowed to be built.

### M5 — Withdrawal and stress

Entry: M4 gate passed. Three rungs, in this order, each its own ticket:
- `15-withdrawal-a`: redraw the assembled figure from its own spec, **image deleted**;
- `16-withdrawal-b`: a new subject from intent alone (composition anchors enter here);
- `17-starry-stress`: Starry-Night-class complexity, reference-free.

Exit AC: each rung's artifact passes G1–G6 with `--ref` omitted where the reference is closed, plus a
reviewer verdict that the drawing reads on its own terms.

## Where we are now

See `STATUS.md`. The ladder's original rung numbers (08–13) map onto M1–M4 as slice homes; the
milestones, not the rung numbers, carry the acceptance.

## Change protocol — what to do when reality moves

| situation | response |
| --- | --- |
| A work item fails its AC twice | park it with status + next step + blocker (R-SES.2); re-scope the *work item*, not the milestone |
| A new drawing demand appears | it becomes a work item under the milestone it serves; if it serves none, defer it (R5) |
| The baseline moves up | nothing to renegotiate — every AC is already relative to "the recorded best". Record the new best in `STATUS.md` |
| A milestone's exit turns out unreachable | renegotiate the **milestone** explicitly and record it in `STATUS.md` → Decisions. Never silently skip it |
| A gate keeps failing for an unrelated reason | fix the gate, record it, and re-state it — a gate that cannot be run is not a gate |
| Someone wants to relax a gate so a failing artifact passes | refuse. Change the artifact, or change the milestone. Gates are the only thing standing between this project and the session that shipped a bust as "FINAL" |
| The engine needs a new capability mid-milestone | allowed only if the current drawing fails without it (R5); the doc entry lands the same session (R4) |

## What would change this roadmap

Tripwires that mean the spine — not just the slices — needs rethinking, recorded in `STATUS.md`:

- M1 passes its gate but the result still reads as a worse picture than the baseline → the gate is
  measuring the wrong thing; revisit G2/G3 before continuing.
- Two consecutive milestones produce no reviewer-visible improvement → the drawing isn't learning;
  change the *method*, not the milestone list.
- The withdrawal rungs (M5) pass while M1–M4 needed the reference heavily → the canon/tier-3 story
  is not actually transferable; that becomes the project's real research question.
