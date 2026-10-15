# Issue 41 — bounded teacher-landmark numeric cross-check

**Opened:** 2026-10-13T15:49:07+08:00. **Owner:** single writer. **Status:** audit complete; semantic re-review required for disputed N1. **Authority:** Main authorized limited evidence re-check only; no drawing, refit, native generation, teacher-source edits, sealed/final renderer/B inspection, or changes to user gates. Preserve issue 37 PASS and original teacher package as historical evidence; audit neither declares all teacher work failed nor endorses N1.

## Objective and acceptance

Cross-check all 19 teacher landmark crop/source mappings and exact source pixels; report point RGB and finite local patches, distinguish sampled interior points from edge/seam/detail/contact placements, and flag semantic contradictions without using color alone to assign objects. Provide pristine crop, unprompted numbered crosshair and raw patch image boards, machine-readable data, reproducible script and provenance. Update current status/owner without changing the R1/user gate. No modifications to original teacher or source material.

## Inputs and outcome

Read issue 40 and only teacher-only `landmarks.csv`, `provenance.json`, `topology-map.md`, registered crop, overlay-generation script, and `image.jpg`. Their hashes and actual audit results are in `evidence/A-teacher-landmark-audit-v1/`. Exact registered crop mapping passed across all 192,000 pixels and all 19 landmarks. N1 crop `(232,47)`, source `(732,367)`, point `#3877b2`, with local patch context contradicts its “visible-neck-skin interior” label. This substantiates a specific coordinate/semantic dispute only; color does not establish the alternative identity and no replacement skin point is asserted. Other points have typed placement notes in `findings.md`; notably TL1 stays an unresolved contact/overlap, not a proven endpoint.

## Deliverables and checks

- `evidence/A-teacher-landmark-audit-v1/audit_landmarks.py` reproduces exact registration checks, numeric per-point audit, individual raw patches, pristine crop copy, numbered crosshair crop, and unlabeled-by-answer zoom board.
- `numeric-audit.json` and `.csv`; `findings.md`; `provenance.json`; `pristine-fullcrop.png`; `numbered-crosshair.png`; `raw-zoom-board.png`; `zoom-patches/`.
- Command: `python3 .scratch/35-r1-articulated-study/evidence/A-teacher-landmark-audit-v1/audit_landmarks.py` — passed; source/crop hashes match, 19 landmarks, all crop pixels exact. No rendering, fitting, environment changes, staging or commit.

The audit is numerical/contextual only; it cannot independently resolve semantic identity, exact seams, or artwork quality. Request independent semantic adjudication of N1 before using its label/coordinate in future fit work. Current owner: Main / fresh semantic reviewer to route. R1 gates unchanged.
