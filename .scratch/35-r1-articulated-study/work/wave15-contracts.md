# Wave 15 — the two packages that can move R1a past wave 14

Cut by the owner of `learn_draw` on 2026-10-21, from the state wave 14's second round left:
`A-bow-study-v2` green at 17/17 (`3825d51`) with **no image verdict on any revision**, and
`B-hand-study-v1-r1` at 22/23 (`4eafe0e`) with one measured contact defect — the index pad hovers
**7.05 px** below the dish's underside against a **5.5 px** bound. Wave 14 is
[`wave14-contracts.md`](wave14-contracts.md).

## Why these two and nothing else

R1a's exit line is met when both object studies pass their gates. Both are mechanically near-complete
and **neither has an image disposition**: A has 17/17 and a bundle no reviewer has opened since the
geometry moved; B is one stage short of its own suite. A verdict on the bow cannot be made by its
producer (P22, invariant 7) and is the only step that can turn 17/17 into a milestone reading; the
index pad is the only remaining *measured* failure between B and its own reviewer. Packages H (the
bow's six defect tests) and I (B's absent tests, well shading, N1–N5) stay uncut: a defect test
written before a verdict encodes the producer's guess at the defect, which is why wave 14 cut H that
way.

**Allocation, one writer per area:** package C writes one file under
`evidence/reviews-r1a/` and runs no git command; package G3 writes only
`evidence/B-hand-study-v1-r1/` and commits it. No path is shared.

## Package C — `r1a-a-bow-v2-image-review-1` (review, fresh context)

- **Kind and name:** review, `r1a-a-bow-v2-image-review-1`, serving the `learn_draw` roadmap at
  R1a's art gate for the bow study. It holds no directory, document or roadmap, and dispatches
  nothing.
- **rev:** the working tree as it stands at `3825d51`; the images are
  `.scratch/35-r1-articulated-study/evidence/A-bow-study-v2/check/draft-fullres.png` (1:1, judge
  detail here) and `check/draft.png`.
- **accept (the criterion the drawing is judged against, and nothing else):** the bow of the
  reference must **read as a ribbon tied into a bow** — a knot where the ribbon wraps and crosses
  itself, two lobes with curved free edges opening away from the knot, two tails leaving the frame,
  creases that follow real folds. The failure readings are: two closed pills, a bowtie, a flat
  sticker, a crumpled paper bag, two lobes joined by a chord. The reference it imitates is
  `image.jpg`, bow bbox `(33,134)-(271,285)` of the registered crop
  `evidence/A-cloth-v8/ref/crop-400x480.png` (read-only; palette and lobe solidity may be compared
  against it).
- **change:** nothing. This packaged review repairs no file, edits no source and re-renders nothing.
- **ran:** nothing was run to produce the images on the reviewer's behalf; they exist and are listed
  in `check/report.txt`. The suite's mechanical result (17/17) is the owner's evidence and is **not**
  an art verdict — do not treat it as one.
- **judge:** read the two images and answer "what is wrong here?", then judge each finding against
  the `accept` line above. Report every finding as location + the criterion it violates + what you
  saw, so an owner can measure it; a finding whose location you cannot place is reported as a
  location you could not place.
- **blocking:** say for each finding whether it blocks the `accept` line or is an observation to
  carry forward.
- **budget:** `idle-compute`, no exclusive resource, **18 minutes wall clock, hard stop.**
- **escalate:** if the images cannot be opened or are not the 800x560 canvas the report claims, say
  so and stop; that is a `blocked` verdict, not a pass.
- **repair:** none. A defect named here becomes a writer package cut by the owner.
- **Verbal shape:** exactly one verdict — `pass`, `fail` (with the violated criterion and how to
  reproduce the reading), or `blocked` (with what is missing). Write it to
  `evidence/reviews-r1a/A-bow-study-v2-image-review-1.md` in the shape of
  `evidence/reviews-r1a/B-hand-study-v1-image-review-1.md` (blocking findings, then nonblocking
  observations). Run no git command; the owner commits the review.

## Package G3 — `r1a-b-hand-r1-index-pad` (work package, one writer)

- **Kind and name:** work package, `r1a-b-hand-r1-index-pad`, serving the `learn_draw` roadmap at
  R1a's contact criterion for the hand study.
- **Goal:** every digit rests on the dish's own emitted underside within the bound the inherited
  test already uses, with nothing in that test added, removed or lowered.
- **Writable path:** `.scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1/` only.
  `B-hand-study-v1/` is frozen evidence and is not touched.
- **Scope, in this order:** (1) the **index** digit's arrival angle — it stands 7.05 px below the
  underside where the middle and ring already sit inside the 5.5 px bound after package G2 made each
  pad's axis the chord parallel to the surface and offset the approach knot by the tip radius
  (`contact.py::finger`, the radius law reaching `r_tip` by 0.88 of the span). The middle and ring
  must stay inside the bound and the distal separations must stay at or above the 0.30 floor with
  roots at or below 0.10. (2) rebuild and commit: `artwork.svg`/`artwork.png`, the `check/` bundle
  routed **inside the package** with `draft-fullres.png` listed first, `manifest.json` +
  `manifest.sha256`, README numbers. No new test, no art change judged by eye, no change to the
  dish, the palm, the thumb, the well's spoke fan (blocker B2) or N1–N5.
- **Accept:** `cd <package> && PYTHONDONTWRITEBYTECODE=1 ../../../../.venv/bin/python -m unittest
  discover -s tests -t .` prints `OK` over **23 tests** (today: `FAILED (failures=1)`, index 7.051 px
  not less than 5.5); the per-digit stand-off is quoted from the suite output inside
  `>= -1.0` and `< clearance + 4.0`; the lift mutation still fails as it must; distal/root
  separations quoted; a fresh build `cmp`-identical to `artwork.svg` and a fresh render to
  `artwork.png`; `check/report.txt` line 1 resolves inside this package; `manifest.py --check` and
  `sha256sum -c` verify over the real file set; one commit at the end.
- **Out of scope, and named so it is not smuggled in:** the four tests package E demanded, package
  H's defect tests, blocker B2, N1–N5 — package I, next wave.
- **Spend:** `idle-compute`, no exclusive resource. **Wall clock 18 minutes, hard stop.**
- **Stop:** at the clock, commit a self-consistent package (artwork, bundle, manifest, README) and
  report the number reached. A truthful RED with a measurement is a valid report. **Never lower a
  bound or weaken an assertion to pass** — if the index pad cannot be closed by the arrival angle,
  report the bound that makes it unreachable (as R3 was reached) rather than editing the test.

## Launch order

C and G3 run in parallel: disjoint write areas, one reviewer and one writer, no shared file. Package
D (B's structural review) still waits for package I, not for G3. Nothing is pushed.
