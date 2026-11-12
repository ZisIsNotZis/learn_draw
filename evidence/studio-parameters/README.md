# One visible decision for related semantic controls

## Why this change

The previous independent lamp creation needed many inspect/preview/accept cycles merely to assign
one part's size, aspect, taper and colour. Those intermediate parameter states were not separately
useful drawing decisions. The intended workflow is to inspect a part, propose a coherent change,
look at its complete result, then accept or discard it.

Repeated --change NAME=VALUE now makes one candidate on the inspected feature. The same typed
controls, stale guards and full-state geometry validation apply. The working scene is untouched
until acceptance; one accept adds one journal item and one undo restores the whole prior scene.
Duplicate names, malformed changes, unexposed controls and invalid values refuse the whole proposal.
A failed new request also invalidates any older candidate in the reused proposal directory.
Single --set/--value and --move retain their behavior and old journal format.

## Controlled evidence

showcase-before/ and showcase-proposal/ contain a real CPU-rendered block-to-shade grouped preview,
including the previous/current boundary overlay. Its six values are recorded in candidate.json.

lamp-replay/ repeats the previous independent operator's actual construction plan through the public
CLI, grouping only the parameter settings of each part and retaining separate moves. The final scene
is exactly equal, and the final PNG is byte-identical to the original independent lamp/book result.
Accepted edits fall from 63 to 28; there are 22 grouped/move previews plus six insertions. The replay
used SVG-only intermediate outputs and a final CPU PNG. This is equivalence and operation-count
evidence, not a timing benchmark, new art judgement or independent creative transfer.
comparison.json and commands.json bind that claim to the actual operations and image SHA256.

replay_lamp.py accepts a fresh destination directory as its first argument. Its default names the
frozen historical package and will refuse to overwrite an existing working scene. Preserve records;
use a new directory for re-execution. The original subject/source remains in ../studio-shape/usability/.

## Independent new-subject evidence

usability/ contains the independent creator's six-part toy-rocket emblem, built from the current
skill and public CLI with no source/scene/SVG workaround, reference or image generation. It actually
viewed every complete grouped preview before acceptance, undid the body group in one step to the
byte-identical displayed default, replayed it and rejected an ill-seated nose placement before
correcting it. The raw scene/artwork and all decisions remain unchanged. image-review-a/b are a
fresh-context critique pair: the subject reads clearly; cap/body ledges, style consistency and
faint fin flecks remain observations. This is bounded creator usability, not human acceptance or
a whole-illustration claim. Grouping assignments is not permission to skip looking.

## Verification and limits

85 combined operation/checker/visibility tests pass, including four new group checks and two
noncrossing/crossing raster regressions: equivalence
with serial settings, one-step accept/undo, input preservation/feature scope, CLI readiness and old
candidate invalidation on duplicate/malformed/invalid requests. Existing default shapes and drawings
are unaffected by the parameter-assignment refactor. Exact current rebuilt image bindings are recorded in
verification/, including the unchanged independent lamp after the rendering correction. Tests establish edit behavior, not artwork quality.

The group still belongs to one selected feature. Object placement remains a separate visible move;
this is not a bulk scene script, attachment graph or automatic drawing policy. Reusing existing art
cannot establish better visual judgement. Next design choices follow the independent new work and
its actual interface/visual gaps, not operation-count reduction alone.

## Image critique found a real rendering defect

Both initial image reviewers saw pale marks inside the right fin. This was verified against actual
pixels rather than dismissed as the earlier external-viewing anomaly. fin-diagnosis/facts.json
finds 24 non-red pixels inside the visible red region eroded by two pixels. The two fins are on the
same support plane but their projected footprints are disjoint. The previous global-order proof
rejected overlapping depth intervals, unnecessarily producing compound triangular clipping masks.
All 24 diagnosed flecks disappear in a separately proved noncrossing painter-order reference.

The renderer now checks every pair of overlapping depth intervals and permits that order only
when their painted projections are disjoint. It retains the exact depth solver for unresolved
crossings. The new raster regression fails before the correction and passes after it; another
case checks a true crossing across a nonadjacent interval, guarding against an overly weak adjacent
pair check. No object position, geometry, palette or depth changed. This is a general proof-boundary
correction, not a depth workaround or a pixel-specific patch.

rocket-clean/ repeats the exact original scene under the corrected implementation, matches the
proved reference in every pixel and repeats identical PNG bytes. The 1,912 changed pixels include
boundary antialias coverage, not just the 24 deep-interior flecks. source-before-noncrossing-fix/
preserves every Studio source file from independent engine d8fd65d5…; the external modules are
unchanged from git 4f101ac. Restore that snapshot into scripts/studio in a disposable checkout to
reproduce the actor implementation; the archive itself is not a standalone package.

clean-review-a/b are a second fresh-context pair given only old/new image bundles. Both see the
local marks removed, unchanged recognition/layout and no new visible defect. The body contour and
abrupt nose/border joins remain minor stylistic limitations. The raw actor image is not silently
replaced. The correction does not prove that genuinely intersecting compound masks are always
seam-free; that is a separate boundary if future artwork exposes it.

![The same independent rocket scene after the renderer correction](rocket-clean/artwork.png)
