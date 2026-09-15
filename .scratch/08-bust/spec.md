# 08 — the head: jaw, face, hair, hat (slice home for milestone M2)

Status: ready-for-agent (blocked by M1 — the assembly must exist before the head can be patched into it)
Blocked by: 13-assembly (M1 exit gate passed)

Re-scoped 2026-09-15: this is no longer "rung 1 of a ladder that starts from nothing". The project
has a baseline (`STATUS.md`), and this ticket is the **M2 slice** that patches the head of the
assembly. Its work still happens here; its output merges into `13-assembly/work/spec.yaml`.

## Entry state — corrected (2026-09-15)

The previous status of this ticket said `blocked by 06, 14`. Most of that has landed: `mirror` and the
`eye` family are in `scripts/relate.py`, canons are measured in `vocabulary.md` set B, and the sunhat
near-edge occlusion is fixed (P17 slice split). Still missing for M2: `arc`, `align`,
taper-as-first-class, and the `face` host family (the ellipse host is the round-chin cause).

**The night session already drew this slice and it failed the gate.** `14/evidence/final/v3.png`
(a bust, committed as "FINAL IMAGE") never faced a fresh reviewer with the bundle, and measures
coverage 0.113 against the baseline's 0.514. Its face renders at review scale as "two thin eye
slits" while the full-resolution render does carry two-tone irises, glints, a tapered lash, brows and
nose/mouth marks — the marks are real, the *judging scale* was wrong. Both facts belong to this
bust's re-assessment and to M2's acceptance (hence the 1:1 pane now shipped in every `check` bundle).

**The bar is therefore not a blank canvas — it is the baseline's head.** M2's acceptance is
"preferred over the baseline's head in a blind A/B", not "better than the night's bust".

## Issue

The ladder jumped from a flat 800×800 duck straight to a full 1024² figure with ribbons, water and
soft shading. The bust is the missing rung: the smallest drawing that has the character's actual
difficulty (hair silhouette, hat over hair, occlusion) and nothing else.

Draw the bust as a **proper drawing** — coherent artwork in the reference's style, judged by looking
at it, not by proximity to one photograph (P14).

## Scope

Head, hair (mass + bangs), hat, shoulders. Nothing below the shoulders. ~25–35 shapes.

- Reference: `image.jpg` crop of the bust, `ref lineart` + `ref palette` derived once
- Authoring: `docs/drawing/abstraction.md` — relations and vocabulary, no hand-typed coordinate
  floods (P19). Geometry that needs more than ~4 coordinates comes from `trace`/`region` or a
  relation; the reference may *seed values*, then gets closed
- Line art first as a real stage (this is the style's defining layer, and the portrait skipped it
  entirely): closed shapes + edge strokes before any soft work
- Add vocabulary nodes only when this drawing fails without them

## Acceptance

Milestone acceptance is owned by `docs/drawing/roadmap.md` — **M2 exit AC A1–A4 plus gates G1–G6**.
Do not restate it here. Ticket-specific technical criteria:

- [ ] renders from a relational spec; `relate.py` diagnostics clean (no OFF-CANVAS / CLIPPED / SUB-PIXEL / CONTRADICTION)
- [ ] every major shape carries its edge stroke (hair mass, hat brim/crown, shoulders, face)
- [ ] a 2x head crop is preferred (or tied) against the same crop of the baseline — the M2 acceptance
- [ ] non-circular jaw/chin (a `face` host family, not the ellipse host)
- [ ] hair tapers (no constant-width tubes); hat reads as a hat (crown volume + tilt, curved brim)
- [ ] no shape in the spec carries more than 4 hand-typed coordinates
- [ ] output merged into `13-assembly/work/spec.yaml`; iteration log in `log.md` via `scripts/draw log`
- [ ] `principles.md` appended **only** if something transferable was learned (P23/P24 already cover
      the ratchet and probes-as-rungs lessons)

## Comments

- 2026-09-14 agent(pi): created as rung 1 of the rebuilt ladder after freezing 05.
- 2026-09-15 agent(pi): re-scoped as the M2 slice home; entry state corrected (the night's bust is
  input and evidence, not progress); the bar is the baseline's head. Blocked by M1's exit gate.
