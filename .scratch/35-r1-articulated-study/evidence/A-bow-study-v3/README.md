# A-bow-study-v3 — the bow rebuilt at the knot and at the junctions

Object study for round R1a of the A track: the bow alone on an 800x560 canvas, flat cel fill,
one ribbon tied into a knot with two lobes and two tails. This revision replaces the v2
construction because the v2 image review found the failure at the knot and at the junctions,
not in its tuning; v2 is frozen and untouched.

## The review image and the rebuild command

The 1:1 review image is **`check/draft-fullres.png`** (800x560, no downscale) in the bundle
produced by, from the checkout root:

```bash
.venv/bin/python scripts/draw.py check .scratch/35-r1-articulated-study/evidence/A-bow-study-v3/artwork.svg
```

`check/report.txt` lists it first. Rebuild the drawing and its render with:

```bash
cd .scratch/35-r1-articulated-study/evidence/A-bow-study-v3
../../../../.venv/bin/python source/build.py --out artwork.svg     # byte-identical to artwork.svg
../../../../scripts/draw render artwork.svg -o artwork.png
../../../../.venv/bin/python source/manifest.py --check && sha256sum -c manifest.sha256
../../../../.venv/bin/python -m unittest discover -s tests -t .    # 15 tests
```

## What changed, blocker by blocker

- **B1 (no knot).** The knot is three passes that cross: the wrap is painted after both lobes
  and after the left tail, the cross band after the wrap, the tail's fold flap after the cross
  band. Paint order is the occlusion model, so ribbon edges now pass over ribbon edges at the
  knot. `tests/test_knot_crossing.py` counts outline intersections and asserts each order; its
  mutation `--no-occlusion` paints front to back and the same audit fails.
- **B2 (cylinder cap, spoke fan, slab tail).** There is no triangle mesh any more, so no fan
  pole exists. The left tail narrows toward the knot (33 px at x=420 against the wrap's 84 px
  at y=280) and ends in a fold flap painted over the cross band, so it folds over into the knot.
- **B3 (cusp, bare creases).** Both lobes are petals with curved free edges (Chaikin-cut
  control polygons); every crease line ends on its band's contour or under a band painted after
  it - the test resolves each endpoint against the drawing's own polygons.
- **B4 (closed pill, dark teardrop).** The lobes' mouths lie under the wrap, not cut by it; no
  filled shape wears the dark value, so a solid dark blob cannot be emitted.
- **B5 (exposed mesh, uniform stroke).** One polygon per band, so there is no per-face fill or
  seam stroke: no striping. Contour 5.0 px against creases 2.4 px; no dashes; no texture,
  shading or background mark.
- **B6 (stacked masses).** Every junction is an occlusion: wrap over both mouths and over the
  left tail's end, cross band over the wrap, fold flap over the cross band, bottom tail over
  the wrap's lower end, plus a gathered crease across each join.

## What is not cured, and open

- **The knot reads as overlapping capsules, not yet as cloth tied once.** The crossings exist
  geometrically and every junction has a break, but a reader still sees tube ends meeting at
  the knot; the wrap's ends are covered by the lobes only partly. This needs a further
  construction pass on the wrap's route, not tuning.
- **The left tail is still nearly straight** between the frame edge and the lobe; it tapers and
  folds over at the knot, but its run is a shallow curve rather than a limp ribbon.
- No image review exists for this revision and none is claimed here.

## Files

`source/` (the build), `tests/`, `artwork.svg` + `artwork.png` (800x560), `check/` (the
reviewer's bundle, 1:1 image first), `manifest.json` + `manifest.sha256`.
