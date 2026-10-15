# Learner packet — author one ribbon spec

You may use the small Python ribbon generator and its teaching card. Your output is text/code only;
do not create or substitute generated picture assets. The reference is not read by the generator.

Read [`ribbon-card.md`](ribbon-card.md) for the actual formula, semantic parameters, ranges, failure
examples and limits. Copy [`../work/teaching-example.json`](../work/teaching-example.json) as a
starting schema, then change only fields justified by your intended component. Do not copy a full
acceptance-case answer as an unseen task.

A minimal valid spec has a semantic name, positive `length` and `width`. `origin` is the root centre
in world coordinates; `heading` fixes its initial direction. `bend`, `depth`, `family`, `tip_ratio`
and `twist` describe the continuous support. `front` and `back` are base material colours selected
from surface facing, not camera-specific flags. The renderer adds a narrow continuous stripe in local
`v` and selects a contrasting stripe color from the same facing rule; it is not a visibility cut or
mesh-edge line. `segments` controls generated mesh sampling. For `crossback`, `abs(bend) >= 0.05`
and `abs(depth) >= 2 * width`; its side displacement is eased through the reverse run. This separates
the principal paired crossing sections only, not a guarantee against every self-intersection. The
corrected crossing example was checked at several finite mesh resolutions; do not treat that as a
general collision solver. The board also uses a stronger muted green-gray card display fill for
contrast; it does not change the support card's geometry/depth or spec input.

Render one view with:

```bash
.venv/bin/python scripts/ribbon_family.py render path/to/my-ribbon.json \
  --name front --yaw 0 --pitch 0 -o .scratch/19-ribbon-family/evidence/my-ribbon
```

The output basename yields a named `.svg` plus `.png`; the sole raster renderer is the existing local
Chromium utility. Try a second yaw/pitch with the *same JSON* to see the same component projected
again. For the known teaching/variation matrix and both fixed diagnostic cameras, regenerate with:

```bash
.venv/bin/python scripts/ribbon_family.py board \
  .scratch/19-ribbon-family/work/cases.json \
  --out-dir .scratch/19-ribbon-family/evidence
```

Do not specify per-view visible ranges, separate near/far copies, or mesh-edge strokes. A visible
fragment is generated from the full strip and other opaque surface depths. Keep the art identity and
mesh construction separate. The current evidence demonstrates one local ribbon family only; no hair
or figure-layout competence is implied.
