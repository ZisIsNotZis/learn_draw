# B-hand-study-v1 — one hand supporting one shallow dish, filling the frame

Object study for round R1a of the B track, under
[`work/r1a-object-study-contracts.md`](../../work/r1a-object-study-contracts.md). The user's
approved shape (issue 55): draw **only** the hand and the dish, at 900x700, because a figure at
figure scale is beyond what this vocabulary composes readably while one object at study scale is
not. No torso, no head, no shoulder, no body connection: the wrist leaves the bottom edge of the
frame and nothing is drawn beyond it.

The drawing is one hand holding one shallow dish from below. The dish is a surface of revolution:
a shallow elliptical bowl inside, a flat rim band with thickness, a curved outer wall, an
underside. The hand is one flattened palm mass and five tapered tubes — four fingers and a thumb
— every one of which is swung from the **dish's own emitted rings**, not drawn next to it. The
picture is compiler output: an orthographic projection, flat-shaded from each quad's own normal,
with every stroke clipped by a depth buffer.

**This package awards no art verdict.** A fresh sight-capable reviewer judges
`check/` and nothing else; `check/report.txt` carries the reviewer protocol. This study is run as
*never run*: earlier attempts at `B-hand-study-v1` left no artefact, no commit and no branch (see
`mail/2026-10-21-orientation.md` §(b)), so nothing here is a repair of anything.

## What it must read as (the reviewer's question, not mine)

A hand supporting a shallow dish from below: the dish's underside meets the palm and fingers, the
digits curl around the dish rather than standing as prongs in front of it, a thumb opposes on the
near side, and the dish reads as a vessel. Failure readings to avoid: fingers as rake tines, a hand
intersecting a plate, the dish balanced on the fingertips, a flat lens with one rim.

## Construction vocabulary

| element | how it is made | where |
| --- | --- | --- |
| dish | one authored `(radius, height)` profile — five corners and four arcs — revolved 60 times | `source/dish.py` `profile()`, `build()` |
| rim with thickness | the profile's flat band between the two folds: 44.9 px of thickness measured on the emitted mesh | `dish.derived_rings()` `rim_outer` / `rim_inner` |
| inner wall + bowl | a quarter-ellipse from the rim's inner fold down to the axis, 90 px deep at the floor | `dish.profile()` bowl span |
| underside | a quarter-ellipse from the axis out and down to the foot ring, the lowest ring of the outside | `dish.profile()` under span |
| palm | one tapered tube, elliptical cross-section (thin 0.58): a wrist off the bottom edge, a mid mass, a rounded distal end landing on the dish's foot | `contact.palm()` |
| finger | four knots and a radius law: root on the palm's knuckle line, then the dish's wall ring, the rim's outer fold and the rim's band; rounded end | `contact.finger()` |
| thumb | the same primitive, thicker and shorter, rooted on the palm's far flank, tipped on the rim's band 21° away from the fingers | `contact.finger()` via `scene.THUMB` |
| fills | each quad's own outward normal through a Lambert law, shade continuous | `source/build.py` `fills()` |
| contours | zero set of (vertex normal · view) per patch, by marching squares on the emitted grid, then kept only where the drawing stops | `source/geo.py` `Patch.silhouette()` |
| folds | mesh edges whose two faces differ by more than 55° | `geo.Patch.creases()` |
| visibility | front-facing quads rasterised into a depth buffer; every stroke is emitted only where its own surface is the nearest thing at that pixel | `geo.depth_buffer()`, `build.visible_runs()` |

Coordinates: every authored number is a pose parameter in `source/scene.py` (a ring station on the
dish, a digit's radii, the palm's length). The only literal positions are the palm's wrist and mid
points, which are outside the dish's frame of reference; everything else is generated.

## Contact derivation — a distance, not a claim

`dish.derived_rings()` finds the dish's real edges by looking at the built mesh: the profile rows
where the surface turns by more than 30° are grouped into folds, and the two folds nearest the top
of the dish are its rim — the wider is the rim's outer edge, the narrower its inner edge. The foot
is the lowest ring of the outside. The outer wall's intermediate rings are interpolated between
the foot and the rim's outer fold. **No index of `profile()` is shared with the hand**, so moving
the profile cannot silently move the hand.

Every digit is then placed against those rings, pushed along the ring's own *surface normal* by the
digit's own radius plus one stated clearance:

| digit | knots | what the knot is |
| --- | --- | --- |
| index, middle, ring, little | root, wall, rim outer, rim band | root = the palm's knuckle line; the other three = dish rings at that digit's station, offset by its radii |
| thumb | root, wall, rim band | same, 21° away, thicker, reaching 0.16 of the way across the rim's band |

`tests/test_hand_construction.py::TestContact` re-derives the rim's band from the mesh **in the
test**, with its own fold detection at its own threshold, and measures each digit's last
cross-section against the band's plane:

| digit | tip, px from the rim's band plane | clearance declared |
| --- | --- | --- |
| index | 3.20 | 1.5 |
| middle | 2.43 | 1.5 |
| ring | 3.81 | 1.5 |
| little | 2.19 | 1.5 |
| thumb | 5.12 | 1.5 |

The tip's own ring is the measurement: its minimum height above the band is the digit's closest
approach, i.e. its clearance, and a negative minimum would be the digit sunk into the rim. The
measured values sit a little above the declared clearance because each tip rests on the *blended*
ring between the rim's two folds, whose normal is tilted relative to the band's plane; the
assertion is `> -1 px` (no penetration) and `< clearance + 4 px` (resting, not hovering). Three
mutations make the check bite: a hand lifted 20 px clear of the rim (measured 22.92 px, fails), two
fingers placed on one rim station, and the dish's own rim radii changed by 26 px, after which the
fingertip moves 22.7 px with it and still rests on the new band.

**What the drawing shows of that contact is a different question from whether it is true.** The
palm's distal end meets the dish's foot underneath the dish, where the dish's own near wall hides
it; the contact is therefore *true in the geometry and largely invisible in the image*. What the
image shows is the digits wrapping the near rim, and the palm's mass below and in front of the
dish's near silhouette. Whether that reads as support is the reviewer's question, not mine.

## Digit separation — at the roots and at the distal halves

Measured on the emitted station rings of each digit, as a fraction of the two digits' mean width on
screen (`util.station_gap` / `util.width_at`):

| pair | roots (station 0.15) | distal halves (station 0.60) |
| --- | --- | --- |
| index–middle | gap 3.2 / width 58.9 = **0.05** | gap 25.1 / width 53.1 = **0.47** |
| middle–ring | gap 0.7 / width 59.3 = **0.01** | gap 44.8 / width 52.9 = **0.85** |
| ring–little | gap 2.0 / width 51.7 = **0.04** | gap 48.1 / width 46.6 = **1.03** |

**The roots are merged, and that is stated rather than hidden:** at the knuckles the digits are
within 0.05 of a digit's width of each other, which is why they read as one mass leaving the palm,
and the test *requires* it (`≤ 0.10`). At the distal halves they are separated by 0.47 to 1.03 of a
digit's width and the test requires `≥ 0.30`. Six crossings between ink curves of different digits
have under `MIN_SEP = 6 px` of depth between them: those are contacts (the merge, and fingertips on
the rim), they are counted and reported by the occlusion audit, and no edge is expected to vanish
at one.

Taper, measured the same way: width at station 0.15 → 0.90 is 51.7 → 25.1 (index, ratio 0.49),
57.0 → 28.9 (middle, 0.51), 52.4 → 26.6 (ring, 0.51), 43.0 → 20.1 (little, 0.47), 77.0 → 39.8
(thumb, 0.52). Floor: `≤ 0.75` of the base width.

## Occlusion — the rear edge is absent, not painted over

Strokes are emitted in a pass *after* the fills, so the only reason a rear edge is missing from the
drawing is that the depth test removed it. `tests/test_occlusion_break.py` finds every 2D crossing
between ink curves of two different parts, and for each crossing with at least one depth-thickness
of separation requires the rear curve's stroke to be absent at that station in the delivered SVG.

| build | occlusions audited | failures | contacts |
| --- | --- | --- | --- |
| delivered (`artwork.svg`) | 74 | **0** | 6 |
| mutation (`--no-depth-break`) | 74 | **74** | 6 |

`--no-depth-break` emits every stroke whole. The same audit then reports a rear edge drawn through
all 74 occlusions, so the mechanism — not paint order, not luck — is what makes the test pass. Both
counts are recorded in `tests/negative-control-output.txt`.

## What is a geometric consequence and what is an author hypothesis

| # | claim | kind | evidence |
| --- | --- | --- | --- |
| 1 | Every digit's tip rests on the dish's rim band, one digit-radius plus 1.5 px above it, and none penetrates it. | geometric consequence: the tip is placed from the dish's derived ring along that ring's normal | `TestContact::test_every_digit_rests_on_the_band_and_none_penetrates_it` (+ the +20 px mutation) |
| 2 | The hand follows the dish: change the dish's rim radii and every digit moves with it. | geometric consequence | `TestContact::test_the_hand_follows_the_dish` (+26 px rim → tip moves 22.7 px) |
| 3 | The rim has thickness (44.9 px), a flat band (its normal is 0.0° off the dish's axis), an inner wall 90 px deep and an underside below the rim. | geometric consequence, measured on the emitted mesh | `TestDishStructure`, `TestContact::test_the_band_is_a_rim_with_two_edges` |
| 4 | The digits are merged at the roots (≤ 0.05 of a width) and separated at the distal halves (0.47–1.03). | geometric consequence, measured on the emitted rings | `TestSeparation` (+ the same-station mutation) |
| 5 | Every digit tapers toward its tip (ratio 0.47–0.52). | geometric consequence | `TestDigitsTaper` |
| 6 | Every stroke is a computed contour or a computed fold; no stroke is authored, and the digits carry no fold at all. | geometric consequence of the emitter | `TestNoDrawnForm` (a recorder proves the emitter's only sources are the mesh's contours and folds) |
| 7 | Which rim station each digit takes, the 0.16–0.88 reach across the rim's band, the digit radii, the palm's length and its wrist entry, the dish's five profile corners, the tilt of 12°, the palette and the light direction. | **author hypothesis** (pose and proportion) | not measurable here |
| 8 | That the picture reads as a hand supporting a dish, with the dish's underside visibly meeting the palm, the digits curling around it, and a thumb opposing on the near side. | **author hypothesis** | **unverified** — no reviewer has judged it; see "What is unverified" |

## Files

- `source/geo.py` — camera, grid meshes, vertex normals, marching-squares contours, fold detection, depth buffer, shading.
- `source/dish.py` — the dish's profile and revolution; `derived_rings()`, the rings the hand is hung from.
- `source/digits.py` — one primitive: a tapered tube swept along a centreline with a parallel-transported frame.
- `source/contact.py` — where each digit meets the dish: ring, normal, radius, clearance.
- `source/scene.py` — every hand-typed number in the drawing, and nothing else.
- `source/build.py` — the compiler: fills, strokes, visibility, SVG.
- `source/manifest.py` — `--write` / `--check` over the real file set.
- `tests/` — 23 tests, the occlusion negative control, and `negative-control-output.txt`.
- `artwork.svg`, `artwork.png` (900x700) — the drawing.
- `check/` — the reference-free `scripts/draw check` bundle; the 1:1 image is listed first.
- `manifest.json`, `manifest.sha256` — the file set, hashes and sizes.

## Exact commands

```bash
cd .scratch/35-r1-articulated-study/evidence/B-hand-study-v1

# build the drawing (deterministic: no clock, no randomness, no reference)
../../../../.venv/bin/python source/build.py                     # -> artwork.svg
../../../../.venv/bin/python source/build.py --no-depth-break    # negative control
../../../../.venv/bin/python source/build.py --lift 30 --out /tmp/lifted.svg   # optional, see below

# render it through the project's renderer
../../../../scripts/draw render artwork.svg -o artwork.png

# the reviewer bundle, reference-free: the 1:1 image is listed first
cd ../../../.. && scripts/draw check .scratch/35-r1-articulated-study/evidence/B-hand-study-v1/artwork.svg \
    --outdir .scratch/35-r1-articulated-study/evidence/B-hand-study-v1/check

# tests (23), from the evidence directory
cd .scratch/35-r1-articulated-study/evidence/B-hand-study-v1
../../../../.venv/bin/python -m unittest discover -s tests -t .

# the occlusion negative control, which rewrites tests/negative-control-output.txt
../../../../.venv/bin/python -c "import sys; sys.path[:0]=['source','tests']; \
    import test_occlusion_break as T; print(T.negative_control())"

# the manifest
../../../../.venv/bin/python source/manifest.py --check
sha256sum -c manifest.sha256
```

## What is unverified, and what is a known limitation

- **The art verdict.** Unverified by design. A fresh image reviewer gets `check/` and nothing else.
  I cannot certify that the hand reads as a hand supporting a dish rather than as digits hooked over
  a plate; the reader should also check the four failure readings in the contract.
- **The palm reads as one mass, not as an anatomy.** It is one flattened tube with a rounded end.
  There is no separate heel wedge, no knuckle row and no thenar bulge beyond what the thumb's own
  root provides. This is the most likely complaint an image review will raise.
- **The palm's contact with the dish's foot is invisible**: it happens underneath the dish, behind
  the dish's own near wall. The claim in row 1 above is a claim about the geometry, and the README
  says so rather than implying the image shows it.
- **The digits' tips are rounded caps.** At 1:1 each cap reads as a rounded pad; a small fold can
  appear on a cap where two consecutive rings are sub-pixel, which is a mesh artefact rather than a
  drawn mark. Sub-pixel quads are excluded from fold detection (`|cross| ≥ 1 m²`) to keep it rare.
- **Faint radial spokes at the bowl's floor centre**, where the revolution's degenerate apex quads
  are inflated by 0.45 px to close the renderer's antialias seam. Visible at 1:1 as slight
  darkening, not as lines.
- **The optional second image** (the same hand with the dish lifted 30 px, proving the pose is
  parameterised) is implemented — `--lift 30` builds it and the digits stay with the hand — but it
  is **not** shipped, because the contract authorises it only once everything else is complete and
  reviewed.
- The canvas is filled in width by the dish (620 of 900 px) plus the hand, and in height by the
  dish and the wrist leaving the bottom edge; the *object group* remains 140 px narrower than the
  canvas on the left. This is an author choice about framing, not a measured target.
