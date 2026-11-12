# 0_ROADMAP ? current product advance

## Goal and authority

The 2026-11-12 user clarification is authoritative: build a drawing workbench for VLM creation,
with useful simple defaults, optional refinement and accumulated drawing skill. The purpose is
`1_PROBLEM.md`; acceptance is `2_GOAL.md`. Reference imitation develops the product and practice.
The former R1?R4 plan and its failure evidence are preserved in
`../.scratch/history/roadmap-before-vlm-studio.md`; they are not current execution requirements.
The sealed brief remains unread and unreleased. Historical images and parts remain unchanged.

## Current evidence

- Upstream history through `0a28db7` has been reconciled without replacing the studio direction.
  The later legacy portrait is `A-full-figure-v2` at reviewed artwork revision `90ff009`, with
  A3/B4/C3/D1–3/E4–5/F3–4 and no whole-art pass. Its attempted W2b repair was reverted. The complete
  old plan is `../.scratch/history/roadmap-upstream-0a28db7.md`; original v2 records are retained.

- A full portrait exists; partial historical user acceptance of A-cloth-v8/B-hand-v2-r1 is retained,
  not generalized to later images. Whole-image art and transfer remain unproven.
- A-full-figure-waist-r1 is a small line/material cleanup. Existing independent review does not claim
  a structural or whole-artwork pass. The chest/waist diagnosis identifies a projected gap, not a
  demonstrated solution. It remains a useful future work item.
- Current code generates dedicated reference-seeded contours and uses depth visibility. Existing
  hair-mass is a width band around 2?5 gesture points. It lacks revision-bound selection/local edits.
- This checkout is an intentionally sparse recovery with pre-existing deletions. Product development
  uses the isolated codex/vlm-studio worktree; the recovery checkout is left untouched.

## Advance A ? a part the VLM can actually revise

**Visible outcome:** a good default hair lock, its alignment/selection view, and a real local edit
sequence with before/after images. A clean small composition will demonstrate reuse after the part
is independently reviewed. This is workbench capability, not a finished portrait claim.

**Required operation:** instantiate from a small gesture; select a semantic edge and bounded influence;
see where the action lands; preview a screen-direction push measured in object widths; accept or
undo. Stable endpoints and unrelated objects survive. Stale previews cannot overwrite a newer scene.

**Implementation:** scripts/studio, using the existing depth engine. JSON scenes remain text-authored;
SVG paths are compiled output. CPU-only rendering. First validate one well-made primitive; expand the
catalog only when real drawing requires it.

**Evidence:** meaningful mechanical checks for edit locality, endpoint protection, stale-state refusal,
undo, invalid geometry and depth crossings; actual CPU-rendered default and successive-edit images;
fresh-context image review. Readability and aesthetics require image evidence, not those checks.

**Owner:** main agent integrates code, artifacts and current docs. Fresh-context reviewers see images
only at checkpoints. Human taste feedback is requested for concrete unresolved choices and remains
asynchronous; silence is not acceptance and does not stop independent work.

**Checkpoint:** after the first rendered edit sequence, choose between improving default shape,
changing editing affordances or proceeding to a small composition based on observed outputs.
If repeated edits do not help, change the mechanism or selection design rather than adding knobs.

## Advance B ? draw with the workbench

Use accepted part operations in a small original composition and in one bounded area of the portrait.
This makes easy-default quality, controllability and practical reuse visible. Preserve all old artwork
versions. Evolve new part versions when needed rather than patching around frozen defective geometry.
A head or hand primitive is introduced only with its own satisfactory default and useful edits.

## Advance C ? broaden creation and externalize the craft

Choose subsequent subjects from actual gaps. Distil demonstrated drawing operations and visual
failure diagnoses into a concise runnable skill. Test another intent-led work using the workbench and
that skill. Keep task-specific constants separate from reusable practice. A bounded original body of
work is evidence of capability; neither a universal creativity claim nor a Starry-Night deadline.

## Resource boundary

The user paused all local GPU training/inference/benchmarks/GPU-dependent validation on 2026-11-12.
No new authorization was given. CPU geometry and static image review may continue; browser rendering
must disable GPU. Do not substitute heavy CPU training. No generated pixels in authored final work.

## Active execution

The first editing prototype is implemented: simple lock, visible selection, compact local pushes,
preview/accept/undo, one-sided width, independent gesture and thickness, and implementation-bound
stale-state refusal. 36 operation/visibility/oracle tests and 81 CPU smoke checks pass; current SVG
rebuild and repeated CPU PNG are identical. `evidence/studio-hair/README.md` indexes actual studies.

**Portrait/hair visual gate remains open.** Both independent reviewers rejected successive legacy portrait
integrations: roots read as caps, horizontal cuts or insertion near the eye; old face-side strips and
back curtains compete with the new mass. Shoulder visibility and curvature improved but do not close
that gate. Those attempts are frozen; no further same-assembly root tweaks are active.

A clean frontal head macro now exists under `examples/studio/head_probe.py`. It reuses legacy
face/eye construction, contains catchlights in their aperture, fuses same-material front hair,
and separates exact rear-cut geometry from intentional smooth face/front-hair artwork. The native
CPU SVG backend rendered one in-process sample in 0.029 s; this excludes process/import startup.
40 focused/inherited tests pass, including two raster negative controls. A prior claim that generic
smoothing necessarily bowed below a straight cut was not supported by its negative control and was
withdrawn; the verified effect is different corner coverage, not that alleged overshoot.

Blind image reviewers still identify cap-like/planar hair, face/ear simplification and rear-cut
stiffness. A separate execution-capable reviewer, given the explicit flat-cartoon head-component use,
ran default and 0.92 eye-scale commands without source edits and found minimum practical usability,
real local eye control and no blocker requiring a redraw. This closes only that bounded usability
question, not whole-artwork quality or general head/hair mastery. The user explicitly answered
“可以作为一个默认预设” to the displayed 09 sample. This accepts that simple flat-cartoon preset
direction; it is not acceptance of the legacy portrait or all future variants.

The head is now a first-class studio node with eye/face/hair selections, semantic parameter previews,
child-lock screen-direction pushes under parent tilt, accept and exact mixed-edit undo/replay.
`evidence/studio-head-integrated/` records the actual sequence, 48 passed tests, 81 CPU smoke checks,
locked environment installation and repeated SVG/PNG byte identity. These are operation evidence,
not whole-artwork acceptance.

Sky/hills/moon/sun presets and undoable insertion/object moves now compose two distinct small scenic
backgrounds. `evidence/studio-composition/` preserves the real edits and both review pairs. The first
palette-swap approach was too repetitive; revised landform, focal placement and a rooted pine group
improved the variation. Fresh critics still find sparse scene character, colour-band hills and
repeated tree icons. These are background/component evidence, not a finished-art gate. 54 combined
tests and repeated current SVG/PNG bytes pass.

An independent creator, given only the skill/public commands and a new dual-avatar intent, completed
seven edits without source, existing images or JSON/SVG workarounds. `evidence/studio-transfer/` keeps
its raw result and critical image-review pair. It exposed a bob-only blue-line palette omission,
stale stock intent and missing creation-time canvas controls. These operation gaps are corrected;
the repair is labeled assisted, with a pre-fix failing regression, 55 combined passing checks,
unchanged default-head PNG and changes confined to the partner's hair. Review still finds similar
faces/expressions, rigid hair and excess lower whitespace; no whole-cover art pass is claimed.

Head expression/gaze is now implemented with actual feature selection, coordinated lid/brow/mouth
changes and conjugate attention. An over-closed prototype was rejected and corrected after image
and execution review. `evidence/studio-expression/` preserves both failures and a balanced variant.
60 combined tests and 81 CPU smoke checks pass; the prior default-head PNG is unchanged. A composed
community-banner candidate has a conditional minimum-usefulness review, with hard hair, simplified
ears and limited facial acting still criticized. Its human taste question is pending asynchronously.

The front-view open-hand primitive is integrated after comparing the legacy ellipse generator and
several knuckle constructions. It has five distinct digits, semantic palette/spread/handedness,
visible tip handles and bounded screen-direction edits about fixed knuckles. An independent operator
used only the skill and public commands to compose a head-and-hand greeting; it deliberately
discarded an unhelpful finger edit. This is a separate-parts greeting asset, not an attached body rig.
71 operation/checker/visibility tests and 81 CPU smoke checks pass; repeated hand and greeting SVG/PNG
are identical, and the accepted default-head PNG remains unchanged. See
`evidence/studio-hand/README.md` for failure contrasts, independent reviews and exact verification.
Blind critics retain rigid hair, hard thumb-side transitions and limited volume.

A contradictory blank-image observation was investigated rather than used to change the drawing.
The compared files decode to identical complete pictures. The review pack now preserves original
PNG bytes and reports their SHA256; this reduces changes in the delivery path, not a proven cure
for an unidentified viewing problem. Original observations and the correction remain together.

Generic colour masses now form an editable lower-level surface: block/oval, taper/rounding, fill
and ink, and four protected arc selections with screen pushes. A root-authored coastal lighthouse
and a separate independent desk-lamp/book creation test subjects outside the preset catalog. The
independent creator used seven generic masses through the skill/public CLI and discarded an
unhelpful local shade edit. It exposed an arbitrary thin-mark width floor, corrected with a
pre-fix failing regression and a separately labeled fine-line repair. Original actor scene/source
and workaround remain unchanged. Fresh critics recognize the lamp but retain ambiguous book
identity; the coastal scene retains schematic cliffs and water/contact ambiguity. No art gate closes.
79 combined tests pass; current default/head/hand/coast and both lamp versions repeat identical
SVG/CPU PNG, and earlier default head/hand pixels are preserved. A working-source/export collision
found during replay also has a pre-fix failing regression and CLI input-preservation guard.
See evidence/studio-shape/README.md for source bindings, review provenance and exact limitations.

Related semantic settings now form one visible, atomic --change proposal. Controlled public-CLI
replay of the actual lamp plan reduces accepted records from 63 to 28 while preserving the exact
scene and PNG. A separate independent six-part toy rocket actually views complete groups, exercises
one-step undo/replay and rejects/corrects an ill-seated nose. Its fresh image critiques find a
clearly readable emblem plus minor joint/border issues. They also expose 24 real interior fin flecks:
disjoint coplanar fins unnecessarily triggered compound triangle clipping. The renderer now proves
commutativity from disjoint painted projections for every overlapping depth-interval pair; true
crossings retain the depth solver. The original scene is unchanged, the diagnosed flecks disappear,
and a second fresh image pair sees no new defect. Raw actor source/artwork remain intact.
85 combined tests and current default-head/hand/mass byte preservation pass.
See evidence/studio-parameters/README.md for independent use, exact replay, rendering diagnosis,
review provenance and the boundary on genuinely intersecting masks.

Visible named mounts and an authored parent graph now preserve projected point connections. The
initial joint measurements show that the old elbow/cap/footing already overlap: placement cannot
be blamed for every seam/volume critique. An independent four-mass cactus views both mount images,
rejects a wrong arm tilt and an awkward tip, and moves the full three-link chain by editing only
the pot. A six-mass pinwheel study changes only handle length; all raw descendants remain identical
while their resolved centers follow by 32px. Preview, detach, offset nudges, stale/cycle refusal and
contextual head/hand/lock editing are covered by 94 combined passing tests. Seven current artworks
repeat, with previous defaults and the raw actor PNG unchanged. A real inset .65 refusal exposed an
unnecessary half-width bound and missing help range; the corrected -2..2 range is documented and
tested, with the original outcome retained. See evidence/studio-attachment/README.md.

**Visual limits remain open.** Fresh critics find the pinwheel too petal-like, with no folded
direction; the cactus has awkward branch contours. Point connectivity does not supply curve shape,
material or a smooth joint. No whole-art gate closes.

An editable rounded stroke now fills the gap between a generic closed mass and raw paths. The
controlled comparisons retain existing rounding-only tuning, two round segments and one continuous
curved cactus branch; fresh critics find the continuous icon coherent with no serious join defect.
Swept wheel vanes communicate direction better but remain ribbons rather than proved paper folds.
A six-component original waving character uses actual chin/wrist and positioned shoulder mounts.
First fresh review exposed tube-like arms and an ambiguous sliver sleeve; actual accepted revisions
change shirt shape, remove the isolated shade stripe and clarify the relaxed arm. The refined fresh
review finds a usable connected flat character, with rigid torso and line-weight limits remaining.
It is available as examples/studio/waving_character.json. No human artwork acceptance is inferred.

106 combined operation/checker/visibility tests pass. Seven previous defaults/artworks preserve
exact PNG bytes; the new default, character and continuous cactus repeat the observed image.
See evidence/studio-stroke/README.md for comparisons, actual history, review provenance and limits.
A fresh public-CLI creator completed a separate five-part greeting using only the skill/help,
with visible chin/shoulder/wrist inspections and a useful pinned-root terminal correction. Its
report records one selection-view sequencing deviation, two declined clipping proposals and a
recoverable hand-width refusal. Fresh image critics find a clear greeting avatar, but a compressed
arm and small pale shoulder notch remain. This is bounded reuse, not human acceptance or full
anatomy. The many inspect/preview/accept calls remain a practical efficiency limitation.

**Next action:** test composition revision beyond adding nodes: replacing/removing an obsolete part currently requires
re-authoring or undo, which is a real gap for the requested iterative workbench. Preserve mounted
children and recoverable history in any removal design. Use a real drawing revision to decide the
operation rather than adding another subject preset. Keep the full VLM-creation goal.
More presets alone cannot establish open-ended creative capability.
Do not turn a hand icon or this cover's limited usability into a whole-portrait/illustration pass.
Preserve the legacy portrait. The development branch is
`codex/vlm-studio`, pushed through the existing SSH identity; main has not been overwritten.
