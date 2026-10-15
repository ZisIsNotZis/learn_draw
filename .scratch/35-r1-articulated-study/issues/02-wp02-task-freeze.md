# Ticket — R1 WP02 reference/task freeze and revision

## Scope and authority

WP02 maintains `.scratch/35-r1-articulated-study/work/task-freeze.md`, sealed heldout custody (read-only), and this ticket. No construction, code implementation, artwork, other WP evidence, vendor edits, dependency/runtime changes, staging, or commit is authorized here. Preserve pre-existing worktree state.

Main's explicit product-routing decision clarified the authority boundary: collar/garment contact was our internal task choice, not a user-confirmed topic; Main authorizes an explicit R1-specific target-object revision. Keep R1's overall user milestone, reasonably reachable arm/hand/contact ability, reference imitation plus variation plus difficult labeled comparison plus reference-free new task, independent gates, and user feedback gate. `image.jpg` remains the overall project imitation target. Do not call the old collar target passed or silently preserve it as a product requirement.

## Previous BLOCK retained as history

The earlier WP02 freeze documented that `image.jpg` crop `(500,320,900,800)` did not expose the then-required collar contact and blocked WP03. That was an accurate statement about the image, not evidence against image.jpg overall. The earlier two bundled-image search (hero and character board) rejected both because they did not show a hand-on-garment pose. This blockage is resolved only by Main's authorization to change our internal contact object, not by a newly discovered collar observation. Old artifacts/heldout are not modified to imply otherwise.

## Revised reference and source/task match

Use `image.jpg` at source/crop hashes in public task-freeze for whole-project composition/clothing only. Its crop is not a hand-contact observation.

The selected teacher for only the hand/arm/object action is vendor scene `09_postimp`, from local vendor commit `f178bd7754a71d6d399473af1501634548efa6cb`. Actual code evidence: `scenes/09_postimp.js` passes the timed cup lift into `RIG.girl`; `lib/paint.js` sets the cup trajectory from table to mouth (raised value at 0.9 sec); `lib/rig.js` maps this to the `R.ik2` shoulder/elbow/hand chain, draws hand and cup, and defines component geometry; its rendered `1.20s` still visibly shows a bent connected arm and hand touching/gripping a cup near the mouth. Config, exact code links, native frame/crop bounds, hashes, caveat and license boundary are in `work/task-freeze.md`.

Reference artifacts (created with existing project `.venv` Playwright and vendor renderer; no dependency install, no vendor modification):
- frame `.scratch/35-r1-articulated-study/work/vendor-reference-09/t001.20.png`, SHA-256 `e60fc92efca3e88d34a089913a341d0addbfc66e68e2cc5b7adc17c9880d3757`;
- observed crop `.scratch/35-r1-articulated-study/work/vendor-reference-09/pose-crop.png`, bounds `(1060,230,1480,650)` in source-frame pixels, SHA-256 `69b3bf2146ca18c0f2b50ec10b9592ec91c3c6b907c39f2d1cf1c01570149ba5`.

Only one concrete vendor code scene was examined for this authorized revision; no further source search is planned. Its authored scene is an independent Canvas code render, but the vendor rig documents coordinates read from a generated setup plate. The render has no generated-image/sprite input at render time; this upstream coordinate provenance is disclosed and no absolute points are transferred. Vendor README says code/docs MIT but restricts its Huashu character frames/art to skill demonstration. Crop/frame may be used only as an internal gesture/contact teacher, with no character/art reuse or outward redistribution. Independent reviewer/integrator must affirm this bounded reference use is acceptable. If not, identify exact permission/source needed and block; do not claim legal certainty or sneak the render into final artwork.

## Frozen case interface and preserved acceptance

- Keep existing public IDs `imitated-target`, `changed-target`, `near-contact-control`, and sealed `heldout-new-action`.
- Fixed `r1-fixed-three-quarter` 3/4 bust camera, same scale/background/camera across three panels.
- Baseline: original clothed torso/shoulder design grounded overall in `image.jpg`; attached bent arm, articulated hand visibly gripping cup near mouth. Vendor reference is limited to action relation; no vendor character/style/composition or reference pixels in engine.
- Variation: same components/contact and camera, semantic target moves from raised-to-mouth cup grip to reachable chest-rest cup grip; shoulder width grows by exactly 8%. Both regenerate from semantic relations.
- Labeled control: baseline except grip-target ends `0.18 × (upper-arm length + forearm length)` short along approach vector, with visible gap, labeled `CONTROL — near miss`; source and render retained. Difficult diagnostic is not accepted art.
- Keep support bindings, depth-derived visibility and explicit non-intersection constraints; only named hand↔cup grip contact is intended touching. No hand-coordinate patches, pixel tuning, manual visible cuts, or 2D painter-order truth.
- Holdout prompt has not been opened. The holdout task owner must later verify the sealed task is materially distinct from this cup-grip baseline after its existing reveal gate; the construction worker must not inspect prompt/answer early.
- WP01 method card remains provisionally integrated solely on its independent source-review PASS at `.pi` artifact `/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/6718445a-9edb-4f98-aeda-8454afdb3161/r1/wp01-source-review.md`. This is method-source PASS only, not local migration or art success. Its collar-specific target example is superseded by this authorized task interface, while the transferable IK/taper/render separation is retained.

## Integrity, checks and outcome

- Contract `.scratch/35-r1-articulated-study/spec.md`, revised SHA-256 `658320a6c4828d5b0011cf7db8b70e4d9cd9ec7d9dfbc820a7f2bf9f3de4eba0`.
- WP01 card `.scratch/35-r1-articulated-study/evidence/method-study.md`, SHA-256 `f22ff7cd59120e783843bfb8ccdef66e499e7b98bf1272a084375ece4b6d0635`.
- Public WP02 task-freeze `.scratch/35-r1-articulated-study/work/task-freeze.md`, SHA-256 `4f74cf14a718be49f3300be094500b66d1d5da7cfc835c74d08b88094252c899`.
- Sealed file `.scratch/35-r1-articulated-study/work/holdout-brief.sealed.md` remains unopened, unmodified and not rehashed. Public previously recorded digest remains `86cc5b9f27c88211c62727abcfe7dc2683b7904dafc0602a5c871031c088f5a5`; exact prompt remains private.
- Commands used: source/scene inspection; `./.venv/bin/python vendor/huashu-art-motion/scripts/engine/render.py --solo 09_postimp --stills 1.2 --no-counter --out .scratch/35-r1-articulated-study/work/vendor-reference-09/`; `.venv` Pillow crop of source-frame pixels `(1060,230,1480,650)`; `sha256sum` on generated frame and crop. Render command completed with a Canvas readback performance warning only; image was produced. No tests are relevant or run.
- Pending independent reviewer: inspect only public task/source evidence and image crop to confirm visible relation, one-to-one code/source provenance, bounded license use, semantic case match and no heldout leak. Reviewer must not read sealed prompt.

**Outcome:** WP02 task-freeze is ready for independent source/task-match and rights-boundary review, but not WP03 start. Integrator must explicitly approve after that independent review. No user-feedback, art-quality, local migration, holdout, or downstream acceptance is claimed. No staging/commit performed; existing staged/dirty state preserved.
