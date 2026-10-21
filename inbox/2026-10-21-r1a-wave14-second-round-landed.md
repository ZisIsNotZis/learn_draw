kind: report — completion of the landing pass, one decision requested
from: learn_draw (owner of this directory)
spend: machine_time idle; ~35 min wall clock of the owner's own run, no device, no money
id: r1a-wave14-r2-landed-3825d51-4eafe0e

# What is now true

**Milestone:** R1a, object studies — wave 14's second round is **landed and rebuilt**, not
green-as-a-milestone. `A-bow-study-v2` (the bow alone) is mechanically complete at 17/17;
`B-hand-study-v1-r1` (the hand and dish) is at 22/23 with one measured defect. **No image verdict
exists on either revision**, so R1a has not passed anything; what changed is that both packages
are now truthful about what they emit.

**The command that shows it** (from `/home/z/vibe/learn_draw`, each prints its own pass/fail line):

    cd .scratch/35-r1-articulated-study/evidence/A-bow-study-v2 && \
      PYTHONDONTWRITEBYTECODE=1 ../../../../.venv/bin/python -m unittest discover -s tests -t .
    # -> Ran 17 tests ... OK ; then ../../../../.venv/bin/python source/manifest.py --check -> 17/17

    cd .scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1 && \
      PYTHONDONTWRITEBYTECODE=1 ../../../../.venv/bin/python -m unittest discover -s tests -t .
    # -> Ran 23 tests ... FAILED (failures=1), the one being TestContact's underside assertion

Commits: `3825d51` (A), `4eafe0e` (B), `199db3c` (STATUS + wave log). Nothing pushed.

**What the last two writers did, and what the kill left.** Both were killed by the runtime at
30 minutes, each with its source edit on disk and **no artefact rebuilt** — so both packages read
red for a reason that was not their code: A failed only its two manifest tests, B failed six
(2 manifest, 2 reproducibility, 1 occlusion, 1 real contact failure). The owner's landing pass
rebuilt each package over its own revision: build → render → `draw check` bundle inside the
package → manifest → README numbers. Two writers did share this one checkout for that round,
against the one-writer-per-tree rule; the edits were in disjoint directories, no file was lost,
and I reconciled them by rebuilding each package from its own sources and checking that each
suite's remaining failures were artefacts rather than construction.

**The two source corrections that were rescued:**

- A: `_knot_at` read the last route part's end off `parts[k+1]` and returned `1.0`, collapsing the
  lower tail's three width knots onto the strip's end. Fixed. Emitted now: width 63.8…300.0 px
  (ratio 4.70), 620 stations, worst isolation 2.69 px, knot waist 0.45, 19 audited crossings
  (mutation 19/19), 0 of 1240 windings wrong. The fix **exposed a depth conflict** it had hidden —
  at the declared width the tail's rails cross the knot 182 px wide and sat within 0.3 px of the
  wrap's depth — so the tail's swing moved to the crushed waist and its level to −6.25 thicknesses.
- B: the pad's approach knot is offset by the **tip** radius so the pad's axis is the chord
  parallel to the underside, and the radius law reaches `r_tip` by 0.88 of the span. The middle and
  ring pads went from 10.6 px to inside the 5.5 px bound; the **index pad from 10.6 to 7.05 px and
  is still 2.05 px over**. The lift mutation still fails as it must (26.50 px caught).

# What is still open, and what it costs

- `A-bow-study-v2`: the six defect tests the R1a contract demands are **unwritten** (package H).
  It is otherwise mechanically complete and its bundle is ready for an image-only reviewer.
- `B-hand-study-v1-r1`: the index digit's arrival angle (a third stage of package G), the well's
  spoke fan (reviewer blocker B2), items N1–N5, and the four tests package E demanded.

# The decision I need

**One: may the image review of the bow be dispatched now, and in what order with the two remaining
stages?** Package C (`A-bow-study-v2` image review) was held waiting on F precisely because a
verdict on a revision about to move expires; F is now landed at `3825d51`, so C is unblocked and
it is the only thing that can turn 17/17 into a milestone verdict. Against that, package H writes
the six bow defect tests and package G3 closes the index pad. My recommendation: **C and G3 in
parallel now** (disjoint packages, one is a fresh-context reviewer, the other a writer), and **H
only after C returns**, because a defect test written before the verdict encodes the producer's
guess at the defect — which is the reason wave 14 already cut H that way. If you would rather hold
all of it until you have looked at the two images yourself, say so and nothing is dispatched:
open `check/draft-fullres.png` in each package and no reviewer is needed to overrule me.

# Effort, so you can price the answer

Dispatching C is one fresh-context reviewer, idle compute, ~20 minutes, no device. G3 is one
writer, idle compute, ~20 minutes. Reversal of my recommendation costs one reviewer run, not a
rebuild: nothing in either package moves while a verdict is being formed.
