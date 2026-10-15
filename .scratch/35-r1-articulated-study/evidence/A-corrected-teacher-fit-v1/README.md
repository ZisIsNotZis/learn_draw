# A corrected-teacher garment fit v1

**Status:** candidate emitted; teacher semantic and teacher output-chain gates passed independently. This does **not** pass A art/readability, independent construction/depth, B/integration, heldout, or R1/user acceptance. Main owns a fresh image-only review after freezing this candidate. Writer did not open or judge rendered images.

## Deliverables

- `artwork-a.svg` / `artwork-a.png`: actual 400×480 A-only drawing against the registered 400×480 crop frame.
- `source/semantic-parameters.json` → `source/build_a.py`: editable low-dimensional garment families; the generator accepts only `--out` and local compact parameters. It cannot open/receive `image.jpg`, crop, patch, regions, landmarks, or traces.
- `fit-plan.md`: part → accepted observation → parameter → family → support/attachment/depth/backend causal chain and hypotheses.
- `teacher-measurements/`: finite observation whitelist and one-time named accepted trace interval measurements, excluded from runtime.
- `check-a/`: registered-crop comparison bundle. `report.txt` is the exact image-list protocol; writer used the numeric line only as an alarm and made no metric-directed change.
- `reproduction/`: reference-absent second SVG+PNG; byte-identical to the primary outputs.
- `tests/test_a_garment_family.py`: focused family/contour/anchor/support/depth/input-isolation tests.
- `manifest.json` and `manifest.sha256`: file hashes, provenance, run evidence and still-open acceptance gates.

## Reproduce

From repository root:

```bash
python3 -B .scratch/35-r1-articulated-study/evidence/A-corrected-teacher-fit-v1/source/build_a.py --out .scratch/35-r1-articulated-study/evidence/A-corrected-teacher-fit-v1/artwork-a.svg
scripts/draw render .scratch/35-r1-articulated-study/evidence/A-corrected-teacher-fit-v1/artwork-a.svg -o .scratch/35-r1-articulated-study/evidence/A-corrected-teacher-fit-v1/artwork-a.png
python3 -B -m pytest -p no:cacheprovider -q .scratch/35-r1-articulated-study/evidence/A-corrected-teacher-fit-v1/tests/test_a_garment_family.py
```

Optional target comparison only (never a render input):

```bash
scripts/draw check .scratch/35-r1-articulated-study/evidence/A-corrected-teacher-fit-v1/artwork-a.svg --ref .scratch/35-r1-articulated-study/evidence/A-teacher-reconstruction-v2/teacher-only-corrected-v2/pristine-fullcrop.png --outdir .scratch/35-r1-articulated-study/evidence/A-corrected-teacher-fit-v1/check-a
```

The only permitted teacher facts are limited fields/neighborhoods in `teacher-measurements/observation-boundary.json`. LTI2, all left-tail-centerline stations, N1/BD1/BD4/TD1, blue identity, DTO2 terminal, hidden seams/armhole and complete/crop-external boundaries remain forbidden/unknown. Smooth closures, attachments, tail route/width and disappearing fragments are explicitly artist/generated hypotheses, not recovered source truth.
