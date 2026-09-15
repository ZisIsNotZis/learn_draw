# 13 — the assembly: one drawing that every milestone patches

Status: **M1 COMPLETE 2026-09-15** (exit criteria met; baseline not promoted) — M2 next
Blocked by: —

Re-scoped 2026-09-15. This was rung 6 of the old ladder, "blocked by 12-fields", i.e. reachable only
after five rungs that were never built — which is why nothing accumulated and the night session's
three probes could each be mistaken for the deliverable. It is now the **home of the artifact**: the
drawing grows here from M1 onward, and the other rung directories keep their specs as *slice homes*
whose output merges here.

## The artifact

`.scratch/13-assembly/work/spec.yaml` — one relational spec, the whole figure. Nothing here is ever
replaced wholesale; it is patched, milestone by milestone, and its `log.md` records which milestone
patched what.

Seed (M1 work item 1): `14-abstraction-research/work/final/final-full.yaml` — the relational head,
hat, hair and body skeleton from the night session, minus its "final image" claim. Promote, then let
that copy die as a source of truth.

## Why this matters (the failure it fixes)

Two artifacts were committed as "FINAL IMAGE" while sitting 4.5–5.6× below the project's own
baseline on coverage. Nothing in the loop compared a new render against the previous best, so
regression was invisible. See `14-abstraction-research/spec.md` → Verdict, and roadmap R1–R3.

## Scope

Compose the whole figure at 1024² from relations, in milestones:

- **M1** (here, now): composition and mass — the subject in the reference's place at the reference's
  scale, with the reference's masses present as flat shapes. No face detail, no folds, no soft fields.
- **M2–M4** (their own slice tickets, patching this spec): head quality, body/cloth, then the fields.
- **M5**: this spec redrawn with the image deleted.

## Acceptance

Milestone acceptance is owned by `docs/drawing/roadmap.md` — do not restate it here. For M1:
**exit AC A1–A4** (G1, G2, G3, G4, G5, G6 — G2b is deferred to M2 by D7).

### M1 — met 2026-09-15

- [x] whole figure renders from one relational spec; every overlap stated in `relations:`, no CONTRADICTION
- [x] coverage 0.528 ≥ baseline 0.514 — nothing deleted (G2)
- [x] G1 bundle, G4 diagnostics clean, G5 17 nodes all with intent / no outline > 4 points, G6 byte-identical
- [x] composition measured and placed from the measurement (`.scratch/13-assembly/work/measure-composition.py`)
- [x] reviewer evidence recorded, including a split verdict settled by measurement (P7)
- [x] `log.md` row per iteration with the gate evidence and the rollbacks
- [~] **baseline promoted — NO, deliberately.** The baseline is still the better drawing (two blind
      reviewers; grid distance 32.6 vs 39.1). See `STATUS.md` D8 — milestone complete and ratchet
      moved are different statements.
- [ ] composition demo: move the figure and scale the hat with ≤ 3 expression edits — **not yet run**;
      carried into M2 as a cheap check of the relational frame

### M2 — next

## Comments

- 2026-09-14 agent(pi): created as rung 6, blocked by 12-fields.
- 2026-09-15 agent(pi): re-scoped to the artifact home and activated as M1's entry point. The seed
  spec at `14/work/final/final-full.yaml` rendered (45 nodes, 10 layers, zero coordinate literals) but
  measured coverage 0.091 against the baseline's 0.514 — its framing and mass placement were wrong,
  which is exactly what M1 fixed.
- 2026-09-15 agent(pi): **M1 complete.** The assembly was rebuilt from measurements of the reference
  (colour-component bboxes/centroids in `vars:` with provenance) rather than from the seed's guessed
  framing. 7 iterations, 3 of them rolled back for making the drawing measurably worse — including
  one that improved a diagnostic while regressing the artifact (P25). Coverage 0.528 > baseline 0.514;
  the baseline nonetheless remains the better drawing and was not promoted (D8).
