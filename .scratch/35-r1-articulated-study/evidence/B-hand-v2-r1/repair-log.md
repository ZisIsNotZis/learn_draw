# Repair log — B-hand-v2-r1 (E1–E10)

Resumed after a harness timeout killed the previous run mid-iteration. It left HEAD at
`7c2f4b5` with **staged but uncommitted** edits to `source/hand_family.py` and `source/scene.py`
and a `rendered/`, `check/`, `manifest.*` set produced from the *earlier* source. Step 0 committed
the staged edits as they stood (`edf0a1c`) so nothing was lost; every later step names the commit
that carries it. Artefacts were then rebuilt from the current source and the package made
consistent: source, SVGs, PNGs, check bundle, tests, manifest, README.

Status vocabulary: **fixed** = the defect is gone and a command shows it; **partial** = the
construction is fixed and measured but the read of the image is not mine to judge; **not fixed** =
unchanged.

| Id | Defect | Status | What changed | Command / evidence |
|---|---|---|---|---|
| E1 | Hand must read as a hand: real palm, thicker/shorter/bent fingers, thumb pressing the near side | **partial** | Palm rebuilt as a pad whose distal edge is the dish's foot and whose wrist is narrower than the sleeve cuff; digits widened (`base_half` 0.080/0.082/0.079/0.069, thumb 0.090), pinch narrowed at the knuckle, and re-aimed at rim angles 118/100/82/64 so the fingers curl on the near wall instead of fanning like tines. Thumb re-rooted on the thenar and re-aimed at the dish's left wall station 0.85. The *read* is unverified — no fresh reviewer has seen it. | `test_digits_are_separated_by_a_fraction_of_their_width` (4.4 px tightest, 0.42 of a digit width), `test_digit_width_tapers_toward_the_tip` (0.62–0.66), `test_thumb_presses_the_dish_outer_left_wall` (0.084 = `tip_half + reach`) |
| E2 | Dish visibly rests on the hand; in front of some digits, behind others; contact not hidden by accident | **fixed** | Contact is still the dish's derived foot line, inset `CONTACT_INSET = 0.006` under it. Fingertips were the real failure: `RimBand.outward_normal` pointed *into* the bowl (sign error), so every tip was pushed up behind the glazed rim ellipse and disappeared. The normal is now the true outward normal and the tip station is `tip_half + reach` down the bowl's outer wall, so tips are visible below the band. | `test_palm_contact_edge_lies_on_the_dish_foot`, `test_palm_sits_behind_the_dish_foot_at_a_constant_stand_off`, `test_every_fingertip_edge_stops_short_of_the_rim_band`, `test_depth_engine_cuts_the_dish_outline_and_fills_every_digit` |
| E3 | One continuous arm: shoulder cap, elbow bend, forearm tapering into a wrist — no sticks, no butt joint at the wrist | **partial** | The arm is one `arm_tube` loft `shoulder -> elbow -> wrist` with a round cap at the shoulder and half-widths `0.240 -> 0.118 -> 0.078`; the separate `shoulder-cap` component (which sat *over* the sleeve as a second disc) is gone. At the wrist the palm now narrows to `PALM_WRIST_HALF = 0.088` behind a `0.078`-half cuff, and its heel is only `0.45 × wrist_half` long, so the cuff covers the palm's wrist end and the palm emerges from the sleeve — the previous palm (0.120 half) was wider than the cuff and read as a wedge butted onto a tube. The taper is measured; whether it *reads* as a wrist is a reviewer's call. | `test_hand_is_one_palm_four_fingers_and_one_thumb` (one `lofted_limb` component, one `palm_pad`), arm half-widths in `source/scene.py` `ARM_*` |
| E4 | Skin and the warm object separated by value and/or hue | **fixed** | Palette unchanged and measured rather than eyeballed: skin L 78.8 / h 25.7, fruit L 35.9 / h 10.7 (ΔL 42.9), dish wall L 50.6 / h 182.7 (Δhue 157°). | luminance/hue table in `README.md`, values read from the declared fills |
| E5 | Control differs in exactly one respect: the dish's displacement | **fixed** | Proven over emitted geometry, not asserted: component-by-component and line-by-line comparison between baseline and control. The only differences are `{dish-wall, dish-rim, fruit, leaf}` and the lines `{rim-light, fruit-seam}`, each a pure `(0, +0.34, 0)` translation with unchanged supports. A 1 mm nudge to the palm fails the check (mutation demo inside the test). | `test_control_differs_only_in_the_dish_displacement` |
| E6 | Enough head/torso construction to read as a person without claiming a face | **not fixed** (unchanged, no regression) | Head is a `lofted_profile` skull-and-jaw mass under a `lofted_hair_mass` (rebuilt from four centres and a knot width law), with jaw/ear/fringe semantic lines; no facial features, and no caption claims a face. | `test_captions_claim_only_what_the_panels_show` |
| E7 | No tautological tests | **fixed** | Both prior tautologies are gone: `assert any(abs(point.u - point.u) <= 0 ...)` (true for every input) is deleted, and no expected value is built from the literal it checks. Widths and gaps are measured on the emitted outlines; the rim stand-off is measured against the ellipse equation re-implemented in the test; four checks additionally demonstrate their own failure by mutating the emitted geometry (separation, taper, palm contact, single-variable control). | `python3 -m pytest -q $P/tests/test_hand_construction.py` — 16 passed; the `_expect_failure` calls are the mutation demos |
| E8 | No dead construction | **fixed** | Removed the unused `pad_half` parameter of `palm_pad`, the unused `PalmPad.length`, and the unused `Loft.start`; the never-executed `shoulder-cap` shape and its `cap_support` frame are gone. A caller search is now a test: every public name defined in `hand_family.py` must be referenced at least twice across family+scene+tests. | `test_hand_family_has_no_unused_public_construction` |
| E9 | Digit separation real at the delivered scale, as a fraction of a digit's width | **fixed** | Was 1.8 px (0.11 of a digit width) between middle and ring — "not separable". Foot span widened (`DISH_FOOT_FRACTION` 0.40 → 0.44) and the digits pinched at the knuckle, giving a tightest gap of **4.4 px = 0.42 of a digit's width** at 102 px/unit. The floor is stated as 0.35 × the narrower digit's own width, measured on emitted outlines, in px. | `test_digits_are_separated_by_a_fraction_of_their_width` (reports the pixel gap and fails below 0.35 of a width; mutation slides the tightest pair together) |
| E10 | Check bundle must carry the 1:1 image from the current `scripts/draw` | **fixed** | `check/` regenerated with the current tooling: `draft-fullres.png` (1350×640, 1:1) is the **first** listed image, followed by the downscaled `draft.png`. `scripts/draw.py` and `scripts/renderer.py` in this worktree already equal the main checkout's versions, so nothing needed copying. | `test_check_bundle_lists_the_one_to_one_image_first`; tooling sha256s in `README.md` |

## Reproduction and consistency evidence

Two consecutive full builds of the current source, byte-compared:

| file | sha256 |
|---|---|
| `rendered/B-baseline-support.svg` | `d8f42599dde0a1f37a1d74c75eb173949d0b6285e2b1dbfa7d4bda7f76104c73` |
| `rendered/B-variant-support.svg` | `01cd6ac672d552f162e9005248c92c5eb3bed9079128539ecbef530e270fbc08` |
| `rendered/B-near-miss-control.svg` | `f2d9c8b4e4ee87229c456498c05074bedc7cf685ce0bc07736b290f3287a9901` |
| `rendered/B-original-support.svg` | `2eedc80ba319a1bb4d69241495519b6dd7061e882af55a65ab0c368e38ad118c` |

`cmp` reports all four identical between the two builds. The PNG is a rasterizer output: two
renders of the same SVG are not byte-identical, and the delivered sheet differs from a fresh
build's sheet in 50 of 864000 pixels by at most 5/255 per channel (anti-aliasing on a panel
edge). That limit is stated in the README rather than hidden.

Source/artefact reconciliation: the inherited `rendered/`, `check/` and `manifest.*` were built
before the staged edits. All four SVGs, all four PNGs, the check bundle, the tests and the
manifest were regenerated from the current source in this round; `manifest.sha256` verifies over
every file in the package.

## Not addressed here

Art verdicts of any kind (a fresh image-only reviewer owns that), the raster determinism limit
above, volumetric collision beyond support-plane depth ordering, and the rest of R1 (A, the
heldout, integrated delivery).
