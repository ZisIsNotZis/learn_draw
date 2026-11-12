# Frontal head recipe — 2026-11-12

**Bounded flat-cartoon component usability demonstrated; complete artwork/hair mastery unproven.**
The recipe is not yet a production studio scene node. Its next step is integration with selection,
preview, accept and undo. Human taste feedback is pending asynchronously, not presumed positive.

## What is real

`09-smooth-art-contours/` is the current author sample. The independent operator's
`usability/default/` and `usability/smaller-eyes/` are the same recipe, generated without reading or
editing source. `usability/REVIEW.md` records actual commands and image inspection. The operator found
a recognizable, coherent, minimally usable frontal flat-cartoon head and a real local eye-scale
change; no blocker required rebuilding the primitive for that stated use. This is not a heldout test.

```powershell
python examples/studio/head_probe.py --hair side-part --outdir evidence/my-head
python examples/studio/head_probe.py --hair side-part --eye-scale .92 --outdir evidence/my-head-variant
python -m unittest scripts.tests.test_studio_head -v
```

The current recipe is authored from host-relative proportions and existing face/eye families, reads
no image, and generates all detailed geometry. The front cap and locks have one fused material
contour. Face/front-hair artwork intentionally uses smooth contours; the rear haircut keeps its
computed boundary. Eye micro-parts are clipped to their shared aperture. No 3D-view/pose claim is made.

## Preserved experiments

- `01-bare-head`: first bare recipe; overly broad iris/catchlight placement and a capsule-like neck.
- `02-bob-context`, `03-bob-context`: shared cap/short locks, then less rear fill and comb lines.
  Two blind reviewers saw a cap plus attached side curtains; the old rear ellipse read as a bib.
- `04-fused-bob`: partial experiment; rendering timed out. Do not infer a rendered/accepted result.
- `05-side-part`, `06-exact-boundaries`: union/side-part and explicit compiled polygon boundaries.
  These are frozen intermediate SVG/PNG records, not current-code reproduction claims.
- `07-native-default`, `08-eye-size`: native SVG and eye-size comparison. Two blind reviewers saw a
  recognizable head and local eye change but found a sharp fringe opening, geometric jaw, blunt rear
  edge, simplified ears and helmet-like hair. Those observations remain valid visual evidence.
- `09-smooth-art-contours`: intentional smooth face/front hair and one connected parting guide.
  The purpose-aware operator's result above is limited to an editable flat-cartoon head component.

The reviewer pair was head_review_a/b for the first context and head_sidepart_review_a/b for 07/08.
They had images only, no history/source/expected verdict. Their “flat icon” reading is kept distinct
from the intended flat-icon component's usefulness; it does not establish full portrait completion.
Neck/shoulders/realistic lighting are not hidden requirements of that component use.

## Validation and correction

40 tests passed across operation, head-probe, visibility and oracle suites. New rendered negative
controls prove (1) removing the aperture clip reintroduces escaped catchlights and (2) generic curve
fitting changes the coverage at computed rear-hair corners. A trial assertion that this fit must
overshoot the declared cut height failed its negative control: that causal claim was withdrawn.
Face curvature is a deliberate art treatment; exact polygons are not automatically good art lines.

Native resvg_py 0.5.0 rendered one text-free sample in 0.029 seconds inside an already running Python
process, excluding import/CLI startup. This is one observed sample, not an end-to-end latency promise.
Shapely 2.2.0 supplies valid-polygon checks and same-support material union. Relevant primary docs:
[Shapely set operations](https://shapely.readthedocs.io/en/stable/manual.html#object.union),
[native SVG renderer API](https://resvg-py.readthedocs.io/en/latest/api.html).

All original portrait files remain unchanged. No generated pixels from an image model, local model
inference, GPU workflow, sealed brief or old portrait-baseline promotion was used.
