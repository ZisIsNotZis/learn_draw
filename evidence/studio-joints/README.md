# Stable head placement and persistent directional joints

Current engine:0a18d3827b496b45d6ac3d166e69d226f392b8ecc9033289e9752374dffd6529.

A head now retains a semantic recipe frame and moves its actual SVG, footprint, chin mount,
selection geometry and local hair locks together. New heads have this frame automatically. Old
free heads capture it when edited; old attached heads first require observed reattachment, so
repairing their earlier fractional pin cannot silently move protected geometry. Detach and parent
removal preserve paint. The old .2936px greeting error is fixed by real rigid placement, not by
counter-offsets, relaxed tolerances or a reference image.

An optional --orient opposed on normal attachment or pending placement keeps point contact and
opposed outward directions. Head chin, hand/grip wrist, body neck and stroke terminals are supported.
Grip handle ends expose their real axes, so connected pole legs follow a turned hand. Angle is
derived and removed from controls; focused feedback exposes derived_angle. Release bakes pose.
Default point pins remain available. Width, depth, contact pressure and anatomy remain separate.

## Actual drawing loop

Root operations01–03 first bound the pre-final-feedback enginefb839.03-head-fit was superseded
before acceptance when target-input alias guards, feedback wording and report scope were corrected.
04–16 on58b302 observed and fitted chin/neck and both hand/cuff joints. Later source44a080 adds only
a legacy attached-head edit refusal to protect lock endpoints; the source snapshots reconstruct the earlier engine. Final source also sanitizes frame comments
for valid double-hyphen IDs; the default-picture geometry is unchanged.17–24 then fitted neck/body direction and leaned the whole greeting
through one body angle. Each accepted proposal had returned actual clean/closeup images in an earlier
tool call. Root run.py preserves actual CLI PID/start/terminal/exit and raw streams; all are terminal0.

working.json,24-final/ and examples/studio/greeting.json bind the completed editable pose study.
The public upper_body helper now uses persistent hand/stem relations by default. Its initial stem
width is computed from the owned handle; later resizing still needs a separate fitting decision.
Current helper replays in current-release/ run by absolute path from an empty cwd, with preserved process
records. All demonstrated point/direction constraints are verified from actual compiled mounts.

## Independent operation and honest limits

usability/ is a fresh skill/help-only operator on58b302:28 real CLI commands,259 frozen digests,
three persistent wrist/handle joins, a purposeful upward wrist revision and exact byte-for-byte
scene/PNG undo/reaccept. No source, tests or full report data were needed. actor-release/ renders
that frozen final scene on current0a18d and has identical clean PNG bytes. These are current-render
and historical-operation claims, not a relabelling of old operations as new-source execution.

The operator initially treated awaited launch-tool returns as completed processes. Live wrappers
were polled on their original handles, and observations repeated before further edits. It needed
explicit execution coaching: one launch per orchestration call, stop dependent work when a session
is returned, and poll to actual terminal before continuing. Do not call the whole run strictly serial
or uncoached. Frozen inputs predate this clarification; usability-execution-coaching.txt and the
actor report retain the boundary. Canonical skill now gives the concrete pattern. Old misleading
wording about directionless handle ends was corrected after actual feedback; frozen guides retain it.

Fresh image-only critics on check-greeting/ and check-flower/ recognize the gestures but retain long
soft fingers, ambiguous graphic grasp, tube-like elbows, flat clothing and abrupt cuff/hand shape.
reviews.json records parent-captured summaries with actual image digests. No whole-artwork pass,
human acceptance, natural anatomy, general bouquet rig or broad drawing mastery is claimed. The
simple style does not need realistic anatomy, but readable structure remains work to improve.

## Verification

138 studio tests pass in tests-release/; ten old/default PNGs remain exact in preservation-release/.
Five head-frame and five orientation tests cover rigid paint/selection coherence, legacy migration,
protected locks, valid named SVG after translation, dependency edits, complete held-prop direction,
release, exact undo and invalid
constraint/input-alias refusal. After example defaults changed, targeted/ captures ten tests with
actual child exit0 and raw streams. An earlier PowerShell stderr-redirection attempt is retained
as UTF-16 with a disposition; its wrapper exit1 is not used as child-success evidence.

Run python evidence/studio-joints/verify_delivery.py --outdir FRESH for frozen digests, source
reconstruction, actual join geometry, recovery and current public helper replays. Old source-bound
verifiers in prior evidence directories retain their original epoch; use this entry and docs9 for
current checks. No GPU work, target access, generated image assets or pixel-target optimization was
used; the portrait baseline remains untouched. The overall creation goal remains active.

The next product gap is the repetitive source/target inspection ceremony and the independent cuff
width/seat decisions. A simpler visible semantic join should be tested against this real workflow,
while keeping scene safety, meaningful optional controls and actual picture quality.
