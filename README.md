# learn_draw — learning to draw via programmatic art

An experiment in learning to draw. Not "generate images": the goal is to build, by hand and by
agent, the *drawing skill* — expressed as explainable vector graphics (SVG/CSS, never diffusion or
pixel generation), first by recreating a reference image, then with the reference closed, then with
no reference at all.

The reference target is `image.jpg` (an anime-style portrait). The stated end-goal complexity is a
Starry-Night-class scene drawn from intent alone.

## Where this project is right now

Start with [`STATUS.md`](STATUS.md). The user-approved target architecture is
[`docs/drawing/spatial-model.md`](docs/drawing/spatial-model.md): separately drawn 2D
components placed on 3D planes or curves, with visibility computed by depth. The existing
`relate.py` / `scene_render.py` pipeline is a **flat 2D implementation**, not yet that engine.
Current milestones and gates are in [`docs/drawing/roadmap.md`](docs/drawing/roadmap.md).

A bounded structural sketch (`scripts/spatial_sketch.py`) places one continuous striped ribbon
around a coarse torso and projects two viewpoints. It uses approximate triangle painter sorting,
not an exact vector visibility implementation. It does not reproduce the target portrait.

The reference study is `image.jpg`; M4j is the latest 2D assembly study. The user accepted the
improvement to hair but says the ribbon's position remains wrong. Historical decisions and
iterations are preserved under `docs/drawing/history/` and `.scratch/13-assembly/log.md`.

## Current toolchain (legacy 2D)

`docs/drawing/abstraction.md` and `scene-format.md` document the working 2D authoring/renderer
contract. `vocabulary.md` inventories reusable families, `method.md` the review loop, and
`principles.md` transferable lessons. None of those overrides `spatial-model.md` on the new
component/surface/visibility contract.

```bash
.venv/bin/python scripts/relate.py .scratch/13-assembly/work/spec.yaml -o /tmp/study.svg
scripts/draw check .scratch/13-assembly/evidence/m4j-final.png --ref image.jpg
.venv/bin/python scripts/spatial_sketch.py -o /tmp/spatial-sketch.svg
```

## Running it

```bash
python3 -m venv .venv && .venv/bin/pip install numpy opencv-python pillow
.venv/bin/python scripts/tests/test_scene.py          # smoke tests
.venv/bin/python scripts/draw.py --help
```

Rendering needs a Chrome build (the tooling uses `chrome-headless-shell` from a Playwright cache).

## Invariants in one breath

Geometry is computed, never eyeballed (≤ ~4 hand-typed coordinates per shape). The engine never
reads the target — a reference may *seed* values, then it is closed, and every addition is tested
with the image deleted. Structure and depth visibility precede designed line art; colour and soft fields come later. Metrics are floors and
alarms, never targets. Never judge your own render: run `check`, then give its image list — and
nothing else — to a fresh-context reviewer. Never replace the recorded best with an unreviewed drawing; structural sketches are separate proofs.

## Licensing

The **code and documentation** in this repository are free software under the **GNU Affero General
Public License v3.0** — see [`LICENSE`](LICENSE).

**Third-party material is not covered by that grant.** This repository also contains reference and
target imagery used as study material:

- `image.jpg` — the drawing target (a third-party illustration);
- `head.png`, `head_hat.png`, `hat.png`, `ribbon.png`, `cloth.png`, `dress.png`, `cutout.png` —
  component plates cropped or redrawn from it;
- renders and comparisons under `.scratch/**/evidence/` that reproduce it.

Those files remain the property of their original rights holders and are included only as the
reference a study of this kind requires. The AGPL grant above applies to the project's own code,
docs and outputs, not to them.
