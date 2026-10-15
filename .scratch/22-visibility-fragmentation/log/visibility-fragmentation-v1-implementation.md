# S1a visibility-fragmentation scratch study

## Result

Implemented the requested **scratch-only diagnostic slice** in `.scratch/22-visibility-fragmentation/`. The evidence supports this geometric cause: the resolver treats overlapping projected triangle bounding boxes as enough to submit depth cutters, although bbox overlap does not establish positive-area triangle intersection. On shared-edge-only pairs, its existing tie bias and EPS line clipping produce repeated-vertex, zero-area fragments and tiny positive slivers; serializing these fragments changes Chromium coverage near mesh edges.

One isolated candidate module adds a strict separating-axis positive-area-intersection gate after the existing bbox rejection. It preserves the existing opaque API, depth-plane clipping, interpolation, declaration/tie policy, and allows genuine overlapping faces—including same-component occlusion—to continue through the resolver. It is not production-integrated.

### Proof highlights

- The computed fractional `4x3` planar mesh has 24 faces and 12 bbox-overlapping/no-positive-area pairs. A concrete same-cell pair has identical bboxes but only a shared diagonal. Current clipping returns 48 fragments, 24 with zero area; the candidate returns the 24 source triangles and byte-identical SVG/Chromium pixels. The current-versus-source delta in this reduced case is four one-level silhouette pixels at the last row/column; this small case isolates the touch/clip mechanism, not the fine arch's interior defect.
- Re-running the fixed parent fine96x12 arch with the same geometry, camber, camera, fit, fill and barycentric safe mask reproduces source raw = **0**, current canonical = **44**, candidate = **0** nonmatching pixels among **8,495** safe interior samples. The 44 current deviations are within 0.42 px of projected internal mesh edges. No source/current/candidate geometry or source code outside exercise22 was changed.
- Fine-arch fragment counts: source 4,416; canonical 29,464 (20,472 zero-area; 201 positive fragments with area `<=1e-10`, 334 `<=1e-7`); candidate 9,681 (5,151 zero-area; 23 `<=1e-10`, 24 `<=1e-7`). Remaining candidate fragments retain positive-area visibility. A second Chromium render of the candidate PNG is byte-identical.
- Scratch safety tests distinguish exact touching from a tiny positive-area overlap, preserve changing depth across a triangle and declaration reversal away from ties, same-component self-occlusion, camera-dependent ring/body occlusion, and the existing first-declared exact coplanar tie. The strict tie and depth logic itself is unchanged.

## Test caveat / open review finding

An isolated candidate-import run of 68 tests across the relevant historical vector-visibility, ribbon-family, support-surface, ribbon-drawing and spatial-sketch tests plus five scratch tests produced **67 passed and 1 failed**. The failing historical test is `scripts.tests.test_vector_visibility.VectorVisibilityTests.test_same_whole_strip_updates_visibility_in_two_cameras`: it expects the oblique strip visible-area fraction `.7968 ± .01`; the candidate yields `0.7559247668712519` (delta `-0.0408752`). Its yaw-0 check and camera-change assertion pass; the new scratch check measures yaw 0 `0.8699601` and yaw 55 `0.7559248`, retaining camera-dependent occlusion. This changed prior area result is material and needs the required independent parent review—it is not silently waived or accepted by this report. The other 67 tests pass when that single historical expected-value check is excluded.

This is not visual/art acceptance, S0 recertification, or an S1a gate pass. No full support matrix, learner, reference comparison, or canonical integration was performed. The labelled/unlabelled boards are diagnostics; their draw-check image lists are in the report files named below.

## Changed-file inventory

All new/modified task files are under the exercise22 scratch seam; `.scratch/22-visibility-fragmentation/spec.md` is unchanged.

- Candidate and tests: `.scratch/22-visibility-fragmentation/work/vector_visibility_candidate.py`, `work/study.py`, `work/test_visibility_candidate.py`.
- Durable log/card: `.scratch/22-visibility-fragmentation/log/visibility-fragmentation-study.md`, `.scratch/22-visibility-fragmentation/teaching/positive-area-overlap.md`.
- Geometry / browser evidence: `evidence/fine/study.json`; `minimal-4x3-{source,canonical,candidate}.{svg,png}`; `arch-{source,canonical,candidate}.{svg,png}`; `arch-candidate-repeat.png`; `arch-{labelled,unlabelled}.png`.
- Reference-free checks: `evidence/check-labelled/{report.txt,draft.png}` and `evidence/check-unlabelled/{report.txt,draft.png}`. Each report lists only its `draft.png` as the image to review.

Canonical visibility source SHA-256 is unchanged at `6cea919d0c83b1c4ebb9b3ec3379854c910e2758610b449c036c25c9ce8e1ada`; historical test source is unchanged at `8977f31fb12e1f9a660f30866bd0ba271e4541f86d29cc091e32cd5a9cd4acd2`. Candidate SHA-256: `ed07910a16000e82215b924d932c1859c4dc2da3b932f6d3740ccbb23cf08da6`. HEAD remains `24693d4`.

## Commands run

- `.venv/bin/python .scratch/22-visibility-fragmentation/work/study.py` — passed; generated source/current/candidate SVG/PNG, geometry/area/pixel/edge evidence, source hashes, and deterministic repeat evidence.
- `.venv/bin/python .scratch/22-visibility-fragmentation/work/test_visibility_candidate.py` — passed, 5 scratch regression tests.
- Explicit candidate-import unittest invocation over the five historical modules plus the scratch tests — ran 68; 67 passed, 1 failed at the documented old oblique area expectation.
- Explicit candidate-import unittest invocation over the same modules/tests excluding only `test_same_whole_strip_updates_visibility_in_two_cameras` — passed, 67 tests.
- `scripts/draw check .scratch/22-visibility-fragmentation/evidence/fine/arch-unlabelled.png --outdir .scratch/22-visibility-fragmentation/evidence/check-unlabelled --pane 1500` — passed; report lists `.scratch/22-visibility-fragmentation/evidence/check-unlabelled/draft.png`.
- `scripts/draw check .scratch/22-visibility-fragmentation/evidence/fine/arch-labelled.png --outdir .scratch/22-visibility-fragmentation/evidence/check-labelled --pane 1500` — passed; report lists `.scratch/22-visibility-fragmentation/evidence/check-labelled/draft.png`.
- Final `sha256sum`, `git status --short`, and `git diff --cached --name-only` — passed; canonical source/test hashes unchanged and all exercise22 files are untracked scratch artifacts.

## Staging / handoff

No files were staged by this task. `git diff --cached --name-only` still reports the **pre-existing protected** staged `.gitmodules` and `vendor/huashu-art-motion`; they were neither changed nor unstaged. Other inherited dirty work was preserved. `noStagedFiles` is therefore `false` for repository state, with no new task staging.

Fresh independent review remains required, particularly for the oblique ring-area discrepancy. Parent owns any choice to integrate or reject the candidate, canonical source/provenance changes, expanded validation, and subsequent S1a decisions.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Only exercise22 scratch work/evidence/log/teaching files were added; canonical implementation, historical tests, reference inputs, and inherited work were left unchanged. The isolated candidate is one strict positive-area triangle-overlap gate, with no rendering/style workarounds."
    },
    {
      "id": "criterion-2",
      "status": "satisfied",
      "evidence": "evidence/fine/study.json records pinned source/plan hashes, generated touch geometry and actual fragments/areas, raw/current/candidate Chromium metrics, edge-proximity coordinates, and a deterministic repeat. Scratch regressions plus exact draw-check image lists and the historical-suite discrepancy are reported for independent review."
    }
  ],
  "changedFiles": [
    ".scratch/22-visibility-fragmentation/work/vector_visibility_candidate.py",
    ".scratch/22-visibility-fragmentation/work/study.py",
    ".scratch/22-visibility-fragmentation/work/test_visibility_candidate.py",
    ".scratch/22-visibility-fragmentation/log/visibility-fragmentation-study.md",
    ".scratch/22-visibility-fragmentation/teaching/positive-area-overlap.md",
    ".scratch/22-visibility-fragmentation/evidence/fine/study.json",
    ".scratch/22-visibility-fragmentation/evidence/fine/minimal-4x3-source.svg",
    ".scratch/22-visibility-fragmentation/evidence/fine/minimal-4x3-source.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/minimal-4x3-canonical.svg",
    ".scratch/22-visibility-fragmentation/evidence/fine/minimal-4x3-canonical.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/minimal-4x3-candidate.svg",
    ".scratch/22-visibility-fragmentation/evidence/fine/minimal-4x3-candidate.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-source.svg",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-source.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-canonical.svg",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-canonical.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-candidate.svg",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-candidate.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-candidate-repeat.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-labelled.png",
    ".scratch/22-visibility-fragmentation/evidence/fine/arch-unlabelled.png",
    ".scratch/22-visibility-fragmentation/evidence/check-labelled/report.txt",
    ".scratch/22-visibility-fragmentation/evidence/check-labelled/draft.png",
    ".scratch/22-visibility-fragmentation/evidence/check-unlabelled/report.txt",
    ".scratch/22-visibility-fragmentation/evidence/check-unlabelled/draft.png"
  ],
  "testsAddedOrUpdated": [
    ".scratch/22-visibility-fragmentation/work/test_visibility_candidate.py"
  ],
  "commandsRun": [
    {
      "command": ".venv/bin/python .scratch/22-visibility-fragmentation/work/study.py",
      "result": "passed",
      "summary": "Exact fixed arch reproduction and generated mesh study; canonical source hash unchanged; candidate repeat PNG byte-identical."
    },
    {
      "command": ".venv/bin/python .scratch/22-visibility-fragmentation/work/test_visibility_candidate.py",
      "result": "passed",
      "summary": "5 scratch candidate tests passed."
    },
    {
      "command": "Candidate-injected unittest run: scripts.tests.test_vector_visibility, test_ribbon_family, test_ribbon_surface, test_ribbon_drawing, test_spatial_sketch, and scratch candidate tests",
      "result": "failed",
      "summary": "68 ran; 67 passed. One documented pre-existing exact oblique ring-area expectation fails at 0.7559248 versus 0.7968 +/- 0.01."
    },
    {
      "command": "Same candidate-injected unittest run, excluding only test_same_whole_strip_updates_visibility_in_two_cameras",
      "result": "passed",
      "summary": "67 tests passed; all remaining relevant historical and scratch checks pass."
    },
    {
      "command": "scripts/draw check .scratch/22-visibility-fragmentation/evidence/fine/arch-unlabelled.png --outdir .scratch/22-visibility-fragmentation/evidence/check-unlabelled --pane 1500",
      "result": "passed",
      "summary": "Reference-free report lists check-unlabelled/draft.png."
    },
    {
      "command": "scripts/draw check .scratch/22-visibility-fragmentation/evidence/fine/arch-labelled.png --outdir .scratch/22-visibility-fragmentation/evidence/check-labelled --pane 1500",
      "result": "passed",
      "summary": "Reference-free report lists check-labelled/draft.png."
    },
    {
      "command": "Final sha256sum scripts/vector_visibility.py scripts/tests/test_vector_visibility.py; git status --short; git diff --cached --name-only",
      "result": "passed",
      "summary": "Historical hashes unchanged; HEAD 24693d4; pre-existing staged .gitmodules/vendor preserved; no task files staged."
    }
  ],
  "validationOutput": [
    "Fine parent geometry: source 0, canonical 44, candidate 0 nonmatching pixels across 8495 safe interior samples.",
    "All 44 canonical deviation locations checked against projected internal edges; reported distances are below 0.42 px.",
    "Current fine mesh: 29464 emitted fragments, 20472 zero-area, 8992 serialized paths; candidate: 9681 fragments, 5151 zero-area, 4530 paths.",
    "Candidate raster repeat SHA-256 equals initial candidate PNG SHA-256: 651ee391dc735918438000f344cb391e795499e05a718ec3617bb6ce32954f93."
  ],
  "residualRisks": [
    "Independent reviewer must resolve the material oblique ring-area change: historical expectation 0.7968 +/- 0.01, candidate 0.7559248.",
    "Candidate has not been integrated; full support matrix, fresh visual review, learner, and S1a acceptance remain undone.",
    "Existing .gitmodules and vendor/huashu-art-motion are pre-existing staged user work and remain staged untouched."
  ],
  "noStagedFiles": false,
  "diffSummary": "Scratch-only positive-area projected-triangle intersection candidate and computed geometry/Chromium safety evidence; no canonical implementation changes.",
  "reviewFindings": [
    "open: scripts/tests/test_vector_visibility.py test_same_whole_strip_updates_visibility_in_two_cameras - candidate changes the yaw-55 visible-area fraction materially; needs independent parent review.",
    "no independent review performed by this implementation worker; review gate remains required."
  ],
  "manualNotes": "No files staged by this worker. The staged paths shown by git are inherited user state and were preserved. No canonical changes, commit, install, full matrix, learner, or art verdict."
}
```
