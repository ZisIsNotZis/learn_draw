# learn_draw — learning to draw via programmatic art

An experiment in learning to draw. Not "generate images": the goal is to build, by hand and by
agent, the *drawing skill* — expressed as explainable vector graphics (SVG/CSS, never diffusion or
pixel generation), first by recreating a reference image, then with the reference closed, then with
no reference at all.

The reference target is `image.jpg` (an anime-style portrait). The stated end-goal complexity is a
Starry-Night-class scene drawn from intent alone.

## Where this project is right now

**Start with [`STATUS.md`](STATUS.md)** — current best artifact, the milestone in progress, and open
defects. Direction lives in [`docs/drawing/roadmap.md`](docs/drawing/roadmap.md) (milestones M0–M5 and
the six gates every one must pass).

Honest headline as of 2026-09-15: an unsupervised research session produced real *language* progress
(one relational resolver, object families, measured canons, 24 principles) while its *drawings* fell
**4.5–5.6× below** the best picture the repo already contained — and both were committed as "FINAL
IMAGE" because nothing compared a new render against the previous best. That is now fixed
(`scripts/draw baseline` records the floor; `check` reports the delta; a `coverage` metric makes
deleted content visible). The full post-mortem is in
[`.scratch/14-abstraction-research/spec.md`](.scratch/14-abstraction-research/spec.md) → Verdict.

## How it works

You do not write coordinates. You describe the drawing in words — anchors, relations, and object
families — and a resolver computes the geometry.

```bash
# describe (relations only, no coordinates)         -> compile -> render -> judge
.venv/bin/python scripts/relate.py <spec>.yaml -o art.png --anchors
scripts/draw check art.png --ref image.jpg      # the whole visual feedback bundle + ratchet delta
scripts/draw baseline art.png --ref image.jpg   # promote, only after a passed gate
```

| piece | what it is |
| --- | --- |
| `docs/drawing/roadmap.md` | direction: milestones and gates |
| `docs/drawing/method.md` | the observe→plan→draw→compare→reflect→revise loop, tier ladder, style guide |
| `docs/drawing/abstraction.md` | the authoring language (anchors / relations / vocabulary) |
| `docs/drawing/vocabulary.md` | object families and measured **canons** (proportion knowledge) |
| `docs/drawing/scene-format.md` | the compiled node format behind the resolver |
| `docs/drawing/principles.md` | transferable lessons, P1–P24, append-only |
| `scripts/relate.py` | the single relational resolver |
| `scripts/scene_render.py` | compiles the node format to SVG, renders via headless Chrome |
| `scripts/draw.py` | CLI: `check`, `baseline`, `compare`, `diff`, `ref`, `log`, `measure` |
| `.scratch/NN-slug/` | one directory per exercise: `spec.md`, `work/`, `evidence/`, `log.md` |

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
with the image deleted. Line art precedes colour; soft fields come last. Metrics are floors and
alarms, never targets. Never judge your own render: run `check`, then give its image list — and
nothing else — to a fresh-context reviewer. Never regress the recorded best.

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
