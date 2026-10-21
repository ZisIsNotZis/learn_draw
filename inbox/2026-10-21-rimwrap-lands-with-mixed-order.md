kind:    report — completion of the experiment root authorised; decision none for the person, one for whoever holds the next hand package
from:    learn_draw (owner of the go package)
spend:   machine_time, idle class, no device held exclusively; ~25 min of my own run, no money, no
         person-attention; one fresh image-only reviewer dispatched (~12 min, idle)
id:      root contract `inbox/2026-10-21-rimwrap-contract.md` (read, landed, deleted) -> the rim-wrap experiment

## The result, in the order it changes your roadmap

- **The experiment ran and its own continuation criterion is met.** `B-hand-study-v2-rimwrap`: the ring
  finger passes **above** the dish's rim band and its pad lands on the **pressed surface past the rim's
  inner corner**, so its fill lies inside the dish's projected outline while the palm and the other four
  digits stay behind the plate. That is the mixed order H1 asks for: one piece in front, the rest behind.
- **The numbers, on the delivered 1:1 PNG:** `cross_px` **3527** against a floor of **2175** — 1.62 % of
  the dish's 217 540 px projected outline, counted against the dish's outline **from its own geometry**,
  not its visible outline — and `contour_breaks` **0** of 6 rear-contour points inside the crossing. Both
  are line 1 of `check/report.txt`, beside the 1:1 image. Suite **28/28** green; rebuild byte-identical;
  manifest verifies; the delivered PNG is a fresh render of the delivered SVG.
- **The audit's own control bites:** the same digit put back on v1-r1's underside route (same station,
  same radii — only the contact surface changed) drops below the floor, so green means "the crossing",
  not "some pixels". `tests/test_joint_audit.py::test_the_audit_zeroes_on_the_r1_route`.
- **Failure route (b) was the live alternative and it is not what happened:** the pixels agree with the
  declared front/rear order — the digit's contour runs unbroken where it crosses and the dish's rim
  contour terminates on it. H0's remaining sliver (the renderer dropping a declared crossing) is now
  dead at this scale, so the class is the drawing's, not the renderer's.
- **The change is small and named:** the dish derives its **bowl** rings the same way it derives the
  underside; `contact.pressed_ring` is a blend of those rings across the rim band and onto the interior;
  `contact.wrap_finger` is the front piece; `scene.WRAP` holds one digit's pose. Palette, framing,
  tessellation, stroke weight, the palm and the other four digits are unchanged, and v1-r1 is untouched.
- **Your diagnosis goes up unchanged, and now with a cure beside it:** every blocking finding in four
  verdicts was a relation between two masses in the picture's plane; every green measurement was one mass
  against a surface in space. The cure is not a rule to remember — it is a measured number on the picture,
  with a control that turns it off.

## What I did not do

No bow v4, no second subject, no gate moved, no fifth attempt of the underside-only route, nothing pushed.
The four remaining v1-r1 findings (bowl tessellation, digit silhouette staircase, doubled rim contour,
ambiguous tip quads) are untouched by scope and still open. **No art verdict is claimed:** whether flesh
over the rim *reads as holding the dish* is the reviewer's question, and R1a's exit stays the person's
judgement of a picture.

## Evidence pointers

- [`.scratch/35-r1-articulated-study/evidence/B-hand-study-v2-rimwrap/README.md`](.scratch/35-r1-articulated-study/evidence/B-hand-study-v2-rimwrap/README.md)
  — the result, the table of what changed, the reproduce block; `check/draft-fullres.png` is the 1:1 image
  and `check/report.txt` line 1 carries the two numbers.
- `git log --oneline -2` → `c4d8d95` (the contract landed and deleted, STATUS one current fact), `37a50a7`
  (the package, 23 files).
- Reproducible: `python source/build.py`, `scripts/draw check artwork.svg --outdir $PWD/check`,
  `python source/joint_audit.py $PWD/check/draft-fullres.png artwork.svg --report`,
  `python -m unittest discover -s tests -q`.

## The review came back before the report closed, and it decides the next step

Fresh image-only review, archived verbatim at
[`reviews-r1a/B-hand-study-v2-rimwrap-image-review-1.md`](.scratch/35-r1-articulated-study/evidence/reviews-r1a/B-hand-study-v2-rimwrap-image-review-1.md):
the crossing **is** in the picture (the reviewer sees flesh inside the near rim), and it "neither wraps
the rim nor presses it" — it reads "as a pasted-on tab rather than a finger hooking the rim", so the
picture holds only weakly. That is **failure route (a)** of the package: floor met, picture still
failing. H1 is not refuted at the joint route; the next hypothesis is the crossing's **shape and
placement** (overshoot past the inner corner, a press that shows compression/contact at the junction),
and no third variant is attempted before that is written down with its cost.

## Your decision

None for the person. For whoever opens the next hand package: the joint criterion is now measurable, so
the next package is judged on the crossing's **shape and placement** (failure route (a)'s next hypothesis)
and should carry the two numbers it inherits. A fresh image-only review of this package's picture was
dispatched at the terminator; if its verdict is not in this file's evidence, it is the first thing to read
before the next package is cut.
