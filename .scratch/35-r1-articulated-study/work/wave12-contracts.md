# Wave 12 — the R1a ownership handover contracts

Issued by the node that took ownership of `learn_draw` at HEAD `5e12d36` (2026-10-21). This file is
the dispatch payload, committed **before** the packages were launched, because a dispatch that
exists only in a conversation is lost when the run dies (P34). The two contracts below were launched
verbatim as the task text of two background children.

## The state this wave starts from, verified at `5e12d36`

- `B-hand-study-v1` exists as a package: `source/`, `tests/`, `artwork.svg` (2 997 633 B),
  `artwork.png` 900x700, `check/` with the 1:1 image first, `manifest.json` + `manifest.sha256`,
  `README.md`. It carries **no art verdict**, correctly. Rebuilt byte-identically from committed
  source by its writer (commit `5e12d36`).
- `A-bow-study-v2` is a dead run's partial restart: `source/`, `tests/`, `README.md` (byte-identical
  to v1's, `46e772ff…`), `artwork.svg`, `artwork.png`. No `check/`, no manifest, no negative control.
  Its inherited suite fails **8 of 17**, re-run in place for this wave with
  `PYTHONDONTWRITEBYTECODE=1 ../../../../.venv/bin/python -m unittest discover -s tests -t .`:
  `test_every_crossing_has_a_depth_break_and_a_broken_rear_edge` (13 audited crossings, |dz| 0.7–15.8 px
  against a 16 px cloth thickness, two rear edges drawn through), `test_every_triangle_wears_its_own_winding`
  (4 of 1240), `test_the_field_actually_varies` (width 77.7–301.6 px, ratio 3.88 against the 4.0 floor),
  `test_the_knot_is_a_waist_between_the_loops` (knot band 113.3–113.5 px vs loops 159.6 px),
  `test_width_is_continuous_along_the_emitted_strip` (9.03 px isolated jump against a 3.0 limit), and the
  three artefact tests (`test_the_bundle_lists_the_1to1_image_first`, `test_manifest_verifies_over_the_real_file_set`,
  `test_sha256sum_agrees_with_the_manifest`) for the bundle and manifest that were never emitted.

## The decisions this wave takes

- **Run ids, for a later reader who has to find a reaped run:** package A `97d0e1c2-0ef3-410a-8afe-449930bc6c3a` (agent `worker`, fresh,
  `timeoutMs` 4 500 000, checkpoint steer at 65 min), package B `d5852429-afb3-47ae-b6d8-2cf270ce7655` (agent `reviewer`, fresh,
  `timeoutMs` 1 500 000, output bound to the archive path). Both launched `async` from the checkout with `worktree: false`,
  which is what lets package A commit into `evidence/A-bow-study-v2/` directly. Package E (wave 13, the B repair) is
  `eec45d67-36fe-4af2-8454-ef17ebeaa3e1`: `worker`, fresh, `timeoutMs` 4 500 000, checkpoint steer at 65 min.

1. **Ordering: the B image review and the v2 repair run concurrently, and neither is a second writer.**
   The reviewer holds no write area in the study tree — it reads two PNGs and writes one report into
   `evidence/reviews-r1a/` — so "one live writer per area" is satisfied with exactly one writer,
   `evidence/A-bow-study-v2/`. The plan already authorises concurrent A and B work on disjoint
   directories; the only thing that would force the review to wait is a second writer in the same
   area, and there is none.
2. **The B reviewer is blind to the producer's reasoning.** It is launched `fresh` (no inherited
   context), it may open exactly two PNG files, and it is forbidden the README, `source/`, `tests/`,
   `check/report.txt`, the manifest, the wave log, the ledger and the writer's report. It is told that
   a verdict formed after reading any producer document is void. It is given the acceptance questions
   and the must-read-as criteria, which are the criterion, not the rationale.
3. **v2 is re-dispatched as the repair root approved** (resume, not restart): retune the turn geometry
   until the inherited law holds, add the six defect tests, replace the README, emit `check/` and the
   manifest. The inherited tests keep every existing assertion; a test that is wrong is a `contract`
   report, never a lowered threshold.
4. **The B structural review waits.** It would run the build and regenerate the `check/` bundle inside
   the directory the image reviewer is reading, which is a write into a frozen area mid-read. It is
   dispatched the moment the image verdict lands, against whatever revision the verdict binds to.

## Package A — `r1a-a-bow-v2-repair` (work package, one writer)

- **Owner:** one writer, directory `.scratch/35-r1-articulated-study/evidence/A-bow-study-v2/` only.
- **Writable path:** that directory. **Read-only:** every other evidence directory (including
  `A-bow-study-v1/` as the reference package shape), `scripts/`, `docs/`, `work/`, and the sealed
  `work/holdout-brief.sealed.md` (not read at all).
- **Exclusions:** no edit to `STATUS.md`, the wave log, the ledger, the R1a contracts or any other
  package; no art verdict; no baseline promotion; no weakening of an inherited assertion; no touch of
  the B study.
- **Acceptance:** every item is a command, not a claim — see the launched task text in
  `wave12-a-bow-v2-repair.js`.
- **Spend:** `idle-compute` (local CPU only, no network write, no paid API, no GPU) and `time`.
  No exclusive resource, so no reservation is written.
- **Wall clock:** 75 minutes, hard stop, checkpoint at 65.

## Package B — `r1a-b-image-review-1` (review package, read-only)

- **Owner:** fresh independent sight-capable reviewer, launched `fresh`.
- **Artefacts judged, pinned:** `check/draft-fullres.png` `e428bb0d…` (900x700) and
  `check/draft.png` `0dbeb263…` (900x700) at commit `5e12d36`; `artwork.png` is byte-identical to
  `check/draft.png`.
- **Writes:** `evidence/reviews-r1a/B-hand-study-v1-image-review-1.md` and nothing else.
- **Spend:** `idle-compute` and `time`. **Wall clock:** 25 minutes, hard stop.
