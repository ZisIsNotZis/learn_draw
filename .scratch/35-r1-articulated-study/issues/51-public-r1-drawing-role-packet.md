# Issue 51 — public R1 reference-free drawing role packet

**Opened:** 2026-10-14T01:50:39+08:00. **Owner:** assigned repo writer; Main retains creator authorization, sealed-text release, and user presentation. **Status:** public preparation ready for independent technical packet review; not creator release/readiness PASS. No new drawing milestone, artwork, rendering, or sealed access.

## Objective, requirements, acceptance

Prepare one public creator role/card and generic callable spatial API guide for a genuinely new, text-only reference-free R1 drawing. Keep the role distinct from the old S1a learner, teacher, evaluator, and Ex28 owner. Preserve the clarified gate relationship: Ex28's four-question worksheet, neutral board, and serialized receipt are old S1a prerequisites only—not extra prerequisites for this distinct R1 artwork, and not waived for S1a. S1a/transfer remain OPEN and old learner dispatch unauthorized. Heldout task-level compatibility is confirmed by the independent test-owner report, but release/readiness remains blocked. Only Main may separately authorize a fresh creator and release the sealed brief.

Acceptance: public card contains no sealed prompt or prompt hints; creator inputs are limited to card, generic API, and separately released text brief; explicitly prohibits reference image/teacher/raster/A-B/old Ex28 access and code-quiz substitution; method explains semantic local components, real support/world mapping, depth-computed fills, separate semantic line art, named/legal contact, and generator-coordinate discipline. API docs expose only existing validated general APIs and one neutral geometry signature; no study-case/preset, source constants, backend, or renderer expansion. No output writer wrapper is needed because the existing call surface is directly callable and no source/runtime change is authorized. No actual drawing is produced; qualified actual-image review remains a later gate.

## Inputs, scope and exclusions

Authority/input: task direction; `.scratch/35-r1-articulated-study/spec.md`; public `work/task-freeze.md`; independent compatibility report `/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/8789947a-c874-4de8-b431-b071bc62a071/r1/test-owner-compatibility.md`; architecture `docs/drawing/spatial-model.md`; current public APIs `scripts/articulated_construction.py`, `scripts/articulated_line_visibility.py`, and `scripts/vector_visibility.py`.

Sealed file, image.jpg, teacher materials, A/B output/source/parameters/pose presets, Ex28 materials, old learner, raster/artifacts, environment changes, network, native image generation, backend/source expansion, code quiz, candidate rendering, staging and committing are excluded. No source modifications or tests additions were made; direct existing APIs are documented rather than wrapped. Existing dirty/staged work was present before this issue; preserve it.

## Changes made

- `teaching/r1-reference-free-method/public-role-card.md`: public role boundary, gate distinctions, method, prohibited inputs, and future gates.
- `teaching/r1-reference-free-method/generic-spatial-api.md`: callable existing API inventory, neutral geometry signature, generic generator/point rules, and limits. Does not expose frozen case builder.
- `STATUS.md`: concise current-fact pointer clarifying role/release and preserving all gates.

## Proof and limits

Compatibility source says task-level PASS but release/readiness BLOCKED. Static source inspection confirmed direct callable types/functions: `Point`, `Component`, `SupportFrame`, `Camera`, `construct_limb`, `triangulate_polygon`, `component_faces`, `visible_scene_regions`, `visible_segment_spans`; `build_study_case` is explicitly excluded. A Python smoke check imported the documented API and projected the neutral polygon to one support-bound face and one visible fill; deterministic function path passed. No new helper/source means no tests added. `git diff --check -- STATUS.md` passed; a Python trailing-whitespace scan of all four scoped files passed. Grep confirmed key boundaries and STATUS pointer. `git diff --cached --name-only` remains the pre-existing `.gitmodules`, `vendor/huashu-art-motion`, `vendor/huashu-design`; this task staged nothing. No drawing, render, sealed read, independent packet review, or creator dispatch occurred. Preparation is NOT a readiness/creator/art/R1 PASS; independent technical packet review remains pending before source/task freeze; Main separately owns fresh creator authorization and sealed-text release. Actual image must later receive qualified review. No stage/commit.
