// Wave 14, package F — r1a-a-bow-v2-width-law (one writer, one deliverable).
//
// Contract: .scratch/35-r1-articulated-study/work/wave14-contracts.md § Package F
//           .scratch/35-r1-articulated-study/work/r1a-object-study-contracts.md § A-bow-study-v1
//
// contract.area       .scratch/35-r1-articulated-study/evidence/A-bow-study-v2/   (one writer; no other area)
// contract.acceptance the six command-proved items in the task text below
// contract.spend      idle-compute (local CPU only) + time; no exclusive resource, so no reservation
// contract.clock      25 min wall clock, hard stop; launch timeoutMs 1 500 000
//
// Launched in this session through the `subagent` tool as a fresh background child whose task text is
// exactly TASK below. This file is the durable record of the payload.
const TASK = [
  "You are one child of a delegation tree; you have no dialogue with the user and you report to the parent only. Your final message IS the report.",
  "Repo root: /home/z/vibe/learn_draw, at commit d56572f. Work there and nowhere else.",
  "",
  "ROLE: single writer with one deliverable, in your own directory. You own exactly .scratch/35-r1-articulated-study/evidence/A-bow-study-v2/ . You do not touch .scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1/ (another child is writing there right now), not evidence/A-bow-study-v1/, not scripts/, not docs/, not STATUS.md, not work/, and you never read work/holdout-brief.sealed.md.",
  "",
  "READ FIRST, in order: (1) /home/z/vibe/agent-policy/AGENTS.md; (2) AGENTS.md at the repo root — especially rule 4 (metrics are signal, never target) and rule 5 (geometry is computed, never eyeballed); (3) .scratch/35-r1-articulated-study/work/wave14-contracts.md § Package F — your contract; (4) the package's own README.md § State, which already names what is open.",
  "",
  "WHERE THE PACKAGE IS. A previous writer run took it to 16 of 17 inherited tests. One fails:",
  "  FAIL: tests.test_ribbon_continuity.TestWidthIsOneField.test_width_is_continuous_along_the_emitted_strip",
  "  'an isolated width jump of 3.58 px at one station left the neighbour steps unchanged: that is a piece boundary'",
  "Run: cd .scratch/35-r1-articulated-study/evidence/A-bow-study-v2 && PYTHONDONTWRITEBYTECODE=1 ../../../../.venv/bin/python -m unittest discover -s tests -t .",
  "The suite prints the emitted numbers: width 62.1..300.0 px over 620 stations, steepest station 19.19 px (6.4% of the widest), worst isolation 3.58 px; knot band median 93.9 px with narrowest 64.0, loops median 117.7; 17 audited crossings, 0 closer than one cloth thickness, mutation 17/17; 1240 triangles, 0 disagreeing with their own winding.",
  "",
  "YOUR ONE DELIVERABLE: the width law holds — no isolated width jump of 3.0 px or more anywhere on the emitted strip, with the inherited test files unmodified. Read the failing test and its helper to see exactly what it measures (station spacing, neighbour steps, the isolation definition) and find the piece boundary in the geometry that produces the 3.58 px step. Fix it in the turn/width construction, not at the test.",
  "",
  "HARD RULES. No assertion is added to, removed from or weakened in the four inherited test files. If the law cannot be satisfied without changing the routed turn count or the loop count, stop and report the measurement and the reason — a truthful RED with a named obstruction is a valid report and is better than a forced number. No shape may be nudged to make the number pass: the number proves the turn is right, it is not the goal (rule 4). Geometry stays computed: the same four-hand-typed-coordinate budget as v1 holds, and no coordinate may be typed to move a station. No art verdict: do not say the bow is good, readable, finished, final, best or done, and do not change the drawing to make it look better — this package changes one geometric law, not the art.",
  "",
  "REQUIRED ACCEPTANCE — each item a command with its output in your report:",
  "1. The suite prints OK for all 17 tests (or, if you are stopped, the exact pass/fail list plus the number you reached).",
  "2. `git diff --stat HEAD -- tests/` shows nothing, or, if you added a test, only additions; the four inherited files keep every assertion.",
  "3. `../../../../.venv/bin/python source/build.py --out /tmp/a2.svg && cmp /tmp/a2.svg artwork.svg` byte-identical.",
  "4. `../../../../scripts/draw render artwork.svg -o /tmp/a2.png && cmp /tmp/a2.png artwork.png` byte-identical, and the delivered artwork.png is that render.",
  "5. `../../../../.venv/bin/python source/manifest.py --check` and `sha256sum -c manifest.sha256` verify 100% over the real file set; `check/report.txt` line 1 still lists the 1:1 image at this revision's path (regenerate the bundle with `scripts/draw check` if the SVG changed, since the bundle must describe the revision that exists).",
  "6. README.md § State updated to the numbers the source now emits (before → after for the width jump and the width range), the art verdict still stated as absent.",
  "",
  "ORDER OF WORK so the package is true at any cut: read, find the cause, fix, run the suite, rebuild the render and the bundle, update the manifest, update the README's numbers, commit. Commit after the geometry holds and again after the bundle+manifest+README land; no uncommitted work at the end and `git status` clean.",
  "",
  "BUDGET: 25 minutes wall clock, hard stop, and you start no new work after minute 22. Spend class idle-compute + time: local CPU, no network write, no paid API, no GPU. Commit what is reproducible and self-consistent, and report what remains rather than leaving a package that is half-true.",
  "",
  "REPORT: what the cause of the jump was, the before → after numbers, which commands you ran with their results, what you did not verify, and where the next writer starts.",
].join("\n");

// returns runs.run("r1a-a-bow-v2-width-law", {
//   agent: "worker",
//   task: TASK,
//   label: "R1a A: close the width-continuity law on A-bow-study-v2",
//   model: "deepseek/deepseek-flash:high",
//   worktree: false,
//   async: true,
// });
