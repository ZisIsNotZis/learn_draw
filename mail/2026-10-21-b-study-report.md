kind:    report
from:    orient-b-study (package launched by root)
to:      root
spend:   idle-compute
id:      none — answered in the run final message

Filed here by root. Body is the run report verbatim.

Everything is committed and every claim verifies. The report follows.

---

# Report → root (`/home/z/vibe`)

**kind:** completion, decision = none (the next act, dispatching the fresh image review, is yours and needs no answer from you for me)
**node whose roadmap this changes:** root's `learn_draw` roadmap — the R1a row "B-hand-study-v1" moves from *absent* to *delivered, mechanically verified, art-unjudged*
**spend:** idle-compute · no network write, no paid API, no exclusive resource

## What was delivered

`B-hand-study-v1` now exists as a package with the same file roles A-bow-study-v1 has: source, a deterministic build, tests, the rendered artwork, `check/` with the 1:1 image listed first, `manifest.json` + `manifest.sha256`, a README. One hand supporting one shallow dish at 900×700 — one image, no panels, no captions, no torso/head/shoulder, the wrist leaving the bottom edge. It is *not* a repair of anything: the directory did not exist, and I touched no other evidence directory, no `docs/`, no `STATUS.md`, no wave log.

The construction is derived, not drawn: the dish is one authored profile revolved once; its rim's two folds, its foot and its wall rings are **found again in the emitted mesh**, so `dish.py` and `contact.py` share no index and cannot drift. Every digit's knots are those rings pushed along the ring's own surface normal by the digit's radius plus one clearance. Every stroke in the drawing is a computed contour (zero set of vertex-normal·view, by marching squares on the emitted grid) or a computed fold (dihedral > 55°); there is no authored mark table, and the digits carry no fold at all.

## Evidence pointer (the rebuild, byte-identical)

```bash
cd .scratch/35-r1-articulated-study/evidence/B-hand-study-v1
../../../../.venv/bin/python source/build.py --out /tmp/bh.svg
cmp /tmp/bh.svg artwork.svg                       # identical
../../../../scripts/draw render /tmp/bh.svg -o /tmp/bh.png
cmp /tmp/bh.png artwork.png                       # byte-identical, 900x700
../../../../.venv/bin/python -m unittest discover -s tests -t .     # Ran 23 tests ... OK
../../../../.venv/bin/python source/manifest.py --check             # 19/19 entries OK
sha256sum -c manifest.sha256                                        # 19/19 OK
```

Commit `5e12d36`; `git status` clean at that revision; only `__pycache__` is ignored.

Artefacts: `.scratch/35-r1-articulated-study/evidence/B-hand-study-v1/{README.md, artwork.svg (2 997 633 B), artwork.png (900x700), check/, source/, tests/, manifest.json, manifest.sha256}` and the dispatch beside the wave's others: `.scratch/35-r1-articulated-study/work/wave11-b-study.js`.

## The contract's acceptance items, each as a number

| item | result |
|---|---|
| tests pass from a clean tree | **23/23 OK** |
| contour re-derivation (test re-derives the dish's rim, not the producer's constant) | the test finds the rim's two folds itself and fits the band plane (0.0° off the dish's axis); every digit's tip is measured against it: **2.19–5.12 px** above the band, clearance declared 1.5, none penetrating |
| separation on emitted rings, roots vs distal halves | roots **0.01–0.05** of a digit's width (**merged — stated, and required** ≤0.10); distal halves **0.47–1.03** (required ≥0.30); taper 0.47–0.52 |
| occlusion break + mutation | **74 occlusions** between different parts, **0** rear edges drawn through; the `--no-depth-break` mutation draws through **74/74**. Both counts in `tests/negative-control-output.txt` |
| two builds byte-identical; delivered PNG = fresh build | `cmp` clean for both SVG and PNG |
| manifest verifies 100%, 1:1 image listed first | 19/19; `check/report.txt` line 1 is `draft-fullres.png`, 900×700 |
| reference-free | no source names `image.jpg`, no image library imported, build identical from another cwd; `scripts/draw check` run with no `--ref` |

## What I do not claim, and the residual risks

I award **no art verdict**. What I can see myself (and have said so in the README rather than hiding): the dish reads as a vessel with a rim band, thickness and interior; the digits hook over the near rim and their shafts are visible in front of the dish's near wall; the thumb is the thickest digit, on the far flank, opposing. What an image reviewer is most likely to strike:

- **The four fingers are still fairly uniform in width and reach** — the closest thing to the contract's "rake tines" failure is not the pose but this uniformity. Changing it is a pose decision I chose not to take unilaterally.
- **The palm reads as one flattened mass, not as anatomy** — no heel wedge, no knuckle row, no thenar bulge beyond the thumb's own root.
- **The palm's contact with the dish's foot is true in the geometry and invisible in the image** (it happens behind the dish's own near wall). The README states this instead of implying the picture shows it.
- Faint radial spokes at the bowl's floor centre, where the revolution's sub-pixel apex quads are inflated 0.45 px to close the renderer's antialias seam.
- The object group is 140 px narrower than the canvas on the left; framing, not a measured target.
- The optional lifted second image builds (`--lift 30`, and the digits stay with the hand) but is **not shipped** — the contract authorises it only once everything else is complete and reviewed.

## Budget

Over the 2-hour wall clock by roughly 25 minutes: the first hour went to getting the renderer's geometry right (two profile-arc sign bugs and a patch-index bug each produced wrong meshes, not wrong parameters), and the mechanical package — tests, mutation, bundle, manifest, README — was authored after that. Nothing was left half-written, and the tree at the committed revision is reproducible.

**Where the next writer starts:** dispatch the fresh sight-capable image review against `check/` alone, per the M1a-RV-IMAGE pattern this study's contract requires; the two most likely blocking findings are the digit uniformity and the palm's anatomy, and both are pose parameters in `source/scene.py`.