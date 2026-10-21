# Wave 14 — two single-stage packages, cut after wave 13's two repairs returned incomplete

Cut by the owner of `learn_draw` on 2026-10-21 after reading both returned revisions. Wave 13 is
[`wave13-contracts.md`](wave13-contracts.md); the returned state is in [`STATUS.md`](../../../STATUS.md)
and in the wave log rows 25 and 27.

## What wave 13 proved about sizing

Both repairs returned **before** their stated 75-minute clock and **neither** was complete:
`A-bow-study-v2` at 12:48 (`558ba1c`, dispatched 12:40) with 16/17 inherited tests and the six
defect tests unwritten; `B-hand-study-v1-r1` at 12:58 (`51ba2eb`, dispatched ~12:42) with 4 failures,
no new test, a stale `check/` bundle and an illegible pose. Both wrote truthful READMEs naming what
they had not done.

Inference, marked as such: the durations are commit timestamps against the dispatch time recorded in
`2bd52cf`/`1124b15`, not run records (those are outside the checkout), so the mechanism is inferred
rather than observed — but the shape is unambiguous. **A single writer run completes about one stage
of this work and then returns**, whatever clock it was given. Wave 13 sized each package as "finish
the repair", which is a goal, not a stage, so each returned a partial.

The cure is the one P34 already prescribes for a different mechanism: cut to a deliverable that is
true when the run stops, and let the next run take the next stage. Every package below therefore has
**one** deliverable, a fresh `check/` bundle as its last act, and a commit at the end.

## Resolutions this wave carries (owner decisions, recorded so no writer has to guess)

**R1 — the B contact-surface conflict raised by package E is resolved; the test is re-targeted, not weakened.**
`tests/test_hand_construction.py::TestContact::test_every_digit_rests_on_the_band_and_none_penetrates_it`
measures each digit's tip against the rim band's **top plane**, which encodes v1's construction (tips
on top of the band, in front of the near rim). Direction (i) — hand under the plate — supersedes that
construction, so the band top is no longer a contact surface and the assertion is unsatisfiable for a
truthful drawing. The law it encodes survives: *a digit's pad rests on the contact surface and does
not penetrate it, and a digit that lifts off is caught*. The surface changes from the rim band's top
to the dish's **underside ring** (`dish.derived_rings()` → `contact.underside_ring()`), with the same
1.5 px clearance, and the lift mutation (clearance + 20 px) must still fail the test.
`test_the_hand_follows_the_dish` is re-targeted the same way: it perturbs `RIM_OUTER`/`RIM_INNER`,
which no longer drive the contact, and must perturb the underside's own drivers
(`FOOT_RADIUS`/`AXIS_UNDER_Z`) instead.
**Not** re-targeted, **not** lowered: `test_the_distal_halves_are_separated` (0.10 against a 0.30
floor) is a real construction failure — the digits are cramped — and package G fixes the geometry.
What reversing this resolution costs: without it the B repair can only pass by putting the hand back
in front of the near rim, i.e. by restoring the reviewed blocker B1.

**R2 — direction (i) is refined to a legible pose.** "Under the plate with an unbroken near rim" is
kept, and it implies that hand surface overlapping the plate is hidden. Legibility therefore cannot
come from drawing the digits against the plate's well: it comes from where the hand is *not* behind
the plate. The pads extend **outboard past the plate's silhouette** and are seen against the
background, with only the digits' inner edges cut by the near rim; the palm's mass drops below and
behind the plate's near contour. Recorded as assumed; the alternative (a lower camera or a tilted
plate) changes the study's fixed framing and is the owner's call, not a writer's.

## Package F — `r1a-a-bow-v2-width-law` (work package, one writer)

- **Goal:** the last inherited law on `A-bow-study-v2` holds: no isolated width jump of 3.0 px or
  more along the emitted strip, with the inherited tests unmodified.
- **Writable path:** `evidence/A-bow-study-v2/` only. `evidence/A-bow-study-v1/` is frozen evidence.
- **Scope:** the turn/width geometry that produces the jump at the station the suite names (3.58 px
  at one station; the neighbour steps unchanged, so it is a piece boundary). No new test, no README
  rewrite, no art change judged by eye, no new structural approach. If the jump cannot be closed
  without changing the routed turn count, stop and report the measurement rather than forcing it.
- **Accept:** `cd evidence/A-bow-study-v2 && PYTHONDONTWRITEBYTECODE=1 ../../../../.venv/bin/python -m unittest discover -s tests -t .` prints `OK` (17 tests), `source/build.py` to `/tmp` is `cmp`-identical to `artwork.svg`, `scripts/draw render` reproduces `artwork.png`, `manifest.py --check` and `sha256sum -c manifest.sha256` verify, and `check/report.txt` still lists the 1:1 image first.
- **Spend:** `idle-compute`, no exclusive resource. **Wall clock:** 25 minutes, hard stop.
- **Stop:** at the clock, commit a self-consistent package (artwork, bundle, manifest, README numbers) and report the number reached; a truthful RED with a measurement is a valid report.

## Package G — `r1a-b-hand-r1-pose` (work package, one writer)

- **Goal:** the repaired revision shows five digits in the delivered image, with the distal halves
  separated at or above the inherited 0.30 floor, and every file a reviewer reads rebuilt from the
  revision that exists.
- **Writable path:** `evidence/B-hand-study-v1-r1/` only. `evidence/B-hand-study-v1/` stays frozen.
- **Scope, in this order (each committed):** (1) `check/report.txt` and `check/*.png` are **stale and
  misrouted** — `report.txt` names `evidence/B-hand-study-v1/` and `check/draft.png` is byte-identical
  to v1's `artwork.png`; regenerate them from the current revision so a reviewer following the report
  judges this revision; (2) the pose pass of R2 — pads outboard past the plate's silhouette, distal
  separation ≥ 0.30, roots still ≤ 0.10; (3) the three contact tests re-targeted per R1 with their lift
  mutation; (4) README's finding→repair table updated to the true state, with the reviewed items it
  did not fix still marked not fixed.
- **Out of scope this stage:** the well's spoke fan (reviewer blocker B2), N1–N5, the absent occlusion
  / thumb-opposition / digit-variation / well-shading tests — package I, next wave.
- **Accept:** suite prints the exact pass/fail list with no assertion added, removed or weakened except
  the three contact tests re-targeted per R1 (the diff of those three tests is in the report, and the
  lift mutation still fails); `check/report.txt` line 1 is this revision's 1:1 image and its paths
  resolve inside `B-hand-study-v1-r1/`; `cmp` of a fresh build and of a fresh render against
  `artwork.svg`/`artwork.png`; `manifest.py --check` and `sha256sum -c` verify over the real file set;
  the distal and root separation numbers quoted from the suite output.
- **Spend:** `idle-compute`, no exclusive resource. **Wall clock:** 25 minutes, hard stop.
- **Stop:** at the clock, commit and report; the bundle regeneration of step (1) is the one item that must never be left half-done.

## Packages cut here and dispatched later — package H and package I

**Package H — `r1a-a-bow-v2-defect-tests`.** The six defect tests the R1a contract demands, one per
defect the v1 image review named, each with a negative control that restores v1's behaviour and fails
(`tests/negative-control-output.txt`), plus the README's defect table. Its criteria depend on what
`r1a-a-bow-v2-image-review-1` (package C of wave 13) returns, so it is not cut in detail until that
verdict is in — a defect test written before the verdict encodes the producer's guess at the defect.

**Package I — `r1a-b-hand-r1-tests`.** The absent tests of package E's acceptance (near-rim occlusion
with a mutation that inverts the depth order, signed thumb opposition, digit variation that fails on
v1's uniformity, well shading that fails on a spoke artefact), plus the well's blocker B2 at its
cause, plus N1–N5 in the review's order.

## Launch order

Package F and package G run **in parallel**: two separate directories, no shared file, one writer
each. Package C (`A-bow-study-v2` image review) waits for F, because F moves the geometry and an
image verdict on a revision that is about to change expires the moment it changes. Package D
(`B-hand-study-v1-r1` structural review) waits for I, not G: D re-runs the suite and the manifest, and
a package whose tests are still being written is not a package to audit.
