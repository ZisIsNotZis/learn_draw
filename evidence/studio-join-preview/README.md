# Paired connection previews and independent cuff refinement

Current source engine:5d491f0d1630c7b1b84a2a657661e4450d548982b153759bbb6cba206e85a006.

`join work.json --source palm.wrist --target shirt.right-wrist --reason "Seat the palm"
--outdir FIT` replaces separate endpoint inspection calls with one inspect-and-propose operation.
Both before ports are labeled in orange/blue; the after artwork and closeup show the actual fit.
It never changes working paint until a later accept. Optional --pending preserves the uncommitted
component and every working node. Auto chooses supported opposed-direction joints or a point pin;
it does not infer fastening, depth, width fit or anatomy. Six PNGs replace three four-view calls.
This is fewer calls, not a measured latency claim. Exact scalar/port contracts live in docs7.

The pending-source smoke revealed that placement's all-mount selection lacked the exact source
port needed by paired arrows/crops. join now selects that named mount while retaining working base
and insertion metadata. Tests cover the real pending CLI render, revisable insertion, unchanged
working bytes, six cameras, label locations and exact undo. Before/after source geometry is bound
to the exact working/pending before_revision. Stale proposals, invalid ports, cycles, render failures
and input aliases refuse. Ordinary endpoint-pin and attachment conflict checks remain in force.

## Actual greeting corrections

The garment now offers a high-wave gesture and optional per-wrist cuff_width. Cuff taper leaves
the skeleton and upper sleeve alone; hand size stays authored. Pose application clears gesture
overrides on both arms but retains cuffs/style/links. Raw scene overrides still apply after defaults.
The raised reach was already expressible by the CPU generator; the old numeric contract had
unnecessarily prevented it. It is not a general reach/IK solver.

Root records04–15 show a high wave, independent right/left cuff taper and a local elbow refinement.
Actual images returned before each separate acceptance. The cuff closeup exposed coloured corner
spikes outside rounded cloth; clipping the colour field to sewn cloth fixes that paint defect.
04–06 predate this clipping-only source change; their engine571dd97 remains historical.01–02 bind
an earlier pre-exact-pending-port source. They are superseded observations, not current replay claims.
03-current-body is a direct successful CLI inspection without a separate PID wrapper. Other numbered
root launch records retain actual PID/start/terminal/exit and raw streams. Do not infer extra process
evidence from a directory alone.

Two image-only critics independently identified the nearly horizontal upper sleeve as the chief
defect. Exact joint coordinates confirmed it.14-elbow-rise changes only local bend from -.5 to -.3:
shoulder/wrist centers stay fixed and the directional hand follows the new forearm. Two new critics
recognize the greeting and retain flat garment/detail imbalance, a pinched shoulder and heavy eyes.
reviews.json contains parent-captured summaries and actual image digests, not human approval or a
finished-art pass. working.json,14-elbow-rise and public-greeting bind the revised editable study.
The public example is examples/studio/greeting.json; the original portrait baseline is unpromoted.

## Independent public operation

usability/ records17 public CLI calls using only frozen skill/seed, help and actual tool feedback.
The operator applies a high wave, tapers a cuff, places a gold oval and joins its right mount to the
hanging wrist without separate target inspection. It observes actual before/after cameras before
accepting. Five actual byte comparisons prove exact undo/reaccept scene/PNG recovery, including
accepted paint matching the proposed PNG. A stale pending insertion refuses with CLI exit2.
No engine repair or source access was needed. Source/target roles were clear, while candidate versus
selection paths still impose bookkeeping. The oval is a tangent-pinned accessory without a strap;
this demonstrates projected placement, not believable fastening or creative transfer.

The operator records a late image-display discrepancy: a returned view appeared as a tiny beige
tile, reopening the same original showed the figure, and the two accepted PNGs remained byte-equal.
This does not invalidate the recorded earlier separate preview observations, but visual display
and byte recovery are different claims. The original note is retained; no invented art correction
or claim of uninterrupted successful display is made. PowerShell formatted the negative-control
stderr as a native error record; its CLI exit2 is preserved separately. Operator logs are merged
streams rather than root-style PID records. See usability/README.md for precise provenance.

## Verification and scope

144 studio-family tests pass in tests-release/; preservation-release/ reproduces ten prior/default
PNGs exactly. Six new tests exercise paired-join safety, pending images/recovery, local cuff geometry
and meaningful pose switching. This does not certify untouched anatomical/style/creative-transfer
questions. Current source and this evidence are checked by:

```
python evidence/studio-join-preview/run_tests.py --outdir FRESH
python evidence/studio-join-preview/verify_preservation.py --outdir FRESH
python evidence/studio-join-preview/verify_delivery.py --outdir FRESH
```

The verifier checks frozen inventory, source binding, tests, preserved PNGs, actual joined geometry,
protected centers, current public render bytes and refusal of a pre-clipping-engine candidate.
Prior source-bound verifiers remain historical and can correctly refuse the newer implementation.
No GPU work, target reading, generated raster assets or pixel-target optimization was used.
The overall intent-led creation goal remains active. The next capability checkpoint is an actual
small original narrative image and a useful local correction, using these tools before adding more.

P36 independent execution review reran the public delivery verifier and the complete144-test suite
(45.463s, exit0), then independently checked the then-frozen387-file inventory/digests with no
missing/extra/mismatched files. independent-execution/ copies its raw test streams, child exit record
and delivery result byte-for-byte from its fresh external outputs. That inspection preceded this
append and the copies; the final manifest includes them, and root rechecks the completed package.
These checks establish mechanical/artifact consistency, not picture acceptance.
