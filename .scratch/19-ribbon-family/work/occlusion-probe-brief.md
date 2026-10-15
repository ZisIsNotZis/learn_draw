# Bounded S1a readability dependency probe

Parent decision after diagnosis 4f09fd69-2743-416b-85b4-74949a9ca90b: twist edge-on pinch is expected,
finite mesh may accentuate; crossing principal depth is correct but same-side fills lack a readable
occlusion contour. S1a not accepted. This is one small experimental line cue, NOT full S2 or a gate
waiver. Existing source, frozen cases, cameras and learner attempt are read-only.

Worker may add ONLY exercise work/occlusion_probe.py, work/test_occlusion_probe.py and evidence/probe/
plus append exercise log. No edits to ribbon_family.py, visibility engine, official docs, cases,
existing renders, learner output or teaching card. Reuse geometry APIs. No new dependencies/commits.

## Experiment

1. Preserve geometry/source hashes. Generate frozen crossing and twisted examples as before.
2. Crossing cue candidates come from the semantic local ribbon perimeter (v=-1/+1 and endpoints),
   NOT tessellation diagonals. Generate candidates over the ENTIRE component once. Project each
   perimeter segment, split by actual projected face intersections/depth equality as necessary,
   and keep only visible boundary portions masking a nonadjacent farther ribbon surface. Use source
   station/UV provenance to exclude the candidate's own adjacent support triangles. No manually typed
   u ranges, crossing coordinate box, near/far flags or clip-after-the-fact artwork patches. Stroke is
   an intentional diagnostic occlusion contour, not an edge expansion used to repair visibility.
   Any numeric tolerance is explained; no broad sample-only universal correctness claims.
3. Compare fill+stripe versus identical geometry with that generated cue. Small unlabelled side-by-
   side board and labelled diagnostic provenance companion; same framing and colour. Also include
   noncrossing teaching case where no occlusion cue should be manufactured, and another camera or
   depth sign reversal to show selected front boundary changes automatically. Do not change frozen
   inputs; reversal is an explicitly additional test, not replacement acceptance case.
4. Twist compare 40 vs128 intervals of SAME spec, SAME fixed oblique camera; locate facing sign zero
   numerically with support-frame convergence. Pinch must remain; only reduced faceting is tested.
   Do not smooth away a physically correct edge-on event or select another camera to evade it.
5. Tests: selected cue lies on semantic boundary; hidden boundary not painted; no internal mesh edges;
   noncrossing negative control; changed depth changes near boundary; original filled geometry equal;
   finite deterministic outputs. Include counterexample to ensure test fails on outlining all edges.
6. Run bounded probe tests, deterministic render/check both labelled/unlabelled comparison boards.
   Return exact report.txt lists and code/source/geometry hashes, point/line provenance and limits.
   No full unrelated suite reruns because production source remains untouched. Return small results,
   not prolonged tooling. If source API lacks sufficient provenance compute it from original rows/
   triangles; if sound clipping requires broad engine changes, stop with isolated case instead.

Parent will blind-review and determine whether this is evidence of a needed line-selection slice.
Do not claim full S1a passed or implement a universal line engine. Command deadlines <=120s; preserve
partial output and stop at run deadline. Do not change or judge the held-out learner attempt.
