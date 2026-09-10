# learn_draw — learning to draw via programmatic art

Goal: learn to draw (SVG/CSS programmatic art, never diffusion/pixel) — first by recreating reference images with explainable, readable vector graphics, later without a reference. Reference target: `image.jpg` (anime-style portrait).

Method, style guide, and loop: `docs/drawing/method.md` — read before any drawing session. Transferable lessons log: `docs/drawing/principles.md` (append-only).

## Invariant rules

1. **Semantic layer only.** Every path/layer gets a name + intent comment. Every edit is justified by a statement about the drawing ("brim ellipse too flat"), never by "moved a point to lower a metric". Chasing pixel metrics = optimizer regression, forbidden.
2. **Line art and coloring are separate concerns**, drawn and compared separately (line mode diff vs color mode diff).
3. **A weird hint means upstream error.** If a diff hint points at something my mental model can't explain, my earlier drawing is structurally wrong — investigate backward, don't patch forward.
4. **Metrics are signal, never target.** Log edge-F1 / color distance per iteration; never tune against them.

## Layout

- `docs/drawing/` — method + principles (design truth)
- `scripts/draw` — CLI: `compare`, `diff`, `ref`, `log`, `render` (see `--help`)
- `.scratch/NN-slug/` — one dir per exercise: `spec.md`, `work/` (iterations, git-committed), `evidence/` (composites), `ref/` (preprocessed refs), `log.md` (iteration log)
- `.venv/` — python env (uv). Run tools via `scripts/draw` wrapper.

## Command cheat sheet

```bash
scripts/draw ref image.jpg lineart -o <ex>/ref/lineart.png   # XDoG line reference
scripts/draw ref image.jpg palette -o <ex>/ref/palette.png   # k-means palette, prints hexes
scripts/draw compare image.jpg <ex>/work/v3.svg --region 500,80,300,300 --zoom 2
scripts/draw diff image.jpg <ex>/work/v3.svg                 # line mode: cyan=ref-only, magenta=mine-only, white=match; prints metrics
scripts/draw diff image.jpg <ex>/work/v3.svg --mode color    # color heatmap + worst-region boxes
scripts/draw measure <ex>/ref/duck.png --point 470,480        # exact color at pixel
scripts/draw measure <ex>/ref/duck.png --hough                # circle detection (head, eye...)
scripts/draw measure <ex>/ref/duck.png --scan col:420:540:625 # color transitions along a line
scripts/draw log <ex> --iter 3 --ref image.jpg --src <ex>/work/v3.svg --note "..."
```

Renderer: `chrome-headless-shell` (playwright cache) — renders SVG and HTML/CSS alike, one source of truth. Python: cv2/numpy/Pillow in `.venv`.
