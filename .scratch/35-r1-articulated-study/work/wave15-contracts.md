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
