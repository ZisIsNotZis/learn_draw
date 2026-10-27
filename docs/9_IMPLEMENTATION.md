# 9_IMPLEMENTATION — environment, commands, the gates to run, testing and determinism, the record areas, machine-local facts

This file owns how the work is run, not what the work decides: product decisions are `5_PRODUCT.md`, what
good means is `2_GOAL.md`, the binding rules are `3_REQUIREMENT.md`, the flows are `4_USECASE.md`, the
milestones are `0_ROADMAP.md`.

# EXPLICIT

## Coordination is remote (M2), because the repository is public

The repository is public at `zisisnotzis/learn_draw`, so the baseline in `.scratch/00-tooling/baseline/`
and the ticket statuses are shared state and a shared floor rather than a local-only one; the
coordination mode is **M2 (remote)**, on explicit user instruction. Remote: `origin` →
`git@github.com/ZisIsNotZis/learn_draw.git` (public, AGPL-3.0, default branch `master`). Shared state —
the docs, the tickets and the recorded baseline — lands on `master`, and concurrent writers use
`git worktree`, one writer per tree.

# INFERRED

## The environment, and how it is rebuilt

`pyproject.toml` declares it: `uv venv .venv && uv pip install -e .`, with `numpy`,
`opencv-python-headless`, `pillow` and `pyyaml`, and `requires-python >= 3.11`. `.venv/` is the local
environment; the resolver and the scene compiler read YAML, so `pyyaml` is part of the toolchain, not
an extra.

Rendering needs a Chrome build. The renderer is not a Python package: `scripts/renderer.py` resolves
the newest `chromium_headless_shell-*` already present in the Playwright cache, overridable with
`CHROME_HEADLESS_SHELL`.

Tools are run through the `scripts/draw` wrapper, which prefers `.venv/bin/python` when it exists and
otherwise degrades to `python3`; a script that is not behind the wrapper is run as
`.venv/bin/python scripts/<script>.py`.

## The toolchain

- `scripts/draw` — the CLI, a wrapper over `scripts/draw.py`: `render`, `compare`, `diff`, `ref`,
  `check`, `log`, `baseline`, `freeze`, `measure` (`scripts/draw --help`).
- `scripts/relate.py` — the single relational resolver: a spec to a render, and the materializer that
  turns a computed `region` into a `traced` sidecar.
- `scripts/scene_render.py` — compiles a scene to SVG through chrome (`--svg`, `--ref`, `--size`).
- `scripts/spatial_sketch.py` — the spatial scaffold: one uncut ribbon on a curved support, two
  viewports, triangle painter sorting; not a visibility engine and not a reproduction of the target.
- `scripts/similarity.py` — contextual (CLIP) similarity, a secondary alarm (`2_GOAL.md`).
- `scripts/tests/test_scene.py` — the smoke suite.

## The commands

### The drawing loop

```bash
scripts/draw check <spec.yaml|art.svg|art.html|art.png> [--ref image.jpg] [--outdir DIR]
scripts/draw log <ex> --iter N [--ref image.jpg] --src <ex>/work/art.png --note "..."
```

`check` is the whole visual bundle in one command. It writes into `<exercise>/evidence/check/` unless
`--outdir` is given: `draft-fullres.png` (the 1:1 draft — detail is judged here), `side-by-side.png`
(ref beside draft, panes ≤ 256 px by default via `--pane`, layout only), the worst regions as
magnified REF|DRAFT crops with their coordinates (`region-N.png`, including one crop on the worst
error *where the draft actually drew something*), and `report.txt` — the image list, the metrics and
the reviewer protocol. It prints the metrics and the `vs recorded best:` delta, and **carries no
verdict by design**: whether the drawing is good is the reviewer's judgement (`4_USECASE.md`). Omit
`--ref` for the reference-free stage: the bundle is then the 1:1 drawing listed first plus a bounded
downscaled preview for layout only.

`log` appends one row to `<ex>/log.md` — `| iter | edge-F1 | color-dist | note |`, creating the file
with its header if it is absent — so the exercise directory must already exist. `--src` is an image,
or an `.svg`/`.html` source that is rendered first, and together with `--ref` its metrics are measured
before the row is written.

### The ratchet

```bash
scripts/draw check <render> --ref image.jpg       # prints "vs recorded best: ..."
scripts/draw baseline <render> --ref image.jpg --note "<the gate that passed>"
```

`.scratch/00-tooling/baseline/` holds two registers. `best.png` with `best.json` is the recorded
ratchet floor that every later render is compared against: a byte copy of the artifact it was
promoted from, never a re-encode, with the source and artifact sha256 named separately, the provenance
and the metrics. `fidelity-reference.png` with `.json` is the hand-fitted render, preserved as the
best match to the target and as a teacher; it is hand-fitted, therefore a trace, and it is not the
floor to beat.

`baseline` records an artifact as the floor and is called only after the applicable whole-drawing gate
has passed (`0_ROADMAP.md`); a structural sketch is not a comparable finished drawing and never
replaces it.

### Targeted follow-ups

```bash
scripts/draw compare image.jpg <art> --region 500,80,300,300 --zoom 2 [-o OUT]
scripts/draw diff image.jpg <art> [--mode line|color] [-o OUT]
scripts/draw measure image.jpg [--point 470,480 | --hough | --scan col:420:540:625]
scripts/draw ref image.jpg palette [-o OUT]
scripts/draw render <src.svg|src.html> [-o OUT] [--size WxH]
scripts/draw freeze <spec.yaml> --ref image.jpg [--outdir DIR]
.venv/bin/python scripts/relate.py <spec.yaml> -o OUT [--anchors] [--ref image.jpg]  # -o is required unless --freeze is given
.venv/bin/python scripts/spatial_sketch.py -o OUT
.venv/bin/python scripts/scene_render.py <scene.yaml> -o OUT [--svg OUT] [--ref REF] [--size WxH]
.venv/bin/python scripts/similarity.py <draft> --ref image.jpg
```

- `compare` — an ad-hoc side-by-side for one attention pass; a targeted question is asked per region
  at a zoom, never on the full frame.
- `diff` — line mode overlays edge maps: **cyan = reference-only (missed line), magenta = mine-only
  (invented line), white = match**, with numbered hint boxes on the worst missing regions; color mode
  gives the amplified colour-distance heatmap and worst-region boxes, and prints edge-F1 with mean
  colour distance.
- `measure` — `--point` prints one pixel's hex colour, `--hough` lists circles, `--scan
  row:y:x0:x1` / `col:x:x0:x1` prints colour transitions along a line.
- `ref palette` — the reference's k-means swatches, printed as hex and written as a strip; it is
  preprocessing, run once per exercise, and drawings are made against it. (`ref lineart` exists but is
  not useful for this reference; `8_DETAIL.md` owns why.)
- `render` — any SVG or HTML source to PNG through the Chrome build.
- `freeze` — materialises every `region` node of a spec into a `traced` sidecar and needs `--ref`;
  a spec with no `region` nodes has nothing to freeze.
- `relate.py` — resolves a spec to a render; `-o` is required unless `--freeze` is given, and
  `--anchors` prints the resolved anchor table beside the render.
- `similarity.py` — prints the cosine similarity to the reference. The instrument is a CLIP image
  embedding (OpenAI `ViT-B-32`, 151M parameters, cached at `~/.cache/clip`); its first readings, from
  the retired 2D sequence, are kept as calibration evidence in
  `.scratch/history/similarity-alarm-readings.md`. It is an alarm, never a gate (`2_GOAL.md`).
- `spatial_sketch.py` — writes the two projected views of the scaffold.

### Before a commit that touches code or a drawing

| gate | command | passes when |
| --- | --- | --- |
| smoke tests | `.venv/bin/python scripts/tests/test_scene.py` | `N/N smoke tests passed`, no `FAIL` |
| ratchet floor | `scripts/draw check .scratch/00-tooling/baseline/best.png --ref image.jpg` | `vs recorded best:` shows all deltas `+0.000` |
| determinism | render the same spec twice, compare `sha256` | identical |

Each command and its observed result are recorded in the ticket or commit message (policy R-REP.4).
The milestone-specific gates are written out with each milestone in `0_ROADMAP.md`; these three rows
are the subset that applies to every commit.

## Guardrails that are operational

- A legacy 2D check bundle is compared against `.scratch/00-tooling/baseline/`, and promotion needs
  the applicable gate; those records stay records and waive no gate.
- Up to ~3 focused fixes per problem is the 2D exercises' rule, not the advance's attempt budget:
  candidate and repair limits are written in the workpackage contract that owns them, and
  `0_ROADMAP.md` says where those contracts are.
- The A/B mapping is recorded in the log at handover and confirmed by pixel comparison against the
  two source files, never from memory: a swapped pair inverts the verdict.
- Metrics are a breakage alarm, and `coverage` is the omission floor — the question `color_dist`
  cannot answer (`P23`).
- Not judging your own render, and the sightedness proof a reviewer gives first, are the review
  protocol's (`4_USECASE.md`).

## The 2D resolver's output conventions

These describe what the 2D resolver emits; the authoring language is `5_PRODUCT.md`.

- `viewBox` matches the reference pixel size, and coordinates are in reference space.
- One `<g id="...">` per semantic part, painter order top to bottom in the document.
- Every shape carries an `id` and an adjacent comment stating its intent ("hair pull-point
  convergence curve"), not appearance trivia.
- Names are forward-compatible (`hairStrand3`, not `path_17`), and no magic number sits where a
  formula reads better.
- CSS carries the soft fields (layered gradients, blur, blend modes) and SVG the structure; one source
  file per iteration, either `.svg` or an `.html` wrapper.
- Blur never touches structure — silhouettes, outlines, face features. A soft field that cannot state
  in one line why it is soft is deleted.
- One standing object-level iteration test: a parameter change re-renders the intended change and
  nothing else. A change that moves something it was not meant to move is a defect in the object,
  not a tuning opportunity.

## The exercise sequence the tools support

`.scratch/NN-slug/` is one directory per exercise, holding `spec.md` and, as the exercise produces
them, `work/`, `evidence/`, `ref/` and `log.md`. The former 2D resolver ladder is the exercise
sequence that shape supports; milestones and gates are `0_ROADMAP.md`'s.

| rung | teaches | vocabulary it is allowed to demand |
| --- | --- | --- |
| L1 bust (08) | line-art discipline, relational basics, the hardest small part: the face | `eye`, `brow/nose/mouth` marks, `hair-mass` |
| L2 torso (09) | occlusion as *declared relations*, cloth around the body | `sleeve`, `bow`, `collar`, `hand` |
| L3 cloth (10) | regular structure from generators, folds as flow | `pleats`, fold `flow` |
| L4 ribbon (11) | generated band + wrap-around z-split | `ribbon` refinements |
| L5 fields (12) | the soft tier, and why it comes last | blur discipline, clip+blob idiom |
| L6 assembly (13) | the composition itself as relations | none — proves the level holds |

The ladder ends in the withdrawal that makes the end goal real: the assembled figure is redrawn from
its own spec with the image closed, then a new subject from intent alone. The rung order, the
`draw check` closure, the resolver diagnostics and the path-coordinate rules are historical evidence,
not automatic gates.

## Where the record areas live

- `.scratch/NN-slug/` — one directory per exercise: `spec.md`, `work/`, `evidence/` (with
  `evidence/check/` for the bundles), `ref/`, `log.md`.
- `.scratch/00-tooling/baseline/` — the two registers of the ratchet.
- `.scratch/history/` — retired docs as records (`roadmap-before-spatial-model.md`,
  `status-before-spatial-model.md`) and `early-studies/` for the early vendor-smooth and
  curve-garment studies. `status-before-spatial-model.md` is also the index for the `D1`–`D33`
  decision numbers and the `M1`–`M4` labels that older records cite; `SA1`–`SA3` are the abstraction
  research exercises under `.scratch/14-abstraction-research/`, and `Ex28`/`Ex29`/`Ex32` are the
  exercise numbers under `.scratch/`. A number that resolves to nothing is a record's own history,
  not a live referent.
- `.scratch/35-r1-articulated-study/work/wave-log.md` — the advance's wave log, with the wave
  contracts beside it and reviews verbatim under `evidence/reviews-r1a/`.
- `evidence/`, `teaching/` and `mail/` keep their shape; `mail/README.md` is the mailbox protocol's
  one home.

Records keep their dates — that is their job — and the docs do not. Vendor content under `vendor/` is
third-party and is never edited.

## Machine-local facts

- Policy documents (`docs/policy/…`) are not vendored here; the policy core inlined in the harness
  session's prompt applies. `docs/policy/remote-coordination.md` is not present in this repository,
  and per `S5` nothing is blocked for lack of it.
- The reference imagery is third-party study material and is not covered by the AGPL grant
  (`1_PROBLEM.md`).
