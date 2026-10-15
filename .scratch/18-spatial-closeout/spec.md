# S0 closeout — first task after the code-only learning plan

## Authority and ownership

User requested detailed plan documentation and implementation by `github-copilot/gpt-6-luna`, with
parent management/orchestration. Parent owns product docs and acceptance; Luna owns the bounded
renderer/test/evidence seam. Base: master at `24693d4` (verify current Git before editing).
Pre-existing staged `.gitmodules` and vendor submodules, and untracked `.agents/`, are user work:
never stage, reset, clean, commit or modify them. No commits/pushes in this task.

Read root AGENTS.md, WORKSPACE.md, STATUS.md, docs/drawing/{roadmap,spatial-model,method}.md and
applicable nested instructions. Roadmap S0 closeout is the acceptance contract. No native image/video
generation, generated sprites, metric tuning, manually cut visibility ranges or painter-order patches.

## Drawing question

Can our tested opaque-surface vector visibility produce a continuous striped strip in two views
without artificial tessellation seams, while preserving real occlusion boundaries?

## Exclusive implementation boundary

Inspect `scripts/vector_visibility.py`, `scripts/spatial_sketch.py`, related tests and
`scripts/figure_scaffold.py`. Edit the visibility implementation and its narrowly relevant tests;
edit sketch rendering only if needed for the diagnostic exercise. Figure source and existing art,
baseline, vendor, dependencies and official docs are read-only. New diagnostics/generator may live
in this exercise's work/. Put artifacts in evidence/, observations in log.md. Parent updates STATUS
and active-work after acceptance. Do not start S1a or redesign the engine.

## Steps and required outputs

1. Reproduce the current seam with deterministic renders and a small geometric case; preserve before
   source/render evidence. Distinguish anti-alias raster cracks from missing visibility geometry.
2. Freeze diagnostic cases and tolerances before evaluating a fix: adjacent tessellated faces;
   partial occlusion with visible/background edges; depth-flip crossing; declaration-order reversal;
   relevant self-occlusion; an evidenced tangent/coplanar case and explicit tie/unsupported policy.
   Include alternate subdivision and two cameras of the same whole strip.
3. Implement the smallest sound fix. Do not globally blur, paint background-coloured seam strokes,
   or enlarge hidden surfaces over an occluder. If expanding/merging fragments is considered, prove
   correct coverage at real external and occlusion boundaries rather than assuming overlap is safe.
4. Add regression tests that fail before the fix and preserve existing geometry tests. Render a
   diagnostic board (SVG/PNG) and keep individual renders for inspection.
5. Run bounded commands and log exact commands, observed results, hashes, versions if relevant,
   changed files and residual limitations. Use controlled reference-unavailable validation without
   removing the original image.jpg. Run scene smoke, spatial/figure tests, determinism and applicable
   baseline gate. `git diff --check` must pass. If a check is unavailable, say so precisely.
6. Run draw check on appropriate diagnostics; record report.txt paths for parent fresh visual review.
   No baseline promotion; geometric proof is not a finished drawing.

## Stop/escalation

If a sound fix requires a new backend, dependency, transparency/intersection contract or material
spending, contact parent and defer only the dependent change. Report exact failures, not green
claims. Checkpoint before deadline. No child delegation. Parent will review diff and evidence and
arrange independent review; worker must not certify its own visual gate.

## Completion report

Return reproduction/cause, actual fix, changed paths, test commands/results, deterministic artifact
hashes, diagnostic case coverage, report.txt image-list location, remaining failures/risks and next
step. Do not claim S0 closed before independent review and parent acceptance.
