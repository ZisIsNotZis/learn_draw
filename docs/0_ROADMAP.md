# 0_ROADMAP — the milestones and the promises they carry, the gates, the workpackage contract, where the project stands, and the next entry

This file owns *when* and *what is promised*. What good means is `2_GOAL.md`; why the work matters is
`1_PROBLEM.md`; the rules that bind every milestone are `3_REQUIREMENT.md`; who does what is
`4_USECASE.md`. A milestone is a user-perceivable artwork or a newly demonstrated visual capability —
never an engine, a test suite or a document — and it is current, reviewable and ready for the person's
judgement when it is called done. After each delivery, dependent work stops at the person's feedback
gate.

# EXPLICIT

**The bar for the current advance is "a full image".** His direction is to continue directly from the
body image that works, up to a whole figure, with the supervision of the build left to the drawing
agent — *"self-supervise (again, not you, that agent)"* — and with no return to the object studies
first.

**The 2026-10-27 direction: proceed.** *"Proceed strictly according to AGENTS.md in your system prompt
with goal in your mind. Redo roadmap if needed (I didn't check)."* The route is handed to the manager
and no verdict on the figure is given. That is not a pause, and it is not acceptance: the figure's
judgement remains his alone, and the advance that prepares the next revision does not wait for it.

# CONFIRMED

**The advance's order was agreed:** the object studies, then the articulated composition, then the
sealed reference-free drawing, then the integrated delivery, then his disposition. The object studies
are suspended at his direction (below), and the figure advance he asked for is a step of that same
road. The later milestones keep their promises; they are not renumbered to absorb the figure.

# INFERRED

## What the person's judgement is, and is not

The person judges; nothing else does. A metric, a self-review and an agent reviewer each produce
evidence; none of them produces a verdict of his, and no internal check is ever represented as his
judgement. A picture whose own review rejects it is not put in front of him, and a repair run neither
awards a verdict of his nor lowers a threshold to make a repair pass.

## A self-review is not a milestone gate

The figure package wrote its own accept line (`A-full-figure-v1/ACCEPT.md`, terms T1–T7) before its
build, and that was the right discipline for construction. It is not the gate. The milestone gate is
`2_GOAL.md`'s six-axis rubric, scored by two independent sighted reviewers on the 1:1 image, because a
term the author writes and clears at his own bar can be honest and still miss what a reader sees. The
previous "T6 cleared" was exactly that: an author's list that emptied at round 28, and an independent
pair then found the figure not seated, one-armed and background-deleted. A term is a craft instrument;
the rubric and the person are the verdict.

## How his delegation of the drawing judgement is bounded

His permission to self-supervise is a permission about craft, not about identity: the self-review of a
full image is written as a line of terms **before** the build, the terms are decidable by observation,
and a term that changes *what the figure is, where it is, or what it wears* is not cleared by moving the
term — it is cleared by changing the drawing. The self-review is never the author's opinion of the
author's own work: the picture still goes to a fresh-context reader, and a defect with no honest
mechanical signature is reported upward as a contract problem, never absorbed by weakening a test.

## Milestone path

### R1 — The whole figure (current advance)

R1's visible promise is one artwork: the reference's girl, whole, in her own 1024² frame. The object
studies (R1a) are suspended at the person's direction; the articulated composition (R1b) remains as the
original-composition study, but the reference-composition half of it is now delivered by R1c.

#### R1c — The whole figure, drawn — current

**Visible work:** one image, `A-full-figure-v2`, the same girl in the reference's frame, built from the
project's own parts by the project's own depth engine. It starts from `A-full-figure-v1`, which is
structurally whole — 31 objects, 57 parts, every one declared, every visible cut computed — and it
carries the drawing that the two independent reviewers of v1 found missing.

**What the v1 review pair found, and what R1c must make untrue** (records:
`.scratch/35-r1-articulated-study/evidence/reviews-r1c/`; vector A3 / B3–4 / C2–3 / D0–3 / E4–5 /
F1–3, with D and F contested):

1. **It does not read as seated.** The torso drops into a symmetrical bell; the dark mass sits detached
   at the left instead of across the lap. This is the largest single defect and it is identity-level.
2. **The hand is a mitten** at ~(845, 820): no fingers, no wrist, a circular blob at its top.
3. **The viewer-left shoulder/arm does not read as attached**; bow, sleeve, hair and torso collide at
   ~(585, 500).
4. **The background's composition is deleted**: the sweeping mint wave, the teal field and the floating
   ribbons are flat angular blocks; the mid-frame motion is gone.
5. **The face is wide-eyed and frontal** where the reference is shy and downcast; the eyes read as flat
   pink discs with specks, without lash weight or lid.
6. **The drawing is unstroked.** Most shapes are flat fills with no contour; the picture reads as
   stickers rather than as a drawing (`P13`, `P11`). The hair is two flat curtains with a square-cut
   streamer; the skirt is panels with straight fold lines.

**Method and transfer:** stroke the shape already owned before inventing a new one (`P13`); a hint that
does not fit the mental model is an upstream error (`invariant 3`), not a stroke to move. Build the
seated lower mass as a lap plane with the skirt crossing it and the navy underlayer carried beneath, not
as a separate polygon. Build the hand as a palm with finger masses and a thumb; build the left arm as an
arm from the sleeve, not as a gap to be covered. Re-cut the eyes as a lid, a lash, an iris under the
lid, a pupil and a catchlight, with the near/far sizes the three-quarter head already has. Background
from the observed masses: one sweeping mint wave whose boundary is a curve, the teal ground, and the
ribbon tails that cross it. Every shape stays a generator with at most about four landmarks; the
reference seeds the landmarks and is closed; depth decides visibility.

**Independent gates:** the six-axis rubric, two independent sighted reviewers on the 1:1 image, targets
A≥4, B≥4, C≥4, D≥4, E≥4, F≥4, the whole vector, no axis contested at Δ≥2 left unresolved; each
reviewer's biggest-defect field naming craft, not identity; the build deterministic, the suite green,
the manifest verified, no image read, and the similarity alarm measured if its optional dependencies are
present, or recorded as unavailable with the reason (it is a secondary alarm, never a gate). Then the
person's judgement.

**Scope/non-goals:** one figure, one frame. No new engine, no pose set, no reference-free task, no
baseline promotion, no metric tuning, no hand-typed station table, no change to another package's
bytes.

**Exit:** the vector at target on two independent reviews, alarms green, and the 1:1 image presented to
the person with what is done and what is not. That is a `need_user_review` milestone: the work that
does not depend on his eye continues, but the R1c advance closes only on his verdict.

**Risk/alternative:** the seated lower mass is the structural risk. Two distinct lower-mass hypotheses
are the limit; if both fail the seated read, the evidence is preserved and the gate is reported
unresolved rather than re-labelled. The hand has the same limit, and the earlier hand studies are the
record of two failed routes. A contested axis is settled by construction and a further review, never by
averaging.

**Status:** v1 reviewed by two independent sighted reviewers (records above). v2 is the advance. No art
verdict is claimed for v1, and none will be claimed for v2 by its author.

#### R1a — Object studies — suspended at the person's direction

**Visible work:** two images, each one object filling its frame — (A) the bow alone, imitating only the
reference's observed bow, with no torso/sleeve/hair/collar claim; (B) an original reference-free
hand-with-dish, with no head/torso/shoulder-join/arm-connection claim and no panel sheet.

**Method and transfer:** computed geometry from relations and vocabulary rather than hand-typed
contours; no author-specified visibility cuts, so depth decides; every mechanism claim carries a test
that fails when the mechanism is removed; the reference seeds A's parameters and is then closed.

**Independent gates:** per study, construction/attachment, physical geometry and depth visibility,
drawing/art, and object cohesion each judged separately on the actual image.

**User sees:** each study as a real authored image with its own independent verdicts, at its own
presentation — never a sheet, never a caption standing in for the picture.

**Scope/non-goals:** one object per image; no figure composition, no captions, no panel set, no sealed
heldout read, no metric tuning, no baseline promotion.

**Risk/alternative:** revise the construction hypothesis inside the study's finite budget; at two failed
hypotheses, preserve the evidence and report unresolved rather than lower an acceptance question. That
budget is spent; the suspension itself is the person's direction, above.

**Exit (unweakened, unmet):** both studies' four questions pass on one frozen revision each; a
reference-free study reproduces reference-free; one manifest binds each revision; each study is
presented for the person's judgement.

**Where it stands:** parked, not deleted. The bow's third image verdict failed on the reading — a knot
of abutting capsules rather than a strip that threads, junctions that stack rather than occlude — after
every mechanical class its reviews named was cured. A fourth attempt's **only** variable is the wrap's
route: how the one strip is walked so it threads through the knot and every junction crosses with one
piece in front of the other. Its tuning (widths, tone, palette, crease counts, stroke weight,
tessellation) is not a variable, and an attempt that changes anything else is refused as the next
thing.

The hand's fourth verdict found no depicted grip: an underside-only contact is by construction always
behind the plate, so the picture shows a dish in front of a bundle of straps. The rim-wrap experiment
that followed puts one digit pressing the dish's inner surface over the near rim and meets its measured
floor — 3527 px of mixed-order crossing against a floor of 2175, no rear contour broken — and the
reviewer still sees a pasted-on tab. The reason is stated and it is the working hypothesis: a crossing
reads as a wrap only where a **crest** above the rim's top edge, an **overshoot** of the pad past the
rim's inner corner, the **two-term order** and a **press** at the junction are visible at once, and the
rim-wrap has the second alone. The package that would build all four is cut and unlaunched; the floor,
the mixed-order rule and the joint route do not move for it.

Nothing here resumes until the person says so. The two studies' contracts — their canvases, artefacts
and acceptance — are `.scratch/35-r1-articulated-study/work/r1a-object-study-contracts.md`, and their
verdicts, the hypothesis and the cut package are records: `.scratch/35-r1-articulated-study/evidence/reviews-r1a/` and
`.scratch/35-r1-articulated-study/work/r1a-method-hypothesis.md` and `.scratch/35-r1-articulated-study/work/wave16-contracts.md`.

#### R1b — Articulated composition (deferred, not deleted)

**Visible work:** complementary actual images — (A) only the reference's perceptible
shoulder/upper-torso clothing and composition, with no hand/pose claim; (B) an original small clothed
upper-body bent arm/hand/prop interaction, with a meaningful variation and a labelled awkward control.
Not pose imitation; no vendor character reuse.

**Method and transfer:** abstract vendor construction semantics only; build the original B on actual
support and world binding and let project depth decide visibility; imitate only what is observed in the
reference. No matching pose photo is required for B, and B is not pose imitation or vendor character
reuse.

**Independent gates:** observed-part correspondence and visual art review; construction, hand-contact,
attachment and physical intersection; actual support and depth visibility; reference-absent
deterministic reproduction; heldout compatibility and distinctness; the person judges the actual
deliverables.

**User sees:** A and B as real authored images — not code, not parameter tables — including B's
baseline, variation and control; the heldout image only after its own gates. Each carries a distinct,
honest learning claim.

**Dependencies and reuse:** the current support/depth architecture and semantic primitives. World and
support mapping must be implemented rather than tagged, and no inferred 3D truth, no old figure
scaffold and no claim on old S1a readability or transfer may be carried in.

**Scope/non-goals:** bounded studies, not full anatomy, a finished portrait or infrastructure work; no
fabricated reference observation, no pixel tracing, no baseline promotion without its own gate.

**Exit:** A visibly imitates only observed features; B is an intentional readable original with a
meaningful variation and a control; support binding, attachment, contact, collision and depth each pass
separately; visual review and reproduction pass; evidence hashes bind one revision; then present and
pause.

**Risk/alternative:** if the hand and its contact stay unreadable or the geometry fails, revise the
representation inside the two-hypothesis budget; preserve the control and the evidence, and never hide
an intersection, invent an observation, drop A or B, or lower readability. At the limit, stop and report
the unresolved gates.

**Contracts:** `.scratch/35-r1-articulated-study/spec.md` and the public two-track freeze
`.scratch/35-r1-articulated-study/work/task-freeze.md`. The freeze's revision is pending independent
review and integrator approval; that is not art acceptance.

**Status:** its reference-composition half is absorbed by R1c; the original-composition half (B) has
not started, and no R1c result substitutes for B's conditions.

### R2 — Responsive components and pose variation

**Visible work:** a coherent multi-pose illustration or contact sheet of an upper-body figure, showing
hand and arm pose and hair or clothing response, with stable component identity and plausible
attachment.

**Method and transfer:** extend R1's accepted construction with continuous-time/response and
local-deformation ideas; compare fixed and responsive variants across an awkward contact and changed
proportions. Motion is a construction test, not video production.

**User sees:** a small set of genuinely varied, readable poses, and one clearly comparable
success/failure case.

**Independent gates:** attachment/pose, non-intersection, depth visibility, visual consistency and
reproducibility, each on actual images — then the person's feedback.

**Dependencies and reuse:** accepted R1 rules and the current spatial support/depth model; do not assume
an arbitrary collision solver or vendor painter-order visibility.

**Scope/non-goals:** a bounded pose set — not a film, not an audio/beat pipeline, not a full animation
engine, not generated assets.

**Exit:** changed pose or parameters produce coherent shape without per-frame hand editing; contact and
attachment stay plausible; intersection and occlusion gates each pass; visual identity survives the
variants; final images and reproduction evidence are hashed and reviewed. Present and pause.

**Risk/alternative:** if the responsive rules create implausible intersections, use a simpler explicitly
supported motion range, or keep the artwork static while preserving the same pose-variation and
readability result — a hidden collision is never acceptable. Replan after two distinct rule hypotheses.

### R3 — Reference-based composition and imitation

**Visible work:** a readable, composed character illustration modelled from the designated reference,
built from accepted semantic components (head, torso, arms and hands, clothing, hair, accessories),
with front and three-quarter views or another justified view pair.

**Method and transfer:** systematically apply the accepted vendor methods from the curriculum coverage
(visual grammar and focal hierarchy, scene and pose organization, component renderer and material
process where the structure supports it, and the review methods that hold up); compare reference-led
construction with a variation in pose, proportion or camera; keep source attribution and migration
evidence. No tracing as the endpoint.

**User sees:** the reference-inspired image plus a materially varied version, readable as one
intentional composition.

**Independent gates:** construction/attachment and collision; depth-derived visibility; whole-image
visual art review **and a line-versus-colour structure review** (separately); reference-free
deterministic re-render; component variation. The person's feedback is an explicit gate.

**Dependencies and reuse:** R1 and R2's accepted methods and the spatial architecture. The legacy M4j
assembly and Ex32 are historical controls, not accepted components and not a required starting
scaffold.

**Scope/non-goals:** one bounded character or composition; no promise of exact reference
reconstruction, no hand-entered dense contours, no baseline promotion without its own gate.

**Exit:** the composition is independently readable and coherent; variants preserve identity; the four
acceptance dimensions are documented separately; the reference is absent for reproduction; the final
review passes. Present and pause.

**Risk/alternative:** reference ambiguity is recorded and resolved as an explicit plausible
interpretation, never as recovered 3D truth. If the composition is too complex, reduce secondary detail
while preserving the core figure, its pose, attachment and art quality.

### R4 — Transfer to new subjects and original creation

**Visible work:** a bounded portfolio of frozen tasks — a held-out reference imitation, a substantial
variation or transfer to a different subject or proportions, and a reference-free original from a short
intent brief, culminating in a Starry-Night-class composition only when the prior results justify it.

**Method and transfer:** combine methods that show evidence of reuse across distinct cases; compare the
held-out reference and the original composition; preserve alternatives and failures; avoid target
leakage and pixel tuning. Vendor dispositions may change, but only against evidence.

**User sees:** the actual task-group artworks, including the reference-free original — never a claim of
universal mastery.

**Independent gates:** per artifact, construction/collision, depth visibility, art review and
reproducibility; a fresh ordinary-model transfer may be tested only with capability-qualified visual
access and a frozen payload and tasks. The person judges the resulting bounded body of work.

**Dependencies and reuse:** only reviewed, reusable rules from earlier slices the person accepted; no
assertion that old S1a transfer passed.

**Scope/non-goals:** a frozen, finite, representative task set; no claim of universal drawing ability,
no metric threshold as an art verdict, no image-generation service.

**Exit:** each predeclared task has an inspectable authored output and reproduction record; independent
reviewers can name what transferred and where it fails; the reference-free task is independently judged
a coherent original image; all results are presented for the person's judgement. Bounded evidence, never
proof of universal mastery.

**Risk/alternative:** if transfer fails, diagnose the missing construction or visual rule and return to
an appropriate slice — never rescue the frozen answer and call it transfer. If the modality or
capability is unavailable, report it unverified, preserve the artifacts and defer that gate.

**Naming note:** the older labels M2, M3 and M4 name a finer split of this same road — M2 the sealed
reference-free drawing (inside R4's reference-free task, still unread and still needing the person to
release it and authorize a creator role), M3 the integrated R1 delivery, M4 the person's recorded
disposition. Records that use those labels resolve here.

The retired 2D milestone sequence used the same letters for its own slices — M1 the composition, M2 the
head, M3 body and cloth, M4 the fields, M5 the withdrawal — and those are exercise history: they name no current
milestone, close no current gate, and do not describe current progress. A rubric example that cites "the
body milestone" means that retired M3, not this advance's M3.

## Workpackage and autonomy contract

Each milestone is decomposed into cohesive workpackages by category: (a) source/method study and
migration card; (b) semantic construction and geometry; (c) rendering and art direction; (d)
independent structure/geometry/depth proof; (e) visual experience and reproduction proof; (f)
integration and user-ready delivery. The categories are a coverage checklist, not one-file tasks;
complete coverage is defined before dispatch.

For each workpackage record objective, source inputs, exact outputs and acceptance, exclusive artifact
and file ownership, interfaces, dependencies, genuinely parallel seams, exclusions, owner, integrator
and reviewer. Shared scene contracts and render artifacts have exactly one writer. Construction may run
alongside source study only on stable interfaces; geometry, depth and experience checks consume the same
final revision; integrate before the whole-slice review. One writer maintains tightly coupled roadmap
and coverage facts — never two writers across that seam.

The integration owner binds source, artifact and evidence hashes and commands to the final revision.
A fresh independent reviewer checks every milestone artifact and its consistency, and a visual reviewer
must prove sight before scoring. The person's acceptance follows presentation and is neither delegated
nor inferred. Failures and prior evidence are preserved. Two distinct structural approaches per
milestone, at most; after the limit, stop and report unresolved rather than lower an acceptance
question. No attempt cap turns a failure into a pass.

Workers choose vendor methods, implementation detail, work split and low-level alternatives freely
inside this contract; they may not waive the person's feedback gate, redefine art acceptance, claim
unreviewed visual evidence, change locked architecture, or put runtime work in the product's place.
Routine internal choices do not go to the person.

**Limits that bind a package.** Candidate and repair limits are not a house number: they are written in
the concrete workpackage contract that owns them — the two-track freeze
(`.scratch/35-r1-articulated-study/work/task-freeze.md`), the object-study contracts
(`.scratch/35-r1-articulated-study/work/r1a-object-study-contracts.md`), and each wave's contract file. A limit must be auditable in the
file that sets it, and no attempt cap turns a failure into a pass.

## The R1c workpackages

**W1 — contour, hand, far arm — landed at `e974d4e`.** One writer applied the line policy, re-cut the
eyes as lid/lash/sclera/iris/pupil/catchlight, gave the hand four finger masses and a thumb, and routed
her right arm from the viewer-left cuff. The contour pass proved too broad: outlining same-garment
panels turns the torso and skirt into a polygon mesh. Its stage-3 image review is **void as a score**
(its descriptions of the eyes and bow are not of that revision) but true on three structures: the
panel seams, the detached lower mass, the flat background
(`evidence/reviews-r1c/A-full-figure-v2-stage3-image-review-1.md`). No art verdict is claimed for the
stage.

**W2 — lines that are art lines, the face, the seated lap, the field and the hair** (owner: one writer,
`A-full-figure-v2`, from `e974d4e`). Objective: the figure reads as a drawn, seated girl in the
reference's composition. Do, in order: (a) keep contours on the outer silhouette, on boundaries between
different objects, on the hand's digits and on a few real folds, and remove the strokes that merely
outline internal same-garment panels; (b) re-cut the face from the reference's measured geometry — the
far eye smaller, a heavier lash, the iris under the lid, a narrow chin, the fringe over the brow;
(c) build the lap plane with the skirt crossing it, the deep-teal underlayer connected beneath, the hem
trim following the skirt, and the lining ribbons crossing the teal; remove the detached slab; (d) make
the mint field's boundary a sweeping curve, with the teal ground and two or three floating ribbon tails
behind the figure; (e) give each hair fall a curved lit/shade boundary, strand lines, a broken inner
edge and a tapered streamer end. Non-do: no coordinate table over four landmarks, no authored depth
cut, no metric tuning, no baseline promotion. AC: (a) no 1:1 outline seam around same-garment panels;
(b) at 4× a heavy lash, lid, sclera, iris under the lid, pupil, catchlight, a smaller far eye and a
narrow chin; at 1:1 a downcast expression; (c) a lap with the skirt across it and the navy layer
beneath, detached slab gone; (d) a curved mint boundary and two floating ribbon tails; (e) two tones,
strand lines and a non-straight inner edge per fall, a tapered streamer; plus the build deterministic,
the manifest verified, no image read, the suite green, and no shape over four typed landmarks.
Status: dispatched.

**W2b — the lap's dark mass, the face, the bow, the hair, the field's curl** (owner: one writer,
`A-full-figure-v2`, from `90ff009`). The v2 pair is in and short of the targets on A, C and D
(`evidence/reviews-r1c/`); both reviewers name the same repairs. Do: (a) re-tone the lower mass to the
reference's truth — the dominant lower field is the dark navy/teal skirt across the lap and bottom, the
pale mint apron panels sit on top of it, the navy hem borders them and the pink/orange ribbons cross
the dark; the pale wedge is not the lap; (b) re-cut the face — the gaze down, the upper lash heavy, the
iris under the lid with little exposed sclera, a soft rounded jaw and chin rather than a V, curved bangs
with a few points instead of a jagged W, a short readable nose and mouth; (c) make the bow two soft
loops off a knot with two tapering tails and creases that follow the cloth, not an extruded tube;
(d) give the hair fewer, broader, curved locks with a lit/shade boundary and tapered ends; (e) restore
the reference's left wave curl and the mid-frame streamers as masses, not thin noodles. Non-do: no
new engine, no shape over four typed landmarks, no authored depth cut, no metric tuning, no baseline
promotion; keep the hand, the far arm, the occlusion and the contour selection. AC: (a) at 1:1 the
largest lower field is dark, the apron sits on it and the lap reads as a lap; (b) a 4× crop shows a
downcast lidded eye with a heavy lash and little sclera, a soft chin, curved bangs; (c) the bow reads as
two loops, a knot and two tails; (d) the hair has broad curved locks, not rails; (e) the left curl and
the streamers are visible masses; plus the build deterministic, the manifest verified, no image read,
the suite green, no shape over four typed landmarks. Status: dispatched.

**W3 — the independent review and the presentation** (owner: manager; two fresh image reviewers + one
execution reviewer). Objective: a verdict on the repaired revision by the rubric. Outputs: two review
records in `evidence/reviews-r1c/` bound to the new hashes; a presentation of the 1:1 image to the
person with what is done, what is not, and what to look at. AC: two sighted reviewers, no unresolved
Δ≥2 axis, alarms green, the image in front of the person. Status: waits for W2b.

**W3 — the independent review and the presentation** (owner: manager; two fresh reviewers + one
execution reviewer). Objective: a verdict on W2's revision by the rubric. Outputs: two review records
in `evidence/reviews-r1c/` bound to the v2 hashes; a presentation of the 1:1 image to the person with
what is done, what is not, and what to look at. AC: two sighted reviewers, no unresolved Δ≥2 axis,
alarms green, the image in front of the person. Status: waits for W2.

## Historical mapping

The stage names S0–S3 are historical identifiers, not gates and not a binding sequence. Old S0's bounded
visibility work is a technical result, not an artwork milestone. Old S1a's construction teaching
artifact was accepted only as a code and method artifact: its perception/readability and its
learner-transfer gates remain open and unrun. `Ex32` is old scaffold pose rotation and local attachment
repair, not a figure or character pass, and old S1b, S2 and S3 labels map to no passed milestone.
Records of all of it are preserved under `.scratch/`, with the retired docs in `.scratch/history/`; old
drawing iterations are not repaired.

## Current state

**The current advance is R1c**, the whole figure drawn. `A-full-figure-v1` is structurally whole: 31
objects, 57 parts, every one declared, 4,739 faces, every visible cut computed by the depth engine, the
build byte-identical on rebuild, no image read. Its own accept line T1–T3/T5/T7 passes; T4 is partial.

**Its review pair, independent and sighted, put the picture at A3 / B3–4 / C2–3 / D0–3 / E4–5 / F1–3**
with D and F contested (`evidence/reviews-r1c/`). The pair's agreement, independent of the rubric, is:
the hand is a mitten; the viewer-left shoulder is unreadable; the background composition is deleted;
the face is frontal and wide-eyed; and — the strongest — **the figure does not read as seated**, because
the dark lower mass sits detached at the left of a symmetrical dress bell. That last one is identity,
not craft, and the v1 self-review's "T6 cleared" missed it. **No art verdict is claimed.**

**W1 has landed** at `e974d4e` (`A-full-figure-v2`): a contour pass, layered eyes, a hand with four
finger masses, and her far arm from the cuff. The pass was too broad — same-garment panels got outlines
and read as a mesh — and the face is still frontal; W2 owns both, with the seated lap, the field and the
hair.

**W2 has landed** at `90ff009`, and its independent pair puts it at **A3 / B4 / C3 / D1–3 (contested) /
E4–5 / F3–4** — progress on B, C and F, still short of A, C and D. Both reviewers name the same thing:
the lower half is a pale wedge, the dark lap mass is a strip, so she still does not read as seated; the
face is startled, the bow a tube, the hair rails, and the left wave curl is a noodle. W2b is that
repair.

**The recorded ratchet floor is unchanged** and is a flat-2D artifact
(`.scratch/00-tooling/baseline/`, recorded from the 2D assembly): the full figure is reference-free and
does not compare against it, and no structural sketch replaces it.

**Open gates, none closed by the figure:** the R1c rubric gate; integrated R1 acceptance;
reference-absent reproduction at the integrated level; heldout compatibility and release; transfer; and
the person's judgement at a real gate. The sealed brief
(`.scratch/35-r1-articulated-study/work/holdout-brief.sealed.md`) stays unread until he releases it and
authorizes the creator role.

**Next entry:** W2b in flight, then W3. If W2's revision does not reach the targets on the pair, the
next advance is the largest remaining defect it names, on v2's source; the person is given the image
only once its own reviews no longer reject it. If the person names a defect, it becomes the next
advance on the current package; the part library stays copied byte-for-byte.
