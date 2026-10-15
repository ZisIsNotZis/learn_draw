# A cloth construction-family v2

**Candidate emitted; not an art/readability or R1 PASS.** This is a new candidate separate from the frozen issue-45 A image. The builder, semantic parameters, and tests are under `source/` and `tests/`; the generator uses opening-derived fold wedges, a tilted waist-continuing body, sleeve fullness/cap with shared transverse cuff, gather/free-edge/return-fold loops, cubic tails, a separate anonymous crop-exiting blue band, and only the approved local neck/shoulder hair context.

- Actual output: `artwork-a.svg`, `artwork-a.png` (400×480).
- Construction families and self-proof boundaries: `construction-contract.md`.
- Registered-crop comparison: `check-a/report.txt`; the exact fresh-review image list is `review-image-list.txt`. Metrics in the check report are breakage alarms only and were not used to fit geometry.
- Reproduction: `reproduction/rebuilt.svg` and `.png`; both are byte-identical to the primary outputs from a reference-absent builder/render.
- Hash/provenance and open gates: `manifest.json`, `manifest.sha256`, and root `report.txt`.

Reproduce the candidate without a reference:

```bash
python3 -B .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2/source/build_a.py --out .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2/artwork-a.svg
scripts/draw render .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2/artwork-a.svg -o .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2/artwork-a.png
python3 -B -m pytest -p no:cacheprovider -q .scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2/tests/test_a_cloth_identity.py
```

The reference/crop is only a finite observation source and post-render comparison. The builder/runtime reads only `source/semantic-parameters.json`. The writer did not open/judge the produced images. Main owns fresh actual-image review. Construction tests do not independently establish overall 3D physical non-intersection, art quality, heldout compatibility, R1 acceptance, or user judgment; all remain open.
