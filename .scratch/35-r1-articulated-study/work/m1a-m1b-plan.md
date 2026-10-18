# R1 advance plan — milestones M1a, M1b, M2, M3, M4

Owns: the approved milestone list to first level for this advance, the M1a/M1b writer work packages, the review work packages that follow each writer, and the integration step. It decides no product scope of its own: scope is the user's decisions recorded in [issue 54](../issues/54-user-review-scope-hair-and-hand.md), the public [task freeze](task-freeze.md) and the R1 section of [roadmap](../../../docs/drawing/roadmap.md).

Status: M0 (this document and the roadmap fourth acceptance question) is delivered as documentation only. M1a and M1b writers are dispatched; no writer output has returned, so no milestone, review, integration or gate is complete. M2, M3 and M4 are not started.

## Authority and inputs

- User decisions under issue 54: A keeps its no-hand scope but must show **both sleeves**, the second cuff's visible shape produced by depth occlusion; hair returns to the two-sided curved sheet; B's hand is rebuilt at the detailed level; an additional acceptance question, **object cohesion**, is added to the roadmap; and the advance instruction was given for M1a, M1b, M2, M3, M4.
- Construction contract: [task freeze](task-freeze.md) (A imitates only the observed shoulder/upper-torso clothing of the registered 400x480 crop, no hand claim; B is an original bent-arm/hand/prop illustration with baseline, meaningful variation and labeled control, reference-free).
- Architecture: [spatial-model.md](../../../docs/drawing/spatial-model.md) — 2D art on support surfaces, visibility computed from depth.
- Gate definitions: [roadmap R1](../../../docs/drawing/roadmap.md), including the new fourth acceptance question.
- Transferable lessons that bind this rebuild: [principles.md](../../../docs/drawing/principles.md) P31–P33.
- Writer dispatch payloads: [wave1-m1ab.js](wave1-m1ab.js).

## Approved milestone list

Each milestone is a user synchronisation point: the user sees the actual rendered images and the independent verdicts, and dependent work stops until he responds. A milestone is complete only when its acceptance holds on one frozen revision; no milestone substitutes for a later one.

### M1a — A v5 clean rebuild (two sleeves, curved hair, one continuous bow)

- **Outcome:** A candidate in which every named object reads as one connected visible thing while still imitating only the clothing and composition observed in the registered crop. Concretely: both sleeves present with the second cuff's surviving shape produced by depth visibility rather than an authored cut; hair is one head-attached two-sided curved sheet; the bow is one continuous ribbon whose width is continuous through the knot.
- **Deliverable:** `.scratch/35-r1-articulated-study/evidence/A-cloth-v5/` — part library + assembly source, seam-contract test with negative control plus the hair/sleeve tests, `artwork-a.svg` and `artwork-a.png` at 400x480, a `scripts/draw check` bundle written under that directory, hash manifest, README with the object and seam inventory.
- **Acceptance:** the package self-checks of the M1a work package below all pass, and two fresh independent reviews (image-only art/cohesion; structural/depth) both find no blocking defect on the frozen image list and revision. The writer awards no art verdict.
- **Synchronisation point:** the user is shown the actual A v5 PNG with the review verdicts and the open items. No baseline promotion and no 2D-art resumption happens before his response.
- **Status:** content decided by the user; writing in flight.

### M1b — B hand rebuild at the detailed level

- **Outcome:** the same B concept, variation and control the user judged readable, with the hand rebuilt as constructed geometry — palm, four separable fingers and a thumb from tapered primitives, with grip contact derived from the dish — so the action reads at the final image size. The control stays a legible near miss.
- **Deliverable:** `.scratch/35-r1-articulated-study/evidence/B-hand-v2/` — hand primitive family + scene source, construction/contact tests, three-panel sheet SVG + PNG and per-panel PNGs, a reference-free `scripts/draw check` bundle written under that directory, hash manifest, README stating which contact claims are geometric consequences and which are author hypotheses.
- **Acceptance:** the package self-checks of the M1b work package below pass, captions claim nothing the image does not show, and two fresh independent reviews (image-only art/cohesion; structural/depth and contact derivation) find no blocking defect.
- **Synchronisation point:** the user is shown the actual three-panel sheet with the review verdicts and the contact-claim inventory.
- **Status:** content decided by the user; writing in flight.

### M2 — sealed reference-free drawing (blocked on user action)

- **Outcome:** a genuinely new authored illustration produced from the sealed text-only brief by a role that never sees A's reference or B's construction, materially distinct from both A and B.
- **Deliverable:** a new evidence directory named at release, containing the new drawing, its reference-free reproduction record, its hash manifest and the independent reviews.
- **Acceptance:** the heldout custodian's compatibility/distinctness check passes, the sealed material was read only after release, reproduction is reference-free, and construction/depth/art/cohesion reviews pass on the actual image.
- **Synchronisation point:** none can occur before release — **M2 requires the user to release the sealed task and to authorize a new creator role**. Until both are given, M2 stays BLOCKED and no substitute task, no rewrite of the brief and no partial read is permitted (see [issue 51](../issues/51-public-r1-drawing-role-packet.md), task freeze "Heldout, separately owned").
- **Status:** not started; blocked pending user release and role authorization.

### M3 — integrated R1 delivery

- **Outcome:** one frozen, integrated revision in which A v5, B hand v2 and (once released and drawn) M2 are bound to their reviews and reproduced together, so the user judges one coherent delivery instead of three scattered candidates.
- **Deliverable:** `.scratch/35-r1-articulated-study/evidence/r1-advance-integrated-v1/` — the exact image set, one hash manifest covering every source, output and archived review report, the reference-absent reproduction record, and the integrator's index.
- **Acceptance:** every upstream review is bound to the same hashes as the delivered images; a reference-absent re-render reproduces the delivered images; cross-artefact consistency holds (one revision per image and per report); the integrator waives no gate.
- **Synchronisation point:** the user sees the integrated actual images with their verdicts.
- **Status:** later milestone, not started.

### M4 — user judgment and R1 disposition

- **Outcome:** the user's own verdict on the delivered images, recorded as the R1 disposition, with each gate either accepted, accepted-with-limits or still open. No agent self-verdict becomes an acceptance.
- **Deliverable:** a current-fact STATUS paragraph, an [acceptance-ledger](../evidence/acceptance-ledger.md) update and an issue recording the user's words separately from the agent's reading of them.
- **Acceptance:** the user has actually seen the delivered images and responded; the record names exactly which gates his response closes and which it cannot close.
- **Synchronisation point:** the user's response is the milestone; nothing dependent proceeds before it.
- **Status:** later milestone, not started.

M3 and M4 are derived from the roadmap's R1 exit contract (reproduction gate, then present the actual images and pause). Their finer internal work packages are not frozen here and are decided when their milestone is entered.

## M0 — contract freeze (this work package, documentation only)

- **Owner:** contract-freeze writer.
- **Scope:** `docs/drawing/roadmap.md` (fourth acceptance question), this plan, [issue 54](../issues/54-user-review-scope-hair-and-hand.md), `STATUS.md`.
- **Exclusions:** no drawing code, no artwork, no evidence directory, no script, no `AGENTS.md`, no `principles.md` edit.
- **Acceptance:** the roadmap lists the fourth question and no longer says three; this plan carries owners, acceptance and numeric budgets per work package; issue 54 records the advance; STATUS records the advance and points here; `git diff --check` is clean.
- **Budget:** 40 minutes wall clock, hard stop.
- **Status:** delivered as documentation; the advance gate is the parent's check, not a self-verdict.

## M1a work package — A v5 writer

- **Owner:** A-cloth writer (single writer, one worktree).
- **Writable path:** `.scratch/35-r1-articulated-study/evidence/A-cloth-v5/` only.
- **Read-only:** `STATUS.md`, `docs/`, every other evidence directory, all of `scripts/` (may read and import, never modify), all B artefacts, and the sealed/heldout material (not read at all).
- **Inputs:** registered teacher crop of `image.jpg`, source bbox `500,320,900,800` (400x480), copied into its directory as the only geometric reference; A v4 source under `evidence/A-cloth-construction-v4/` copied, never edited in place; `scripts/articulated_construction.py`, `scripts/ribbon_surface.py`, `scripts/figure_scaffold.py` (`hair_sheet`), `scripts/vector_visibility.py`.
- **Exclusions:** no hand or pose claim, no reference geometry outside the crop, no hand-drawn visibility cut or shortened outline for the second cuff, no third-party/vendor art reuse, no metric tuning, no edit of another package, no baseline promotion.
- **Required properties:** one continuous bow ribbon with width continuous through the knot; two whole sleeves with the second cuff's visible extent produced by the existing depth computation; one head-attached two-sided curved hair sheet whose layout and twist are re-derived from the crop rather than copied from S1's untested twist; per-part family modules authored in their own (u,v) frames with named seam anchors; an enforced seam contract (coincident boundary within epsilon, shared tangent) with a negative control that demonstrably fails the test before restoration; a README object inventory stating the one connected thing each named object is, and any deliberate split.
- **Acceptance (proved by command, art verdict excluded):** all package tests pass; the deliberately broken joint fails the seam test before restoration; both cuffs exist as components and the second one's visible extent is a depth result; the hair sheet has two distinct side fills; the bow strip's width is continuous through the knot; manifest hashes verify; the check bundle exists under the package directory.
- **Budget:** 120 minutes wall clock from the first tool call; intermediate checkpoint written into the directory at 100 minutes; hard stop at 120. No-progress cap: two distinct geometry hypotheses per acceptance item, then stop and report rather than trying a third. The writer never extends its own allocation.
- **Artefacts emitted:** `source/`, `tests/`, `artwork-a.svg`, `artwork-a.png` (400x480), `check/` bundle with `report.txt`, `manifest.json`, `manifest.sha256`, `README.md`, and the checkpoint file.
- **Stop and report:** if depth cannot occlude the second cuff, report that blocker instead of authoring the cut; if two hypotheses fail an acceptance item, stop and report unresolved rather than lowering it.

## M1b work package — B hand writer

- **Owner:** B-hand writer (single writer, one worktree).
- **Writable path:** `.scratch/35-r1-articulated-study/evidence/B-hand-v2/` only.
- **Read-only:** `STATUS.md`, `docs/`, all of `scripts/` (read/import only), every A artefact, and the sealed/heldout material (not read at all).
- **Inputs:** copied (never edited in place) `evidence/goal-recovery-r1-v2-completion/r1_scene.py`, `spatial_adapter.py`, `shape-grammar.md`, `teacher-observations.json`, the accepted sheet renders, and `evidence/B-caption-corrected-v1/` for the truthful caption text. B runs without a reference: `scripts/draw check` with no `--ref`.
- **Exclusions:** no reference imitation for B, no change to the approved concept, panel set, variation target or control offset, no manual visibility cuts between fingers, thumb, palm and dish, no caption claiming an unshown thumb or brace, no edit of another package, no baseline promotion.
- **Required properties:** palm, four fingers and a thumb built from tapered tube/strip primitives with their own anchors and individual pose, readable as separate digits at final size and not a traced contour table; grip contact derived from the dish geometry (palm cup supporting the underside, fingers/thumb closing on the rim enough to read as support), with README naming which contact is a geometric consequence and which is an author hypothesis; three panels preserved (baseline chest level, variation lifted + broader dish, control near miss); depth decides overlap.
- **Acceptance (proved by command, art verdict excluded):** construction tests for digit count, separation and taper plus the derived contact relation all pass; sheet and per-panel PNGs exist; digits are individually posed and separable; the contact relation is computed from the dish; captions make no claim the image does not show; manifest hashes verify; the reference-free check bundle exists.
- **Budget:** 120 minutes wall clock from the first tool call; checkpoint written into the directory at 100 minutes; hard stop at 120. No-progress cap: two distinct hand-construction hypotheses, then stop and report. The writer never extends its own allocation.
- **Artefacts emitted:** `source/`, `tests/`, three-panel sheet SVG + PNG and per-panel PNGs, `check/` bundle with `report.txt`, `manifest.json`, `manifest.sha256`, `README.md`, and the checkpoint file.
- **Stop and report:** if the derived contact cannot be made to read without a false claim, keep the truthful open-support reading, report the gap, and never restore the `thumb braces rim` caption.

## Review work packages

Every review is fresh-context and independent of the writer; the writer's own tests are in-slice evidence, not review. A reviewer receives the goal and acceptance, the exact image list and revision hashes, its exclusions, the mechanical results already obtained with the commands that produced them, and a finite budget — and nothing that would smuggle the writer's rationale into an image verdict. Reviewers write no source and no artwork; they return their report to the parent, and the integrator archives it verbatim with its hash.

### M1a-RV-IMAGE — A v5 image-only art and cohesion review

- **Owner:** fresh independent sight-capable reviewer.
- **Inputs:** the A v5 `report.txt` image list and the frozen PNG revision only; the reference crop for correspondence where the acceptance question is observed-part imitation. No writer README, source or rationale.
- **Questions:** for each of the four acceptance questions — construction/attachment/pose, physical geometry and visibility, drawing/art, object cohesion — what is wrong here? Name any object that reads as more than one disconnected piece, any second cuff that reads as an authored cut, and any region where the hair reads flat or single-sided.
- **Acceptance:** a verdict per acceptance question plus specific blocking/nonblocking findings located against the image coordinates, or an explicit BLOCKED for missing modality.
- **Budget:** 40 minutes wall clock, hard stop; one follow-up question round to the parent only.

### M1a-RV-STRUCT — A v5 structural and depth review

- **Owner:** fresh independent structural reviewer.
- **Inputs:** the A v5 source, tests, manifest and reports, the registered crop facts, and the frozen revision hashes. No art verdict requested.
- **Questions:** does the seam contract actually fail on the negative control; is the second cuff's surviving outline a depth computation rather than an authored shape; is the hair one two-sided sheet with projected-face fill selection; is the bow one continuous strip; do the manifest hashes and test results verify.
- **Acceptance:** each check re-run or re-derived with its command, a finding list with locations, and the unverifiable parts named.
- **Budget:** 40 minutes wall clock, hard stop.

### M1b-RV-IMAGE — B hand v2 image-only art and cohesion review

- **Owner:** fresh independent sight-capable reviewer.
- **Inputs:** the frozen three-panel sheet and per-panel PNGs with exact paths. No writer README or rationale.
- **Questions:** does the hold read in baseline and variation; do the digits read as separate digits at final size; does the hand read as one connected object with the arm and palm; does the control still read as a legible near miss; is any caption false against the image.
- **Acceptance:** a verdict per acceptance question with located findings, or BLOCKED for missing modality.
- **Budget:** 40 minutes wall clock, hard stop.

### M1b-RV-STRUCT — B hand v2 structural, depth and contact review

- **Owner:** fresh independent structural reviewer.
- **Inputs:** B hand v2 source, tests, manifest, and the frozen revision hashes; the approved concept/variation/control parameters.
- **Questions:** are digits and thumb constructed primitives rather than drawn marks; is the contact relation computed from the dish; is the control's gap produced by its frozen offset; does visibility come from depth; do the tests and hashes verify.
- **Acceptance:** each check re-run with its command, findings located in source and image, and the unverifiable parts named.
- **Budget:** 40 minutes wall clock, hard stop.

### Repair cycle

Each review round allows one scoped repair by the original writer followed by a re-review against the repaired revision and a fresh hash manifest; a repair that widens scope or touches another package is a new work package, not a repair. At two failed hypotheses or at budget, the writer preserves evidence, reports unresolved, and no gate is claimed.

## M1-INT — integration step

- **Owner:** integrator, independent of both writers.
- **Writable path:** `.scratch/35-r1-articulated-study/evidence/r1-advance-integrated-v1/` only.
- **Steps:** take only writer revisions whose reviews are complete and whose hashes are bound; copy the exact image sets and archived review reports; write one combined manifest; rerun the applicable tests and a reference-absent reproduction of each image; check cross-artefact consistency (one revision per image and report, captions truthful, no manual visibility cut introduced anywhere); record the open gates and the exact image list for the user.
- **Acceptance:** combined manifest verifies, reproduction matches, every review is bound to the delivered hashes, and the open-gate list is complete. The integrator merges and verifies; it does not decide art and does not waive a gate.
- **Budget:** 45 minutes wall clock, hard stop.
- **Artefacts emitted:** `images/`, `reviews/` (verbatim reports plus hashes), `manifest.json`, `manifest.sha256`, `reproduction.md`, `index.md`, and the user-facing image list.

## Sequencing, and what this plan does not authorize

M0 completes before M1a/M1b are read as contract. M1a and M1b are concurrent because their writable directories, references and artefacts are disjoint; neither may read the other's in-flight output. Reviews follow their writer; integration follows both review sets and is the only place the two are combined. M2 waits for the user; M3 waits for M1a, M1b and — when released — M2; M4 waits for M3.

This plan does not authorize: any drawing or code change outside the two writer directories, any edit to `AGENTS.md`, `principles.md`, the task freeze, scripts or evidence directories, any read of the sealed heldout, any baseline promotion, any push, or any claim that a milestone, review or gate has passed.
