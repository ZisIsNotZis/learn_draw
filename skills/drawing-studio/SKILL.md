---
name: drawing-studio
description: Create and refine programmatic flat-cartoon heads, hair locks and small scenic illustrations with learn_draw's revision-bound workbench. Use for scene composition, semantic feature controls, visible object placement, local edge pushes, previews and undo. Supported scenic presets are sky, hills, moon and sun.
---

# Drawing studio

Run from this repository with `python -m scripts.studio`. Use the current goal and progress in
`docs/0_ROADMAP.md`; exact scene fields and limitations are in `docs/7_INTERFACE.md`.

## Work one visible issue

1. State a drawing issue and what must stay fixed. Start from a useful default (`new scene.json --kind head`, or omit kind for a standalone lock)
   or an existing scene; optional shape controls are in the interface document.
2. `inspect scene.json --feature eyes --outdir VIEW` for a head. Choose face, hair, object,
   left-lock or right-lock for other features; standalone locks use `--side left --at .55 --radius .30`.
   Add `--object ID` when several objects exist.
   Read artwork, alignment and edit-closeup. Confirm the highlighted edge is the intended edge.
   Left/right edge names follow root-to-tip travel; movement directions refer to the screen.
3. For a semantic feature use `preview scene.json --selection VIEW/selection.json --set eye_scale
   --value .92 --reason "Quieter eye proportions" --outdir TRY`. For a selected lock edge use
   `preview scene.json --selection VIEW/selection.json --move right --amount .10
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
Only a successfully rendered ready candidate can be accepted. A failed render supplies no image list.
Root and tip are protected by an interior influence interval. A crossing/collapse refusal asks for
a smaller move or a better gesture, not manually corrected generated vertices.

## Choose the right operation

- For a landscape, `new scene.json --kind landscape`, then `add scene.json --kind moon` or sun.
  Insertion is undoable. Inspect the named object before revising it. Try `--set fullness --value .28`
  for a slimmer crescent, `--set style --value day` on sky, or horizon/relief on hills. Inspect lists
  the controls of the actual selected object; exact fields are in the interface document.
- To place an entire head, lock, moon or sun, inspect `--feature object` and use `--move`.
  Object-move amount is a fraction of the shorter canvas dimension; a local lock push uses lock width.
  Movement is in screen space even for tilted parts. Canvas-wide sky/hills use their semantic controls.
  Compare the clean image and orange current / pink dashed previous boundary before accepting.

- Head defaults require no path input. Inspect exposes allowed controls: eyes offer eye_scale/iris_color;
  face offers jaw/skin_color; hair offers hairstyle/hair_color. Object exposes size, tilt and depth.
  Child-lock pushes preserve endpoints and the other lock; screen directions account for head tilt.
- For a character's intent, inspect `--feature expression` and preview `--set expression --value
  curious` (or gentle/neutral/smile). The overlay includes brows, mouth and eyelids that move together.
  Inspect eyes for `--set gaze --value 1` to look toward the head's right, or -1 toward its left.
  Check the actual reading, especially at small size: a preset name does not establish natural emotion.
- Choose the canvas when creating a scene with `new cover.json --kind head --size 960x540`;
  `--background '#rrggbb'` sets its paper. Select object and `--set intent --value "..."` when the
  authored purpose changes. Stock descriptions deliberately avoid mutable hairstyle/colour claims.

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
the study README, never inferred from the existence of an image. `evidence/studio-head/` preserves
head studies and bounded usability review; the user accepted the simple flat-cartoon default preset.
`evidence/studio-head-integrated/` demonstrates semantic/local edits and exact undo/replay.
This establishes a bounded head-component operation loop, not general drawing mastery. Human taste questions are
specific and asynchronous; continue independent work while awaiting a reply.

`examples/studio/compose.py --theme moonrise|daylight --outdir FRESH` replays a documented original
composition through the public CLI, without a reference. Its choices are a demonstration, not a
formula for every picture: choose your focal point, negative space and palette for the actual intent.
Inspect defaults first. Preserve a useful silhouette; additional marks must serve grouping or meaning.
Changing a seed or palette does not establish a new composition: inspect the actual silhouette and
focal placement. Simple scenic presets can be useful backgrounds while remaining insufficient as
finished illustrations. Two differently coloured instances also do not establish new facial anatomy
or expression; keep that capability boundary explicit.
