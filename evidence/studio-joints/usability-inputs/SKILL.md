---
name: drawing-studio
description: Create and refine programmatic vector art with learn_draw's revision-bound workbench, using editable gesture strokes, generic colour masses and semantic head, hand, compact grip, hair and scenic presets. Use for new-subject composition, grouped parameter previews, visible placement, digit-tip moves, local contour pushes, acceptance and undo.
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
4. Let image-tool results return to the model before a separate acceptance call; loading an image
   and accepting inside the same script is not visual observation.
   Accept with `accept scene.json TRY/candidate.json` when the change helps the stated issue;
   otherwise discard TRY. Inspect the new revision before the next edit. Use `undo scene.json`
   to recover the previous accepted input exactly. Opposite small corrections are normal work.
5. At a useful visual checkpoint run `python scripts/draw.py check TRY/artwork.png --outdir CHECK`.
   Give the listed images alone to fresh-context reviewers. Record actual observations and revision
   bindings; mechanical correctness and author judgment do not establish artwork acceptance.

Default CLI feedback focuses on the selected part, controls, operation and file/image handles.
The complete scene report remains at files.report; use --full-report only when that broader data is
needed. Read actual images before acting. Reusing a preview directory for inspection invalidates
its old candidate because those preview images have been replaced.

If a CLI tool returns a live session handle, poll that same handle to a terminal result before
starting the next dependent inspection, edit or acceptance. Partial stdout and output files alone
do not prove completion. Do not restart on an observation timeout.

Stale selections/previews are refused after scene or implementation changes; inspect again.
Only a successfully rendered ready candidate can be accepted. A failed render supplies no image list.
Lock-edge pushes protect root and tip with an interior influence interval. A crossing/collapse refusal asks for
a smaller move or a better gesture, not manually corrected generated vertices.

## Place a component before committing paint

Use `place scene.json --kind shape --id NAME --reason "..." --outdir TRY` when composing.
It renders one pending component with orange boundary and labeled mounts; the working scene and
history are unchanged. Optional `--change NAME=VALUE` uses the preset's object controls, or
`--feature FEATURE` for that part. Initial `--at center|upper_center|upper_left|upper_right`
and `--offset X Y` use semantic canvas anchors and width/height fractions. Defaults need neither.
Read TRY/artwork.png and alignment.png before choosing a correction.

To correct the same pending shape, use `place scene.json --revise TRY/candidate.json --move left
--amount .05 --reason "..." --outdir TRY2` (one shell line). Its controls, placement and name are
retained. Screen moves use the shorter canvas dimension. Add optional --change controls to the
same proposal; use a different output directory from the candidate being read. Nothing has landed.
To connect it after observing its own mounts, separately inspect the working target's anchors, then
revise with --attach TARGET/selection.json, --self-anchor NAME and --target-anchor NAME. Existing
point-attachment limits and exact positioned-anchor inspection rules apply. Default pins keep angle
explicit; use optional --orient opposed for a persistent directional joint after inspecting both mounts.
Accept with `accept scene.json TRY2/candidate.json` only after reading the resulting image; undo
removes the entire insertion. Discarding a proposal requires no scene mutation. Reinspect after acceptance.
A stale/failed candidate cannot be revised or accepted. `add` is the older immediate convenience
for scripted replays; use `place` for this observe-before-insertion workflow.

## Editable upper body

Use --kind body for a simple long-sleeved upper body. It owns collar, torso and sleeves; head,
neck skin and hands remain separate components. Object offers pose=relaxed|offering|folded,
length, width, sleeve_width, cuff, angle, fill/ink colour and support depth. A pose supplies defaults;
explicit arms overrides persist when pose changes. Start a fresh body for an unmodified pose.

Inspect right-elbow or left-elbow, then preview --move left/right/up/down --amount .03. The amount
is a fraction of torso height, in screen space even when rotated. The elbow moves while shoulder
and wrist stay fixed. Inspect right-wrist/left-wrist to move a cuff; shoulder and relative bend ratios
stay fixed, so the elbow can move too. Observe clean, alignment and closeup before accepting.
Overfolded, too-thick, disconnected or collapsed geometry refuses; reduce the move or unfold it.
The shoulder feature exposes controls but is not a draggable joint. Optional side-prefixed controls
are wrist_spread, wrist_height, elbow_at and elbow_bend; ordinary work should use visible joint moves.

Named ports are neck and left/right shoulder, elbow and wrist (e.g. right-wrist). Inspect the exact
ports before attaching a hand's wrist or a neck. Default pins maintain point contact; child angle stays explicit. Optional --orient opposed
keeps an inspected wrist opposed to the cuff direction after pose edits. A neck/center-pinned body permits local
joint moves; a body pinned through a moving arm port must first detach. Material is continuous
across the shoulders. Internal left sleeve/torso/right sleeve depths are -1/0/+1 added to body depth;
an external prop at body depth+.5 can pass in front of chest and behind the nearer sleeve.
This is a bounded graphic garment, not general anatomy, inverse kinematics or cloth simulation.

## Keep a joint fitted during pose changes

Inspect exact source/target mounts and view both alignments. Preview --attach TARGET/selection.json
--orient opposed with the usual self/target anchors. This persists both point and opposed outward
direction: use hand/grip wrist, head chin, body neck or stroke root/tip as the source. A directionless
center refuses. Grip handle_left/right now expose outward handle axes; fitting a stroke root to
those ends lets external pole sections follow a turned hand. Fit each intended relation once, then
inspect and edit the parent elbow/wrist. Observe the whole chain, not only the joint marker.

With direction bound, angle is derived and omitted from exposed controls; focused feedback supplies
derived_angle. Detach bakes current angle/placement, preserving paint. Reattach without --orient to
return to a point-only pin while keeping the current orientation. An oriented stroke refuses free
terminal drags, two-endpoint binding and one-shot --aim; detach before choosing another constraint.
Depth, size and cuff width stay independent. Direction fit is not anatomy, pressure or physical contact.

New heads use a stable recipe frame automatically. Moving changes placement, not rounded facial
shape. Existing unframed heads keep old paint until an edit; reattaching a legacy head captures its
current frame and fixes its fractional chin-pin error. Frame values are tool-managed, not controls
to tune against the picture. Hair selections, endpoint locks, detachment and undo use the same frame.

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

- `new grip.json --kind grip` creates a compact flat illustrated closed hand **with its own handle
  segment**. Use this candidate vocabulary for simple held handles/poles, not a physical 3D hand
  that can enclose any existing object. Inspect object, palm, fingers, thumb or handle. Thumb offers
  thumb_reach / thumb_thickness; fingers offer fold_length; handle offers handle_span /
  handle_thickness / handle_color / handle_ink_color. These are bounded semantic parameters, not
  digit-tip drags. Inspect the selected shape before a --set or grouped --change, then read the
  clean preview and overlay, accept or undo. Preserve the known blind-image criticisms; detailed
  anatomy and whole-illustration finish are not established by this symbolic component.
- Grip mounts are wrist, grip, handle_left, handle_right, handle_top and handle_bottom. Inspect
  anchors before attaching a sleeve or extending a pole. The end names follow the preset through
  rotation/mirroring; they are not screen left/right. Connect external handle legs or pole sections
  to the included segment using the ordinary stroke attachment/endpoint operations below. A 90-degree
  grip angle turns its handle vertical. thumb_side chooses the thumb's side in the unrotated preset.
  Whole-object length/width/angle/colour and normal preview/accept/undo are available.
  The report's dimensions_canvas gives wrist_width and handle_thickness in shorter-canvas units;
  these can set a matching sleeve/pole thickness. Observe continuity rather than relying on names.

- For a landscape, `new scene.json --kind landscape`, then `place scene.json --kind moon --reason "One quiet focal moon" --outdir TRY` or sun.
  Observe and accept the proposal; insertion is undoable. Inspect the named object before revising it. Try `--set fullness --value .28`
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

Use new scene.json --kind shape --id tower for a generic rounded colour mass; place more named shapes
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

For carrying/grasping/pouring or a mark connecting movable objects, read
[object interaction](references/object-interaction.md) before adding detail. It records the actual
watering failures, depth-based wrap experiment and the demonstrated far-end drift and the newer endpoint-binding remedy.

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

## Paint a rounded or curved gesture

new line.json --kind stroke creates a clean round mark without path coordinates. For a composed
scene place --kind stroke --id NAME with --reason/--outdir, then observe and accept. Inspect object for a coherent --change group: length is the
root-to-tip chord / shorter canvas dimension (.005..2, default .4); thickness is independent
canvas fraction (.001..1, default .045). Angle points root to tip: 0 down, 90 right, 180 up, -90 left.
Bend (-1..1, default 0) bows the middle sideways while preserving terminals. Start_width/end_width
are thickness multipliers (0..4, default 1); start_cap/end_cap are round (default) or flat.
Ink_width is an independent canvas fraction (0.. .1, default 0). Fill/ink/shade colours are optional.
Shade none is default; left/right adds a simple material-relative colour plane, not physical
illumination or a complete paper fold. Use it only when the actual image becomes clearer.

Inspect --feature spine --at .5 --radius .25 before a local --move. The highlighted midline, white
focus and green terminals show the action; amount is a fraction of nominal thickness. A push keeps
both terminals and width fixed. Inspect root or tip for a free-terminal move; amount then uses the
shorter canvas dimension and keeps the opposite end fixed. A pinned terminal cannot move; a free
terminal can move when the opposite one is pinned. A center pin requires detaching before terminal
moves, or use object parameters to reshape around the pin. Crossing/collapsed paint is refused.

Stroke root/tip mounts lie at the round-cap centers, so ordinary joined marks overlap naturally.
A longer mark need not become wider. Try one continuous bowed mark before layering many rounded
blocks around an elbow. Inspect clean artwork after every proposal; one functioning edit is not
proof it improved the drawing. The earlier cactus/wheel comparisons retain that distinction.

## Connect real features in a character

The head now exposes chin at its own face-midline contour; a hand exposes wrist at its generated
wrist joint. Stroke roots/tips can connect neck/sleeve gestures to these actual points. This is
projected construction with independent depth, not a general 3D anatomy rig.

For an exact shape-edge position, inspect --feature anchors --anchor right@.2 (or left@.8 for the
upper left side). The fraction follows the existing clockwise arc convention continuously, rather
than jumping between sampled stations. Read that actual labeled point and closeup before attaching.
Source and target --self-anchor/--target-anchor can be omitted when each inspected one exact point;
the preview infers those points. Otherwise defaults are center. A positioned address must have
been inspected explicitly; a hidden, guessed point cannot be substituted. Parameter changes still
use object/feature inspections. A local edit that changes a pinned point or its tangent is refused.

## Replace obsolete parts without rebuilding the scene

Start with new scene.json --kind blank for an empty paper, then place, observe and accept named parts. Inspecting blank
paper without an object shows the canvas; add an object before selecting a feature.

To remove a part, inspect --object ID --feature object and read its actual outline and descendants
in the report. Preview --remove with a drawing reason. By default direct legacy children are released at
their current visible placements; their children retain their relations. A two-ended stroke releases
only pins whose targets were deleted, retaining its other pin and current paint. Use --cascade only when
you intend to remove the whole descendant chain. Read clean artwork and alignment: red dashed
labels are removed old paint; blue labels are retained children released in place. Neither guide
is part of the clean image. Accept or discard; undo restores the full prior scene and relations.

For a replacement, remove the old part with the appropriate child policy, preview a new named preset with place,
then refine/accept it and inspect both mounts before reconnecting retained parts. The steps
are separate recoverable edits, not one atomic replace transaction. Removing the last part leaves
valid blank paper; add/undo still work. An eyes/edge/anchor selection cannot delete a whole object.

## Keep a gesture connected at both ends

Inspect a stroke with --feature root or tip and separately inspect its destination with --feature
anchors (optionally --anchor NAME). Read both actual alignment views. Preview --bind-end
TARGET/selection.json with a drawing reason; --target-anchor and --inset use the inspected mount.
The source end comes from its inspected root/tip feature. Existing legacy root/tip pins are retained;
a center pin must be detached first. Read the clean image and blue pinned-end rings before accepting.

One pin keeps a freely editable chord. Two pins derive length/angle from the target geometry, so
those controls disappear; bend/thickness/colour and protected local spine pushes remain. Do not
move an entire doubly pinned stroke or drag a pinned end. Move its targets, adjust its gesture, or
inspect that root/tip and preview --unbind-end. Releasing one/both pins preserves the current paint.
--detach from an anchors inspection releases all pins. Default deletion of a target releases only
the affected link in place, retaining the other pin; cascade follows both dependencies. Cycles and
collapsed/invalid derived gestures are refused. These are projected constraints with independent
depth, not a fluid simulation or a general grip/physics solver.

## Aim an observed connected stroke into its join

Inspect the source stroke with --feature root or tip. Separately inspect the target with
--feature anchors --anchor NAME and read both images. Teal arrows show outward join direction
where it exists: a surface edge normal, stroke terminal tangent or hand/grip wrist direction.
Centers and handle-end mounts may be directionless; the report keeps direction separate from
surface normal, so a directional wrist is still not an inset surface.

Use `preview scene.json --selection END/selection.json --aim TARGET/selection.json --reason
"Let the cuff enter along the wrist" --outdir TRY` (one shell line). The two parts must already
share this exact endpoint/mount relation, in either dependency direction. The operation opposes
the outward arrows by changing only bend, preserving both stroke endpoints, widths and existing
connections. Read clean and magnified images before accept/undo. A center or unreachable angle
is refused: reposition a target or choose another gesture rather than moving the locked ends.

This fits the current picture once. It does not add a persistent orientation constraint, fit
cuff widths, align both end tangents independently or establish anatomical/physical contact.
If moving/resizing a connected target changes the chord/direction, inspect again and re-aim.
Existing endpoint pins continue to follow their positions. Small-part mount labels use separate
rails and screen-sized guides in closeups; the clean artwork never contains these aids.
