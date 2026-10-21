# B-hand-study-v1-r1 — repair pass on the failed B hand study (SUITE GREEN 25/25, ART VERDICT PENDING)

This directory is a copy of `../B-hand-study-v1/` (which stays untouched: it is the revision
the archived image review is bound to by hash) carrying one repair pass against
[`../../work/r1a-object-study-contracts.md` § B-hand-study-v1](../../work/r1a-object-study-contracts.md),
the archived verdict
[`../../evidence/reviews-r1a/B-hand-study-v1-image-review-1.md`](../reviews-r1a/B-hand-study-v1-image-review-1.md),
and package E of [`../../work/wave13-contracts.md`](../../work/wave13-contracts.md).

**Read this first: the suite is green, 25 of 25.** Every digit's tip ring rests on the dish's own
underside inside the bounds the contact test already states: the closest vertex of each pad stands
between 1.63 px and 3.92 px off the surface, against the window `> −1.0` and
`< clearance + 4.0` (5.5 px at the stated 1.5 px clearance). The palm's nearest vertex is 1.50 px
from the same surface, and a hand held at the old pose no longer meets a moved dish. The lift
mutation (`clearance + 20 px`) still fails the check at 21.70 px. Two tests were added and none of
the inherited bounds was moved or weakened: `test_the_palm_cap_meets_the_underside` and
`test_the_committed_record_is_this_revision`. This package awards no art verdict and claims none: a
fresh reviewer decides.

## What changed in the construction

The hand is now **under the plate**. Every digit's pad, and the palm's distal end, are placed on
the dish's own **underside rings** — derived from the emitted mesh by `dish.derived_rings()`
(`"under"`, `"axis"`, `"foot"`), interpolated by `contact.underside_ring()`, and offset along each
ring's own surface normal by the part's radius plus the stated 1.5 px clearance. The underside is
the face that carries the plate's weight, so:

- the plate's near rim is nearer to the camera than any hand surface that overlaps it, so no hand
  quad paints in front of the rim (the v1 inversion is gone by construction, not by paint order);
- the palm's distal station is **solved**, not typed: `contact.palm` builds the mass, measures its
  nearest vertex against the dish's own underside and moves the station by the error until the
  closest vertex sits one stated clearance below the surface (it reads 1.50 px; the measured truth
  of the previous revision was 28.05 px, which is what its README wrongly called "meets");
- the digits reach in under the plate and are **cut off by the plate's near silhouette**.

Two other changes are pose/geometry only, both computed:

- **digit variation** (`scene.FINGERS`): uneven stations (228, 254, 286, 316 deg), reaches that
  differ by a third of the underside's radius (0.86, 0.98, 0.94, 0.88), and radii from 33/35/30/25
  down to 17/19/15/12 at the tips — the "rake tines" uniformity the study names is no longer true
  of the numbers, but see the legibility gap below;
- **a knuckle row and a heel**, both as radius-law bulges rather than new parts (the inherited
  `TestParts` fixes the part list at palm + four fingers + thumb + dish): every finger's law peaks
  at t = 0.12 (knuckle, wider than its shaft), and the palm's law peaks at t = 0.18 (heel,
  126 px against 108 at the mid mass);
- **the thumb's root** is the flank of the palm's mid mass that is nearer to the camera, chosen by
  measurement (`min(flank, key=depth)`) rather than typed as "far" or "near";
- **the dish's interior** is tessellated with 33 profile rows instead of 17 (`dish.profile()`),
  which halves the width of the flat-tone banding the review measured. No other shading change
  was landed; see blocker 2 below.

## What this pass changed

Three things, each committed separately:

1. **The review bundle was stale and misrouted.** `check/report.txt` named
   `evidence/B-hand-study-v1/` and `check/draft.png` was byte-identical to v1's `artwork.png`
   (md5 `c9950caa…`), so a reviewer following the report judged a revision that is not this one.
   Regenerated from this revision's `artwork.svg` with `scripts/draw check … --outdir
   <package>/check`: every path in the report now resolves inside `B-hand-study-v1-r1/`, and
   `draft.png` is this revision's `artwork.png` (md5 `e2680593…` at that step).
2. **The pose pass of resolution R2.** The knuckle line was moved back along the palm's own axis
   (`scene.KNUCKLE["back"]`, a fraction of the palm's length: 0 → 0.55) and the finger stations
   were spread from 228/254/286/316 deg to 202/240/288/330 deg. Before the change every digit lay
   inside the plate's silhouette — the underside tops out at screen y = 154.5 px while the plate's
   lower silhouette reaches 209.1 px — so the delivered image showed one stub. Rooted below the
   plate's own lower contour, each digit's length now reads against the background and only its
   upper end is cut by the near rim.
3. **The three contact tests re-targeted per resolution R1** (see § Tests), against the dish's
   `derived_rings()` → `contact.underside_ring()` surface instead of the retired rim-band top.
4. **The pad's arrival angle** (this pass, package G3): the third knot on the pad's own axis, one
   `PAD_RUN` behind the approach knot, so the last cross-section is framed by the pad and not by
   the shaft. That is the change that closed the stand-off on all five digits; the numbers are in
   § the last measured stand-off.

## Finding → repair, against the archived review

| # | finding (archived review) | what was done | status |
| --- | --- | --- | --- |
| B1 | occlusion inverted: digits in front of the near rim, dish unsupported | every contact moved to the dish's underside rings, so the rim is the nearest surface at every overlapping pixel; the knuckle line moved back below the plate's lower silhouette so each digit's length reads against the background | **geometry done; the occlusion is gone by construction** (91 of 91 occlusions carry a depth gap, over 98 crossings and 7 contacts). Legible in the measured sense: five digit lengths now show below the plate where the previous revision showed one stub. **The pads themselves do not read outboard** — see "what R2 could not deliver" |
| B2 | radial spoke fan + concentric terracing in the well | bowl tessellation 17 → 33 rows; the inflate/underlay change was designed but **not landed** | **NOT FIXED** |
| B3 | five near-parallel, evenly spaced prongs; no thumb opposition, no knuckle mass; bottom block unreadable | uneven stations (202/240/288/330 deg) + unequal reaches + unequal radii; thumb rooted on the measured near flank at 338 deg; knuckle bulge at each finger's base; heel bulge in the palm | **partly done** — the distal halves now separate at 1.12 / 1.65 / 1.57 of a digit's width, but **the signed thumb-opposition test is absent**: nothing measures that the thumb opposes the fingers, only that it is rooted on the measured near flank |
| N1 | staircase silhouette, boxy flat digits | not addressed (tessellation of the digits unchanged) | not fixed |
| N2 | transverse seam + dark V notch where digits meet the palm | knuckle bulges change the digit bases; not measured | not verified |
| N3 | doubled rim contour, hard-terminating highlight | not addressed | not fixed |
| N4 | unexplained thin marks inside the well, floating rim fragment | not addressed | not fixed |
| N5 | ambiguous pale quads at digit tips | not addressed | not fixed |

**The art verdict is absent.** No reviewer has seen this revision; the table states what was
changed and what was measured, and it is not a judgement that the hand reads as a hand.

## What R2 could not deliver, and why (measured, not judged)

R2 asks for the digit **pads** to extend outboard past the plate's silhouette. Under an unbroken
near rim that is not reachable from this construction, and the numbers say so:

- the lowest screen point any underside contact can have is the foot ring's near point,
  y = 154.5 px, and a resting pad's surface is only the 1.5 px clearance below it (a thicker pad
  would hang lower, but the taper law caps a tip at 0.75 of its base width);
- the plate's own lower silhouette at the same x reaches y = 209.1 px — the outer wall bulges
  below the rim, so the boundary to clear is the wall, not the rim;
- 154.5 + 2·r_tip + 1.5 px, projected, stays above 209 for every tip radius the taper law allows.

So a pad that rests on the underside is always behind the plate, and what R2 can have is the
digit's *length* reading against the background — which is what was delivered. Whether the pose
now reads as a hand is a reviewer's question and nobody has answered it.

## The last measured stand-off, and how it was closed

`TestContact::test_every_digit_rests_on_the_underside_and_none_penetrates_it` measures each digit's
tip ring against the dish's underside, re-derived through `dish.derived_rings()` →
`contact.underside_ring()`. Quoted from the suite, all five digits:

```
index    tip   1.74 ..  35.27 px below the dish's underside
middle   tip   3.92 ..  37.11 px below the dish's underside
ring     tip   2.69 ..  30.31 px below the dish's underside
little   tip   1.68 ..  25.32 px below the dish's underside
thumb    tip   1.63 ..  53.37 px below the dish's underside
palm     nearest vertex 1.50 px below the dish's underside
mutation (clearance + 20 px): lowest 21.70 px
```

The stand-off was never the contact point: that point is derived correctly. It was the **arrival
angle** — the orientation of the tube's last cross-section, which is framed from the sampled
centreline, therefore from the direction between the last two samples, therefore from the *shaft*
whenever the pad's own chord is shorter than the sample spacing. The middle digit lands at
`reach = 0.98`, where a chord of 2.2 px runs against a spacing of 10 px: its pad stood on edge to
the plate and its nearest vertex was 13.5 px off however exactly its contact point was derived.

Two changes, both in `contact.py::finger`, neither touching a test:

- the pad's two knots (approach and tip) stand the same **tip** radius plus the clearance off the
  underside, each along its own station's normal, so the chord between them is parallel to the
  surface (package G2's change, kept);
- a third knot sits `PAD_RUN` = 1.6 tip radii behind the approach knot, on the pad's own axis. The
  approach-to-tip span is then a straight run along the plate, longer than the tube's sample
  spacing, so the last cross-section is framed by the pad and its nearest vertex reaches the
  clearance instead of the pad's radius.

Measured before → after, minimum stand-off per digit: index 7.05 → 1.60, middle 13.50 → 4.26,
ring 13.56 → 2.86, little 6.24 → 1.60, thumb 8.81 → 1.63. Only the index digit was previously
named because the assertion stops at the first digit it visits; all five were over.

`PAD_RUN` is not free: measured step by step on this construction, `PAD_RUN` = 1.7 gives 95
occlusions and 0 failures, and the first failure is at 1.8 (the thumb's bend into its pad breaks
the palm's rear edge, `tests/test_occlusion_break.py::test_every_occlusion_has_a_broken_rear_edge`),
so the run is as long as the frame allows, not as long as the contact bound allows.

## The contract conflict the previous pass hit — RESOLVED (kept for the record)

Resolved by the owner as R1/R2 of [`../../work/wave14-contracts.md`](../../work/wave14-contracts.md):
re-target, never weaken. The three contact tests now measure the surface the construction actually
touches. The previous pass's account of the conflict, kept so the resolution has a reason:

Direction (i) ("the hand is under the plate; the near rim is unbroken foreground") is
geometrically incompatible with the inherited assertion
`tests/test_hand_construction.py::TestContact::test_every_digit_rests_on_the_band_and_none_penetrates_it`,
which requires each digit's tip ring to sit 1.5 px *above the rim band's plane*. The dish is
widest at the rim's outer edge (r = 310 at z = 8, with the wall vertical there), so a tip resting
*on top of* the band necessarily occludes the near rim at its own pixels — that is exactly the
inversion the review blocked. A tip under the plate is 80–95 px below the band plane.

I raised this to the parent (contract report, options A/B/C in the message) and the reply timed
out. I implemented **option A was NOT implemented either**: the inherited contact tests are
currently **failing, untouched**, because re-targeting an inherited assertion without the
parent's word is the edit the law forbids. So the three failing `TestContact` cases and the two
manifest assertions are the open question, not an oversight:

- the three contact tests were re-targeted onto the underside (§ Tests); all three pass now,
  and the lift mutation still fails;
- `TestSeparation::test_the_distal_halves_are_separated` was **not** re-targeted and its floor
  was **not** lowered: it was fixed by the geometry (0.10 → 0.85).

## Contact derivation

`dish.derived_rings()` finds the dish's real edges on the built mesh: folds are the profile rows
where the surface turns by more than 30 deg, the two folds nearest the top are the rim (wider =
outer edge), the foot is the lowest ring of the outside, and the underside rows are the rows
between the axis row and the foot at fractions 0.30/0.55/0.80. `contact.underside_ring(t)` walks
axis → 0.30 → 0.55 → 0.80 → foot, interpolating between consecutive rows, so any `t` lands on the
surface the dish really has. A pad's centre is `ring point + ring normal * (radius + clearance)`.
No index of `profile()` is shared with the hand, and no number in `scene.py` is a coordinate.

## Separation values

Measured on the emitted station rings (`util.station_gap` / `util.width_at`), root = station 0.15,
distal = station 0.60, as a fraction of the two digits' mean width — quoted verbatim from the
suite's own output, every pair:

```
distal index -middle gap  58.4 / width  52.3 = 1.12
distal middle-ring   gap  79.4 / width  48.2 = 1.65
distal ring  -little gap  63.5 / width  40.6 = 1.57
roots index -middle gap   0.7 / width  51.7 = 0.01
roots middle-ring   gap   2.6 / width  48.1 = 0.05
roots ring  -little gap   1.8 / width  41.9 = 0.04
```

Every distal pair is above the inherited 0.30 floor and every root is below the 0.10 limit. The
floor was not moved: it reads 0.30 in `tests/test_hand_construction.py` (`DISTAL_FLOOR`).

## Commands

```bash
cd .scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1
../../../../.venv/bin/python source/build.py                 # -> artwork.svg (deterministic)
../../../../scripts/draw render artwork.svg -o artwork.png   # the documented render path
../../../../.venv/bin/python -m pytest -q tests/                # 25 tests: 25 passed
# regenerate the negative-control record after any build (both controls, whole file):
PYTHONPATH=../../../../.venv/lib/python3.12/site-packages:. ../../../../.venv/bin/python -c \
  "import sys; sys.path[:0]=['tests','source','.']; import test_occlusion_break as t; t.negative_control()"
../../../../.venv/bin/python source/manifest.py --check      # 19/19
sha256sum -c manifest.sha256                                 # 19/19 OK
# the review bundle, routed inside this package (no --ref: this stage is reference-free)
cd .. && cd ../..            # repo root
scripts/draw check .scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1/artwork.svg \
  --outdir .scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1/check
```

## What is unverified, and what is absent

- **The art verdict is absent.** Nobody has reviewed this revision; this README does not claim the
  review is answered.
- Whether the hand reads as a hand in the delivered image: the numbers place five separated digit
  lengths below the plate, and that is all this document claims.
- B2, the well's spoke fan and its shading: **NOT FIXED**, and it belongs to the next stage
  (package I). The extra profile rows were not measured for banding.
- No new test was written: the near-rim occlusion audit, the signed thumb-opposition test, the
  digit-variation test and the well-shading growth/tone-step test are all **absent** from the
  suite; `tests/negative-control-output.txt` now also carries this revision's contact negative
  control.
- The rim-band contour, the highlight's hard termination, the stray marks inside the well and the
  pale tip quads (review items N1–N5) are untouched, and so are the image reviewer's blocking
  findings B1 (the dish reads as an exposed triangle fan with a dither grid) and B2 (the hand reads
  as flat-shaded facets with a serrated silhouette): this pass cured execution blockers on the
  construction, not the picture. `source/contact.py`'s dead `thumb()` - no call site, the thumb is
  built by `finger()` - was deleted in this pass.
- the contact window is met by every digit; the middle digit is the loosest at 3.92 px against the
  5.5 px bound, and a wider `PAD_RUN` closes that margin further but breaks the palm's rear edge,
  so the two are in tension and only the occlusion test decides between them;
- the distal separations grew with the pad straightening (0.82/1.17/1.28 → 1.12/1.65/1.57 of a
  digit's width): the digits are now further apart than the previous revision's, and whether that
  reads as a hand rather than as five prongs is a reviewer's question, not this document's claim;
- `--lift` (the optional second image) was not re-checked after the pose change.

## Tests changed (resolution R1)

Three, and no assertion was added, removed or weakened anywhere else. What changed is the surface
each one measures — the rim band's top plane (retired) became the dish's underside ring:

- `test_every_digit_rests_on_the_band_and_none_penetrates_it` →
  `test_every_digit_rests_on_the_underside_and_none_penetrates_it`; it measures each tip ring
  against `util.underside_heights(...)`, which re-derives the surface through
  `dish.derived_rings()` → `contact.underside_ring()` and takes the distance to the nearest point
  of that surface, signed by its own normal. Same 1.5 px clearance, same ±: not a penetration
  (`> −1.0`) and rests rather than hovers (`< clearance + 4.0`).
- `test_a_digit_that_lifts_off_the_rim_is_caught` → `test_a_digit_that_lifts_off_the_underside_is_caught`;
  same mutation (`clearance + 20 px`), same assertion, on the new surface.
  Proof it still bites: `tests/negative-control-output.txt`.
- `test_the_hand_follows_the_dish`: perturbs the underside's own drivers,
  `dish.FOOT_RADIUS` (+60) and `dish.AXIS_UNDER_Z` (+30), instead of `RIM_OUTER`/`RIM_INNER`, which
  no longer drive contact. The perturbation is one that **bites**: the rebuilt hand rests on the
  moved surface (1.61 px) and a hand held at the old pose does not (6.88 px, past the 5.5 px bound).
  The old numbers (+26 / −20) were replaced because at −20 the dish's underside collapses: every
  sample's normal is zero and every height is 0.00 by construction, a null measurement the test
  read as a perfect contact. `util.underside_surface` now drops the axis ring and **raises** when
  any other sample's normal has vanished, so a degenerate dish fails the test instead of passing it.

Two tests were added in this pass:

- `test_the_palm_cap_meets_the_underside` measures the palm's nearest vertex against the underside
  with the test's own sampler (the claim had no measurement behind it, and the geometry missed the
  surface by 28.05 px);
- `test_the_committed_record_is_this_revision` recomputes the whole negative-control record and
  fails when `tests/negative-control-output.txt` and the build disagree, so the record cannot go
  stale under a green suite (it was the previous revision's numbers, 74/6 against this build's
  93/5). `negative_control()` now rewrites **both** sections - occlusion and contact - instead of
  overwriting the file with one of them.

Every command below was run: `source/build.py` (4030 quads, 27 stroke curves), both renders, the
record regeneration, `manifest.py --write`, `pytest -q tests/` → 25 passed.

`TestContact::test_the_band_is_a_rim_with_two_edges` and every other test are untouched: the dock
still has a rim with thickness, and the band is still measured — it is simply no longer the contact
surface.

## Files

`source/` (`geo.py`, `dish.py`, `digits.py`, `contact.py`, `scene.py`, `build.py`, `manifest.py`),
`tests/` (25 tests: 23 inherited bounds, two added this pass), `artwork.svg` + `artwork.png` (900×700),
`check/` (1:1 image listed first), `manifest.json` + `manifest.sha256`, this README.
