# Visibility fragmentation scratch follow-up — candidate V3

## Revision preservation and narrow code change

- Candidate V1 is preserved at `work/vector_visibility_candidate_v1.py`, SHA-256 `ed07910a16000e82215b924d932c1859c4dc2da3b932f6d3740ccbb23cf08da6`.
- Candidate V2 is preserved at `work/vector_visibility_candidate_v2.py`, SHA-256 `6faa70eb71457dba5c848b0f46da98be9aebe914261e1763885ed3dd2e0a6855`. V2 logs, tests, `study-v2.json`, oracle-v2 JSONs, V2 SVG/PNG outputs and check bundles were not overwritten.
- V3 is the existing isolated candidate path `work/vector_visibility_candidate.py`, SHA-256 `5f289fed2ffe3d35740e0d3927b0a2ed168883d8785f4786746e6610e3112da7`.
- Canonical renderer and historical tests remain read-only; canonical renderer SHA-256 is unchanged at `6cea919d0c83b1c4ebb9b3ec3379854c910e2758610b449c036c25c9ce8e1ada`. No commit/install, source/test/docs edit, full matrix, learner, or production integration occurred.

V3 leaves the public tolerance-aware `line_clip(poly, fn, keep_positive=True)` behavior equal to V2: the scratch test compares V2 and V3 outputs across signs, windings and scaled halfspaces. The new private `_clip_halfspace` takes an explicit classification boundary and always interpolates on that same boundary. Public clipping still selects the existing `-EPS`/`+EPS` thresholds. `subtract_convex` calls the helper with boundary zero for both complementary halves; it no longer retains the shared positive-area EPS band. It skips only an **exact projected zero-length edge** (`a.x==b.x and a.y==b.y`) because such an edge defines no separating halfspace. No short nonzero edge is EPS-dropped, no coordinate precision sweep/clamp was added, and the original cutter points/depth/tie policy/API remain unchanged.

## Exact partition guards and measurements

Five V3 scratch tests cover:

- Public V2/V3 `line_clip` parity, finite/source-contained crossings, in-segment intersection parameters, both keep signs, both windings, fixed scales `.5,1,2`, and vertices exactly on the public EPS classification boundary. Canonical and V1 remain failing source-external controls.
- Convex subtraction under translation, scaling (`.25,1,2,8`), and reversed subject/cutter winding. Independently computed convex intersection area defines the expected remainder. Every returned vertex stays in the subject; positive-area outputs have pairwise intersections within `1e-10 * max(1, subject area)`; summed output area matches source-minus-intersection within that declared error.
- The V2 short-edge witness: V2 remains a negative control with positive-area overlaps; V3 remainder area is `4.1065323085392863e-8` against independently clipped expected `4.106532308539279e-8` (error `7.28e-23`, declared bound `1e-12`), zero pairwise positive-area overlap, and minimum subject barycentric weight `-6.7e-16`.
- Repeated consecutive cutter vertices, redundant collinear vertices, and zero-length edges. V2's vacuous zero edge reproduces overlapping whole-subject outside pieces; V3 skips only the exact zero-length projected constraint and yields a disjoint partition. Coincident subtraction may return degenerate zero-area polygons, but their total area is zero and `_compound_path` serializes none. Shared-edge touching preserves the source; a positive overlap is still cut.
- A real cutter edge of length `1e-8` (< EPS) with area above EPS remains active and conserves subject-minus-intersection area. The `visible_fragments` tiny positive occlusion above the existing bbox deadband remains active and returns the near face at the overlap sample.

The audit file `evidence/oracle/subtract-eps-witness-v3.json` records V1/V2/V3 comparisons and the corrected witness. No broad clipping framework or area-merge mechanism was added.

## Independent depth oracle / fragment geometry

The bbox-tiled original-triangle max-depth oracle is rerun as `work/visibility_oracle_v3.py`; V1, V2 and V3 results are separate in `evidence/oracle/visibility-oracle-v3.json`. It centers the same ring fixture, samples N=128/256/512/1024 phase .5 and N=1024 phases .25/.75, interpolates depth from original triangles, reports source-edge/tie ambiguity, candidate fragment union and summed fragment area separately, and adds geometry-only source-owner tags without altering raster grouping. Run time: **4.80 s**, peak RSS about **157,508 KB**. It remains finite-sampled evidence, not a continuous proof.

- Independent original-triangle observations are yaw 0 `.8667341–.8690753`, yaw 55 `.7489383–.7497473`. V3 summed fragment fractions are yaw 0 **`.8690584319`** and yaw 55 **`.7492076592`**, matching those independent observations rather than the stale `.7968` yaw-55 sum expectation. This agreement is evidence, not a new output-gold test.
- The V3 geometry audit finds zero source-triangle vertex excursions beyond `1e-10` barycentric, and zero nonconvex/self-intersecting positive fragments in both yaw views. Yaw 0 emits 310 strip fragments (181 zero area); yaw 55 emits 399 (217 zero area, 5 positive areas `<=1e-18`). Zero/tiny outputs are excluded from sampled union.
- Fragment-union sampling shows many candidate-fragment boundary samples: strict interior estimates are below the original-triangle oracle (yaw 0 about `.8055–.8057`, yaw 55 about `.7134–.7138`); boundary-inclusive samples contain all but no continuous claim is possible, and boundary-inclusive false positives are substantial (about 9k and 24–25k sample centers respectively at N1024). This is an ambiguity measurement, not a renderer failure claim. Source-edge/depth-tie oracle samples were zero; cut/mesh fragment-boundary samples are a separate ambiguity class.

## Fine arch and true-boundary evidence

The V3 parent arch run uses the fixed fine96x12 geometry/view/fit and same 8,495 safe interior sample mask. Raw source has **0**, canonical has **44**, V3 has **0** nonmatching base-fill samples; V3 has **0** background-like interior samples. A repeated V3 Chromium render is byte-identical (PNG SHA-256 `c7763f73fb86ef815ce7cafcacdd59b896481446c400971bc24c630219d07afc`). The 4x3 generated minimal repro remains raw-pixel-identical under V3 while canonical retains its touch-fragment silhouette deltas.

The V3-injected historical suite passed the existing Chromium tessellation/exterior/occlusion boundary checks, partial far-edge/background case, and source-edge body-card probe. Only the stale yaw-55 summed-fragment fraction check failed. These are bounded regression observations, not visual/art acceptance.

V3 labelled/unlabelled boards are `evidence/fine/arch-v3-labelled.png` and `arch-v3-unlabelled.png`. Reference-free draw-check reports list exactly:

- `.scratch/22-visibility-fragmentation/evidence/check-v3-labelled/draft.png`
- `.scratch/22-visibility-fragmentation/evidence/check-v3-unlabelled/draft.png`

The check reports contain those exact image lists and no reference comparison.

## V3 proposed test patch (not applied)

`teaching/proposed-v3-tests-complete.patch` is a dry-run-checked, unapplied parent proposal. It preserves the same two-camera ring fixture and the `> .05` camera-change intent, removes the stale `.8755/.7968` output-sum gold, adds an analytically checkable disjoint source-partition test, and includes the independent original-triangle coverage test from `proposed-independent-oracle-tests.patch`. The previous V2 proposal and this V3 update remain artifacts; neither was applied to historical tests.

## Test results / stale compatibility alarm

The final V3-injected chosen suite counted **63 historical + 10 scratch = 73 total**. **72 passed; exactly one historical assertion failed**: `test_same_whole_strip_updates_visibility_in_two_cameras` expects `.7968 ± .01` at yaw 55, while V3 sums `.7492076594`. The independent original-triangle depth oracle estimates `.7489383–.7497473`; retain this historical failure as a stale-ground-truth compatibility alarm until parent review. It was not edited. A run excluding only this one test passed **72/72**.

Both historical V3-relevant failures observed under V2 are resolved: the partial-occlusion source area is now within its exact expected value, and the body-card query no longer reports the farther card. No unexplained failure remains in the chosen suite. The proposed patch should still receive independent review before any canonical integration.

## Commands and provenance

- `.venv/bin/python .scratch/22-visibility-fragmentation/work/test_visibility_candidate_v3.py` — 5 passed.
- Candidate V3-injected selected suite — 73 total (63 historical + 10 scratch), 1 stale summed-area failure above.
- Same suite excluding only that stale assertion — 72 passed.
- `.venv/bin/python .scratch/22-visibility-fragmentation/work/visibility_oracle_v3.py` — passed in 4.80 s; wrote `visibility-oracle-v3.json`.
- `.venv/bin/python .scratch/22-visibility-fragmentation/work/visibility_subtract_audit_v3.py` — passed; wrote `subtract-eps-witness-v3.json`.
- `/usr/bin/time .venv/bin/python .scratch/22-visibility-fragmentation/work/study_candidate_v3.py` — passed in 12.87 s; wrote V3 raw/canonical/candidate arch/minimal SVG/PNG and determinism evidence.
- V3 labelled/unlabelled `scripts/draw check` runs — passed; image lists above.
- `git apply --check teaching/proposed-v3-tests-complete.patch` — passed as dry run; not applied.

## Handoff

V3 is still scratch-only. Parent owns whether to accept or reject it and any canonical/provenance/test changes. No production integration, visual/art/readability verdict, full support matrix, learner run, or S1a pass is claimed.
