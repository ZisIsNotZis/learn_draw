# Pending placement: observe and revise before insertion

2026-11-13. Public `place` now stages one component outside the working scene. It renders
clean artwork, actual orange boundary and labeled mounts. `--revise` retains the pending shape
while changing exposed semantic controls, screen placement or a separately observed attachment.
Accept inserts the complete configured component as one recoverable edit. Discard changes nothing.
This is a usable authoring slice, not whole-project or whole-artwork acceptance.

## Actual visual work

| Record | Observed decision |
| --- | --- |
| 00-flag-observe | Existing banner mounts inspected before composing a badge. Input is the prior independently authored flag with parent pole finishing. |
| 01-badge-default | Native sun proposed on the banner. Its crown crowds the upper/lower edges. Working scene remains the five-node flag. |
| 02-badge-quiet | Revise the same pending sun: rays 0, length .095. More breathing room; retain its name and other controls. |
| 03-badge-seated | After observing its own mounts, attach the pending disc center to the inspected flag center. Same independent screen orientation; point fit only. |
| 04-accepted / 05-undone / 06-restored | Actual public accept, undo and reaccept. Undo recovers the original scene and PNG exactly; reaccept recovers the badge image exactly. |
| 07-extra-emblem | An extra crescent makes the disc appear accidentally bitten. Viewed and discarded, never accepted; disposition.json preserves the decision. |
| usability/ | Fresh operator chooses a retro camera from intent and authors all seven masses through public CLI from blank paper. Housing is revised before acceptance; an obstructive strap trial is discarded. |

![Independent original camera](usability/11-final/artwork.png)

The camera operator read only frozen inputs in usability-inputs/, CLI help and own outputs;
no source/tests/examples or direct scene/SVG authoring. Placement still uses semantic anchors,
two coarse offset fractions and screen moves; it is not coordinate-free. The operator found
no interface blocker and did not rebuild a primitive. It identified crowded mount labels on tiny
parts. This demonstrates one modest original flat composition, not universal subject transfer,
natural anatomy, body rigging or a full 3D contact solution. The shipped editable camera in
../../examples/studio/camera.json reproduces its exact PNG.

Two fresh image-only critics recognize both flag action and camera at full/thumbnail sizes.
They retain the hand's ambiguous thumb/pads and stiffness; the camera has clean rings/overlaps but
flat lens depth and generic top/flash rectangles. These parent-bound qualitative summaries in
reviews.json are separate from operational usability and do not constitute a formal portrait
rubric gate or human aesthetic approval. The earlier human approval covers the graphic hand
preset direction, not these whole artworks.

## Use the operation

From the repository root, in a fresh workspace:

```
python -m scripts.studio new work.json --kind blank
python -m scripts.studio place work.json --kind shape --id housing --reason "Establish the camera body" --outdir FIRST
```

Read FIRST/artwork.png and FIRST/alignment.png. Then correct the same pending shape:

```
python -m scripts.studio place work.json --revise FIRST/candidate.json --move down --amount .04 --change rounding=.65 --reason "Soften and lower the housing" --outdir SECOND
```

Read SECOND's images before `accept work.json SECOND/candidate.json`; `undo work.json`
restores the input. Discard by leaving a candidate unaccepted. Use distinct revision output/input
directories. Full command contract is ../../docs/7_INTERFACE.md and practice is in the drawing skill.
The older immediate add remains for legacy replays; current composition should use place.
operate.py and commands.jsonl preserve the actual parent sequence, not safe in-place replay commands
for this frozen directory. Use fresh locations when repeating work.

## Verification and known limits

110 studio tests pass, including seven pending-placement tests. Ten prior/default PNGs are exact.
The new tests cover actual CLI staging/revision/acceptance/undo, visible mount output, all native
presets, revision preservation, stale/foreign/failed refusal, output aliases/hard links and failed
render reuse invalidation. verification/delivery.json checks actual parent image/state recovery,
unchanged existing resolved geometry, paint differences confined to the badge, 155 operator artifact
hashes, operator blank recovery and the published camera's exact PNG. Tests do not judge art.

```
python evidence/studio-grasp-glyph/run_tests.py
python evidence/studio-placement/verify_preservation.py
python evidence/studio-placement/verify_delivery.py
python evidence/studio-placement/manifest.py
```

Source remained frozen at engine 6f3b918e9ee6dca625e031b8522eb0102e05f81354da8de902eee7d65a321ef4
through parent operations, tests and independent use. No GPU or generated image assets were used.
The earlier test runner is reused because it dynamically discovers package-named studio tests;
its old output/evidence is not overwritten. Root manifest includes nested operator-input manifests.

The operator's first bezel command encountered equal nested 120-second deadlines; no terminal
callback was observed before the retry. Missing output was incorrectly treated as enough to retry.
Its historical termination remains unverified. OPERATIONAL_AUDIT.txt and process-audit.json retain
the correction and current empty targeted process query; no process was killed. Subsequent commands
have recorded exit0 results. The review dispatch rule now explicitly carries process observation and
persist-before-launch requirements. This is an execution-method failure, not a reason to hide the
successful artifacts or call the interrupted attempt successful.

Guide limits remain: revising a pending component compares separate images, without a pink prior-
proposal contour; tiny labels overlap. A point pin does not fit edges or align a sleeve/nozzle tangent.
Replacing an existing assembly still involves separate removal and insertion transactions.
