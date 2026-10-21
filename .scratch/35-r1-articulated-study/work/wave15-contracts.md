# Wave 15 — the four verdicts R1a exit needs, cut before they can be launched

Cut by the owner of `learn_draw` on 2026-10-21 while wave 14's two writers were still running, so
that a kill of this session costs an order rather than a contract. Wave 14 is
[`wave14-contracts.md`](wave14-contracts.md).

## Why four and not two

R1a's exit ( [`docs/drawing/roadmap.md`](../../../docs/drawing/roadmap.md) § R1a) is: *both studies'
four acceptance questions pass on one frozen revision each; a reference-free study reproduces
reference-free; one manifest binds each study's revision; each study is presented for the user's
judgment.* The four acceptance questions are construction/attachment/pose, physical geometry and depth
visibility, drawing/art, and object cohesion — and an image reviewer cannot answer the mechanical two
any more than an execution reviewer can answer the two that need sight (P36). So each study takes one
image-only verdict and one execution verdict, and neither stands for the other.

## What each review is bound to

Every review below binds to **one frozen revision**: the commit hash, the sha256 of the 1:1 image named
first in `check/report.txt`, and the sha256 of `manifest.sha256`. A revision that moves invalidates its
verdict, and the verdict says so in its first line. The owner records the binding in the ledger in the
same act.

## Package J — `r1a-a-bow-v2-image-review` (image-only judge, read-only)

- **Owner:** fresh independent sight-capable reviewer, launched `fresh`. It awards one art and one
  cohesion verdict on the picture and nothing else.
- **Inputs:** line 1 of `evidence/A-bow-study-v2/check/report.txt` (the 1:1 image) and the source image
  it lists. **Nothing else** — no README, no `source/`, no `tests/`, no manifest, no ledger, no wave log,
  no producer report, and **not** the six defects v1's review named: a reviewer handed the previous
  verdict answers the previous verdict. Its findings are compared against the six by the owner.
- **Questions:** as in wave 13 package C — the must-read-as line for a ribbon bow (a knot where the
  ribbon wraps and crosses itself; two lobes with curved free edges opening away from the knot; two
  tails leaving the frame; creases following real folds) and the failure readings (two closed pills, a
  bowtie, a flat sticker, a crumpled paper bag, two lobes joined by a chord), plus the four acceptance
  questions it can answer from the image: does the object read as one connected thing, and does the
  image read as a drawing rather than as a mesh.
- **Writes:** `evidence/reviews-r1a/A-bow-study-v2-image-review-1.md` and nothing else.
- **Spend:** `idle-compute` + `time`. **Wall clock:** 20 minutes, hard stop.
- **Launches when:** package F has committed a revision whose suite is green or whose one failure is
  named, and the owner has written the binding (commit + two hashes) into the dispatch.

## Package K — `r1a-b-hand-r1-image-review` (image-only judge, read-only)

- **Owner:** fresh independent sight-capable reviewer, launched `fresh`.
- **Inputs:** `evidence/B-hand-study-v1-r1/check/report.txt` line 1 and the two images it lists, at the
  sha256 the dispatch names. **Nothing else**, and not the archived v1 verdict or its three blockers.
- **Questions:** the four acceptance questions as far as an image can answer them, plus the study
  contract's must-read-as line for a hand holding a plate (a hand with distinguishable digits whose
  relation to the plate is legible; the plate supported rather than floating; failure readings: five
  prongs, a dish on a stick, a hand in front of the plate it is supposed to hold).
- **Writes:** `evidence/reviews-r1a/B-hand-study-v1-r1-image-review-1.md` and nothing else.
- **Spend:** `idle-compute` + `time`. **Wall clock:** 20 minutes, hard stop.
- **Launches when:** package G (and, for the tests, package I) has landed and the bundle is regenerated
  from that revision — a stale bundle is exactly what made the wave 13 revision unreviewable.

## Package L — `r1a-b-hand-r1-execution-review` (execution check, read-only)

- **Owner:** fresh independent reviewer with execution tools (P36: a reviewer whose session cannot run
  a command reports everything NOT RUN, which is honest and is not verification).
- **Inputs:** `evidence/B-hand-study-v1-r1/` at the dispatched hash, its tests, `manifest.json`,
  `manifest.sha256`, and the contract it was built to
  ([`r1a-object-study-contracts.md`](r1a-object-study-contracts.md) § B-hand-study-v1). The README is a
  **claim list to falsify**, never evidence.
- **Questions:** (1) the suite passes from a clean tree, and the delivered PNG equals a fresh build and
  a fresh render through the documented path, byte for byte; (2) `manifest.py --check` and
  `sha256sum -c` verify 100 % over the real file set, and no file present is unlisted; (3) the contact
  test *re-derives* the dish's underside (perturb `FOOT_RADIUS`/`AXIS_UNDER_Z` and watch it fail), and
  the lift mutation still fails; (4) the occlusion count and its inverted-depth mutation are
  reproducible; (5) no source file names `image.jpg` or imports an image library; (6) the printed
  separation numbers match the README; (7) no README claim lacks source support; (8) **the
  construction/attachment and physical-geometry questions**: does every named part attach where the
  claim says, are there illegal interpenetrations, and does depth hide what is farther.
- **Writes:** `evidence/reviews-r1a/B-hand-study-v1-r1-execution-review-1.md` and nothing else.
- **Spend:** `idle-compute` + `time`. **Wall clock:** 25 minutes, hard stop.

## Package M — `r1a-a-bow-v2-execution-review` (execution check, read-only)

Same shape as package L, over `evidence/A-bow-study-v2/`, with two additions specific to A: the
reference may seed parameters and must then be closed (the build reads neither the crop nor a metric at
runtime), and every measured-vs-author-choice table in the README must match the emitted numbers.

## The gate after them

When J and M pass, and K and L pass, and each study's reference-free reproduction and manifest are
verified by the owner, R1a is at its exit gate: **the person sees both images and judges them**. No
agent awards that; no agent approves it on his behalf, and if he is away the gate waits. A study whose
verdict fails is repaired inside its own finite budget, or reported unresolved — never with a lowered
criterion, and never by promoting a revision whose review did not bind to its hash.

## First round dispatched — what wave 14's second round unblocked, and the one stage it left open

Added by the owner on 2026-10-21 after wave 14's second round landed, without changing J–M above.

**Package J returned FAIL** (`d6b6fd3`), bound to commit `3825d51`, `check/draft-fullres.png`
sha256 `1d517c0c82061c39831f034811a973ade9a4858796ecc6e6a16b8949998dbe7d`, verified before it
judged; it recorded `manifest.sha256` as outside its input set and did not extend the verdict to it.
Its six blocking findings are in [`../evidence/reviews-r1a/A-bow-study-v2-image-review-1.md`](../evidence/reviews-r1a/A-bow-study-v2-image-review-1.md)
and none of them is one of the six v1's review named. **The bow therefore carries no passing art
verdict and M (its execution review) is not launched**: an execution verdict on a revision whose art
gate failed buys nothing, and the repair of B1–B6 is a new package for the next round.

**Package K and package L were dispatched together by the owner**, not sequentially: waiting for K's
reading before launching L costs a reviewer round and buys nothing, because the two bind to the same
revision and answer different questions. That routing is root's `assumed` decision, not the person's.
Both bind to commit `34b31b4`, `check/draft-fullres.png` sha256
`4dbcad2ec517191c73c75057f948f0a73aeec5566566df922e1f9ac8e8354083`, `manifest.sha256` sha256
`6127712360946cd1072ae59bf00548cbcc3175826aca5bcfa8e622d511d907b7` (19 entries).

**Package G3 — `r1a-b-hand-r1-index-pad`** (work package, one writer, wave 14's package G at its
third stage). The first round's G2 put every pad's axis on the chord parallel to its underside and
the radius law reached `r_tip` by 0.88 of the span; the middle and ring pads came inside the 5.5 px
bound, the **index pad moved 10.6 → 7.05 px and is still 2.05 px over** (`4eafe0e`).

- **Writable path:** `evidence/B-hand-study-v1-r1/` only. `evidence/B-hand-study-v1/` is frozen.
- **Scope:** the **index** digit's arrival angle (`contact.py::finger`), with the middle and ring
  inside the bound and the distal separations at or above the 0.30 floor, roots at or below 0.10;
  then rebuild artwork, `check/` bundle (routed inside the package, 1:1 image first), manifest and
  README numbers. No new test, no dish, palm, thumb, well-shading, B2 or N1–N5 work.
- **Accept:** the suite prints `OK` over 23 tests (today `FAILED (failures=1)` — index 7.051 px not
  less than 5.5); per-digit stand-off quoted inside `>= -1.0` and `< clearance + 4.0`; the lift
  mutation still fails; separations quoted; `cmp` clean on a fresh build and a fresh render;
  `check/report.txt` line 1 resolves inside the package; `manifest.py --check` and `sha256sum -c`
  verify; one commit.
- **Never:** lower a bound, weaken an assertion, or edit the contact test. If the index pad is
  unreachable by the arrival angle, report the bound that makes it so — as R3 was reached — and it
  becomes a `contract` report upward.
- **Spend:** `idle-compute`, no exclusive resource. **Wall clock 18 minutes, hard stop.**
- **Landed `34b31b4`, 23/23:** `source/contact.py::finger` puts a third knot `PAD_RUN` (1.6 tip
  radii) behind the approach knot on the pad's own axis, because the middle digit's pad chord
  (2.2 px at `reach = 0.98`) is shorter than the tube's sample spacing (10 px) so its last
  cross-section inherited the shaft's direction. Closest vertex per digit: index 1.60, middle 4.26,
  ring 2.86, little 1.60, thumb 1.63 px inside the inherited window `> -1.0`, `< 5.5`; lift
  mutation still fails at 21.77 px. No bound moved, no assertion or test edited. The writer left
  the word `SUITE GREEN` in place but the regenerated `manifest.sha256` listed the pre-edit
  `README.md` hash; the owner re-ran `source/manifest.py --write` before committing, so all 19
  entries verify and none is unlisted.
- **Stop:** commit a self-consistent package at the clock and report the number reached; a truthful
  RED with a measurement is a valid report.

Allocation, one writer per area: J writes one review file under `evidence/reviews-r1a/` and runs no
git command; G3 writes only its own package and commits it. No path is shared. Nothing is pushed.
