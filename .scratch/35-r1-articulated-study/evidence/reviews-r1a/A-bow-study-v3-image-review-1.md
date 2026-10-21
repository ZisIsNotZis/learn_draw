# image review — A-bow-study-v3 (image-only, fresh eyes, r1a)

VERDICT: **FAIL** — violated criterion: *the knot where the ribbon wraps and crosses itself, one ribbon edge visibly passing over another* (and its partner: *two lobes with curved free edges opening away from the knot*). Location: knot at full-res x 495–600 / y 205–265, both lobe mouths at x≈500 (left) and x≈600 (right) / y≈230–270. Reproduction below.

Binding: `draft-fullres.png` sha256 `fc30a067d1aad031e6266dac33b2a1001b1b4c74d180cf2c15f65f621276a927`, repo HEAD `553b52f`, 800×560 RGB, decodes. Rebuild: `.venv/bin/python scripts/draw.py check .scratch/35-r1-articulated-study/evidence/A-bow-study-v3/artwork.svg` from `/home/z/vibe/learn_draw`.

## what holds
- Palette: bow fill (206,78,126) vs reference bow fill (204,80,126) and (212,79,129) *(measured: `Image.getpixel` / colour histogram of `ref/crop-400x480.png`)*.
- Weight order: outer contour 5–6 px, interior fold strokes 2–3 px *(measured: dark-run lengths on columns x=260/300/340/400 and rows y=200/240/300)*. Contour above fold weight — reads as a drawing, not a wireframe.
- Two tails leave the frame: fill reaches x=0 at y 294–314 and y=559 at x 548–608 *(measured: fill-mask scan)*.
- No striping, no spoke fan, no donut knot, no bowtie; the lobes are asymmetric (left ≈2× right), so the bowtie reading does not fire. Fill is flat, no gradient or banding *(inference from 3 dominant colours + antialias only)*.

## what fails
1. **No knot crossing.** The knot is a rounded trapezoid with one straight 3 px vertical seam at x 555–557 running contour-to-contour with no direction change; a second vertical at x 587–591 and the capsule edge at x 602–608 sit beside it *(measured: dark-run positions on row y=230)*. No ribbon edge underlaps another — nothing is threaded through anything *(inference: no over/under contour continues past a crossing anywhere in the knot)*.
2. **Stacked pieces, not articulation.** Below the knot sits a full horizontal capsule spanning x≈400–645, both ends closed with round caps *(measured: fill segments per row y=270/278/282/292)*. It is drawn complete and on top of the left lobe and the down-tail. Read as a strip laid across a pill — the failure reading "flat sticker / stacked pieces".
3. **Two closed pills, no mouths.** Each lobe's contour closes all the way around and runs into the knot; the interior arcs sit near-parallel to the outer contour (contour echoes) and stop free in the fill, so no crease terminates at a fold or an occlusion, and no lobe mouth opens away from the knot *(measured: interior dark runs 2–3 px offset 20–35 px inside the contour; free-ended, e.g. left lobe y 191/175/168 at x 260/300/340)*.
4. **Dark blob on a junction.** Ink half-thickness reaches 6.0 px (i.e. ~12 px wide, double the 5–6 px contour) in two masses, area 116 px at x 463–495 / y 327–332 and 96 px at x 398–430 / y 329–334 — the lobe's lower contour and the capsule's lower edge smear into one dark scar instead of meeting as a clean occlusion edge *(measured: `scipy.ndimage.distance_transform_edt` on the ink mask, threshold ≥4.0)*.
5. **Floating stroke stubs.** Straight dashes that end in flat fill with no fold reading: diagonal inside the knot x≈525–570 / y≈235–250, crescent at x≈470–500 / y≈315 inside the dark mass, short dash in the left lobe x≈300–340 / y≈355, short dash in the right lobe x≈690 / y≈250 *(measured: located in NEAREST crops; reading is inference)*.
6. **Plank tail.** The left tail is two near-parallel lines 20–26 px apart running straight from the lobe to the frame edge with no taper, twist or fold *(measured: fill height at x=0 is 20 px, at x=60 is 26 px)*.

## reproduction
From `/home/z/vibe/learn_draw/.scratch/35-r1-articulated-study/evidence/A-bow-study-v3`:
`python3 -c "from PIL import Image; im=Image.open('check/draft-fullres.png'); r=im.crop((490,200,600,275)); r.resize((r.width*5,r.height*5),Image.NEAREST).save('/tmp/knot.png')"` — the straight seam and both capped ends of the capsule are visible at 5×; and `crop((370,300,530,350))` at 5× — the 12 px dark scar and the free-ended crescent inside it.

## scope of this review
Image only. Nothing read outside the two named files; producer intent, tests and manifest not consulted. Numbers marked *(measured)* come from the commands above; readings of "what it looks like" are *(inference)*. Palette was not judged for correctness beyond the reference match, and is not mine to change.
