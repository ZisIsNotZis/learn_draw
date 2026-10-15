# S1a visibility-fragmentation scratch follow-up — candidate V3

## Implemented, with prior revisions preserved

V3 adds the approved exact complementary partition inside `subtract_convex`, while leaving public tolerance-aware `line_clip(poly, fn, keep_positive=True)` behavior unchanged. A single private helper evaluates and interpolates the same signed halfspace boundary: public clipping uses the existing `-EPS`/`+EPS` thresholds; the two complementary subtraction clips use zero. `subtract_convex` skips only an **exact projected zero-length edge** as a vacuous constraint (`x/y` both exactly equal); it does not EPS-drop short nonzero edges, alter cutter geometry, clamp intersections, change depth/tie policy, or introduce a broader geometry framework.

V1/V2 remain preserved:

- Candidate V1 SHA-256 `ed07910a16000e82215b924d932c1859c4dc2da3b932f6d3740ccbb23cf08da6`.
- Candidate V2 SHA-256 `6faa70eb71457dba5c848b0f46da98be9aebe914261e1763885ed3dd2e0a6855`, copied to `work/vector_visibility_candidate_v2.py` before V3 edits. V2 logs, tests, `study-v2.json`, oracle-v2 JSONs, V2 SVG/PNG outputs and check bundles were not overwritten. The previous V2 output report was copied to `.scratch/22-visibility-fragmentation/log/visibility-fragmentation-v2-implementation.md` before updating this run's output artifact.
- Candidate V3 SHA-256 `5f289fed2ffe3d35740e0d3927b0a2ed168883d8785f4786746e6610e3112da7`.
- Canonical renderer/test hashes remain `6cea919d0c83b1c4ebb9b3ec3379854c910e2758610b449c036c25c9ce8e1ada` and `8977f31fb12e1f9a660f30866bd0ba271e4541f86d29cc091e32cd5a9cd4acd2`; neither was edited.

## Exact partition/source-geometry safety

`work/test_visibility_candidate_v3.py` has five tests. It compares public V3 `line_clip` outputs to V2, exercises the EPS-boundary source witness, and checks source containment, finite vertices, signs, winding, fixed scales `.5,1,2`, and intersection `t∈[0,1]`. It includes vertices exactly on both public EPS classification boundaries. Canonical/V1 remain failing controls for the source-external zero-root witness.

The exact partition tests cover translations, scales `.25,1,2,8`, reversed subject/cutter winding, source-subset vertices, pairwise positive-area overlaps, area conservation against an independently clipped convex intersection, coincident/touching geometry, and a tiny positive visible overlap above the existing bbox deadband. Repeated consecutive vertices, redundant collinear vertices, and an exact zero-length cutter edge are included; V2's vacuous zero edge reproduces overlapping whole-subject outside pieces, while V3 skips only that constraint. A real nonzero cutter edge of length `1e-8 < EPS`, with cutter area above EPS, remains active and conserves area. Coincident subtraction may return zero-area pieces, but their total area is zero and `_compound_path` serializes none.

For the V2 EPS-sensitive short-cutter witness, V3's source area is `5e-8`, exact intersection area `8.934676914607205e-9`, expected remainder `4.106532308539279e-8`, and output remainder `4.1065323085392863e-8`. Difference is `7.28e-23`, under the declared audit bound `1e-12`; source-barycentric excursion is `-6.7e-16`; no positive-area pairwise fragment overlap was measured. V2 on the same witness summed to `7.91e-8` and had two pairwise overlaps. Details: `evidence/oracle/subtract-eps-witness-v3.json`.

## Independent original-triangle oracle and geometry audit

`work/visibility_oracle_v3.py` preserves the runnable bbox-tiled barycentric max-depth oracle and separately measures fragment union, summed fragment area, topology, source-owner containment, source-edge ambiguity and depth ties for raw canonical/V1/V2/V3. The source-owner tags are geometry-only and do not change raster grouping. It ran N=128/256/512/1024 phase .5 and N=1024 phases .25/.75 for both yaws in **4.80 seconds**, peak RSS about **157,508 KB**. Sampling is not a continuous proof.

- Independent original-triangle observations: yaw 0 `.8667341–.8690753`; yaw 55 `.7489383–.7497473`. V3 summed fragment fractions are yaw 0 **`.8690584319`**, yaw 55 **`.7492076592`**, matching those sampled observations rather than the stale `.7968` yaw-55 sum expectation. This agreement is evidence, not a new output-gold test.
- V3 geometry-tagged output has no source-triangle vertex excursions beyond tolerance, and no nonconvex or self-intersecting positive fragments in either yaw view. Yaw 0 emits 310 strip fragments (181 zero area); yaw 55 emits 399 (217 zero area, 5 positive areas `<=1e-18`). Zero/tiny outputs are excluded from sampled union.
- Fragment-union sampling remains boundary-ambiguous: strict-interior coverage is below the oracle at many grid centers because they lie on output boundaries; boundary-inclusive coverage has no missed visible sample centers, but records about 9k possible false positives at yaw 0 and 24–25k at yaw 55 for N=1024. This is only a sampled boundary classification, not a continuous union proof.

## Fine arch, raster boundaries, determinism and draw checks

The V3 rerun uses the same fixed fine96x12 parent geometry/view/fit and the same 8,495 safe-interior mask. Raw source has **0**, canonical **44**, V3 **0** nonmatching base-fill samples. V3 has **0** background-like interior samples. Repeated candidate PNGs are byte-identical, SHA-256 `c7763f73fb86ef815ce7cafcacdd59b896481446c400971bc24c630219d07afc`. The 4x3 generated minimal mesh remains raw-pixel-identical. Historical Chromium exterior/tessellation/occlusion boundary tests passed, including the partial far-edge/background and source-edge body-card probes.

V3 labelled/unlabelled boards are `evidence/fine/arch-v3-labelled.png` and `arch-v3-unlabelled.png`. Reference-free draw-check reports list exactly:

- `.scratch/22-visibility-fragmentation/evidence/check-v3-labelled/draft.png`
- `.scratch/22-visibility-fragmentation/evidence/check-v3-unlabelled/draft.png`

The `report.txt` files contain the exact lists; no reference comparison was run.

## Proposed parent regression patch; not applied

`teaching/proposed-v3-tests-complete.patch` is a valid dry-run-checked, unapplied proposal. It preserves the existing two-camera fixture and its camera-change intent, removes obsolete exact fragment-SUM outputs, adds an analytically checkable source-partition assertion, and includes the independent original-triangle coverage test. It is not new-output gold and has not been applied to canonical tests. The earlier V1/V2 proposal artifacts remain unchanged.

## Tests and stale compatibility alarm

The final V3-injected chosen run counted **63 historical + 10 scratch = 73 total**. **72 passed; exactly one historical assertion failed:** `test_same_whole_strip_updates_visibility_in_two_cameras` expects yaw-55 summed fragment fraction `.7968 ± .01`; V3 returns `.7492076594`. The independent original-triangle oracle estimates `.7489383–.7497473`, so this remains the single stale-ground-truth compatibility alarm requested by the parent. The fixture's camera-change assertion (`abs(front-oblique) > .05`) still passes. No historical test was edited. Re-running with only that stale assertion excluded passed **72/72**.

All other selected historical checks pass under V3, including partial occlusion area and the body-card probe. The complete suite's only failure is the stale yaw-55 SUM assertion.

## Commands and limits

- `.venv/bin/python .scratch/22-visibility-fragmentation/work/test_visibility_candidate_v3.py` — 5 passed, including exact zero-edge, redundant-collinear and short nonzero-edge controls.
- Candidate V3-injected historical + scratch run — 73 total (`63 + 10`), only the stale `.7968` yaw-55 SUM assertion failed.
- Same V3-injected run excluding only that stale assertion — 72 passed.
- `/usr/bin/time .venv/bin/python .scratch/22-visibility-fragmentation/work/study_candidate_v3.py` — passed in 12.87 s, peak RSS ~103,324 KB; source/canonical/V3 arch and minimal SVG/PNG plus deterministic rerender persisted.
- `/usr/bin/time .venv/bin/python .scratch/22-visibility-fragmentation/work/visibility_oracle_v3.py` — passed in 4.80 s; persisted raw/canonical/V1/V2/V3 union and geometry measurements.
- `.venv/bin/python .scratch/22-visibility-fragmentation/work/visibility_subtract_audit_v3.py` — passed; persisted subtract partition audit.
- Both V3 labelled/unlabelled `scripts/draw check` commands — passed; exact report image lists above.
- `git apply --check .scratch/22-visibility-fragmentation/teaching/proposed-v3-tests-complete.patch` — passed as a dry run; not applied.
- Final hash/status inspection — HEAD `24693d4`; canonical source/test hashes unchanged; pre-existing staged `.gitmodules` and vendor paths preserved.

## Handoff

V3 remains isolated scratch candidate work. Parent owns any canonical integration, provenance/test updates, and independent review. No production merge, full camber matrix, learner, visual/art/readability verdict, or S1a pass is claimed. The finite sampled union-boundary ambiguity remains a disclosed limit.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Implemented V3 only in the isolated exercise22 scratch candidate: public EPS clipping remains byte-equivalent to V2; subtract_convex now partitions on a shared zero boundary and skips only exact projected zero-length edges. V1/V2 modules and outputs remain preserved; canonical code/tests were not edited."
    },
    {
      "id": "criterion-2",
      "status": "satisfied",
      "evidence": "The durable report and V3 evidence contain version hashes, runnable independent oracle/audit, exact area/source-subset/disjointness measurements, finite union-boundary limitations, repeated Chromium output, draw-check image lists and explicitly counted tests/failure."
    }
  ],
  "changedFiles": [
    ".scratch/22-visibility-fragmentation/work/vector_visibility_candidate.py",
    ".scratch/22-visibility-fragmentation/work/vector_visibility_candidate_v2.py",
    ".scratch/22-visibility-fragmentation/work/test_visibility_candidate_v3.py",
    ".scratch/22-visibility-fragmentation/work/study_candidate_v3.py",
    ".scratch/22-visibility-fragmentation/work/visibility_oracle_v3.py",
    ".scratch/22-visibility-fragmentation/work/visibility_subtract_audit_v3.py",
    ".scratch/22-visibility-fragmentation/evidence/fine/study-v3.json",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-source-v3.svg",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-source-v3.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-canonical-v3.svg",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-canonical-v3.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-candidate-v3.svg",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-candidate-v3.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-candidate-v3-repeat.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/minimal-4x3-source-v3.svg",
    ".scratch/22-visibility-fragmentation/evidence/fine/minimal-4x3-source-v3.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/minimal-4x3-canonical-v3.svg",
    ".scratch/22-visibility-fragmentation/evidence/fine/minimal-4x3-canonical-v3.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/minimal-4x3-candidate-v3.svg",
    ".scratch/22-visibility-fragmentation/evidence/fine/minimal-4x3-candidate-v3.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-v3-labelled.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-v3-unlabelled.png",
    ".scratch/22-visibility-fragmentation/evidence/oracle/visibility-oracle-v3.json",
    ".scratch/22-visibility-fragmentation/evidence/oracle/subtract-eps-witness-v3.json",
    ".scratch/22-visibility-fragmentation/evidence/check-v3-labelled/report.txt",
    ".scratch/22-visibility-fragmentation/evidence/check-v3-labelled/draft.png",
    ".scratch/22-visibility-fragmentation/evidence/check-v3-unlabelled/report.txt",
    ".scratch/22-visibility-fragmentation/evidence/check-v3-unlabelled/draft.png",
    ".scratch/22-visibility-fragmentation/log/visibility-fragmentation-v3.md",
    ".scratch/22-visibility-fragmentation/teaching/proposed-v3-regression-update.patch",
    ".scratch/22-visibility-fragmentation/teaching/proposed-v3-tests-complete.patch",
    ".scratch/22-visibility-fragmentation/log/visibility-fragmentation-v2-implementation.md",
    "/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/5cc5aa2b-68ed-485f-ada4-5500c4efd8a0/s1a/visibility-fragmentation-implementation.md"
  ],
  "testsAddedOrUpdated": [
    ".scratch/22-visibility-fragmentation/work/test_visibility_candidate_v3.py"
  ],
  "commandsRun": [
    {
      "command": ".venv/bin/python .scratch/22-visibility-fragmentation/work/test_visibility_candidate_v3.py",
      "result": "passed",
      "summary": "5 V3 exact-partition, zero-edge, redundant-collinear, short-real-edge and public-clip compatibility tests passed."
    },
    {
      "command": "Candidate-V3-injected selected historical + scratch unittest runner",
      "result": "failed",
      "summary": "73 total = 63 historical + 10 scratch; 72 passed. Only the expected stale yaw-55 summed-area assertion failed (.7492076594 vs .7968 +/- .01)."
    },
    {
      "command": "Same V3-injected runner excluding only test_same_whole_strip_updates_visibility_in_two_cameras",
      "result": "passed",
      "summary": "72 tests passed; partial area, source-edge card, boundary and self-occlusion checks pass."
    },
    {
      "command": "/usr/bin/time .venv/bin/python .scratch/22-visibility-fragmentation/work/study_candidate_v3.py",
      "result": "passed",
      "summary": "12.87 seconds, peak RSS about 103324 KB; raw/canonical/V3 arch and minimal Chromium images plus deterministic rerender saved."
    },
    {
      "command": "/usr/bin/time .venv/bin/python .scratch/22-visibility-fragmentation/work/visibility_oracle_v3.py",
      "result": "passed",
      "summary": "4.80 seconds, peak RSS about 157508 KB; both yaw grids and phases saved for canonical/V1/V2/V3."
    },
    {
      "command": ".venv/bin/python .scratch/22-visibility-fragmentation/work/visibility_subtract_audit_v3.py",
      "result": "passed",
      "summary": "Persisted V1/V2/V3 source subset, area conservation and pairwise overlap witness."
    },
    {
      "command": "V3 labelled and unlabelled scripts/draw check commands",
      "result": "passed",
      "summary": "Reference-free reports each list their corresponding V3 board draft.png only."
    },
    {
      "command": "git apply --check .scratch/22-visibility-fragmentation/teaching/proposed-v3-tests-complete.patch",
      "result": "passed",
      "summary": "Proposed canonical test patch dry-run passed; it was not applied."
    },
    {
      "command": "Final canonical/test/V1/V2/V3 sha256sum, git status --short and git diff --cached --name-only",
      "result": "passed",
      "summary": "Canonical/test hashes unchanged, all candidate revisions preserved, inherited staged paths unchanged."
    }
  ],
  "validationOutput": [
    "V3 exact subtract witness: expected 4.106532308539279e-8; observed 4.1065323085392863e-8; error 7.28e-23 under declared 1e-12 bound; no pairwise positive-area overlaps.",
    "Fine parent arch safe samples: raw 0, canonical 44, V3 0 nonmatching base-fill pixels among 8495; V3 background-like interior samples 0.",
    "Independent raw-triangle sum fractions: V3 yaw0 .8690584319 and yaw55 .7492076592; sampled oracle ranges yaw0 .8667341-.8690753 and yaw55 .7489383-.7497473.",
    "V3 output polygons are source-triangle-subset within tolerance, convex and simple; strict vs boundary-inclusive grid union remains ambiguous and is not presented as continuous proof."
  ],
  "residualRisks": [
    "The original yaw-55 .7968 summed-fragment expectation remains one stale-ground-truth historical failure; it was not edited or replaced with new-output gold.",
    "Finite union sampling has substantial fragment-boundary ambiguity; possible union observations are not continuous coverage proof.",
    "Fresh independent review of V3 and its unapplied proposed canonical test patch remains required.",
    "Pre-existing staged .gitmodules and vendor/huashu-art-motion remain staged and untouched."
  ],
  "noStagedFiles": false,
  "diffSummary": "Preserved V1/V2; V3 keeps public EPS line_clip behavior and uses a zero-boundary complementary partition for subtract_convex, skipping exact zero-length projected cutter edges only. Added partition/degeneracy tests and V3 oracle/raster evidence; no canonical integration.",
  "reviewFindings": [
    "Open compatibility alarm: test_same_whole_strip_updates_visibility_in_two_cameras still fails only the stale .7968 yaw-55 SUM expectation; independent original-triangle coverage is near .749.",
    "Open evidence limit: strict V3 fragment-union sample membership is boundary-ambiguous; boundary-inclusive coverage has no sampled misses but appreciable possible false positives.",
    "No fresh independent review has accepted V3; parent review remains required."
  ],
  "manualNotes": "V1/V2 modules, raster evidence, and reports are preserved. No canonical test/source edits, production merge, learner, full matrix, or art acceptance. No task files staged; existing staged user paths were protected."
}
```
