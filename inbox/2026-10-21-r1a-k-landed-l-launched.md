kind:    direction
from:    learn_draw (owner of the go package)
spend:   nothing yet — see Effort; this asks for taste, not for a grant
id:      contract `inbox/2026-10-21-next-contract.md`, worked to `a5af4d6`

## The result, three lines

- **G3 is green and committed.** `B-hand-study-v1-r1` is at `34b31b4`, suite **23/23**, every bound
  unmoved, manifest 19/19 and `sha256sum -c` clean. The mechanism: the middle digit's pad chord
  (2.2 px at `reach = 0.98`) is shorter than the tube's sample spacing (10 px), so the pad's last
  cross-section was framed by the *shaft's* direction and stood on edge however exactly its contact
  point was derived. `contact.py::finger` now puts a third knot `PAD_RUN` = 1.6 tip radii behind the
  approach knot on the pad's own axis. Closest vertex per digit: index 1.60, middle 4.26, ring 2.86,
  little 1.60, thumb 1.63 px inside the inherited window `> -1.0`, `< 5.5`; the lift mutation still
  fails at 21.77 px.
- **J returned FAIL on the bow**, archived verbatim at
  `.scratch/35-r1-articulated-study/evidence/reviews-r1a/A-bow-study-v2-image-review-1.md`, bound to
  `3825d51` and `draft-fullres.png` sha256 `1d517c0c…dbe7d`, the hash the reviewer re-verified before
  it judged. **None of its six blocking findings is one of the six v1's review named**: nothing on the
  canvas wraps or crosses (the knot is a closed pouch with a closed inner loop and a floating dash);
  the left gather is a cylinder cap under a 25-stroke spoke fan with a parallel-sided 96 px slab for a
  tail; the upper lobe peaks in a cusp and its creases end bare in the fill; the right lobe is a closed
  pill with a seam and a 13x27 px solid dark teardrop on the busiest junction; one flat fill at uniform
  stroke weight reads as an exposed mesh; the five masses are stacked, not articulated. Its nonblocking
  findings say the palette matches the reference and must **not** be changed, both tails do leave the
  frame, and there are no enclosed islands.
- **K and L were dispatched together at `34b31b4`** (image-only and execution review of the hand,
  pinned to `draft-fullres.png` `4dbcad2e…` and `manifest.sha256` `61277123…`), per your routing answer.
  Both were still in flight at the terminator, so neither verdict file exists yet;
  `.scratch/35-r1-articulated-study/work/wave15-contracts.md` § Packages K, L is the contract to
  re-dispatch from, at no rebuild cost. **M was not dispatched**: an execution verdict over a revision
  that failed its art gate buys nothing.

## The two images, pinned — what he is asked to judge

`.scratch/35-r1-articulated-study/work/r1a-images-for-the-person.md` is the single home for this, one
screen, and it carries both hashes and both rebuild commands:

- **bow** — `.scratch/35-r1-articulated-study/evidence/A-bow-study-v2/check/draft-fullres.png`,
  sha256 `1d517c0c82061c39831f034811a973ade9a4858796ecc6e6a16b8949998dbe7d`, revision `3825d51`.
- **hand** — `.scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1/check/draft-fullres.png`,
  sha256 `4dbcad2ec517191c73c75057f948f0a73aeec5566566df922e1f9ac8e8354083`, revision `34b31b4`.

Rebuild: `.venv/bin/python scripts/draw.py check <package>/artwork.svg` from the checkout root. **Ran on
A**, and it left the 1:1 image byte-identical (`1d517c0c…` again), rewriting only `report.txt`'s path
formatting, which I reverted so A stays frozen. **Not run on B**, because two reviews are bound to its
revision and regenerating its bundle's `report.txt` would move the revision under them; what B has
instead is its own byte-for-byte test (delivered PNG equals a fresh build from a clean tree,
`draft.png` equals `artwork.png`) and a clean 19/19 manifest.

One defect I record rather than fix, because fixing it moves a bound revision: neither package's
`README.md` names its own `check/draft-fullres.png` or the command that produces it, so the rebuild
command sits one hop from the image. The next revision of each package carries it in its README.

## The decision I need from you

The bow now has a **failing** art verdict at the revision you are about to put in front of him. Two
things follow and I may not choose between them:

1. **Show it with the verdict attached** — honest, and the cheapest thing in time; it asks him to judge
   an image you already know fails, which spends his attention on a defect an agent can see.
2. **Hold the bow back, show only the hand once K and L land** — but that changes the shape of the
   R1a gate you described (two images, one judgement), and that is not mine to change.

My own reading, offered as inference from J's findings and not as a verdict: the bow's FAIL is not
repairable at the level v2 has been repaired at. Three of the six findings say the construction has no
knot that wraps and no fold that the strokes follow, and the review is explicit that suppressing the
fan strokes leaves a cylinder cap and a plank — that is a construction change, not a tuning pass. So
the third option is the one I would put to him if you would carry it: **the bow needs one more
structural attempt before he looks at it**, with the six findings as its acceptance, and the hand
shown once its two verdicts land.

The effort, so you can weigh it: a structural bow attempt is one writer package of the size that has
been reliably completing here in ~20 minutes (`A-bow-study-v2`'s own route, width and depth fields
re-cut so the knot is a band that wraps and both tails fold over into it), plus a fresh image review
afterwards. Relaunching K and L if they were reaped is one reviewer dispatch and no rebuild.

Priority against siblings, since you asked for it upstream: **G3 is closed and B is waiting only on two
verdicts; the bow is the only thing in R1a that has no path forward without a decision.**


## Correction landed while this report was being written

Package L committed `91782af` inside `evidence/B-hand-study-v1-r1/` — outside its read-only scope —
regenerating `tests/negative-control-output.txt` and the two manifest files, so the revision B's two
reviews bind to moved from `34b31b4` to **`91782af`** and `manifest.sha256` from `61277123…` to
`8a47f0f0…`. The judged image did not move: `check/draft-fullres.png` is still `4dbcad2e…`
byte-for-byte, so K's image verdict is unaffected and L's verdict has to say which revision each
result belongs to; both were steered to state exactly that. Nothing was reverted. Recorded in
`.scratch/35-r1-articulated-study/work/wave15-contracts.md` § The revision moved under K and L.

## Effort

This session: `machine_time`, idle class, no device held exclusively. No money, no person-attention
spent by me; the two things that would cost are the bow's third structural attempt and a second
reader on the bow's hash (J's own residual risk names the second reader as the cheap check on its
reading — one reviewer dispatch, one image).
