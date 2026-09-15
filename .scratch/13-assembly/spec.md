# 13 — the assembly: one drawing that every milestone patches

Status: **ACTIVE** — this ticket owns the project's single drawing artifact (roadmap R1)
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
**exit AC A1–A3 plus gates G1–G6**. Ticket-specific technical criteria, additional to the gate:

- [ ] whole figure renders from one relational spec; every overlap stated in `relations:` and raising
      no CONTRADICTION
- [ ] a composition demo: move the figure and scale the hat by editing **≤ 3 expressions**, with the
      rest of the drawing following correctly (the acceptance 05's scene-format migration wrote for
      itself and never passed)
- [ ] the assembly survives a head-size change with no hand-fitted geometry breaking
- [ ] `log.md` row per milestone with the gate evidence (bundle path, `vs recorded best:` line,
      reviewer verdict)
- [ ] `scripts/draw baseline` promoted **only** when the gate passes and the reviewer prefers it

## Comments

- 2026-09-14 agent(pi): created as rung 6, blocked by 12-fields.
- 2026-09-15 agent(pi): re-scoped to the artifact home and activated as M1's entry point. The seed
  spec at `14/work/final/final-full.yaml` renders (45 nodes, 10 layers, zero coordinate literals) but
  measures coverage 0.091 against the baseline's 0.514 — its framing and mass placement are wrong,
  which is exactly what M1 fixes. Do not promote it as-is; patch it.
