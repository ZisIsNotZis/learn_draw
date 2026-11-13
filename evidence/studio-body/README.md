# Native editable upper body

A body is now one native semantic garment with collar, torso and two computed sleeves. It provides
small relaxed/offering/folded defaults, optional semantic controls, neck/joint mounts, and visible
elbow/wrist moves through normal inspect/preview/accept/undo. Elbow moves protect shoulder/wrist;
wrist moves preserve shoulder and bend ratios. This is a graphic garment, not anatomy/cloth simulation.

Try python examples/studio/upper_body.py --pose offering --outdir FRESH, folded for a second flower
pose, or --scene greeting for the independent new-intent composition after root finishing. The
helper works from an empty cwd by absolute path and refuses an existing output. Scenes remain
editable native JSON, not the older process-local adapter in evidence/studio-arm.

## Actual operation and art

usability/ is a frozen independent skill/help-only run on engine8970df: 34 terminal CLI operations,
all exit0, no full report read. It corrected elbow and wrist with exact scene/PNG undo/reaccept,
then composed a greeting figure from blank using staged body, neck stroke, head and open hand.
420 digests bind its files. Frozen guides are in usability-inputs/. Every acceptance followed returned
images in a separate call. An orchestration error launched dependent commands while a prior accept
was still live; old-revision proposals were preserved, all handles polled, then current inspection
and insertion repeated. No stale proposal was accepted. The current skill/workflow makes terminal
waiting explicit. This is an operator failure/recovery, not an engine error.

The first greeting lacked a hanging hand. Root finishing in06 adds one through observed pending
placement and acceptance on engine4f02. examples/studio/greeting.json preserves that authored scene.
Current engine2151 replays it in current-verified/greeting/. Fresh image pairs/followups recognize
the gesture and both hands/joins, while retaining tubular elbows, long fingers, planar clothing,
narrow eyes, hard hair edges and ambiguous graphic grip anatomy. Flower poses also crowd the neck
when folded and leave excess space at right. reviews.json binds each critique to actual image bytes;
old critiques are not silently applied to changed PNGs. No whole-artwork gate/human acceptance,
portrait-baseline promotion or broad drawing mastery is claimed.

## Depth and coverage findings

Internal left sleeve/torso/right sleeve support offsets are -1/0/+1. The 04-occlusion/ fixture shows a red pole
between chest and forearm, then a genuinely sloping pole passing in front. The initial sloped output
exposed pale per-surface mask seams. seam-study/ retains a CPU experiment: one shared fill from the
exact computed winner regions removes these internal raster cracks without moving their visibility
boundaries. The 05-current-occlusion/ fixture adopts it.

A separate interior-paper regression then found an armpit region added by shared-cloth rounding
but outside every local surface. Local material now uses the same morphological closing radius
as the sewn cloth. Dilation distributes over union, so the local surface coverage includes the
whole shared cloth; depth ownership remains computed. The 07-covered-occlusion/ fixture retains the corrected
fixtures. A fresh targeted critic finds neither earlier internal spike nor pale depth seam.
This coverage repair is distinct from the exact-boundary underpaint. Geometry/visibility outlines
are simplified at .0003 torso height for CPU efficiency, while paint paths stay dense.

## Verification and limitations

Current native engine:21518446e9ddb18ca7fe0a90a543428a76f6a6e9a7ba372cacb61fcd59832536.
128 studio tests pass in tests-final/; ten old/default PNGs stay exact in preservation-final/.
The six new body tests cover rotated local locking, attached hand/recovery, staged public editing,
no visual input in a fresh cwd, invalid geometry and true internal/external depth crossings.
Interior paper detection specifically guards the observed seam failure; it is not a drawing target.
Earlier tests/preservation directories retain their actual source/coverage boundaries.

verify_delivery.py --outdir FRESH verifies frozen digests/recovery plus current public helper runs
from an empty cwd. current-verified/ reconstructs engine8970df and intermediate4f02 from two source
snapshots, proving only body coverage/rendering changed after independent operation. The operation
backend is unchanged, but old operations are not relabelled as execution of current source.

The first verifier run in current/ failed because it demanded exact pins for every legacy component.
Current verification still asserts exact native body/hand/neck pins, and separately reports an
UNRESOLVED .2936px head-chin deviation in the greeting. The legacy head recompiles rounded absolute
SVG coordinates (scene_render.smooth_path emits integers); translation is not invariant. Do not
hide this with a broad tolerance or claim every component has exact pins. This needs a local-frame
or equivalent principled correction. Child orientation also remains explicit after wrist edits;
width, neck seating and cuff fit still require decisions. These are concrete next product gaps.

No GPU inference/training, image-model final assets, target image access or metric optimization was
used. The overall VLM-creation goal remains active. This unit delivers a useful body editing slice
and actual new-intent evidence, not the whole goal.
