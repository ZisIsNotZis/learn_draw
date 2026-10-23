# A-full-figure-v1 — the girl, whole, built from the parts this project already has

**Where this starts.** The person's direction of 2026-10-23 named the one output that works —
`A-cloth-v8/artwork-a.png` (`sha256 da9d92c9…`, 400×480, 13 parts) — and said to continue it directly,
until a full image. So the torso is not rebuilt: `source/parts/` here is `A-cloth-v8`'s part library,
copied byte-for-byte and never edited, and this package composes it into the reference's own 1024×1024
frame and adds the parts that frame needs (hat, upper head, face, hair above the crop, falls, locks,
skirt, lining, arm). `A-cloth-v8` keeps its own bytes and its own verdict.

**The acceptance line is written before the build and lives in [`ACCEPT.md`](ACCEPT.md)** — seven terms,
each decidable by observation. **The self-review rounds are in [`review-log.md`](review-log.md)**, one
entry per render, ranked by whether a mismatch changes identity. This revision lands at round 12: a
whole figure in the frame; T1, T2, T3, T5 and T7 pass, **T4 is partial and T6 is not cleared**. It is
**not** an art pass and no verdict is claimed — the open list is the last section of `review-log.md`.

## What the figure is

25 objects, every one a part with a stated intent, every part declared in
`source/full/figure.py:OBJECTS`:

| object | parts | what it is |
| --- | --- | --- |
| hat-brim | `A-hat-brim-under`, `A-hat-brim-top` | the wide brim: teal underside near the camera, navy top face beyond |
| hat-crown | `A-hat-crown` | the crown standing on the brim |
| hat-puff-top, hat-puff-right | 2 parts | the pink clusters, one at the crown's back, one on the brim's right |
| hair-back | `A-hair-back` | the mass behind the head |
| hair-bangs | `A-hair-bangs` | the fringe over the forehead |
| hair-falls | `A-hair-fall-left`, `-right` | the two falls hanging past the shoulders |
| hair-locks | `A-hair-lock-left`, `-right` | the thin locks in front of each shoulder |
| face, neck | `A-face`, `A-neck`, `A-visible-neck-skin` | the face field; the neck between chin and collar |
| eye-left, eye-right | 4 parts each | lid, iris, the iris's shade, catchlight |
| brows, mouth | 3 parts | |
| collar, bodice, chest-bow | 8 inherited parts | the sailor collar, the cream blouse and waist, the magenta bow |
| left-sleeve, right-sleeve | 4 inherited parts | both puff sleeves and their navy cuffs |
| arm-right, hand-right | `A-arm`, `A-hand` | her right arm out of the cuff, and the hand |
| skirt-front, skirt-drop, underskirt, pleats, lining | 8 parts | the mint skirt, its shaded fold, the navy under-layer, three pleats, the pink and orange lining bands |

Two inherited parts are **dropped**, with the measurement that justifies each: `A-head-face` ends its
jaw at image y 442 — the crop's chin, 58 px below this frame's — so it drew a second jaw line across
the neck; `A-hair-sheet` crosses in front of what is chest once the frame is the whole figure. Both are
replaced by parts authored here. The reasoning is in `source/full/figure.py:build`.

## Build and verify

```
PKG=.scratch/35-r1-articulated-study/evidence/A-full-figure-v1
.venv/bin/python $PKG/source/build_full.py --out $PKG/artwork.svg --report $PKG/build-report.json
.venv/bin/python scripts/draw.py check $PKG/artwork.svg --outdir $PWD/$PKG/check
.venv/bin/python $PKG/source/manifest_full.py --check
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s $PKG/tests -t $PKG
```

The 1:1 image a reviewer judges is `check/draft-fullres.png`; `check/side-by-side.png` is the reference
and this render at the same size, left to right. The build takes ~30 s (the depth engine is pairwise
over ~3.7 k triangles).

## The discipline it keeps

- **No image read.** `source/` contains no image library and no path to `image.jpg`; the reference
  seeded the landmarks in `source/full/figure.py:LAYOUT` while they were authored and is closed after
  that. `tests/test_full_figure.py::test_the_build_reads_no_image` fails if any source file grows an
  image read.
- **Geometry computed, not eyeballed.** One `LAYOUT` dict holds the landmarks (7 per part at most);
  outlines come from generators — ellipse, rotated dome, catmull route, tapered strip, polar clover.
- **Depth decides visibility.** The hat is behind the hair, the falls in front of the sleeves, the bow
  in front of everything on the chest. No visible cut is authored; the project's triangle engine
  computes it.
- **One line policy** by semantic class (`silhouette`, `free_edge`, `contact`, `fold_edge`, `trim`,
  `hair_edge`, `hat_edge`); a mark with no owner or no declared class raises.
- **Hash discipline.** `manifest.sha256` covers every file a rebuild needs; `--check` re-verifies.
- The sealed brief `.scratch/35-r1-articulated-study/work/holdout-brief.sealed.md` was not opened.
