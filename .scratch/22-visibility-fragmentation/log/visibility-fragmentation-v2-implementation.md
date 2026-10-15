# S1a visibility-fragmentation scratch follow-up — candidate V2

## Implemented

Preserved candidate V1 byte-for-byte and all unsuffixed V1 evidence. Added an isolated V2 candidate with the approved minimal `line_clip` correction: shift signed values by the same `EPS` threshold used for classifying the kept halfspace, then interpolate at shifted zero. Positive clipping uses `g=fn+EPS`; negative clipping uses `g=fn-EPS`. The interpolation parameter comes from those shifted values, not a clamp or a zero-root approximation. No canonical file, historical test, old plan, reference image, learner, or official doc was changed.

Also persisted a runnable bbox-tiled original-triangle barycentric max-depth oracle and separate subtract geometry audit. Source-owner tags exist only for geometric attribution; they do not change component/color grouping or raster calls. The proposed independent-oracle regression patch is a dry-run-checked scratch artifact and was **not applied**.

## V1 preservation

- V1 module: `.scratch/22-visibility-fragmentation/work/vector_visibility_candidate_v1.py`, SHA-256 `ed07910a16000e82215b924d932c1859c4dc2da3b932f6d3740ccbb23cf08da6` (matches V1).
- V1 `study.py`, `evidence/fine/study.json`, V1 source/current/candidate images and prior check bundles were left intact.
- The prior V1 handoff report was copied verbatim to `.scratch/22-visibility-fragmentation/log/visibility-fragmentation-v1-implementation.md` before updating this run's authoritative output artifact.
- Canonical `scripts/vector_visibility.py` still hashes to `6cea919d0c83b1c4ebb9b3ec3379854c910e2758610b449c036c25c9ce8e1ada`; historical `scripts/tests/test_vector_visibility.py` still hashes to `8977f31fb12e1f9a660f30866bd0ba271e4541f86d29cc091e32cd5a9cd4acd2`.

## P1 witness and corrected behavior

For `fn=EPS*x` on the independent review's source triangle `[(-.8,0),(-1.2,1),(-.8,2)]`, canonical and V1 classify using `fn>=-EPS` but interpolate at `fn==0`, yielding `(0,-2)` and `(0,4)` outside the source triangle. V2 emits boundary intersections at `x=-1`, on the actual classification threshold. The durable scratch regression checks finite results, source-triangle containment, source-edge segment `t∈[0,1]`, both keep signs, both input windings, and fixed signed-function scales `.5,1,2`; canonical and V1 are failing controls in each case. EPS itself was not swept, and no segment parameter is clamped.

A short-cutter-edge `subtract_convex` audit also confirms V1 source-external output (minimum subject barycentric weight `-0.6667`) while V2 vertices remain in the subject hull (minimum `-5.6e-16`). It exposes a residual that is not patched around: on that EPS-sensitive witness, V2 returns three outside pieces with total area `7.9077e-8` against subject area `5e-8`; pairwise intersections measure `2.7804e-8` and `1.2729e-9`. These outputs' sum is not their union. See `evidence/oracle/subtract-eps-witness-v2.json`; no merge/overlap/precision mechanism was added.

## Durable independent oracle results

`work/visibility_oracle.py` is runnable and uses only the fixture's original projected triangles: centered coordinates `(200,150)`, barycentric depth interpolation, per-sample maximum depth, and bbox-tiled sampling. It reports source-edge/depth-tie ambiguity, candidate fragment **union** separately from summed fragment area, strict and sample-boundary-inclusive membership, polygon topology, and geometry-only source-owner containment. It excludes zero/tiny (`<=1e-18`) polygons and zero-length edges from union membership. Run time was **4.23 seconds**, peak RSS **157,292 KB** for both yaws at N=128/256/512/1024 phase .5 plus N=1024 phases .25/.75. These are empirical samples, not a continuous proof.

- Oracle visible fractions: yaw 0 — `.8667341` (N128), `.8688997` (N256), `.8690314` (N512), `.8689985` (N1024/.5), with N1024 phase range `.8690680–.8690753`; yaw 55 — `.7497473`, `.7492057`, `.7495848`, `.7492159`, with N1024 phase range `.7489383–.7494460`. No sampled source-edge or strip/body depth ties occurred.
- V2 summed fragment fractions are **`.8759310` yaw 0** and **`.7542604` yaw 55**. These are not ground truth and differ from the sampled oracle. At yaw 55, V2's sum is still about `.0045–.0053` of raw source area above the oracle observations.
- V2 fragments are finite, convex/simple, and source-triangle-subset within numeric tolerance on both ring views. At yaw 0, strict sampled fragment union had no false-positive or false-negative source-visible centers on tested grids. At yaw 55, strict-interior membership misses roughly `.99–1.03%` of source-visible centers because many lie on output-fragment boundaries; boundary-inclusive membership has no false negatives and 0–54 false positives among approximately 221k source-visible samples. This is boundary-classification uncertainty, not continuous coverage proof.
- The bbox broad phase still uses its historical `EPS` deadband before SAT, so represented positive overlaps with bbox extent at or below `EPS` are not covered by the tiny-positive test (which uses width `1e-4`). It was not broadened here.

## Fine arch, minimal repro, and browser evidence

The rerun uses the fixed parent fine96x12 arch with the same geometry, camber, camera, fit, fill, and safe barycentric mask. Raw source = **0**, canonical = **44**, V2 = **0** deviations among **8,495** safe interior samples. V2's second Chromium PNG is byte-identical to the first (SHA-256 `3660a0300a3e05586b20a54d9421abe458ea1a833e0879dd0c3c6b0389059fca`). V2 emits 9,757 fragments (2,739 zero-area, 2,493 positive fragments `<=1e-10`, 2,512 `<=1e-7`) and 7,018 serialized paths; those area/path counts are not artistic acceptance.

The computed fractional 4x3 mesh retains the V1 comparison: candidate raw-identical raster; canonical has 24 zero-area outputs and four last-row/column partial pixels. V2-suffixed SVG/PNG evidence does not overwrite V1 files. Labelled/unlabelled V2 boards are `evidence/fine/arch-v2-labelled.png` and `arch-v2-unlabelled.png`. Reference-free check reports list exactly:

- `.scratch/22-visibility-fragmentation/evidence/check-v2-labelled/draft.png`
- `.scratch/22-visibility-fragmentation/evidence/check-v2-unlabelled/draft.png`

The exact lists are recorded in their `report.txt` files. The V1 report lists remain preserved separately.

## Test outcomes and unresolved failures

The chosen V2 run counted **63 historical + 8 scratch = 71 total**. Three historical assertions failed; the other **68 passed**, and a filtered run excluding exactly those three passed 68. The three failures are retained, not waived:

1. `test_partial_occlusion_preserves_far_edges_and_background`: fragment area sum `6.0000004500000035` versus `6 ± 1e-8`, exposing the small EPS-band area contribution after aligning classification/interpolation thresholds.
2. `test_same_whole_strip_updates_visibility_in_two_cameras`: yaw-55 sum `.7599172533` versus `.7968 ± .01`. The independent oracle places coverage near `.749`; the old assertion remains a compatibility alarm, not a ground-truth target. It was neither deleted nor replaced with V2 output.
3. `test_card_depth_probes_and_visibility_do_not_depend_on_declaration_order`: the query is exactly on a source-triangle edge (`barycentric (0.5,0,0.5)`), with near depth `.224765` versus card depth 0, yet V2 also returns the support-card fragment at that query. This is a source-edge classification regression/ambiguity, not a depth tie; it must be reviewed.

V2's three new clipping/subtract tests passed. The preserved V1 scratch suite, explicitly run against V1, passed 5/5.

## Regression patch proposal and scope

`teaching/proposed-independent-oracle-tests.patch` proposes a new independent source-triangle sampled-coverage test plus the `EPS*x` source-subset witness. `git apply --check` passed as a dry run; the patch was **not applied**. It does not remove or replace the historical summed-area alarm, and it is not new-output gold. A fresh independent review of V2 is still required.

No canonical integration, full support matrix, learner, visual/art verdict, or S1a gate pass is claimed. No dependency/install, commit, baseline promotion, or source edits outside the scratch seam occurred.

## Commands run

- `.venv/bin/python .scratch/22-visibility-fragmentation/work/test_visibility_candidate_v2.py` — 3 passed, including canonical/V1 failing controls.
- V1-injected `.venv/bin/python` unittest runner for `test_visibility_candidate.py` — 5 passed.
- Candidate-V2-injected selected historical and scratch runner — **71 total** (63 historical + 8 scratch), 3 failures listed above.
- Same candidate-V2-injected runner excluding only those three failing historical methods — **68 passed**.
- `/usr/bin/time .venv/bin/python .scratch/22-visibility-fragmentation/work/visibility_oracle.py` — passed; 4.23 s, ~157,292 KB RSS; writes `evidence/oracle/visibility-oracle-v2.json`.
- `.venv/bin/python .scratch/22-visibility-fragmentation/work/visibility_subtract_audit.py` — passed; writes `evidence/oracle/subtract-eps-witness-v2.json`.
- `/usr/bin/time .venv/bin/python .scratch/22-visibility-fragmentation/work/study_candidate_v2.py` — passed; 11.80 s, ~103,336 KB RSS; source/canonical/V2 arch and minimal rasters, hashes, geometry and determinism saved.
- Both V2 `scripts/draw check` commands on labelled/unlabelled boards — passed; exact image lists above.
- `git apply --check .scratch/22-visibility-fragmentation/teaching/proposed-independent-oracle-tests.patch` — passed as dry-run only; not applied.
- Final source hashes/status/staged-path inspection — canonical and historical source hashes unchanged; inherited staged paths preserved.

## Handoff

Parent owns whether to retain or reject the scratch candidate and any later canonical/provenance changes. The immediate review should address the source-edge card overpaint, EPS-band overlap/area behavior, fragment-union boundary uncertainty, and the three historical alarm failures. No production merge is authorized by these results.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Implemented the approved candidate-only P1 correction and durable independent oracle under exercise22 scratch work/evidence. V1 module and unsuffixed V1 evidence are preserved; canonical source/tests remain unchanged."
    },
    {
      "id": "criterion-2",
      "status": "satisfied",
      "evidence": "The report identifies source and V1/V2 hashes, executable oracle and subtract audit results, exact candidate test counts and failures, geometry/topology/source-subset measurements, raster determinism, and exact draw-check image lists for independent review."
    }
  ],
  "changedFiles": [
    ".scratch/22-visibility-fragmentation/work/vector_visibility_candidate.py",
    ".scratch/22-visibility-fragmentation/work/vector_visibility_candidate_v1.py",
    ".scratch/22-visibility-fragmentation/work/study_candidate_v2.py",
    ".scratch/22-visibility-fragmentation/work/test_visibility_candidate_v2.py",
    ".scratch/22-visibility-fragmentation/work/visibility_oracle.py",
    ".scratch/22-visibility-fragmentation/work/visibility_subtract_audit.py",
    ".scratch/22-visibility-fragmentation/evidence/fine/study-v2.json",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-source-v2.svg",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-source-v2.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-canonical-v2.svg",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-canonical-v2.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-candidate-v2.svg",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-candidate-v2.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-candidate-v2-repeat.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/minimal-4x3-source-v2.svg",
    ".scratch/22-visibility-fragmentation/evidence/fine/minimal-4x3-source-v2.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/minimal-4x3-canonical-v2.svg",
    ".scratch/22-visibility-fragmentation/evidence/fine/minimal-4x3-canonical-v2.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/minimal-4x3-candidate-v2.svg",
    ".scratch/22-visibility-fragmentation/evidence/fine/minimal-4x3-candidate-v2.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-v2-labelled.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-v2-unlabelled.png",
    ".scratch/22-visibility-fragmentation/evidence/oracle/visibility-oracle-v2.json",
    ".scratch/22-visibility-fragmentation/evidence/oracle/subtract-eps-witness-v2.json",
    ".scratch/22-visibility-fragmentation/evidence/check-v2-labelled/report.txt",
    ".scratch/22-visibility-fragmentation/evidence/check-v2-labelled/draft.png",
    ".scratch/22-visibility-fragmentation/evidence/check-v2-unlabelled/report.txt",
    ".scratch/22-visibility-fragmentation/evidence/check-v2-unlabelled/draft.png",
    ".scratch/22-visibility-fragmentation/log/visibility-fragmentation-v2.md",
    ".scratch/22-visibility-fragmentation/log/visibility-fragmentation-v1-implementation.md",
    ".scratch/22-visibility-fragmentation/teaching/proposed-independent-oracle-tests.patch",
    "/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/5cc5aa2b-68ed-485f-ada4-5500c4efd8a0/s1a/visibility-fragmentation-implementation.md"
  ],
  "testsAddedOrUpdated": [
    ".scratch/22-visibility-fragmentation/work/test_visibility_candidate_v2.py"
  ],
  "commandsRun": [
    {
      "command": ".venv/bin/python .scratch/22-visibility-fragmentation/work/test_visibility_candidate_v2.py",
      "result": "passed",
      "summary": "3 P1 source-subset, signed/winding/scaled clipping and subtract safety tests passed; canonical/V1 controls fail as expected."
    },
    {
      "command": "V1-injected unittest runner for .scratch/22-visibility-fragmentation/work/test_visibility_candidate.py",
      "result": "passed",
      "summary": "Preserved V1 scratch suite passed 5/5."
    },
    {
      "command": "Candidate-V2-injected selected historical and scratch unittest runner",
      "result": "failed",
      "summary": "71 total = 63 historical + 8 scratch; 68 passed and 3 historical assertions failed as documented."
    },
    {
      "command": "Same candidate-V2-injected runner excluding exactly the three documented failing methods",
      "result": "passed",
      "summary": "68 tests passed."
    },
    {
      "command": "/usr/bin/time -f 'elapsed=%e sec maxrss=%M KB' .venv/bin/python .scratch/22-visibility-fragmentation/work/visibility_oracle.py",
      "result": "passed",
      "summary": "Both yaws, four resolutions and three specified phases completed in 4.23 sec, peak RSS about 157292 KB; wrote oracle JSON."
    },
    {
      "command": ".venv/bin/python .scratch/22-visibility-fragmentation/work/visibility_subtract_audit.py",
      "result": "passed",
      "summary": "Persisted EPS line/subtract geometry, source-subset and overlap witness."
    },
    {
      "command": "/usr/bin/time -f 'elapsed=%e sec maxrss=%M KB' .venv/bin/python .scratch/22-visibility-fragmentation/work/study_candidate_v2.py",
      "result": "passed",
      "summary": "11.80 sec, peak RSS about 103336 KB; V2 arch/minimal raw-canonical-candidate diagnostics and repeat render saved."
    },
    {
      "command": "scripts/draw check .scratch/22-visibility-fragmentation/evidence/fine/arch-v2-labelled.png --outdir .scratch/22-visibility-fragmentation/evidence/check-v2-labelled --pane 1500; scripts/draw check .scratch/22-visibility-fragmentation/evidence/fine/arch-v2-unlabelled.png --outdir .scratch/22-visibility-fragmentation/evidence/check-v2-unlabelled --pane 1500",
      "result": "passed",
      "summary": "Both reference-free reports list only their own draft.png image."
    },
    {
      "command": "git apply --check .scratch/22-visibility-fragmentation/teaching/proposed-independent-oracle-tests.patch",
      "result": "passed",
      "summary": "Proposed patch syntax checked only; patch was not applied."
    },
    {
      "command": "Final sha256sum scripts/vector_visibility.py scripts/tests/test_vector_visibility.py candidate V1/V2; git status --short; git diff --cached --name-only",
      "result": "passed",
      "summary": "Canonical/test hashes unchanged; V1 hash preserved; inherited staged .gitmodules/vendor remain untouched."
    }
  ],
  "validationOutput": [
    "Candidate V2 arch: raw 0, canonical 44, V2 0 nonmatching pixels in 8495 fixed safe interior samples; candidate repeat PNG SHA-256 is 3660a0300a3e05586b20a54d9421abe458ea1a833e0879dd0c3c6b0389059fca.",
    "Independent original-triangle oracle fractions span yaw0 .8667341-.8690753 and yaw55 .7489383-.7497473 across reported grids/phases; no source-edge/depth-tie oracle samples occurred.",
    "Yaw55 V2 fragment-union strict interior has about 1% sampled misses on candidate-fragment boundaries; boundary-inclusive union has no misses and 0-54 possible false positives, so continuous coverage remains unproven.",
    "Candidate V2 fragment sums remain above sampled oracle; subtract witness output pieces overlap and area sum is 1.5815 times subject area."
  ],
  "residualRisks": [
    "Three historical assertions fail under V2: small partial-occlusion area change, oblique ring sum compatibility alarm, and support-card fragment visible at a source-edge query with non-tied depth.",
    "The EPS-sensitive subtract witness returns overlapping pieces; area sums are not unions. CandidateV2 is not ready for production integration.",
    "The independent oracle is finite-sampled and boundary-inclusive results are ambiguous; no continuous coverage proof or visual/art gate is claimed.",
    "The existing bbox EPS broad-phase deadband remains; overlaps at or below that extent are not certified by the tiny-overlap test.",
    "Fresh independent review of the revised candidate remains required."
  ],
  "noStagedFiles": false,
  "diffSummary": "Preserved candidate V1 and its outputs; corrected only line_clip's inconsistent EPS crossing root in scratch candidate V2; added runnable independent oracle, subtract audit, V2 raster artifacts and an unapplied regression-test proposal.",
  "reviewFindings": [
    "Open/P1: test_card_depth_probes_and_visibility_do_not_depend_on_declaration_order returns support-card at a near ribbon query on a source edge despite a .224765 depth separation.",
    "Open: subtract_convex EPS witness returns pairwise overlapping polygons and area sum above subject area; no merge fix was authorized/applied.",
    "Open compatibility alarm: historical yaw55 sum expectation .7968 differs from V2 .7599173; independent oracle estimates geometric coverage near .749 and should not be replaced by a V2 gold value.",
    "No fresh independent reviewer has accepted V2; parent review is required."
  ],
  "manualNotes": "No canonical source/test changes. V1 module/evidence is preserved and copied prior handoff is under exercise22/log. Pre-existing staged .gitmodules and vendor/huashu-art-motion remain staged untouched; no task files were staged."
}
```
