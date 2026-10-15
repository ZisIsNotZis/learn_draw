# R1 integrated reset contract — single-owner handoff

**Status: contract preparation complete; pending independent feasibility review, not implementation-ready.** Main authorized one final bounded integration-reset plan-preparation, preserving the R1 artwork goal and gates. This ticket records approval and the strict start gate; it does not authorize code/render yet.

## Decision and integration rationale

Retain R1 A observed-part imitation plus B original arm/hand/prop mechanism-transfer artwork, heldout gate and all visual/structural/user acceptance. Replace the stale pattern of separate demo leaves/repeated continuation with one WP04 owner integrating both tracks in a single fresh revision. The audit at [`issue 20`](20-execution-loop-audit.md) identified the concrete bypass: demonstration-specific spatial code existed, but no mandatory integrated import/dataflow boundary and image-review rejection check existed. Therefore structural integration acceptance now precedes image review. No claim that all approaches failed; no further budget roll-forward.

## Contract artifacts and paths

- Detailed executable contract/spec: [`integrated-reset-r1-v1/spec.md`](../evidence/integrated-reset-r1-v1/spec.md)
- WP04 writer handoff: [`integrated-reset-r1-v1/handoff.md`](../evidence/integrated-reset-r1-v1/handoff.md)
- Sole future implementation/evidence path, currently planning-only: `.scratch/35-r1-articulated-study/evidence/integrated-reset-r1-v1/`

Path collision check before writing confirmed the future directory, revision-local spec/handoff targets, and issues 20/21 absent. No code/art/render/raw evidence changed. The historical ticket 20 was archived verbatim from its real external source; it had not existed in repo before this run because the prior output-path config failed to land it here. See its provenance header.

## Interface fact and feasibility gate

Inspected actual module definitions in `evidence/vendor-smooth-spatial/smooth_spatial.py`: general public curve functions `cubic_segments`, `evaluate`, `validate_closed_contour`, and `sample_closed_curve` exist; `build_components`, `visible_boundary_spans`, and SVG build/emission use fixed example constants/scenes. Therefore it is inaccurate to call the whole module a general-purpose scene API. The contract constrains the consumer to the real sampled-curve/guard functions plus existing `scripts.articulated_construction` support/world/camera/component/depth APIs, `scripts.articulated_line_visibility` line clipping, and `scripts.vector_visibility` fill visibility as needed. No new renderer/engine and no edits to historical smooth module. A revision-local thin composition adapter is proposed, but remains subject to fresh independent proof that both emitted fills and lines actually derive from those APIs and validated geometry. The reviewer must report feasible or identify exact interface blocker before any writer start.

## Frozen execution envelope

- Exactly one writer owns complete cohesive A+B integration in the named new revision. No new standalone demo leaves or parallel implementation.
- Max 90 minutes for implementation, integration/dataflow tests, static pipeline, one render, and self-check inclusive. No rolling extension.
- At most one evidence-backed P1 repair: max 20 minutes inclusive tests. Fresh independent visual review only after structural acceptance, max 15 minutes; any follow-up review/repair must fit existing cap or stop blocked.
- Each command timeout max 120 seconds. No automatic continuation. Halt and report BLOCKED/UNVERIFIED on time, interface or acceptance failure.
- Fresh independent feasibility review is now recorded below. Fresh visual reviewer sees only image paths after structural PASS. Keep sealed heldout inaccessible, do not stage/commit.

## Planning-input acceptance and integrated implementation execution

Fresh independent feasibility review: [`integrated-reset-feasibility-review.md`](/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/442e7d7b-0bc7-4712-b57a-b264f9bf719a/r1/integrated-reset-feasibility-review.md). Its verdict is **PASS for feasibility only**: it confirms a thin revision-local adapter can compose the named sampling, support, depth-fill, and line APIs. The review explicitly does not pass implementation/dataflow, art, heldout or user gates. This planning input is accepted as feasibility evidence only, not art acceptance.

- **Interpretation/scope:** implement the complete cohesive A observed-context garment study and B original arm/hand/prop baseline, meaningful variant and near-miss with revision-local adapter, tests, renders/check evidence and manifest. Preserve all product, geometry, depth, heldout and user gates. No standalone demo, recursive delegation, new hypotheses, edits to existing engine/evidence/vendor files, target access from renderer, sealed-task access, stage or commit.
- **Decomposition:** one integrated writer leaf owns all A+B candidate and revision-local glue/tests/artifacts; split is not authorized or needed. If actual dataflow cannot pass mandatory pre-render gates, stop blocked rather than reroute around the contract.
- **Baseline:** this worktree was already extensively dirty/staged; preserve all unrelated state. The revision directory initially contained only `spec.md` and `handoff.md`. Root `image.jpg` SHA-256 `322ad77c0cfd28fa040c625c55c592a54b3052ac4bea61fc31d967d8acff81fb` and recomputed crop `(500,320,900,800)` dimensions 400x480 / PNG SHA-256 `52e01f5e75e5d98fcd9a0a4c63be91ed09b8a18ca0f62e7e0348a021b2dd87d` match the frozen provenance.
- **Authority and limits:** execute one approved writer phase, max 90 minutes total, every command <=120 seconds, no rolling extension or automatic continuation. Render only after pre-render checks. Structural/visual review remain separate gates; feasibility is neither.
- **Acceptance record:** feasibility review and planning inputs are accepted as described above. No implementation PASS, art/visual verdict, R1 PASS, heldout clearance or user approval is claimed.

## Integrated writer checkpoint — candidate and self-check complete

All new implementation, tests, crop, renders, and check bundles are confined to [`integrated-reset-r1-v1/`](../evidence/integrated-reset-r1-v1/). The final artifact/index is [`manifest.json`](../evidence/integrated-reset-r1-v1/manifest.json), with dependency and artifact SHA-256 values, dataflow/test evidence, runtime isolation, source/crop registration, B semantic contact/gap/collision-range checks, matching output/crop viewport, command records, and explicit remaining review gates. The recorded writer window is 2706 seconds including inspection/implementation/tests/render/check (<=90 minutes); per-command timing was not captured for most commands and is marked unknown rather than estimated. Pre-existing staged paths remain untouched; no stage/commit was performed.

- A actual SVG/PNG: `../evidence/integrated-reset-r1-v1/rendered/A-observed-garment.svg` and `.png`; A draw-check report image list is in `../evidence/integrated-reset-r1-v1/checks/A/report.txt`.
- B actual baseline/variant/near-miss panel SVG/PNG: `../evidence/integrated-reset-r1-v1/rendered/B-original-action.svg` and `.png`; reference-free report image list is in `../evidence/integrated-reset-r1-v1/checks/B/report.txt`.
- Final source-test run: eight integrated tests passed. Both draw-check bundles were produced; metrics are alarms only. Crop source and PNG digests match frozen task provenance.
- **Remaining:** independent structural/dataflow acceptance has not been performed; therefore no image-only visual reviewer has been sent these images. Independent art, support/contact/collision and depth gates, sealed heldout compatibility/release/artwork, user feedback, and final integrity acceptance remain open. This checkpoint is a candidate/self-check delivery only—not R1, art, or visual PASS.
