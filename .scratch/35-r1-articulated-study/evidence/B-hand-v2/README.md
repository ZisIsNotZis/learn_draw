# B-hand-v2 — hand rebuilt as constructed geometry (baseline / variation / control)

Single-writer evidence directory for milestone M1b. It keeps the reviewed B concept, the
variation and the control, and replaces only the hand. Nothing here is an art verdict: the
three panels must still be judged by a fresh image-only reviewer.

Start with `check/report.txt` (the reference-free `scripts/draw check` bundle) or
`rendered/B-original-support.png`. B runs with **no reference image**; no file in this
directory was produced from, or compared against, `image.jpg`.

## What changed and what did not

Unchanged from the accepted sheet (`evidence/goal-recovery-r1-v2-completion/`,
caption derivative `evidence/B-caption-corrected-v1/`): the three-panel layout, panel canvas
450×640 composed to 1350×640, the camera (`Camera()` orthographic front view), the body,
head, hair, bent two-bone arm (`construct_limb`), the dish/fruit/leaf, the semantic labels,
and the authored control offset (dish moved +0.34 scene units, hand still).

Replaced: the hand. The previous hand was one closed "scalloped palm pad" silhouette with
three drawn-on finger notches, a thumb heel folded into the same outline, and web/thumb
crease lines drawn over it. That is the toy-level construction the user rejected. The new
hand is six separate constructed components: a palm cup, four tapered finger tubes and one
tapered thumb tube.

## Hand construction vocabulary (`source/hand_family.py`, `source/scene.py`)

| Vocabulary | Meaning |
|---|---|
| tube / tapered digit | centreline of arc-length stations, offset to both sides by a width law, closed with round end caps. Built by `tapered_digit(base, knuckle, tip, base_half, tip_half, joint_dip)`; the width law smoothsteps from base to tip and dips locally at the knuckle. |
| palm cup | `build_hand`'s palm: its contact rim is the dish's own foot line, its wrist end is a rounded cap on the forearm's wrist anchor, and its two flanks are generated splines from the contact rim back to the wrist (the thenar side carries the thumb). |
| knuckle edge | the palm's distal edge, hanging `KNUCKLE_DROP` down from the contact rim's right end; the four digits start on it, `KNUCKLE_SETBACK` inside the palm. |
| digit pose | each digit's own `base` (knuckle station), own `tip` (a rim-band station, see below), own width taper, own knuckle bow and own depth plane. No two digits share a point, a length, a direction or an outline. |
| depth layer | every hand component has its own named support plane. Palm plane < dish plane < finger planes < thumb plane; the dish's rim and fruit sit in front again. Nothing is painted by order. |

Coordinates: every point in the modules is a local `(u, v)` on that component's support
frame. Absolute frame/screen coordinates exist only in the compiler output (`build_svg`).
Largest hand-authored input per shape: 4 semantic anchors (`_shape` rejects more), and each
digit carries only its two positions — both derived, not typed.

## Contact claims — what is a geometric consequence, what is a hypothesis

Every claim below is checkable in `tests/test_hand_construction.py`; none is an art verdict.

Geometric consequences (computed from the dish, re-checked by a test):

1. **Palm contact = the dish's foot line.** `dish_foot_contact` reads the lowest flat run out
   of the dish's own sampled contour and returns evenly spaced stations; the palm's contact
   edge is those stations raised `CONTACT_INSET = 0.006` into the dish so the contact line is
   hidden under the dish rather than drawn as a second line. Test
   `test_palm_contact_edge_is_the_dish_foot_line` re-derives the foot from the dish's contour
   and asserts every palm contact station lies on it.
2. **The palm sits behind the dish, touching it.** The dish support is `DISH_DEPTH_OFFSET =
   0.012` in front of the palm plane; the projected contact gap is exactly `CONTACT_INSET`
   and the depth separation is constant. Test `test_palm_supports_the_dish_underside_in_depth`.
   So the palm supports the dish's underside along its foot line — a support surface, not a
   drawn overlap.
3. **The palm is built against the nominal (own-case) dish.** In the variation the dish is
   lifted and 1.12× broader, and the wrist, contact edge and every fingertip move with it.
   In the control the dish alone is displaced, so the hand is *byte-identical* geometry to
   the baseline. Tests `test_variation_builds_the_hand_against_a_broader_lifted_dish` and
   `test_control_moves_only_the_dish`.
4. **Each fingertip reaches the dish's rim band.** `RimBand.near_point(angle)` samples the
   dish's rim ellipse; each digit's tip centre is placed `tip_half + reach_margin` below that
   arc so the fingertip edge stops just outside the glazed rim. Test
   `test_each_fingertip_is_placed_against_the_dish_rim_band` measures the tip's distance to
   the rim ellipse independently.
5. **Depth does the cutting.** The digits are in front of the dish and the palm behind it.
   Test `test_depth_engine_actually_cuts_the_dish_outline` asserts the dish's visible boundary
   is strictly shorter than its full outline (the fingers interrupt it) and every digit emits
   visible fill. `test_no_manual_visibility_ranges_in_the_scene_source` asserts no paint-order
   or visibility-range machinery exists in the scene.

Author hypotheses (authored proportion/pose values, not derived, not measured):

- which rim-angle stations the four fingertips take (`FINGERS[*].rim_angle_degrees`), and the
  stand-off margins (`reach_margin`: the middle and ring fingers nearly touch the rim, the
  index and little stop 10–26 mm-of-scene short);
- the digit widths, taper ratios, knuckle dip and bow, and the thumb's thenar position;
- that this arrangement reads as an open hand supporting the dish from below.

Not claimed, and deliberately absent from the caption: the previous public caption's
`thumb braces rim` is gone. The thumb's tip is *placed* against the dish's left rim band as a
geometric consequence, but whether the rendered thumb reads as bracing the rim is left to the
reviewer; the published caption states only `bent arm - open hand supports dish from below`
and, for the control, `CONTROL — near miss` / `dish displaced; hand remains still`
(`test_captions_claim_only_what_the_panels_show`).

## Files

- `source/hand_family.py` — the tube/digit primitive and the palm-cup geometry.
- `source/scene.py` — the B scene: body/arm/dish copied unchanged in semantics, the new hand
  assembly, the declared-contact validator, the single depth pass and the SVG compiler.
- `source/spatial_adapter.py` — copy of the reviewed composition glue, vendor path repointed at
  the shared `evidence/vendor-smooth-spatial`; unmodified otherwise.
- `source/run_b.py` — writes the three panel SVGs and the composed sheet.
- `source/make_manifest.py` — writes `manifest.json` and `manifest.sha256`.
- `tests/test_hand_construction.py` — 12 construction/contact/identity tests.
- `rendered/` — `B-baseline-support`, `B-variant-support`, `B-near-miss-control` (SVG+PNG, 450×640)
  and `B-original-support` (SVG+PNG, 1350×640).
- `check/` — reference-free `scripts/draw check` bundle (`draft.png`, `report.txt`).

## Commands run (from the repository root)

```bash
uv venv .venv && uv pip install --python .venv/bin/python numpy opencv-python-headless pillow pyyaml pytest
.venv/bin/python .scratch/35-r1-articulated-study/evidence/B-hand-v2/source/run_b.py            # 4 SVGs, ~50 s
for f in .scratch/35-r1-articulated-study/evidence/B-hand-v2/rendered/*.svg; do
  scripts/draw render "$f" -o "${f%.svg}.png"; done                                              # 4 PNGs
scripts/draw check .scratch/35-r1-articulated-study/evidence/B-hand-v2/rendered/B-original-support.png \
  --outdir .scratch/35-r1-articulated-study/evidence/B-hand-v2/check                             # reference-free
.venv/bin/python -m pytest -q -p no:cacheprovider \
  .scratch/35-r1-articulated-study/evidence/B-hand-v2/tests/test_hand_construction.py            # 12 passed, ~63 s
.venv/bin/python .scratch/35-r1-articulated-study/evidence/B-hand-v2/source/make_manifest.py
(cd .scratch/35-r1-articulated-study/evidence/B-hand-v2 && sha256sum -c manifest.sha256)         # all OK
```

## Explicitly unverified

- **Art/readability.** No reviewer has judged these images. Whether the hand reads as a
  detailed hand rather than a device, whether the digits read as separate digits *at final
  size*, and whether the hold reads in the baseline and variation while the control still
  reads as a failure are all open and belong to a fresh image-only review.
- **The reviewer's view.** `check/draft.png` is the pane-fitted whole sheet; its hand region is
  small. The per-panel PNGs are full resolution, and a reviewer should be given the sheet plus
  the three panel PNGs. No crop bundle was produced.
- **Physical plausibility beyond this model.** The artwork is 2D-on-3D support surfaces: each
  component is a flat patch. Depth ordering is verified (constant separation, no plane
  crossings outside named joints) but this is not a volumetric collision proof; the palm is
  drawn behind the dish's wall and the digits in front of it, which is the model's way of
  saying "under the dish" and "around its rim".
- **Thumb read.** The thumb is placed and tapered like the other digits and is visible, but no
  claim is made that it braces the rim.
- **Determinism across environments.** Re-running `run_b.py` reproduces the same geometry
  values (all derived from frozen numbers); byte-identical SVG output was not diffed in this
  run, and the PNG raster depends on the resolved `chrome-headless-shell` revision.
- **The rest of R1.** Nothing here addresses A, the heldout, transfer acceptance or user
  acceptance. The recorded best is untouched; no baseline promotion is implied.

## Budget note

The M1b allocation was 120 minutes with a checkpoint at 100. The checkpoint was passed while
the second hand hypothesis (fingertips around the dish's side wall) was being evaluated, and
the delivery steps (tests, check bundle, manifest, this README) finished after the hard stop.
The overrun is disclosed rather than hidden; no acceptance item was skipped to save time.
