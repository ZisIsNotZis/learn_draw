# R1 WP01 — method/source selection ticket

## Contract, interpretation, ownership

**Objective:** execute only R1-01 in `.scratch/35-r1-articulated-study/spec.md`: grounded, bounded selection of vendor methods directly applicable to WP03's shoulder/torso/bent-arm/hand/collar-contact construction; identify support/depth compatibility, local Ex32 limitation, predicted change/failure, and explicit non-transfers.

**Owner:** method-study worker (single writer). **Status:** done; WP artifact awaits the contract's fresh source reviewer and R1 integrator approval before WP03 use.

**Exclusive outputs:** `.scratch/35-r1-articulated-study/evidence/method-study.md` and this WP01 ticket. No drawing/code/vendor execution, no WP02 or holdout access, no roadmap/SSOT edits, no WP03+ work. Preserve all pre-existing dirty/staged state, vendor, `.gitmodules`, `.agents`, and evidence; no staging/commit.

**Inputs:** frozen R1 contract/spec, current roadmap/vendor-learning-map/spatial-model, Ex32 prior-art source, enumerated vendor sources specified in WP01. WP01/WP02 may run independently; downstream WP03 waits for method card and WP02 freeze. Maximum deep source units three: selected implementation `rig.js`, contrast implementation `rig_huashu.js`, real-use example `09_postimp.js`. Specified refs/tests are only bounded corroborating checks; vendor tests searched for applicability and found no rig/visibility evidence. Do not assert references alone establish migration.

## Acceptance/proof plan

- Identify source path and symbol for each adopted/isolate/exclude decision and bind vendor revision/hash.
- Explicitly map the proposed semantic IK anchors, taper construction and pose-vs-renderer separation to shoulder, torso, elbow/wrist/palm/fingers, sleeve/cuff and collar contact.
- Preserve project local-art-on-supports and depth-derived visibility; identify exact conflict with vendor flat painter order/Canvas visible-line filtering.
- Compare against Ex32's old scaffold component rotation and state what new rule it cannot demonstrate.
- State candidate failure modes, excluded mechanisms/source families, provisional status, and whether tests/negative-case evidence apply.
- Verify source links/hashes, scoped document whitespace, exact output ownership and no staged changes. No visual/render/runtime acceptance is claimed.

## Baseline / decisions / budget

Before writing, inspected target contract, applicable execution Task routing/Product decisions/Proof and review, current roadmap/map/spatial model, required source inventory, git state. Project HEAD `24693d4b764755165509fc206695ebca03ee44fe`; vendor HEAD `f178bd7754a71d6d399473af1501634548efa6cb`. At baseline the exercise directory had the contract only; working tree contained existing unrelated staged and unstaged changes. These remain untouched.

Selected a compact method hypothesis: adapt goal-driven 2-bone IK + named anchors and taper into spatial support-local constructions; isolate renderer/line responsibility from pose while rejecting painter order / pixel-diff visibility. Selection remains provisional; not a claim that hand-first is uniquely optimal or that vendor method has been learned locally. Excluded stretch, rigidPose, hooks as an API, motion and unrelated source families. Budget: deep-dive cap 3 primary source units, no tests executed, no vendor scripts/services, no recursion, each command <=120s.

## Results and evidence

Primary output: `../evidence/method-study.md`. It contains concrete symbol-level mapping, non-transfers, failures, Ex32 contrast, test negative-case applicability and SHA-256/source revision evidence. Tested contract source links against this checkout by opening exact files. `tests/test_capabilities.py` and `tests/test_images.py` do not exercise rig/IK/taper/depth; source search found no applicable rig tests. This is source study only, not a runtime check.

## Revision-bound checks / current state

- `git -C vendor/huashu-art-motion rev-parse HEAD` → `f178bd7754a71d6d399473af1501634548efa6cb`.
- `sha256sum` of seven named contract vendor files → recorded in method card.
- Tests added/updated: none; tests run: none (inapplicable to this documentary selection and vendor execution prohibited).
- Pending: independent fresh source reviewer verifies grounding and no painter-order/depth substitution; R1 integrator approves card. This worker does not mark either complete.
- Parent next step: route independent WP01 review/integration approval; may route WP02 independently. WP03 must await WP01+WP02 acceptance.
