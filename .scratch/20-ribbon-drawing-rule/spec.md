# Readable ribbon drawing rule — bounded S1a dependency

## Authorization and why

User said “go” after the S1a outcome documented geometry/API success but failed readability and
visual transfer. Continue with github-copilot/gpt-6-luna implementation, parent-managed acceptance.
Repo /home/z/vibe/learn_draw, master base HEAD 24693d4, inherited S0/S1a/docs dirty plus protected
staged vendor/.gitmodules and untracked .agents. No commits/push/install/clean/reset or baseline
promotion. Read applicable AGENTS, WORKSPACE, STATUS, roadmap/spatial-model/method and
.scratch/19-ribbon-family/outcome.md.

Diagnosis: true edge-on projection can pinch a perfectly continuous strip; both visits of a crossing
may show the same material and merge perceptually. The earlier overlap-only cue helped one crossing,
not its depth reversal. A face-dependent dark/cream stripe changes identity at the turn. Tests alone
cannot certify readable drawing. This new task tests a **semantic line and artwork rule** under
fixed geometry, not another support formula or cosmetic patch. Full S2/figure/hair remain unaccepted.

## Scope and ownership

Add one small drawing-layer module `scripts/ribbon_drawing.py`, dedicated
`scripts/tests/test_ribbon_drawing.py`, and this exercise's work/evidence/teaching/log. Existing
ribbon_family.py, vector_visibility.py, all S0/S1a sources/tests/cases/evidence, figure/assembly,
learner outputs, reference, vendor and official docs are READ-ONLY. Parent owns docs/state. One
writer only. You may read/reuse the tested .scratch/19 work/occlusion_probe.py algorithm, but the new
reusable module must not have a runtime dependency on .scratch (extract only the actually reused
functions necessary for this slice; no universal graphics/line framework).

## Freeze the hypotheses and comparisons before rendering

Create work/cases.json identifying the exact old specs/cameras by hash/reference. Retain originals.
Use a uniform render-resolution setting for comparisons (128 longitudinal intervals is an explicit
compiler sampling override, not changed author input). For each same geometry/camera compare:

- control: current fills and face-dependent stripe, no new ink;
- rule A: depth-visible semantic perimeter ink, classifying external silhouette and overlap/occlusion
  boundary; no mesh ink, contact lines or invented folds;
- rule B: rule A plus a consistent local longitudinal motif on BOTH material sides (e.g. a narrow
  light core with dark local borders); identity survives colour-side change. Keep front/back base
  palette and support geometry. This motif is artwork on full (u,v), not a projected line drawn to
  connect a guessed break. If needed, use existing barycentric UV clipping inside original support
  triangles so new artwork does not bend geometry.

This is at most TWO candidate rules plus control, not an open-ended style search. Define line/motif
width rules before images; semantic stroke weight may differ for silhouette vs overlap but never
manually by u interval or screen location. No soft field/shadow/texture masking, pixel objectives,
per-view authoring, depth expansion, camera substitution or invented visibility cuts.

Mandatory geometry/views: teaching arch (no overlap but full visible perimeter exists); frozen
crossback front; explicitly additional depth-sign reversal front; frozen half-twist front and
oblique; original failed learner spec front and oblique as a regression only (NOT a repaired unaided
transfer pass). Include a support-card test so foreground objects clip hidden ink too. Geometry or
parameters must not be changed to make a rule pass. Old learner answer remains untouched.

## Line responsibilities

Candidates originate ONLY from named local domain perimeter (v=+/-1 and u endpoints), never mesh
diagonals. Generate complete candidates once, project and split at actual support edge intersections
and depth-equality roots; hidden segments are omitted. Intersections with external occluder surfaces
must be considered, not just self-occlusion. Use UV/triangle provenance to distinguish owning surfaces
from unrelated cover; do not ignore an arbitrary neighbourhood that can hide true folds without
explaining scope. Exclude the same source geometry/ties via existing declared opaque tie policy.

Keep geometric visibility separate from artistic weighting. A foreground boundary may carry a
stronger overlap line when it masks a farther nonadjacent strip; external silhouette gets a restrained
line. A selected stroke's finite width is artistic ink, not a geometric remedy. If stroke placement
can leak across occluder edges, clip its coverage or explicitly bound that failure; don't claim
complete line visibility from centerline-only tests. Avoid cap bridges across hidden gaps.

Do not smooth away an actual edge-on pinch or change physical depths. The question is whether these
rules let a viewer recognize one turning sheet and its overlap. If not, retain failure and identify
whether support family/artistic projection needs a distinct next experiment; don't invent more rules.

## Outputs and executable checks

- A documented small renderer/CLI accepting the existing compact ribbon spec with rule selection,
  camera and sampling override; construction source stays untouched. Named line/fill paths with intent.
- Tests for complete semantic perimeter, hidden line rejection including external card, absence of
  internal edges, class/weight provenance, depth reversal changes selected front overlap, consistent
  local motif on both sides, preserved original support triangles and filled visibility, deterministic
  output/unique IDs, known failure controls (all-edge ink, hidden-edge overpaint).
- Clear fixed-framing comparison boards, labelled and unlabelled, plus line-only panels where helpful
  to isolate boundaries. Pair same geometry/camera/resolution; no answer arrows/near/far labels in
  unlabelled perception image. Include original lower-resolution control only separately if useful.
- Teaching card: rules, commands, reason each line exists, units, range/known limitations and next
  learner-facing interface. Do not claim visual learning yet.
- Exact source/support/case hashes and commands/results. Run relevant new tests and existing focused
  S0/S1a suites plus scene smoke; no edits to old tests. Deterministic render twice; draw check labelled
  and unlabelled boards and preserve exact report.txt image lists. No reference-image runtime input.

Each command gets finite timeout (normally <=120s; explain larger bound if needed). Bound meshes and
board size; don't respond to high visibility cost by weakening depth correctness. Report checkpoint
well before deadline, with actual files/artifacts/checks and precise remaining work. No child delegation.

## Parent acceptance

Parent inspects scoped diff/test evidence. Fresh image-only reviewer first receives report images and
“What is wrong here?”; follow-up describes actual continuity/two faces/over-under for original AND
reversed-depth cases. Verify spatial claims against geometry/panel provenance. A review aggregate
OK is not a substitute for required perception. One small trial need not generalize universally;
record tested scope. Only after a drawing rule is accepted does parent run a NEW held-out ordinary-model
attempt using its teaching interface. Old failed learner rendering may show regression improvement,
never unaided success. No baseline promotion or figure migration.

Worker final report: chosen rules and tested responsibilities; changed paths; preserved geometry hash
checks; actual tests/render/determinism outcomes; report image lists; failures/limits; gates pending.
