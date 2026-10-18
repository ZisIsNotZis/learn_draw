// Wave 8 — independent review of A-cloth-v6 (image-only art, plus execution-verified structure).
const IMAGE_TASK = [
  "You are a fresh independent reviewer with a deliberately narrow job. You did not write this drawing.",
  "Read ONLY these five images:",
  "  /home/z/vibe/learn_draw/.scratch/35-r1-articulated-study/evidence/A-cloth-v6/check-a/side-by-side.png",
  "  /home/z/vibe/learn_draw/.scratch/35-r1-articulated-study/evidence/A-cloth-v6/check-a/draft-fullres.png",
  "  /home/z/vibe/learn_draw/.scratch/35-r1-articulated-study/evidence/A-cloth-v6/check-a/region-1.png",
  "  /home/z/vibe/learn_draw/.scratch/35-r1-articulated-study/evidence/A-cloth-v6/check-a/region-2.png",
  "  /home/z/vibe/learn_draw/.scratch/35-r1-articulated-study/evidence/A-cloth-v6/check-a/region-3.png",
  "Do not read any other file: not the README, not the source, not the intent, not the manifest.",
  "Answer one open question: what is wrong here? Report what you actually see, worst-damaging first, with approximate locations as fractions of width/height. Judge detail on the full-resolution image, not on the side-by-side panes.",
  "For each finding say whether it is shape/construction, line art, colour, or composition, and whether it would still bother you if you did not know what the picture was meant to be.",
  "Then answer separately: what does the drawing now read as — describe it as you would to someone who cannot see it.",
  "Do not decide acceptance, do not assess code, do not speculate about intent. Your report is evidence for the parent.",
  "Budget: 25 minutes. Keep it under one page.",
].join("\n");

const STRUCT_TASK = [
  "You are a fresh independent verifier. You did not write this package. You have execution tools and must use them: nothing may be reported as passing without the command that produced it.",
  "Repo root: /home/z/vibe/learn_draw. Use scripts/draw or .venv/bin/python; the venv exists.",
  "PACKAGE: /home/z/vibe/learn_draw/.scratch/35-r1-articulated-study/evidence/A-cloth-v6/",
  "CONTEXT: this package is a repair of A-cloth-v5 after an independent structural review (which found: hair twist not implemented, hidden hand-typed stations, overstated README seam claim, incomplete joint coverage, no tangency negative control, dead code, knot passes at equal depth) and an independent image review (which found the drawing unreadable as a figure, the bow not resolving, hair reading as flat ribbons). The repair writer claims: build fixed (was crashing on a self-intersecting neck contour), D5/D7/D9/D12 fixed, D1/D2/D3/D4/D6/D8 partial, D10 and D11 NOT fixed, manifest rewritten over 39 files.",
  "JUDGE, with commands, and only these:",
  "1. Does the package build and render from its own source at this revision, and does the delivered artwork-a.png match a fresh build byte-for-byte? Report the commands.",
  "2. Does `sha256sum -c manifest.sha256` verify fully, and does the manifest cover the real file set?",
  "3. Do the tests pass, and are any of them tautological — does an expected value come from the same code path it is meant to check? Name every such test with file and line.",
  "4. Is the hair mechanism real: does the sheet pass a twist function that flips all columns together, so that setting twist to zero changes the two-sided result? Verify by running the test and by reading the construction.",
  "5. Is the seam contract enforced for every declared joint, and do its negative controls actually fail (translation, depth, and — if present — tangency)? Run them.",
  "6. Are the writer's counter-claims true: is D10 (tangency negative control) really missing, is D11 (dead code, including folded_loop/gather_patch/tension_tail/_band_from_stations/hair_curlband) really still present, and are the D3 (hair hole) and D4 (line ownership) and D8 (declared == actual authoring count) tests really missing? Re-derive each independently instead of trusting repair-log.md.",
  "7. Is the bow still one continuous strip with one constant width and depth-driven lobe overlap, with the knot passes at distinct depths?",
  "Report each item as verified / contradicted / unverified with the command and its output. Separate blocking from nonblocking.",
  "CONSTRAINTS: do not modify, create or delete any file; do not commit; do not repair. End with `git status --porcelain` and confirm the tree is clean.",
  "BUDGET: 40 minutes; hard stop at 40. Never report an unrun check as passed; if a command fails, report the exact error.",
].join("\n");

return runs.all([
  runs.run("review-a6-image", {
    agent: "reviewer",
    task: IMAGE_TASK,
    label: "Review A v6 image: what is wrong here",
    model: "deepseek/deepseek-flash:low",
    async: true,
    worktree: false,
  }),
  runs.run("review-a6-structure", {
    agent: "worker",
    task: STRUCT_TASK,
    label: "Verify A v6: build, manifest, tautologies, hair twist, dead code",
    model: "deepseek/deepseek-flash:low",
    async: true,
    worktree: false,
  }),
]);
