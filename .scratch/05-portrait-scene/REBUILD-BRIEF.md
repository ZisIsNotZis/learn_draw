# REBUILD BRIEF — portrait assembly v20 (read fully before working)

## Mission

Rebuild `.scratch/05-portrait-scene/work/v20.svg` so the full figure **reads correctly at a glance** compared to `image.jpg`. Current v17 is structurally broken in visible ways: hat brim (帽檐) collapsed, dark skirt body missing, colorful translucent ribbons invisible, hands too small/short. You fix these by REBUILDING with measurements, not patching.

## Success criteria (all must hold)

1. Hat: wide brim sweeping from left tip (~444,46) OVER the head, descending right, exiting right edge ~(1024,340±20). Teal underside wedge visible left-below the dome. Dome sits ON the head.
2. Skirt: big dark-navy mass dominating (500-860, 690-1010) with white zigzag hem triangles along the bottom hem (y 830-1010, big triangles 60-120px wide) AND pale celadon layer pieces; dark navy ≥ 50k px in zone (500-860, 700-1000).
3. Colorful translucent ribbons VISIBLE over the skirt area: pink (#e088a8-ish), yellow (#e6cc90), green (#8ed0a8) — feathered edges (filter blur), opacity 0.5-0.75.
4. Right arm: cuff (826-890, 588-645) → forearm angling down-left ~150px → hand (~795-835, 735-775) with 2-3 finger lines. Visibly longer than 100px.
5. Neck: pink #d7aec2 visible between jaw bottom (~y 392) and collar top (~y 428), x 712-786.
6. Every iteration: render + VIEW the full image and judge like a human ("does this look like the reference illustration?").
7. File must parse: `xml.etree.ElementTree.fromstring` before every render.

## Files & tools

- Reference: `/home/z/vibe/learn_draw/image.jpg` (1024x1024). VIEW it (read tool) — always compare full frames.
- Current (broken) assembly: `.scratch/05-portrait-scene/work/v17.svg` — salvage shapes from it, do not trust its structure.
- Output: `.scratch/05-portrait-scene/work/v20.svg`; render each iteration: `.scratch/05-portrait-scene/evidence/v20-iter<N>.png`
- Render: `scripts/draw render <svg> -o <png>` (chrome-headless, works). Side-by-side: `scripts/draw compare image.jpg <svg> --region x,y,w,h --zoom 1.2 -o out.png` then VIEW out.png. Pixel probe: python cv2.
- Python: `.venv/bin/python` (cv2, numpy available). DO NOT use system python for cv2.

## Hard-won pitfalls (each cost a debugging session — obey)

1. `str.replace()` anchors rot: after ANY programmatic edit, assert the edit happened (count occurrences before/after) or parse-verify.
2. Regex surgery on nested `<g>` groups truncates at the first `</g>`. Use ElementTree for anything nested.
3. `file://` + relative path = blank page. render handles it; don't bypass.
4. `cv2.imwrite` fails silently on missing dirs.
5. Mask leakage: pale skirt colors ≈ pale bg colors. Constrain masks to tight regions; verify contour area is sane before using.
6. A V-notch needs lateral apex offset from the tip midpoint or the fill reads solid.
7. After every structural change: render and VIEW THE FULL IMAGE. Region zooms hide whole-figure regressions.

## Measured geometry (from pixel scans/contours — trust these over eyeballs)

### Layer order (z, bottom→top)

bg-gradient → ribbon-body → ribbon-tail-curl → white-strips → teal-band → skirt (underlayer→dark mass→zigzag→overskirt pieces) → petals → blouse/sleeves/collar-ext/jabot/bow → OVERLAYS (feathered pink/yellow/green) → face-group (transform translate(580,150) scale(0.5); contains neck, collar-sliver, skin, eyes, face-hair) → bangs-top-filler → curtain-filler → right-wall-strands → curtain → wing → curtain-flow → ARMS (cuffs, forearms, hands) → hat (underside wedge → dome+band → teal rim → poms) → brim edge strokes.

### Hat (draw as ONE silhouette + wedge + rim)

- Navy silhouette: `M 468 21 C 540 26, 600 48, 647 73 C 700 58, 760 56, 813 68 C 862 82, 894 143, 891 191 L 1024 342 L 1024 398 L 1002 370 L 972 330 L 935 290 L 890 250 L 840 208 C 800 188, 758 172, 718 132 C 700 105, 685 78, 665 66 C 610 52, 540 30, 468 21 Z` (fill #32405b)
- Teal underside wedge: `M 452 33 L 430 62 L 452 145 L 501 211 L 555 254 L 611 130 L 670 100 L 600 40 L 539 48 C 510 40, 478 33, 452 33 Z` (fill #559eae)
- Teal rim strip along band upper edge: `M 865 240 L 890 250 L 935 290 L 972 330 L 1002 370 L 1024 395 L 1024 408 L 980 360 L 945 322 L 905 282 L 868 246 Z` (fill #559eae)
- Brim edge stroke (lower band edge): `M 881 210 C 895 225, 910 240, 927 250 C 945 265, 960 278, 973 290 C 988 304, 1000 318, 1012 330 C 1016 335, 1020 340, 1024 342` stroke #1e2a3f w3
- Pom-1 (618,62 area), Pom-2 (898-996, 154-246): pink #df9199 cloud blobs.

### Skirt (the v10 inversion was WRONG — the dark navy DOES dominate)

- Dark mass: waist (630-840, 655-685) → billows LEFT+DOWN: left edge (630,660)→(596,790)→(520,900)→(455,955); hem bottom (455,955)→(700,1014)→(862,962); right edge (862,962)→(856,715)→(834,660). Fill #112e4b.
- White zigzag hem triangles ON the dark, along bottom hem: 5-6 triangles, bases on the hem, apexes up ~80-120px, x 440-860, fill #e7ecdf, varying sizes.
- Pale celadon pieces (#d2e2d6): partial layer pieces at upper-left of skirt (470-640, 690-820), wavy edges.
- Fold lines: 3 strokes #2a4a66 w3 from waist to hem, following billow.
- Translucent petals behind: 2 blobs #cfe0ea op 0.75 at (640-790, 745-875).

### Ribbon

- Body: `M 0 395 C 60 400, 150 388, 240 390 C 330 382, 420 378, 565 380 C 560 450, 545 520, 520 570 C 480 640, 432 722, 392 772 C 330 754, 255 740, 180 726 C 115 714, 50 700, 0 690 Z` fill gradient #a5dcc0→#78cbc3→#4ba7b1.
- Tail curl: stroked spiral at (12-160, 420-570): `M 12 480 C 38 432, 95 420, 132 455 C 158 480, 156 522, 128 545 C 102 566, 66 558, 54 528` stroke #a86a9a w24 round + pink highlight arc `M 20 480 C 55 440, 105 440, 132 475` stroke #e0a8b8 w10 op .85 + end flick `M 0 545 C 20 552, 38 560, 50 572` stroke #b878a8 w10.
- White angular strip: `M 310 688 L 385 672 L 452 682 L 508 700 L 558 718 L 545 738 L 470 728 L 408 732 L 350 712 L 310 688 Z` fill #eef4f2 op .9.
- Teal band: `M 0 730 C 70 738, 150 758, 205 788 L 195 808 C 140 780, 65 760, 0 752 Z` fill #4ba7b1 op .85.

### Overlays (feathered: filter feGaussianBlur stdDeviation 6)

- green: existing path (790-1024, 600-1010) op .75; pink: (200-470, 660-1024) op .6; yellow: (428-558, 902-1024) op .55.

### Face group

Embedded via `<g transform="translate(580,150) scale(0.5)">` — copy the face parts block from v17 (it is correct: skin, eyes, face-hair; neck+collar sliver must be INSIDE it FIRST, before skin groups). Face parts source: `.scratch/02-portrait-face/work/v9.svg` groups: scene{neck,collar} then face, eye-left, eye-right, hair (strip hat-corner). Verify the neck renders (pink px ~700 in zone 715-785 x 368-415).

### Arms (LONGER than current)

- cuff-right: `M 826 588 C 850 596, 872 614, 888 638 L 862 648 C 848 628, 834 610, 818 600 Z` fill #2c3a55
- forearm: from (868,645) angling down-left to wrist (818,745): path band ~28px wide: `M 860 650 C 874 668, 880 692, 872 716 C 866 736, 852 752, 834 758 C 824 761, 815 758, 812 750 C 809 742, 813 734, 821 731 C 834 726, 844 714, 849 698 C 853 682, 852 664, 846 652 Z` fill #dcdccb stroke #8a8272 w3
- hand: `M 818 726 C 806 732, 796 742, 794 754 C 793 763, 799 768, 807 766 C 803 759, 806 752, 813 748 C 809 755, 810 762, 817 765 C 824 768, 831 764, 832 757 C 834 748, 829 738, 823 732 Z` + 2 finger strokes
- If still short vs ref (ref forearm ~140-150px cuff→wrist), extend to (790,770).

### Palette

hair #3d73a7 / #3974ab · hair-outline #26354a · hat #32405b · teal #559eae · skin-face #f2e8d5 · skin-arm #dcdccb · skin-shadow #d7b1c7 · blouse #e1e7dc · collar #e7ecdf · trim #2b3b55 · bow #d44f81 · cuff #2c3a55 · skirt #112e4b · celadon #d2e2d6 · zigzag #e7ecdf · bgGrad #c3d7da→#bcd6d2 · ribbon #a5dcc0→#4ba7b1

## Iteration protocol

1. Render full frame. 2. VIEW it (read the png). 3. Write down the 3 most visible deltas vs `image.jpg` (view that too). 4. Fix those. 5. Repeat. Minimum 6 rounds. Do not report done while a naive viewer would spot missing anatomy (neck/hands/hat-brim/dark-skirt/colorful-ribbons).

## Deliverable

v20.svg (well-formed), final render png, plus a ≤15-line changelog of what you fixed per round. Commit is done by the orchestrator, not you.
