kind:    report — cost, one question: where the next writer package goes
from:    learn_draw (owner of the go package)
spend:   machine_time, idle class, no device; this round spent ~20 min of my own run plus one writer
         (12 min) and one fresh image reviewer (10 min), both idle CPU; no money, no person-attention
id:      root contract `inbox/2026-10-21-bow-repair-contract.md` (read, landed, deleted) -> wave 15 round three

## The result, in the order it changes your roadmap

- **The bow's third attempt is built, committed and re-reviewed, and it FAILED.** `A-bow-study-v3` at
  `553b52f`, image `check/draft-fullres.png` sha256 `fc30a067…`. The verdict is one file,
  [`evidence/reviews-r1a/A-bow-study-v3-image-review-1.md`](.scratch/35-r1-articulated-study/evidence/reviews-r1a/A-bow-study-v3-image-review-1.md),
  written by a fresh image-only reviewer that pinned its own binding line and the rebuild command
  (`.venv/bin/python scripts/draw.py check …/A-bow-study-v3/artwork.svg` from the checkout root) before it judged.
- **What J's six blockers cost and what they do not.** Cured at the mechanical level and confirmed by the
  reviewer: no triangle fan and no per-face striping (one polygon per band), contour 5.0 px against crease
  2.4 px, no dashed hairlines, 18/18 crease ends resolving under a later band, no dark-filled shape at all,
  palette unchanged at (206,78,126) matching the reference, both tails leaving the frame, no enclosed
  islands, 15/15 tests, byte-identical rebuild, 15/15 manifest, and the README names its own review image
  and the command that rebuilds it — the drift defect you asked me to stop reproducing is not reproduced.
  **Not cured:** nothing in the picture threads. The knot is overlapping rounded capsules with one straight
  vertical seam, so no ribbon edge visibly passes over another; a complete horizontal capsule is drawn on
  top of the left lobe and the down-tail (stacked, not articulated); both lobe contours close all the way
  round with no mouth opening from the knot; a ~12 px dark scar where the lobe contour and the capsule
  edge smear together; floating stubs; the left tail a 20–26 px parallel plank.
- **The hand got worse than "not shown yet": both its verdicts are FAIL.** K (image, `4dbcad2e…`): five
  parallel tapered blades that never cross the rim, so it reads as a plate resting on a hand — `resting
  under`, not holding; nonblocking background sliver at x 533-545, y 470-482. L (execution): the committed
  `tests/negative-control-output.txt` states the previous revision's numbers (74 occlusions / 6 contacts
  where the delivered artwork gives 91 / 7) and its producer overwrites rather than maintains it; the
  README's dish-perturbation proof passes on a degenerate surface; the README's `PALM["reach"]` claim is not
  what the geometry does and no test measures the palm. Its mechanical green is untouched — 23/23, pads
  1.60–4.26 px, occlusion break 91/91, manifest 19/19 — and that green is not an art pass.
- **Your two changes are landed where they belong.** No rejected picture goes in front of the person; the
  drift class ("the evidence and the thing it judges can drift apart") is written into STATUS and the
  acceptance ledger as a class, with both instances and the two structural cures (a README names its own
  review image; a reviewer resolves and prints its own binding line before judging). Your contract is
  deleted from `inbox/`; its facts are in `STATUS.md`, `work/wave15-contracts.md` § third round, and the
  ledger.

## The decision I need

**One, and it is a routing decision under a budget, not a taste question: the bow's fourth attempt or the
hand's repair first.** I put both in front of you because they now compete for the same writer slot.

My recommendation, offered as inference from three failed bow reviews and two failed hand verdicts: **the
hand first.** The bow's remaining failure is one sentence of construction — a wrap that threads through
itself rather than abutting, and junctions that occlude rather than stack — and a fourth pass costs a
writer package plus a review (~25 min idle) with no guarantee, since three attempts have each cured the
class named and found the next one; there is nothing left in the bow that is cheap. The hand's three
execution blockers are *documentation and evidence defects on a green, measured construction*, the
cheapest kind of thing this project knows how to fix (a regenerated negative-control record, a real dish
perturbation, a palm test), and its image blocker — digits that never cross the rim — is a pose/route
change on a construction that already measures 1.60–4.26 px. Both are one package each; the hand's buys
more certainty per minute.

If you would rather keep the bow moving because it is the older failure, say so and the fourth attempt is
one contract cut from the reviewer's six findings, with the wrap's route — not its tuning — as the only
variable.

Effort of either: one writer package, idle compute, ~20–25 minutes, no device, no money, plus a review
(~10 min) that binds itself. Declining both costs nothing this second and leaves the person's judgement at
R1a where it already is: nothing to look at.

## Evidence pointers, so nothing above has to be taken on my word

- `git log --oneline -4` → `3998a17`, `553b52f` (package N), `0995133` (K and L landed, ledger and class),
  `d148b78` (your contract).
- Bow: `.scratch/35-r1-articulated-study/evidence/A-bow-study-v3/` — `README.md` names the image and the
  rebuild command; `check/report.txt` line 1 is the 1:1 image.
- Every verdict: `.scratch/35-r1-articulated-study/evidence/reviews-r1a/` (J, K, L, and v3's review).
- Nothing pushed; the main area is on `master`, tree clean at `3998a17`, no branch created.
