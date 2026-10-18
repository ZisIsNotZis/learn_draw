# B-hand-v2-r1 — hand and arm as constructed geometry (baseline / variation / control)

Single-writer evidence directory for milestone M1b, round 1. It keeps the B concept, the
variation and the control the user judged readable, and rebuilds the hand and the arm out of
constructed primitives. Nothing here is an art verdict: the three panels must still be judged
by a fresh image-only reviewer (AGENTS invariant 7).

Start with `check/report.txt` (the reference-free `scripts/draw check` bundle; its first image,
`check/draft-fullres.png`, is the 1:1 sheet) or `rendered/B-original-support.png`. B runs with
**no reference image**; no file here was produced from, or compared against, `image.jpg`.
Per-defect disposition for the repair itself: `repair-log.md`.

## What is in the drawing

One figure, three panels, matched camera, 450×640 each, composed to a 1350×640 sheet. A bent
arm carries a small fruit dish at chest level (baseline), presents it lifted and broader
(variation), and in the control the dish alone is displaced away from a still hand.

## Construction vocabulary (`source/hand_family.py`)

| Vocabulary | Meaning |
|---|---|
| `loft_tube` | one limb primitive: a semantic centreline polyline, a width law of `(t, half-width)` knots, offset to both sides by that law per arc-length station, closed with elliptic end caps. Digits, the palm's flanks, the arm, the neck, the skull and the hair are all instances. |
| `digit_tube` | one finger or thumb: `base -> knuckle joint -> tip` with a width law that narrows toward the tip. |
| `arm_tube` | the whole arm as **one** limb: shoulder cap, a bend at the elbow, taper into the wrist (`0.240 -> 0.118 -> 0.078` half-width). |
| `palm_pad` | the palm: its distal edge *is* the dish's derived foot line, its flanks are generated splines back to the wrist, its wrist end is a shallow heel narrower than the sleeve cuff so the cuff covers it. |

Coordinates: every point in the modules is a local `(u, v)` on that component's own support
frame; absolute frame/screen coordinates exist only in the compiler output (`build_svg`).
Largest hand-authored input per shape: 4 semantic anchors (`_shape` rejects more).

## Claim table — geometric consequence or author hypothesis

Each row is checkable; the test named in the last column is the check. Geometric consequences
are computed from the dish or from emitted geometry; author hypotheses are design values that
no measurement here can confirm or refute.

| # | Claim | Kind | Evidence (test) |
|---|---|---|---|
| 1 | The palm's distal rim is the dish's own flat foot line, raised `CONTACT_INSET = 0.006` under the dish so the contact is hidden rather than drawn twice. | **geometric consequence** (`dish_foot_contact` reads the lowest flat run of the dish's sampled contour) | `test_palm_contact_edge_lies_on_the_dish_foot` (+ mutation: a station moved 0.02 off the foot fails) |
| 2 | The palm sits behind the dish at a constant `DISH_DEPTH_OFFSET = 0.012`, projected gap ≤ `CONTACT_INSET`. | **geometric consequence** | `test_palm_sits_behind_the_dish_foot_at_a_constant_stand_off` (+ mutation: raising the palm plane 0.02 fails) |
| 3 | Every fingertip's own edge stops `reach` short of the dish's near rim band, measured against the ellipse's equation rather than the band's own sampler: `\|distance − (tip_half + reach)\| ≤ 0.004`. | **geometric consequence** | `test_every_fingertip_edge_stops_short_of_the_rim_band` (+ mutation: a tip raised 0.12 hides behind the band and fails) |
| 4 | The thumb's tip stops `tip_half + reach` from the dish's outer left wall contour. | **geometric consequence** (`dish_wall` reads the contour) | `test_thumb_presses_the_dish_outer_left_wall` |
| 5 | Fingertips land **below** the near rim band, on the bowl's outer wall, so they stay visible instead of vanishing behind the glazed ellipse. | **geometric consequence** (this is the E1/E2 ambiguity fix) | `test_every_fingertip_edge_stops_short_of_the_rim_band` |
| 6 | Digits are separate at the delivered scale: the tightest pair (middle–ring) is 4.4 px apart, i.e. 0.42 of a digit's own width, floor 0.35. | **geometric consequence** (measured on emitted outlines) | `test_digits_are_separated_by_a_fraction_of_their_width` (+ mutation: sliding the pair together fails) |
| 7 | Every digit tapers toward its tip, `tip ≤ 0.75 × base` (measured 0.62–0.66). | **geometric consequence** | `test_digit_width_tapers_toward_the_tip` (+ mutation: fattening the tip fails) |
| 8 | The control differs from the baseline in exactly one respect: `{dish-wall, dish-rim, fruit, leaf}` and the lines `{rim-light, fruit-seam}` translated by `(0, +0.34, 0)` with unchanged supports; every hand, arm, torso, head and garment component is identical. | **geometric consequence** | `test_control_differs_only_in_the_dish_displacement` (+ mutation: a 1 mm hand nudge fails) |
| 9 | The variation builds the hand against the wider dish: the palm's contact span grows by the dish's own 1.12 width ratio. | **geometric consequence** | `test_variation_builds_the_hand_against_the_wider_dish` |
| 10 | Depth, not paint order, decides what is visible; the digits interrupt the dish's visible outline. | **geometric consequence** | `test_depth_engine_cuts_the_dish_outline_and_fills_every_digit` |
| 11 | Which rim-angle station each fingertip takes, the stand-off margins (`reach`), the digit widths and taper ratios, the knuckle bow, the thenar bulge and the palm's wrist width. | **author hypothesis** (proportion and pose values) | not measurable here; only a reviewer can say whether they read |
| 12 | That the arrangement reads as an open hand carrying a dish from below, and that the arm reads as one continuous limb with a wrist rather than a tube butted to a wedge. | **author hypothesis** | **unverified** — no fresh reviewer has judged it |

Palette separation (E4), measured on the declared fills: skin `#eec2a1` L 78.8 h 25.7; dish wall
`#5f8a8c` L 50.6 h 182.7; fruit `#b8452c` L 35.9 h 10.7. Skin and the warm object are separated
by 42.9 luminance units and by hue; skin and the dish by 157° of hue. These are the authored
constants, not a sampled-image measurement.

Captions: the panels say only `bent arm - open hand holds the dish from below` and, for the
control, `CONTROL — near miss` / `dish displaced; hand remains still`. No caption claims a thumb
bracing a rim; the previous package's `thumb braces rim` text stays removed, and
`test_captions_claim_only_what_the_panels_show` fails if `braces` reappears.

## Files

- `source/hand_family.py` — the one loft primitive, the digit/arm/profile builders, the palm pad.
- `source/scene.py` — the B scene: the dish, the derived-contact hand assembly, the body, the
  semantic lines, the declared-contact validator and the SVG compiler.
- `source/spatial_adapter.py` — reviewed composition glue (vendor path repointed); unmodified.
- `source/run_b.py` — writes the three panel SVGs and the composed sheet.
- `source/make_manifest.py` — writes `manifest.json` and `manifest.sha256`.
- `tests/test_hand_construction.py` — 16 construction/contact/identity/package tests.
- `rendered/` — three panels (SVG+PNG, 450×640) and `B-original-support` (SVG+PNG, 1350×640).
- `check/` — reference-free `scripts/draw check` bundle: `draft-fullres.png` (1:1, 1350×640),
  `draft.png` (downscaled preview), `report.txt`.
- `repair-log.md` — E1–E10 disposition with the command for each.

## Commands run (from the repository root, `python3` = system env with numpy/cv2/Pillow/pytest)

```bash
P=.scratch/35-r1-articulated-study/evidence/B-hand-v2-r1
python3 $P/source/run_b.py --outdir $P/rendered          # 2m31s, 4 SVGs
python3 $P/source/run_b.py --outdir /tmp/build_b         # second build, compared byte for byte
for f in $P/rendered/*.svg; do scripts/draw render "$f" -o "${f%.svg}.png"; done
scripts/draw check $P/rendered/B-original-support.png --outdir $P/check     # reference-free
python3 -m pytest -q -p no:cacheprovider $P/tests/test_hand_construction.py # 16 passed
python3 $P/source/make_manifest.py
(cd $P && sha256sum -c manifest.sha256)
```

Tooling used (already at HEAD of the main checkout, so no copy was needed):
`scripts/draw.py` sha256 `c0c77e5828c0503e641d8801a40c8e94bd1a968eef92ab9e35c456c0f9cd39fc`,
`scripts/renderer.py` sha256 `4ae1b27870ebaa70fff5c1975a9d9c2632b0c6e0f4f483197b852c3ed3692b94`.

## Explicitly unverified

- **Art/readability.** No reviewer has judged these images. Whether the hand reads as a
  detailed hand, whether the digits read as separate at final size, whether the wrist reads as
  a transition rather than a join, and whether the control reads as a near miss all remain open
  and belong to a fresh image-only review of `check/draft-fullres.png` plus the panel PNGs.
- **Raster determinism.** Two consecutive `run_b.py` builds emit **byte-identical SVGs** (four
  sha256s recorded in `repair-log.md`). The chrome renderer is *not* byte-deterministic: two
  renders of the same SVG differ, and the delivered PNG differs from a fresh build's PNG in
  50 of 864000 pixels by at most 5/255 per channel, all of it anti-aliasing on a panel edge.
  So "delivered PNG equals a fresh build" holds up to rasterizer anti-aliasing, not byte for byte.
- **Physical plausibility beyond this model.** The artwork is 2D-on-3D support surfaces: each
  component is a flat patch. Depth ordering is checked (constant stand-off, no plane crossings
  outside named joints) but this is not a volumetric collision proof.
- **The rest of R1.** Nothing here addresses A, the heldout, or user acceptance. The recorded
  best is untouched; no baseline promotion is implied.

## Budget note

This round resumed after a harness timeout killed the previous run mid-iteration, leaving staged
source edits and artefacts built from the older source. The first action was to commit those
staged edits intact (`edf0a1c`) before reconciling them; the reconciliation and the geometry
repair are recorded step by step in `repair-log.md`.
