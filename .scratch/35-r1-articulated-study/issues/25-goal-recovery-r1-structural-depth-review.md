# Issue 25 — independent structural/depth review of goal-recovery R1

**Opened:** 2026-10-13T11:49:35+08:00. **Owner:** independent validator (non-writer). **Disposition:** BLOCK for R1 acceptance; source-set structural implementation is substantially verified, but visual/art gate fails on the actual images and some full render reproduction checks did not complete under current CPU contention. No fixes made.

## Scope and immutable target

Reviewed only `.scratch/35-r1-articulated-study/evidence/goal-recovery-r1-v1/` frozen source/manifest/tests/grammar and the public R1 contract, issue 24 and relevant existing spatial adapters. Did not inspect sealed/worker session material. Source-set SHA-256 was independently recomputed as `c77499e3693d1d1c0aeda32ec0917565a621f55be90b7e5188328c4ba235690b`, matching the requested frozen revision. Manifest-listed source hashes and rendered hashes all matched current files. No source, image, or prior evidence was edited; no staging, environment, network, backend, or vendor change was made.

## Independent findings

### Confirmed bounded structural properties

- Grammar documents teacher-derived compact semantic families, purpose, inputs, generated contours, supports and variation. Runtime A consumes a small authored anchor set and generates bezier families; no dense observed boundary is handed to the renderer. Teacher crop metadata records source SHA `322ad77c0cfd28fa040c625c55c592a54b3052ac4bea61fc31d967d8acff81fb`, exact source rectangle `(500,320)-(900,800)`, 400x480/no resize; crop-registration and focus image were visually source-aligned. Teacher pixels appear limited to the observation side; A renderer accepts semantic data, B uses invented authored geometry.
- Inspected actual adapter/render path: generated controls are sampled/validated into component outlines; support mapping plus camera feeds `component_faces`; `visible_regions` emits filled regions, and `visible_segment_spans` clips boundary and semantic lines against shared-scene faces. `build_svg` uses these outputs for each authored shape and clips owner lines using the scene components. The actual B cases have hand, arm, dish, and depth supports; source computes per-case contact points on the generated dish contour, checks world-space equality and projected overlaps/depth crossing, declares forearm/palm and digit/prop attachments, and creates a dish-displaced unchanged-hand control. This is scene-specific evidence, not universal volume physics.
- The filled image sources and B panels were actually opened. B baseline and variant depict forearm/hand/dish visually, and the control visibly separates the dish. However, finger/dish boundary is cluttered by crossed-looking long tapered shapes and several apparent overlaps; the action is not visually unambiguous as a supported dish. Rendered sheet labels also show encoding mojibake (`SUPPORT Â·`, `CONTROL â€”`). A side-by-side crop shows source garment has a recognizable body/shoulder/sleeve/collar/bow; draft reads as a nearly rectangular torso block with a detached-looking tall side appendage and an overlaid bow, and does not convincingly reproduce the visible garment relations. These are actual-art failures, not structural test failures.

### Runnable checks and limits

- `PYTHONPATH=. /home/z/.venv/bin/pytest -p no:cacheprovider -q .scratch/35-r1-articulated-study/evidence/goal-recovery-r1-v1/test_goal_recovery_r1.py -k 'not complete_a_svg and not complete_b_baseline_svg'` — **passed**, 5 passed / 2 deselected, 59.84s. Covers compact authored shapes, actual-case B contact/variant/control deterministic semantic geometry, registered crop/reference absence declarations, adapter fill/line dataflow using a fixture, and bounds.
- Manifest source-set recomputation and all manifest source/render file SHA checks — **passed**, as above.
- Tried simultaneous complete A and B render tests with command deadlines of 110s; both timed out while unrelated high-CPU full test processes were running elsewhere. Retried A alone with 115s deadline; it also timed out. This is resource-limited/unverified evidence, not a test failure assertion. No further retries were made. The worker's claimed prior 57.08s / 51.83s results are recorded in issue 24 but were not reproducible in this review environment; do not treat the blocked commands as current independent reproduction PASS.
- Did not run `draw check`; did not assess image similarity metrics. Opened the frozen actual review images directly instead.

### Gate disposition

**BLOCK / NOT PASS for R1.** The actual A and B images fail the independent visual/art goal (A garment relations and shape; B hand/prop support readability). Structural depth/dataflow checks provide bounded positive evidence but cannot establish art acceptance. Full actual render reproducibility remained unverified in this environment after deadline-bound timeouts. Heldout compatibility/release and user feedback remain outside this review and open. No fix or repair was authorized/performed.

## Change protection and evidence

Review commands used deadline-bounded execution; every pytest command was capped at 120 seconds. At review end, preserve the observed unrelated dirty/staged state. No staging or commit performed; do not infer this review's lack of staged changes from the global index because pre-existing staged `.gitmodules` and vendor submodule entries existed at start. Scoped ticket/report are the only review artifacts added.
