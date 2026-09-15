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

| # | gate | command / method | passes when |
| --- | --- | --- | --- |
| G1 | render + bundle | `scripts/draw check <assembly-render> --ref image.jpg` | bundle written; `draft-fullres.png` is in the reviewer image list |
| G2 | no regression | the `vs recorded best:` line in `report.txt` | `coverage` ≥ best − 0.01 and `edge_f1` ≥ best − 0.01; `color_dist` may not jump > 10 |
| G3 | fresh eyes (blind A/B) | hand a fresh-context reviewer **only** the two images (new render, best render) + the target, in randomized order; ask "which reads more like the target, and what is wrong with each?" | the new render is preferred or judged a tie; no reviewer-reported defect is left unclassified |
| G4 | diagnostics | resolver output in `report.txt` | clean, or each firing is stated and justified |
| G5 | authoring budget | inspect the spec | no shape carries > 4 hand-typed coordinates; every node has an intent `desc:` |
| G6 | determinism | re-render, compare `sha256` | byte-identical |

On pass, if the new render is better, promote it: `scripts/draw baseline <render> --ref image.jpg
--note "…"`. **The baseline only ever moves up.**

## Milestones

### M0 — Baseline recorded ✅ (2026-09-15)

Intent: make regression *visible*, because it was invisible and that cost a session.

Exit: a recorded best artifact with provenance, and `check` reporting a delta against it.
Done: `.scratch/00-tooling/baseline/` (best.png + best.json) holds the 2026-09-11 full-figure
assembly — coverage 0.514, edge_f1 0.252, color_dist 62.8; byte-identical reproduction verified.

### M1 — Beat the baseline on composition (the whole figure, coarsely)

Intent: stop being *below* the project's own bar. The measured deficit is coverage (0.514 → 0.091),
i.e. missing subject mass, not wrong detail. This milestone is **placement and mass**, drawn flat.

Entry: M0.

Exit AC:
- A1 the subject sits where the reference's sits, and fills the frame the way the reference does
  (reviewer states this in words; that is the acceptance, not a number);
- A2 the masses the reference has are present *as flat shapes*: figure, hat, hair sweep, blouse,
  bow, dark skirt mass, pale overskirt, and the left background field + ribbon sweep;
- A3 G1–G6 all pass.

*Not in M1:* face detail, folds, shading, gradients. Flat fills only.

Note on invariant 2 (soft fields last): M1 draws the field's **silhouette** flat, because coverage
counts its presence. Its *soft treatment* (gradients, blur, translucency) is M4 and stays deferred.

Provisional work items:
1. Seed `.scratch/13-assembly/work/spec.yaml` from `14/work/final/final-full.yaml` (it already has
   the relational head/hat/hair + body skeleton). Promote, then delete 14's copy as a source of truth.
2. Fix the figure's position and scale against the reference's own framing (head var, canvas anchor).
3. Re-author the skirt/dress mass where the reference has it (lower-left, not centred).
4. Add the background field + ribbon sweep as two flat relational shapes.
5. Record the milestone in `13-assembly/log.md` with the gate evidence.

### M2 — Beat the baseline on the head

Intent: the face is the hardest small part and the ladder's L1 discipline; the night session's eye
family and canons are already built and finally get applied to a drawing that is not below the bar.

Entry: M1 gate passed.

Exit AC:
- A1 a 2x crop of the head is preferred (or tied) against the same crop of the baseline;
- A2 reviewer confirms, at 2x: non-circular jaw/chin, layered eyes with iris/pupil/glints, tapered
  one-sided lash, mouth/nose marks present, hair tapered (no constant-width tubes);
- A3 hat reads as a hat — crown volume plus tilt, curved brim, not "a disc with a ball";
- A4 G1–G6.

Provisional work items: `face` host family (jaw block, Loomis cross anchors); taper-first-class;
`hair-mass` family with tip zigzag and flow; hat crown silhouette + brim curvature.

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
