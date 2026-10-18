// Wave 4 — independent review of the merged M1b B-hand candidate.
const IMAGE_TASK = [
  "You are a fresh independent reviewer with a deliberately narrow job. You did not write this drawing.",
  "Read ONLY this image: /home/z/vibe/learn_draw/.scratch/35-r1-articulated-study/evidence/B-hand-v2/check/draft.png",
  "Do not read any other file: not the README, not the source, not the manifest, not any other image.",
  "Answer one open question: what is wrong here? Report what you actually see, worst-damaging first, with approximate locations as fractions of each panel's width/height.",
  "There are three panels; treat each separately and then say whether the three read as one coherent comparison.",
  "For each finding, say whether it is shape/construction, line art, colour, or composition, and whether it would still bother you if you did not know what the picture was meant to be.",
  "Do not decide acceptance, do not assess code, do not speculate about intent. Your report is evidence for the parent.",
  "Budget: 20 minutes. Keep it under one page.",
].join("\n");

const STRUCT_TASK = [
  "You are a fresh independent reviewer for one candidate package. You did not write it. You DO have execution tools in this session and you must use them — an earlier reviewer could not run anything, so nothing here may be reported as passing without the command that produced it.",
  "Repo root: /home/z/vibe/learn_draw. Use scripts/draw or .venv/bin/python; the venv exists and cv2 is installed.",
  "PACKAGE: /home/z/vibe/learn_draw/.scratch/35-r1-articulated-study/evidence/B-hand-v2/ (README.md, source/, tests/, rendered/, check/, manifest.json, manifest.sha256).",
  "AUTHORITATIVE INPUTS: AGENTS.md (invariant rules), docs/drawing/spatial-model.md, docs/drawing/principles.md, .scratch/35-r1-articulated-study/work/m1a-m1b-plan.md (the M1b work package and its acceptance), .scratch/35-r1-articulated-study/issues/54-user-review-scope-hair-and-hand.md (the user's binding requirement: the hand must be constructed geometry at a detailed level, not a blob), .scratch/35-r1-articulated-study/evidence/B-caption-corrected-v1/public-caption-disposition.md (the truthful-caption constraint).",
  "WRITER CLAIMS TO VERIFY BY RE-RUNNING, not by trusting: 12 passing construction tests; digit count 1 palm + 4 fingers + 1 thumb; distal separation >= 0.010; width taper distal <= 0.80 x proximal; palm contact re-derived from the dish contour; palm-behind-dish depth separation 0.012 with a 0.006 hidden inset; fingertip-to-rim distances equal to tip_half + reach margin; the control keeps all six hand outlines identical to the baseline; manifest verifies for 17 entries.",
  "JUDGE, and only judge, these questions:",
  "1. Run the test suite; report the command and the result. Are the tests actually asserting the claimed geometry, or are they asserting numbers the implementation itself supplies (a circular check)? Name any test whose expected value comes from the same code path it is meant to check.",
  "2. Is the contact relation a consequence of the dish geometry, or is it a coincidence of hand-placed numbers? Trace where the dish contour enters the hand construction and where the fingertip reach comes from.",
  "3. Does the construction avoid both failure modes: a blob with drawn-on claw lines, and an over-fitted contour table (many hand-typed coordinates)? Count the hand-typed coordinates per digit and per palm and state the real number.",
  "4. Does the control panel differ from the baseline only in the dish (and its caption), with the hand unchanged? Verify mechanically, not by reading the prose.",
  "5. Does the delivered caption claim anything the rendered image does not show (in particular about the thumb and the rim)?",
  "6. Does the manifest verify (sha256sum -c), and does every listed file exist?",
  "7. Is there dead code or an unreachable mechanism in the package, and does any README claim overstate what the code does?",
  "Report each finding with file and line or function, the criterion it violates, and the command that produced the evidence. Separate blocking from nonblocking.",
  "CONSTRAINTS: do not modify, delete or create any file; do not commit; do not repair. Finish by running `git status --porcelain` and confirming you left the tree clean.",
  "BUDGET: 40 minutes; hard stop at 40. ESCALATION: if a command fails, report the exact error rather than substituting a weaker check. Never report an unrun check as passed.",
].join("\n");

return runs.all([
  runs.run("review-b-image", {
    agent: "reviewer",
    task: IMAGE_TASK,
    label: "Review B image: what is wrong here",
    model: "deepseek/deepseek-flash:low",
    async: true,
  }),
  runs.run("review-b-structure", {
    agent: "worker",
    task: STRUCT_TASK,
    label: "Verify B structure: run tests, trace contact, check captions",
    model: "deepseek/deepseek-flash:low",
    async: true,
  }),
]);
