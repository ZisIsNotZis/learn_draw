# Ticket — WP03 reference-independent construction preparation leaf

## Contract / scope

Owner: implementation worker. Authorized by Main for one bounded, reference-independent preparation leaf only. Scope: a reusable semantic 2D two-segment IK plus tapered limb construction and named support-frame binding; tests and concise interface description. Exclusive outputs: `scripts/articulated_construction.py`, `scripts/tests/test_articulated_construction.py`, this ticket. Do not modify WP03 reserved scene/art/backend files, existing figure scaffold or other WP outputs. No rendering or reference access. Do not read sealed holdout. No staging, environment/runtime/network changes, commits, dependency installation, or edits to existing evidence/append-only files.

Inputs read-only: R1 `spec.md`, WP01 `evidence/method-study.md`, WP02 public `work/task-freeze.md`, `docs/drawing/spatial-model.md`, vendor MIT `scripts/engine/lib/rig.js` algorithms `R.ik2` and `R.taper`; existing target/Git state and applicable task routing/proof policy. Overall reference matching/visual acceptance remains blocked by WP02 independent match/license review and prior public-reference retry; this code does not waive WP02 or change R1 goals/cases. Holdout stays sealed.

## Interface and acceptance

Compact semantic parameters (support-local shoulder anchor, segment lengths, hand target, elbow branch, endpoint/mid widths) yield computed elbow/wrist, smooth taper contours, and palm attachment frame, all on a named support frame; no screen-space authored contour or art hand/fingers. Bind depth-support identity as an interface reference only; no engine integration or visibility/collision assertion. Enforce finite/nondegenerate input and explicit unreachable/reach-limit behavior. Contact is an authored future task input, not observation of R1 reference. Include accurate MIT method attribution/license note; no vendor art/coordinates.

Checks: reachable and out-of-reach; exact segment lengths; deterministic result; branch change; support/palm attachment identity; width ratio change; degeneracy; verify test coverage explicitly does not establish support-surface projection, collision, visual quality, artwork, legal clearance of reference, or R1 pass. One construction-rule hypothesis, one implementation/validation cycle, commands <=120s and 30-minute total. Independent code review required from Main.

## Initial state / boundary

Initial `git status --short --branch` observed `master...origin/master`, with pre-existing staged `.gitmodules` and two vendor adds; broad pre-existing dirty tracked modifications and untracked work including R1; all preserved. Target WP03 exact contract owns `.scratch/35-r1-articulated-study/work/scene.yaml` and `evidence/construction-self-check.md`; neither is touched. Public selected reference and source/crop remain untouched; sealed file not read. Policy methods at `/home/z/vibe/docs/policy/execution.md` Task routing and Proof and review read. `docs/policy/execution.md` link in target AGENTS is absent in target repo, resolved against governing parent instructions.

## Options / recommendation

Use a small standalone, pure Python semantic geometry leaf rather than expanding the legacy renderer or spatial backend. It can prove numerical construction semantics independent of unavailable reference match while preserving the support/depth engine boundary. No integration claim. The two remaining route comparisons are paper-only: (1) obtain a locally available, authorized actual reference via Main-approved source and rights evidence while preserving image.jpg imitation requirement; (2) separate MIT mechanism demonstration from the original-image imitation assignment, but only under an explicit changed contract and independent review—cannot silently remove the reference requirement. No third blind search.

## State / proof

Implemented one hypothesis: bounded 2-bone IK with elbow branch and tapered support-local contours, returned as semantic support-bound geometry. Interface: `scripts/articulated_construction.py` exposes immutable `Point`, `SupportFrame(support_id, depth_ref)`, `LimbParameters`, `LimbConstruction`, and `construct_limb()`. Invalid/degenerate/unreachable targets fail explicitly; support binding is opaque metadata for later adapter use and does not itself project onto or validate a 3D surface. Palm attachment is a tangent frame at wrist; no hand/finger art is supplied.

Tests: `scripts/tests/test_articulated_construction.py` exercises reachability, segment lengths, attachment/support identity, unreachable/degenerate/invalid branch, branch-side change, width change and deterministic output. `python -m unittest scripts.tests.test_articulated_construction` passed (5 tests). `git diff --check -- <three owned files>` passed. New implementation hashes: module `838464e55614a8cdf05874c3327f3ed410e655ea5781edd36706e778caad4702`; tests `32fc69b69463e1da727cf9680ab8d365456d8c345b1412b3acdad78a5c5d077a`; ticket `d8cbb32fc5d88d32606dff7a5d3884bb3ff63b1388feb8eb2baf736739c1fca2`.

Paper-only route comparison: (1) locally available, specifically authorized reference with provenance/rights review could satisfy the still-frozen reference condition; no source was selected, and the two observed TLS timeouts yielded zero candidates. (2) MIT mechanism demonstration separated from original-image imitation would require an explicit changed contract and independent review; it cannot silently delete R1's image.jpg imitation requirement. No third blind search performed.

No R1 milestone acceptance changed. Code/test PASS only establishes numeric construction behavior—not support-surface mapping/depth, collision, hand identity/art, any rendered work, reference/source/legal clearance, visual/reference matching, or WP03/R1 completion. WP02 independent source/action and license review remains pending, as do all visual, art, reference-match, holdout and later R1 gates. Main independent code review required. Staging is unchanged: pre-existing staged `.gitmodules`, `vendor/huashu-art-motion`, `vendor/huashu-design` only; no files staged by this task.
