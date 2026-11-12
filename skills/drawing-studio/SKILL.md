---
name: drawing-studio
description: Create and refine programmatic vector art with learn_draw's revision-bound workbench, using generic editable colour masses and semantic head, hand, hair and scenic presets. Use for new-subject composition, grouped parameter previews, visible placement, digit-tip moves, local contour pushes, acceptance and undo.
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
   To configure one coherent part, use repeated `--change length=.17 --change width=1.8
   --change taper=.65 --change fill_color=#c98d4a` instead of --set/--value. Read the complete
   resulting preview before accepting; the group is one edit and one undo step. Controls must all
   belong to the inspected feature. Use one drawing reason for the combined decision.
   A lock-edge amount is a fraction of nominal lock width. Read the resulting normal artwork and overlay;
   compare the local change and whole shape. The preview has not overwritten the scene.
4. Accept with `accept scene.json TRY/candidate.json` when the change helps the stated issue;
   otherwise discard TRY. Inspect the new revision before the next edit. Use `undo scene.json`
   to recover the previous accepted input exactly. Opposite small corrections are normal work.
5. At a useful visual checkpoint run `python scripts/draw.py check TRY/artwork.png --outdir CHECK`.
   Give the listed images alone to fresh-context reviewers. Record actual observations and revision
   bindings; mechanical correctness and author judgment do not establish artwork acceptance.

Stale selections/previews are refused after scene or implementation changes; inspect again.
Only a successfully rendered ready candidate can be accepted. A failed render supplies no image list.
Lock-edge pushes protect root and tip with an interior influence interval. A crossing/collapse refusal asks for
a smaller move or a better gesture, not manually corrected generated vertices.

## Choose the right operation

- `new hand.json --kind hand` creates a front-view open palm. Inspect index, middle, ring, little
  or thumb before moving it: orange is the selected digit, white its movable tip-pad handle, green
  the fixed knuckle. `preview ... --move left --amount .04` moves that handle in screen space by
  .04 of its nominal digit span. Tilt and handedness are handled automatically. Accept or discard
  after reading both clean artwork and overlay. Other digits stay fixed; this does not curl fingers
  in 3D. Free-finger collisions are refused. Semantic finger_length / finger_lean are optional.
- Select hand object for handedness, spread, size, skin/ink/crease colour and depth. The default
  is a graphic hand icon; it is not a hand-turn, closed-fist or full anatomical rig. The old relational
  hand-lobe family is historical and is not the current hand authoring route.

- For a landscape, `new scene.json --kind landscape`, then `add scene.json --kind moon` or sun.
  Insertion is undoable. Inspect the named object before revising it. Try `--set fullness --value .28`
  for a slimmer crescent, `--set style --value day` on sky, or horizon/relief on hills. Inspect lists
  the controls of the actual selected object; exact fields are in the interface document.
- To place an entire head, hand, lock, moon or sun, inspect `--feature object` and use `--move`.
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

## Contradictory image observations

If a full-resolution image appears blank but another view of the same scene was visible, verify
report image SHA256 and scene revision before changing art. Compare decoded dimensions/pixels if
needed, reopen the original PNG and preserve the conflicting observation. An identical file is not
evidence that geometry disappeared. draw check preserves source PNG bytes in draft-fullres.png and
reports their digest. This reduces delivery transformations; it cannot guarantee an external viewing
surface. Never infer a model or rendering failure solely from a contradictory display.

## Create a subject outside the preset catalog

Use new scene.json --kind shape --id tower for a generic rounded colour mass; add more named shapes
with explicit intents. Inspect object to change length (height / shorter canvas dimension), width
(width / height), profile block|oval, rounding (0 sharper, 1 ellipse), taper (-.98 narrower bottom,
+.98 narrower top), stroke (width / height, 0 flat fill), fill_color and ink_color. Block uses a
superellipse, so sharp is still softly rounded. Oval ignores rounding. This is a silhouette, not a
3D solid or an attached child. Use screen moves and depth to compose; insertion starts in front.

For a local correction inspect --feature left|right|top|bottom --at .5 --radius .25. The orange
arc shows the influence; endpoint rings stay fixed. Preview --move left|right|up|down --amount .08
uses the nominal shorter shape extent and screen directions even under rotation. Arc at runs
clockwise: top left-to-right, right top-to-bottom, bottom right-to-left, left bottom-to-top.
The arc parameter follows nominal arc length; edited bounds do not reparameterize prior edits.
Inspect a new revision before each further operation. Reject an unhelpful preview. Combine these
shapes for new subjects instead of assuming a subject-specific generator must exist first.

Thin marks can use a tall shape with width .008 and stroke 0, rotated as needed. The initial
width floor .05 blocked this legitimate use; current minimum is .001. At very small sizes inspect
the actual raster: nominally thin geometry can be below a pixel. This does not add a centerline
brush or make a thick workaround aesthetically equivalent to a fine line.

Keep your working scene separate from VIEW/TRY exported scene.json/candidate.json/report files.
The CLI refuses an output/input path collision before writing. If you write a replay script using
the lower-level bundle API, it accepts a scene value and exports scene.json; it does not know where
you read that value. Use e.g. working.json and a different output directory.

## Place connected parts by visible named mounts

Inspect both parts with --feature anchors and separate output directories. Read both alignment
images: green labeled callouts identify the actual geometry, not guessed canvas coordinates.
Shapes have center/top/right/bottom/left (shape-local sides under tilt); other current macros have
center, and a standalone lock also has root/tip. The report lists actual available anchors.

After source CHILD and target PARENT inspections at the same current revision:
preview scene.json --selection CHILD/selection.json --attach PARENT/selection.json
--self-anchor bottom --target-anchor top --inset .04 --reason "Seat the support in the pot"
--outdir TRY (one shell line). Blue marks the target; orange is the proposed source and pink its
previous boundary. Inspect the clean artwork and overlay before accepting. Positive inset embeds
into a target shape surface by a fraction of that target's nominal shorter extent (range -2..2); negative leaves
a gap. Center has no outward surface direction, so use inset 0 for center mounts.

Accepted relations stay semantic. Moving/resizing/sculpting the parent recomputes its child mounts,
including descendant chains. A pin fixes one point and preserves the child's own screen angle;
it does not inherit rotation/size, fit two edges, smooth a joint or change depth. Planar overlap
and art treatment still need visual judgement. Sky/hills may be targets but not mounted children.
A connected-looking joint is not proof of a 3D solid, and a placement constraint cannot add volume.

To nudge a mounted object, inspect object and use the usual screen --move; it adjusts the retained
offset from the mount. To release it, inspect anchors then preview --detach with a drawing reason;
accept preserves its current visible placement. A local contour push that would move a pinned
shape anchor/tangent is refused; choose an interval away from it or detach. Other feature controls
remain on their usual selections. Source and target selections both go stale after any scene or
implementation change: inspect both again. Cycles and missing/unknown mounts are refused.
