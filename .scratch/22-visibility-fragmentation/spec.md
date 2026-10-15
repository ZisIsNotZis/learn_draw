# Upstream renderer regression — fragmentation introduced interior raster defects

## Authority and scope

User's continuing “go” authorizes reversible work needed for the open S1a drawing objective. Parent
independent probe now isolates a renderer-stage defect, so pause the transverse-camber visual claim
and investigate backward. Implement with github-copilot/gpt-6-luna, parent-managed. Repo master
base24693d4; preserve all earlier dirty source/docs/evidence and staged user vendor/.gitmodules.
No commit/push/install/dependency, baseline promotion or reference/learner edits.

Read AGENTS, WORKSPACE, STATUS, spatial-model/method/roadmap and exercise21 parent-validation.
Reference implementation is tested only in bounded cases, not production-proven. This is neither a
new support/colour hypothesis nor an image metric optimization.

## Independent reproducer

Run/read `.scratch/21-ribbon-cross-section/work/parent_raster_probe.py` and its output
`evidence/fine/parent-raster-probe.json`. It uses the fixed fine96x12 untwisted arch, same camber .35,
geometry/camera/fit, pixel-centre barycentric intersections and nearest depth. Interior samples are
away from actual perimeter and local stripe boundaries, NOT away from mesh edges.
8495 safe interior pixels: authored raster41 base deviations>12RGB units; raw same-colour source
triangles serialized into one compound path have0; identical geometry after visible_regions has44.
No full background-colour holes at the sample centres, but partial-coverage flecks exist. This
isolates clipping/fragment serialization/raster interaction; it is not proof underlying depth is
wrong everywhere. It also explains why old coarse occupancy-threshold masks didn't detect the issue.

## Exclusive implementation boundary

Old canonical vector_visibility.py, ribbon modules, tests, frozen plans, existing images, learner,
figure, vendor and official docs remain READ-ONLY in this first diagnostic slice. New files only
under exercise22 work/evidence/log/teaching. Produce a minimized executable geometric repro and
ONE justified candidate patch against the current canonical visibility implementation. A small
scratch candidate module or exact patch file is allowed solely for evaluation, not a new production
renderer/fork. Parent owns eventual canonical integration/provenance updates after evidence.
Do not make old fixture hashes pass by modifying historical inputs or reference artifacts.

## Work

1. Preserve canonical source hash and reproduce parent's source-vs-depth raster difference. Minimize
   into computed geometry (no long handwritten contours) if practical. Determine whether unwanted
   subject subdivision on merely touching/projected-nonoverlapping triangles, tiny cut geometry,
   or compound serialization creates the partial coverage. Inspect actual fragment geometry/areas,
   shared-edge locations and raster; don't just trust the observer's white-speckle diagnosis.
2. Derive a geometric rule that addresses the cause. A projected bbox overlap is not automatically
   a positive-area occlusion. Investigate that distinction if evidenced, but don't assume it fixes
   the bug. No blanket skip-self/component rule: bent surfaces must retain genuine self-occlusion.
3. Implement ONE minimal candidate; no EPS/precision/random parameter sweep, pixel-score tuning,
   hidden-surface dilation, blur, background strokes, painter reordering or hand visibility masks.
   Keep current opaque API, interpolated depth intersections, tie policy and semantic provenance.
4. Regression checks: raw/depth visibility coverage for a known non-self-occluding surface; internal
   mesh edges do not create raster flecks; real outer/occlusion boundaries unexpanded; genuine
   crossing and changing-within-triangle depth; self-occlusion and declaration reversal away from
   exact ties; exact coplanar tie remains documented; touching-only and tiny positive-area overlap
   are distinct. Use failures/positive controls to prove tests catch an invalid shortcut.
5. Evaluate candidate with existing relevant S0/ribbon/support tests where feasible via isolated
   import/injection without editing their canonical source bindings. Explicitly report candidate vs
   canonical test revision. Save geometric area/provenance and deterministic SVG/PNG evidence.
6. Generate a small labelled/unlabelled source/canonical/candidate diagnostic and draw-check image
   lists. This is clean-render coverage evidence, NOT acceptance of camber/art readability. Do not
   rebuild full support matrices or run a new learner before parent accepts/integrates the patch.

## Completion/stop

Tests on pixels establish preservation of known geometry, not artistic optimization. Parent accepts
only source-backed cause and safety regression, with independent review and actual browser output.
If cause remains uncertain or fix requires a new engine/dependency/material contract, preserve
minimal repro and ask parent; do not expand silently. Do not claim new S0 certification or S1a pass.

Finite commands/progress: normally<=120s; one measured full probe may use<=600s. Incrementally save
results; checkpoint before deadline with exact files/checks/artifacts and minimal remaining step.
No child delegation or source edits outside stated scratch-only seam.
