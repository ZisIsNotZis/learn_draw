# 0_ROADMAP ? current product advance

## Goal and authority

The 2026-11-12 user clarification is authoritative: build a drawing workbench for VLM creation,
with useful simple defaults, optional refinement and accumulated drawing skill. The purpose is
`1_PROBLEM.md`; acceptance is `2_GOAL.md`. Reference imitation develops the product and practice.
The former R1?R4 plan and its failure evidence are preserved in
`../.scratch/history/roadmap-before-vlm-studio.md`; they are not current execution requirements.
The sealed brief remains unread and unreleased. Historical images and parts remain unchanged.

## Current evidence

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
tests and repeated current SVG/PNG bytes pass. The next capability test gives only the skill/public
commands and a new dual-avatar intent to an independent creator, without source or existing images.

**Next action:** inspect that independent creation result and any operational gaps before expanding
the catalog. A richer foreground subject and composition remain necessary for an illustration claim.
Preserve the legacy portrait. The development branch is
`codex/vlm-studio`, pushed through the existing SSH identity; main has not been overwritten.
