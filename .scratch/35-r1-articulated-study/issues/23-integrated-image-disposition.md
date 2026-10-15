# Issue 23 — integrated reset image disposition

**Disposition: R1 resource-blocked / unverified; no repair authorized or performed.** This is an image-review disposition, not art acceptance or whole-objective failure. It closes only the fresh image-observation verification requested for the final integrated reset.

## Revision and evidence reviewed

- Candidate: `.scratch/35-r1-articulated-study/evidence/integrated-reset-r1-v1/`.
- Structural/dataflow gate: issue [22](22-integrated-reset-structural-review.md), PASS for structural integration only. It expressly does not assess visual legibility or art.
- Fresh image observations: `/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/70793b55-11cc-406f-870b-673ea2c0f4a0/r1/integrated-image-observations.md`.
- Examined actual image-list artifacts: `checks/A/side-by-side.png`, `checks/A/draft-fullres.png`, registered `reference-crop.png`, `checks/B/draft.png`; source `r1_scene.py`, contract `spec.md`, manifest and A/B check reports.
- A registration in `manifest.json`: crop `(500,320)-(900,800)`, 400x480, no resize/stretch. Source and crop hashes are recorded there. A reference crop and draft are shown at same 400x480 dimensions in the side-by-side image. The comparison supports the visual claims below; image metrics were not used as objectives.

## Claim dispositions

### A — scope boundary and observed garment

- **Accept — visible garment silhouette/mass mismatch.** The registered reference crop shows a shaped torso/shoulder garment and distinct right sleeve contour; the rendered A is dominated by a broad, nearly rectangular rounded pale body mass with a large isolated-looking right-side lobe. The draft's rightmost contour (approximately x=321–380, y=205–382 in crop coordinates per authored shape landmarks) is not a clearly articulated sleeve-to-bodice contour comparable to the visible source sleeve. This is within required A observed shoulder/upper-torso garment context, not a demand for the entire character.
- **Accept — collar/shoulder relation insufficiently expressed.** Source crop visibly places a layered collar/neckline along the sloped shoulder/upper chest, with dark edging. Draft collar controls occupy a shallow horizontal band around y=344–387 and the emitted visual reads as a separate flat strip, not a clear shoulder/collar/bodice connection. This is inside the required garment contour/connection scope.
- **Accept — bow relationship/proportion/context weak.** Bow is identifiable, but its regular loops/round central knot and large simple tails read as an overlay on the broad body, rather than sitting as folded cloth on the chest. Source bow is irregular and embedded in neckline/torso context. The reviewer observation of overly large bow and stiff attachment is supported qualitatively by the paired image.
- **Accept — horizontal trim issue.** Draft has a long dark band across the lower body (source lines at y≈62–108 in the crop coordinates); the registered reference at that location does not show a matching uninterrupted broad band. It is a within-scope garment-context discrepancy, though not a newly discovered source-code defect.
- **Not applicable to current A scope — missing full head/hair/hand/forearm.** Task freeze and integrated spec explicitly limit A to observed shoulder/upper-torso clothing/composition and explicitly forbid fabricated hand/pose claims. The reference crop happens to include hair and hands, but those are not required A subjects. Their absence alone is not an A defect and must not widen A into a full-character imitation. This does not negate the relevant garment/sleeve/collar discrepancies above.
- **Accept in bounded sense — neighboring overlap cues are weak where they define garment edges.** Hair itself is out of scope, but the visual observations that source-side shoulder/sleeve and dark garment-edge transitions are clearer than draft-side pale empty contours are relevant to the required neighboring garment context. Do not infer a requirement to draw hair or hands from this observation.

### B — hand shape and prop action

- **Accept — genuine hand-shape/contact readability defect, not merely an unsupported claim about a reference hand.** B is an original-action artwork and has no reference pose claim. In the actual panel image, each hand is a small rounded terminal shape, the two authored finger marks appear as short near-horizontal lines, and the hand/prop boundary reads as tangency/adjacency rather than fingers visibly wrapping around a prop. The visual action is not independently clear as grip or support.
- **Structural qualification:** manifest and issue 22 establish semantic contact/target and bounded collision/gap checks, and controls include finger segments ending near the contact point. Those are structural facts, not a visual hand-shape verdict; they do not contradict the visual failure. No general 3D collision proof is claimed.
- **Accept — variation/control observation.** The three panels preserve a recognizable arm pose family; the variant changes pose/shoulder width, and control is labeled. But the same indistinct terminal hand/contact persists, while the control's separated horizontal lines reinforce a geometric-connector reading. This is a visual gate failure, not evidence that semantic variation tests failed.

## Repair disposition and budgets

**No single source-local P1 repair is evidenced.** The verified A mismatches are compositional shape/garment-art shortcomings across several components (bodice/sleeve, collar connection, bow treatment, lower trim); B requires a clearer articulated hand shape and convincing contact integration. The scene source confirms these are intentionally sparse semantic shape inputs and B finger line marks, not a one-line rendering/visibility/dataflow bug. A meaningful correction would require a new art-shape/hand-design hypothesis and likely coordinated changes across components; that is not the contract's one evidence-backed P1 repair. The contract's scoped 20-minute repair allowance is not permission to introduce a new art hypothesis, redraw the whole work, or use a demo to test one. No repair, additional render, or automatic continuation was undertaken.

Remaining 15-minute independent image-review allowance is not authorization for another reset. The integrated writer's separate manifest records 2706 seconds (45m06s) against the 90-minute cap; command-level times for most commands were not recorded. This disposition did not run drawing, rendering, or tests, and cannot reconstruct prior per-command time. The scoped repair allowance remains unused, not converted to an extension. No stage/commit was performed; pre-existing staged entries remain `.gitmodules`, `vendor/huashu-art-motion`, and `vendor/huashu-design`.

## Handoff / gates

This final bounded reset has failed its independent image-quality gate for the stated R1 artwork targets. Therefore **R1 remains resource-blocked / unverified**, not PASS and not whole-objective failure. Do not continue automatically, roll budgets forward, propose another reset/demo, or claim user-ready delivery. No artwork gate is accepted by this disposition.

Revision-bound evidence retained: integrated candidate manifest and hashes; eight structural/dataflow tests and independent issue 22 PASS; independent A/B image observations and this claim-by-claim verification. Still open: garment/context visual/art quality; B visual hand/contact readability; independent construction/support/contact/general collision/depth gates beyond existing bounded tests; heldout compatibility/release/distinct drawing; deterministic reproduction as an acceptance gate; user feedback and final integrity. Existing structural PASS does not close these gates. Main should tell the user plainly that no artwork was delivered/accepted and report the bounded resource-blocked state, without transferring responsibility for technical next steps to the user.
