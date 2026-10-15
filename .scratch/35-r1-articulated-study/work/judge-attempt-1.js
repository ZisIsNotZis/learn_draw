const DIR = ".scratch/35-r1-articulated-study/work/reference-free-attempt-1";
const COMMON = "Repo/cwd /home/z/vibe/learn_draw; AGENTS applies. Read-only unless this task explicitly grants writing. No staging/commit, no environment/network/provider/install changes, no edits to A/B candidates, teacher evidence, sealed material, or append-only files. Keep pre-existing dirty/staged state. Commands <=120s.";

const tech = await runs.run("technical", {
  agent: "worker",
  label: "Validate frozen attempt source and evidence",
  model: "github-copilot/gpt-6-luna:low",
  context: "fresh",
  timeoutMs: 1500000,
  toolTimeoutMs: 120000,
  output: "r1/attempt1-technical-validation.md",
  task: COMMON + "\nFresh independent technical validator (not the creator, not an art judge). Scope: the frozen attempt directory " + DIR + " (source.py, test_source.py, artwork.svg, artwork.png, report/check/, manifest.json, ticket.md, input-provenance.txt, recovery-snapshot/). Also read the public packet teaching/r1-reference-free-method/generic-spatial-api.md only if needed for API expectations. Do NOT read the sealed brief or its contents; do NOT treat the brief as needed for this technical check.\nVerify from actual bytes: (1) manifest hashes match current files and PNG/check-draft binding; (2) source is genuinely original programmatic construction that consumes its own authored semantic inputs to build component-local 2D outlines mapped through real SupportFrame world geometry, camera projection, and the existing depth visibility/line visibility path (component_faces / visible_regions / visible_segment_spans), with no imported preset/case-builder/previous candidate/pasted raster; (3) no manual visibility intervals or global painter order; (4) per-shape authored coordinate discipline is honest (generator-consumed inputs, not metadata counters, not a dense literal table renamed as relations); (5) determinism and reference-absence: rerun the creator's own generation command once at most (<120s) into a temp dir and compare hashes, or cite the manifest's recorded reproduction if rerunning is not feasible; (6) run the 5 self-tests once (each group <120s) and report actual results; (7) public artifacts (ticket/manifest/report) do not contain or quote private brief wording, answer text, or distinctive task facts — flag if they do.\nReport SCOPED PASS/BLOCK with actual commands/hashes, what you ran vs cited, and explicit unknowns. This is construction/source/repro evidence only, never an art or task-satisfaction verdict.",
});

const sight = await runs.run("sight", {
  agent: "reviewer",
  label: "Read attempt image-only sight facts",
  model: "github-copilot/gpt-6.1-sol:low",
  context: "fresh",
  timeoutMs: 1200000,
  output: "r1/attempt1-sight-facts.md",
  outputSchema: {
    type: "object",
    properties: {
      visible: { type: "boolean" },
      filled: { type: "array", items: { type: "string" } },
      facts: { type: "string" },
      imagePaths: { type: "array", items: { type: "string" } },
      limits: { type: "string" },
    },
    required: ["visible", "filled", "facts", "imagePaths", "limits"],
    additionalProperties: false,
  },
  task: "Read only " + DIR + "/report/check/report.txt to obtain the listed image paths, then actually open those images. Do not read source, manifest, ticket, brief, teacher, or any explanation; do not infer from filenames. Do not yet judge art. First give checkable image-specific facts: actual pixel dimensions, and 3 (three) clearly non-background, non-text stable interior probes, each with (x,y), approximate colour category, and relative position, chosen from distinct regions, avoiding edges/lines/titles; state your approximate visual error (<=8 px). Also list two vivid, well-saturated fill colours you can name, using the largest distinct colour areas. Set visible=false with an explicit IMAGE BLOCKED note if you cannot actually see the images. Do not provide an artistic verdict yet; source-isolated. No repo writes.",
});

if (!tech.ok) return { stage: "technical", tech };
if (!sight.ok || !sight.structuredOutput || !sight.structuredOutput.visible) return { tech, sight };

const verify = await runs.run("verify", {
  agent: "worker",
  label: "Numerically verify the sight facts",
  model: "github-copilot/gpt-6-luna:low",
  context: "fresh",
  timeoutMs: 900000,
  toolTimeoutMs: 120000,
  output: "r1/attempt1-sight-verification.md",
  outputSchema: {
    type: "object",
    properties: {
      verdict: { type: "string", enum: ["PASS", "BLOCK", "UNVERIFIED"] },
      evidence: { type: "string" },
      limits: { type: "string" },
    },
    required: ["verdict", "evidence", "limits"],
    additionalProperties: false,
  },
  task: COMMON + "\nIndependent read-only verification of the supplied image-sight facts. Claim: " + JSON.stringify(sight.structuredOutput) + "\nOpen the actual image(s) named in the claim and, using Pillow in the repo venv, measure: image dimensions, each claimed probe's exact RGB and its 17x17 neighborhood uniformity, the actual two vivid saturated non-background colours (report their RGB and rough fraction of the canvas, ignoring near-white/near-black/near-gray pixels), and the claimed spatial relations. Do NOT read the brief or the source; judge only whether the claimed facts are numerically supported, allowing the stated <=8px tolerance. Also report the actual encoded SHA-256 of the image file you measured so the binding is unambiguous. Return PASS only if the probe colours/uniformity, the vivid colour identification (a saturated colour must have a large max-min channel spread, not be near-neutral), and relative positions are all supported; BLOCK/UNVERIFIED otherwise with specifics. This is a limited observation-capability check, not an art, task-satisfaction, transfer, or R1 verdict. One bounded command, <=120s.",
});

if (!verify.ok || !verify.structuredOutput || verify.structuredOutput.verdict !== "PASS") return { tech, sight, verify };

const observation = await runs.run("observe", {
  resume: sight.runId,
  label: "Qualified image-only observation",
  timeoutMs: 1200000,
  output: "r1/attempt1-image-observations.md",
  task: "Your limited image-sight facts were independently verified as numerically supported, so your observation is qualified. Now, reading only the same image set and nothing else (no source, manifest, brief, teacher, or expected answer), answer the open question 'what is wrong here?'. Describe, source-isolated: what objects/figures you actually see; their pose, connections, and any contact or overlap; how the visible depth/occlusion reads; and any ambiguity, inconsistency, or defect in readout. Give actual image dimensions and approximate coordinates, and state uncertainty. Do not assume any unshown content is required. This is a qualified observation, not a task-satisfaction, art, transfer, or R1 verdict; do not claim one. Keep the same output schema: put the full observation in facts, keep visible=true and the actual image paths, and record limits. No repo writes.",
});

if (!observation.ok) return { tech, sight, verify, observation };

const judge = await runs.run("judge", {
  agent: "worker",
  label: "Judge frozen drawing against the held-out brief",
  model: "github-copilot/gpt-6-luna:medium",
  context: "fresh",
  timeoutMs: 2100000,
  toolTimeoutMs: 120000,
  output: "r1/attempt1-brief-satisfaction-judgement.md",
  outputSchema: {
    type: "object",
    properties: {
      verdict: { type: "string", enum: ["PASS", "BLOCK", "UNVERIFIED"] },
      criteria: { type: "string" },
      evidence: { type: "string" },
      leakRisk: { type: "string" },
      limits: { type: "string" },
    },
    required: ["verdict", "criteria", "evidence", "leakRisk", "limits"],
    additionalProperties: false,
  },
  task: COMMON + "\nYou are the independent held-out task owner/grading role, authorized for this task to read the sealed brief " + DIR.replace(/\/work\/reference-free-attempt-1$/, "/work") + "/holdout-brief.sealed.md (verify the exact path against the public R1 spec/freeze first) and to view the frozen candidate drawing " + DIR + "/artwork.png. This is the one role permitted the private comparison. Independent qualified image observations exist at r1/attempt1-image-observations.md and technical/source evidence at r1/attempt1-technical-validation.md; consult them but make your own judgement.\nJudge only this question: does the frozen drawing satisfy the actual requirements stated in the brief (subject, action/pose, required elements, any stated variation/control, and the brief's own acceptance wording)? Read the brief carefully, enumerate its explicit criteria, and check the drawing against each: which are clearly satisfied, which are absent or wrong, and which are ambiguous. Inspect the PNG directly; do not credit code, manifests, or author claims as visual fulfilment. Also flag any requirement the brief states that neither image nor source addresses.\nOutput verdict PASS only if every explicit brief criterion is met by the visible drawing; otherwise BLOCK with the specific unmet criteria. In leakRisk, state whether your report, the public artifacts you read, or the brief path itself risk disclosing private content, and keep the report itself free of verbatim or identifying brief content (summarize generically, no answer text, no distinctive task facts). Report limits and unknowns. This is the held-out drawing gate only: it does not pass old S1a worksheet/neutral-board/receipt gates, transfer, or overall R1 by itself.",
});

return { tech, sight, verify, observation, judge };
