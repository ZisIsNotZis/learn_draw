# Visibility fragmentation scratch follow-up — candidate V2

## Revision/provenance boundary

Candidate V1 is preserved byte-for-byte at `work/vector_visibility_candidate_v1.py` with SHA-256 `ed07910a16000e82215b924d932c1859c4dc2da3b932f6d3740ccbb23cf08da6`. Its original study code/results remain `work/study.py`, `evidence/fine/study.json`, and the unsuffixed V1 arch/minimal/diagnostic outputs. Candidate V2 is the same isolated scratch module plus the approved `line_clip` interpolation correction; V2 SHA-256 `6faa70eb71457dba5c848b0f46da98be9aebe914261e1763885ed3dd2e0a6855`. Canonical `scripts/vector_visibility.py` remains `6cea919d...` unchanged. No canonical source or test was edited.

## P1 interpolation correction

Both canonical and V1 classify a positive clip with `fn >= -EPS` (negative: `fn <= EPS`) but locate crossings at `fn == 0`. The persisted EPS-times-x witness uses source triangle `[(-.8,0),(-1.2,1),(-.8,2)]` and `fn=EPS*x`; old interpolation emits `(0,-2)` and `(0,4)`, outside the source hull. V2 shifts the signed values used for classification and interpolation together: `g=fn+EPS` for keep-positive and `g=fn-EPS` for keep-negative; intersection is `g==0`. It does not clamp `t`, alter depth or tie policy, or sweep EPS. Scratch tests check finite outputs, convex-source membership, edge interpolation `t∈[0,1]`, both clip signs, reversed winding and fixed signed-function scales `.5,1,2`; canonical and V1 are failing controls across those cases.

The same short-edge `subtract_convex` witness was measured separately. V1 outputs source-external vertices (minimum source barycentric weight `-0.6667`); V2 outputs are finite and remain in the subject hull (minimum `-5.6e-16`). V2 also exposes a residual: for a subject area `5e-8`, its three outside polygons sum to `7.9077e-8` (1.5815× source area) and two returned piece pairs intersect with areas `2.7804e-8` and `1.2729e-9`. This diagnostic overlap is recorded in `evidence/oracle/subtract-eps-witness-v2.json`; the patch intentionally adds no merge/dedup/tolerance mechanism. Sum must not be read as union.

## Persisted independent original-triangle depth/coverage oracle

`work/visibility_oracle.py` is now a rerunnable, independent, bbox-tiled barycentric max-depth oracle for the original `ring_and_occluder` projected triangles. It centers coordinates at `(200,150)`, uses depth max, records source-triangle edge/depth-tie ambiguities, computes resolver fragment union separately from summed polygon area, reports strict and sample-boundary-inclusive memberships, and attaches source-owner indices only for geometry audit (no raster grouping change). It skips zero/tiny polygons and zero-length edges for union; topology/source-subset measures are reported separately. It ran both yaws at N=128,256,512,1024 phase .5 plus N=1024 phases .25/.75 in 4.23 seconds (max RSS ~157,292 KB). This is sampled evidence—not a continuous coverage proof.

- Oracle observations: yaw 0 `.8667341` at N128, `.8688997` N256, `.8690314` N512, `.8689985` N1024/.5; the N1024 phase range is `.8690680–.8690753`. Yaw 55: `.7497473` N128, `.7492057` N256, `.7495848` N512, `.7492159` N1024/.5; the N1024 phase range is `.7489383–.7494460`. No source-edge or depth-tie sample was detected on these grids.
- V2 summed strip-fragment fractions are `.8759310` (yaw0) and `.7542604` (yaw55); these are explicitly not union truth. The centered V2 yaw55 sum is still about `.0045–.0053` above the oracle observations. V2 fragments in these tests are finite, convex/simple, and source-triangle-subset within numeric tolerance.
- V2 yaw0 strict fragment-union sample coverage matches all tested oracle centers exactly (no sampled FP/FN). At yaw55, strict interior-only union classifies about `.7390–.7404` raw-area fraction and misses ~0.99–1.03% of oracle-visible centers, but these centers are on candidate fragment boundaries: possible union including sampled boundaries has zero false negatives and 0–54 false positives among ~221k visible samples. This does not prove continuous coverage; edge membership is ambiguous.
- The old `.7968 ± .01` yaw55 summed-area assertion remains in the historical suite as a compatibility alarm, not a geometric truth target. It was not changed or deleted. V2's centered sum is `.7542604`; do not replace the old expected value with V2's output.

## Fine arch / minimized Chromium rerun

`work/study_candidate_v2.py` wrote V2-suffixed source/canonical/candidate SVG and PNGs and `evidence/fine/study-v2.json`; V1 files remain intact. On the same fixed fine96x12 parent arch and 8,495 safe interior samples: raw source 0 nonmatching, canonical 44, V2 0. V2 repeat PNG is byte-identical. V2 emits 9,757 fragments (2,739 exactly zero area, 2,493 positive fragments <=1e-10, 2,512 <=1e-7) and 7,018 serialized paths. The small computed 4x3 mesh remains 24 V2 fragments and raw-identical Chromium pixels; canonical retains its 24 zero-area outputs and four last-row/column partial pixels. These are bounded raster observations only.

V2 labelled/unlabelled boards are `evidence/fine/arch-v2-labelled.png` and `arch-v2-unlabelled.png`. Reference-free reports are `evidence/check-v2-labelled/report.txt` and `evidence/check-v2-unlabelled/report.txt`; each exact image list contains only its `draft.png`.

## Candidate V2 safety and historical tests

Candidate V2 scratch tests: 3 passed. The preserved V1-only candidate regression file, run with V1 explicitly injected, still passes all 5. The chosen V2 run explicitly counted **63 historical + 8 scratch = 71 total**. Three historical assertions failed; 68 passed, and an explicit rerun excluding only those three passed 68:

1. `test_partial_occlusion_preserves_far_edges_and_background`: summed area `6.00000045` versus `6 ± 1e-8`; this shows EPS-band area contribution after matching intersection thresholds.
2. `test_same_whole_strip_updates_visibility_in_two_cameras`: yaw-55 summed fraction `.7599173` versus `.7968 ± .01`. Independent original-triangle samples put coverage near `.749`; keep the old test as a compatibility alarm, not a truth oracle.
3. `test_card_depth_probes_and_visibility_do_not_depend_on_declaration_order`: at the fixture query the near source triangle has barycentric `(0.5,0,0.5)` (exact source-edge sample) and depth `.224765` versus card depth 0, but V2 also returns a support-card fragment at that point. This is a source-edge coverage ambiguity/regression; it must remain visible in the handoff, not be waived as a tie.

No canonical tests were altered. `.scratch/22-visibility-fragmentation/teaching/proposed-independent-oracle-tests.patch` proposes (but does not apply) source-subset and one-sided raw-triangle sampled-union regression tests. It retains the historical summed-area assertion separately; it is not an output-gold replacement.

## Commands and evidence

- `.venv/bin/python work/test_visibility_candidate_v2.py`: 3 passed.
- V1 test invocation with `vector_visibility_candidate_v1.py` injected: 5 passed.
- V2 chosen-suite invocation: 71 total = 63 historical + 8 scratch; 3 failures above. Filtered invocation excluding exactly those 3: 68 passed.
- `/usr/bin/time .venv/bin/python work/visibility_oracle.py`: passed in 4.23 s, ~157 MB RSS; saved `evidence/oracle/visibility-oracle-v2.json`.
- `.venv/bin/python work/visibility_subtract_audit.py`: passed; saved `evidence/oracle/subtract-eps-witness-v2.json`.
- `/usr/bin/time .venv/bin/python work/study_candidate_v2.py`: passed in 11.80 s, ~103 MB RSS; V2 raw/canonical/candidate images and repeat hash saved.
- V2 `scripts/draw check` labelled and unlabelled board runs passed; exact lists are in their report files.
- `git apply --check teaching/proposed-independent-oracle-tests.patch`: passed as a dry-run only; patch was not applied.

## Disposition

This is still candidate-only scratch work, not a production integration. The P1 source-external interpolation is corrected in V2, but the observed subtract piece overlap, historical area alarm, and source-edge card fragment must be reviewed. Independent oracle misses are reported with boundary ambiguity, and finite sampling is not continuous proof. No source/test merge, full support matrix, learner, visual/art verdict, or S1a pass is claimed. Parent/reviewer owns the next decision.
