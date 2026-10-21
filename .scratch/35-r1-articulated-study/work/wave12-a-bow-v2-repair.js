// Wave 12, package A — A-bow-study-v2 repair (resume the dead run's partial restart).
//
// Contract: .scratch/35-r1-articulated-study/work/wave12-contracts.md § Package A
//           .scratch/35-r1-articulated-study/work/r1a-object-study-contracts.md § A-bow-study-v1
//
// contract.area       .scratch/35-r1-articulated-study/evidence/A-bow-study-v2/   (one writer)
// contract.acceptance the eight command-proved items in the task text below
// contract.spend      idle-compute (local CPU only) + time; no exclusive resource, so no reservation
// contract.clock      75 min wall clock, hard stop, checkpoint at 65
//
// Launched in this session through the `subagent` tool as a fresh background child whose task text is
// exactly TASK below. This file is the durable record of the payload and is re-dispatchable through
// `runs.run` unchanged if the harness kills the run.
const TASK = [
  "You are one child of a delegation tree; you have no dialogue with the user and you report to the parent only. Your final message IS the report.",
  "Repo root: /home/z/vibe/learn_draw, at commit 5e12d36 or later on master. Work there and nowhere else.",
  "",
  "ROLE: the A-bow-study-v2 writer, single writer, own directory. You own exactly .scratch/35-r1-articulated-study/evidence/A-bow-study-v2/ . You do not touch any other evidence directory (in particular not B-hand-study-v1, which another child is reading right now), not scripts/, not docs/, not STATUS.md, not work/wave-log.md, not evidence/acceptance-ledger.md, and you do not read work/holdout-brief.sealed.md at all.",
  "",
  "READ FIRST, in this order: (1) /home/z/vibe/agent-policy/AGENTS.md — the law you work under: land before reporting, one writer per area, no trash, absence recorded as absence; (2) AGENTS.md at the repo root — the eight invariant rules, especially rule 4 (metrics are signal, never target), rule 5 (geometry is computed, never eyeballed, ~4 hand-typed coordinates per shape), rule 6 (the engine never sees the target), rule 7 (never judge your own render); (3) .scratch/35-r1-articulated-study/work/r1a-object-study-contracts.md § A-bow-study-v1 — the binding contract; (4) .scratch/35-r1-articulated-study/evidence/acceptance-ledger.md § 'R1a — object study: A-bow-study-v1' — the independent image review's six named defects, which is the only record of that review.",
  "",
  "WHAT YOU INHERIT. A-bow-study-v2 is a dead run's partial restart. source/parts/bow.py already carries the r2 turn repair (R_FOLD/R_WRAP/H_FOLD, knot at KNOT_X=553, loop limbs brought back over each other); source/build.py, source/ribbon.py, source/manifest.py and the four test files are byte-identical to v1's. README.md is byte-identical to v1's (both sha256 46e772ff…), so it describes a drawing v2 no longer makes. artwork.svg and artwork.png exist and are the committed source's own output. There is no check/ bundle, no manifest, no negative control, and the inherited suite fails 8 of 17. Measured in place for this dispatch: 13 audited self-crossings with |dz| 0.7–15.8 px against a 16 px cloth thickness and two rear edges drawn through; 4 of 1240 triangles against their own winding; width 77.7–301.6 px (ratio 3.88 against the 4.0 test floor); knot band 113.3–113.5 px vs loops 159.6 px; one isolated width jump of 9.03 px against a 3.0 limit.",
  "",
  "WHAT THIS PACKAGE IS. Retune the turn geometry until the inherited law holds with the inherited tests unmodified; add a test for each of the six defects the v1 image review named, each demonstrated to fail when v1's behaviour is restored; replace the stale README with one that describes what v2 actually emits; emit the check/ bundle, manifest.json, manifest.sha256 and the negative control. The parent has already decided resume-not-restart: do not throw the construction away, and do not start a third structural approach.",
  "",
  "THE SIX DEFECTS (from the v1 image review, via the ledger). (1) two background islands enclosed inside the lobes where the reference's lobes are solid cloth; (2) no readable knot — the mass is widest where it must pinch, and the knot sits at 0.63 of the width where the reference measures 0.70; (3) a beak-like spike at top centre, about x 0.56, y 0.19; (4) a doubled/hatched edge at lower right, about x 0.73-0.82; (5) the lower tail reads as a stem on a stand; (6) nearly all interior strokes free-terminate, and a single flat fill leaves overlap order unreadable. The reviewer's coordinates are approximations, not measurements (P7): re-derive the true location from the emitted geometry and say in the README where each defect actually was.",
  "",
  "HARD RULES. The four inherited test files keep every assertion they already make; adding tests is expected, weakening a threshold is forbidden. If a test is wrong or cannot be satisfied by a truthful drawing, that is a contract report to the parent, not an edit. Geometry is computed, never eyeballed: the same four-hand-typed-coordinate budget as v1 holds. No shape may be nudged to make a number pass: the number proves the turn is right, it is not the goal. No art verdict: you do not say the bow is good, readable or finished, and you never use the words final, best or done about the image. If a defect cannot be closed by the construction you have, say which one, keep the drawing truthful and report it instead of hiding it.",
  "",
  "REQUIRED ACCEPTANCE — each item a command with its output in your report:",
  "1. `cd .scratch/35-r1-articulated-study/evidence/A-bow-study-v2 && PYTHONDONTWRITEBYTECODE=1 ../../../../.venv/bin/python -m unittest discover -s tests -t .` prints OK, and `git diff --stat <v1-tests> -- tests/` (or an equivalent line-by-line check) shows only additions to the four inherited files.",
  "2. Six new tests, one per named defect, each with a negative control that restores v1's behaviour and FAILS — the way `tests/negative-control-output.txt` in A-bow-study-v1 demonstrates its crossing-break mutation. All control outputs in tests/negative-control-output.txt.",
  "3. `../../../../.venv/bin/python source/build.py --out /tmp/a2.svg && cmp /tmp/a2.svg artwork.svg` — byte-identical from committed source.",
  "4. The delivered PNG equals a fresh render of the delivered SVG through the documented path (`../../../../scripts/draw render …`), compared with cmp.",
  "5. `../../../../.venv/bin/python source/manifest.py --check` and `sha256sum -c manifest.sha256` both verify 100% over the real file set, and `check/report.txt` lists the 1:1 image first.",
  "6. README.md replaced: its sha256 differs from 46e772ff…, it names v2, and every table in it (route, width field, depth separation, crease endpoints) carries the numbers the current source actually emits, with the measured-target-vs-author-choice distinction v1 used and an explicit list of what you did not verify. State the art verdict as absent, not as pending.",
  "7. The package is self-consistent at every commit: commit after the geometry holds, after the tests land, and after the bundle+manifest+README land. No uncommitted work at the end, `git status` clean.",
  "8. Final report: what changed, the before/after number for each of the eight failing tests, the six defect tests with their control results, and where the next writer starts.",
  "",
  "BUDGET: 75 minutes wall clock, hard stop; you will be asked to checkpoint at 65 and start no new work then. Spend class idle-compute and time — no network write, no paid API, no GPU. Commit what is reproducible if you are stopped, and report what remains rather than leaving a package that is half-true.",
].join("\n");

// returns runs.run("r1a-a-bow-v2-repair", {
//   agent: "worker",
//   task: TASK,
//   label: "R1a A: repair A-bow-study-v2 to reviewable",
//   model: "deepseek/deepseek-flash:high",
//   worktree: false,
//   async: true,
// });
