# A-track art-direction brief — what the picture must read as

Owned by: art-direction author (A track). Scope: art direction for the A candidate only. It draws nothing
and repairs nothing. Every number below comes from `work/a-measure-crop.py` running on the registered
crop (`image.jpg` bbox `500,320,900,800` → 400x480, verified equal to
`evidence/A-cloth-v6/ref/crop-400x480.png`). The numbers seed *parameters* — proportions, ratios,
taper, occlusion order, palette values. They are not coordinates to plot, and no traced contour belongs
in a spec.

## (a) What the picture must read as

**One sentence:** a person's upper body from below the mouth to the lap, sitting facing the viewer,
wearing a white sailor-collar blouse with a large magenta bow tied on the chest, hair hanging down both
sides past the shoulders.

**A viewer must be able to say, on the image alone:**
1. This is a person — there is a chin and jaw above a neck, the neck descends into a collar, the collar
   is worn on shoulders that slope away on both sides, and the head is above the shoulder line.
2. The neck and shoulders are one continuous form: no straight vertical tube from chin to chest, no gap
   where a head should be.
3. There is clothing, not a vase or a mannequin: the shoulders are round and slightly forward, the
   sleeves end at cuffs on two arms, the blouse has soft width below the bow, and the collar is a
   garment part that wraps the neck.
4. The magenta object is a *bow*: a small tight knot of gathered ribbon at the middle, two wide lobes
   spreading from it, and two tails leaving the knot, one sideways off-frame and one down across the
   chest — with the ribbon visibly crossed and turned at the knot.
5. The hair is hair: two dark masses of unequal width hanging from above the frame down both sides,
   narrower at their ends than at their tops, each carrying a few interior strand lines, one of them
   passing in front of the jaw's right side and one in front of the left chest.

**Readings that count as failure (an outside observer can state any of these on the image alone):**
- "It is a vase / bottle / mannequin / a dress on a stand." Diagnostic: the silhouette has no shoulder
  slope, or the neck-to-shoulder transition is a straight vertical, or nothing sits on a head above.
- "There is no head, only a pink column." Diagnostic: no chin corner, no jaw line, no mouth mark, and
  the skin region has the same width at the top of the frame and at the collar.
- "The bow is two closed pills." Diagnostic: each lobe's outline closes on itself; there is no internal
  crease; both outlines are drawn through the crossing; the top edges are straight and parallel.
- "The hair is flat paper ribbon." Diagnostic: constant width end to end, square end cuts, no interior
  strand lines, a background-coloured hole between masses.
- "The neck and collar are geometry, not anatomy." Diagnostic: the collar is a rectangle/ring floating
  around a cylinder, the neck has no trapezius slope into the shoulder, no skin shading under the jaw.
- "The arm is a sleeve with nothing in it." Diagnostic: no cuff band, no forearm leaving the cuff, no
  hand or arm mass at the end of the sleeve.

## (b) Composition and proportion table

All ratios are of the measured reference; tolerance is what an observer would still accept as the same
picture. Lengths in crop px (400x480).

| quantity | measured | ratio | tolerance |
| --- | --- | --- | --- |
| face (lit skin) width in crop | x131–272 = 141 | 3.2 × neck width | ±15% |
| jaw: descends from the left face edge to the chin corner | (129,0) → (190,56); turns back up at 56, then hidden behind a hair lock from x≈215 | jaw drop 56 px ≈ 0.12 of crop height | ±0.03 |
| mouth mark | 6×1 px at (179,33) — the only facial feature in the crop | 0.043 × face width | ±50% (it is a mark, not a shape) |
| neck width | 41–48 px at y=65–85, 26–37 px at y=95–105 | 0.12–0.20 × shoulder width | ±20% |
| neck centre line | x≈241 at y=75 → x≈216 at y=105 | drifts 25 px left over 30 px down (≈40° lean) | ±15° |
| neck height (jaw to collar) | y56 → y≈100 | 92 px total head-to-collar ≈ 0.19 of crop height | ±0.03 |
| collar overall | x148–348, y85–148 | 200 wide = 0.86 × shoulder width; 63 tall | ±15% |
| neck opening at the collar | y=110: skin 203–222 | 20 px = 0.46 × neck width at the jaw; opens to 37 px at y=95 | ±25% |
| collar front leaf (white) | x138–173 at y=110 | 36 px = 0.18 × collar width | ±25% |
| collar navy stripe | 5 px at y=110; measured ink run 8 px on col 156 | 0.03 × collar width | ±40% |
| shoulder width at collar level | body cloth 120–351 at y=130 | 232 px = 0.58 × crop width | ±10% |
| widest body span incl. right sleeve | 83–399 at y=210 | 317 px = 1.37 × shoulder width | ±10% |
| shoulder→arm corner (right) | cloth right edge 362 @y=180 → 387 @y=185 → 399 @y=205 | corner at y≈183, i.e. 98 px below the collar's top edge = 0.20 of crop height | ±0.02 |
| waist (below the sleeve) | 103–283 at y=290–330 | 175–180 px = 0.75 × shoulder width | ±12% |
| bow | bbox 239×152 at (33,134)–(271,285) | width 1.03 × shoulder width; height 0.32 × crop height | ±12% |
| bow lobes (outside the knot) | left lobe 118→199 (81 px), right lobe 208→271 (63 px) | lobe width 0.34 / 0.26 of bow width | ±15% |
| bow knot | narrowest cross-section at x=201: y144–202, 59 px tall; the drawn crease gap runs at x=199–202 from y=206 down | knot height 0.39 × bow height; knot sits at 0.50 of crop width | ±20% |
| bow top edge | y=134 at x≈140, y=143 across x 129–271 | the top edge is a slightly rising curve, not a horizontal | ±6 px |
| bow tails | left tail x33–115: 2 px tall where it meets the crop edge, 28 px tall at x=81; lower tail 78 px wide at y=278, tip at y≈285 | left tail runs 168 px from the knot (x≈200) to the frame edge = 0.42 of crop width | ±20% |
| right sleeve puff | shoulder corner y≈183 → cuff top y=268 | 85 px long = 0.37 × shoulder width | ±15% |
| right cuff band | bbox (337,268)–(399,328), 2036 px, axis 144°, thickness ≈28 px, length along that axis ≈73 px | thickness 0.12 × shoulder width; length ≈2.6 × thickness | ±20% |
| second cuff band | bbox (85,256)–(108,276), 24×21, ≈345 px | 345 px of navy against the right band's 2036 = 17% survives | ±30% |
| forearm below the cuff | skin begins (369,306) and fills the corner | cuff→forearm boundary at 144°, parallel to the cuff | ±8° |
| hair, right mass | bbox (274,0)–(399,252), max row width 125 | 0.54 × shoulder width; 0.53 × crop height | ±12% |
| hair, left mass | bbox (0,0)–(142,120), max row width 70 at y=31 | 0.30 × shoulder width | ±15% |
| hair lock at the jaw | bbox (227,0)–(267,65), max width 25 at y=19 | 0.6 × neck width, 66 long | ±20% |
| periwinkle ribbon (second blue, a separate object) | (0,211)–(53,238) and (44,280)–(104,361) | a lighter blue than the hair — #5572aa vs #3b71a1, see (d) | — |

Ledger of what the crop is: face cut by the top edge; the right arm and the right hair run off the right
edge; the left tail and the left hair run off the left edge; the lap fills the bottom quarter.

## (c) Per-object shape facts that make it read

**Bow** (single continuous ribbon: knot → lobe → knot → lobe → knot → two tails).
- The knot is a wrapped band, not a patch: measured 59 px tall × ~9 px of crease gap at x 199–202, which
  is the turn of the ribbon. Both lobes must spring from the same two edges of the knot; no lobe outline
  may close independently of the knot.
- Lobes are solid cloth with curved free edges (the outer edges bulge and return), and they carry internal
  crease lines with measured endpoints: (119,202)→(171,268) 83 px; (124,201)→(168,218); (129,196)→(164,206);
  (174,145)→(187,165); (196,192)→(226,220); (197,151)→(205,171); (199,170)→(223,178). Seven interior
  strokes on a 239×152 object; each is a fold, not a texture.
- The ribbon is *dark* where it turns: the fold shadow is #80183f against the fill #d34e7f (measured at
  (140,205) vs (140,175)). Without that value difference the knot cannot read as wrapped.
- Tails leave the knot under the lobes and taper: the left tail is 2 px tall where it crosses the crop's
  left edge and 28 px where it leaves the knot; the lower tail narrows from 78 px at y=278 to the tip.
  A tail's root edge must sit inside the knot, never beside it.
- Occlusion: the left tail crosses in front of the second cuff and in front of the periwinkle ribbon; the
  lower tail crosses in front of the blouse. The crossing order must come from depth, and each crossing
  must *break* the rear object's outline rather than run both outlines through.

**Hair** (two-sided curved sheet, S1 mechanism; not a flat band).
- Right mass: 125 px at its widest, 4 px at the tip at y=247–252 — a taper of 30:1, achieved by a pointed
  end, not a cut. Left mass: 70 px at y=31 narrowing to 6 px at y=120.
- Width varies *along* the mass (max at 0.2 of its length, not constant), and the mass must show its two
  sides: the fill is chosen by which face of the sheet points at the viewer.
- Interior strand lines: the measured masses carry 7 and 3 interior strokes, each 1–3 px wide and 14–32 px
  long, at stated positions. A mass with zero interior strokes reads as paper.
- The lock at (227,0)–(267,65) crosses in front of the jaw's right side and continues over the neck; the
  neck's right edge is *behind* it. The right mass's left boundary lies against the collar's pale blue and
  the blouse, not against background.
- No background-coloured hole may appear inside a hair mass: the reference has none. Where the masses meet
  the blouse, the boundary is a drawn edge with the blouse continuous on the other side.

**Neck and collar.**
- The jaw must be a corner: a drawn line descending to (190,56), then turning back up; the chin is not a
  curve tangent to the neck. Below it the neck runs 45 px down to the collar and its centre line leans
  ~40° left as it descends — the neck is not vertical.
- Skin under the jaw is the shaded value #d9adc3, the face is #f2e8d5: a value break at the jaw is what
  makes the head read as sitting on the neck rather than merging into it.
- The collar wraps: white front leaf (36 px) → navy stripe (5–8 px) → pale-blue body → neck opening
  (20 px at y=110) → pale-blue body → navy stripe → pale-blue leaf. The opening is *narrower* than the
  neck above it, i.e. the collar grips the neck, and the two leaves lie at different depths (the right
  leaf overlaps the shoulder, the left leaf is cut by the bow).
- Trapezius: the shoulder line leaves the collar at a slope, not a horizontal — the body's left edge runs
  x=138 at y=110 to x=83 at y=210, i.e. the shoulder edge descends 1.8 px for every px it moves outward.

**Sleeves and cuffs.**
- The sleeve is a puff that widens from the shoulder to above the cuff (right sleeve's outer edge climbs
  from x=355 at y=150 to the frame edge by y=205), then is bound by a *dark band at an angle* (axis 144°,
  28 px thick, 12 px of measured ink run at its upper edge).
- The dark band is the pivot that makes the arm read: above it cloth, below it skin. The forearm's first
  skin appears at (369,306), immediately under the band and parallel to it.
- The second cuff exists and is *partially* visible: 24×21 px surviving, against the right cuff's 63×61.
  The pink tail crosses it on its upper right and the periwinkle ribbon on its lower left; the white
  sleeve sliver above it is a few px. Authored whole; the surviving shape is depth's output, never an
  authored cut.

## (d) Ink and colour policy by measured class

Measured widths (dark run, luminance < 100, one probe each; colour boundaries carry no dark line):

| class | treatment | measured |
| --- | --- | --- |
| figure silhouette | darkest and crispest line; navy-black #102838 family | 1–3 px |
| garment colour boundary (collar stripe, cuff band) | no black line: the fill itself is the edge; where a line is drawn it is the band's own dark value | stripe 8 px, cuff edge 12 px |
| fold / seam stroke inside cloth | thinner and lighter than the silhouette, on the shade value #8cbecf family | ≤3 px |
| hair interior strand | 1–3 px, same value as the hair's dark side | 3 px |
| chest dark band (under the bow, centre) | a genuinely dark mass, not a line | 14 px wide |
| skin boundaries | value break only (lit #f2e8d5 / shade #d9adc3); no outline inside the face | — |

Palette (all sampled at a stated coordinate, listed in full in the script's section 7):

| region | hex | sample |
| --- | --- | --- |
| background, mint field | #77c8bf | (30,260) |
| background, pale blue-grey | #d1dbdf | (12,12) |
| background, teal lower right | #48a8b3 | (300,430) |
| skin, lit | #f2e8d5 | (180,20) |
| skin, shaded (under the jaw) | #d9adc3 | (240,60) |
| blouse, white | #ddebdd | (200,300) |
| lower garment / lap | #d2e2d8 | (60,450) |
| cloth shade, pale blue | #8cbecf | (150,430) |
| collar pale blue | #a1c6de | (300,100) |
| navy stripe / cuff | #3d4a6a / #2c3a57 / #2f3c5c | (151,110) / (360,300) / (95,266) |
| bow fill | #d34e7f | (140,175) |
| bow fold shadow | #80183f | (140,205) |
| hair | #3b71a1 and #346d95 | (60,60) / (370,200) |
| second blue, periwinkle (ribbon, not hair) | #5572aa | (12,222) |

Two policy consequences that come straight out of the table:
- The blouse white (#ddebdd) and the lap (#d2e2d8) are the *same value family*: separate them by a drawn
  line and by shading, never by a colour change.
- Hair (#3b71a1) and the periwinkle ribbon (#5572aa) are *different* blues. Painting the ribbon with the
  hair fill merges two objects that the reference keeps apart.

## (e) Falsifiable checklist for the next reviewer

Answer each on the image alone, without reading the source. **No = failure.**

1. Above the neck there is a head shape with a visible jaw corner and a mouth mark, and the skin is
   narrower at the collar than at the jaw? (no → the "pink column")
2. The neck's centre line is not vertical and the neck narrows as it descends into the collar?
3. The collar opens around the neck, its opening narrower than the neck above it, with a white leaf, a
   dark stripe and a pale-blue body in that order on at least one side? (no → geometry, not anatomy)
4. Both shoulder slopes exist, and the shoulder line leaves the collar at an angle rather than
   horizontally, so nothing about the outline is a straight vertical from chin to chest? (no → vase)
5. A viewer can name the magenta object as a bow with a knot, two lobes and two tails? (no → "two pills")
6. Inside the magenta shape there are at least three separate interior crease strokes, one of which is
   where the ribbon turns at the knot, and at least one area noticeably darker than the fill? (no →
   flat sticker)
7. No magenta lobe has an outline that closes on itself independent of the knot, and no rear object's
   outline is drawn *through* a crossing point? (no → impossible object)
8. Two sleeves exist, each ending in a dark band, and the second band is only partly visible with the
   pink tail crossing in front of it? (no → one sleeve; or a hand-authored cut)
9. Below the right dark band there is skin continuing as a forearm, and the band's angle and the forearm's
   direction agree? (no → "a sleeve with nothing in it")
10. Both hair masses hang past the shoulders, each visibly narrower at its end than at its widest point,
    with the ends pointed or tapered rather than cut square? (no → paper ribbon)
11. Each hair mass carries visible interior strand strokes, and no background-coloured hole exists inside
    any hair mass? (no → punched hole / flat band)
12. One hair mass visibly crosses in front of the jaw or neck and the rear outline breaks there? (no →
    hair that is a sticker behind the head)

Checklist scoring: any single "no" blocks the candidate; a "cannot tell at 1:1" counts as no.

## (f) Non-goals and out of scope

Must **not** be added:
- A face you cannot draw well. The crop shows a chin, a jaw and a 6×1 mouth mark, nothing else. Eyes,
  nose, brows or a full head are forbidden: an invented eye is worse than the cropped emptiness the
  reference actually has.
- A full body, legs, or a seated pose. The crop stops at the lap; the lap is a mass with fold lines, not
  an anatomical pelvis.
- An invented background. Background stays the three measured flat fields (mint, pale blue-grey, teal),
  no scenery, no gradient mesh, no vignette.
- A symmetrical bow, a symmetrical figure, or mirrored hair. Every measured pair differs (lobes 81 vs
  63 px, hair 143 vs 126 px wide, cuffs 63 vs 24 px visible); symmetry is a misread of the reference.
- Extra decorations: no ribbons the reference does not show, no buttons, no texture, no soft-field
  gradients. Soft fields are the last tier and are not part of this target.

Out of scope for the A track:
- Hands. No hand claim, and no palm or fingers; the right arm ends as a cuff plus forearm, the second
  arm's visible part is a cuff wedge. Adding a hand invents what the crop does not show.
- Pose and gesture; the figure's posture is whatever the shoulder/collar geometry implies.
- Anything outside the registered crop: no reference geometry from `image.jpg` outside `500,320,900,800`.

## Provenance and what is uncertain

- Every number above is printed by `work/a-measure-crop.py` (deterministic, rerunnable, verifies the crop
  against the bbox before measuring).
- Least confident measurements: (1) the *knot's* extent — it is inferred from the narrowest vertical
  cross-section and the crease gap, not from an object boundary, so ±20% at best; (2) the collar leaf
  widths — JPEG noise makes blouse white and pale-blue shading flip near their boundary, and the left
  leaf is cut by the bow; (3) the second cuff's coverage percentage — its visible area is firm but "what
  covers the rest" is an occlusion *order* read from adjacency, not measured depth; (4) ink widths — one
  probe per class, and this drawing has almost no black interior line work, so "fold stroke ≤3 px" rests
  on a small number of samples.
- Not measured, therefore not claimed: absolute 3D depth of any part; whether the periwinkle ribbon is in
  front of or behind the second cuff; the number of ribbon layers at the knot.
