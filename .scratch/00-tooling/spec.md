# 00 — tooling: compare/diff/ref toolkit + smoke test

Status: done

## Deliverables

- `scripts/draw.py` + `scripts/draw` wrapper: subcommands `render`, `compare`, `diff`, `ref`, `log`
- Renderer: chrome-headless-shell (playwright cache path), zero extra deps
- Python venv `.venv` (py3.12): cv2, numpy, pillow
- Docs: `AGENTS.md`, `docs/drawing/method.md`, `docs/drawing/principles.md`

## Extensions (2026-09-15) — the ratchet

Added after the night session committed two artifacts as "FINAL IMAGE" while sitting 4.5–5.6× below
the best drawing the repo already held (`.scratch/14-abstraction-research/spec.md` → Verdict):

- `scripts/draw baseline ART [--ref REF] [--note]` — records ART as the project's best artifact in
  `.scratch/00-tooling/baseline/` (`best.png` + `best.json` with sha256, metrics, provenance).
- `coverage` metric — fraction of the reference's content the draft accounts for. The omission
  alarm: `color_dist` cannot distinguish "drawn wrong" from "not drawn". Floor and alarm, never a
  target (roadmap R6).
- `check` now emits **the 1:1 draft** (`draft-fullres.png`) and lists it for the reviewer, and adds
  one crop on the worst error **where the draft actually drew something** — closing 07's finding that
  the face never received a crop.
- `check` prints the delta against the recorded baseline (`vs recorded best: …`).
- Test counter fixed: it reported `11/7` (hardcoded denominator); now counts actual checks.

Rationale and gates: `docs/drawing/roadmap.md`. Lesson: `principles.md` P23.

## Acceptance

- [x] smoke.svg vs hand-made ref: compare side-by-side, region zoom
- [x] diff line mode: cyan=ref-only, magenta=mine-only, white=match + numbered hint boxes (evidence/smoke-diff.png)
- [x] metrics consistent between `diff` and `log` (edge_f1 0.406 both paths)
- [x] ref lineart + palette on image.jpg

## Knowhow learned (provenance → promote if reused)

- chrome-headless-shell `--screenshot --window-size` is a complete zero-dep HTML/SVG renderer.
- BUG CLASS: `file://` + relative path → relative part becomes URL *host*, silently renders blank page. Always abspath. Cost 3 debug rounds.
- cv2.imwrite silently returns False on missing parent dirs — wrap it.
- .venv default python from uv was 3.9 — pin `--python 3.12` for `X | None` syntax.

## Comments

- 2026-09-10 agent(pi) phase 0 executed, smoke evidence committed, metrics bug (swapped precision/recall numerators) fixed, palette swatch padding fixed.
- 2026-09-15 agent(pi): the ratchet added (see Extensions). This ticket now owns the baseline store
  `.scratch/00-tooling/baseline/` — the project-wide floor, not an exercise's artifact.
