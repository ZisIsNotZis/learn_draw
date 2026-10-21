// Wave 14, second round, package G2 — r1a-b-hand-r1-pad (one writer, one deliverable).
//
// Contract: .scratch/35-r1-articulated-study/work/wave14-contracts.md § "Second round",
//           with owner resolution R3 (the pads-outboard means is retired; the end is legibility).
// Follows: package G, returned at 22/23 (`36c02d7`) with one honest construction failure it named.
//
// contract.area       .scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1/   (one writer; no other area)
// contract.acceptance the items in the task text below, each with its command
// contract.spend      idle-compute (local CPU only) + time; no exclusive resource
// contract.clock      20 min wall clock, hard stop; launch timeoutMs 1 200 000
const TASK = [
  "You are one child of a delegation tree; you have no dialogue with the user and you report to the parent only. Your final message IS the report.",
  "Repo root: /home/z/vibe/learn_draw. Work there and nowhere else.",
  "",
  "ROLE: single writer, one deliverable, own directory: .scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1/ . You do not touch .scratch/35-r1-articulated-study/evidence/A-bow-study-v2/ (another writer is there right now), not evidence/B-hand-study-v1/ (frozen), not scripts/, not docs/, not STATUS.md, not work/. Never read work/holdout-brief.sealed.md.",
  "",
  "COMMIT WITH EXPLICIT PATHS: `git add .scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1 && git commit -m '...'`. Never `git add -A`, `git add .`, `git commit -a`, and never checkout/reset anything outside your directory: a second writer is in the same checkout. Do not push, do not switch branch.",
  "",
  "READ FIRST: (1) /home/z/vibe/AGENTS.md (the union view; the brief's earlier pointer /home/z/vibe/agent-policy/AGENTS.md does not exist); (2) repo AGENTS.md rules 5, 6, 7; (3) .scratch/35-r1-articulated-study/work/wave14-contracts.md § Package G, § Second round and resolution R3; (4) your own README.md and tests/negative-control-output.txt.",
  "",
  "WHERE THE PACKAGE IS. 22 of 23 tests pass. The bundle is regenerated and routes inside this package. The one failure is construction, not measurement, and the previous writer measured it and left two reverted attempts behind rather than a half-landed fix:",
  "  FAIL TestContact::test_every_digit_rests_on_the_underside_and_none_penetrates_it — 'middle hovers 10.6 px below the underside instead of resting on it'.",
  "  Cause: source/contact.py::finger offsets the pad's centre along the surface normal by `r_tip + clearance`, but the digit arrives steeply, so the tube's cross-section — perpendicular to the digit's tangent, not to the plate — stands off by an extra `r_tip * (1 - sin theta)`. Measured stand-off: index 3.60, middle 10.65, ring 10.82, little 4.41, thumb 5.05 px.",
  "  Its own suggestion: make the pad's axis run parallel to the surface it rests on (offset both pad knots by the same amount, taper the radius to r_tip by the approach station).",
  "",
  "YOUR ONE DELIVERABLE: every digit's pad rests on the underside within the same bounds the test already uses (>= -1.0 px, < clearance + 4.0 px), the suite is 23/23, and the package is rebuilt and self-consistent over the new revision (artwork.svg, artwork.png, check/ bundle, manifest, README numbers).",
  "",
  "OWNER RESOLUTION R3, so you do not chase an impossible target. The previous run proved R2's 'pads extend outboard visible past the plate's silhouette' is unreachable under an unbroken near rim: the lowest a resting pad can reach is y ~ 154.5 + 2*r_tip + 1.5 px, always above the plate's 209.1 px lower contour for every tip radius the taper law allows. R3 therefore retires the *means* and keeps the *end*: the digits are legible because their shafts and knuckles read against the background below the plate's silhouette (which the delivered revision now does — digits span y 71 to 382), not because the pads clear the rim. Do not move the rim, the camera or the framing to expose the pads.",
  "",
  "HARD RULES. No assertion added, removed or weakened; the three contact tests keep the bounds they already have after the R1 re-target. If the parallel-axis fix over-corrects into penetration (the previous run measured -7.4 px on one attempt) say so with the number and stop rather than leaving a wrong pose committed. Geometry computed: radii, stations, reaches and fractions in source/scene.py, contact.py, digits.py — no typed coordinates. No art verdict: do not say the hand looks like a hand, is readable, finished, final, best or done.",
  "",
  "REQUIRED ACCEPTANCE, each with its command and output:",
  "1. `cd .scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1 && PYTHONDONTWRITEBYTECODE=1 ../../../../.venv/bin/python -m unittest discover -s tests -t .` prints OK for 23 tests; quote the per-digit stand-off line it prints (all digits inside the bounds).",
  "2. The separation numbers still printed and still inside their limits: distal halves >= 0.30, roots <= 0.10; quote them verbatim.",
  "3. `../../../../.venv/bin/python source/build.py` then `cmp` against artwork.svg; `../../../../scripts/draw render artwork.svg -o /tmp/b2.png` then `cmp` against artwork.png — the delivered pair is a fresh build and render, byte-identical.",
  "4. Bundle regenerated from this revision with `../../../../scripts/draw check artwork.svg --outdir check`: report.txt line 1 is this revision's 1:1 image, every path in it resolves inside this package, and check/draft.png equals artwork.png (`md5sum` both).",
  "5. `../../../../.venv/bin/python source/manifest.py --check` and `sha256sum -c manifest.sha256` verify 100% over the real file set.",
  "6. README.md: the finding->repair table updated (B1 done; the pad stand-off named with its before -> after per digit; B2 the well's spoke fan still NOT FIXED and named as the next stage; B3's missing signed thumb-opposition test still named absent; N1-N5 untouched), and the numbers it quotes are the ones the suite prints.",
  "",
  "OUT OF SCOPE, do not start: the well's spoke fan/shading, N1-N5, and the four absent tests — package I, next wave.",
  "",
  "ORDER OF WORK so the package is true at any cut: fix, run the suite, rebuild artwork + bundle + manifest, update the README table, commit. `git status` for your directory clean at the end.",
  "",
  "BUDGET: 20 minutes wall clock, hard stop, no new work after minute 17. idle-compute + time: local CPU, no network write, no paid API, no GPU. If you are stopped, leave a self-consistent package and report the number reached.",
  "",
  "REPORT: the fix and its numbers per digit, the suite's pass/fail list, the commands and their results, what you did not verify, and where the next writer starts. The next writer is a fresh image reviewer, so the revision you leave must be the one the bundle describes.",
].join("\n");

// returns runs.run("r1a-b-hand-r1-pad", {
//   agent: "worker",
//   task: TASK,
//   label: "R1a B: pads resting on the underside, and a rebuilt package",
//   model: "deepseek/deepseek-flash:high",
//   worktree: false,
//   async: true,
// });
