# review-log — the self-review rounds, each against the render it judged

`ACCEPT.md` is the line. This is the loop. Every round names the render it judged by hash, lists the
mismatches it found ranked by whether they change *identity* (what she is, where she is, what she
wears) or only craft, and says what the next round changed. A round that did not shorten the identity
list is recorded as a failure, not folded into the next one.

The reference is `image.jpg` (1024×1024) and the crops in `ref/`. Comparison is visual, side by side,
at 1:1.

## Round 1 — `ff1` (first assembly: hat, head, hair-back, falls, skirt, arm over the inherited torso)

Identity list, worst first:

1. The brim sits too low and too large and swallows the head: the face is almost entirely under it.
2. The face is small and hidden; the eyes are unreadable.
3. The neck is a wide pink slab running from the jaw to the collar.
4. The hair reads as one blue blob on the left plus two thin strips; nothing falls in front of the
   shoulders.
5. The bow is small against the reference's, and the torso is dwarfed by the skirt.
6. The arm is a pink stick ending in a floating dot.
7. The pink lining is a rectangle floating on the navy.
8. Palette: the hair is too dark, the ground too green and flat.

Changed: the composition was re-authored from measured landmarks (`ref/head.png`, `ref/torso.png`,
`ref/lower.png`): brim raised and re-tilted with a teal underside and a navy top face, the head
enlarged to the reference's 170 px face, two hair falls added in front of the shoulders, the lower
mass given a navy under-layer and two lining bands.

## Round 2 — `ff3`

1. The fringe covers the whole upper face down past the eyes: the figure reads as hooded, not
   fringed.
2. The eyes float on the fringe with no skin around them.
3. The hair falls are thin V-shaped strips with visible taper points, not masses.
4. The hat's crown reads as a second hat: it is small and sits off to the right.
5. The neck shows a doubled jaw line, and a blue V crosses the chest.
6. The skirt is a round cream balloon three times the torso's area.

Changed: fringe lifted to the brow line; falls widened and extended past the frame's bottom edge so
no taper point floats; the mass behind the head routed past the bottom edge; the crown enlarged and
centred on the brim's top face; the neck pulled up under the chin and narrowed; iris enlarged to fill
the lid; arm widened.

## Round 3 — `ff4`

1. The falls are now flat blue curtains that cover the shoulders and the bow.
2. The fringe still reaches below the eyes on the right, and a notch of blue crosses the chin.
3. The brim's underside is a dark sliver; the thin chord line reads as a seam.
4. The skirt is still a balloon; the navy under-layer and the pink band are small islands.
5. The collar and bodice are almost entirely covered by hair.

Diagnosed rather than tuned: the blue V across the chin and chest, and the doubled jaw line, are two
*inherited* parts placed by the crop's own frame — `A-head-face` ends its jaw at image y 442 (the
crop's chin, 58 px below this frame's chin) and `A-hair-sheet` crosses in front of what is chest in a
full figure. Both are dropped from this frame and replaced by parts authored for it; the drops are
recorded in `source/full/figure.py:build` with the measurement that justifies each.

## Round 4 — `ff5`

Identity list now:

1. The falls are still two straight columns with hard inner edges.
2. The top of the head is a blue helmet with no hairline and no strand separation.
3. The jaw is wide and square; the chin does not taper.
4. The torso is squeezed between the bow and the skirt; the collar's V is not readable.
5. The right arm is disconnected from the cuff; the hand floats.
6. The skirt has no fold structure.

Changed: the face ring re-cut to eleven points that taper from the temples to a narrow chin; the
fringe re-cut to a hairline with points between and beside the eyes; the falls' width profile widened
at the head and tapered at the bottom; the arm moved back into the cuff.

## Round 5 — `ff6`

1. The falls attach at the temples and read as a wig with straight-cut sides.
2. The fringe's lower edge is nearly straight across the forehead.
3. The collar is barely visible under the chin.
4. The skirt is one flat balloon with no pleats; the lining bands do not follow the folds.
5. The arm is a rectangle with a floating ball for a hand.
6. The brim's underside has a hard straight chord and a stray hairline.

Changed: the falls' routes now start under the fringe and sweep outward, with a thin lock added in
front of each shoulder (the reference's cascade); the skirt re-coloured to the reference's mint with a
cream fold, and the lining bands re-cut to sit inside the navy under-layer.

## Round 6 — `ff7` (the state this advance lands)

Judged: `check/draft-fullres.png` at `artwork.svg` — this commit.

Identity list, worst first, and none of them is "it is a different picture":

1. **The hair crowds the face.** The falls attach wide enough that the face sits between two hair
   walls, and the left lock clips the left eye's outer corner. The reference leaves cheek, ear and
   jaw clear on the left and lets the hair start outside the eye.
2. **The falls' inner edges are perfectly straight vertical lines.** Hair is read by a broken,
   curving inner edge; a strip's straight edge is the single most drawing-like thing left.
3. **The lower mass has no fold structure.** It is one mint balloon; the reference is a stack of
   overlapping pleats with a navy pleat and the pink/orange ribbons running diagonally through them.
4. **The right arm is a disconnected slab** — no taper, no wrist, and the hand is a circle.
5. **The collar is not readable.** The reference's light-blue sailor collar is the second-largest
   shape on the chest; here it is a sliver behind the bow.
6. **The brim's underside boundary is a straight chord** with a stray thin line across it.
7. Craft only: the fringe's strand separations are missing; the mouth is a flat oval.

None of items 1–6 changes *what she is*: hat with two pink puffs, long blue hair, cream sailor dress
with a magenta chest bow, big eyes, seated on a teal ground with her skirt to the left. The figure is
whole in the frame — the hat is cut by the top edge exactly as the reference's is, and the lower mass
runs past the bottom edge. Round 6 is a **landing point, not a pass**: T6 is not cleared.

## What round 7 must change, in this order

1. Pull both falls outward and start them at the ear, so the face is clear; drop the left lock's
   radius so it does not clip the eye.
2. Break the falls' inner edges: replace the strip's straight edge with a wave whose amplitude is a
   function of station (one generator term, not typed points).
3. Give the lower mass its pleats: three overlapping mint/cream wedges plus the navy pleat, with the
   lining bands inside them.
4. Rebuild the arm as a tapered strip with a wrist, and give the hand the study's finger mass.
5. Bring the collar forward: raise the collar's depth above the bow's chest, or re-cut the bow's
   position so the collar's V shows above it.

## Round 7 — `ff8` (falls pulled out, waves, pleats, tapered arm)

1. The left fall's width and route put it straight across the left eye: the face lost half.
2. The hand came out cream — `planar()`'s default fill, not skin.
3. The pleats were invisible: three of them sat *behind* the skirt's own depth.
4. The brim still carried a thin chord line across it, which read as a scratch.

Changed: the wave ramped in over the first quarter of the route so the attachment stays unbroken;
the falls' routes moved out to the temple; `fill=SKIN` on the hand; pleats moved in front of the
skirt; the brim's chord mark deleted.

## Round 8 — `ff9`

1. The falls are two straight vertical slabs with a rectangular notch at the head.
2. The navy pleat is a dark gulf across the skirt's right.
3. The skirt is a flat balloon; the cream pleat is a pale blob at the bottom.
4. The arm is a slab; the hand is a lump with no wrist.

Diagnosed: a strip's two edges are *the same generator's offset*, so no width profile can make an
inner edge that is clear of the bodice while the outer edge follows the silhouette. The falls were
converted from strips to closed curtains (`fall_left_poly`, `fall_right_poly`: nine landmarks each,
catmull, both edges authored) with three strand curves inside each.

## Round 9, 10 — `ff10`, `ff11` (curtains, then clearance)

- `ff10`: the curtains' inner edges still crossed the left sleeve and the bow's left tail; the right
  fall buried the right sleeve, its cuff and the arm. Navy pleat narrowed to a fold.
- `ff11`: the right fall's inner edge moved out to x 846 at the shoulder; the arm's depth dropped to
  0.29 so the inherited cuff (0.30) occludes its top and it emerges from the sleeve instead of
  starting in mid-air.

## Round 11 — `ff12` (palette measured, not guessed)

Every fill was sampled from the reference at named points and the deltas written down. Eight of the
ten fills were already within ΔRGB ≤ 20; three were not, and were corrected to the sampled values:

| fill | was | now | reference sample | Δ after |
| --- | --- | --- | --- | --- |
| skin | `#e6c4bd` | `#f2e3d3` | (244,231,213) at (660,300) | 2 |
| brim underside | `#8cb8bd` | `#569cae` | (86,156,174) at (470,150) | 0 |
| ground teal | `#78a49b` | `#56adb8` | (86,173,184) at (150,760) | 0 |
| skirt mint | `#d8e6cf` | `#cbdfd3` | (203,223,211) at (620,900) | 0 |
| hair lit / shade | `#3a72b4` / `#274f85` | `#3e73a5` / `#2f5f92` | (62,115,165) / (55,114,169) | ≤ 8 |

Hat navy, dress cream, bow magenta, cuff navy and puff pink were already within 20 and are unchanged.

## Round 12 — `ff14` (the state this advance lands)

Judged: `check/draft-fullres.png` at `artwork.svg` — this commit. `check/head-2x.png` is the head at
2×, which is where identity is decided.

Identity list — what still stops T6 from clearing, worst first:

1. **The hair is flat.** The curtains' edges are right, but nothing inside them varies: the reference's
   hair has a lit face and a shaded face with a soft boundary, and its strand lines curve. Mine is a
   flat fill with three straight-ish strands.
2. **The lower mass is a stack of flat panels**, not folds: the skirt, its fold and the pleats meet at
   hard edges, and the navy pleat reads as a shape laid on the skirt.
3. **The collar is small.** The reference's light-blue sailor collar is the second-largest shape on
   the chest; here it is a sliver behind the bow, because the inherited collar was cut for a neck
   opening 58 px lower.
4. **The hat/hair relationship is inverted at the top of the head**: in the reference the hair emerges
   from under the brim with the brim's shadow on it; here the brim's teal underside and the hair meet
   at a hard line with no shadow.
5. **The hand is still a mitten blob**; the arm has no wrist.
6. Craft only: the fringe's points are too regular; the mouth is a flat oval; the bodice has no
   gathered waist.

**Assessment against `ACCEPT.md`, stated plainly and not rounded up:**

| term | state | evidence |
| --- | --- | --- |
| T1 whole figure | **pass** | hat cut by the top edge as the reference's is (crown top at y 0), lower mass runs past the bottom (y 1024); silhouette bbox x 415–968, y 0–1024 against the reference girl's x 420–1020, y 20–1024 |
| T2 parts present | **pass** | 26 objects, 41 parts, `missing_objects: []`, `undeclared_parts: []` in `build-report.json`; `tests/test_full_figure.py` fails if either list is non-empty |
| T3 proportions | **pass** — all four within 8 % | head height 214 px vs 210; brim width 534 vs 525; eye line 264 vs 262 (both /1024); face width 166 vs 180 |
| T4 hat/hair/bow relations | **partial** | brim overhangs the face on both sides ✓; falls in front of the shoulders ✓; bow on the collar's V ✓; the brim/hair junction has no shadow ✗ (item 4) |
| T5 palette | **pass** | ten fills sampled against the reference; every ΔRGB ≤ 20 except the two the table above corrected |
| T6 reads as her | **not cleared** | the identity list above has six entries; items 1–5 are visible at a glance |
| T7 discipline | **pass** | determinism, no image read, inventory, colours, one line policy, manifest |

So: **the figure is whole and the parts are all there; the picture is not yet good.** The next
advance's work is the six items above, in that order, and T6 is the only one that can clear it.

## What the next advance does, in order

1. Give the hair a light and a shade: split each curtain along its own fold into a lit and a shaded
   region with a curved boundary, and curve the strand lines (one generator, not typed points).
2. Turn the lower mass into folds: overlap the pleats with the skirt rather than laying them on it,
   and give each pleat two edges that are not parallel.
3. Enlarge the collar: the inherited collar's opening is 58 px below this frame's chin, so the figure
   needs a collar cut for its own neck — a new part, with the inherited one kept as its inner leaf.
4. Put a shadow under the brim: a soft band on the hair where the brim's edge crosses it.
5. Rebuild the hand from the hand study's own mass (the `B-hand-*` packages have the geometry), and
   give the arm a wrist.

## Round 13 — `ff15` (the landing render after two defects a 2× look found)

A 2× crop of the head (`check/head-2x.png`) showed two things the 1:1 view hid:

1. **Three grey lines fanned across the hat brim.** They were the left fall's strand marks: the
   strands were made by offsetting the curtain's landmarks, which put them *outside* the curtain and
   in front of the brim (z 0.505 against the brim's 0.20). Strands are now a fraction of the way from
   the curtain's outer edge to its inner edge at three heights, so they cannot leave the curtain.
2. **The eyebrows read green.** They were drawn in `HAIR_DEEP`, the darkest teal shade; they are now
   `HAIR_SHADE`, the hair's own mid tone.

Both are craft, not identity. The six identity items in round 12 stand, and so does its assessment.

## Round 14 — `ff19` (the tests found three things the eye did not)

The suite written for the figure (`tests/test_full_figure.py`) failed on its own first run, and each
failure was a real defect rather than a test to relax:

1. **`A-face` typed eleven coordinates, the fringe fourteen, each fall nine.** Invariant 5 says no
   shape carries a hand-typed station table. The face ring is now eight landmarks; each fall is eight;
   and the fringe became a **generator**: four landmarks (where it starts, where it peaks, where it
   ends, how low it hangs) plus `teeth` and a depth pair, so its points are computed
   (`figure.py:fringe`). The first two generator attempts were wrong and are recorded here rather than
   dropped: sampling only at tooth tips gave a flat lower edge, and a 66 px tooth depth put a spike
   between the eyes. The fringe now hangs to the brow line (230–252) with four shallow teeth.
2. **The copied `A-cloth-v8` test suite is gone from this package.** Nine of its files assert things
   about the *crop-frame* assembly and open `artwork-a.png`, which exists in `A-cloth-v8` and not
   here: three errors and three failures that said nothing about this figure. They stay tested where
   they belong. What remains here is the figure's own suite.
3. **The palette test was wrong, not the code**: it looked for every fill among `figure.py`'s own
   constants, and the inherited parts declare their colours in their own modules. It now gathers the
   palette from the part modules too.
4. **The no-image test was too blunt**: it forbade the string `image.jpg` anywhere under `source/`,
   which the inherited `build_a.py` docstring legitimately contains ("never reads image.jpg"). It now
   forbids an image *library* everywhere and the reference's *name* only in this package's own
   builders.

5. **Three of the figure's own tests still read `OBJECTS` the old way** (`for part, why in
   values():`) after the dict became name -> ([parts], statement); they errored on an unhashable list.
   Fixed, and the suite is green: **9 tests, OK**.

Landed render: `ff19`; `check/draft-fullres.png` and `check/head-2x.png` are its images.

**Where this leaves the figure.** Craft: the fringe's zigzag is still too regular, the lower mass is
still panels rather than folds, the collar is small, the hair has no light/shade split, the hand is a
mitten. Identity: the figure is whole, all of its parts are hers, and the picture is recognisably the
reference's girl seated in the same frame — but T6 does not clear yet, and no verdict is claimed.

## Round 15 — T4's gap, and the hole the shadow hunt found

T4's missing relation was "the brim casts no shadow on the hair". The reference answers it narrowly
and I sampled it before drawing anything: along the junction — (600,215), (720,205), (800,250),
(840,280), (860,310) — the hair is the *same* lit blue everywhere, and the only dark value is a very
dark line (0,50,91) exactly at the junction. So the brim's shadow here is a **contact line on the
hair**, not a band across it.

- A broad band was tried first and deleted: the brim's near edge is at eye height on the falls, where
  the hair is in front of the brim and cannot be shaded by it, so the band drew two dark crescents
  across the falls. The band that lands is the fringe's own hairline, 2 → 7 px deep (`band()` on
  `fringe_arc()`), colour `#16406a`.
- The same pass found a **hole**: the collar's opening is wider than the neck, and the inherited
  collar was cut for a chin 58 px lower, so background showed through both sides of the neck —
  sampled `#56adb8` at (640,395) and (720,415). `A-neck-hollow` fills the opening behind the neck.

## Round 16 — the hair's lit/shade split, and the collar rebuilt

- Each fall is now two tones: the curtain lit, and a **shaded turn** inset along its inner edge by a
  fraction of the way to its outer edge, so the mass reads as turning away instead of as a flat fill.
- The sailor collar was rebuilt for this frame's neck (`A-collar-left`/`-right`, light blue, in front
  of the bodice, behind the bow) and the inherited pair dropped for the same measured reason as the
  head boundary: at this frame they sit inside the bodice and read as a sliver.

## Round 17 — the lower mass re-cut

The first lower mass was five axis-aligned panels with five parallel strokes on top and read as a
cushion. Re-read from `ref-lower.png`: a large deep-teal field across the centre-bottom, pale mint and
cream cloth over its upper right, the pink and orange lining ribbons crossing the teal diagonally.
Re-cut to exactly that, with the fold lines regenerated as three long curves that leave the waist at
intervals and run down-right along the drape (the first version radiated them from one point and read
as a fan).

## Round 18 — the hand, the eyes, the fringe

- **Hand**: a palm, a thumb and three creases at the wrist's end, with the arm's own width profile
  tapering to a wrist (`32 - 12 t^1.6`). The thumb was first a `SKIN_SHADE` blob floating on the palm
  — same tone as the palm now, with a crease where it turns off.
- **Eyes**: a dark disc behind a pink disc reads as a goggle, which is what the 1:1 view said. An eye
  is now a sclera, an iris that does not fill it, a pupil, a catchlight, a heavy lash arc above and a
  thin lid below. Iris lowered in the lid so the dark reads as an upper lash rather than a ring.
- **Fringe**: the teeth were a saw (four sharp V points), then a single deep tooth between the eyes,
  then a crown of three points over the forehead. It is now soft scallops of unequal depth — a raised
  cosine per tooth, the amplitude taken from a fixed irrational pattern — ending **above** the eyes
  (226 → 241), with the brows under it showing only where the scallops leave room.

## Round 19 — a route tried and rejected, recorded with its pixels

The figure's torso is narrower than the reference's shoulder mass. Scaling the whole inherited torso
group by 1.10 about the body's axis was tried and **rejected**: the chest bow is a sheet whose own grid
carries the knot's place, so the scale pushed it up over the collar and the chin and the collar
vanished under it. `TORSO_SCALE` is back at 1.0 with that reason written beside it. Widening the torso
has to be done by re-cutting the bodice, not by one factor over a group.

## Round 20 — the streamer (the landing render)

The reference's signature is a thin lock that flies out to her left and hooks at the end. Added as
`A-hair-streamer`, a tapered strip on a route that leaves her hair at the temple and hooks down at
(296,578), at the hair's own depth order. It is the gesture the reference's silhouette is built on and
the figure did not have it.

**T6 after this advance — the list, not softened:**

1. **The head is frontal where the reference's is turned three-quarters to her left**, and that is the
   largest single difference left. It is a re-cut of the face group (the far eye narrower, the features
   moved off the centre line, the hat's tilt changed), not a tuning pass, and it is the next round's
   whole job.
2. **The lower mass is still a dome with wedges on it.** The tones and the fold lines are right; the
   silhouette is one round shape where the reference's is cloth that has been sat on — angular, with
   the knees' two peaks.
3. **The torso is narrow** (round 19's rejected route): the bodice is a cream column where the
   reference's is a blouse with a waist and a peplum.
4. Craft: the falls' inner edges are still straight lines; the hand is a mitten at 4×; the mouth is a
   flat oval.

Items 1–3 are identity; none of them is a tuning pass.
