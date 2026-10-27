# Contributing

This is a personal drawing study with a written method, not a general-purpose library. The method *is*
the project, so a change is welcome when it serves the drawing and is rejected when it serves a number.
Read `AGENTS.md` first: it holds the rules that override habit and routes every question to the one
document in `docs/` that owns it.

## Scope

In scope:

- a defect in a drawing, stated as a statement about the drawing ("the brim ellipse is too flat", "the
  bow's loops stack instead of crossing") with the evidence that shows it;
- a defect in a tool — a wrong measurement, a renderer that resolves the wrong Chrome build, a
  non-deterministic build;
- a documentation error: a fact that lives in the wrong link, a broken path, a rule that contradicts
  another rule.

Out of scope, and closed without discussion:

- changing the medium. The deliverable is explainable vector art (SVG/CSS). Diffusion, pixel
  generation, and generated sprites are not an implementation detail of this project, they are its
  opposite;
- tracing the reference as an endpoint, or tuning against a metric instead of fixing the drawing;
- raising a threshold, narrowing a gate, or redefining acceptance so that a revision passes;
- editing `vendor/` (third-party material, submodules) or the files listed under "Licensing" in
  `README.md`.

## Running the checks

The environment is `pyproject.toml`'s:

```bash
uv venv .venv && uv pip install -e .
```

The three gates that apply to every commit touching code or a drawing (`docs/9_IMPLEMENTATION.md`):

```bash
.venv/bin/python scripts/tests/test_scene.py                                # smoke suite: N/N passed
scripts/draw check .scratch/00-tooling/baseline/best.png --ref image.jpg    # vs recorded best: +0.000
# render the same spec twice; the sha256 must match                          # determinism
```

A drawing package carries its own suite; run it the way the package's `README.md` says, e.g.

```bash
PKG=.scratch/35-r1-articulated-study/evidence/A-full-figure-v2
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s $PKG/tests -t $PKG
.venv/bin/python $PKG/source/manifest_full.py --check
```

The other suites under `scripts/tests/` are `unittest` modules and can be run one at a time:
`.venv/bin/python scripts/tests/test_ribbon_family.py`.

## What a pull request has to carry

1. **The statement the change makes about the drawing**, or the failing check it repairs. "Moved a point
   to lower a metric" is not one.
2. **The commands you ran and what they returned**, in the commit message or the PR body. An unrun
   claim is treated as unverified.
3. **The evidence**, under the exercise's `evidence/` directory, with the hash of the artifact it
   judges. A record keeps its dates and its dead links; do not tidy old evidence to match a new fact.
4. **No regression of the recorded best.** Promotion of a new floor happens only through
   `scripts/draw baseline`, and only after the applicable whole-drawing gate in `docs/0_ROADMAP.md`
   has passed.
5. **One atomic unit per commit**, in a Conventional Commit (`fix:`, `feat:`, `docs:`, `chore:`), with
   nothing left running and nothing half-committed.

Small, honest commits are easier to review than a large correct one. Do not force-push a branch someone
is reviewing, and do not rewrite history on `master`.

## Issues

An issue is a question about a picture, a tool, or a document — say which, and say how you observed it.
"Looks wrong" without a named observation cannot be acted on; "the left fall crosses in front of the jaw
in the reference and behind it in the render, at region 640,300,300,300" can. Reproductions of a
measurement should name the command and the artifact hash, because a verdict about one revision does not
carry over to the next.

There is no response-time promise. This is one person's study; a defect with a clear observation will be
handled before a suggestion about style.
