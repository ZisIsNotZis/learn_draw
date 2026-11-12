# Generic colour masses: creation outside the preset catalog

## Question and bounded result

Can a VLM create a new subject without first implementing a subject-specific generator, and inspect
where a local correction will land? The new shape primitive is one small lower-level surface:
a useful rounded block by default, optional oval/taper/rounding/palette/outline, and protected
left/right/top/bottom arc pushes. It uses the same preview/accept/undo/stale guards as other parts.
No raw path controls, target raster or image generator is required.

A root-authored lighthouse coastal scene uses named generic masses for tower, roof, lantern, rock
planes, panes and water marks, plus existing sky/sun. There is no lighthouse primitive. Its source
shares a named tower ruler for placement; this is a scripted composition, not independent CLI use.
Original and revised pictures and critiques are preserved. Repeated reviewers still identify
ambiguous water/cliff marks and schematic volume; the revised work does not earn an artwork pass.
Fresh-context review-a/b reports at this directory supply an additional image-only pair.

## Actual study sequence

- 00-default: first angular-sampling experiment, before arc-length resampling. A historical output,
  not a current replay source. Its old implementation hash is retained; source was not archived.
- 01-arclength: initial nominal-length resampling and actual selected left boundary.
- 02-local-push: the default mass's left middle bows outward while its joins stay fixed.
- coast: first 18-part subject, source and two image critiques. The dark base reads like a puddle,
  rock/water boundaries are ambiguous and tower contact is weak.
- coast-refined: 23-part parameter revision with separate upper/side planes, footing and water marks.
  Its source rebuilds that pre-local-edit scene; later scene.json contains the accepted correction.
- 03-cliff-selection and 04-cliff-proposal: actual visible region and bounded shelf extension.
- 05-cliff-accepted and cliff-edit-record.json: public CLI accept, exact scene undo and replay, then
  reinspection. replay_cliff_edit.py needs the pre-local scene from coast-refined/source.py first.
- coast-final-check: PNG-source-preserved image-review bundle. coast-final-review-a/b retain
  repeated observers; fresh-review-a/b are separate reviewers spawned with no inherited context.
- usability: independent operator's desk-lamp/book intent, seven generic masses built only with the
  skill/public CLI. It discarded an unhelpful shade edit. All original choices and failures remain.
- thin-line-repair: separately labeled root-assisted width correction after the independent run.
  The fine mark is now permitted; all pixels outside the old mark are exact. Fresh lamp-review-a/b
  see the finer line but retain ambiguous book identity and flat/junction limitations.
- verification: current source/scene hashes, repeated CPU SVG/PNG identity, default preservation.

## Mechanism and verification

Four nominal quadrant arcs are resampled by length. A compact cosine field applies a local push
inside one selected arc, keeping its joins and every station outside influence exact. The requested
screen move is inverted to material-local axes, so rotating the sculpt rotates its deformation.
The fill and explicit half-stroke form the opacity footprint, handled by the existing depth engine.
Self-intersections/collapse refuse a proposal; current object bounds never reparameterize old edits.
Details and the authoritative schema are in docs/8_DETAIL.md and docs/7_INTERFACE.md.

79 combined operation/checker/visibility tests pass, including eight new shape tests across all four
sides, oval/block, tilt, non-square canvas, screen locality, whole-object rotation, invalid requests
and undo. The preceding hand unit's 81 CPU smoke checks passed; generic shape changes do not alter
legacy generators. Current repeated SVG and CPU resvg PNG bytes match. Accepted default-head PNG
and default-hand PNG remain unchanged. verification/validation.json gives exact values. Tests prove
operation properties; they do not settle aesthetics. No whole-art baseline was promoted.

## Scope and next gap

This is a compact contour tool beneath semantic macros. There are no arbitrary paths, compound
holes, scene-object booleans or attachment graph. More degrees of freedom are justified by an
actual blocked drawing operation. Current scenes still use separate manually positioned objects;
coherent joints and shared boundaries are more consequential than endlessly adding preset subjects.

## What the independent creation changed

The operator's request for width .008 was refused by an arbitrary .05 aspect floor. Its original
thicker low-contrast workaround is preserved, not relabeled as the desired fine line. A pre-fix
failing regression is retained as thin-mark-before.txt (PowerShell UTF16 capture) and the decoded
UTF8 copy. The floor is now .001; a painted, antialiased sub-two-pixel mark is tested. Exact fill
RGB is not required in a mark narrower than two pixels. Root-assisted repair changes only width;
it demonstrates permission/control and locality, not a whole-icon aesthetic solution. The complete
Studio source used by the independent operator is archived at source-at-independent-use/; current
implementation differs by the width floor, clearer help and output/input alias protection.

A root replay initially used the same scene.json path for working input and bundle export, so the
export replaced the input before accept. Actor source/artwork were untouched. This also exposed a
public CLI hazard: preview could invalidate candidate.json before reading a working input of that
name, or write exported scene.json over the working file. An input-preservation regression failed
before the fix. Inspect/preview now refuse aliases among planned outputs and scene/selection inputs
before any write; API callers must keep their own source/export paths separate. The successful
repair replay uses working.json and records exact locality. No working source is deleted.

The independent scene still rebuilds to its original PNG hash 0103f189278697c4bc2f48964f276781a860d1e1a3fc6feaa74bd3ddb9cfbb2b
under current code. Its one blank-view observation was checked against identical fullres/preview
hashes and not used to alter geometry. The cause of inconsistent external display is still unknown.

The trial also required many inspect/preview/accept calls to configure each new mass. A useful next
product change is one visible atomic preview for a coherent group of semantic parameter changes,
followed by relative placement/attachment where separate shapes must meet. These address observed
creation effort and joint ambiguity, rather than expanding the subject catalog indefinitely.
