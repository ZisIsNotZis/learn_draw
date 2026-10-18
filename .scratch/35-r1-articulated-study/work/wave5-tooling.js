// Wave 5 — tooling: review bundles must carry full-resolution images, not thumbnails.
const TASK = [
  "You are one child of a delegation tree; you have no dialogue with the user and you report to the parent only.",
  "Repo root: /home/z/vibe/learn_draw. Read AGENTS.md first, then docs/drawing/method.md (the drawing loop and what a check bundle is for).",
  "Environment: .venv exists (cv2/numpy/pillow/pyyaml installed); run tools through scripts/draw or .venv/bin/python. Renderer resolves automatically.",
  "",
  "ROLE: tooling owner. You may modify exactly these paths: scripts/draw.py, scripts/tests/ (add tests there if that directory is the right home, otherwise tests/ at the repo root if it exists), docs/drawing/method.md (only the sentences that describe check-bundle images), and you must leave everything else untouched.",
  "",
  "DEFECT (observed, blocking review quality): in two independent fresh image reviews this session, the reviewer was handed a check bundle whose only drawing image was a downscaled preview — `.scratch/35-r1-articulated-study/evidence/B-hand-v2/check/draft.png` is 256x121 for a 1350x640 sheet, and the reviewer explicitly reported 'the image arrived at thumbnail scale and I did not magnify it', after which it could not see digit separation at all. An art review conducted on a thumbnail is not evidence about the artwork.",
  "",
  "ROOT CAUSE TO CONFIRM: scripts/draw.py check builds its bundle with a bounded pane size (option --pane, default 256) and writes that bounded image as the bundle's draft. Confirm the actual code path and the actual default before changing anything, and report what you found with file and line.",
  "",
  "REQUIRED OUTCOME:",
  "1. A check bundle must always contain a full-resolution image of the drawing (no downscale), named so a reviewer knows it is the 1:1 image, and the report's image list must name it. Bounded previews may remain as additional files but must never be the only drawing image.",
  "2. The reviewer protocol text in the report must not encourage a downscaled view.",
  "3. Region crops keep their existing zoom behaviour.",
  "4. Existing behaviour that other tickets depend on (metrics, 'vs recorded best', bundle layout, report fields) must not change.",
  "5. Add a test that fails if a produced bundle's primary drawing image is smaller than the source artwork (test the bundling function, or run check on a small fixture SVG and assert the emitted image dimensions equal the artwork's). Run it and report the command and result.",
  "",
  "CONSTRAINTS: do not modify any evidence directory, any drawing source, STATUS.md, roadmap.md, or any file outside the paths listed above. Do not regenerate any existing bundle (that would rewrite evidence); verify with a temporary output directory inside .tmp/ or /tmp, and delete it afterwards.",
  "Report: the root cause with file and line, the exact diff, the test command and result, and anything you deliberately left unchanged.",
  "BUDGET: 45 minutes. If changing the default would break a documented contract, prefer making the full-resolution image mandatory in addition to the existing preview, and say so.",
].join("\n");

return runs.run("tooling-review-images", {
  agent: "worker",
  task: TASK,
  label: "Fix check bundles so reviews get full-resolution images",
  model: "deepseek/deepseek-flash:low",
  worktree: true,
  async: true,
});
