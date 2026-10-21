# A-bow-study-v2 — image-only art + cohesion review, round 1 (package J)

Binding: commit `3825d51`, `evidence/A-bow-study-v2/check/draft-fullres.png` sha256 `1d517c0c82061c39831f034811a973ade9a4858796ecc6e6a16b8949998dbe7d` (re-verified this session with `sha256sum`, matched).

`manifest.sha256` hash: unknown to this review — the dispatch carried only the commit and the image hash, and `manifest*` is outside my input set. This verdict binds to the commit and the 1:1 image and does not extend to the bundle or its manifest until the owner records that hash alongside this one.

## Verdict

**FAIL** — the violated criterion is "the reference's bow must READ AS A RIBBON TIED INTO A BOW", specifically its first clause, *a knot where the ribbon wraps and crosses itself*: no ribbon edge in the picture passes over another ribbon edge. The reading it lands on is **a crumpled paper bag on two planks**, carried by an exposed triangular mesh (a spoke fan, per-face striping, floating stroke stubs) and by a solid dark teardrop on the silhouette. Reproduction is in §Reproduction below.

## What I read

Inputs, and only these: `check/draft-fullres.png` (800x560, 1:1), `check/draft.png`, `evidence/A-cloth-v8/ref/crop-400x480.png` (bow bbox (33,134)-(271,285)) for palette and lobe solidity. I did not open `source/`, `tests/`, `README.md`, `manifest*`, any wave log, any ledger, any producer report, or the archived v1 review; I ran no git command and changed nothing outside this file. Detail was judged on 2x–5x nearest-neighbour crops of the 1:1 image, cut in `/tmp` and not kept.

Coordinates below are **fullres pixels on the 800x560 canvas**, origin top-left. Measurements marked *(measured)* came from the commands in §Reproduce; readings marked *(inference)* are mine from looking, with the pixels that produced them named.

## Blocking findings

**B1 — there is no knot: nothing wraps and nothing crosses.**
Location: the centre mass, roughly (450,200)–(640,350); the enclosed loop at (505,215)–(560,280); the floating dash at (517,274)–(523,277).
Criterion violated: "a knot where the ribbon wraps and crosses itself".
What I see: the centre of the bow is a closed rounded pouch. Inside it sits a *closed* oval loop with a hook on its lower left, and a 7x4 px dark dash floating in the fill inside that loop with no attachment. Nowhere on the canvas does one stroke pass over another: strokes meet at T-junctions or terminate in open fill *(measured: 7 stroke components ≥20 px; the mass and its creases form one 11743 px component, the right lobe's outline a separate 2834 px component — no stroke-over-stroke crossing exists anywhere to be counted)*. If the inner loop was intended as the ribbon passing through the knot it does not work, because the loop is closed — no band enters at one side and leaves at the other — so it reads as a bag handle. *(inference)* The pouch is also the largest rounded form on the canvas, the two lobes are the smaller appendages; in the reference the knot is a small band crossing (≈55x47 px) inside a 238x151 bow, with the lobes dominating.
What a reader sees: a knot drawn as a donut, on a bag.

**B2 — the left junction is a cylinder cap with a spoke fan, and the left tail is a parallel-sided slab.**
Location: the "gather" at (270,150)–(350,360), strokes converging at ≈(330,245); the left tail from x=0 to x≈270.
Criterion violated: "creases that follow real folds" (and the failure reading "crumpled paper bag" / exposed mesh).
What I see: a near-circular dome arc closes the left tail, and from a single point at ≈(330,245) about two dozen straight thin strokes radiate to that arc, evenly spaced, like a pinwheel or a bicycle wheel. *(measured: a circle of radius 60 px centred (330,245) crosses 25 strokes; at radius 80 px, 20)*. No fold in cloth behaves this way; this is a triangle fan whose pole is visible. The tail it caps is two straight, exactly parallel edges — top edge at y=259 for x 150–269, bottom edge at y=365 — constant height ≈96 px, ending dead where the dome begins. Nothing gathers, nothing twists, nothing folds over into a knot.
What a reader sees: the cut end of a sausage with a sunburst on it, attached to a plank.

**B3 — the upper lobe's free edge is a cusp, and its creases end bare in the fill.**
Location: peak at (410,58); concave notch at (392,140); creases terminating at (448,197), (460,275) and the diagonal stub (473,278)–(503,275).
Criterion violated: "two lobes with curved free edges opening away from the knot".
What I see: the upper shape rises to a sharp point at (410,58) where two near-straight edges meet, and its left free edge carries a concave kink at (392,140) — paper creased, not ribbon curving. Its interior is three long near-parallel strokes that stop at full weight in the middle of the fill with nothing there: one ends at (448,197), another at (460,275), a third veers off as a bare diagonal at (473,278)–(503,275). A fold line ends where the surface flattens; these end where a patch boundary happens to be.
What a reader sees: a paper-bag flap or a fin.

**B4 — the right lobe is a closed pill with a seam, and the notch beside it holds a dark teardrop.**
Location: right lobe (552,71)–(744,327); its near-vertical seam stroke at x≈615–625, y 75–330; the solid dark teardrop at (626,298)–(639,324); floating stubs at (557,161)–(572,170) and (608,310)–(619,314); the J-hook stub at (621,284)–(629,300).
Criterion violated: "two lobes with curved free edges opening away from the knot" — its failure readings "two closed pills" and "two lobes joined by a chord".
What I see: a fully closed rounded shape whose only structural line is one stroke running down its left side like a seam; it touches the mass at a cusp, not at a fold, so its mouth — the place a lobe would fold out of the knot — is not drawn at all. Where lobe, mass and vertical tail meet, the silhouette bottoms out in a **solid dark teardrop 13x27 px** that reads as a drip of ink or a mole, with two detached 12 px strokes floating in the fill beside it and a stem-and-arm "Y" above. That teardrop is the single most read-breaking mark on the canvas: it is the only solid dark blob in the picture and it sits on the busiest junction.
What a reader sees: a balloon with a seam, glued against the mass, with something dripping off it.

**B5 — it reads as an exposed mesh, not a drawing.**
Location: the whole canvas; most legible as vertical striping on the right lobe at (560,70)–(640,170) and across the centre mass; the dotted hairline at (327,292)–(336,357); the three detached stubs listed in B1 and B4.
Criterion violated: "does it read as a drawing rather than an exposed mesh" — and it is what produces the ACCEPT line's "flat sticker" reading.
What I see: one flat magenta fill with all structure carried by strokes of *identical* weight. *(measured: the fill resolves to 1044 distinct colours of which 93.9 % fall in 9 shades within ±1 per channel, and scanning column-by-column gives 120 colour-class transitions against 22 row-by-row — the jitter is laid down in vertical strips, i.e. per face or per column, and reads as ribbing)*. *(measured: dark-run widths on scanlines y=120, 200, 300 are 3, 4, 4, 4 px — the silhouette has the same weight as an interior crease, so there is no contour-versus-fold hierarchy, which is why the object sits flat on the page)*. *(measured: a sub-pixel hairline renders as a dotted line)*.

**B6 — it is one connected region but not one connected object.**
Location: the four junctions — left tail at (269,258) and (335,365); vertical tail at (395,395) and (575,345); upper lobe at (455,95); right lobe at (620,290).
Criterion violated: "does it read as one connected object".
What I see: at every junction one part's silhouette is simply cut by another's outline — no fold, no gather, no occlusion break, no stepped edge, no crease running across the join. *(measured: the silhouette is a single connected region, 180406 px, bbox x[0,744] y[52,559], and there are no enclosed background holes — 2 background components, both touching the canvas edge — so nothing is fractured or floating as a region)*. The failure is therefore not fracture but articulation: five pieces — left plank, bottom plank, upper fin, centre pouch, right ball — are stacked and each is outlined as if it were complete on its own.

## Nonblocking findings (carry forward; do not treat as permission to change them)

**N1 — palette is right.** Reference ribbon fill (206–211, 77–79, 125–127); draft fill (206,78,126) with the derived shades above. Hue and value match the reference to within a few units. Every defect in B1–B6 is structure and stroke discipline, not colour. Do not "fix" the flat cel fill: the reference is a flat cel fill.

**N2 — both tails do leave the frame, so that clause is met.** Left tail crosses x=0 between y=259 and y=365; bottom tail crosses y=559 between x≈360 and x≈575. The clause "two tails leaving the frame" is satisfied on presence. Their constant width and parallel edges are finding B2/B6, not a separate absence.

**N3 — no islands and no holes.** Stated in B6 as measurement; recorded here too so no repair is spent on cohesion-by-connectivity.

**N4 — the empty teal ground is not a defect.** The reference bow sits on a garment; this study shows the bow alone on flat ground, which is what the study is of. The ACCEPT line is about the bow. Do not add a ground, a garment or a shadow as a way of curing B5.

## Reproduction

The verdict is a reading, so reproduce it as one, at the source — `check/draft-fullres.png`, never a resized copy:

1. View the image at 1:1. The object reads as a pink lumpy mass with two planks. Then cut the four windows and view each at 4x–5x:
   `convert draft-fullres.png -crop 130x230+245+155 +repage -resize 400% /tmp/j1.png` → B2's spoke fan and the tail-capped-by-dome.
   `convert draft-fullres.png -crop 120x170+555+180 +repage -resize 500% /tmp/j2.png` → B4's teardrop, seam and floating stubs.
   `convert draft-fullres.png -crop 200x190+445+195 +repage -resize 400% /tmp/j3.png` → B1's closed inner loop, floating dash, absence of any crossing.
   `convert draft-fullres.png -crop 220x230+330+45 +repage -resize 350% /tmp/j4.png` → B3's cusp and creases ending bare.
2. The measurements quoted *(measured)* are recomputable on any machine from the PNG: background = within 12 of (119,200,192) by sum-abs; stroke = channel sum < 330; 8-connected labelling. Expected: 1 object component; 2 background components both edge-touching; 7 stroke components ≥20 px (11743, 2834, 1514, 825, 55, 36, 20); 25 stroke crossings on a radius-60 circle about (330,245) and 20 on radius 80; column-wise/row-wise dominant-fill-colour transitions 120/22; dark-run widths 3–4 px on y=120,200,300.
3. The reading to confirm: at 4x, nothing on the canvas passes over anything else (B1), the sunburst follows no fold (B2), and the teardrop is a solid blob that belongs to no fold (B4). If a viewer can find one ribbon edge crossing another and one fold ending where the surface flattens, B1 and B3 fall and the verdict changes; that is the way to attack this verdict.

## What a repair must not do

- Do not add shading, texture or a background to make B5 go away; the criterion is a knot that wraps, and no amount of tone makes the fan read as cloth.
- Do not scale, rotate or recolour the masses to fit the reference; the failure is at the junctions and at the knot, so a repair has to be built there.
- Do not suppress the fan strokes alone: with the strokes gone the dome at (270,150)–(350,360) is still a cylinder cap and the tail still a plank. The cure for B2 is that the tail has to fold over into the knot and be narrower than the knot's wrap, which is a construction change, not a rendering one.

## Residual risk

One image-only reviewer, one revision, no execution: I cannot tell whether the fan and the tearing are a mesh or a render of it, and I did not look at the geometry. If the underlying surface is right and only the stroke routing is wrong, B5 and B3 part are cheap and B1, B2, B6 are not. A second independent reader on the same hash is the cheap check on my reading; if their reading differs, the one that can name a pixel where a ribbon edge crosses another wins.
