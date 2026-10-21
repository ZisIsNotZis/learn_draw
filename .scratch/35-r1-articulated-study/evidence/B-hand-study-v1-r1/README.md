# B-hand-study-v1-r1 — repair pass on the failed B hand study (INCOMPLETE)

This directory is a copy of `../B-hand-study-v1/` (which stays untouched: it is the revision
the archived image review is bound to by hash) carrying one repair pass against
[`../../work/r1a-object-study-contracts.md` § B-hand-study-v1](../../work/r1a-object-study-contracts.md),
the archived verdict
[`../../evidence/reviews-r1a/B-hand-study-v1-image-review-1.md`](../reviews-r1a/B-hand-study-v1-image-review-1.md),
and package E of [`../../work/wave13-contracts.md`](../../work/wave13-contracts.md).

**Read this first: the pass ran out of its 75-minute wall clock before it was complete, and the
suite is RED (6 failures, listed below).** What is landed here is a truthful intermediate state,
not a repair. This package awards no art verdict and claims none: a fresh reviewer decides, and
the state below is not ready for one.

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

## Finding → repair, against the archived review

| # | finding (archived review) | what was done | status |
| --- | --- | --- | --- |
| B1 | occlusion inverted: digits in front of the near rim, dish unsupported | every contact moved to the dish's underside rings, so the rim is the nearest surface at every overlapping pixel; the palm's end meets the underside and its mass rises to the near contour | **geometry done, legibility NOT verified** — the digits are now *entirely* hidden behind the plate (see "known gap" below) |
| B2 | radial spoke fan + concentric terracing in the well | bowl tessellation 17 → 33 rows; the inflate/underlay change was designed but **not landed** | **NOT FIXED** |
| B3 | five near-parallel, evenly spaced prongs; no thumb opposition, no knuckle mass; bottom block unreadable | uneven stations + unequal reaches + unequal radii; thumb rooted on the measured near flank at 338 deg; knuckle bulge at each finger's base; heel bulge in the palm | **partly done** — no signed thumb-opposition test was written, and the digits are invisible, so the review's reading cannot be re-judged from this revision |
| N1 | staircase silhouette, boxy flat digits | not addressed (tessellation of the digits unchanged) | not fixed |
| N2 | transverse seam + dark V notch where digits meet the palm | knuckle bulges change the digit bases; not measured | not verified |
| N3 | doubled rim contour, hard-terminating highlight | not addressed | not fixed |
| N4 | unexplained thin marks inside the well, floating rim fragment | not addressed | not fixed |
| N5 | ambiguous pale quads at digit tips | not addressed | not fixed |

## Known gap that blocks this revision

`check/report.txt` lists the new 1:1 image. In it the plate is the only foreground object and the
hand is a single stub below it: **the digits' pads sit just behind the plate's near contour and
the palm's mass covers the rest, so the image does not show five digits at all.** The numbers say
the digits are where the contact demands; the picture says the pose is not yet legible. A pose
pass (spreading the digit pads outboard past the palm's silhouette and lowering the palm's mass
away from the camera) is the next writer's first job, and it must be done from the geometry, not
by moving the rim.

## The contract conflict this pass hit (assumed decision, not approved)

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

- `TestContact::test_every_digit_rests_on_the_band_and_none_penetrates_it` — measures the tip
  against the rim's *top band*; unsatisfiable with a hand under the plate.
- `TestContact::test_a_digit_that_lifts_off_the_rim_is_caught` — same surface.
- `TestContact::test_the_hand_follows_the_dish` — perturbs `RIM_OUTER`/`RIM_INNER`, which no
  longer move the contact surface (the underside is driven by `FOOT_RADIUS`/`AXIS_UNDER_Z`).
- `TestManifest` ×2 — stale until `source/manifest.py --write` was re-run; re-run done, so these
  two now pass (the transcript above shows the pre-write run).
- `TestSeparation::test_the_distal_halves_are_separated` — the digits now converge on the
  underside and their distal halves are 0.10 of a width apart: a **real** construction failure
  (the digits are cramped), not a stale measurement.

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
distal = station 0.60, as a fraction of the two digits' mean width:

| pair | roots | distal halves |
| --- | --- | --- |
| index–middle | 2.7 / 53.9 = **0.05** | 5.5 / 54.5 = **0.10** (floor 0.30 — FAILS) |
| middle–ring | 1.9 / 53.3 = **0.04** | not recorded in this pass |
| ring–little | 1.6 / 43.0 = **0.04** | not recorded in this pass |

The roots' merge is still within the inherited limit (≤ 0.10) and is stated, not hidden. The
distal floor is violated: the digits are cramped under the plate.

## Commands

```bash
cd .scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1
../../../../.venv/bin/python source/build.py                 # -> artwork.svg (deterministic)
../../../../scripts/draw render artwork.svg -o artwork.png   # the documented render path
../../../../.venv/bin/python -m unittest discover -s tests -t .   # 23 inherited tests: 18 pass, 5 fail
../../../../.venv/bin/python source/manifest.py --check      # 19/19
sha256sum -c manifest.sha256                                 # 19/19 OK
```

## What is unverified, and what is absent

- **The art verdict is absent.** Nobody has reviewed this revision; this README does not claim the
  review is answered.
- Whether the hand reads as a hand *at all* in the delivered image: it does not show five digits
  (see "known gap").
- Whether the well's spoke fan is gone: the extra profile rows are expected to halve the banding,
  and **no measurement of the spokes was taken**.
- No new test was written: the near-rim occlusion audit, the signed thumb-opposition test, the
  digit-variation test and the well-shading growth/tone-step test are all **absent**, and
  `tests/negative-control-output.txt` still carries v1's numbers.
- The rim-band contour, the highlight's hard termination, the stray marks inside the well and the
  pale tip quads (review items N1–N5) are untouched.
- `--lift` (the optional second image) builds and was not re-checked after the pose change.

## Files

`source/` (`geo.py`, `dish.py`, `digits.py`, `contact.py`, `scene.py`, `build.py`, `manifest.py`),
`tests/` (23 inherited tests, unchanged), `artwork.svg` + `artwork.png` (900×700),
`check/` (1:1 image listed first), `manifest.json` + `manifest.sha256`, this README.
