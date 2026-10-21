# The two images the person is asked to judge (R1a)

One screen: the file he looks at, the revision it belongs to, how to rebuild it, and what a verdict on
it would say today. Both paths are relative to the checkout root `/home/z/vibe/learn_draw`.

## The images

| study | his image | sha256 | revision |
| --- | --- | --- | --- |
| A, the bow | `evidence/A-bow-study-v2/check/draft-fullres.png` (800x560, 1:1) | `1d517c0c82061c39831f034811a973ade9a4858796ecc6e6a16b8949998dbe7d` | `3825d51` |
| B, the hand and dish | `evidence/B-hand-study-v1-r1/check/draft-fullres.png` (900x700, 1:1) | `4dbcad2ec517191c73c75057f948f0a73aeec5566566df922e1f9ac8e8354083` | `34b31b4` |

Both are inside `.scratch/35-r1-articulated-study/`. `check/draft.png` beside each is the same picture
and is not the one to judge on: the 1:1 `draft-fullres.png` is where line weight and separation are
visible.

**What a judgement on them would say now, before he sees them:** the bow's image-only verdict is
**FAIL** (`evidence/reviews-r1a/A-bow-study-v2-image-review-1.md`, six blocking findings, bound to the
hash above) and the hand's two verdicts were dispatched at the hash above and had not landed when this
file was written. He is being shown an image whose independent art verdict failed, and that has to be
said in the same breath as the image, or the asking is dishonest.

## Rebuild, and the check that it is the image he judges

The command that regenerates a `check/` bundle, with its 1:1 image first, is:

```
.venv/bin/python scripts/draw.py check .scratch/35-r1-articulated-study/evidence/A-bow-study-v2/artwork.svg
.venv/bin/python scripts/draw.py check .scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1/artwork.svg
```

Run from the checkout root with the project venv (`.venv`; it carries numpy, cv2, pillow, pyyaml and
**no pytest**, so a suite runs as
`PYTHONPATH=/home/z/vibe/learn_draw/.venv/lib/python3.12/site-packages:. python -m pytest -q tests/`
from inside a package).

**Ran, on A only:** the command left `check/draft-fullres.png` byte-identical
(`sha256` unchanged at `1d517c0c…` above) and rewrote only `check/report.txt`, whose diff was path
formatting; that churn was reverted so A stays frozen at `3825d51`. **Not run on B**, because B's
revision is bound by two reviews in flight and rewriting its bundle's `report.txt` would move the
revision under them. What B has instead: its own suite's byte-for-byte test passes (the delivered
`artwork.png` equals a fresh build from a clean tree, and `check/draft.png` equals `artwork.png`), its
manifest verifies 19/19, and `sha256sum -c manifest.sha256` is clean.

**A defect this file records rather than fixes:** neither package's `README.md` names the file
`check/draft-fullres.png` or the command that produces it, so the rebuild command is one hop away from
the image rather than in the same place. The next revision of each package carries it in its own
README; editing the README now would move a revision that a review is bound to.

## What is still owed before he judged the hand

`evidence/reviews-r1a/B-hand-study-v1-r1-image-review-1.md` (art and cohesion) and
`...-execution-review-1.md` (construction, geometry, depth, mechanics). An absent file means the
verdict did not land; it is re-dispatched from
[`wave15-contracts.md`](wave15-contracts.md) § Packages K, L at no rebuild cost.
