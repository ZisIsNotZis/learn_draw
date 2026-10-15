# Artistic relation-grammar continuation render manifest

Status: actual WP04 authored image candidate, not an art acceptance result. Renderer is revision-local at `source/render_artistic_r1.py`; it only consumes local scene/design values. The depth adapter and compound/path visibility adapters are imported unchanged. The public reference is used only by external `draw check --ref` for A comparison; renderer source has no reference file input/read.

## Artifacts

| Artifact | SHA-256 |
|---|---|
| `source/render_artistic_r1.py` | `700754b5409f2f70dfd2e62a92c38db0841d8fdec6f239c086952e399981dae4` |
| `source/test_artistic_grammar.py` | `08d198e9ced8fedb8d9d877428a3e766cc2cf555316649f3ab01c73311b083e9` |
| `source/artwork.svg` | `3e1022b48c74230115f6a482c1d48d1ea73fc101854c563e13e697026f560996` |
| `source/artwork-a.svg` | `bf663f36675fd56abb9956037b485e85bcca5261d357791216b61a9e54a2d453` |
| `source/artwork-b.svg` | `fbd463c568d48bebaf27b6a0a67ce91c6359ca0b5de2ac31365909fc3d6a4d9b` |
| `check-a/draft-fullres.png` | `199294e2e4c00570d4e646d2a6b2d8102bc8cef9946d0f5cacb9aeceff61be69` |
| `check-b/draft.png` | `6643be6676a28ea8d91ad11a9a79ef6ca62dbd6285d5bffbde09425e3c5f70f3` |
| `check-sheet/draft.png` | `93ca800e28dec10077c7dcfb8629f11b10f7964ae5c91f6f5feba55a04492a5f` |

`draw check` command outputs (full reports contain reviewer protocol and image paths):
- A: `scripts/draw check .scratch/35-r1-articulated-study/evidence/artistic-replan-r1/source/artwork-a.svg --ref image.jpg --outdir .scratch/35-r1-articulated-study/evidence/artistic-replan-r1/check-a`
- B: `scripts/draw check .scratch/35-r1-articulated-study/evidence/artistic-replan-r1/source/artwork-b.svg --outdir .scratch/35-r1-articulated-study/evidence/artistic-replan-r1/check-b`
- Sheet: `scripts/draw check .scratch/35-r1-articulated-study/evidence/artistic-replan-r1/source/artwork.svg --outdir .scratch/35-r1-articulated-study/evidence/artistic-replan-r1/check-sheet`

Fresh visual review must receive only actual image list from each report: A `check-a/side-by-side.png`, `check-a/draft-fullres.png`, `check-a/region-1.png`, `check-a/region-2.png`, `check-a/region-3.png`; B `check-b/draft.png`; combined sheet `check-sheet/draft.png`. Metrics printed by A check are breakage alarms only, never optimization targets. No visual/art verdict is claimed by this manifest.
