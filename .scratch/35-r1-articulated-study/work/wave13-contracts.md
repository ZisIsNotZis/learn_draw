# Wave 13 — the two reviews R1a exit still needs, cut before they can be launched

Cut by the owner of `learn_draw` while wave 12's two packages were still running, so that a kill of
this session costs the dispatch order and not the contracts. Wave 12 is
[`wave12-contracts.md`](wave12-contracts.md); its run ids are recorded there.

## What wave 13 is waiting on

**Wave 12's review returned before this file's second edit, and it BLOCKED.** The verdict is
archived verbatim at
[`evidence/reviews-r1a/B-hand-study-v1-image-review-1.md`](../evidence/reviews-r1a/B-hand-study-v1-image-review-1.md)
(`5e12d36`, `draft-fullres.png` `e428bb0d…`): three blocking findings — (1) the occlusion is inverted,
digits drawn in front of the plate's near rim so the dish is unsupported, (2) a radial spoke fan and
concentric banding in the well turn it into a flat lens with one rim, (3) the hand is five evenly
spaced parallel prongs with no thumb opposition and no knuckle mass — plus five nonblocking ones. The
reviewer stated it opened only the two PNGs and executed nothing. B therefore carries an art verdict
now: **failed**, on the frozen revision, and the plan's repair cycle (one scoped repair by a writer,
then a re-review against the repaired revision with a fresh manifest) is what follows.

That reorders the two packages below:

- **`r1a-b-hand-repair-1`** (package E, below) is cut and dispatched instead of waiting.
- **`r1a-b-struct-1`** (package D) now reviews the **repaired** revision, not `5e12d36`: a structural
  pass over a revision whose construction is about to change is work that has to be redone, and the
  failed revision's mechanical claims are not what R1a exit will rest on.
- **`r1a-a-bow-v2-image-review-1`** (package C) is unchanged and still waits on the repair landing.

- **`r1a-a-bow-v2-image-review-1`** launches the moment `r1a-a-bow-v2-repair`
  (`97d0e1c2-0ef3-410a-8afe-449930bc6c3a`) reports a frozen revision, and not before: a review of a
  moving tree is a review of nothing. Its artefacts are whatever that revision's `check/` bundle
  lists first, and its report binds to the sha256 the writer's report names.
- **`r1a-b-struct-1`** launches after `r1a-b-image-review-1`
  (`d5852429-afb3-47ae-b6d8-2cf270ce7655`) has returned. The reason is mechanical, not procedural:
  a structural re-run rebuilds and may regenerate `check/`, which is a write into the directory the
  image reviewer reads, and a frozen image that moves mid-read is not frozen.

## Package C — `r1a-a-bow-v2-image-review-1` (review package, read-only)

- **Owner:** fresh independent sight-capable reviewer, launched `fresh`.
- **Artefacts judged:** line 1 of `evidence/A-bow-study-v2/check/report.txt` (the 1:1 image) and the
  source image it lists, at the sha256 the repair's report names. Nothing else.
- **Blindness:** the same clause as wave 12's package B — no README, no `source/`, no `tests/`, no
  `check/report.txt` beyond the image list, no manifest, no ledger, no wave log, no producer report.
  The six defects that v1's review named are **not** given to it: the question is "what is wrong
  here?", and a reviewer handed the previous verdict answers the previous verdict. Its findings are
  then compared against the six by the owner, not by the reviewer.
- **Questions:** the four acceptance questions, unchanged, plus the study's must-read-as line for a
  ribbon bow (a knot where the ribbon wraps and crosses itself; two lobes with curved free edges
  opening away from the knot; two tails leaving the frame; creases following real folds; failure
  readings: two closed pills, a bowtie, a flat sticker, a crumpled paper bag, two lobes joined by a
  chord).
- **Writes:** `evidence/reviews-r1a/A-bow-study-v2-image-review-1.md` and nothing else.
- **Spend:** `idle-compute` + `time`. **Wall clock:** 25 minutes, hard stop.

## Package D — `r1a-b-struct-1` (review package, read-only)

- **Owner:** fresh independent structural reviewer, launched `fresh`.
- **Inputs:** `evidence/B-hand-study-v1/` at `5e12d36` — source, tests, `manifest.json`,
  `manifest.sha256`, and the contract it was built to
  ([`r1a-object-study-contracts.md`](r1a-object-study-contracts.md) § B-hand-study-v1). The writer's
  README may be read as a **claim list to falsify**, never as evidence.
- **Questions:** (1) does the suite pass from a clean tree, and does the delivered PNG equal a fresh
  build through the documented path, byte for byte; (2) does `manifest.py --check` and `sha256sum -c`
  verify 100 % over the real file set, and is a file present that the manifest does not list;
  (3) does the contact test *re-derive* the dish's rim from the emitted mesh rather than reuse a
  producer constant — the check is to perturb the constant and watch the test fail; (4) is the
  occlusion count and its `--no-depth-break` mutation reproducible, and does the mutation draw
  through all of them; (5) does any source file name `image.jpg` or import an image library
  (reference-free is the contract); (6) are the separation numbers at the roots and at the distal
  halves the ones the README states, measured on the emitted outlines; (7) is any claim in the
  README not supported by the source.
- **Acceptance:** each check re-run with its command and output, findings located in source and
  image, and the parts it could not verify named as unverifiable rather than passed.
- **Writes:** `evidence/reviews-r1a/B-hand-study-v1-structural-review-1.md` and nothing else.
- **Spend:** `idle-compute` + `time`. **Wall clock:** 30 minutes, hard stop.

## What neither package may do

Neither awards an art verdict on the other study, neither touches a writer's directory, neither
promotes a baseline, and neither is dispatched with a budget larger than the harness deadline it is
given (`timeoutMs` named at launch, checkpoint steer ten minutes before it).

## Package E — `r1a-b-hand-repair-1` (work package, one writer) — dispatched 2026-10-21

- **Owner:** one writer. **Writable path:** `evidence/B-hand-study-v1-r1/` only — a copy of
  `evidence/B-hand-study-v1/` as its base. `B-hand-study-v1/` stays untouched: it is the revision the
  failed review is bound to, and evidence that gets overwritten is evidence that was never worth
  keeping. Precedent: `B-hand-v2` → `B-hand-v2-r1`, `A-cloth-v6-closeout`.
- **Directions** taken by the owner, recorded as assumed here so the writer is not left guessing:
  (i) the hand is **under** the plate — the near rim is an unbroken foreground silhouette and every
  digit that reaches past it disappears behind it; (ii) the thumb opposes **on the near side**, which
  is the study contract's own wording and which v1's README records itself as having violated ("on the
  far flank"); (iii) digit width, reach and direction **vary**, because uniformity is the "rake tines"
  failure the contract names; (iv) the palm gains a knuckle row and a heel, because the review could
  not tell the bottom block from a wrist. What reversing these costs: a re-review of the same revision
  that leaves the two worst blockers in place, i.e. one full review cycle per reversal.
- **Acceptance:** every item a command — the inherited suite OK with no assertion weakened; a
  near-rim-occlusion test that asserts each digit's contact faces are behind the rim's near surface and
  that fails when the depth order is inverted (mutation in `tests/negative-control-output.txt`); a
  thumb-opposition test with a signed side, not a prose claim; a digit-variation test that fails on the
  v1 uniformity; a well-shading test that fails on a spoke/apex-wedge artefact (the review's blocker 2
  is the sub-pixel apex quads inflated 0.45 px plus 60-step revolution flat shading — find the real
  cause, do not paint over it); `check/` with the 1:1 image first; `manifest.json` +
  `manifest.sha256` over the new file set, fresh hashes; two builds byte-identical and the delivered
  PNG equal to a fresh render; README that carries a finding-to-repair table against the archived
  review, the measured numbers the new source emits, and an explicit list of what is unverified.
- **Spend:** `idle-compute` + `time`; no exclusive resource, so no reservation. **Wall clock:** 75
  minutes, hard stop, checkpoint steer at 65.
- **Run id:** recorded in `wave12-contracts.md` beside wave 12's, and in the wave log row 27.
