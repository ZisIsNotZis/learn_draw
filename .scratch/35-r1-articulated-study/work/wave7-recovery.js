// Wave 7 — recovery after three runs were reaped mid-flight by run-directory cleanup.
const COMMON = [
  "You are one child of a delegation tree; you have no dialogue with the user and you report to the parent only.",
  "INFRASTRUCTURE WARNING (observed this session): three sibling runs were killed mid-flight at the same instant and their run directories and config were deleted by run-directory cleanup, not by their own logic. Progress that is not committed is lost. Therefore: commit your work to your own git branch as small checkpoints every ~20 minutes (`git add -A && git commit -m \"wip: ...\"` inside the directory you own), and do not leave long stretches of uncommitted work. Never commit outside your own branch, never touch other directories, never rewrite history.",
  "Repo root: /home/z/vibe/learn_draw. Read AGENTS.md first (binding invariant rules), then docs/drawing/spatial-model.md, docs/drawing/principles.md P31-P33, .scratch/35-r1-articulated-study/work/m1a-m1b-plan.md.",
  "Environment: .venv exists (cv2/numpy/pillow/pyyaml). Run tools through scripts/draw or .venv/bin/python. check bundles now always carry a 1:1 `draft-fullres.png` and list it first — that is the image a reviewer judges.",
  "Never award an art verdict for your own output; a fresh independent reviewer decides art. Metrics are a breakage alarm, never a target.",
].join("\n");

const A_RESUME = [
  COMMON,
  "",
  "ROLE: A-repair resume writer. Your cwd is the existing worktree at ~/vibe/worktrees/learn_draw/pi-worktree-5e7cbf95-af4e-4a89-9df8-dda2840a95d4-s0-0 and you own the directory .scratch/35-r1-articulated-study/evidence/A-cloth-v6/ inside it. Everything else is read-only (including evidence/A-cloth-v5/, scripts/, docs/, STATUS.md, all B artefacts, and the sealed material, which you must not read).",
  "",
  "WHAT HAPPENED: a previous writer built this package for about 100 minutes and was then killed by infrastructure. Its work-checkpoint.md claims everything is complete and hash-verified. THAT CLAIM IS FALSE AT HEAD. The parent verified: `sha256sum -c manifest.sha256` reports 20 OK, the whole `check-a/` bundle is missing (7 listed files absent), and several `source/*.py` files fail their recorded hashes because the source was edited after the manifest was written. Last activity was 11:59 local, mid-run.",
  "",
  "YOUR JOB IS TO MAKE THIS PACKAGE TRUE AGAIN, not to write a new drawing from scratch. Reuse the existing source, tests and artwork.",
  "",
  "1. Establish the actual current state: run the test suite, run the build, regenerate the artwork, run `scripts/draw check` with `--outdir` inside the package (the reference is the 400x480 crop already in ref/crop-400x480.png; do not read image.jpg for geometry), rewrite manifest.json + manifest.sha256 over the real file set, and verify with sha256sum -c until it is fully green. Report the commands and the counts.",
  "2. Prove the delivered artwork is reproducible from the delivered source: build twice into two temporary paths and compare bytes; report whether they are identical.",
  "3. Re-read the defects D1-D12 in .scratch/35-r1-articulated-study/work/wave3-a-repair.js (the dispatch that started this work) and write repair-log.md stating, per defect, what the current source actually does and whether it is fixed, partially fixed, or not fixed. Verify each by inspecting the code, not by trusting work-checkpoint.md.",
  "4. Write README.md so that every mechanism claim is true of the code at this revision — in particular the hair: if the sheet passes a real twist function and flips all columns together, say so; if the mint region is still a self-overlap artefact at the route's hairpin, say THAT and do not call it a twisting normal. Same rule for the seam contract's attachment clause and for the authoring-budget claim (the count must be the real number of hand-typed coordinates, declared equal to actual).",
  "5. Keep the verified structural properties: one continuous bow strip with one constant width and depth-driven lobe overlap; two whole sleeves with whole cuffs and depth-produced occlusion; authored crease marks; seam contract with its negative controls; no manual clipping.",
  "",
  "ACCEPTANCE (all mechanical, prove each with a command): test suite passes; manifest verifies 100%; the check bundle exists with a 1:1 image; two builds are byte-identical; repair-log.md dispositions D1-D12; README claims verified against code.",
  "Do not attempt to fix art-quality defects (D1-D6) by changing the drawing if they are not already addressed — record their true status in repair-log.md instead. Art is judged elsewhere; a false claim of fix is worse than an honest 'not fixed'.",
  "BUDGET: 60 minutes wall clock; checkpoint commit every ~20 minutes; hard stop at 60. Report: commands with results, per-defect disposition, unverified items, and any blocker.",
].join("\n");

const B_REPAIR = [
  COMMON,
  "",
  "ROLE: B-repair writer for M1b repair round 1. You own exactly one new directory: .scratch/35-r1-articulated-study/evidence/B-hand-v2-r1/ . Read-only for you: everything else, including evidence/B-hand-v2/ (copy it in as your starting point; never edit it), evidence/B-caption-corrected-v1/ (its caption policy still binds), scripts/, docs/, STATUS.md, all A artefacts, and the sealed material (do not read it at all).",
  "",
  "STARTING POINT: copy .scratch/35-r1-articulated-study/evidence/B-hand-v2/ into your directory. It already has real hand construction (palm + four tapered finger tubes + thumb), derived contact, 12 passing tests, a three-panel sheet and a manifest. Keep those properties; repair what an independent image reviewer and the parent saw at 1:1.",
  "",
  "DEFECTS YOU MUST FIX (from a fresh independent image review at 1:1, confirmed by the parent):",
  "E1. The hand does not read as a hand in any panel: four thin fingers splay upward in front of the dish like rake tines over a flat palm slab, and the thumb adds a fifth spike. Nothing curls or grips. FIX: pose a supporting open hand — palm's whole surface under the dish, fingers lying along/curving up to meet the far rim, thumb pressing the near side — and add palm structure (palm width, knuckle line, wrist narrowing) so the palm is not a flat slab. Fingers must be thicker, shorter and bent, not tines.",
  "E2. The dish does not read as resting on the hand: it sits behind and above the fingertips. FIX: the contact must be visible — the dish's underside meets palm/fingers, with the dish in front of some digits and behind others, and the contact must not be hidden behind the hand.",
  "E3. The arm reads as three sticks: flat parallelogram upper arm, vertical strip forearm, then a hand, with no shoulder and no readable elbow. FIX: one continuous arm with a shoulder cap joining the torso, an elbow that reads as a bend, and a forearm tapering into a wrist — parameter-driven, not a traced contour table.",
  "E4. The arm's skin tone and the warm held object merge. FIX: separate them by value and/or hue while keeping the palette coherent; state the relation in the README.",
  "E5. The control panel changes several things at once. FIX: the control must differ from the baseline in exactly one respect — the dish's displacement — with hand, arm, torso, palette and framing identical. Prove it mechanically by comparing emitted outlines and supports between panels.",
  "E6. Residual toy artifacts (two-dot face, hexagonal head, flat fills). FIX within B's scope: B is an original illustration, so give head and torso enough construction to read as a person (jaw/cheek boundary, neck, garment edge) without claiming a face you cannot draw.",
  "",
  "MUST NOT REGRESS: six separate hand parts each with its own anchors and support, posed individually; contact derived from the dish's own contour; published captions stay truthful (nothing claims a visibly identifiable thumb bracing the rim unless the image shows it); no manual visibility cuts; manifest of every source and output file.",
  "",
  "REQUIRED VERIFICATION (run it, record exact commands and outputs): full test suite passes with a count; a grip test where each digit's contact lies on the dish rim/underside within a stated tolerance and is derived from the dish geometry; a palm-support test that the dish's underside contact lies inside the palm's outline region (or the digit contact band) and the dish does not float behind the digit tips; a single-variable control test proving hand and arm outlines are identical between baseline and control; a dead-code/reachability check; manifest verifies; `scripts/draw check` with `--outdir` inside the package, with the bundle's 1:1 `draft-fullres.png` as the review image.",
  "",
  "DELIVERABLES in .scratch/35-r1-articulated-study/evidence/B-hand-v2-r1/: source/, tests/, rendered/ (sheet + per-panel PNGs at 1:1), check/, manifest.json, manifest.sha256, README.md (construction vocabulary; geometric consequence vs author hypothesis; colour relation; exact commands; unverified list), repair-log.md mapping E1-E6 to changed or not.",
  "BUDGET: 120 minutes wall clock; checkpoint commit every ~20 minutes; hard stop at 120; two hypotheses per defect. Stop and report rather than faking progress if a defect cannot be fixed in scope or a check cannot run.",
  "REPORT BACK: file list with hashes, per-defect disposition, commands and results, unverified items, and anything the parent must decide.",
].join("\n");

const B_REVIEW = [
  "You are a fresh independent reviewer for one candidate package. You did not write it. You have execution tools and must use them; nothing may be reported as passing without the command that produced it.",
  "Repo root: /home/z/vibe/learn_draw. Use scripts/draw or .venv/bin/python; the venv exists.",
  "PACKAGE: /home/z/vibe/learn_draw/.scratch/35-r1-articulated-study/evidence/B-hand-v2/ (README.md, source/, tests/, rendered/, check/, manifest.json, manifest.sha256). Judge this committed revision, not any uncommitted edit.",
  "AUTHORITATIVE INPUTS: AGENTS.md, docs/drawing/spatial-model.md, docs/drawing/principles.md, .scratch/35-r1-articulated-study/work/m1a-m1b-plan.md (M1b acceptance), .scratch/35-r1-articulated-study/issues/54-user-review-scope-hair-and-hand.md, evidence/B-caption-corrected-v1/public-caption-disposition.md.",
  "WRITER CLAIMS TO VERIFY BY RE-RUNNING (not trusting): 12 passing construction tests; digit counts; distal separation >= 0.010; width taper distal <= 0.80 x proximal; palm contact re-derived from the dish contour; palm-behind-dish depth 0.012 with a 0.006 hidden inset; fingertip-to-rim distances equal to tip_half + reach margin; control keeps all six hand outlines identical; 17-entry manifest.",
  "JUDGE ONLY THESE: (1) run the suite; do the tests assert the claimed geometry or do their expected values come from the same code path they check (circular)? name any; (2) is the contact a consequence of the dish geometry or a coincidence of typed numbers — trace where the dish contour enters and where fingertip reach comes from; (3) does the construction avoid both a blob with drawn-on claw lines and an over-fitted contour table — count the real hand-typed coordinates per digit and per palm; (4) does the control differ from the baseline only in the dish, verified mechanically; (5) does any caption claim something the rendered image does not show; (6) does the manifest verify and does every listed file exist; (7) dead code or README claims beyond the code.",
  "Report each finding with file and line, the criterion violated, and the command that produced the evidence; separate blocking from nonblocking.",
  "CONSTRAINTS: do not modify, create or delete any file; do not commit; do not repair. End with `git status --porcelain` and confirm the tree is clean.",
  "BUDGET: 40 minutes; hard stop at 40. If a command fails, report the exact error rather than substituting a weaker check; never report an unrun check as passed.",
].join("\n");

return runs.all([
  runs.run("m1a-resume", {
    agent: "worker",
    task: A_RESUME,
    label: "Resume A v6: rebuild artefacts, true manifest, honest repair log",
    model: "deepseek/deepseek-flash:low",
    async: true,
    cwd: "/home/z/vibe/worktrees/learn_draw/pi-worktree-5e7cbf95-af4e-4a89-9df8-dda2840a95d4-s0-0",
    worktree: false,
  }),
  runs.run("m1b-repair-1", {
    agent: "worker",
    task: B_REPAIR,
    label: "Repair B: hand grip readability, arm articulation, colour separation",
    model: "deepseek/deepseek-flash:low",
    async: true,
    worktree: true,
  }),
  runs.run("review-b-structure", {
    agent: "worker",
    task: B_REVIEW,
    label: "Verify B structure: run tests, trace contact, check captions",
    model: "deepseek/deepseek-flash:low",
    async: true,
    worktree: false,
  }),
]);
