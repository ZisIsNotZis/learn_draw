# Visible named mounts and preserved drawing relations

## Result and motivation

A named, inspected point can now be pinned to another object's current geometry. Shape mounts are
painted arc midpoints plus center; other macros currently expose center, with root/tip also on locks.
Relations stay in authored data. A compiler copy resolves the acyclic graph for rendering, selection,
crops, depth and reports. Parent changes recompute descendants; a child retains its own screen angle
and size. This is a projected point pin, not a full 3D joint or inherited transform.

The independent creator made a four-shape cactus using only the skill/public CLI, viewed both
named-mount images before each decision, rejected an incorrect arm tilt and an awkward oval tip,
and moved only the pot to improve centering. Public report bounds show all four pieces followed
exactly -25.6px in x and 0 in y through three links. [Its raw report](usability/REVIEW.md) and logs
preserve the decisions and limits. Fresh [image review A](usability/image-review-a.md) and
[B](usability/image-review-b.md) retain awkward arm contours and inconsistent part shapes. This is
bounded creator usability and connection evidence, not human acceptance or whole-artwork success.

## Joint diagnosis before implementation

prior-joint-facts.json measures the old lamp elbow, rocket cap and cliff footing. The elbow already
has 42.73 square pixels of projected paint overlap; the cap also overlaps; the footing lies entirely
inside the rock-top patch. Those critiques do not establish detached geometry. Named mounts address
repeated placement and subsequent drift; they do not add material, volume, smooth joins or edge fits.
verification/cactus-joints.json likewise checks actual mounted paint overlap, not imagined gaps.
These measurements diagnose construction, not an art score or tuning objective.

## Actual studies

- probe/: initial vertical support and base, before legible callouts; historical exploratory output.
- probe-labels/: the same placement with separated labels/callouts on a thin part and blue target.
  Current label placement was actually viewed before independent use. Early views are not current
  replay source bindings; current proof is verification/ and the source snapshot below.
- pinwheel/: original six-mass mount graph. Only the handle has a free canvas placement; the hub
  and four blade roots use named relations. A handle-length change moves every descendant center
  exactly 32px upward with all five raw descendant nodes unchanged. Actual preview/accept/undo/replay
  are recorded. Both fresh critics say the triangular paddles lack folds/directional bend and read
  like petals. Keep it as a mechanics study, not finished folded-paper artwork.
- usability/: independent cactus, all actual input/output, refused and declined proposals, CLI-only
  wrapper and command log. Original artwork/source are preserved.
- inset-study/: separately rendered .65 embedding proposal after the interface correction; never
  accepted, with no art improvement claim or silent replacement of the creator's result.
- verification/: current-source repeats and preservation of prior defaults/artwork plus graph facts.
- source-before-inset-fix/: complete Studio source used by the creator (engine fcf26133…). External
  modules are unchanged from git ed01d24. Restore into scripts/studio in a disposable checkout to
  reproduce it; the archive itself is not a standalone package.

examples/studio/cactus.json is the unchanged independent scene. pinwheel.json is the raw mount study.
examples/studio/mount_demo.py --outdir FRESH rebuilds that study and its meaningful parent edit.
It deliberately refuses an existing output directory. The frozen records are not scratch output.

## Operation, safety and verification

The operation is inspect anchors on both objects, preview --attach TARGET_SELECTION with named
self/target mounts and optional inset, then inspect and accept/discard. Inset moves inward along
the target's actual normal; offset nudges stay in screen units. Both source and target revisions
must match. The blue target, green labeled mounts, orange current source and pink prior boundary
make the intended placement visible. Depth is still computed independently; no visible cuts are authored.

Detach preserves the current rendered placement. Normal object moves retain an attachment offset.
A local contour interval that changes a pinned midpoint or its tangent is refused. Cycles, missing
or unavailable mounts, illegal types and output/input aliases refuse the proposal. Node-level
geometry requires resolved nodes to prevent silently using nominal positions for attached parts.

94 combined tests pass, including nine mount checks spanning rotated/nonsquare geometry, dependent
chains, parent resize/rotation/sculpt, unrelated parts, exact visual detach, history undo, stale
and cyclic refusal, contextual hand-tip/head-lock/lock editing and CLI input preservation. Current
head/hand/mass defaults, the old independent lamp, clean rocket, raw cactus and pinwheel repeat the
same SVG/CPU PNG. Prior and actor PNG hashes remain unchanged; verification/validation.json records
exact source/scene/image bindings. These checks prove operations, not aesthetics.

## The real range failure and correction

The creator asked for inset .65 and was refused by the initial -.5.. .5 bound, omitted from help/skill.
That half-width limit was an unnecessary interface choice: inset uses the target's shorter nominal
extent, not half the surface's full axis or a probability. A pre-fix regression fails on that valid
embedding. Current range is -2..2, documented in help and skill; .65 renders as a separate whole
proposal. No numerical range change repairs a contour automatically. The raw .5 creator outcome
is intentionally unchanged. Bounds should express a discoverable interface/math/resource limit,
not substitute for looking at a valid but possibly unattractive pose.

## What the pictures say next

The pinwheel's petal reading and cactus's blunt/mismatched branch joints are not solved by point
connectivity. Before multiplying high-level subject templates, compare existing shape controls
with a reusable rounded/curved gesture mark and a controlled simple colour-plane treatment. Keep
both the failure and the discriminating visual comparison. Use the resulting tools in a small
connected character illustration with the accepted head/hand presets; generic icon studies alone
must not become the final scope of the VLM drawing product.
