# Compact grip: native operations, real integration and independent use

2026-11-13. This unit changes the native drawing vocabulary and demonstrates it in
actual drawings. It does not complete the project, pass the legacy portrait, or
establish anatomical/general 3D grasp ability. The person accepted retaining this graphic hand as a simple preset direction on
2026-11-13, after the local thumb/pole refinements. This does not accept natural
anatomy or a whole artwork; the earlier flat-head approval remains separately scoped.

## The usable slice and its limits

`python -m scripts.studio new work.json --kind grip` creates one compact illustrated
closed hand with its own handle segment. Required input is semantic id/kind/intent;
thumb, folded-pad and handle refinements are optional. Inspect exposes the actual
selected shape, revision, named mounts and dimensions; previews are separate,
acceptance is revision/engine-bound, and undo recovers the input. The owned handle
is extended through the existing attachment/two-target stroke graph.

This is a 2.5D symbolic vocabulary item. It computes short folded pads, compact palm
and bent opposing thumb from a hand ruler, with constant support depths deciding
visibility. Ink is intentional, separate from fills, and has no sealed tissue-root
seam or isolated tiny finger fragments. It reads no teaching SVG, mesh, target or
generated picture. Production source is `scripts/studio/grip.py`; exact supported
fields live in `docs/7_INTERFACE.md`, practice in the drawing skill.

Blind reviewers still find rounded-pad anatomy, broad thumb, a tiny crease-end tick,
and schematic palm/wrist proportions. Preserve those observations. A fresh
purpose-aware operator separately found that the default can serve a flat held-flag
composition without rebuilding it. This is one bounded usability result, not an
automatic threshold reduction, anatomy pass, human taste verdict or universal transfer.

## Pictures and actual work

| Record | Actual result |
| --- | --- |
| `00-teaching-reference/` | OpenMoji raised-fist teaching SVG rendered larger on paper; source paths unchanged. Licensed reference, not runtime geometry. |
| `01-compact/`, `02-watering/` | Independent procedural short-pad/palm/thumb grammar and its first scene assembly. No OpenMoji paths are loaded or copied by the generator. Blind anatomy/overlap criticisms retained. |
| `03-native-default/` | Same direction integrated as a native kind, with cleaned isolated ink fragments, softer wrist joins and actual selectable thumb geometry. Default hand/handle is produced from one sparse node. |
| `04-thumb-shorter/`, `05-thumb-observe/`, `06-thumb-easeback/` | Actual public-CLI correction: thumb reach .90 → .72 → .80, observing each result. Wrist, handle ports and other materials stay fixed. |
| `06-undo/`, `06-restored/` | Undo restores the .72 image exactly; reaccepting the revision-bound .80 candidate restores its exact PNG. Current small working scene is `native-working.json`. |
| `07-native-watering/` | Fully native replacement in the existing watering scene: one grip, two doubly bound handle legs, dependent reservoir/spout and soil-bound water. No SVG macro insertion at runtime. |
| `08-sleeve-observe/`, `09-sleeve-tangent/` | The cuff cut across the wrist. Change only sleeve bend so its endpoint tangent enters the hand, while both terminals and grip mounts remain pinned. Accepted. |
| `10-flag-handle-observe/`, `11-flag-continuous-pole/` | Parent finishing on a copy of the independent flag: match held-segment outline colour to the plain pole. All mounts/bounds unchanged; visible material seams disappear. The actor's original result is untouched. Accepted. |
| `12-can-opening/` | Discarded model-API initial-authoring preview. A correctly mounted oval is mostly hidden by the foreground sleeve and becomes two stray patches. Never accepted into the preferred scene; not a public CLI atomic-insertion claim. |
| `13-water-observe/`, `14-water-flow/` | Match the stream's starting direction to the spout; taper and lighten it, preserving both bound endpoints. Accepted. The result is an authored quadratic gesture, not fluid simulation. |

Current examples are `examples/studio/held_flag.json` (5 nodes) and
`examples/studio/watering_grip.json` (23 nodes). Render them into fresh editable copies:

```
python examples/studio/held_props.py --scene flag --outdir FRESH_FLAG
python examples/studio/held_props.py --scene watering --outdir FRESH_WATERING
```

The preferred flag's check bundle is `check-flag-finished/draft-fullres.png`; the
preferred watering view is `check-watering-current/draft-fullres.png`. Both retain
their real full-resolution PNG bytes. Two fresh image-only reviewers saw both.
They read the flag/grip clearly and report no obvious pole contact/visibility break;
watering still has ambiguous small fingers, schematic elbow/cuff, and wire-like
water. One calls thickness uniform; the authored widths actually taper from .85
to .45 of nominal thickness. That numerical fact does not cancel the wire-like
perception or establish a drawing pass. No portrait baseline was promoted.

## Independent operation and calibration

`usability/REPORT.txt` owns the fresh operator's report, with original scene,
command records, failed first sleeve composition, all previews and exact undo/replay
evidence. It read only the skill, its interaction reference and interface schema;
no source, examples, earlier studies, generated images or GPU. Its original final
is `usability/07-final/artwork.png`, SHA256
`196634bb0929daf6d795fb0fdffb5f8d00d866fab2c5fc0165ad7fc1ce461ccd`.
Parent finishing is separate and must not be described as that unaided final.
Actual allowed inputs were frozen throughout the run and copied into
`usability-inputs/` before current guidance changed. Engine remained
`7e6b1a1d61cf8f2395ef547cb20d2cebd690627feb5415054d586189639f8648`.

The operator seated a sleeve by changing its angle after observing a triangular
gap. It shortened thumb reach .90 → .72, retained every mount/external bound, and
verified accepted → undone → reaccepted scene/render identities. A verification
script first used exact floating equality for a 2.84e-14 px residual; that failed
diagnostic is retained and the corrected tolerance is explicit. No engine repair
or primitive reconstruction was performed.

`reviews.json` keeps the blind qualitative observations beside the purpose-aware
result. A blind review of the published OpenMoji fist raises similar realism,
diagrammatic-thumb and mitten complaints. Those observations do not prove that
reviewers are wrong; they show why an unprompted fault list alone is not a scoped
component usability verdict. `docs/4_USECASE.md` already required that distinction.
The author had failed to apply it, causing unnecessary mesh-only refinements;
this unit changes the method by actually running the separate operational review.
These are parent-bound image-only qualitative critiques, not independently printed
commit/hash bindings for a formal portrait-rubric gate.

## Verification and provenance

```
python evidence/studio-grasp-glyph/run_tests.py
python evidence/studio-grasp-glyph/verify_preservation.py
python evidence/studio-grasp-glyph/verify_delivery.py
```

103 package-named studio tests pass, including seven new grip tests. Two earlier
`unittest discover` invocations were invalid for the namespace test directory;
their failure logs are retained. The corrected runner loads all studio test modules
by their package names. Seven prior/default artwork PNGs remain exact. Delivery
verification rechecks 126 actor file hashes, actual semantic/anchor recovery,
preferred PNGs, sleeve/nozzle tangents, and both helpers from a fresh cwd, including
existing-output refusal. Tests/geometry and blind art review prove different claims.

OpenMoji's pinned source and CC BY-SA 4.0 license/attribution are in `third-party/`.
The enlarged paper-backed teaching preview remains under that license. The native
generator has its own relational geometry and does not import those vector paths.
The abandoned mesh route is in `../studio-grasp-contact/`. No production dependency
on either the teaching art or its study-only 3D packages is introduced.
`manifest.json` accounts for the frozen study bytes; current decisions live in docs.

For integrity only, run `python evidence/studio-grasp-glyph/manifest.py`; it checks
both study trees and includes nested operator-input manifests. `--seal` is reserved
for an intentional new evidence revision, never a way to accept changed art silently.
