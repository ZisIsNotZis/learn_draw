# learn_draw — learning to draw via programmatic art

An experiment in learning to draw. Not "generate images": the goal is to build, by hand and by agent,
the *drawing skill*, expressed as explainable vector graphics (SVG/CSS, never diffusion or pixel
generation) — first by recreating a reference, then with the reference closed, then with no reference
at all, up to a Starry-Night-class scene drawn from intent alone. The reference target is `image.jpg`,
an anime-style portrait.

Where the project stands, what the current advance is and what the next entry is: `docs/0_ROADMAP.md`.
Why the work matters: `docs/1_PROBLEM.md`. Everything else — the goal and rubric, the binding rules,
the loop, the authoring language, the architecture, the formats, the commands — is reached from the
map in [`AGENTS.md`](AGENTS.md).

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
reference a study of this kind requires. The AGPL grant above applies to the project's own code, docs
and outputs, not to them. `vendor/` holds third-party learning material under its own licences.
