# Original night-window study and pending two-contact strokes

Current engine:9a610ba4951fd3dca30c01c4a05a23bb36d52e1d2b96555cafeb64b2090ab305.
**The cat artwork remains unresolved. It is not an adopted cat preset or a finished-art pass.**

The intended image is a quiet night reading nook with a sleeping cat, open book, lamp and crescent.
It uses authored semantic masses/strokes/moon and computed relations, with no visual input. Current
source is examples/studio/window_cat.json; python examples/studio/window_cat.py --outdir FRESH opens
that editable study. --initial-sketch explicitly rebuilds the earlier supported recipe. The default
does not silently return the old sketch. Overall creation capability remains an active goal.

## What actually worked

The book exposed a real insertion gap: working strokes could bind two ends, while pending strokes
could not. place --revise now accepts --feature root|tip --bind-end TARGET/selection.json. A new
stroke is observed first, then each end is fitted to an independently observed working mount. Both
constraints, bend/thickness/colour and cap refinements remain pending until one later acceptance.
Actual source/target labels fit the operation camera. The second pin derives chord length/angle.
Existing nodes, readiness, revision/source binding, stale refusal and exact undo remain protected.

usability/ is a fresh skill/help/feedback-only operator:16 real public CLI calls, separately observed
pending/root/both-contact proposals, a rejected sagging bow, a revised cover, acceptance/undo/reaccept
and stale-target/candidate refusals. The operator touched no source or parent scene. Original23
nodes are unchanged. Its records retain matching recovery hashes; the delivery verifier additionally
compares four actual JSON/PNG byte pairs. Merged PowerShell logs and the UTF-16-BOM recovery proof
are preserved raw. The verifier decodes that BOM instead of rewriting the evidence; its first UTF-8
assumption failed before this correction. Frozen skill inputs predate a later generic-shape wording
correction; current skill correctly describes projected attachment.

Root then revised that exact pending proposal. Thin flat caps removed endpoint lobes, but the cover
became buried: its first mounts were on page sides above the underside.25–28 observe and rebind
actual bottom-edge points, making the supporting cover visible. This is a drawing correction, not
proof that coincident pins automatically produce correct art. The two actual contacts have zero
measured point error.30 seats the sill's front lip beneath the board rather than leaving a paper
seam.50 pushes the inspected rear underside while preserving support/head/tail mounts.

## What did not work, and why the next action changes

Eight fresh image-only reviews at four exact-image checkpoints recognize the room and resting cat.
They consistently retain ambiguous cat anatomy: an oval torso, unclear foreleg/haunch structure and
a tail read as a band or sling. Proportion changes, head inset, shorter ears, altered tail root/curl,
rear occlusion, a small forepaw, shared coat material and a local underside push do not establish
the missing limb/weight construction. reviews.json records parent-captured summaries and PNG digests.
No reviewer or human finished-art approval is inferred from recognition or from passing checks.

The earliest authoring mistake was treating an ellipse assembly plus registration as a sufficient
sleeping-cat structure, then decorating the scene before proving that component. This skipped the
structure-before-line/colour principle. The workbench's pins and previews did their mechanical job;
the author did not supply a coherent thorax/haunch/tucked-foreleg/support model. Stop this cosmetic
loop. Next isolate those volumes and a leg/paw chain in a structural plate, establish contact and
overlap, then design deliberate art lines before returning to the room. Do not productize a weak cat
macro merely to hide its complexity. The24-node limit also constrained detail; that does not justify
omitting structure or automatically expanding the engine before the component works.

## Provenance and verification

01-sketch was deliberately canceled before artwork existed after ambiguous coplanar ordering
triggered expensive visibility work. The actual owned processes were stopped and the original exec
handle drained to terminal1; provenance.json retains the scope. It is not a completed renderer run.
02 uses explicit paint planes;03 repairs an undersized support using rotated thin masses. These
initial authoring-recipe iterations are not relabeled as public-CLI local editing. Root04–54 then
retain actual CLI PID/start/terminal/exit and separate streams; observed images preceded separate
acceptance calls.04–20 bind old engine5d491;21 onward bind9a610. Actual prior placement.py/__main__.py
snapshots reconstruct the older engine. Rendering geometry did not change at that API boundary.

148 studio tests pass in tests-release/; ten prior/default PNGs remain byte-exact in preservation-release/.
Four new tests cover pending two-end geometry, derived controls, existing-node preservation,
acceptance/undo, stale/invalid refusal, aliases and failed-render safety. Existing successful checks
are reused for unchanged code. Current commands (choose fresh outputs outside this frozen tree):

```
python evidence/studio-window-cat/run_tests.py --outdir FRESH
python evidence/studio-window-cat/verify_preservation.py --outdir FRESH
python evidence/studio-window-cat/verify_delivery.py --outdir FRESH
```

The delivery verifier checks inventory/digests, current/old source epochs, actual contacts and
protected mounts, four recovery byte comparisons, older-candidate refusal, fresh-cwd public replay
and a visual-input audit. Fresh replay preserves PNG bytes; the audited SVG text is identical after
normal newline decoding. These are capability/artifact checks, not an anatomical or aesthetic gate.
No GPU, target access, generated raster, pixel-target optimization or portrait-baseline promotion.

P36 independent execution review reran the delivery verifier (exit0) and the four new endpoint
tests (2.401s, exit0). It independently checked the then-frozen892-file inventory/hashes before and
after both runs with no missing/extra/mismatched files. The unchanged source's successful148-test
suite and ten PNG checks were reused. independent-execution/ preserves its raw process streams,
actual PID/start/terminal/exit and before/after inventories. That check preceded these copies and
this append; root rechecks the final manifest after including them. It awards no art verdict.
