// Wave 14, package G — r1a-b-hand-r1-pose (one writer, one deliverable).
//
// Contract: .scratch/35-r1-articulated-study/work/wave14-contracts.md § Package G, and the two owner
//           resolutions R1 (contact test re-targeted to the underside) and R2 (legible pose) above it.
//
// contract.area       .scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1/   (one writer; no other area)
// contract.acceptance the items in the task text below, each with its command
// contract.spend      idle-compute (local CPU only) + time; no exclusive resource, so no reservation
// contract.clock      25 min wall clock, hard stop; launch timeoutMs 1 500 000
//
// Launched in this session through the `subagent` tool as a fresh background child whose task text is
// exactly TASK below. This file is the durable record of the payload.
const TASK = [
  "You are one child of a delegation tree; you have no dialogue with the user and you report to the parent only. Your final message IS the report.",
  "Repo root: /home/z/vibe/learn_draw, at commit d56572f. Work there and nowhere else.",
  "",
  "ROLE: single writer with one deliverable, in your own directory. You own exactly .scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1/ . You do not touch .scratch/35-r1-articulated-study/evidence/A-bow-study-v2/ (another child is writing there right now), not evidence/B-hand-study-v1/ (frozen: it is the revision the failed image review is bound to by hash), not scripts/, not docs/, not STATUS.md, not work/, and you never read work/holdout-brief.sealed.md.",
  "",
  "READ FIRST, in order: (1) /home/z/vibe/agent-policy/AGENTS.md; (2) AGENTS.md at the repo root — rule 5 (geometry is computed, never eyeballed), rule 6 (the engine never sees the target), rule 7 (never judge your own render); (3) .scratch/35-r1-articulated-study/work/wave14-contracts.md § Package G **and its two resolutions R1 and R2 above it** — the parent has already resolved the contract conflict the previous run raised, so do not raise it again, implement R1; (4) your own README.md, which states the finding-by-finding table honestly.",
  "",
  "WHERE THE PACKAGE IS. The previous run moved the hand onto the dish's own emitted underside rings, so the reviewed inversion is gone by construction — and the consequence is that the hand is now hidden: the delivered artwork.png shows one stub below the plate, not five digits. The suite is RED with four failures:",
  "  TestContact::test_every_digit_rests_on_the_band_and_none_penetrates_it  (measures the tip against the rim band's top plane)",
  "  TestContact::test_a_digit_that_lifts_off_the_rim_is_caught             (same surface)",
  "  TestContact::test_the_hand_follows_the_dish                           (perturbs RIM_OUTER/RIM_INNER, which no longer drive the contact)",
  "  TestSeparation::test_the_distal_halves_are_separated                   (index-middle distal gap 0.10 against a 0.30 floor: real cramping, not a stale measurement)",
  "Run: cd .scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1 && PYTHONDONTWRITEBYTECODE=1 ../../../../.venv/bin/python -m unittest discover -s tests -t .",
  "",
  "RESOLUTION R1 — re-target, never weaken. The band-top contact surface is retired because the construction no longer touches it (the owner directed the hand under the plate). Keep the law: a digit's pad rests on the contact surface and does not penetrate it, and a digit that lifts off is caught. Move the three contact tests onto dish.derived_rings()/contact.underside_ring() with the same 1.5 px clearance, keep the lift mutation (clearance + 20 px) failing, and for test_the_hand_follows_the_dish perturb the underside's own drivers (FOOT_RADIUS / AXIS_UNDER_Z) instead of the rim radii. TestSeparation is NOT re-targeted and NO floor is lowered: 0.30 stands and the geometry must meet it.",
  "",
  "RESOLUTION R2 — the legible pose. Under the plate with an unbroken near rim is kept, so any hand surface behind the plate is hidden. Legibility therefore comes from where the hand is not behind the plate: the digit pads extend outboard past the plate's silhouette and read against the background, with only their inner edges cut by the near rim, and the palm's mass drops below and behind the plate's near contour. Do not move the rim to expose the hand, do not raise or tilt the camera, do not change the framing (900x700 and the study's viewpoint are fixed).",
  "",
  "HARD RULES. No assertion added, removed or weakened anywhere except the three contact tests re-targeted exactly as R1 says — and their diff must appear in your report. Geometry is computed, never eyeballed: pose values are station angles, reaches and radii in scene.py, not coordinates. No art verdict: you do not say the hand looks like a hand, is readable, finished, final, best or done. If the numbers say the pose is legible and you can see it is not, say exactly that and report it; do not paper over it.",
  "",
  "REQUIRED ACCEPTANCE — each item a command with its output in your report:",
  "1. **The evidence is truthful first** (do this before any geometry): check/report.txt and check/*.png are stale and misrouted — report.txt names .scratch/35-r1-articulated-study/evidence/B-hand-study-v1/ and check/draft.png is byte-identical to v1's artwork.png. Regenerate the bundle from THIS revision through the documented path (../../../../scripts/draw check with no --ref, or the package's own documented invocation) so that report.txt line 1 names a 1:1 image inside B-hand-study-v1-r1/ and the image is this revision's render.",
  "2. The pose pass of R2 is landed and the suite prints OK for all 23 inherited tests, with the three contact tests re-targeted per R1 (diff in the report) and their lift mutation still failing in tests/negative-control-output.txt.",
  "3. The suite's own printed separation numbers: index-middle and every recorded pair's distal halves ≥ 0.30, roots ≤ 0.10, quoted verbatim.",
  "4. `../../../../.venv/bin/python source/build.py` then `cmp` against artwork.svg, and `../../../../scripts/draw render artwork.svg -o /tmp/b1.png` then `cmp` against artwork.png — the delivered pair is a fresh build and a fresh render, byte-identical.",
  "5. `../../../../.venv/bin/python source/manifest.py --check` and `sha256sum -c manifest.sha256` verify 100% over the real file set, with the new bundle and README inside it.",
  "6. README.md's finding→repair table updated to the true state: B1 (occlusion) done and legible — say whether the pads now read outboard; B2 (the well's spoke fan) still NOT FIXED and named as the next stage's; B3 partly done with the missing signed thumb-opposition test named as absent; N1–N5 untouched. Art verdict still stated as absent.",
  "",
  "OUT OF SCOPE THIS STAGE, do not start them: the well's spoke fan and shading, review items N1–N5, and the absent new tests (near-rim occlusion audit, signed thumb opposition, digit variation, well shading) — those are package I, next wave.",
  "",
  "ORDER OF WORK so the package is true at any cut: (1) regenerate the bundle and fix report.txt, verify, commit; (2) the R2 pose pass + the R1 re-targeted tests + the separation floor, run the suite, commit; (3) rebuild artwork + bundle + manifest + README table, commit. `git status` clean at the end.",
  "",
  "BUDGET: 25 minutes wall clock, hard stop, and you start no new work after minute 22. Spend class idle-compute + time: local CPU, no network write, no paid API, no GPU. If you are stopped, the bundle regeneration of step 1 is the one item that must never be left half-done.",
  "",
  "REPORT: what you changed (pose parameters and their before → after), the suite's pass/fail list and separation numbers, the commands you ran, what you did not verify, and where the next writer starts.",
].join("\n");

// returns runs.run("r1a-b-hand-r1-pose", {
//   agent: "worker",
//   task: TASK,
//   label: "R1a B: legible pose and truthful evidence on B-hand-study-v1-r1",
//   model: "deepseek/deepseek-flash:high",
//   worktree: false,
//   async: true,
// });
