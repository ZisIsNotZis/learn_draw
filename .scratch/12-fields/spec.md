# 12 — L5 fields: backdrop, curtain, water

Status: ready-for-agent (blocked)
Blocked by: 10-cloth, 11-ribbon

## Issue

Rung 5, and *only now* the soft tier. The portrait reached for gradients, opacity and blur first and
got mush: `blur: std 6` over the four largest colour fields, on a reference that is flat cel art with
crisp boundaries. Soft-field technique is legitimate; pointing it at the whole figure is not.

## Scope

The background field, the hair/curtain masses that read as atmosphere, and the water. Flat where the
reference is flat; soft only where the reference is genuinely soft, and stated as intent.

- Blur is allowed only on a named field with a stated reason; never on structure
- Keep the figure's silhouette reading: fields go behind it, or inside a clip — never smeared over it

## Acceptance

- [ ] every soft-field node has a one-line reason in its `desc`; a field with no reason is deleted
- [ ] the figure still reads with fields removed and re-added (proves they are atmosphere, not structure)
- [ ] no blur applied to any structural shape (silhouettes, outlines, face features)
- [ ] diagnostics clean; fresh-eyes review reports no "washed out / mushy / can't tell where anything is"
- [ ] iteration log + evidence composite

## Comments

- 2026-09-14 agent(pi): created as rung 5 — deliberately last. Soft fields before line art and structure
  is the single most expensive lesson from 05 (see `docs/drawing/principles.md` P14–P21 context).
