# Image review 2 — B-hand-study-v1-r1

**VERDICT: FAIL** — the picture does not read as a hand holding a plate, and the hand does not read as a drawing: it reads as a dish standing in front of a bundle of flesh-toned straps that never touch it.

**Binding.** image sha256 `e66d72183660333f4f94dd2a11d1cb1cc1d51f62ecca3bd65aec54f77e281322` (`check/draft-fullres.png`, verified locally, 900×700, PNG colour-type 2) · dispatch revision `1a59a07` — **not verified by me**: I was instructed to read only the two image files, so I did not open git history; treat the revision as claimed by the dispatcher, not as checked · rebuild command: `cd /home/z/vibe/learn_draw && .venv/bin/python scripts/draw.py check .scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1/artwork.svg` (not run; my judgement is bound to the delivered PNG, not to artwork.svg).

## Inputs read
- `evidence/B-hand-study-v1-r1/check/draft-fullres.png` — judged at 1:1 plus nearest-neighbour crops.
- `evidence/B-hand-study-v1-r1/check/draft.png` — same 900×700 canvas; `ImageChops.difference` gives max per-channel difference 0 over all 630000 pixels, so the two files are pixel-identical and the different sha256 (`b08999a1…`) is encoding only. I judged `draft-fullres.png`, whose hash is the one bound above.
- Nothing else: no README, source, tests, manifest, git log or prior review.

## Method
Masks from the delivered pixels only: background = exact `(243,238,230)` (354347 px); flesh = `R>G>B and R−B≥15` (56402 px); plate = neutral/bluish `G>R and B≥R−1` (204879 px); luminance `0.299R+0.587G+0.114B`. Measurements taken: silhouette extent per row; plate outer-arc ellipse fit; deep-shadow connected components; per-row dark-run tables; luminance scanlines through the bowl; angular residual on rings inside the bowl; dark-band width just inside the left and right hand contours. Crops were written to `/tmp` only; nothing was written into the repository.

## The reading question, question by question

**1. Does it read as a plate?** Yes. A grey elliptical dish with a rim annulus, concentric contour rings, a concave interior and a fan-lit bowl. The upper outer arc is a good ellipse: centre (449.5, 258.0), a=311.5, b=224.0, maximum radial residual 2.5 px along the upper arc → b/a=0.719, i.e. a disc seen from ≈46° above. The plate is the picture's one legible object.

**2. Does it read as a hand?** No. The flesh mass is four to five long tapered strips with near-parallel long axes, no joints, no knuckles, no nail, no fingertip pad, no palm plane, no wrist, and no opposed digit. Measured: the strips are bounded by repeating luminance sawtooth ramps that restart from ~185 to ~57 (e.g. row y=560: 157→184→133→150→158→153→140→116→86→58, then reset to 185), which is one fill per strip, not one light direction across forms. Their separations are creases that die out (see F2), and their free ends are blunt chisel and sharp cusp terminations (F1). It reads as a bundle of straps hanging below a dish.

**3. Does it read as a hand *holding* a plate?** No. Nothing in the picture depicts support or contact: no fingertip touches the rim, no finger wraps the near rim, no palm meets the underside (F1).

**4. Does it read as a drawing?** Only the plate does. The plate has drawn contour rings; the hand has no linework — it is gradient-mesh fills between contours that break, reverse and terminate in spurs and notches (F4). At 1:1 the hand's marks read as fill artefacts rather than as drawn form.

## Blocking findings

### F1 — No depicted grip: every flesh form ends in mid-air, away from the plate
- **Location.** Terminations against empty ground at (290–420, 600–650) (left bundle, blunt chisel ends), (455–520, 545–575) (concave bite), (545–560, 590–600) (sharp cusp). The plate's front rim is the silhouette through y≈452 at x=300, 479 at x=400, 482 at x=450, 478 at x=500, 451 at x=600.
- **Criterion violated.** Accept: the picture must read as "a hand holding a plate". A grip needs at least one depicted contact or wrap between hand and plate.
- **Reproduction.** Unbroken-run widths of the flesh mask (`R>G>B and R−B≥15`) per row: y=490 → x 301…624, width 324 (the first row where the flesh forms one unbroken run, i.e. the widest row of the solid hand, immediately below the rim); y=560 → 270; y=620 → 203; y=660 → 168; y=695 → 175. Above y=490 the flesh pixels are scattered boundary fragments, not a body (y=450: span 352 but only 47 flesh pixels in the row), so the solid hand begins only where it clears the rim. The hand narrows monotonically *downwards*, so its free ends point away from the plate while its other ends are hidden behind the rim. The flesh never crosses the plate outline anywhere along the near rim span x=283…644: comparing the flesh's top boundary with the plate's bottom silhouette in each column gives a difference of −6…+2 px, and 162 flesh pixels lie above that silhouette across 130 columns with no column holding more than 4 of them — boundary-adjacent pixels, not an overlapping shape. Crop `(590,390)-(700,500)` at 4× shows the flesh cut cleanly by the rim's underside.
- **Consequence.** The drawn configuration is "dish in front, bundle behind", not "hand under/around a plate". Nothing supports the plate, so the plate reads as floating — the one thing the subject cannot afford.

### F2 — Finger separations terminate in the middle of the mass with no fingertip
- **Location.** Deep-shadow creases (luminance<95 inside flesh), as connected components with pixel counts: (1453 px) (385,478)–(439,598); (750 px) (495,477)–(519,561); (329 px) (528,474)–(544,526); (146 px) (296,472)–(317,527); (80 px) (541,530)–(548,548).
- **Criterion violated.** A hand's individual fingers are bounded by continuous separations running from palm to tip; three of the four major separations stop dead inside flesh, so the forms they bound are straps with no ends, not fingers.
- **Reproduction.** Per-row dark-run table for the right-hand crease, rows y=500…572 in steps of 4, dark pixels within x 515…580: y=500 →515–540, 508 →537–542, 516 →539–544, 524 →540–542, **528 → none**, 536 →542–547, 544 →543–545, 548 →544–544, **552 → none**, **556 → none**, 564 →545–551. The separation breaks into dashes and vanishes; the form it bounds therefore has no legible finger boundary. The 4× crop `(420,440)-(580,620)` shows the middle strip ending in a concave bite with a detached sliver instead of a tip, and the crop `(500,440)-(660,660)` shows three rectangular steps at x≈535–557, y≈505–575 where two forms' edges cross.

### F3 — No palm, no wrist, no opposed digit: the lower mass is an unarticulated slab cut by the frame
- **Location.** y=650…699, x≈370–550; flesh at the bottom frame row y=699 spans x=372…547 (175 px) and is cut by the image edge.
- **Criterion violated.** Reads as "a hand": a hand needs a palm mass and a wrist, and the pose needs one digit opposed to the others to grip.
- **Reproduction.** Unbroken-run widths for the flesh mask — 324 px at y=490 (widest solid row, immediately below the plate), 270 at y=560, 203 at y=620, 168 at y=660, 175 at y=695 — i.e. the mass converges to a stump that runs off the bottom edge with no wrist crease, thenar eminence or knuckle; and all long axes are near-parallel (the right-hand crease drifts only x=545→551 over 72 rows, ≈6°), so no digit is opposed to any other. The bottom-frame cut removes exactly the region that would have told the viewer which end is the wrist.

### F4 — The hand's contours break, reverse and sprout spurs, so the hand does not read as a drawing
- **Location.** (500–530, 545–570) concave bite with reversed contour; (535–557, 505–580) staircase of three rectangular steps; (540–560, 595–660) spur continuing below the cusp; (400–430, 615–630) detached sliver wedge with its own dark edge; (455–465, 565–600) thin finger-thin spill below the bite.
- **Criterion violated.** Reads "as a drawing": a drawn contour is a continuous mark that bounds a form; these are fill boundaries that terminate, double back and spawn fragments with no bounded form attached, which is the signature of intersecting construction geometry rather than a drawn hand.
- **Reproduction.** The crops named above at 3–4× nearest-neighbour (`/tmp` copies made from `check/draft-fullres.png`, boxes `(420,440,580,620)`, `(500,440,660,660)`, `(270,570,470,690)`), plus the crease-dropout table in F2 and the isolated (80 px) shadow blob at (541,530)–(548,548) sitting between two forms.

## Nonblocking findings
- **Fan banding in the bowl.** Angular residual on rings inside the bowl centred (450,310): 35 local maxima at R=60 and 59 at R=90, residual std ≈0.7–1.1 luminance levels — visible at 1:1 as radial streaks. Low amplitude; polish, not a blocker.
- **Edge weight asymmetry.** Mean dark band (luminance<120) just inside the silhouette: 1.1 px on the left boundary (n=49, max 4) versus 14.2 px on the right (n=49, max 19). Defensible as one-sided lighting, but combined with the per-strip sawtooth ramps it is what makes the forms read as extruded ribbons rather than fingers.
- **Fills are gradients, not tone.** 8742 unique colours; on the bowl scanline y=300, x=300…600 there are 30 distinct luminance levels and 25 of 299 adjacent pairs differ by only 1–2 levels. There is no flat-tone or ink character to read.
- **Composition.** The plate nearly touches the top (plate top y=34, 40 px margin; left x=138, right x=761) while the hand bleeds off the bottom at y=699. The crop removes the wrist and leaves the subject's anchor outside the frame.

## Residual risk
- Reference-free judgement: I cannot rule out that the artwork targets some other subject (a dish behind a hand, a prop study). If so, the brief "a hand holding a plate" is still not met, so the verdict does not depend on this.
- Revision `1a59a07` is unverified (see Binding). If the delivered PNG is not the render of that commit, the findings stand for the PNG, whose hash I did verify.
- I did not run the rebuild command, so I cannot say the PNG is reproducible from `artwork.svg`; if it is not, that is a separate defect and the image evidence dies with the file.
- The 46° elevation comes from an ellipse fit on the **upper** arc only (max residual 2.5 px). The lower silhouette is not elliptical (the rim wall and foot thicken it), so the angle is used qualitatively — as "the plate is seen clearly from above" — and no finding rests on its numeric value.
- I did not test whether the drawing was authored as vectors with a solver or hand-placed: the "not a drawing" judgement is about what the delivered pixels show, not about how they were produced.
- Measurements used colour masks with stated thresholds; a different threshold would shift the pixel counts slightly but not the per-row widths, the crease dropouts, or the terminations, which are visible in the crops at 3–4×.

## What carried the parts that do work
The plate: a clean elliptical rim at 46° elevation, contour rings that describe the lip, and a bowl gradient that reads as concavity. The failure is entirely in the hand and in its failure to meet the plate.
