# Observed endpoint direction: real cuff corrections and guide review

2026-11-13. Adds public `preview --aim` for an inspected connected stroke terminal and an
inspected target mount. The operation fits the current outward directions by changing only bend,
keeping both terminal centers, width, depth and the named connection. A center/unsupported angle
refuses rather than inventing a direction or moving a locked end. It is a one-shot fit, not a
persistent orientation constraint or a physical/anatomical hand/arm solver.

## What was actually drawn

A new person-with-flower illustration uses 17 named native components, a computed five-petal
ring and explicit depth layers. Its initial structured authoring is compose.py; this is **not**
a claim of public-CLI-only initial creation. Subsequent observed corrections are public commands
in operate.py/commands.jsonl. The shipped ../../examples/studio/person_flower.json is the corrected
editable study. It is not whole-artwork accepted or a finished anatomical figure.

| Record | Actual decision/evidence |
| --- | --- |
| failed-initial-schema.json | The first table width 6.5 exceeded the existing shape range. Increase panel height, use width 6 and derive its top from the actual table edge. No engine range was expanded. |
| initial-working.json / 01-sleeve-observe | Five overlapping petals were authored at the same depth. Ten coplanar projection pairs triggered the full visibility route. The still-live candidate was deliberately canceled after this specific diagnosis; terminal exit was observed. No finished initial image is claimed. |
| equal-depth-diagnostic.json / equal-depth-cancellation.json / author_layers.py | Preserve diagnosis, actual PIDs and cancellation reason. Layer petals clockwise beneath their heart with computed depths; no manual visibility cuts or metric tuning. layered-working.json is the first rendered baseline. |
| 01b-sleeve-observe / 02-wrist-observe | Read actual clean sleeve and magnified wrist/arrow views. The flat horizontal cuff cuts across a diagonal wrist. |
| 03-sleeve-aim | Fit its tip to the observed wrist direction; only bend changes. Both pin centers and other authored components stay exact. The cuff seats visibly. |
| 04-accepted / 05-undone / 06-restored | Actual accept/undo/reaccept; original and corrected PNGs recover byte-for-byte. |
| 07-shirt-observe / 08-softer-shirt / 09-cuff-observe / 10-wrist-observe / 11-cuff-refit / 12-current | The torso was a rigid slab. Soften its shape with existing controls, observe the changed connected chord, then re-fit the cuff. This demonstrates why a later pose edit may need another one-shot fit. |
| 13-resting-root-observe / 14-left-shoulder-observe / 15-resting-arm-seated / 16-current | The far sleeve was attached at left@.23 (lower left), leaving an unclear triangle. Inspect actual left@.77, then reattach at the shoulder. The clockwise convention was already documented; the author had failed to use it. |
| 17-current-source | Same corrected art recompiled after the inspection-only arrow contrast change; clean PNG remains exact. |

Fresh image critics find the cuff/gesture and body silhouette improved. Their targeted follow-up
recognizes the formerly triangular shape as a hanging sleeve. They still find a tube-like elbow,
assembled shoulder/torso boundary, flat neckline, ambiguous large grip, uneven detail and weak
face participation. These are retained failures/limits, not silently promoted into an art pass.
The drawing reveals missing body/arm vocabulary; more connection commands cannot supply it.

## Guides and independent use

00-small-guides/ shows the selected camera glint at full/magnified scales. Minimum label rails
and screen-sized anchor/edit guides separate labels in the closeup. The full frame still crowds
several markers at the tiny object; use the magnified or exact-anchor inspection for precision.
The first arrows had weak contrast on dark paint. 00b-small-guides-contrast/ adds a light halo;
both image critics find the closeup contrast issue resolved. Shape side names remain local to the
rotated shape, while screen moves remain in canvas directions.

The independent operator read only frozen usability-inputs/, CLI help and own outputs. It repaired
the cuff, raised the hand/flower .04, observed the resulting cuff mismatch and re-aimed. Actual
undo/reaccept recovered canonical scenes and PNGs exactly. All 17 CLI launches have actual terminal
outcomes (one deliberate stale refusal); no live/missing process is inferred from absent artifacts.
Report, raw commands and 152 hashed artifacts remain frozen in usability/.

That original operation run binds engine 10fe6d92…c49b8. A later **inspection-only** arrow-halo
change binds current engine 46b89076…4eda2. prove_source_transition.py reconstructs the prior render
module and verifies its complete recorded engine hash; only that overlay function differs, with
alignment/model semantics unchanged. The reconstructed file is labeled reconstructed, not claimed
to have been captured earlier. current-guide-review/ is a separate 16-file operator supplement (plus two external guide image digests)
on current source, not another generation/recovery claim. Its clean PNG is unchanged. A fresh
current-engine public aim proposal in verification-current/aim/ also reproduces the exact earlier
canonical result/clean PNG without changing working input. Old candidates remain engine-stale.

reviews.json keeps parent-bound image-only observations and follow-ups. Those reviews do not have
independently printed formal portrait-rubric bindings and are not whole-artwork/human acceptance.
The operator's bounded usability verdict and the art limitations establish different claims.

## Try it

From the repository root, using your own working copy and separate output folders:

```
python -m scripts.studio inspect work.json --object sleeve --feature tip --outdir END
python -m scripts.studio inspect work.json --object hand --feature anchors --anchor wrist --outdir WRIST
python -m scripts.studio preview work.json --selection END/selection.json --aim WRIST/selection.json --reason "Let the cuff enter along the wrist" --outdir TRY
```

Read clean/alignment and closeups before accept. The two parts must already share this exact
join, in either dependency direction. A changed chord may require inspecting and aiming again.
Full contract/math live in ../../docs/7_INTERFACE.md and 8_DETAIL.md; practice is in the skill.
The study helpers preserve actual stages and can overwrite their historical outputs; repeat work
in a separate location, not against this frozen evidence directory.

Current-source verification: 118 studio tests, ten prior/default exact PNGs, actual parent/actor
recovery, explicit source-version separation and exact published study reproduction. Tests and
hashes never establish art quality. verify_delivery.py gathers those mechanical claims;
manifest.py checks frozen evidence bytes including nested input manifests. CPU geometry/resvg only;
no GPU work, reference image, diffusion/generated pixels or portrait baseline promotion.
