# V4 independent coverage gate correction

## Scope and disposition

Independent reviewer `78502f65` BLOCKed the V3 proposed oracle gate on a scale-dependent boundary predicate (P1) and missing near-policy accounting (P2). This bounded follow-up changes only a versioned oracle, its data/negative controls, a proposed unapplied test patch, and current-state records. V3 visibility kernel `5f289fed2ffe3d35740e0d3927b0a2ed168883d8785f4786746e6610e3112da7` and canonical renderer `6cea919d0c83b1c4ebb9b3ec3379854c910e2758610b449c036c25c9ce8e1ada` remain unchanged. Prior V1/V2/V3 audit artifacts are preserved.

## Corrected boundary and source-policy masks

V4 boundary membership uses Euclidean point-to-segment distance `<=1e-12` in centered screen-coordinate units, with projection checked against explicit endpoints/interior and exact zero-length edges skipped. This tolerance was predeclared and was not swept. It is used only by oracle membership, never clipping. Negative controls at edge lengths `1e-8` and `1e-14` demonstrate V3's old raw cross/dot rule accepts points `1e-6` away and an endpoint extension as “boundary”; V4 rejects those while retaining true edge/endpoint hits, translation/winding equivalents, and duplicate-edge handling. Three oracle-boundary scratch tests pass.

The source near-policy width is parsed from the pinned V3 `visible_fragments` tie-bias branch and combined with its public `line_clip` EPS: `1e-5+1e-7 = 1.0100000000000002e-5` depth units. V4 counts source edges, exact max-depth ties, cross-component near ties, same-component strip/body top-two near ties, source layer multiplicity, candidate fragment-edge samples, and their unique exclusions. Source policy is established before examining candidate results. Strict fragment interiors are compared bidirectionally with the nearest-depth raw-triangle oracle; boundary-inclusive membership is not used to claim success. Exact coplanar/declaration behavior remains a separate contract, and V4 explicitly does not model the full declaration result inside the near band.

## V4 data and measurements

`work/visibility_oracle_v4.py` (SHA-256 `4716422647afd4070cf0401b899f6f62b1acc743acb388e5d69ec16e4f8cc826`) uses the original projected triangles, barycentric interpolated depth, max z, centered coordinates, bbox tiling, N=128/256/512/1024 phase .5 plus N=1024 phases .25/.75. It stores canonical/V1/V2/V3 sums, topology/source subset, and per-grid FP/FN on the unambiguous domain in `evidence/oracle/visibility-oracle-v4.json` (SHA-256 `5f347ce42026a62b98302a337d76bfe4345aa77c49d7012e0326b75645871627`). The final run took **6.13 s**, peak RSS **206,272 KB**. No runtime warning occurred.

- Candidate V3 had **0 false positives and 0 false negatives** in every reported unambiguous sampled comparison, with **0 candidate fragment-boundary exclusions** at these grid points.
- Oracle source-edge and exact-depth-tie counts were zero on these grids. At yaw55 N=1024 phases .5 and .75, one cross-component source near-band sample each was excluded. Same-component strip/body top-two near-tie counts were zero. Strip layer overlap still occurs: at yaw55 N1024/.5, 27,866 samples had >=2 strip layers (maximum 6); these samples were counted separately from near-top ties.
- Summed strip fractions remain distinct: V3 yaw0 `.8690584319`, yaw55 `.7492076592`; independent sampled oracle ranges yaw0 `.8667341–.8690753`, yaw55 `.7489383–.7497473`. These are finite observations, not continuous/full-policy certification.

## Proposed regression gate

`work/test_visibility_oracle_gate_proposal.py` is a runnable scratch form (3 tests pass under V3 injection; SHA-256 `55f158f5aad70795124dd59c3cf9e204dea798e2b8ae224a6a38c5e9c4c0348b`). The unapplied canonical test patch `teaching/proposed-v4-oracle-gate.patch` has SHA-256 `5fc74940dc18987e9c19362df0f429efcc2a7116a1b807870353130243e154b0`. It adds the tiny-segment boundary negative controls, derives the near-policy band from resolver source, compares FP **and** FN only outside source-policy and strict fragment-boundary masks, and includes source-owner plus partition checks. It leaves the historical `.7968` sum assertion untouched; previous V3 proposal artifacts remain preserved. `git apply --check` passed; nothing was applied.

## Current review block and limits

The V3 kernel is read-only in this task. Historical `.7968` remains stale as independent geometric truth but is still a compatibility alarm. V4 does not waive the V3 independent-review BLOCK: the corrected oracle and proposed gate need a fresh independent review. No candidate integration, artwork verdict, learner, full camber matrix, or S1a acceptance is claimed.
