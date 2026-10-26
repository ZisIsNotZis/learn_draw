# Roadmap — learn to make readable, expressive programmatic art

`STATUS.md` owns observed current state and next entry; [`spatial-model.md`](spatial-model.md) owns spatial architecture; [`vendor-learning-map.md`](vendor-learning-map.md) alone owns vendor-source coverage and migration dispositions. This roadmap owns the product goal, milestone promises, gates and work-package contract. Historical evidence and decision rationale live in exercise tickets, not current-fact documents.

## Product goal and invariants

Learn by reference study, imitation and deliberate variation to create explainable, readable, artistically coherent programmatic illustrations, eventually making reasonable original work without a reference (including a Starry-Night-like challenge). Treat local vendor examples as a curriculum to systematically assess and absorb all useful non-image-generation methods, combining proven methods with existing primitives, 3D support surfaces and depth visibility. Vendor content is not presumed correct or already learned. Models may inspect references but author text/code only; no generated images, sprites or pixel-metric optimization. A reference teaches, it is not runtime geometry.

A milestone is a user-perceivable artwork or newly demonstrated visual capability, not an engine, test suite or document. The artifact must be current, reviewable, and ready for the user's judgment. After each delivery, stop dependent work at the user feedback gate. Internal study, methods, work-package sequencing and technical replanning are project-autonomous; do not ask the user to decide internal plans. Never represent internal checks as the user's judgment or promise art success in advance.

Keep four acceptance questions distinct:
1. **Construction/attachment/pose:** do named parts form plausible connected objects and attach in a readable pose?
2. **Physical geometry and visibility:** are solids/surfaces free of illegal intersections (or is a designed bend/contact explained), and does depth independently hide the physically farther surface? Correct occlusion does not excuse interpenetration; a hair strand entering a head/body must be plausibly divided/deformed or routed clear.
3. **Drawing/art:** does the actual rendered image read clearly and feel compositionally/artfully coherent, with intentional line and colour treatment?
4. **Object cohesion:** does every named object read, in the actual rendered image, as one connected visible thing, with any intentionally split object documented as a deliberate split? This is separate evidence from construction, geometry and art, because a drawing can pass all three while one object still renders as two detached pieces and only the image shows whether it reads as one thing.

Each relevant gate requires its own evidence. Geometry/code cannot establish visual quality. Experience checks use real rendered visual artifacts and a qualified sight-capable independent reviewer; actual experience is not runtime-enforced. Missing modality is BLOCKED/UNVERIFIED, never PASS. Metrics are alarms only.

## Milestone path

Stage names below are new roadmap identifiers; old S0–S3 names are historical facts, not completed gates or binding sequence. Methods/packages may be replanned without lowering product outcomes. Every stage has a vertical visible deliverable.

### R1 — Readable articulated study

R1 splits into R1a object studies and R1b articulated composition by the user's approved scope decision ([issue 55](../../.scratch/35-r1-articulated-study/issues/55-r1a-object-study-scope.md)). The four acceptance questions above apply unchanged to both, and R1a passing does not satisfy R1b.

#### R1a — Object studies — suspended by the person's direction of 2026-10-23

The person named the body image (`A-cloth-v8/artwork-a.png`) as the one output that works and ordered it
continued directly until a full image, self-supervised. That direction replaces the object studies as the
current advance: the bow study is parked after three failed image verdicts, the hand study after four, and
neither is resumed or replaced until he says otherwise. The full figure it produced is
`evidence/A-full-figure-v1/`; R1a's own exit line below is unweakened and unmet.

- **Visible work/capability:** two actual images, each one object filling its own frame: (A) the bow alone, imitating only the reference's observed bow, with no torso/sleeve/hair/collar claim; (B) an original reference-free hand-with-dish, with no head/torso/shoulder-join/arm-connection claim and no panel sheet.
- **Method and transfer:** computed geometry from relations and vocabulary rather than hand-typed contours; no author-specified visibility cuts, so depth decides; a mechanism claim carries a test that fails when the mechanism is removed; the reference seeds A's parameters and is then closed, so the build reads neither the crop nor any metric at runtime.
- **User sees:** each study as a real authored image with its own independent verdicts, at its own user presentation.
- **Independent gates:** per study, construction/attachment, physical geometry and depth visibility, drawing/art, and object cohesion each judged separately on the actual image.
- **Scope/non-goals:** one object per image; no figure composition, no captions, no B panel set, no sealed heldout read, no metric tuning, no baseline promotion.
- **Exit:** both studies' four acceptance questions pass on one frozen revision each; a reference-free study reproduces reference-free; one manifest binds each study's revision; each study is presented for the user's judgment. R1a passing does not satisfy R1b.
- **Risk/alternative:** if an object still does not read, revise the construction hypothesis inside that study's finite budget; at two failed hypotheses preserve the evidence and report unresolved rather than lowering an acceptance question.
- **Contracts:** the two study contracts, including canvases, artefacts and acceptance, are owned by [`r1a-object-study-contracts.md`](../../.scratch/35-r1-articulated-study/work/r1a-object-study-contracts.md).

#### R1b — Articulated composition (deferred)

The original R1 composition, deferred not deleted: it starts once both R1a studies pass, and its exit conditions below are unchanged and unweakened.

- **Executable R1 work-package contract:** [`R1 task contract`](../../.scratch/35-r1-articulated-study/spec.md) and public [`two-track task freeze`](../../.scratch/35-r1-articulated-study/work/task-freeze.md) define owners, interfaces, evidence and finite budget; task-freeze revision is pending independent review/integrator approval, not art acceptance.
- **Visible work/capability:** complementary actual images: (A) imitate only perceptible shoulder/upper-torso clothing/composition in `image.jpg`, with no hand/pose claim; (B) apply vendor MIT semantic IK/taper method to an original small clothed-upper-body bent arm/hand/simple-prop illustration, with meaningful changed-target/proportion variant and labeled awkward control. No matching pose photo required for B; it is not pose imitation or Huashu character reuse.
- **Method and transfer:** abstract vendor construction semantics only; build original B using actual support/world binding and project depth visibility. A genuinely imitates observed reference parts. Keep independent sealed heldout reference-free drawing gate and require its owner to check compatibility/distinctness before release.
- **User sees:** A and B as real authored images (not code or parameter tables), including B's baseline/variation/control; separate heldout image only after its gates. Each has a distinct, honest learning claim.
- **Independent gates:** observed-part correspondence/visual art review; B construction/hand-contact/attachment and physical intersection; actual support/depth visibility; reference-absent deterministic reproduction; heldout compatibility/distinctness and review; user judges actual deliverables. No successful user feedback assumed.
- **Dependencies/reuse:** current support/depth architecture and semantic primitives; world/support mapping must be implemented rather than tagged. No inferred 3D truth, old figure scaffold, or claim old S1a readability/transfer.
- **Scope/non-goals:** bounded studies, not full anatomy/finished portrait/infrastructure work; no fabricated reference observation, matching extra pose-photo requirement, pixel tracing, or reuse of vendor Huashu character, frames or coordinates.
- **Exit:** A visibly imitates only observed features, B is an intentional readable original image with meaningful variation/control, heldout remains a separate compatible reference-free drawing gate; actual support binding, attachment, contact, collision and depth each pass separately; visual review and reproduction pass; evidence hashes bind one revision. Then present actual images and pause.
- **Risk/alternative:** if hand/contact is unreadable or geometry fails, revise representation within the finite two-hypothesis budget including already completed provisional code prep. Preserve control and evidence; do not hide intersection, invent observations, drop A/B, or lower readability. At limit, stop and report unresolved gates.
- **Status:** deferred until both R1a studies pass; nothing in R1b has started, and no R1a result satisfies or substitutes for any condition above.

### R2 — Responsive components and pose variation

- **Visible work/capability:** a coherent multi-pose illustration/contact sheet of an upper-body figure showing hand/arm pose and hair or clothing response, with stable component identity and plausible attachment.
- **Method and transfer:** extend R1 accepted construction using useful vendor continuous-time/response, local deformation and semantic renderer ideas; compare fixed/static and responsive variants across an awkward contact plus changed proportions. Distinguish motion as a construction test from video production.
- **User sees:** a small set of genuinely varied, readable poses and a clearly comparable successful/failure case.
- **Independent gates:** separate attachment/pose, non-intersection, depth visibility, visual consistency/readability, and reproducibility reviews on actual images; user feedback gate after delivery.
- **Dependencies/reuse:** accepted R1 rules and current spatial support/depth; do not assume arbitrary collision solver or vendor painter-order visibility.
- **Scope/non-goals:** a bounded pose set, not a film, audio/beat pipeline, full animation engine or generated assets.
- **Exit:** changed pose/parameters produce coherent shape without per-frame hand editing; contact and attachment remain plausible; intersection and occlusion gates each pass; visual identity survives variants; final images/reproduction evidence are hashed and reviewed.
- **Risk/alternative:** if responsive rules create implausible intersections, use a simpler explicitly supported motion range or keep the artwork static while preserving the same pose-variation/readability result; never call hidden collisions acceptable. Replan after two distinct rule hypotheses.

### R3 — Reference-based composition and imitation

- **Visible work/capability:** a readable, composed character illustration modeled from the designated reference, built from accepted semantic components (head, torso, arms/hands, clothing, hair, accessories) with front/three-quarter views or another justified view pair.
- **Method and transfer:** systematically apply accepted vendor methods from the coverage map, including visual grammar/focal hierarchy, scene/pose organization, component renderer/material process when structure supports it, and useful quality/review methods. Compare reference-led construction with a variation in pose/proportion/camera; retain source attribution and migration evidence. No tracing as endpoint.
- **User sees:** the actual reference-inspired image plus a materially varied version, readable as one intentional composition.
- **Independent gates:** construction/attachment and collision; depth-derived visibility; whole-image visual/art review and line-versus-colour structure review; reference-free deterministic re-render; component variation. Human feedback is an explicit gate.
- **Dependencies/reuse:** R1/R2 accepted methods, spatial architecture; legacy M4j and Ex32 remain historical controls, not accepted components or required starting scaffold.
- **Scope/non-goals:** one bounded character/composition; no promise of exact reference reconstruction, no hand-entered dense contours, no baseline promotion without its separate gate.
- **Exit:** composition is independently readable and coherent, variants preserve identity, all four acceptance dimensions separately documented, reference absent for reproduction, final review passes. Present and pause for user response.
- **Risk/alternative:** reference ambiguity is recorded and resolved as an explicit plausible interpretation, not false recovered 3D truth. If composition is too complex, reduce secondary detail while preserving the core figure, pose, attachment and art quality.

### R4 — Transfer to new subjects and original creation

- **Visible work/capability:** a bounded portfolio of frozen tasks: a held-out reference imitation, a substantial variation/transfer to a different subject or proportions, and a reference-free original illustration from a short intent brief (culminating in a Starry-Night-like composition challenge only when prior results justify it).
- **Method and transfer:** combine methods with evidence of reuse across distinct cases; compare held-out reference and original composition, preserve alternatives/failures, avoid target leakage and pixel tuning. Vendor map dispositions may evolve with evidence.
- **User sees:** the actual task-group artworks, including reference-free original, not a claim of universal mastery.
- **Independent gates:** each artifact gets appropriate construction/collision, depth visibility, visual/art review and reproducibility; fresh ordinary-model transfer may be tested only with capability-qualified visual access and frozen payload/tasks. User judges the resulting bounded body of work.
- **Dependencies/reuse:** only reviewed reusable rules from earlier user-accepted slices; no assertion old S1a transfer passed.
- **Scope/non-goals:** frozen, finite representative task set; no claim of universal drawing ability, no metric threshold as art verdict, no image-generation service.
- **Exit:** each predeclared task has inspectable authored output and reproduction record; independent reviewers can identify what methods transferred and where they fail; reference-free task is independently judged as a coherent original image; all results presented for user feedback. This is bounded evidence, not proof of universal mastery.
- **Risk/alternative:** if transfer fails, diagnose missing construction/visual rule and return to an appropriate visible slice; do not rescue the frozen answer and call it transfer. If capability/modality unavailable, report unverified, preserve artifacts and defer that gate.

## Work-package and autonomy contract

Each milestone is decomposed into cohesive WPs by category: (a) source/method study and migration card; (b) semantic construction/geometry; (c) rendering/art direction; (d) independent structure/geometry/depth proof; (e) visual experience/reproduction proof; (f) integration and user-ready delivery. Categories are a coverage checklist, not mandatory one-file tasks. Define complete coverage before dispatch.

For each WP record objective, source inputs, exact outputs and acceptance, exclusive artifact/file ownership, interfaces, dependencies and genuinely parallel seams, exclusions, owner, integrator and reviewer. Shared scene contracts/render artifacts have one writer. Construction can run alongside source study only on stable interfaces; geometry, depth and experience checks consume the same final revision/artifact; integrate before whole-slice review. A single writer maintains tightly coupled roadmap/coverage-map facts; do not split simultaneous writers across this seam.

Integration owner binds source/artifact/evidence hashes and commands to final revision. Fresh independent reviewer checks all milestone artifacts and consistency; visual reviewer must actually inspect images and establish sight capability. Human/user acceptance follows presentation and is not delegated or inferred. Preserve failures and prior evidence. Per milestone allow at most two distinct structural approaches; after no useful evidence or limit, stop, document unresolved outcome and replan at product-goal level, never silently reduce acceptance. No attempt cap makes failure a PASS.

Workers autonomously select vendor methods, implementation details, work split and low-level alternatives inside this contract. They cannot waive user feedback gates, redefine art acceptance, claim unrun visual/experience evidence, change locked architecture/authority, or use runtime work as the product. Routine internal choices do not go to user.

## Historical mapping and current state

Old S0 bounded visibility geometry is a technical result, not an artwork milestone. Old S1a construction teaching artifact was independently accepted only as code/method artifact; S1a perception/readability and transfer remain OPEN/UNRUN. Ex32 is old scaffold pose rotation and local attachment repair, not a human/figure PASS. Old S1b/S2/S3 labels do not map to passed new milestones. Preserve all original records/evidence; do not repair old drawing iterations. Detailed vendor coverage is in [`vendor-learning-map.md`](vendor-learning-map.md). Current entry and blockers are in STATUS.
