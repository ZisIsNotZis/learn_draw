// Wave 12, package B — B-hand-study-v1 image-only art and cohesion review (M1a-RV-IMAGE pattern).
//
// Contract: .scratch/35-r1-articulated-study/work/wave12-contracts.md § Package B
//           .scratch/35-r1-articulated-study/work/m1a-m1b-plan.md § Review work packages
//
// contract.area       nothing writable in the study tree; one report into evidence/reviews-r1a/
// contract.acceptance a verdict per acceptance question, findings located on the image, or BLOCKED
// contract.spend      idle-compute + time
// contract.clock      25 min wall clock, hard stop
//
// Launched in this session through the `subagent` tool, context `fresh`, so nothing of the producer's
// reasoning, the README, the ledger or the parent's opinion is in its window. The payload below is
// the exact task text.
const TASK = [
  "You are one reviewer in a delegation tree. You have no dialogue with the user; your final message IS your report. You are judging an image and nothing else.",
  "",
  "You may open exactly two files, and no others:",
  "  /home/z/vibe/learn_draw/.scratch/35-r1-articulated-study/evidence/B-hand-study-v1/check/draft-fullres.png   (900x700, sha256 e428bb0ded708452c573d871b6d70d4a922453a99fe4bbac4476270865c59aec)",
  "  /home/z/vibe/learn_draw/.scratch/35-r1-articulated-study/evidence/B-hand-study-v1/check/draft.png          (900x700, sha256 0dbeb263277db3e0ee0b468fc5319fe416270046650241cdd53ac5c9131dfa12)",
  "Do not open any README, any file under source/ or tests/, check/report.txt, any manifest, any .md, .json, .txt or .svg in the repository, and do not run the build or any test. You have been given no producer rationale on purpose: if you read one anyway, say so, and your verdict is void. Judge detail on draft-fullres.png (1:1).",
  "",
  "THE OPEN QUESTION IS: what is wrong here?",
  "",
  "Answer these four, each with a verdict of PASS, BLOCKING FINDING or NONBLOCKING FINDING:",
  "1. Construction, attachment and pose. Does this read as a hand supporting a shallow dish from below? Name anything that reads as a failure: a hand as rake tines, a hand intersecting a plate, a dish balanced on fingertips, a flat lens with one rim, digits standing as prongs in front of a vessel rather than meeting it.",
  "2. Physical geometry and visibility. Where does the picture's depth disagree with the body it claims — parts interpenetrating, a surface passing through another, a limb floating free, a hidden edge drawn as visible, a visible edge cut for no reason?",
  "3. Drawing and art. Name every artefact you can see: a spike, a doubled or hatched edge, a crease or stroke that stops in mid-air, a seam, a banding or spoke pattern, a fill flat enough that the order of overlap cannot be read, a shape whose mass is in the wrong place (for instance a joint or a knot widest where it should pinch).",
  "4. Object cohesion. Does each object read as one connected thing? Name any object that reads as more than one disconnected piece, and any part whose identity you cannot tell from the picture.",
  "",
  "For every finding: what you see, and where — give an approximate pixel coordinate or a short description of the region, and label it approximate. A reviewer's locations are reliable only as approximations; say so rather than implying measurement. Rank the findings: at most three are blocking.",
  "",
  "Then state plainly which single defect a draftsman should fix first, and what a viewer would misread if it is left.",
  "",
  "IF YOU CANNOT SEE THE IMAGE — the file does not open, or you receive no picture, or you can only read bytes — answer exactly BLOCKED with what failed. Never infer content from a filename, a file size or a hash. An invented verdict is worse than no verdict.",
  "",
  "WRITE your report verbatim to /home/z/vibe/learn_draw/.scratch/35-r1-articulated-study/evidence/reviews-r1a/B-hand-study-v1-image-review-1.md and write no other file anywhere. Do not modify, move or delete anything. Budget 25 minutes wall clock, hard stop; land the report before you finish rather than at the end of a longer thought.",
].join("\n");

// returns runs.run("r1a-b-image-review-1", {
//   agent: "reviewer",
//   task: TASK,
//   label: "R1a B image-only art review: what is wrong here",
//   model: "deepseek/deepseek-flash:high",
//   worktree: false,
//   context: "fresh",
//   async: true,
// });
