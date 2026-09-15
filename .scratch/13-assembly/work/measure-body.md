# M3 body/cloth measurement — reference `image.jpg` (1024×1024)

Read-only reconnaissance for M3 ("beat the baseline on body and cloth"). Everything below is
measured from `image.jpg` with colour-component probes (BGR + tolerance + **region restriction**),
using the same method as `measure-composition.py`. Colours repeat in this palette (the dark navy is
hat crown + skirt + cuffs + bow tail; the cream is blouse + skirt), so **every probe is
region-restricted** and the region is stated in each row. Bboxes are `x0,y0 - x1,y1` in 1024-space;
`% frame` = area / 1 048 576.

Anchors reused from `spec.yaml` (not re-measured): head/face, hat, hair, blouse pale, skirt pale,
bow magenta, skirt dark, mint field, petals, ribbon.

## Measured elements

| element | bbox x0,y0 – x1,y1 | centroid | area px | % frame | how measured | confidence |
|---|---|---|---|---|---|---|
| Sailor collar — full (pale body + navy trim) | 649,384 – 848,468 | (750,430) | ~7 200 | 0.69% | union of the two probes below, region x[620,860] y[380,490] | med-high |
| Collar pale-blue body | 662,384 – 847,464 | (751,427) | 6 160 | 0.59% | probe `#96c3d6` BGR(214,195,150) tol 20, region x[620,860] y[380,490] | high |
| Collar navy trim band | 649,409 – 827,468 | (745,445) | 1 145 | 0.11% | probe `#374b68` BGR(104,75,55) tol 24, same region | med-high |
| Right puff-sleeve cap (viewer right) | ~790,465 – 870,605 | (~830,535) | ~5 500 (est) | ~0.52% | **not colour-separable** — same cream as the blouse; bbox read from the armhole seam (faint dark line at x≈797, y 505–595) + outer silhouette + collar/cuff bounds | **low** |
| Right navy cuff band | 837,586 – 922,648 | (878,614) | 2 534 (total 2 867) | 0.24% | probe `#2d3b58` BGR(88,59,45) tol 18, region x[800,960] y[555,700] | high |
| Forearm skin patch (right arm) | 869,622 – 924,665 | (896,643) | 1 309 | 0.12% | probe `#c9aabb` BGR(187,170,200) tol 24, region x[840,940] y[610,740] | high |
| Right arm — forearm cream mass | 790,658 – 925,905 | (854,760) | 9 555 | 0.91% | probe `#ccded7` BGR(204,222,215) tol 14, region x[780,960] y[635,930]; principal axis **117°** (down-left, ~27° from vertical), endpoints (907,656)→(795,877) | med-high |
| Hand (shadowed fingers) | ~845,878 – 870,928 | (~857,903) | ~450 | ~0.04% | mauve shape at the arm's lower end; bounded by an outline, but could be a translucent petal over the skirt | **low** |
| Bow magenta — all | 540,456 – 770,601 | (671,522) | 15 018 | 1.43% | probe `#d35081` BGR(129,79,212) tol 35, region x[480,820] y[430,720]; one connected component | high |
| Bow right loop | 690,462 – 770,554 | (726,501) | 5 032 | 0.48% | magenta subset x≥690 | med |
| Bow left loop (upper lobe) | ~540,456 – 647,575 | (~615,515) | ~4 500 | 0.43% | magenta subset x<648, y<575 | low-med |
| Bow knot | ~648,500 – 689,570 | (~667,535) | ~2 000 | 0.19% | magenta subset x[648,689]; knot is only ~1% darker (`#cf4e7e`) so not separable by colour | low |
| Magenta tail | 572,561 – 687,601 | (640,578) | 2 593 | 0.25% | magenta subset y>560; runs left/slightly down (angle 6°) | med |
| Navy ribbon tail (below the bow) | 647,603 – 669,682 | (656,638) | 986 (main 865) | 0.09% | probe `#2f3c58` BGR(88,60,47) tol 16, region x[600,720] y[560,720]; steep (66°), hangs down from the knot | high |
| Skirt navy trim / edge arcs | boundary, no distinct colour | — | — | — | row-scan of pale↔dark transitions; the trim is the same navy `#2b546d` as the skirt body | med |
| Skirt fold-line directions | — | — | — | — | Canny + HoughLinesP, length-weighted angle histogram; **3–4 dominant directions** | med |
| Petal rose/salmon | 208,850 – 420,1024 (upper lobe 220,786 – 328,861) | (325,927) + (272,821) | 24 470 | 2.33% | probe `#e59295` BGR(150,144,227) tol 20, region x[40,700] y[600,1024]; two components | high |
| Petal peach/cream top | 222,627 – 432,767 | (343,705) | 14 480 | 1.38% | probe `#f2ddd9` BGR(218,222,242) tol 14, same region | med |
| Petal pale blue | 313,771 – 472,848 | (387,807) | 6 740 | 0.64% | probe `#89bccc` BGR(204,188,138) tol 16, same region | high |
| Petal warm tan/orange | 421,930 – 564,1024 | (489,984) | 9 380 | 0.89% | probe `#e3c695` BGR(149,199,227) tol 18, same region | high |
| Petal pale green | 78,600 – 333,695 | (222,638) | 15 316 | 1.46% | probe `#a9ce9a` BGR(169,206,154) tol 18, same region; may be a translucent petal over the mint field | low-med |
| Petal light pink | ~299,766 – 348,852 | (~327,810) | ~1 100 | 0.11% | probe `#f5d1de` BGR(222,209,245) tol 10; two small patches, may merge with the peach patch | low-med |

Secondary pale-blue patches inside the skirt (same probe as "petal pale blue"):
`500,878–600,947` (2 465 px) and `65,968–159,1024` (3 079 px) — edge highlight bands, not central petals.

## Collar shape (the V/opening)

The navy trim traces the collar's front edge as a **shallow wide U**: lowest point **(760,466)**,
rising left to (655,447) and right to (825,430). The pale-blue field sits above/inside it, spanning
x 662–848, y 384–468. The front opening (where the two flaps part) is on the **left, under the bow**
(no trim is visible left of x≈649 because the bow covers it). At the shoulders the collar meets the
blouse at the pale-blue/cream boundary, roughly the same curve — there is no separate seam colour.

## Skirt trim and pleats

- **Trim arcs:** the dark-navy "trim" is *not a distinct colour* — it is the same `#2b546d` navy as
  the whole underskirt. The visible arcs are just its edge against the cream apron. The apron's
  right/under edge against navy runs from about (770,720) down to (700,950), with a navy band
  ~20–40 px wide; a pale-blue highlight band (`#8abdce`) sits just inside it.
- **Fold directions (length-weighted Hough histogram):**
  - **~140–150°** (down-left, e.g. (521,862)→(640,791)) — strongest, the pale apron's main pleats;
  - **~30–47°** (down-right, e.g. (524,858)→(626,929)) — several, on the dark skirt left;
  - **~87–107°** (near-vertical) — apron seams;
  - **~170–173° / 0°** (near-horizontal) — hem bands and petal edges.
  So roughly **3 dominant cloth-fold directions** (≈145°, ≈40°, ≈95°) plus horizontal hem edges.

## Bow structure

- Overall magenta mass: 15 018 px, bbox **540,456–770,601**, centroid (671,522). One connected
  component, so loops/knot/tail are split only by column/row cuts (hence the lower confidence).
- **Right loop** is clean: 690–770 × 462–554.
- The magenta tail is short and points **left, slightly down** (bbox 572,561–687,601); it does not
  reach down the left of the blouse — what reads as a long "tail" there is the **blue background
  ribbon** (`#5372ae`, already measured as `ribbon blue`).
- The **navy ribbon tail** is the separate dark band 647–669 × 603–682 hanging down from the knot.

## Could NOT separate reliably (honest gaps)

1. **Left puff sleeve** — fully occluded by the bow. Only **55 cream px** survive in the left
   shoulder region x[480,570] y[420,560]. No usable bbox.
2. **Right puff sleeve vs blouse** — identical cream; a flood fill from inside the sleeve leaks into
   the blouse (22 632 px, same as a blouse-seeded fill), and the armhole seam is a faint line
   (gray ≈85 vs 230) that does not close. The bbox in the table is read off the seam line, not
   colour, hence **low** confidence.
3. **Placket** — there is **no narrow navy-piped band distinct from the bow's ribbon tail**. The
   only vertical navy strip on the blouse front is the ribbon tail (647,603–669,682). A vertical
   cream strip with fold lines exists around x[655,700] y[600,770] but has no distinct fill colour,
   so its width cannot be measured by this method. Reported as "not separable", not as zero.
4. **Hand vs. background petal** — the mauve shape at 845,878–870,928 sits at the end of the
   forearm and is outline-bounded, but its colour (#b2829b) is close to the translucent petal
   overlay; it cannot be confirmed as skin. Low confidence.
5. **Left arm** — not visible at all (hidden behind the bow/body); no probe finds it.
6. **Navy trim arcs vs. skirt body** — same colour; only the boundary is measurable, not a trim
   object.
7. **Exact fold-line count** — Hough lines are broken by the petals and highlights; the 3-direction
   summary is a length-weighted histogram, not a per-pleat count.
8. **Petal patch inventory is fuzzy at the edges** — the 6 patches above are colour-distinct, but the
   light-pink and peach patches overlap in the tolerance band, and the pale-green patch may be the
   field rather than a petal. The rose, pale-blue and tan patches are solid.

## Instrument

The `body & cloth (M3)` block appended to `measure-composition.py`'s `PROBES` reproduces the rows
above. Note: in `reference` mode the script only prints connected components **≥1200 px** (the
existing `components()` default, left untouched), so probes whose mass is split into components
below that floor — `collar trim navy` (1 145 px total), `forearm skin R` (1 309 px across two
components), `bow tail navy` (986 px) — print `(none)` there; they still resolve correctly in
`compare` mode, whose `mass()` has no such floor. Both commands were run and exit cleanly.
