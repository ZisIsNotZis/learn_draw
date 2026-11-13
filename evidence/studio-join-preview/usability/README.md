# Independent public-tool usability operator

This is a bounded operator study, not whole-artwork acceptance. Frozen engine: `5d491f0d1630c7b1b84a2a657661e4450d548982b153759bbb6cba206e85a006`; renderer feedback: `resvg-py-0.5.0-cpu`.

Only supplied inputs/SKILL.md, seed.json, public CLI help, focused CLI output and generated images were consulted. No engine source, tests, project docs, other studies, target, raster generation or GPU use. The seed was copied to working.json; scene JSON was never hand-edited. All writes stayed inside this directory. No commit or push was made. All launched processes reached terminal results; none remains live. Some help/accept/inspect launches returned live session handles and required several polls even after stdout appeared. Each dependent CLI launch was a separate orchestration invocation; visual calls completed before later acceptance calls.

## Outcome and observations

The initial image already had a mid-height open-palm greeting. The `wave` semantic pose raised it above the head and removed the seed's older arm overrides, while attached neck/head/hands stayed connected. The arm is still an angular graphic garment, with a nearly horizontal upper sleeve; this study does not establish anatomical polish. The wrist selection clearly highlighted the intended high cuff and exposed right_cuff_width. Setting .9 modestly narrowed its rim toward the skin wrist while leaving the palm and arm joints fixed. This was a useful local correction, rather than a claim that the entire sleeve is finished.

I chose a small gold oval wrist charm rather than a balloon: a single painted oval has no string or knot and should not be described as a balloon. Place showed it alone in the upper-left with named mounts. Join --pending moved its right edge to resting-hand.wrist without inserting a duplicate or changing working.json before acceptance. The actual result reads as a gold disk accessory beside the hanging cuff, with fingertips and high wave still visible. Its simple tangent contact lacks a strap/fastener, so physical attachment and detailed prop identity remain limited.

Join's before and after images alone made the roles clear: orange source gold-charm.right, blue target resting-hand.wrist, labels inside each camera, and both original endpoints visible in before-closeup. After-closeup showed the coincident pin and different arrows. Terminal output explicitly reported requested auto -> point; the charm retained its upright angle. This is an understandable point connection, not directional fitting or matching silhouettes. No second target inspection was needed. The mount names were known from the supplied seed and place feedback; the tool did not infer the desired accessory semantics.

## Actual command and terminal record

[commands.txt](commands.txt) records all 17 public CLI invocations in order with their real arguments. Matching NN-*.log files retain merged raw stdout/stderr as captured by PowerShell. Steps 01-16 succeeded (help, ready previews/inspections, or returned acceptance/undo revision). Step 17 deliberately returned CLI exit 2, recorded in [17-exit.txt](17-exit.txt), with `studio: stale placement; preview against the current scene and implementation`; the final working scene remained byte-identical to accepted-prop.json. PowerShell formatted native stderr as a NativeCommandError in that raw log; this wrapper formatting does not change the captured underlying CLI refusal.

The operator did not need a rejected visual proposal or an engine repair. The extra CLI help command made pending/source/target syntax unambiguous. Friction is the number of separate file paths and the need to track candidate versus selection revisions. The ready JSON is lengthy but the image handles, current controls and point mode are discoverable. There is no inferred fastening or automatic aesthetic guarantee.

## Images actually viewed before each decision

- 02-old: artwork, alignment. Identified the starting mid-height gesture.
- 03-wave: artwork, alignment, edit-closeup. Read the raised palm and revised elbow before step 04 accept.
- 05-cuff: artwork, alignment, edit-closeup. Confirmed orange wrist focus and wide cuff rim.
- 06-taper: artwork, alignment, edit-closeup. Confirmed modest rim taper before step 07 accept.
- 09-charm: artwork, alignment. Read the pending oval and its labeled right mount.
- 10-joined: before-alignment, before-closeup, artwork, alignment, edit-closeup. Read both original mounts and proposed fit before step 11 accept.
- 12-accepted artwork and 14-undone artwork. Observed insertion and recovery before step 15 reaccept.
- 16-reaccepted artwork, then original-detail reopen of 16 and 12. See contradictory display record below.

[Before connection](10-joined/before-alignment.png) / [before closeup](10-joined/before-closeup.png) / [proposed connection](10-joined/alignment.png) / [joint closeup](10-joined/edit-closeup.png) / [final clean picture](16-reaccepted/artwork.png).

## Recovery evidence and display discrepancy

[recovery.json](recovery.json) and [18-recovery.log](18-recovery.log) record actual byte comparisons (not only hashes): undo restored 2515 scene bytes and 38220 PNG bytes exactly; reaccept restored 2974 scene bytes and 39118 PNG bytes exactly. The accepted PNG also exactly matches the observed join proposal. Undo returned revision `4f693ccdf0250b972354d2f0649cb6d71e365b54930712bc3cc8242e7518624e`; reaccept returned `69903c67596f50277cbd402e112df95230a66ca7a970027a64de2499b5fd0c34`.

A late view of 16-reaccepted/artwork.png appeared as a tiny blank beige tile. Reopening that same original-detail file showed the full character and charm. In that same later call, 12-accepted/artwork.png appeared as a tiny beige tile despite previously displaying fully and being byte-identical to 16. Both have SHA256 `bcb6f5896b95037057a3186b727cff0ff4416781dc469ca12cfba64a15f830c5`. This conflicting display is retained as observation; it did not justify an art or engine change. No claim is made about the cause of the viewing discrepancy.

Root owns fresh-context artwork review, draw-check and whole-drawing gates. CLI acceptance here means only the observed operator edits were landed; it does not award the whole-artwork gate or human acceptance.
