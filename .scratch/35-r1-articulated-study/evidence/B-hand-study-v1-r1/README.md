# B-hand-study-v1-r1 — repair pass on the failed B hand study (ONE MEASURED FAILURE OPEN)

This directory is a copy of `../B-hand-study-v1/` (which stays untouched: it is the revision
the archived image review is bound to by hash) carrying one repair pass against
[`../../work/r1a-object-study-contracts.md` § B-hand-study-v1](../../work/r1a-object-study-contracts.md),
the archived verdict
[`../../evidence/reviews-r1a/B-hand-study-v1-image-review-1.md`](../reviews-r1a/B-hand-study-v1-image-review-1.md),
and package E of [`../../work/wave13-contracts.md`](../../work/wave13-contracts.md).

**Read this first: the suite is RED on exactly one test and the reason is a measured defect, not
a stale measurement** — `TestContact::test_every_digit_rests_on_the_underside_and_none_penetrates_it`
fails because the index pad stands **7.1 px** off the dish's underside against the stated 1.5 px
(the test allows up to 5.5; the middle and ring pads, at 10.6 px before the pad-axis change below,
now sit inside it). One digit still hovers. Everything else passes (22 of 23). This package awards no
art verdict and claims none: a fresh reviewer decides, and the state below is not ready for one.
The review bundle is truthful for this revision (§ Commands), which the previous pass could not
claim.

## What changed in the construction

The hand is now **under the plate**. Every digit's pad, and the palm's distal end, are placed on
the dish's own **underside rings** — derived from the emitted mesh by `dish.derived_rings()`
(`"under"`, `"axis"`, `"foot"`), interpolated by `contact.underside_ring()`, and offset along each
ring's own surface normal by the part's radius plus the stated 1.5 px clearance. The underside is
the face that carries the plate's weight, so:

- the plate's near rim is nearer to the camera than any hand surface that overlaps it, so no hand
  quad paints in front of the rim (the v1 inversion is gone by construction, not by paint order);
- the palm's distal end meets the underside at `PALM["reach"]` and its mass rises to the plate's
  near contour with no background gap;
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

## Finding → repair, against the archived review

| # | finding (archived review) | what was done | status |
| --- | --- | --- | --- |
| B1 | occlusion inverted: digits in front of the near rim, dish unsupported | every contact moved to the dish's underside rings, so the rim is the nearest surface at every overlapping pixel; the knuckle line moved back below the plate's lower silhouette so each digit's length reads against the background | **geometry done; the occlusion is gone by construction** (120 of 120 ink crossings carry a depth gap). Legible in the measured sense: five digit lengths now show below the plate where the previous revision showed one stub. **The pads themselves do not read outboard** — see "what R2 could not deliver" |
| B2 | radial spoke fan + concentric terracing in the well | bowl tessellation 17 → 33 rows; the inflate/underlay change was designed but **not landed** | **NOT FIXED** |
| B3 | five near-parallel, evenly spaced prongs; no thumb opposition, no knuckle mass; bottom block unreadable | uneven stations (202/240/288/330 deg) + unequal reaches + unequal radii; thumb rooted on the measured near flank at 338 deg; knuckle bulge at each finger's base; heel bulge in the palm | **partly done** — the distal halves now separate at 0.85 / 1.15 / 1.32 of a digit's width, but **the signed thumb-opposition test is absent**: nothing measures that the thumb opposes the fingers, only that it is rooted on the measured near flank |
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

## One measured failure, open

`TestContact::test_every_digit_rests_on_the_underside_and_none_penetrates_it` fails on the
**index** digit:

```
index    tip   7.05 ..  29.96 px below the dish's underside   (breaks the assertion: 7.05 > 5.5)
middle, ring, little, thumb: inside the bounds, quoted from the suite
```

The cause is in `contact.finger`, not in the measurement: the pad's centre is offset along the
surface normal by `r_tip + clearance`, but the digit arrives at the surface steeply, so the tube's
cross-section — a disc perpendicular to the digit's own tangent, not to the plate — stands off by
`r_tip · (1 − sin θ)` in addition to the clearance. Two changes have been made against it:
the pad's approach knot is now offset by the **tip** radius rather than the middle radius (so the
pad's axis is the chord parallel to the surface, not a line tilted into the plate) and the radius
law reaches `r_tip` by 0.88 of the span instead of at the tip. That took the middle and ring pads
from 10.6 px to inside the bound and the index pad from 10.6 px to **7.05 px**; the index still
sits 2.05 px over. What remains is the arrival angle of that one digit, not the pad's mechanism.

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
distal index -middle gap  45.0 / width  53.0 = 0.85
distal middle-ring   gap  55.6 / width  48.3 = 1.15
distal ring  -little gap  53.7 / width  40.7 = 1.32
roots index -middle gap   0.6 / width  52.4 = 0.01
roots middle-ring   gap   0.6 / width  48.1 = 0.01
roots ring  -little gap   2.8 / width  42.1 = 0.07
```

Every distal pair is above the inherited 0.30 floor and every root is below the 0.10 limit. The
floor was not moved: it reads 0.30 in `tests/test_hand_construction.py` (`DISTAL_FLOOR`).

## Commands

```bash
cd .scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1
../../../../.venv/bin/python source/build.py                 # -> artwork.svg (deterministic)
../../../../scripts/draw render artwork.svg -o artwork.png   # the documented render path
../../../../.venv/bin/python -m unittest discover -s tests -t .   # 23 inherited tests: 22 pass, 1 fail
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
  pale tip quads (review items N1–N5) are untouched.
- the index pad standing 7.1 px off the underside (the open failure above) is **not** fixed;
  the pad-axis change took the previous 10.6 px to 7.05 px but not inside the 5.5 px bound;
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
- `test_the_hand_follows_the_dish`: perturbs the underside's own drivers, `dish.FOOT_RADIUS` (+26)
  and `dish.AXIS_UNDER_Z` (−20), instead of `RIM_OUTER`/`RIM_INNER`, which no longer drive contact.
  Same assertions (`moved > 20 px`, `rests on the new surface`).

`TestContact::test_the_band_is_a_rim_with_two_edges` and every other test are untouched: the dock
still has a rim with thickness, and the band is still measured — it is simply no longer the contact
surface.

## Files

`source/` (`geo.py`, `dish.py`, `digits.py`, `contact.py`, `scene.py`, `build.py`, `manifest.py`),
`tests/` (23 inherited tests, unchanged), `artwork.svg` + `artwork.png` (900×700),
`check/` (1:1 image listed first), `manifest.json` + `manifest.sha256`, this README.
