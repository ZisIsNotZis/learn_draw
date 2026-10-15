# Ticket — V4 independent coverage gate correction

## Interpretation and authority

Implement only the P1/P2 oracle and proposed-gate corrections from the 2026-10-08 parent follow-up and reviewer `78502f65` BLOCK. Candidate V3 (`5f289fed…`) and canonical renderer (`6cea919d…`) are immutable. Preserve V1/V2/V3 code/evidence. This is diagnostic/test-gate work, not kernel repair, integration approval, or visual acceptance.

## Scope and split decision

One cohesive leaf: version the independent oracle, its sample-boundary and near-policy accounting, and an unapplied proposed regression patch; then update only the scratch V4 ticket/log/card and CURRENT STATE lines in `STATUS.md` and `.scratch/active-work.md`. No delegation/split: the code and evidence form one bounded, independently rerunnable gate. Canonical source/tests, historical `0.7968` assertion, old plans, images, learner, official design docs, support matrix and engine APIs remain read-only.

## Chosen interpretation/options

- Replace raw cross-product/dot boundary tolerance with Euclidean point-to-segment distance using a predeclared `1e-12` tolerance in centered-coordinate units, with explicit endpoint projections/bounds and zero-length-edge handling. The projection clamp/endpoint selection is only distance-to-segment geometry, never visibility intersection clipping. Negative controls use L=`1e-8` and `1e-14`, interior/outside points at distances well above tolerance, actual edge/endpoints, duplicates, translated and reversed polygons.
- Parse the numeric declaration tie bias from the V3 `visible_fragments` source and add its unchanged public clip EPS to derive the source-only near-policy band (`1.01e-5` for the pinned V3 source). Separately count cross-component top-layer near ties, same-component strip/body top-layer near ties, exact ties, and source-triangle edge cases. Build this mask before comparing any V3 result; do not enlarge it post hoc.
- Compare strict fragment interior to original-triangle nearest-depth truth bidirectionally (FP and FN) only outside source-policy and V3 fragment-boundary ambiguity; report all exclusions and ambiguity counts. No permissive boundary union can convert misses into a pass. Exact-coplanar declaration tests remain separate.
- Keep the historical summed-area assertion untouched. The V4 proposed patch is additive and leaves this stale compatibility alarm in place; no assertion replacement is proposed until independently accepted.

## Proof method / acceptance

Run the V4 oracle at the existing finite resolutions/phases with bbox tiling (deadline 180 seconds), query fixed candidate/topology/source-owner/conservation metrics for V3 only, and test boundary negative controls. Inspect false-positive AND false-negative counts, source-layer/near-tie counts, edge exclusions, and oracle/fragment boundary exclusions. Rerun only the requested old candidate geometry/safety suite if audit changes require it; do not redraw the camber matrix or run a learner. Stop/report if any unambiguous mismatch remains. Reviewer block remains until new oracle output and proposed patch receive fresh independent review.

## Durable artifacts planned

`work/visibility_oracle_v4.py`, an oracle boundary test, `evidence/oracle/visibility-oracle-v4.json`, a V4 unapplied patch, and scratch V4 ticket/log/card updates. Preserve existing V3 JSONs, reports and patch artifacts byte-for-byte. Record command runtimes, source hashes, and exact residuals.

## Outcome / current status

Completed without changing candidate V3 or canonical source. Final V4 oracle derives the tie bias by parsing the pinned V3 `visible_fragments` source and adds public EPS; run time 6.13s (max RSS ~206272 KB). Boundary controls pass at L=1e-8 and 1e-14. N=128/256/512/1024 phase .5 and N=1024 phases .25/.75 show bidirectional 0 FP/0 FN on every unambiguous sampled domain. One yaw55 cross-component near-policy sample is excluded at each N1024 phase .5/.75; no source-edge, exact-depth tie, same-component top-layer near tie, or candidate-fragment-boundary sample is excluded on these grids. Source layer overlaps still occur (strip samples with >=2 layers grow to 27866 at yaw55 N1024/.5; max depth layers 6); the near-top masks are separately zero. These finite samples do not certify full declaration-order behavior inside the source-derived 1.0100000000000002e-5 band or continuous coverage.

The corrected proposed gate patch is `.scratch/22-visibility-fragmentation/teaching/proposed-v4-oracle-gate.patch` (SHA `5fc74940dc18987e9c19362df0f429efcc2a7116a1b807870353130243e154b0`); scratch source is `.scratch/22-visibility-fragmentation/work/test_visibility_oracle_gate_proposal.py` (SHA `55f158f5aad70795124dd59c3cf9e204dea798e2b8ae224a6a38c5e9c4c0348b`). Three proposal tests pass and `git apply --check` passed. Patch is unapplied; historical `.7968` assertion is untouched. Oracle script SHA `4716422647afd4070cf0401b899f6f62b1acc743acb388e5d69ec16e4f8cc826`, data SHA `5f347ce42026a62b98302a337d76bfe4345aa77c49d7012e0326b75645871627`. Independent re-review remains required; current disposition is BLOCK pending V4 review. V3 kernel/canonical hashes remain pinned.
