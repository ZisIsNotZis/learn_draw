# A-bow-study-v2 — one ribbon, retuned turns (state after the r2 review repairs)

Object study for round R1a of the A track: the bow alone, filling an 800x560 canvas. One
continuous ribbon walked once — left tail, knot wrap, left lobe (out and back), band over the
knot, right lobe (out and back), lower tail — with one width field, one depth field and one
roll field along it. The support surface is a spine in 3D plus those three scalar fields; the
picture is compiler output, an orthographic projection with visibility taken from depth.

This file replaces v1's README, which was byte-identical here (`sha256 46e772ff…`) and
described a drawing this source no longer emits. What follows is what this source emits,
measured on the emitted geometry, plus what was **not** done. Read the "State" section before
trusting any number in it.

## State — read this first

This package is **not complete**: the width law and the tail's piece boundary both hold, and
every artefact here is rebuilt from this revision, but the six defect tests the R1a contract
demands are still not written.

## State — read this first

| item | state |
| --- | --- |
| inherited test suite (17 tests, unmodified assertions) | **17 pass, 0 fail**: worst width isolation 2.69 px against its 3.0 px limit |
| six tests, one per defect named by the v1 image review | **not written** (0 of 6) |
| negative-control output for the crossing-break mechanism | written, `tests/negative-control-output.txt`, mutation 19/19 fails |
| build reproducible from committed source | `source/build.py --out /tmp/a2.svg` is byte-identical to `artwork.svg` |
| delivered PNG | a fresh `scripts/draw render artwork.svg` of the delivered SVG |
| `check/` bundle | emitted by `scripts/draw check artwork.svg --outdir check`, 1:1 image listed first |
| manifest | `manifest.json` + `manifest.sha256`, written over the real file set |
| art verdict | **absent**. No image review of this build exists, and I do not award one (AGENTS.md rule 7) |

## What changed from v1 (and from the r2 partial build)

1. **The turn radius was retuned against the cloth.** At a 180-degree turn the ribbon's inner
   edge has radius `R_FOLD - H_FOLD`. Measured on the r2 build that radius was 8 px, so the
   triangles fanning out of it had altitudes down to half a pixel: what the renderer emitted
   for them was their 2.6 px outline, and a fan of outlines is the hatch the v1 review saw at
   the lower right. `R_FOLD` 46 → 38 and `H_FOLD` 38 → 34 put the inner edge 4 px out.
2. **The triangle inflation was removed.** The r2 build grew every triangle 0.8 px about its
   own centroid to close the renderer's antialiasing seams. That moved the emitted geometry,
   which is the geometry the width tests measure: it put a 9 px isolation spike in the width
   series and flipped the winding of two near-degenerate triangles. The seam is now closed by
   the stroke, at a width that never exceeds twice the triangle's own smallest altitude.
3. **A quad has one depth.** The two triangles of one cross-section were sorted into painter
   order by their own mean depth, so which of them came first — and therefore what a reader
   can measure on the emitted polygons — depended on the field's local slope. Both triangles
   of a quad now carry the quad's depth.
4. **Each visit of the strip has its own depth level.** The old field interpolated through
   three levels and left six crossings closer than one cloth thickness. The six levels below
   put every one of the 17 audited crossings at least 40 px apart.
5. **The knot is crushed and the lobes gather into it.** The returning limb of each lobe now
   climbs back towards the knot's centre (`GATHER`) instead of running parallel to its
   outbound limb, so a lobe is a lens and the knot is a waist between two lenses rather than
   the widest part of a sausage. Widths through the knot: `H_KNOT`.
6. **The lower tail hangs in front of the right lobe** instead of behind it, so its rails run
   from the knot to the frame edge unbroken instead of stopping at a horizontal ledge.
7. **The fold's pinch is stated once.** The right fold's width was crushed at the band's end
   (`0.92` of the band's route length) *and* at the fold turn's own middle, so the band's
   belly had to be reached in 16 stations and given back in 15. Two cosine ramps that short
   turn the emitted width series at `(pi^2/2)(dh/N^2)` = 1.9 + 2.1 half-width px per station²
   at their apex: an isolation of 3.58 px, which the continuity test read as a piece boundary.
   The pinch now has one home, the fold turn's middle, matching the left fold's `P(3, 0.5)`;
   the band's belly keeps its value and gains 36 stations to fall over.
8. **The tail's three knots are three knots.** `_knot_at(parts, k, frac)` read part `k`'s end
   off `parts[k + 1]` and returned `1.0` for the last part, so every fraction inside the lower
   tail collapsed onto the strip's end and its three width knots landed on one station — a
   90 half-px step the continuity test could not see at the series boundary. The last part now
   walks its own span (`parts[k]` … `1.0`), so the tail's width series is the one the source
   declares (width range 62.1…300.0 → 63.8…300.0 px, stations 621 → 620, crossings 17 → 19).
9. **The tail's depth level is where its own geometry is.** With the tail's width no longer
   collapsing, its rails at the junction are 182 px wide and sweep across the knot, within
   0.3 px of the wrap's depth; the swing therefore moved to where the ribbon is crushed to
   `H_KNOT`, and the tail's level is `-6.25` cloth thicknesses instead of `-3.75`, so it reads
   in front of everything it crosses.

## Measured on this build (emitted geometry, not source literals)

| quantity | value | how it is measured |
| --- | --- | --- |
| ribbon | one strip, 620 stations, 1240 triangles, 6 route runs + 3 turns | `bow.build()` |
| triangles disagreeing with their own winding | **0 of 1240** (1171 front, 69 back) | polygon area sign vs its `class` |
| strip width | 63.8 … 300.0 px, ratio **4.70** (floor 4.0) | `tests/test_ribbon_continuity.py` |
| steepest width step | 18.44 px = 6.1 % of the widest | same |
| worst width isolation | **2.69 px** against the 3.0 px limit | same |
| knot waist | narrowest in the band 64.0 px, loops median 140.8 px = **0.45** (limit 0.55) | same |
| knot position | narrowest column chord at x = 540 of the emitted cloth's x 0…749 = **0.72** of its width | column chords of the union of the emitted fills |
| enclosed background islands inside the lobes | **0** of area > 40 px² | connected components of the filled mask, border-reachable = outside |
| audited self-crossings | **19**, all with a depth break and a broken rear edge; mutation `--no-depth-break` fails 19/19 | `tests/test_crossing_break.py` |
| sub-pen triangles (narrower than the pen) | 93 of 1240, each stroked at 2x its own altitude, never at the seam width | `build.resolve()["slivers"]` |
| rail runs / crease runs emitted | 12 / 6 | `source/build.py` |

## The fields (author choices, with the radii they cost)

Cloth thickness 16 px is the minimum depth break. Depth is in canvas px, negative = nearer.

| name | value | what it is |
| --- | --- | --- |
| `R_FOLD` | 38 | turn radius at each lobe's fold |
| `H_FOLD` | 34 | ribbon half-width through a fold (inner edge 4 px) |
| `R_WRAP` | 62 | turn radius of the knot's wrap |
| `H_KNOT` | 32 | ribbon half-width through the knot — the one crushed place |
| `GATHER` | 0.45 | how far a lobe's returning limb climbs back toward the knot |
| `THICKNESS` | 16 | one cloth thickness |
| `TAIL_IN` | +60 | left tail, behind the knot |
| `WRAP` | −60 | the knot's wrap, over everything |
| `LOBE_OUT` | −40 | each lobe's outward limb |
| `LOBE_RET` | +40 | each lobe's returning limb |
| `BAND` | −20 | the band crossing the knot, over both returns |
| `TAIL_OUT` | −60 | the lower tail, in front of the right lobe |

Every level is separated from its neighbours by at least 2.5 cloth thicknesses, and the swing
between two levels is placed inside a turn, which is the one place the ribbon really does turn
over. One hand-typed position: the route's first point, `(-95, Y_RETURN + 32)`; every other
point is generated by `Route.run` / `Route.turn` from lengths, angles and radii.

## Measured target vs author choice

Measured from the reference crop (bow bbox `(33,134)-(271,285)`, 239x152, registered to
`image.jpg` bbox `500,320,900,800` and scaled into this canvas): bow aspect 1.57; the knot's
waist at 0.706 of the bow's width; lobes 81:63 = 1.29; fill `#ce4e7e`, fold shadow `#67233d`,
background `#77c8c0`. Author choices: everything else — the radii, the width field's knots,
the gather, the depth levels, the crease table, the roll field, and both tails' routes.

The knot's measured 0.706 is what `KNOT_X` was composed around; this build puts the narrowest
column at 0.72 of the emitted width. That is a comparison of two different measurements (the
reference's waist column vs this drawing's narrowest column chord) and it is **not** a claim
that the knot matches the reference's shape.

## What I did not verify, and what is open

- **The six defect tests do not exist.** The v1 image review named six defects; this build
  changes the geometry behind four of them, but no test asserts any of the six and no negative
  control restores v1's behaviour to make one fail. That is the largest gap in this package
  and it is the next writer's first job.
- **The width isolation test now passes** (2.69 against 3.0, was 3.58). The old reading —
  "the lobes' and the fold's fullness have to be reached inside a route part that is only
  0.034 of the strip long, so the field needs more length" — was wrong about the mechanism:
  the field did not need more length, the pinch was stated twice. The route, the turn count
  and the loop count are unchanged.
- **A second piece boundary is still in the width field, and it is not visible to the emitted
  series.** `_knot_at(parts, 8, frac)` returns 1.0 for `k = 8`, so the lower tail's three width
  knots (`P(8,0.12)=H_KNOT`, `P(8,0.45)=96`, `(1.0,122)`) all land at `u = 1.0` and the tail
  tapers 92 → 32 instead of being crushed and then broad as the source says. The strip's
  last station therefore carries a 90 half-width px step (`h[619]=32.0`, `h[620]=122.0`) that
  the width series cannot see, because the series samples station starts and stops at 619.
  Fixing it changes the tail's silhouette and the emitted width range; it is a separate
  judgement and was not taken here.
- **The image still carries defects I can see and have not closed**: a fan of thin dark
  wedges inside the left lobe at its fold, a crumpled crossing at the knot, and a pointed
  peak at the top centre. Whether they still read as the v1 review's defects is a reviewer's
  question, not mine.
- The route table, the crease table with endpoints, and the self-check against the
  art-direction brief's bow criteria (items 5, 6, 7), which the study contract requires, are
  **not written** here.
- No image review of this build exists. Nothing here is an art verdict, and the words for a
  judgement of the picture are not used in this file.

## Commands

```bash
cd .scratch/35-r1-articulated-study/evidence/A-bow-study-v2
PYTHONDONTWRITEBYTECODE=1 ../../../../.venv/bin/python -m unittest discover -s tests -t .   # 17/17
../../../../.venv/bin/python source/build.py --out /tmp/a2.svg && cmp /tmp/a2.svg artwork.svg
../../../../scripts/draw render artwork.svg -o artwork.png
../../../../scripts/draw check artwork.svg --outdir check
../../../../.venv/bin/python source/manifest.py --check
sha256sum -c manifest.sha256
```

Files: `source/` (the build), `tests/`, `artwork.svg` + `artwork.png` (800x560), `check/`
(the reviewer's bundle, 1:1 image first), `manifest.json` + `manifest.sha256`.
