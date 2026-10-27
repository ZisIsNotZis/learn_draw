# 3_REQUIREMENT — the binding rules and constraints: P1–P41 and the invariants they distil

This file owns the rules and what they forbid, not how one is implemented or which command checks it
(`9_IMPLEMENTATION.md`), not the architecture they constrain (`6_ARCHITECTURE.md`), not the gates that
decide a milestone (`2_GOAL.md`, `0_ROADMAP.md`), not the flow a review runs in (`4_USECASE.md`).

# EXPLICIT

**Silhouette, outline and object.**

## P13 — Outlines are free: stroke the shape you already own (user insight, portrait-face)

When the reference shows an outline the draft lacks, the first question is whether the shape is already
there, unstroked: the face, neck and collar outlines of portrait-face are missing not because the shapes
are missing but because those paths are never stroked. 描边 is the reuse of an existing path with a
stroke; only the stroke colour and width are measured (near-black `#101018`, ~5 px here).

## P14 — Draw the object, not the pixels (user insight, 05-portrait-scene reframe)

The goal is a proper drawing in a similar style, not pixel or edge correspondence with one reference
photo. Holistic semantic shapes — a whole ribbon, a whole hair mass with parameterized strands — beat
fragmented point-matching patches, and being a *coherent artwork* outranks being *close* to the
reference. Overlay-based zone-distance compare is a calibration aid, never the objective; the drawing is
judged by looking at it as a whole. The person's reframe: "you don't need to match its location... it
should be a proper drawing first, not necessarily as close as possible."

**Generation over hand-placed geometry.**

## P15 — Physics-ish generation over hand-drawn geometry (user insight, scene-format design)

Regular, structured things — ribbons, curtains, hair strands, water ripples — are GENERATED from few
parameters (a spine, gravity direction, wave length, taper) rather than hand-placed point-by-point. Hand
coordinates are for genuinely irregular anchors only. This is what makes the drawing read as "drawn as
the whole thing" instead of assembled fragments. Origin: the person proposing gravity/wave ribbon
generation in the scene-format discussion.

**The engine and the reference.**

## P18 — The engine must not need the target (user constraint, 06-relational-geometry)

A reference image is a *teacher*, never the engine. Tracing can seed values for a drawing spec, but if
the solver needs the target to produce geometry, it is worthless for the end goal of drawing without a
reference. So the test for every abstraction is: *does this still work with the image deleted?*

**Depth produces visibility, not the author.**

## P29 — Let physical depth produce visibility, not the author (user correction, spatial model)

A continuous 2D component is painted on a plane or a curved 3D support. A ribbon that bends around a
person must remain one local artwork; it disappears where the person's surface is nearer and reappears
where its own surface is nearer. The engine derives those visible fragments from projected depth. Asking
a VLM to specify the precise hidden/reappearing intervals preserves the failure mode this architecture
is meant to remove. A 3D scaffold explains occlusion but does not replace the artist's later selection
and beautification of line art. Architecture SSOT: `docs/6_ARCHITECTURE.md`. Origin: the person's
explicit correction after M4j's apparently continuous but spatially misplaced ribbon.

# INFERRED

**Occlusion, edges and layering.**

## P1 — Occlusion is drawn, not implied (T1, warmup-duck)

Overlapping shapes must be drawn with explicit occlusion: arcs interrupted where covered (head arc broken
at beak), path ends tucked behind the covering shape (body ends inside head circle), background strokes
split into segments (waterline behind duck). A line drawn "through" a shape in front of it is always
wrong. The defects that taught this: the dark waterline crosses the hull and the head outline crosses the
beak.

## P2 — Not every visual edge is a stroke (T1/T2, warmup-duck)

Distinguish *outlines* (drawn strokes) from *fill boundaries* (color changes only): waterline = thin
darker stroke on top of a fill boundary; blush, belly shade, water shadow = pure color regions, no
outline. Before drawing any line ask: "is this an outline, or a boundary between two fills?" The recorded
errors are blush and belly outlines drawn as strokes, and a grey waterline stroke where the reference has
a fill boundary plus a subtle edge stroke.

## P11 — Shared edges: fill-only + separate edge stroke (T2, portrait-face)

Two adjacent filled shapes both carrying their outline stroke produce a double-line seam through solid
fill (hair-top vs right mass at x352). Give one side fill-only, then draw the visible edge as its own
stroke path — only where a real boundary exists.

## P17 — z-plane split for wrap-around elements (historical 2D workaround, REBUILD v2 #6/#3/#5)

**Superseded as an architecture prescription by P29.** This describes what the old flat renderer
required, not what an author should do in the new spatial model.

Elements that wrap AROUND the figure (ribbon circling the body, hair behind vs in front, hands tucked
behind) are modeled as ONE continuous shape split by z-plane, never pre-split paths: two node instances
sharing geometry (+seed), complementary arc/angle ranges, different `z`. For the ring generator the
zigzag phase is purely angular, so complementary arcs re-join seamlessly. Occlusion stays the renderer's
job (scene-format rule). The recorded cases are the ribbon ring's back/front halves and the green hair
mass moved from front overlay to the hair-behind layer.

## P20 — Two orders, kept separate (06-relational-geometry)

*Resolution* order (a node may use any shape declared before it) and *paint* order (`layers` + z) are
different orders and must never be conflated. Separating them is what removed the portrait's occlusion
surgery: a shape is declared where it is convenient to reason about it, and placed in the stack where it
belongs visually. Case: `sunhat` needs the head declared first but painted after the hair.

## P31 — Diagnose a surprising visual cue before prescribing its removal (S1a twist/crossing)

A twist's apparent point-like splice occurs at a smooth facing-normal sign change with positive world
width: an expected edge-on projection, not a broken attachment. Higher tessellation reduces stripe
scalloping but cannot remove that event. Same-facing, same-colour crossing visits also merge
perceptually despite depth separation; a geometry-derived occlusion contour helps the original crossing
but not the depth-reversed control. Thus projection, approximation, visibility and artistic-expression
causes are identified separately. A physical explanation does not waive the visual gate, and a useful
diagnostic line is not a general line-art solution. Evidence: the S1a outcome and
`evidence/parent-learner-projection.json`; scope remains those tested cases.

## P32 — A valid contour candidate is not automatically a useful art line (ribbon rule trial)

Complete depth-visible ribbon perimeter ink generated from real local boundaries, with hidden finite-width
ink clipped and no mesh diagonals, still meets competing lines at crossings/twists in the valid blind
comparison; a side-consistent local motif does not clarify front order. Keep candidate extraction,
visibility and **artistic selection** separate. Do not replace the missing selection rule with "draw
every valid outline", or call more consistent decoration a readability solution. This rejects the two
tested treatments, not all contour approaches. Negative controls and exact revision:
`.scratch/20-ribbon-drawing-rule/outcome.md`.

**Measurement and computed geometry.**

## P3 — Compute geometry, never eyeball it (T1, warmup-duck)

Eyeballed arc endpoints let the SVG arc solver invent a different circle center, and the head comes out
squashed. Measure circles with `measure --hough`, compute arc endpoints from the measured center, verify
color values with `measure --point`. The tool is a ruler; the semantics stay the author's. The recorded
fix is the measured (385,299,r112), which replaces the eyeballed endpoints in one step.

## P5 — Scan shading before assuming it (T2, warmup-duck)

A mental model of the belly shading is inverted until the pixels are read: the darker band sits mid-body
with a *bright rim below it* (water reflection), not darker at the bottom. `measure --scan col:x:y0:y1`
along a few rows/columns through a region reveals true shading structure cheaply — in warmup-duck the
pixel scans at x=350/380/420/560.

## P9 — Trace boundaries, don't guess coordinates (T1/T2, portrait-face)

For complex regions, scanline-trace the actual boundary from the reference (color-classify pixels per
column/row, find edge points) and build the path from measured points; verify ambiguous areas with a
coarse color-class grid map. Eyeball estimates are off by 20-60px repeatedly: the right mass edge is
x375-390, not 350; the left mass ends at y270, not 330; the hat is a large triangle. The
portrait-face boundary tracer catches three structural errors this way.

## P10 — Line refs fail on layered interiors; zoom + observe (T1, portrait-face)

XDoG line extraction turns anime eyes into noise — unusable. Interior-layered structures (eyes:
sclera→lid-band→iris→glints→outline) must be read from direct zoomed observation (`measure --point` grid
+ 3.5x crops), not derived from line refs. Line refs stay useful for coarse outer boundaries.

## P12 — Feature marks are tiny but positional (T1, portrait-face)

A nose can be a 5px vertical tick and a mouth a 15px horizontal dash — swappable without a zoom crop.
Locate small marks programmatically (dark-component scan within a region) before assigning identity;
verify with a zoom. The portrait-face nose and mouth are initially swapped until a 4.5x crop separates
them.

## P16 — Component plates: align before trusting (REBUILD v2, 05-portrait-scene)

User-supplied component plates (crops of the ref or redrawn versions) must be template-matched against
the reference before being used as geometry sources — a plate's alignment tells you whether it is a
position-true trace (usable for placement) or a redraw (usable for style/shape only). Matching = masked
TM_SQDIFF over a scale scan; scale 2.0 on a 2048→1024 plate means 1:1. Redrawn plates match nothing and
must not be force-fit. `dress.png`/`cloth.png` are redraws (style refs); `hat`/`ribbon`/`head_hat` are
position-true.

## P19 — Geometry by computation, semantics by eye (05-portrait-scene diagnosis)

A VLM is strong at naming/grouping/z-order/judging and weak at coordinate regression. Any shape needing
more than ~4 hand-typed coordinates must come from a computed source (trace, region, generator, or a
relation), never from the model's head. The portrait's 824 hand-typed vertices produced mush; 119
computed contours produced the character in 2.4s. Evidence: `evidence/diagnosis/`.

## P28 — The ruler is the one thing a fit must not move (13-assembly, M2 attempt 4b)

Fitting the `face` family's parameters to the reference's visible-skin mask has two traps. The first is
named in advance: the trace is the *visible* skin, so the fit must be scored with the occluders applied
or the bare shape overshoots. The second is not: **the `face` node is the ruler** — the hat, the eyes and
the hair are all placed off `head.*`. Left free, the optimiser shrinks the head (`rx` 95 → 52) to chase
the hair-occluded skin, buying IoU 0.691 while **collapsing the head gate to `edge_f1` 0.328 / coverage
0.385**. Pinning the head box and fitting only `cheek/jaw/chin-w` (+`turn`) gives the honest answer: IoU
0.552, i.e. this family cannot express this skin.

Rule: in a relational system where everything is placed off a host measure, **the host is not a free
parameter** — fitting it moves the entire drawing, and the resulting IoU is not a measurement of the
shape but of how far the ruler ran away. Pin the host to its measured canon, fit only what is
host-relative, and report the fixed-ruler number even when a free fit looks better. A free fit that
improves the fit metric while degrading the drawing is P25's lesson in a new costume.

## P33 — Declared parts are not a connected object; a physical thing is one continuous strip (A v4 review)

A drawing can carry a dozen named components with support frames and attachment records and still render
as disconnected pieces, because an attachment record is a name, not a geometric requirement. The A v4 bow
is the recorded case: a 12×15 px gather patch, two independent solid lobes, and a tail starting at an
offset whose 16.8 px width exceeds the knot's 12 px, so the tail's root is a straight cut beside the knot
rather than an emergence from it. The physical object is one ribbon visiting knot → lobe → knot → lobe →
knot → tails, and the reference's lobes are solid cloth read through crease and fold lines, not holes.
Consequences that generalise: a joint needs a seam contract (coincident boundary, shared tangent) that a
build can fail, so the defect is caught before a reviewer sees it; and a surface mechanism, once earned,
must not be silently simplified away — A v4's hair falls back from S1's two-sided twisting sheet
(`figure_scaffold.hair_sheet`, projected-face-orientation paint generalised in `ribbon_surface.py`) to a
flat single-colour band. Composition also decides whether such a defect is even visible: the second
sleeve exists, is small and mostly covered by the bow tail, and its surviving shape belongs to depth
occlusion rather than an author-drawn cut. Evidence:
`.scratch/35-r1-articulated-study/issues/54-user-review-scope-hair-and-hand.md`,
`evidence/A-cloth-construction-v4/source/family-rules.py` (`gather_patch`, `folded_loop`, `tension_tail`,
`_band_from_stations`), and the registered reference crop `500,320,900,800`.

**Shape reading and character.**

## P4 — Junctions and negative spaces carry the character (T1, warmup-duck)

The sky gap under the lifted tail petal, the thin notch between head and body, the open mouth showing
sky — these small negative spaces are what make it read as "rubber duck" rather than a generic yellow
blob. Zoom-compare crops (`compare --region ... --zoom`) on junctions reveal semantic truth invisible at
full scale. In warmup-duck the beak/tail crops carry it, and the critic independently flags the
head-body merge as its #1 finding.

## P8 — Model silhouettes, not assemblies of parts (T2, portrait-face)

A hair mass with strand tips is ONE silhouette whose bottom edge zigzags (tips down, notches up); the
"pockets" of shadow between strands are the underlying skin showing through notches — not shapes to draw
separately. Portrait-face's base+strands+pockets drawn as separate outlined shapes produce boxy
artifacts; the single zigzag path fixes it in one step.

**Metrics, judgement and the fresh eye.**

## P6 — When metric and eye disagree, trust semantics (warmup-duck)

Edge-F1 prefers the semantically wrong dark waterline (strong canny edge) over the correct light one.
Metrics are signal for progress tracking only; when they diverge from visual/semantic judgment, write
down why and move on. The recorded case is a metric drop that accompanies a clear visual improvement.

## P7 — Fresh-eyes critic: trust silhouette reads, discount impossible spatial claims (warmup-duck)

A no-context reviewer catches character-level truths staring misses ("chubby chick, not classic rubber
duck"). But it can also make spatial claims that are geometrically impossible ("larger and shifted
right" at identical canvas scale) — verify every critic claim against measurements before acting. In the
warmup-duck close-out review 3 of ~9 findings are actionable, the rest perceptual/minor.

## P25 — A per-element diagnostic is not an objective (13-assembly, M1)

Reshaping the hair so its centroid moves from (0.825, 0.472) toward the reference's measured (0.713,
0.348) makes the drawing **worse** — the aggregate coarse-grid colour-mass distance goes 39.1 → 42.8.
The indicator improves while the artifact regresses: invariant 4's failure mode (optimizer regression)
one level up, from pixels to measured mass centroids. A per-element table **diagnoses** — it tells you
which part to look at — but only the whole-image comparison (or a blind reviewer) **arbitrates**. Rule:
never tune a shape to a number in the diagnostic table; change it for a stated drawing reason, then
check the aggregate. Both roll-backs are in `.scratch/13-assembly/log.md`.

**The gate must be a real gate.**

## P22 — A proof must pass the gates it exists to enforce (06, SA1 re-assessment)

The relational language's proof render is declared readable with "diagnostics clean" — but the project's
own acceptance (`draw check` + fresh-context reviewer, invariant 7) is never run on it. The render is not
readable: the hat's occlusion is inside-out, the face is buried under hair, the shoulders are detached —
every defect invisible to the four shipped diagnostics. Diagnostics are a *subset* of the evidence,
never a substitute for the gate. Rule: **a mechanism's own demo runs the same acceptance as real
work** — build the check bundle, ask the fresh reviewer, and only then claim "readable". "Clean" means
"no rule fired", which is not "correct". SA1 finds it on the one artifact the whole language rests on.

## P23 — A ratchet, or the drawing silently regresses (14, night-research verdict)

A growing language and a shrinking drawing is a normal, invisible outcome. The night-research artifacts
are committed as "FINAL IMAGE" while sitting 4.5–5.6x below the best drawing the repo already contains —
no step in the loop ever compares a new render against the previous best, so there is nothing to notice.
Two instruments close that hole: a **stored baseline** (`scripts/draw baseline` records the best
artifact; `check` prints `vs recorded best:`), and an **omission alarm** (`coverage` — how much of the
reference's content the draft accounts for — because `color_dist` cannot tell "drawn wrong" from "not
drawn", so a bust and a bad full figure score alike). Rule: **progress is measured against your own best
render, never against your own design.** Metrics stay floors and alarms, never targets. Recorded: two
fresh reviewers, shown only the images, both prefer the older drawing.

## P24 — A rung's deliverable is a patch to the assembly, never a standalone probe (14, night-research)

Three parallel probes (a critique, a face study, a Starry-Night evocation) produce three directories and
zero patches to any drawing. Each probe is individually sound, so each is presentable as the
deliverable — which is how a language advance gets mistaken for drawing progress. Rule: **one drawing
grows across the milestones** (`.scratch/13-assembly/work/spec.yaml`); a probe is
welcome, but it merges into that drawing or is discarded *in the same milestone*. If nothing merges,
nothing is delivered. The recorded case: the night's three probes, and the assembly that still has to be
seeded from a probe.

## P26 — Verify the instrument before trusting its reading (13-assembly, M2 attempt 2)

Two fresh-eyes reviewers dispatched to judge a head crop both return "model does not support images" —
while reviewers of the same kind of image give detailed, position-referencing descriptions of it.
**Capability is not a property of the plan; it is a property of the instance that runs it.** A gate that
silently degrades to a blind reviewer is worse than a gate that was never run, because it produces a
verdict-shaped object with no perception behind it.

Two rules come out of it. First: **a reviewer must prove it can see before its verdict counts** — ask
for one fact only a sighted agent could state, checkable against a measurement already in the repo. An
unsighted verdict is **void, not negative**: it neither passes nor fails the work, and the record must
say the visual half was not run. Second: **refusing to answer is the correct behaviour.** Both reviewers
report the blocker rather than describing pixels they have not seen, and one turns the failure into real
evidence by reading the two *specs* instead — which finds that the baseline's brim is four independent
fills plus two disjoint strokes, and that its brim is clipped by the canvas edge where the reference's
is not. A missing verdict with an honest reason is worth more than a confident one without perception.

## P27 — A gate that can be passed by copying the answer measures copying (13-assembly, M2 attempt 3)

A gate that compares the assembly to the baseline on fidelity to the reference, where the baseline is
itself hand-fitted to the reference, reduces "beat the baseline" to "trace the reference more
accurately" — and a spec that flood-fills five regions of `image.jpg` at render time wins easily, head
`edge_f1` 0.619 against the baseline's 0.422. The number is real and the progress is not: the artifact
can no longer be rendered with the image deleted, so the engine now *needs* the target, which is the one
thing the reframe forbids.

Two rules. First: **check admissibility before fidelity** — render the judged artifact without the
reference, and if it cannot, every comparison on it is void. Second: **when a gate can be won by
copying, the gate is wrong, not the copy.** Fix the gate's window (which region) *and* its precondition
(does the artifact stand up), or the ratchet will happily promote a traced image.

The constructive half, and the part worth keeping: the reference is a legitimate teacher, and the way to
use it is to **materialize** — trace once, freeze the computed vertices into the spec with provenance,
close the image. The geometry is still *computed* (invariant 5: not the model's bad coordinate
regression), the reference is still the source of the values (P18's teacher role), and the artifact
stands alone. A live raster read is the one form of teaching that cannot be withdrawn.

## P30 — Construction, interface use and visual reading are separate evidence (S1a ribbon study)

A fresh smaller model successfully authors the requested S/taper/half-turn spec using only the teaching
packet and a black-box generator. Parent checks confirm attachment, widths and material sides; the visual
reviewer still cannot identify one continuous two-sided sheet. Neither valid JSON nor correct depth
establishes drawing readability. Preserve an unaided failed image alongside successful parameter tests;
repairing it and calling the repaired answer transferred hides the missing ability. Evidence and tested
scope: `.scratch/19-ribbon-family/outcome.md`.

## P37 — A mechanism claim is unproven until a check distinguishes the mechanism from its absence (A v6, B v2)

A README sentence — the hair passes a twist function, the cuff is one whole authored piece, the seam
contract covers every joint — is prose until some check fails when the mechanism is removed: the twist
set to zero, one joint broken on purpose, one declared file dropped from the manifest. That failing check
is what turns the claim into evidence, and its absence means the claim is unproven rather than
supported. What P30's separation of construction, interface use and visual reading does not say is how
often the two disagree: three A candidates and two B candidates pass every code-level gate and still
fail their image reviews. Evidence:
`.scratch/35-r1-articulated-study/evidence/A-cloth-v8/tests/test_hair_two_sided.py`
(`test_the_twist_is_what_turns_the_sheet_over` removes the twist and requires the reverse-side fill to
collapse), `.scratch/35-r1-articulated-study/evidence/A-cloth-v6/tests/negative-control-output.txt` (18
joints intact, 5 failures when broken, 0 after restore), and the review dispatches
`.scratch/35-r1-articulated-study/work/wave2-review-a.js`, `wave4-review-b.js`, `wave8-review-a6.js`.

**Instruments and evidence.**

## P21 — The engine reports in words (06-relational-geometry)

A model has no numeric sense of a 1024² canvas, so the resolver must hand back derived facts as
sentences: OFF-CANVAS / CLIPPED / SUB-PIXEL shapes, and CONTRADICTION when a declared `front/behind`
relation disagrees with the layer stack. On the first bust render this catches two defects (a wrong
layer order, and shoulders clipped 68px past the frame edge) before the image is ever looked at.
Instrument: `scripts/relate.py` diagnostics.

## P35 — Liveness is observed, never read from a status field (run reaping, wave 7)

Three sibling runs die at the same instant when run-directory retention cleanup deletes their run
directories and async config files, and `status` keeps reporting them as running because the status
lives in the directories that are deleted. So a stored status is a claim about a record, never about a
process: conclude a child is alive only from a live process and a new event timestamp and a growing
artefact, and call it dead on no process, no new events and no new files, however confidently the status
disagrees. P26's lesson one level down — a reading is only as good as the thing the instrument actually
observes. Evidence: `.scratch/35-r1-articulated-study/work/wave7-recovery.js`, the recovery dispatch that
opens with this warning.

## P36 — Execution capability is a reviewer property, like sight (A v5 review pair)

P26 establishes that a reviewer must prove it can see. Execution is the same kind of property: a
reviewer with no execution tools reports every check as NOT RUN, which is honest and is not
verification, and a dispatch that asks only for judgement returns a prose verdict over claims nobody
ran. Pair the two reviewers and keep their reports separate — an image-only reviewer answers what is
wrong with the picture, an execution-capable reviewer re-runs the mechanical claims (tests, manifests,
negative controls, mutations) and reports them with the commands that produced them — and let neither
one's silence stand in for the other's gate. Evidence:
`.scratch/35-r1-articulated-study/work/wave2-review-a.js` (the A-cloth-v5 pair, whose structural half
prefaces its report with an execution-limit note) and
`.scratch/35-r1-articulated-study/work/wave4-review-b.js`, which opens by telling its verifier that an
earlier reviewer cannot run anything.

## P38 — A command surface that cannot run has no gates (session-start tooling rot)

The documented loop cannot always run at all, and that state is the gate failure: `scripts/draw` points
at a `.venv` that does not exist, `scripts/draw.py` imports a module the environment lacks, the renderer
path is pinned to a playwright revision that has been deleted, and no dependency file has ever been
committed — while every document describes the loop in the present tense and every earlier record still
reads as verified. So run a documented command before trusting it, and treat a broken command surface as
a gate failure rather than an inconvenience: with no runnable loop nothing below it is verifiable,
whatever the records say. The repair generalises — declare the dependencies, resolve a versioned path
dynamically instead of pinning it, and let the wrapper degrade to whatever interpreter exists. Evidence:
the environment repair recorded in
`.scratch/35-r1-articulated-study/issues/54-user-review-scope-hair-and-hand.md` and its current state —
`pyproject.toml` tracked, `scripts/renderer.py` selecting the highest cached revision, `scripts/draw`
falling back to `python3`.

## P39 — A copied package inherits the base's evidence, and evidence is the first thing a copy must rebuild (B-hand-study-v1-r1)

The repair of B-hand-study-v1 is cut as a *copy* of it, into `evidence/B-hand-study-v1-r1/`, because the
reviewed revision has to stay untouched. The copy carries the base's `check/` bundle with it:
`check/report.txt` still names `evidence/B-hand-study-v1/`, and `check/draft.png` is byte-identical to
the base's `artwork.png` — the image an independent review has already BLOCKED once. A reviewer
following that bundle judges the revision the repair replaced, and no hash in the package says so.

So a copy-based repair regenerates its bundle as its **first** act, before any geometry, and the check
that it did is textual, not visual: `check/report.txt`'s paths resolve inside the package's own
directory and line 1 names an image whose pixels equal the package's own render. The general form: an
artefact that is evidence is bound to the revision that produced it, so any operation that creates a new
revision — copy, branch, worktree, rename — invalidates every bundle, manifest and report that came
along, and inheriting them silently is how a package passes a check of the wrong thing. Evidence:
`.scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1/check/report.txt` (three paths naming
`B-hand-study-v1/`), `md5sum check/draft.png` equal to `evidence/B-hand-study-v1/artwork.png`
(`c9950caa…`), and the wave 14 package G acceptance item 1 which puts the regeneration before the pose
work.

**Sizing a package and ordering its deliverables.**

## P34 — A budget the harness does not honour orders nothing; order the work so it is true at any cut (A v6)

A subagent run is killed at the harness wall — 1,800,000 ms observed in the harness, about thirty minutes
— so a dispatch that budgets sixty or a hundred and twenty minutes is spending time the run will never
be given, and the writer is stopped wherever it has reached. The kill is never clean: the A-cloth-v6 run
is taken by infrastructure instead (run reaping, P35) and left source ahead of its renders, its manifest
and its check bundle — exactly the inconsistency the package's own gates exist to catch — while
`work-checkpoint.md` asserts a completeness the tree does not have.

Two things generalise. A stated budget must fit inside the harness limit, or the limit is raised
explicitly at dispatch. And the deliverables are ordered so the package is true at any cut — source,
renders, manifest and check bundle first, documentation last — so a kill leaves a smaller package rather
than a false one, and `sha256sum -c manifest.sha256` plus every listed file existing is the check that
decides "true". Evidence: `.scratch/35-r1-articulated-study/evidence/A-cloth-v6/work-checkpoint.md`
claims everything complete and hash-verified, while `sha256sum -c manifest.sha256` reports 20 entries OK,
the whole `check-a/` bundle absent from that revision and several `source/*.py` hashes stale (verification
recorded in `.scratch/35-r1-articulated-study/work/wave7-recovery.js`); the preserved state is the one
that verification names.

## P40 — A package sized as a goal returns a partial; size it as one stage and order it so any cut leaves a true package (wave 13's two repairs)

Both wave 13 repairs are cut with a 75-minute clock and both return early and incomplete: A-bow-study-v2
at 16 of 17 tests with the six defect tests unwritten, B-hand-study-v1-r1 RED with its bundle stale. The
clock is not the limit; the package is, because "finish the repair" is a goal that contains several
stages, and a run stops when it stops rather than at a stage boundary. The cure is the one P34 already
prescribes for a different mechanism: one deliverable per package, the acceptance as commands, the
`check/` bundle and a commit as the last act, and the next stage in the next dispatch. Evidence: the
durations are commit timestamps, since the run records live outside the checkout, and
`.scratch/35-r1-articulated-study/work/wave14-contracts.md` § "What wave 13 proved about sizing".

**The invariant set.**

## What a principle is

A *principle* is knowledge the model carries, so it survives the reference being closed; a *tool* that
needs the target does not, and P18 is the test that separates them. The invariants that distil these
principles into rules an agent must follow are stated once in `AGENTS.md` § Invariant rules; this file
owns the principles, not the rules.

**A lesson takes the next number and keeps it.** `P`-numbers are append-only: a new lesson takes the
next unused number — `P42` today — and an existing number is never reused, renumbered or dropped, because the whole repo points
at lessons by number. A lesson that a later observation overturns is corrected in place and says so;
its number stays.

## The numbered invariant rules

The numbered invariant rules 1–8 are stated once in `AGENTS.md` § Invariant rules, and each names the
principle it distils; this file owns those principles and does not restate the rules. The commands that
run a gate, and the ratchet procedure, are `docs/9_IMPLEMENTATION.md`.

**Boundary.** This file owns the binding rules and constraints — `P1`–`P41` — and their provenance. It
does not own: how a rule is implemented or which command runs it (`docs/9_IMPLEMENTATION.md`); the
architecture the rules constrain, including the spatial model P29 names as its SSOT
(`docs/6_ARCHITECTURE.md`); what success means and the gates that decide it (`docs/2_GOAL.md`); the
formats and field lists the rules touch (`docs/7_INTERFACE.md`); the language a drawing is authored in
(`docs/5_PRODUCT.md`); the flow a review runs in (`docs/4_USECASE.md`); why programmatic drawing at all
(`docs/1_PROBLEM.md`); and the records that keep the evidence these rules point at
(`docs/9_IMPLEMENTATION.md`).

## P41 — A record that is not derived from the build drifts away from the thing it judges (A v2, B r1, L)

A record written by hand states the revision before it. Two instances passed a green suite while
lying: a package README that did not name its own review image, so the rebuild command sat one hop from
the artifact and the image under review could not be traced back; and a committed negative-control
record stating an earlier build's counts (74 occlusions and 6 contacts where the delivered artwork
gives 91 and 7), whose producer overwrote the occlusion half and deleted the contact half. The same
class appears the other way round: a review whose binding was moved under it by a commit inside a
read-only package, so its verdict had to be re-ledgered per check.

The cure is mechanical, not a note: the record is rewritten from the build it describes and a test
fails when the committed file and a fresh computation disagree; a package's README names its own
`check/draft-fullres.png` and the command that rebuilds it; a reviewer resolves and prints its own
binding line — revision and artifact hash — before it judges. Verify when adopting someone else's
evidence: does the record come from this build, and does the review name the bytes it saw?


