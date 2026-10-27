# 4_USECASE — who does what, and in which flow: the drawing loop, the review protocol, the person's judgement gate, delegation

Commands and file layout are `9_IMPLEMENTATION.md`; what good means is `2_GOAL.md`; the rules the loop
follows are `3_REQUIREMENT.md`.

# EXPLICIT

## The judgement gate reads the drawing, not the distance to the reference

The person's reframe (P14) is the primary criterion: the goal is a proper drawing in a similar
style, not pixel or edge correspondence with one reference — "a proper drawing first, not
necessarily as close as possible". It is judged by looking at the full render and by fresh-eyes
critic review. Holistic semantic shapes outrank pixel correspondence, and a fragmented but "closer"
draft is worse than a coherent drawing. Zone-distance and edge metrics are weak regression signals
only: they catch accidental breakage, and they never become objectives to tune against.

The axes that a judgement is read on, the thresholds and the alarms built on those metrics:
`2_GOAL.md`.

## A review is built to be repeatable (user direction)

Scoring is refined on the person's direction into several axes, each with explicit and checkable
rules, so that two independent reviewers land within ±1 and a reviewer's disagreement is diagnosable
rather than vague.

# INFERRED

## What an advance is, and who is in it

An advance is studied from applicable vendor and local methods, constructs a bounded visible work,
varies it, preserves its successes and its failures, and reviews the actual image. Construction and
attachment, physical non-intersection, depth visibility, visual/art review and fresh-model transfer
establish distinct claims, and each is checked separately; colour and material follow only when the
structure supports it. A reference observation may seed semantic parameters and never runtime
geometry.

The drawing is authored by a model that may inspect images and outputs text and code only; a
teaching example, a generator, a test or a fresh-model attempt is supporting evidence, never a
substitute for a user-judgable rendered artwork, and generated image assets are not a substitute
either. A rescued learner attempt is not unaided transfer. Visual review requires actual image
modality and code cannot stand in for it: where that modality is unavailable the gate is marked
BLOCKED/UNVERIFIED and runtime repair does not become the objective.

The milestone and work-package contract that says when an advance is done is `0_ROADMAP.md`; the
acceptance questions `2_GOAL.md`; the invariants `3_REQUIREMENT.md`.

## The 2D drawing loop

The 2D resolver's own loop runs **observe → plan → draw → compare → reflect → revise**, cycled, with
line art first, colour second and soft fields last. It is the retired 2D resolver's workflow and it
must not override the spatial architecture or the milestone gates.

1. **Observe** — describe the target semantically in words first: subject, pose, composition,
   palette, what each region *is*. A drawing does not start by writing paths.
2. **Plan** — a shape inventory plus the draw order, painter's algorithm: background → body →
   clothes → hair → hat → face → details. The SVG layer structure mirrors that plan, and that is what
   makes the drawing explainable.
3. **Draw** — line art stage: strokes on region boundaries and on compact dark regions, no fill (this
   reference has no uniform black line art, see the T1 correction in `8_DETAIL.md`); big silhouette →
   medium structures → small details. Colour stage: fills against the palette swatches. Soft-field
   stage: gradients, blurred blobs, opacity, blend modes — last, never before structure.
4. **Compare** — one command over the whole bundle, then the bundle's image list goes to a
   fresh-context reviewer; for a targeted question, fall back to one region at a zoom. The commands
   are `9_IMPLEMENTATION.md`'s.
5. **Reflect** — a written note per iteration in the exercise's log: what was wrong, what changed,
   why. Each reflection ends by asking what the *transferable* principle is, and distils it into the
   principles document (`3_REQUIREMENT.md`).
6. **Revise** — edit the named paths, commit as a revision, re-run the comparison. The history is the
   learning curve; roll back when a "fix" makes the drawing worse.

## The rubric review protocol

1. **An independent reviewer, with no context.** A fresh subagent is given the target and the draft
   and *nothing else*: no history, no intent, no suspected verdict, and no sight of previous scores.
   It reads the rubric only (`2_GOAL.md`).
2. **Sight is proven before the verdict counts** (D18). The reviewer's first output is **three**
   checkable facts, each compared against a measurement already in the repo: the colour of the large
   field shape left of centre and roughly where its right edge stops (mint `#7dccc1`, right edge ≈
   x718); where the subject sits in the frame (seated, right of centre, head upper-right); and one
   named shape in the target's lower half (the salmon shard at ≈ x250–400, y700–950). A reviewer that
   cannot answer is not sighted, and its verdict is **void, not low** — the review is recorded as *not
   run*.
3. **Two independent reviewers, always.** A single review is recorded as *provisional*. A harness
   replay of a previous result is **not** a second opinion: the review is dispatched again, and the
   log says so.
4. **Agreement rule.** Axes differing by ≥2 between the two reviewers are **contested**, and a
   contested axis can pass or fail no milestone until it is settled — by measurement or by a third
   review. Axes differing by ≤1 are recorded as the mean and stand.
5. The vector is recorded in the exercise's log together with the bundle it was scored from.

## What a reviewer is given

- the target (`image.jpg`), or, for a region milestone, the target crop;
- the draft: the **1:1 draft first**, then the whole-frame side-by-side — a downscaled pane destroys
  exactly the detail being judged;
- for a region milestone, the region crop at full resolution, the target's and the draft's side by
  side, because the milestone is judged on the region it owns;
- nothing else.

## The reviewer's two free-text fields

The most valuable output of a review is two sentences: the **biggest single defect**, concrete and
checkable, and **the one change that would most improve it**. The second field is what the next
iteration works from.

## What the person is shown, and how an image is bound to a revision

The person judges a picture, not a report. What he is shown is the study's own 1:1
`check/draft-fullres.png`; the `check/draft.png` beside it is the same picture at thumbnail scale and
is not the picture to judge, because line weight and separation are visible only at 1:1.

An image is bound to a revision by its pinned hash together with the command that rebuilds it, so
that his judgement expires with the artefact: when the revision moves, the judgement refers to
nothing. Three rules follow, and each is a defect class when it is broken:

- **A rejected picture is not put in front of him.** A picture that its own review has already
  rejected is repaired first; the failing verdict has to be said in the same breath as the image, or
  the asking is dishonest.
- **The binding is printed by the reviewer, not remembered.** A reviewer resolves and prints its own
  binding line before it judges, and a review whose binding was moved under it — a commit landing
  inside the package it is reading — is ledgered per check rather than trusted.
- **The package names its own image.** A package's README names its own `check/draft-fullres.png` and
  the command that rebuilds it, so the rebuild is one hop from the picture; a package that does not is
  a recorded defect, not a revision moved under a review that is bound to it.

Each study is presented for his judgement once its own independent verdicts are in, as one frozen
revision with the verdicts beside it (`0_ROADMAP.md` owns that promise).

## Delegating the loop: the harness limits that shape a flow

The loop is executed by a parent that dispatches writers and reviewers, and the harness decides
whether a dispatch can do anything at all.

- **A writer budget fits inside the harness wall (P34).** A subagent run is killed at the wall —
  1,800,000 ms, about 30 minutes, observed here — so a budget larger than the wall is fiction: fit the
  package inside the limit or raise the timeout explicitly at dispatch, and have the writer commit a
  checkpoint every few minutes, because reaping (P35) takes uncommitted work without warning.
- **The deliverables are ordered so the package is true at any kill point (P34).** Source, renders,
  manifest and the check bundle first, documentation last: a kill then leaves a smaller package rather
  than a false one. The mechanical test for "this package is true" is a verified manifest plus the
  existence of every file it lists, run before any reviewer is dispatched.
- **Liveness is never read off a `status` field (P35).** A reaped run still reports itself as
  running. A dispatch is live while a process can be sampled, a new event timestamp appears and an
  artefact grows; no process, no new events and no new files is death, whatever the status says.
- **The dispatch script is committed before worktree-isolated children are launched.** Managed
  worktree isolation refuses a dirty tree, and writing the script is the dirt, so dispatch scripts are
  committed under a `plan:` message.
- **An image-only reviewer is paired with an execution-capable one (P36).** One judges the picture;
  the other re-runs the tests, the manifests and the negative controls and reports the commands that
  produced them. Pairing is not a substitute for the two independent reviewers on the image half.
- **The 1:1 image is named in the review dispatch, and the bundle is checked for currency.** A review
  dispatched at a thumbnail judges a thumbnail; a bundle older than the full-resolution image is stale
  evidence to regenerate, not evidence to dispatch.
- **A documented command is run before it is trusted (P38).** A command surface that cannot run is a
  gate failure, and the repair is declared dependencies, dynamically resolved paths and a wrapper that
  degrades to an available interpreter.
- **An absent verdict file means the verdict did not land.** The package is re-dispatched from the
  committed contract at no rebuild cost.
- **The run that carries a repair neither awards the art verdict itself nor lowers a threshold to
  make the repair pass.** A defect with no honest mechanical signature is reported upward as a
  contract problem, not met with a weakened test.
