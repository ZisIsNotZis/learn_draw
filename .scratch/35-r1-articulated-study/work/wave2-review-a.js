// Wave 2 — independent review of the merged M1a A candidate (two fresh reviewers).
const IMAGE_TASK = [
  "You are a fresh independent reviewer with a specific, deliberately narrow job. You did not write this drawing and you have no history with it.",
  "Repo root: /home/z/vibe/learn_draw (absolute paths below are complete).",
  "Read ONLY these five images:",
  "  /home/z/vibe/learn_draw/.scratch/35-r1-articulated-study/evidence/A-cloth-v5/artwork-a.png",
  "  /home/z/vibe/learn_draw/.scratch/35-r1-articulated-study/evidence/A-cloth-v5/check-a/side-by-side.png",
  "  /home/z/vibe/learn_draw/.scratch/35-r1-articulated-study/evidence/A-cloth-v5/check-a/region-1.png",
  "  /home/z/vibe/learn_draw/.scratch/35-r1-articulated-study/evidence/A-cloth-v5/check-a/region-2.png",
  "  /home/z/vibe/learn_draw/.scratch/35-r1-articulated-study/evidence/A-cloth-v5/check-a/region-3.png",
  "Do not read any other file: not the README, not the source, not the intent, not the manifest.",
  "Answer one open question: what is wrong here? Report what you actually see, ordered by how badly it damages the image, and for each finding give the image and the approximate location (fraction of width/height is fine).",
  "For each finding also say whether it is a defect of shape/construction, of line art, of colour, or of composition, and whether it would still bother you if you did not know what the picture was meant to be.",
  "Do not propose a verdict on acceptance, do not assess the code, and do not speculate about what the author intended. Your report is evidence for the parent, not a decision.",
  "If an image is unreadable or missing, say so plainly instead of guessing.",
  "Budget: 25 minutes. Keep the report under one page.",
].join("\n");

const STRUCT_TASK = [
  "You are a fresh independent structural reviewer for one candidate drawing package. You did not write it.",
  "Repo root: /home/z/vibe/learn_draw. All paths below are absolute.",
  "GOAL OF THE PACKAGE: rebuild the A candidate so that each drawn object reads as one connected physical thing, under the task scope 'imitate only the clothing/composition of the reference crop; no hand claim'.",
  "CANDIDATE: /home/z/vibe/learn_draw/.scratch/35-r1-articulated-study/evidence/A-cloth-v5/ (README.md, source/, tests/, artwork-a.svg, artwork-a.png, check-a/, manifest.json, manifest.sha256, ref/crop-400x480.png).",
  "AUTHORITATIVE INPUTS: docs/drawing/spatial-model.md (component = 2D artwork on a support surface; the engine computes visibility from depth; no author-specified visibility cuts), docs/drawing/principles.md P31-P33, .scratch/35-r1-articulated-study/issues/54-user-review-scope-hair-and-hand.md (the user's binding requirements), AGENTS.md (invariant rules), .scratch/35-r1-articulated-study/work/m1a-m1b-plan.md (the M1a acceptance list).",
  "ALREADY ESTABLISHED BY THE WRITER, to be re-run rather than trusted: a seam contract over 16 joints, a negative-control transcript at tests/negative-control-output.txt, two-sided hair test, two-sleeve test, identity test, a draw-check bundle, and a manifest of 38 files. Re-run everything yourself and report the exact commands and results.",
  "JUDGE, and only judge, these questions:",
  "1. Is the bow one continuous ribbon whose width is continuous through the knot, with the lobes' overlap produced by depth and its crease/fold reading authored rather than accidental? Inspect the source for how the spine and width are generated; a tail that starts wider than the knot or at an offset is the defect this milestone exists to remove.",
  "2. Are both sleeves present as whole components with the second cuff authored whole, and is the second cuff's surviving visible extent a depth result rather than an authored cut, shortened outline, or separate 'visible part' shape? Search for any hand-authored clipping.",
  "3. Is the hair a single curved support sheet with a twisting normal and two distinct side fills chosen by projected face orientation, and is that mechanism actually reachable from the build (not dead code)?",
  "4. Does the seam contract actually fail when a joint is broken (run the negative control), and does it cover every joint the build declares?",
  "5. Do the tests pass now, in this revision? Report the command and the result.",
  "6. Does the package honour the authoring rules: no shape with more than ~4 hand-typed coordinates, absolute frame coordinates only as compiler output, no metric tuning?",
  "7. Does the manifest verify (hash every listed file)?",
  "Report each finding with its location (file and line or function) and the criterion it violates, and each check with the command that produced it. Separate blocking from nonblocking.",
  "EXCLUSIONS: do not judge art quality or readability (a separate image-only reviewer owns that); do not edit any file; do not repair anything; do not commit.",
  "BUDGET: 40 minutes. Stop at the limit and report what you reached, including anything unverified.",
  "ESCALATION: if a check cannot run, report the exact error rather than substituting a weaker check. Never report an unrun check as passed, and never claim a runtime behaviour you did not observe.",
].join("\n");

return runs.all([
  runs.run("review-a-image", {
    agent: "reviewer",
    task: IMAGE_TASK,
    label: "Review A image: what is wrong here",
    model: "deepseek/deepseek-flash:low",
    async: true,
  }),
  runs.run("review-a-structure", {
    agent: "reviewer",
    task: STRUCT_TASK,
    label: "Review A structure: bow strip, sleeves, hair, seam contract",
    model: "deepseek/deepseek-flash:low",
    async: true,
  }),
]);
