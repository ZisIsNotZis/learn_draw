---
name: drawing-studio
description: Create and locally refine programmatic hair locks with learn_draw's revision-bound drawing workbench. Use for studio scene authoring, edge alignment, previewed contour edits, or restoring accepted edits. Other object families are not implemented by this slice.
---

# Drawing studio

Run from this repository with `python -m scripts.studio`. Use the current goal and progress in
`docs/0_ROADMAP.md`; exact scene fields and limitations are in `docs/7_INTERFACE.md`.

## Work one visible issue

1. State a drawing issue and what must stay fixed. Start from a useful default (`new scene.json`)
   or an existing scene; optional shape controls are in the interface document.
2. `inspect scene.json --object ID --side left --at .55 --radius .30 --outdir VIEW`.
   Read artwork, alignment and edit-closeup. Confirm the highlighted edge is the intended edge.
   Left/right edge names follow root-to-tip travel; movement directions refer to the screen.
3. `preview scene.json --selection VIEW/selection.json --move right --amount .10
   --reason "the inner edge is too straight" --outdir TRY` (one shell line).
   Amount is a fraction of nominal object width. Read the resulting normal artwork and overlay;
   compare the local change and whole shape. The preview has not overwritten the scene.
4. Accept with `accept scene.json TRY/candidate.json` when the change helps the stated issue;
   otherwise discard TRY. Inspect the new revision before the next edit. Use `undo scene.json`
   to recover the previous accepted input exactly. Opposite small corrections are normal work.
5. At a useful visual checkpoint run `python scripts/draw.py check TRY/artwork.png --outdir CHECK`.
   Give the listed images alone to fresh-context reviewers. Record actual observations and revision
   bindings; mechanical correctness and author judgment do not establish artwork acceptance.

Stale selections/previews are refused after scene or implementation changes; inspect again.
Root and tip are protected by an interior influence interval. A crossing/collapse refusal asks for
a smaller move or a better gesture, not manually corrected generated vertices.

## Choose the right operation

- `sweep`, `angle` and `length` shape the whole gesture. A local boundary push refines a segment.
- `width_side: right` grows width to the right of the root-to-tip gesture, keeping its left edge.
  Changing width preserves that edge; sweep is independent of thickness. Both-sided width is default.
- Inspect in context before claiming a hair primitive works. An isolated smooth tapered shape can
  read as a leaf; a round root can become a visible cap when placed in front of the scalp. A correct
  local shape may still cover a sleeve or eye that must remain readable.
- Depth is a separate operation. A sloping plane crossing a flat hat produced a horizontal exposure
  boundary in the portrait study. Putting the root inside the host and behind face/fringe removed
  that particular mechanism; the visible root grouping still failed review. Visibility remains computed.
- Tone regions follow edited boundaries. Adding fine lines does not settle attachment or silhouette.

## Evidence and scope

`evidence/studio-hair/` preserves rejected early studies, real edit sequences and context experiments.
Their SVGs are frozen historical inputs; current defaults may differ. Review dispositions belong to
the study README, never inferred from the existence of an image. This skill documents a prototype
operation loop, not a passed head/hair system or general drawing mastery. Human taste questions are
specific and asynchronous; continue independent work while awaiting a reply.
