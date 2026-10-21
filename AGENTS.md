# learn_draw — learning to draw via programmatic art

Goal: learn to draw (SVG/CSS programmatic art, never diffusion/pixel) — first by recreating reference images with explainable, readable vector graphics, later without a reference. Reference target: `image.jpg` (anime-style portrait).

Where we are right now: `STATUS.md` (repo root) — current best artifact, milestone, blockers.
Where the current advance's contracts and run records are: `.scratch/35-r1-articulated-study/work/wave14-contracts.md`
(wave 13: `wave13-contracts.md`; wave 12: `wave12-contracts.md`) and the wave log beside them; reviews land verbatim in `.scratch/35-r1-articulated-study/evidence/reviews-r1a/`.
This project's roadmap, its split and its mailbox (`mail/`, below this file — its shape is declared in
`mail/README.md`) are held by the node that owns the project, not by any package it dispatches; a
package's answer is its report, and the owner files it.
Where we are going: `docs/drawing/roadmap.md` — current spatial-model milestones and gates.
Architecture SSOT: `docs/drawing/spatial-model.md` — 2D artwork on 3D support surfaces;
the engine computes visibility from depth. The current `relate.py`/SVG pipeline is legacy 2D.

Method, style guide, and loop: `docs/drawing/method.md` — read before any drawing session.
Current 2D authoring language: `docs/drawing/abstraction.md` — relations and object vocabulary,
resolved by `scripts/relate.py`; not the future spatial component language.
Transferable lessons log: `docs/drawing/principles.md` (append-only).
Current flat 2D compiled node format (back end): `docs/drawing/scene-format.md`.

## Invariant rules

1. **Semantic layer only.** Every path/layer gets a name + intent comment. Every edit is justified by a statement about the drawing ("brim ellipse too flat"), never by "moved a point to lower a metric". Chasing pixel metrics = optimizer regression, forbidden.
2. **Structure, line art and coloring are separate concerns.** First establish component identity,
   attachment and depth-based visibility; then design/review line art separately from colouring.
   Soft fields come *last*. A projected mesh edge is not automatically an art line.
3. **A weird hint means upstream error.** If a diff hint points at something my mental model can't explain, my earlier drawing is structurally wrong — investigate backward, don't patch forward.
4. **Metrics are signal, never target.** Log edge-F1 / color distance per iteration; never tune against them. `check` prints them as a breakage alarm only.
5. **Geometry is computed, never eyeballed** (P19). No shape carries more than ~4 hand-typed coordinates — anything larger comes from a relation, a vocabulary node, `trace`/`region`, or a generator. Existing 2D art uses `abstraction.md`; new spatial components use `spatial-model.md`. Absolute frame coordinates are compiler output, not an authoring target.
6. **The engine never sees the target** (P18). A reference may seed the values in a spec, then gets closed. Tracing is a teacher, never the engine — test every addition with the image deleted. For new spatial work, never hand-specify visibility cuts: component depth determines occlusion.
7. **Never judge your own render.** Run `draw check`, then give `report.txt`'s image list — and nothing else — to a fresh-context reviewer asking "what is wrong here?". Verify a reviewer's spatial claims against the bundle's region coordinates (P7: observations are reliable, locations are not).
8. **Never regress the recorded best.** `check` prints `vs recorded best:` for comparable drawings; structural sketches are not comparable finished drawings and must not replace the baseline. "Final", "readable" and "done" require the applicable roadmap gate (P22). Promote a new best only through `scripts/draw baseline` after a passed whole-drawing gate.

## Layout

- `STATUS.md` (root) — where the project is today (SSOT for state)
- `docs/drawing/` — roadmap, method, authoring language, vocabulary/canons, principles, node format (design truth)
- `scripts/similarity.py` — contextual (CLIP) similarity to the reference: a **secondary alarm**, never a gate
- `scripts/draw` — CLI: `check`, `baseline`, `compare`, `diff`, `ref`, `log`, `render`, `measure` (see `--help`)
- `scripts/scene_render.py` — compiles node-format scenes to SVG → chrome
- `scripts/relate.py` — the single relational resolver (promoted 2026-09-14; forks deleted)
- `.scratch/00-tooling/baseline/` — the recorded best artifact (the ratchet floor)
- `.scratch/13-assembly/work/spec.yaml` — the assembly (seeded in M1): the one drawing every milestone patches
- `.scratch/NN-slug/` — one dir per exercise: `spec.md`, `work/`, `evidence/`, `ref/`, `log.md`
- `.venv/` — python env (uv). Run tools via `scripts/draw` wrapper.

## Command cheat sheet

```bash
# the drawing loop (one command, whole visual bundle — see method.md)
scripts/draw check <ex>/work/spec.yaml --ref image.jpg   # or a .svg/.png; omit --ref when reference-free
scripts/draw log <ex> --iter 3 --ref image.jpg --src <ex>/work/spec.yaml --note "..."

# the ratchet: compare against the recorded best, then promote only on a passed gate
scripts/draw check <render> --ref image.jpg        # prints "vs recorded best: ..."
scripts/draw baseline <render> --ref image.jpg --note "M1 exit gate passed; reviewer preferred it"

# targeted follow-ups
scripts/draw compare image.jpg <ex>/work/art.svg --region 500,80,300,300 --zoom 2
scripts/draw diff image.jpg <ex>/work/art.svg [--mode color]   # line: cyan=ref-only, magenta=mine-only, white=match
scripts/draw measure <ex>/ref/ref.png --point 470,480 | --hough | --scan col:420:540:625

# authoring + rendering a relational spec (no coordinates; see docs/drawing/abstraction.md)
.venv/bin/python scripts/relate.py <ex>/work/spec.yaml -o <ex>/work/art.png --anchors
```

Note: `ref lineart` (XDoG) is **not** useful for this reference — it has no uniform black line art
(12.6% of pixels below gray 95); structure comes from region decomposition and traced boundaries.


Renderer: `chrome-headless-shell` (playwright cache) — renders SVG and HTML/CSS alike, one source of truth. Python: cv2/numpy/Pillow in `.venv`.
