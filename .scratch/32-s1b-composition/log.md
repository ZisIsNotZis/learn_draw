# S1b composition — implementation log

## Scope and disposition

Executed the bounded construction + variation slice recorded before implementation in `spec.md`. Reused the existing figure scaffold and the S1a exercise's semantic strip interface/construction rules; did not edit project source, the renderer, S0/S1a records, vendor, official docs, baseline, or append-only principles. The figure remains an unvalidated coarse hypothesis. Independent recognition/pose/front-back review is still pending; no learner run; S1a readability remains open.

## Artifact

`work/compose.py` loads the existing scaffold, renders two cameras of its baseline composition, then repeats those same two cameras after one semantic pose change: rotate `arm-right` and attached `hand` around the shoulder support by 38° in world space, prior to projection. It passes all resulting surfaces through the existing depth resolver and authors no visibility intervals. Both evidence variants include the existing semantic `head`, `torso`, `arm-left`, `arm-right`, `hand`, `hair-sheet`, `hair-fall`, `bow`, and continuous `ribbon` components (plus the scaffold's lap/skirt/hat forms and eye marks). Geometry and route are inherited scaffold hypotheses, not reconstructed or visually approved.

## Commands and results

- Initial composition smoke failed at import (`ModuleNotFoundError: vector_visibility`): execution of the imported legacy module did not inherit its script search path. Fixed runner by explicitly adding the existing `scripts/` directory to `sys.path`; no backend changes.
- `.venv/bin/python -m unittest scripts.tests.test_figure_scaffold scripts.tests.test_vector_visibility` — passed, 20 tests in 12.303s. Existing draw.py temporary SVG `ResourceWarning`s appeared; tests passed.
- `timeout 120 .venv/bin/python .scratch/32-s1b-composition/work/compose.py --out-dir .scratch/32-s1b-composition/evidence` — passed; emitted baseline and changed-pose SVGs.
- `timeout 120 scripts/draw render .scratch/32-s1b-composition/evidence/two-view.svg -o .scratch/32-s1b-composition/evidence/two-view.png --size 2048x1024` — passed.
- `timeout 120 scripts/draw render .scratch/32-s1b-composition/evidence/pose-variation.svg -o .scratch/32-s1b-composition/evidence/pose-variation.png --size 2048x1024` — passed.
- SVG source inventory — each render contains all required named composition parts; baseline has 38,523 visible polygons and varied pose 38,475. Counts are provenance only, not quality metrics.
- Markdown relative-link check — initial run exposed an incorrect assumed S1a card path; corrected to the accepted artifact's actual `spec.md`. Final check passed: 7 relative links, 0 missing.
- `.venv` Python compile check via `python -m py_compile .scratch/32-s1b-composition/work/compose.py` — passed. `git diff --check -- .scratch/32-s1b-composition` — passed (new exercise files are untracked, so Git has no diff content for them).
- Worktree status inspected: pre-existing staged `.gitmodules` and vendor additions are unchanged; no staging command was run. Therefore no task files are staged, but the overall repository is **not** free of staged files. Many prior dirty/untracked files are preserved; this task added only this exercise record.

## Writer-fallback repair and review disposition

- Addressed the independent review's P1 finding: the hair-sheet root previously sat behind and outside the head support in z despite projected overlap. The root z is now computed on the upper surface of the head ellipsoid from its shared center/radii parameters; the existing downstream sheet shape interpolates away from that root. Added a focused structural test asserting each generated root vertex satisfies the head ellipsoid equation.
- Regenerated both two-camera/two-pose SVGs and PNG renders below; no raw evidence was edited. Review disposition: the identified geometric attachment defect is repaired and verified by the test; independent fresh review/re-review is still required. No visual acceptance claim.
- `.venv/bin/python -m unittest scripts.tests.test_figure_scaffold scripts.tests.test_vector_visibility` — passed, 21 tests in 12.301s (existing temporary-SVG ResourceWarnings).
- `timeout 120 .venv/bin/python .scratch/32-s1b-composition/work/compose.py --out-dir .scratch/32-s1b-composition/evidence` — passed.
- `timeout 120 scripts/draw render .scratch/32-s1b-composition/evidence/two-view.svg -o .scratch/32-s1b-composition/evidence/two-view.png --size 2048x1024` — passed.
- `timeout 120 scripts/draw render .scratch/32-s1b-composition/evidence/pose-variation.svg -o .scratch/32-s1b-composition/evidence/pose-variation.png --size 2048x1024` — passed.

## Remaining proof/gates

No visual self-judgment is claimed. The requested fresh independent reviewer must assess whether the figure reads as a seated figure and whether pose, attachment, and front/back relations work. The pose output only proves a parameterized geometric transform runs; it is not proof the changed pose is visually plausible. Ribbon path, anatomy, hair, and all readability remain hypotheses. Transfer is UNRUN; no claim that S1a readability passed.
