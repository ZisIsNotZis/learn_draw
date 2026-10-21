// Wave 14, second round, package F2 — r1a-a-bow-v2-tail (one writer, one deliverable).
//
// Contract: .scratch/35-r1-articulated-study/work/wave14-contracts.md § "Second round"
// Follows: package F, returned clean at 17/17 (`cddd8b2`) with one residual defect it named itself.
//
// contract.area       .scratch/35-r1-articulated-study/evidence/A-bow-study-v2/   (one writer; no other area)
// contract.acceptance the items in the task text below, each with its command
// contract.spend      idle-compute (local CPU only) + time; no exclusive resource
// contract.clock      20 min wall clock, hard stop; launch timeoutMs 1 200 000
const TASK = [
  "You are one child of a delegation tree; you have no dialogue with the user and you report to the parent only. Your final message IS the report.",
  "Repo root: /home/z/vibe/learn_draw. Work there and nowhere else.",
  "",
  "ROLE: single writer, one deliverable, own directory: .scratch/35-r1-articulated-study/evidence/A-bow-study-v2/ . You do not touch .scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1/ (another writer is there right now), not evidence/A-bow-study-v1/, not scripts/, not docs/, not STATUS.md, not work/. Never read work/holdout-brief.sealed.md.",
  "",
  "COMMIT WITH EXPLICIT PATHS: `git add .scratch/35-r1-articulated-study/evidence/A-bow-study-v2 && git commit -m '...'`. Never `git add -A`, `git add .`, `git commit -a`, and never checkout/reset anything outside your directory: a second writer is in the same checkout and those would sweep or destroy its files. Do not push, do not switch branch.",
  "",
  "READ FIRST: (1) /home/z/vibe/AGENTS.md (the union view; the brief's earlier pointer /home/z/vibe/agent-policy/AGENTS.md does not exist); (2) repo AGENTS.md rules 4 and 5; (3) .scratch/35-r1-articulated-study/work/wave14-contracts.md § Package F and § Second round; (4) your own README.md § 'What I did not verify', which names exactly the defect you are here to close.",
  "",
  "WHERE THE PACKAGE IS. The suite is green (17/17) and the deliverable is truthful. The previous writer found and named one residual defect it did not fix, because fixing it changes the silhouette:",
  "  source/parts/bow.py::_knot_at returns 1.0 for `k >= len(parts) - 1`, so for the last route part every requested fraction collapses to u = 1.0. The lower tail's three knots (P(8,0.12), P(8,0.45), (1.0,122)) therefore all sit at the strip's end: the tail tapers 92 -> 32 instead of 'crushed, then broad', and the emitted width series ends h[619]=32.0, h[620]=122.0 — a 90 half-width px step that the continuity test cannot see because it samples station starts and stops at 619.",
  "",
  "YOUR ONE DELIVERABLE: that off-by-one is gone, the tail's width series is what the source says it is, and the package is rebuilt and self-consistent over the new revision (artwork.svg, artwork.png, check/ bundle, manifest, README numbers). Verify it is really gone by measuring the emitted series at the last stations and printing the numbers — not by reading the code.",
  "",
  "HARD RULES. Inherited test files keep every assertion: no test added, removed or weakened. If the corrected tail breaks a law (width continuity, knot waist, crossing depth break, winding), fix the geometry inside the construction and report the numbers; do not restore the off-by-one to make a test pass, and do not lower a threshold. Geometry stays computed (~4 hand-typed coordinates per shape). No art verdict: do not say the bow is good, readable, finished, final, best or done — and do not change the tail's shape to look nicer, only so that it is the shape the source declares.",
  "",
  "REQUIRED ACCEPTANCE, each with its command and output:",
  "1. `cd .scratch/35-r1-articulated-study/evidence/A-bow-study-v2 && PYTHONDONTWRITEBYTECODE=1 ../../../../.venv/bin/python -m unittest discover -s tests -t .` prints OK for 17 tests, and the printed width line shows no jump at the last stations (quote the terminal stations' widths).",
  "2. `git diff --stat <your first commit>^ -- tests/` shows nothing touched by you.",
  "3. `../../../../.venv/bin/python source/build.py --out /tmp/a3.svg && cmp /tmp/a3.svg artwork.svg` byte-identical; `../../../../scripts/draw render artwork.svg -o /tmp/a3.png && cmp /tmp/a3.png artwork.png` byte-identical.",
  "4. The bundle regenerated from THIS revision: `../../../../scripts/draw check artwork.svg --outdir check` — report.txt's line 1 names the 1:1 image, its paths resolve inside this package, and its draft.png equals artwork.png (`md5sum` both).",
  "5. `../../../../.venv/bin/python source/manifest.py --check` and `sha256sum -c manifest.sha256` verify 100% over the real file set.",
  "6. README.md § State and § 'What I did not verify' updated to the new numbers: the off-by-one is named as fixed with its before -> after width range, and the residual list no longer claims it.",
  "",
  "ORDER OF WORK so the package is true at any cut: fix, run the suite, rebuild artwork and bundle, rewrite the manifest, update the README numbers, commit. `git status` for your directory clean at the end.",
  "",
  "BUDGET: 20 minutes wall clock, hard stop, no new work after minute 17. idle-compute + time: local CPU, no network write, no paid API, no GPU. If you are stopped, leave a self-consistent package and report the number reached.",
  "",
  "REPORT: the cause, the before -> after width range and terminal-station numbers, the commands and their results, what you did not verify, and where the next writer starts. The next writer is a fresh image reviewer, so the revision you leave must be the one the bundle describes.",
].join("\n");

// returns runs.run("r1a-a-bow-v2-tail", {
//   agent: "worker",
//   task: TASK,
//   label: "R1a A: the last route part's off-by-one, and a rebuilt package",
//   model: "deepseek/deepseek-flash:high",
//   worktree: false,
//   async: true,
// });
