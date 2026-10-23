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
