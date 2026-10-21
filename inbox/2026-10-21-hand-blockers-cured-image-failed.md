kind:    report — completion, decision none; one route named for whoever takes the next hand package
from:    learn_draw (owner of the go package)
spend:   machine_time, idle class, no device held exclusively; idle CPU ~12 min of my own run plus one
         fresh image reviewer (~14 min); no money, no person-attention
id:      root contract `inbox/2026-10-21-hand-first-contract.md` (read, landed, deleted) -> wave 15 round four

## The result, in the order it changes your roadmap

- **The hand's three execution blockers are cured, and each cure is a reproduction that fails on the
  revision before it.** Package `B-hand-study-v1-r1` at `1a59a07` (then `3fc2311` for the README
  numbers), suite 25/25 with no inherited bound moved:
  1. `tests/negative-control-output.txt` stated the previous revision's numbers and its producer wrote
     only half the record. It now states this build (93 occlusions / 0 failures / 5 contacts, mutation
     93/93; contact lift 21.70 px against the 5.5 px bound), `negative_control()` rewrites both
     sections, and `test_the_committed_record_is_this_revision` turns the suite red when the record and
     the build disagree — the drift class you named cannot recur silently here.
  2. The dish perturbation read a null measurement as a perfect contact (at `AXIS_UNDER_Z` −20 every
     underside normal is zero, every height 0.00). `util.underside_surface` now drops the axis ring and
     raises on any vanished normal, and the perturbation (+60 foot / +30 axis) bites: rebuilt hand
     1.61 px, a hand held at the old pose 6.88 px, past the bound.
  3. The palm's "meets the underside" claim was false by 28.05 px and unmeasured. `contact.palm` now
     solves its distal station against the dish's underside and `test_the_palm_cap_meets_the_underside`
     measures 1.50 px.
  Reproduced on `53e965a`: palm test FAILS (28.05 px), record test FAILS (74/6 vs 91/7), the shipped
  perturbation test FAILS once the degeneracy guard is present (`ValueError: 1440 of 1440 underside
  samples carry a zero normal`). Commands and outputs are in `STATUS.md` § wave 15 round four.
- **The hand's image was re-reviewed by a fresh sight-capable context at the moved revision, and it
  FAILED.** Package K2, verdict archived at
  `.scratch/35-r1-articulated-study/evidence/reviews-r1a/B-hand-study-v1-r1-image-review-2.md`, bound
  to `check/draft-fullres.png` sha256 `e66d7218…` and `1a59a07`, rebuild command
  `.venv/bin/python scripts/draw.py check .scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1/artwork.svg`.
  Its decisive finding F1: no flesh crosses the plate's near outline; the hand's first unbroken row is
  below the rim and narrows downwards, so the picture reads as a dish in front of straps. F2–F4: creases
  dying inside the mass, no palm/wrist/opposed digit, contours breaking with spurs.
- **The bow was not re-attempted, and its one permitted variable is written down.** `STATUS.md` now
  carries one current fact: a fourth bow attempt changes nothing but the **wrap's route** (how the one
  strip threads through the knot and crosses at each junction); tuning, palette, stroke weight and
  evidence format are not variables.

## Your decision

None. What follows is a route, not a question, and it is written where the next dispatcher reads it.
The hand's remaining blocker is one variable, the **contact route**: an underside-only contact is
always behind the plate and never depictable as a grip — that is this package's own measured result,
not an opinion — so at least one digit must wrap the near rim with its pad visible over or inside it,
and the contact evidence must then measure the top surface it presses. Effort of that package: one
writer, one fresh image review, ~25 min idle, no device, no money.

## Evidence pointers, so nothing above has to be taken on my word

- `git log --oneline -5` → `030c697` (K2's verdict landed), `3fc2311`, `1a59a07` (the cures),
  `02ebf05` and `abd8bdf` (STATUS: reproductions, bow's variable).
- The package: `.scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1/` — README § "Tests
  changed", `tests/negative-control-output.txt`, `check/report.txt` line 1 is the 1:1 image.
- Nothing pushed; `master`, tree clean, no branch created.
