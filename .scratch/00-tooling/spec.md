# 00 — tooling: compare/diff/ref toolkit + smoke test

Status: done

## Deliverables

- `scripts/draw.py` + `scripts/draw` wrapper: subcommands `render`, `compare`, `diff`, `ref`, `log`
- Renderer: chrome-headless-shell (playwright cache path), zero extra deps
- Python venv `.venv` (py3.12): cv2, numpy, pillow
- Docs: `AGENTS.md`, `docs/drawing/method.md`, `docs/drawing/principles.md`

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
