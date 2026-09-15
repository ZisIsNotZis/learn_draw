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

| # | gate | command / method | passes when |
| --- | --- | --- | --- |
| G1 | render + bundle | `scripts/draw check <assembly-render> --ref image.jpg` | bundle written; `draft-fullres.png` is in the reviewer image list |
| G2 | **alarm** — nothing deleted, nothing broken | the `vs recorded best:` line in `report.txt` | `coverage` ≥ best − 0.01 (deletion floor) and `color_dist` ≤ best + 15 (breakage). Applies at **every** milestone |
| G2b | **detail floor** | as above | `edge_f1` ≥ best − 0.01 — applies **from M2 onward**, when detail becomes the job. Reported but not gating in M1 |
| G3 | placement check | per-element mass measurement (centroid + area% of the reference's main colour masses) against the reference | each mass present, and its centroid within ~0.05 of the reference's. This is the composition instrument; it is what caught reviewer error in M1 |
| G4 | diagnostics | resolver output in `report.txt` | clean, or each firing is stated and justified |
| G5 | authoring budget | inspect the spec | no shape carries > 4 hand-typed coordinates **per outline**; a mass may carry ≤ 4 spine points + a width (the sanctioned gesture form, `scene-format.md`); every node has an intent `desc:` |
| G6 | determinism | re-render, compare `sha256` | byte-identical |

**Promotion is a separate act, not a milestone exit, and it takes the WHOLE artifact.** The baseline
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
- A1 a 2x crop of the head is preferred, or tied, against the same crop of the baseline **by blind
  reviewers AND by the head-region colour-mass distance** — and where those disagree, the measurement
  decides (attempt 1 is the worked example: reviewers split 1–1, the measurement said baseline, so
  the baseline won);
- A2 a reviewer confirms, at 2x: non-circular jaw/chin, layered eyes with iris/pupil/glints, tapered
  one-sided lash, mouth/nose marks present, hair tapered (no constant-width tubes);
- A3 the hat reads as a hat — crown volume plus tilt, and **one continuous brim**, not "a disc with a
  ball" and not two detached lobes;
- A4 G1, G2, G2b (detail floor now applies), G3, G4, G5, G6.

Provisional work items: `face` host family ✅ (attempt 1, jaw/chin verified against the reference's
row profile); two eyes placed independently rather than `mirror-of` ✅ (this is a 3/4 view); fringe
+ cheek locks ✅ (the reference's visible face is 151×153 only because hair covers it);
**one continuous brim silhouette ← the blocking defect**; taper-first-class for hair.

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
