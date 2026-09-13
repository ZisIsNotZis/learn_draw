# 08 — L1 bust: head, hair, hat, shoulders (ladder rung 1)

Status: ready-for-agent (blocked)
Blocked by: 06-relational-geometry

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

- [ ] renders from a relational spec; `relate.py` diagnostics clean (no OFF-CANVAS / CLIPPED / SUB-PIXEL / CONTRADICTION)
- [ ] every major shape carries its edge stroke (hair mass, hat brim/crown, shoulders, face)
- [ ] fresh-eyes subagent, given only REF vs DRAFT: identifies the subject unprompted and reports no
      structural error ("hat is not a hat", "hair is detached", "face is unrecognizable")
- [ ] no shape in the spec carries more than 4 hand-typed coordinates
- [ ] iteration log in `log.md` via `scripts/draw log`; ≥1 evidence composite in `evidence/`
- [ ] principles distilled (append to `docs/drawing/principles.md`)

## Comments

- 2026-09-14 agent(pi): created as rung 1 of the rebuilt ladder after freezing 05.
