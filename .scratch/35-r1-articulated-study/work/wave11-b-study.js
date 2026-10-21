// Wave 11 — R1a part B: the reference-free hand-and-dish object study (B-hand-study-v1).
//
// Contract: .scratch/35-r1-articulated-study/work/r1a-object-study-contracts.md § B-hand-study-v1
// Plan row: .scratch/35-r1-articulated-study/work/m1a-m1b-plan.md § R1a-B-HAND
// Run as NEVER-RUN: no artefact, no commit and no branch existed for this study when it was
// dispatched (see mail/2026-10-21-orientation.md §(b)); three documents claiming an artefact are
// wrong, and this dispatch is what replaces the fiction with a package.
//
// contract.area       .scratch/35-r1-articulated-study/evidence/B-hand-study-v1/  (one writer)
//                     .scratch/35-r1-articulated-study/work/wave11-b-study.js     (this file)
// contract.acceptance see "REQUIRED PROOF" below; each item is a command, not a claim
// contract.spend      idle-compute      (no network write, no paid API, no exclusive resource)
const TASK = [
  "You are one child of a delegation tree; you have no dialogue with the user and you report to the parent only. Your final message IS the report.",
  "Repo root: /home/z/vibe/learn_draw. Read first, in this order: .scratch/35-r1-articulated-study/work/r1a-object-study-contracts.md (the binding contract for B), .scratch/35-r1-articulated-study/work/m1a-m1b-plan.md (owners, paths, budgets), mail/2026-10-21-orientation.md §(b) (why this study is run as never-run).",
  "",
  "ROLE: B-hand-study-v1 writer, single writer, own directory. You own exactly .scratch/35-r1-articulated-study/evidence/B-hand-study-v1/ and this dispatch script. You may copy primitives from .scratch/35-r1-articulated-study/evidence/B-hand-v2-r1/ read-only. You do NOT repair A-bow-study-v2, you do not touch its files, and you do not change the R1a contracts — another package owns v2 and a second writer in that directory is what the parent is preventing.",
  "",
  "CONTRACT (binding, from r1a-object-study-contracts.md § B-hand-study-v1):",
  "- Canvas 900x700, single image, no panels, no captions.",
  "- Object: a hand supporting a shallow dish, filling the frame. No torso, head, shoulder join or body connection.",
  "- Must read as: a hand supporting a dish from below — the dish's underside visibly meets the palm/fingers, the digits curl around or lie along the dish rather than standing as prongs in front of it, a thumb opposes on the near side, the dish reads as a vessel. Failure readings: fingers as rake tines, a hand intersecting a plate, the dish balanced on the fingertips, a flat lens with one rim.",
  "- Binding construction: contact derived from the dish's own emitted contour, with the test re-deriving that contour instead of reusing the producer's constant; digit separation reported at the roots and at the distal halves as a fraction of a digit's width, with the roots' merge stated rather than hidden; the dish carries a rim with thickness, an inner wall and an underside; palm/fingers and dish interleave in depth with the rear edge broken at every occlusion, asserted with a mutation demonstration; no drawn-on claws or crease lines standing in for form; reference-free, so scripts/draw check runs with no --ref.",
  "- Optional: a second image of the same hand with the dish lifted 30 px, only if everything else is complete, purely to prove the pose is parameterised.",
  "- Artefacts: source/, tests/, artwork.svg, artwork.png (900x700), check/ bundle with the 1:1 image listed first, manifest.json + manifest.sha256, README.md (construction vocabulary, geometric consequence vs author hypothesis, contact derivation, separation values with the root/distal qualifier, commands, unverified items).",
  "",
  "LAW this study follows (the project's own):",
  "- Geometry computed, never eyeballed. Every stroke in the drawing must be derived from the mesh (a silhouette, or a fold whose dihedral exceeds a threshold); no authored mark table.",
  "- The engine never reads a reference. No source file may name image.jpg or import an image library.",
  "- Metrics are alarms not targets. Do not tune a threshold to make a drawing look better; report the measurement.",
  "- No candidate is promoted and nothing is called final without the roadmap's gate. The render is judged by a fresh sight-capable reviewer on the image, never by you. You do not declare the art good.",
  "",
  "REQUIRED PROOF (commands and outputs in the report):",
  "- Source, a deterministic build, tests, the rendered artwork (900x700), and a check/ bundle with manifest.json, manifest.sha256 and a negative control, matching the shape A-bow-study-v1 has.",
  "- A rebuild from the committed source reproduces the delivered image byte-identically, proven by the command.",
  "- The study's own tests pass from a clean tree.",
  "- The contour re-derivation: the test derives the dish's rim band itself and every digit's tip is measured against it.",
  "- The separation values at the roots and at the distal halves, as fractions of a digit's width, with the merge stated.",
  "- The occlusion-break test plus its mutation, both counts recorded in tests/negative-control-output.txt.",
  "- manifest verifies 100% and the 1:1 image is listed first in the check bundle.",
  "",
  "BUDGET: 2 hours wall clock, idle-compute. Commit what is reproducible if incomplete, and report what remains and where the next writer starts.",
  "STOP AND REPORT rather than faking: if a claim cannot be made true, keep the drawing truthful and report the gap.",
].join("\n");

return runs.run("r1a-b-hand-study", {
  agent: "worker",
  task: TASK,
  label: "R1a B: hand-and-dish object study, reference-free, 900x700",
  model: "deepseek/deepseek-flash:low",
  worktree: false,
  async: true,
});
