# S1a support-family experiment — transverse curvature, not another ink rule

## Authority / current state

User said “go” after exercise20 completed as a negative result. Continue implementation by
`github-copilot/gpt-6-luna`, parent-managed. Repo /home/z/vibe/learn_draw master base24693d4,
all earlier S0/S1a/drawing-rule work uncommitted. Preserve staged .gitmodules/vendor, untracked
.agents, old source/evidence/learner/reference. No commit/push/install/dependency or baseline promotion.
Read applicable AGENTS, WORKSPACE, STATUS, roadmap/spatial-model/method, exercise19/20 outcomes.

S1a is OPEN: construction/API worked but turning-sheet perception failed. Complete perimeter ink and
side-consistent motif did not solve it. This task studies ONE upstream support parameter rather than
more colours/stroke weights. No full S2/hair/figure/transfer acceptance.

## Hypothesis and causal control

The old support is straight across its width (a ruled strip). At a half-twist facing-zero event it
can project to an almost point-like width, even though actual material width is positive. A mildly
bowed transverse section has normals varying across width; the whole width need not be edge-on at
once. Test whether that geometric expressiveness improves recognition of one continuous sheet.
A mathematically correct change alone does not pass perception; don't assume this hypothesis wins.

Compare flat versus one mild nonzero transverse camber, holding centre route, twist, attachment,
base front/back palette, cameras and local artwork fixed. Choose and freeze one camber value before
rendering (suggest dimensionless .35, justified as modest cross-section rise). Do not sweep values,
fit pixels, change old specs/cameras or hand-author a fold/visible interval. No new ink/shadow/texture.

## Exclusive seam

Add `scripts/ribbon_surface.py` (or one equally descriptive NEW support-family module), dedicated
`scripts/tests/test_ribbon_surface.py`, and exercise21 work/evidence/teaching/log files. All existing
ribbon_family/ribbon_drawing/visibility source/tests, old cases/outputs/learner/figure/vendor/docs are
READ-ONLY. Parent owns docs/state. Reuse existing centreline/transport/twist and vector_visibility.
No general engine rewrite or runtime dependency on .scratch in new reusable module.

## Geometry contract / proposed parameterization

Whole artwork domain remains u in[0,1], v in[-1,1]. Root/tip and centreline remain attached, with
camber envelope zero at u endpoints and nonzero through the turn (e.g. sin²(pi*u)). Existing centre C,
transported-and-twisted width axis W and normal N come from old generator. A simple bowed section is
Q(u,v)=C(u)+k(u)*[v*W(u)+c(u)*v²*N(u)], with one semantic dimensionless camber parameter and
c(u)=camber*envelope(u). It keeps Q(u,0)=C(u), no per-view cuts. This is a new explicit support
family, not recovered ground truth for the reference ribbon.

Preserve material width/taper by transverse **arc length**, not by silently widening cloth to fix
projection: for c!=0 the full arc length is k*(sqrt(1+4c²)+asinh(2c)/(2c)); at c=0 it is2k. Choose
k to match the old requested width(u). Explain units and limits and check independently numerically.
If a different equally simple formula is sounder, justify before rendering and freeze it. No camera-
dependent width inflation. Front/back comes from actual new surface normals/winding, not old face
labels copied blindly. Visibility uses actual depths including across-width self-occlusion.

Flat limit must genuinely reproduce the old support/artwork, not just matching centre/endpoints.
If subdividing old source triangles in UV, use barycentric baseline points to preserve them exactly
at zero camber; document any distinction between continuous formula and finite sampled frame.
New curve samples shared by neighboring triangles must agree (no new anti-alias cracks or fake splits).
Do not assert smooth nonintersection from a few finite samples. Diagnose/fail invalid support cases
rather than patching silhouette.

## Preselected study and bounded sampling

Freeze work/cases.json with old input/camera hashes before producing candidate images:
- original positive half-twist, front and oblique cameras;
- untouched failed ordinary learner's negative half-twist spec, both same cameras, REGRESSION ONLY;
- untwisted teaching arch as negative/control condition and root/width check.

Every case gets flat and same mild curved section, identical framing/camera/palette/paint. Show base-
fill and existing local stripe consistently if both help isolate geometry; do not introduce a third
art treatment or rejected complete-perimeter style. Use a uniform declared mesh setting for pair
comparisons, enough transverse samples to show curvature. Profile one pair FIRST; incremental
save/cache/progress required for more expensive panels. Tests/selected extra convergence case compare
finer u/v sampling; don't hide faceting with postprocess or lower resolution only for hard cases.
No smaller subset substituted for the mandatory case classes.

If the kernel becomes too costly or degenerate, isolate exact geometry/runtime limitation, save
completed independent panels and report rather than extending into a new visibility engine. No
rendered image is claimed complete when panels are missing. Computation/render commands have explicit
finite deadlines and progress paths (normally120s individual; up to900s full measured build, raster180s).

## Outputs and tests

- Compact interface: existing ribbon spec + one support camber parameter, no author mesh coordinates.
  Runnable SVG/PNG renderer; named/intent-commented artwork, no all-mesh-edge ink.
- Analytic/numeric tests for root/tip/centreline invariance; material arc-length width and taper;
  zero-camber old-surface equivalence; local connectivity/shared vertices; finite consistent normals;
  facing change and depth visibility across width; original depth-positive/negative cases where
  relevant; sampling/convergence checks with explicit tolerances. Include counterexamples so tests
  detect widening, forced facing colour, or an invented seam. Preserve original exact-tie policy.
- Before/after view board labelled and unlabelled, with full strip visible and no answer arrows;
  frame common fit to combined geometry/card bounds, tested centre/margins. Inspect inline-SVG
  serialization and actual nonempty browser raster (lessons from exercise20), unique IDs.
- Teaching card describes mechanism/units/valid range, zero limit, constraints and actual failures.
  Geometry diagnostics at old facing-zero region distinguish physical width from projected width;
  numeric projection measurements are mechanism evidence, not optimization objectives.
- Command/source/support hashes and determinism. New tests plus relevant old focused tests and
  scene smoke; reference-independent draw check and exact report.txt lists. No self visual verdict.

## Acceptance / stopping

Parent reviews source and evidence, then fresh image-only review (images only, open question) and
follow-up describes visible continuity/front-back at both directions of twist. Only an accepted
method earns a NEW ordinary-model held-out task; never repair old learner then call it transferred.
No full S1a completion from this isolated experiment, no hair/figure/baseline promotion.

If transverse curvature adds fold clarity but causes collision/seams, report both; if no perceptual
benefit, retain negative finding and stop this hypothesis. No camber sweeps/additional ink rules.
Checkpoint before deadline: actual changed files, checks, saved artifacts and smallest remaining step.
Worker may contact supervisor on mathematical/architecture boundary; no child delegation.
