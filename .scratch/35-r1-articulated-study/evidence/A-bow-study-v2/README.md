# A-bow-study-v1 — one ribbon, filling the frame

Object study for round R1a of the A track. The user's approved shape: draw **only** the bow, at
large scale, because a 400x480 figure is beyond what this vocabulary composes readably while one
object at 800x560 is not. No figure, no torso, no sleeve, no hair, no lap.

The drawing is one continuous ribbon tied in a bow: the strip enters the frame on the left as a
tail, wraps over the knot, runs out to the left loop and back, crosses the knot, runs out to the
right (smaller) loop and back, and leaves the frame downwards as the second tail. Every lobe,
fold and knot pass is a piece of that one strip. The support surface is a spine in 3D plus three
scalar fields along it, and the finished picture is compiler output: an orthographic projection
with visibility taken from depth.

## What it must read as (the reviewer's question, not mine)

An independent reviewer answers this from `check/` alone, starting with `check/draft-fullres.png`:
a knot where the ribbon wraps and crosses itself, two lobes with curved free edges opening away
from the knot, two tails leaving the frame, and creases that follow real folds. Failure readings
to avoid: "two closed pills", "a bowtie", "a flat sticker", "a crumpled paper bag", "two lobes
joined by a chord". **I do not award that verdict**; this package only makes it answerable.

## Object inventory

| element | how it is made | where |
| --- | --- | --- |
| ribbon spine | 9 generated segments: 6 cubic runs + 3 180-degree turns, walked forward from one point | `source/parts/bow.py` `_route()` |
| strip surface | 621 stations resampled by arc length; rails at centre ± half-width along the strip's own across vector | `source/ribbon.py` `Strip` |
| left loop | run out, 180-degree fold turn, run back | route parts 2–4 |
| right loop (smaller) | run out over the knot, 180-degree fold turn, run back | route parts 5–7 |
| knot | the wrap turn (part 1) plus the band (part 5) passing over the loops' returning limbs | route parts 1 and 5 |
| left tail | part 0, leaves the frame at x = -70 | route part 0 |
| lower tail | part 8, leaves the frame at y = 552 | route part 8 |
| creases | 7 marks authored in the strip's own (u, v), sampled across it and curved along it | `CREASES` |
| visibility | 1240 triangles rasterised into a depth buffer; strokes clipped where a nearer part of the same ribbon covers them | `source/ribbon.py`, `source/build.py` |
| face colour | each triangle's own projected winding decides front or back | `source/build.py` `resolve()` |

### The route, visit by visit (u is arc-length fraction along the strip)

| visit | u | what the ribbon is doing | depth (px, negative = nearer) | half-width (px) |
| --- | --- | --- | --- | --- |
| 0 | 0.000–0.234 | left tail, off frame at x=-70 across to the knot | +36 | 15 → 40 |
| 1 | 0.234–0.301 | knot wrap: a 180-degree turn that climbs from behind to in front | +36 → −28 | 22 → 40 |
| 2 | 0.301–0.363 | left loop, outward limb, over the top to the fold | −28 → 0 | 35 → 90 |
| 3 | 0.363–0.525 | left loop fold, 180 degrees | 0 → +16 | 34 → 89 (pinches) |
| 4 | 0.525–0.593 | left loop, returning limb, back to the knot | +16 | 90 → 96 |
| 5 | 0.593–0.707 | the band crossing the knot, rising to the right loop | +16 → 0 | 50 → 101 |
| 6 | 0.707–0.830 | right loop, fold, and returning limb | 0 → +16 | 31 → 97 |
| 7 | 0.830–0.852 | right loop, returning limb at the knot | +16 | 92 → 99 |
| 8 | 0.852–1.000 | lower tail, out of the frame at y=552 | +16 → +36 | 46 → 17 |

One spine, one width field, one depth field, one roll field. Nothing is a separate piece: there is
no knot patch, no lobe solid and no tail slab, and the build cannot express one.

## The width field

One field of `(u, half-width in canvas px)`, cosine-interpolated, so it is continuous by
construction and any taper is a statement about the whole ribbon rather than a per-piece width:

```
u 0.000 15 | 0.129 30 | 0.234 40 | 0.264 22 | 0.301 34 | 0.331 90 | 0.357 69 | 0.363 45
  0.444 34 (fold pinch) | 0.525 95 | 0.593 96 | 0.656 101 | 0.707 50
  0.775 31 (right fold pinch) | 0.830 99 | 0.852 82 | 0.949 46 | 1.000 17
```

The ribbon is gathered where it turns: at each fold and at the knot the half-width drops well
below the turn's radius, because a strip wider than its turn's radius has its two rails crossing
at the inside of the turn (measured at the first build: a fan of hairline triangles at both folds
until the field was narrowed there). `tests/test_ribbon_continuity.py` measures the emitted strip,
not this table: continuity, the absence of an isolated one-station jump, that the width varies at
all, and that the knot band is a waist between the loops.

## The crease table

Seven marks, each authored as a point in the strip's own surface coordinates `(u, v)` with a small
curvature so it follows the fold instead of chording across it, sampled at 13 points across the
strip, and clipped by the same depth buffer as the rails. `(x, y)` are the emitted canvas ends.

| # | anchor (route part, fraction) | u | v start → end | emitted (x,y) → (x,y) | what fold it follows |
| --- | --- | --- | --- | --- | --- |
| 0 | 1, 0.46 | 0.264 | +0.80 → −0.80 | (491,234) → (525,239) | the gather where the knot band closes on itself |
| 1 | 1, 0.76 | 0.284 | +0.55 → −0.55 | (479,215) → (492,187) | the second turn of the wrap |
| 2 | 2, 0.58 | 0.337 | +0.80 → −0.28 | (344,193) → (396,141) | the crease running out of the left fold |
| 3 | 4, 0.34 | 0.548 | +0.86 → +0.10 | (341,221) → (373,285) | the returning limb's fold, out of the knot |
| 4 | 5, 0.58 | 0.659 | −0.45 → +0.60 | (619,215) → (567,133) | the band crossing the knot, folded along its length |
| 5 | 7, 0.38 | 0.838 | +0.20 → −0.80 | (634,317) → (662,223) | the right loop's returning limb |
| 6 | 8, 0.32 | 0.903 | +0.58 → −0.22 | (446,552) → (479,552) | the fold where the lower tail leaves the knot |

No mark is a long straight chord across a lobe: the longest spans 74 px of the 800 px canvas and
each is a cross-strip fold line, 0.9 to 1.6 of the strip's own width in v. A mark that runs off
the visible strip is clipped by depth like any other stroke, so no mark terminates at nothing.

## The depth separation table

Cloth thickness `THICKNESS = 16 px`; every crossing must step by at least that much. Levels:
`WRAP = −28` (knot band, nearest), `FRONT = 0` (outward limbs), `MID = +16` (returning limbs),
`BACK_TAIL = +36` (tails, furthest).

| crossing (emitted x,y) | front visit / depth | rear visit / depth | separation |
| --- | --- | --- | --- |
| (164,260) | the loop's returning limb, +9 | the left tail, +30 | 21 px |
| (337,208) | left loop, FRONT, 0 | left loop, returning limb, +16 | 16 px |
| (451,162) | knot band, −28 | left loop outward limb, 0 | 28 px |
| … | 10 crossings found and audited in total | | ≥ 16 px |

`tests/test_crossing_break.py` finds every place two rail segments from *different visits* of the
strip cross in 2D, then requires two things of each: at least one cloth thickness of depth between
the two surfaces, and **no emitted stroke of the rear rail running through that station**. The
build's negative control (`--no-depth-break`) removes the depth separation and emits every stroke
unbroken; the same audit then reports 10 failures (P37: the mechanism is what makes the test pass).
`tests/negative-control-output.txt` records both counts.

## What is a measured target and what is an author choice

Measured targets, scaled from the registered crop `image.jpg` bbox `500,320,900,800` by
`work/a-measure-crop.py` (canvas scale 3.28 = 800 / 244):

| quantity | reference (crop px) | canvas target | this drawing | verdict |
| --- | --- | --- | --- | --- |
| bow bbox aspect | 239 × 152 = 1.57 | 1.57 | 784 × 497 ≈ 1.58 | hit |
| knot waist height | 59 (0.39 of bow height) | ~193 px | knot band ≈ 150 px tall, 43 px wide | ~ hit (−22%) |
| knot position across the bow | 0.70 of width | x ≈ 559 | x ≈ 500 (0.63) | miss (−10%) |
| lobe width ratio left:right | 81:63 = 1.29 | 1.29 | loop throws 1.30 : 1 | hit |
| lobes solid, free edges curved | 7 interior strokes on a 239×152 object | ≥ 3 creases, curved | 7 creases, all curved | hit |
| fill / fold-shadow values | #ce4e7e / #67233d | same | #ce4e7e front, #67233d back and creases | hit |
| background | mint #77c8c0 at (30,260) | same | #77c8c0 | hit |
| tails leave the frame | left tail 2 px at the frame edge, lower tail off the bottom | two tails crossing the frame edge | left at x=−70, lower at y=552 (both clipped by the canvas) | hit |
| lobe opening | the reference's lobes are solid cloth | no hole inside a lobe | **the left loop shows an opening** (a triangle of background inside the loop) | miss |

The left loop's opening is the loop the ribbon closes; in the reference the lobes read as solid
because the two limbs lie flat against each other. This is the largest known art risk in the
package and it is not hidden.

Author choices (not measured): cloth thickness 16 px, the roll field (how far the strip turns
about its own axis), the two tail routes, the crease table, the canvas scale, and the decision to
keep the ribbon flat except for the lower tail's end.

## Colours and the two faces

A ribbon is two-sided cloth, so both faces carry a measured value from the same palette:
front `#ce4e7e` (bow fill, measured at (140,175) of the crop) and back `#67233d` (the fold shadow
on the same ribbon, measured at (140,205)). Each triangle takes its colour from the sign of its
own projected winding, so the rule is exercised by geometry: the lower tail hangs turned over
(roll to 152 degrees) and shows the back in 22 of 1240 triangles.
`tests/test_fill_and_build.py` recomputes the sign of every emitted triangle and requires the
colour to agree, and requires both faces to occur — a rule with one possible answer is not a rule.

## Exact commands

```bash
cd .scratch/35-r1-articulated-study/evidence/A-bow-study-v1

# build the drawing (deterministic: no clock, no randomness, no reference)
../../../../.venv/bin/python source/build.py                    # -> artwork.svg
../../../../.venv/bin/python source/build.py --no-depth-break   # -> negative control

# render it through the project's renderer
../../../../scripts/draw render artwork.svg -o artwork.png

# the reviewer bundle, reference-free: the 1:1 image is listed first
../../../../scripts/draw check artwork.svg --outdir check

# tests
../../../../.venv/bin/python -m unittest discover -s tests -t .
../../../../.venv/bin/python -c "import sys; sys.path[:0]=['source','source/parts','tests']; \
    import test_crossing_break as T; print(T.negative_control())"

# the manifest
../../../../.venv/bin/python source/manifest.py --check
sha256sum -c manifest.sha256
```

## Self-check against the brief's bow criteria

Brief `work/a-art-direction-brief.md` section (c) "Bow", and checklist items 5, 6 and 7.

| criterion | how this drawing satisfies it | evidence |
| --- | --- | --- |
| **one continuous ribbon**: one spine visiting knot → left lobe → knot → right lobe → knot → two tails, one width field, no separate knot patch or lobe solids | the whole object is one 9-segment route and one triangular chain; the two tails are the spine's two ends, so the cycle reads knot → left loop → knot → right loop → knot with the tails at the ends of the same strip | `source/parts/bow.py` `_route()`; `tests/test_ribbon_continuity.py` (monotone evenly-spaced stations, shared quad boundaries, one continuous width field) |
| **lobe overlap and the wrapped knot come from depth**, not declaration order or an authored cut | outbound limb at z=0 over the returning limb at z=+16; knot passes at −28 / +16 / +36, every step ≥ one cloth thickness; strokes are clipped by a depth buffer, so nothing declares what is visible | `tests/test_crossing_break.py` — 10 crossings, each with ≥16 px of depth and a broken rear edge; `tests/negative-control-output.txt` — the same test fails 10/10 when the break is removed |
| **creases are authored marks on the strip surface**, short, following a fold, clipped by depth; no long chord, no mark ending at nothing | 7 marks authored as `(u, v)` on the same surface parameterisation, curved along the fold, sampled across the strip, clipped by the same depth buffer | crease table above; `source/parts/bow.py` `CREASES`; `source/build.py` crease clipping |
| **where the ribbon crosses itself the rear edge is BROKEN** | depth-clipped strokes plus a locally-nearest depth test so a rear stroke is broken even where the front *edge* covers it | `tests/test_crossing_break.py` (assertion + mutation) |
| **both faces differ, fill from each triangle's own winding** | front `#ce4e7e`, back `#67233d`; 22 back-facing triangles on the turned-over lower tail | `tests/test_fill_and_build.py` |
| **geometry computed, not eyeballed**: no shape with more than ~4 hand-typed coordinates | one hand-typed position (the left tail's start, `(-70, 300)`); every other point comes from run lengths and angles, turn radii, and the three fields. Points handed to a generator as *targets* (`end=(…)`) are composition, and no shape carries more than the two ends of one run | `source/parts/bow.py` `_route()` — 1 literal position + 6 runs + 3 turns |
| **no reference at runtime** | no source imports an image library, no source reads the crop; the build's bytes are identical when run from another directory | `tests/test_package.py::TestNoReferenceAtRuntime` |
| **checklist 5** a viewer can name it as a bow with a knot, two lobes and two tails | the picture shows the knot band crossing the loops, two loops with curved free edges, and two tails leaving the frame | `check/draft-fullres.png` — reviewer's call, not mine |
| **checklist 6** at least three separate interior creases, one where the ribbon turns at the knot, and an area noticeably darker than the fill | 7 creases, two of them at the knot's turns; the back face and the crease value are #67233d against #ce4e7e | crease table; `tests/test_fill_and_build.py` |
| **checklist 7** no lobe outline closing on itself independent of the knot, no rear outline drawn through a crossing | there is no lobe outline: the rails are the one strip's two edges, and every rear rail is broken at every crossing | `tests/test_crossing_break.py` |

## What is unverified, and what is a known miss

- **The art verdict.** Unverified by design. A fresh image reviewer gets `check/` and nothing else.
  I cannot certify that it reads as a ribbon bow rather than as "a crumpled paper bag"; the seams
  at the two folds were the worst of that reading and are now narrow, not absent.
- **The left loop's opening** — a triangle of background inside the loop — is the clearest
  departure from the reference (whose lobes are solid cloth). It comes from the loop being thrown
  wider than the limbs are thick; closing it means either a shorter throw or thicker limbs, and
  both are composition decisions I did not take unilaterally.
- **The knot's position** is at 0.63 of the bow's width against the measured 0.70, and the knot
  band is ~22% shorter than the measured waist. Both are outside or at the edge of the brief's
  ±20% band.
- **The interior crease count is right but their placement is unmeasured against the reference's
  seven strokes**: the reference's endpoints were not transcribed, because a traced coordinate is
  not an authored one.
- **The right fold still shows a small wedge of hairline triangles** where the ribbon turns at a
  tight radius; the left fold's is gone. Visible at 1:1 as a slight darkening, not as a fan.
- The canvas is filled by the object in width (784 of 800 px) but not in height (497 of 560);
  the brief asked for the object to fill the frame, and the vertical margin is 26 px at the top and
  37 px at the bottom of the *bow's* bbox, with the lower tail running out of the bottom.
