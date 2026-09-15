# STATUS — where this project is right now

**One line:** M1 rebuilt the figure's composition on the relational layer and now covers more of the
reference than the baseline does (0.528 vs 0.514); M2 gave the head a real face — jaw, chin, layered
eyes, fringe — but **failed its gate**: measured against the reference, the baseline's head is still
closer (head-region distance 22.4 vs 40.7). The baseline remains the bar and nothing is promoted.

Last updated: 2026-09-15 · Direction lives in `docs/drawing/roadmap.md` · Milestones M0–M5

## Current best artifact — the ratchet floor

| field | value |
| --- | --- |
| render | `.scratch/00-tooling/baseline/best.png` |
| origin | `.scratch/05-portrait-scene/evidence/current.png` (REBUILD v2, 2026-09-11) |
| spec | `.scratch/05-portrait-scene/work/scene.yaml` (133 nodes) |
| `artifact_sha256` | `1a7cae4fa400068725ebbbfce5a1401188aa21b3885fb376332089baec080c7c` (byte-identical to the source render; `draw baseline` now stores a byte copy, and records the two digests separately — a renamed single `sha256` had held the *source*'s digest while claiming to be the artifact's) |
| metrics | `coverage 0.514 · edge_f1 0.252 · recall 0.207 · color_dist 62.8` |
| provenance | `.scratch/00-tooling/baseline/best.json` |

Reproduce (verified byte-identical, 2026-09-15):

```bash
.venv/bin/python scripts/scene_render.py .scratch/05-portrait-scene/work/scene.yaml \
    -o /tmp/best.png --ref image.jpg
.venv/bin/python scripts/draw.py check /tmp/best.png --ref image.jpg     # prints "vs recorded best: all +0.000"
```

`coverage` = fraction of the reference's content the draft accounts for — the omission alarm.
It is a **floor and an alarm**, never a target (roadmap R6).

## Milestones

| milestone | intent | status |
| --- | --- | --- |
| **M0** baseline recorded | make regression visible | ✅ done 2026-09-15 |
| **M1** recover the baseline's composition | the whole figure, coarsely, flat fills | ✅ **exit criteria met 2026-09-15 — baseline not promoted.** Coverage 0.528 vs 0.514 (nothing deleted); the baseline is still the better drawing (two blind reviewers, and the grid measurement agrees). Artifact: `.scratch/13-assembly/evidence/m1-final.png`; gates + rollbacks in `13-assembly/log.md` |
| **M2** beat the baseline on the head | jaw/eyes/lash/hat crown/hair taper | 🔄 **in progress — attempt 2 still not passed.** Attempt 2 found and fixed the brim's real cause (a straight chord split across the disc, now a fold-over rim band — engine gain, kept) and improved every alarm vs attempt 1 (`coverage` 0.529, `color_dist` 65.6). But head-region measurement still favours the baseline (edge_f1 0.422 vs 0.173) because the baseline was **hand-fitted to the reference** while the assembly re-derived values coarsely. **Next: seed the geometry from the reference (D15)** |
| **M3** beat the baseline on body & cloth | collar, bow, sleeves, arms, hands, pleats | ⬜ blocked by M2 |
| **M4** beat the baseline on the fields | soft tier last (invariant 2) | ⬜ blocked by M3; the whole-figure promotion belongs here |
| **M5** withdrawal + stress | 15 → 16 → 17, reference-free | ⬜ blocked by M4 |

## In flight

**Running with full autonomous permission, to a stop condition (D31).** The user granted permission
to orchestrate `fork=false` subagents until one of the standing stop conditions fires (roadmap S1–S3:
abstraction / comprehension / perception failure). Whoever picks this up: the loop is
*dispatch a writer → verify its claims myself → run the gates → commit → rubric-review → next slice*,
and the writer's report is always a **claim** until re-verified.

Current: **M3a (upper body)** — collar, bow structure, arms, hands, sleeve/cuff — plus a **rubric
pipeline validation** running on the frozen parametric floor (`evidence/m2-final.png`) by two
independent reviewers, to (a) check the reviewers can actually see and (b) record a baseline rubric
vector for the floor.


**M2 — the head: attempts 1 and 2 both failed the gate; attempt 3 changes the approach.**
The brim's real defect is fixed (D16). The blocking reason M2 cannot beat the baseline's head is
now understood and is *strategic*, not artistic: the baseline was hand-fitted to the reference, and
the assembly threw those reference-accurate values away to re-derive them coarsely (D15).
**Next slice: seed the assembly's head geometry from the reference — measure → fill the spec → close
the image — keeping the relational structure.** Slice home `.scratch/08-bust/spec.md`; iteration
record `.scratch/13-assembly/log.md`.

Nothing else is in flight. The 2026-09-14/15 unsupervised research session is **stopped** (P0).

Its work is kept selectively, per `14-abstraction-research/spec.md`:

- **kept as real progress:** `scripts/relate.py` (one resolver: anchors, relations, `sunhat` + `eye`
  families, 4 diagnostics); the measured canons in `vocabulary.md`; `principles.md` P1–P22; the
  declarative-family proposal in `14/work/declarative-families.md`.
- **demoted to probes:** `14/evidence/final/v3.png` (bust) and `14/evidence/final/full-v2.png`
  (full figure) — the two artifacts committed as "FINAL IMAGE". Neither passes the gate; both are
  below the baseline. They are evidence about the language, not the project's drawing.
- **the assembly seed:** `14/work/final/final-full.yaml` is M1's starting point, to be promoted into
  `.scratch/13-assembly/work/spec.yaml`.

## Open defects and questions

1. **The assembly under-uses the reference as a teacher** (D15, strategic, blocking M2): values the
   reference could *seed* are re-derived coarsely from colour components, so the assembly is coherent
   but measurably less accurate than the hand-fitted baseline it replaced. Fix: seed geometry from the
   reference where the approximation is far off — legitimate per `abstraction.md`, and different from
   the banned 824-hand-typed-coordinate failure.
2. **The brim is much shallower than the reference's crescent droop** — a flat ellipse cannot express
   it (least-squares conic fits go degenerate). Needs a shape that can droop, or seeded traced points.
3. **The fringe covers the mid-brim** and squashes the navy/teal areas — the direct cause of the
   `x660`/`x740` silhouette gaps and most of the navy area deficit.
4. **The face is 9% too wide and 18% too tall** (164×180 against the reference's visible 151×153).
5. **`check` has no test of its own** — the bundle logic (bundle paths, crop ranking, baseline delta,
   `coverage`) is verified only by manual runs. `measure-composition.py` is likewise untested.
6. **Line-mode `diff` stays weak for this reference** (no uniform black line art; 12.6 % of pixels
   below gray 95). Region decomposition is the structural source — a known, accepted limitation.
7. **No `style:` header** — deferred until two looks are needed in one project.
8. **`region` / `trace` nodes are teacher-only** (they read the reference raster). By design; they
   must not appear in M5's reference-free specs.
9. **Proportion-vs-placement literal lint** (SA1 finding 6): proportion constants in `vars:` with
   provenance are convention-only; the resolver does not yet warn on raw `frame.*` placement.
10. **`region` is an overloaded name (found 2026-09-15).** It is both a **raster-flood node type**
   (`{region: <id>, seed: ..., tol: ...}`) and a **bbox parameter** of the `strands`, `stars` and
   `flow` families (`{strands: x, region: [x0,y0,x1,y1], ...}`). Grepping for `region:` therefore
   reports the baseline and the starry probe as teacher-dependent when they are not — it made me
   conclude the ratchet floor failed G0, which is false (both render without `--ref`). Not renamed
   yet (it would touch many files for a clarity win); **any admissibility audit must match
   `{region: <id>, seed:`, not `region:`**.
11. **Admissibility inventory (2026-09-15):** the *only* teacher-dependent artifact in the repo is the
   live assembly `.scratch/13-assembly/work/spec.yaml` (5 raster nodes) — the thing the freeze slice
   is fixing. `06/work/bust.yaml`, `14/work/final/*.yaml` and the baseline `05/…/scene.yaml` all render
   with the image deleted.

## Decisions log (append-only)

- **2026-09-15 · D1 — the night session's completion claim was false.** A bust and then a full
  figure were committed as "FINAL IMAGE" without the gate its own rules require (P22). Both are
  reclassified as probes. Recorded rather than reverted: the artifacts are evidence, and the git
  history is the learning curve.
- **2026-09-15 · D2 — the 2026-09-11 full-figure render is the project's baseline**, not a frozen
  dead end. `05` stays frozen as a *ticket* (it was doing too much at once) but its artifact becomes
  the ratchet floor.
- **2026-09-15 · D3 — the roadmap's milestone gates are adopted** (`docs/drawing/roadmap.md`).
  Milestone exit = gate pass, not slice completion. Spine changes require an entry here.
- **2026-09-15 · D4 — `coverage` adopted as an alarm and a floor**, never a target: the metric that
  would have made a bust visible as a bust. It is a *floor* because deleting content is a regression
  even when the remaining detail improves.
- **2026-09-15 · D5 — the assembly is one artifact** (`.scratch/13-assembly/work/spec.yaml`, seeded
  in M1), patched
  by every milestone. The old ladder's rung directories keep their specs as slice homes, but do not
  each own a separate drawing.
- **2026-09-15 · D6 — `blob` has two legitimate forms** (`poly` closed, or `spine` + `w` ribbon) in
  both the authoring front end and the compiled back end. The front end previously accepted only the
  ribbon form while the back end accepted both — a dialect split that crashed the full-figure spec.
- **2026-09-15 · D7 — the gate was mis-specified, and M1 found it.** G2 originally required
  `edge_f1 ≥ best − 0.01` at every milestone, but M1 is *defined* as flat masses with no line work, so
  the floor failed it for doing its job — and passing it would have meant smuggling M2/M3 work into
  M1, the "one ticket doing several things at once" failure that got 05 frozen. Split into: **G2
  alarm** (coverage deletion floor + color_dist breakage bound; applies always) and **G2b detail
  floor** (`edge_f1`; applies from M2). **Promotion separated from milestone exit** — the baseline
  moves only on a blind A/B preference, never on metrics and never because a milestone passed.
  A gate that fails a drawing for doing what the milestone asked is a gate defect; the fix is
  recorded, not quietly applied.
- **2026-09-15 · D8 — M1 exit criteria met; the baseline was NOT promoted.** The assembly now exists
  at `.scratch/13-assembly/work/spec.yaml` with measured composition, coverage 0.528 (> 0.514, so
  nothing was deleted), diagnostics clean, 17 nodes, byte-deterministic. But two fresh reviewers both
  called the baseline the better *drawing*, and the coarse-grid measurement agrees (32.6 vs 39.1). The
  milestone is complete and the ratchet has not moved: those are different statements, and keeping
  them separate is the whole point of D7. M1 did fix real composition errors the baseline has — its
  dark skirt mass (0.6% of frame vs the target's 7.8%) and its ribbon (0.1%) are essentially missing.
- **2026-09-15 · D9 — the largest remaining M1 deficit is occlusion, not composition.** The target's
  cream mass is 12.5% of the frame against the assembly's ~4.5%, but enlarging the cream shapes made
  the drawing worse (M1 v4: coverage 0.523 → 0.502). The cream the reference shows is *behind* the bow
  and hair, so it is M3's occlusion problem, not an M1 size problem. Recorded so M3 does not
  re-discover it.
- **2026-09-15 · D10 — the ratchet is a WHOLE-artifact floor; region comparisons are evidence.**
  The roadmap previously implied M2 could promote the baseline on the head *crop* alone. It cannot:
  promoting a render whose head improved but whose body is cruder than the current best would move
  the floor *down* in disguise. So a region-scoped comparison (the head crop in M2) is milestone
  **evidence** and can gate the milestone, but the baseline moves only when the whole artifact is
  preferred. M2–M3 contribute evidence; M4 is where the whole figure can win. Corrected in the
  roadmap the same session it was found.
- **2026-09-15 · D11 — M2 attempt 1: gate NOT passed, kept as evidence.** The head got a real face —
  a new `face` family whose jaw/chin taper matches the reference's measured row profile, two eyes
  placed independently (this is a 3/4 view, so `mirror-of` would have forced them equal), fringe,
  cheek locks, brows/nose/mouth — and the totals moved the right way (`edge_f1` 0.082 → 0.106,
  `color_dist` 68.8 → 66.4). But the head-region colour-mass distance says the **baseline is still
  closer** (22.4 vs 40.7 at 64px cells), the baseline's visible face bbox is nearly exact (150×151
  against the target's 151×153) while M2's is 164×180, and two reviewers **split 1–1**. Measurement
  decided it. Milestone stays open; the single blocking defect is named (the brim does not read as
  one piece).
- **2026-09-15 · D12 — the gate caught a real bug in my own new code.** The first `face` family drew
  a full-height cranium with the jaw wedge *inside* it, so the cranium's round bottom was the
  silhouette and no chin rendered. Both reviewers independently said "round blob, no chin" and both
  were right. This is the second time a fresh-eyes gate has caught a defect I could not see in my own
  work (P22 was the first) — evidence that the gate, not the author, is what makes the claim safe.
- **2026-09-15 · D13 — `vocabulary.md` set B canons have the wrong host, verified numerically.**
  Set B is host-relative (`head.cy − 0.58·head.ry`). Applied to this project's head ellipse
  (skull-top → chin, cy 264, ry 114) that puts the eye line at y198 — but the reference's eyes are at
  y262–268. Set B's numbers only work if the host is the **face** ellipse (hairline y243 → chin y378:
  cy 310.5, ry 67.5 → `310.5 − 0.58·67.5 = 271`). So set B was measured against a different host
  shape than the one the assembly uses. Corrected in `vocabulary.md`; the assembly's own values are
  measured directly from the reference instead.
- **2026-09-15 · D14 — a comparison gate must be evaluated on the region the milestone owns**
  (third occurrence of the same defect: D7 fixed it for M1, D7's G2b reintroduced it for M2, and M2
  attempt 2 hit it again). G2b was a *whole-frame* `edge_f1` floor applying "from M2 onward", but M2
  owns only the head — so the floor failed it for work it was never asked to do, and passing it would
  have meant smuggling M3's cloth detail into M2. General rule now: **every comparison gate (G2b, G3)
  is measured on the region the milestone owns; the whole-frame alarm G2 always applies too.** A gate
  whose measurement window is wider than the milestone's scope is a defect in the gate, not a failure
  of the work. Applied to M2: head-region `edge_f1`/coverage/colour-mass distance.
- **2026-09-15 · D15 — the assembly must SEED from the reference, not re-derive what is already
  measured.** Strategic finding from M2 attempt 2. The baseline wins the head region on measurement
  (`edge_f1` 0.422 vs 0.173, coverage 0.702 vs 0.585) largely *because it was hand-fitted to
  `image.jpg`*, while the from-scratch relational assembly is more coherent but less accurate. That is
  not a mystery to be ground away at — it points at a mistake in how M1/M2 were done: **reference-
  accurate seeded values were thrown away and re-derived coarsely from colour components.**
  `abstraction.md` explicitly sanctions using the reference to *seed* values (measure → fill the
  spec's numbers → close the image), and `trace`/`region` are the documented nodes for it; the
  824-coordinate failure was about **hand-typing** coordinates, not about using traced ones. Corrected
  approach: keep the relational structure and the vocabulary, and seed the geometry from the reference
  where the relational approximation is measurably far off. The values are the teacher's; the
  structure is ours. This is what the reframe said to do and M1/M2 did not do it.
- **2026-09-15 · D16 — M2 attempt 2: better, gate still not passed.** The brim's real cause was found
  and fixed (see below), `lift`/`pom` corrected, and every alarm improved against attempt 1
  (`coverage` 0.519 → **0.529**, `color_dist` 66.4 → 65.6, head colour-mass distance 40.7 → 36.2).
  But the baseline's head still wins on measurement, so nothing is promoted. The brim fix itself is a
  genuine engine gain worth keeping: `sunhat` used to split the brim with a **straight chord across the
  disc**, so the two fills met only at the two tips — and the tips and chord are exactly where the
  hair and crown sit, which is why two reviewers saw a "detached teal lozenge". The far slice is now
  the rim band along the brim's far edge folding over (`rim`, default 0.45), the near slice is the top
  surface it borders, and the two still tile the ellipse exactly.
- **2026-09-15 · D17 — the orchestrator model cannot see images; only reviewer subagents can.**
  Every `read` of a render in this session returned "model does not support images". Earlier summaries
  described renders as if they had been looked at; that was wrong and is corrected here. Consequence
  for the method: for this orchestrator, *all* visual judgment must come from a fresh-context subagent
  (which demonstrably can see — reviewers quote colours, positions and malformations) plus measurement.
  "Never judge your own render" is not just a rule here; it is the only physically available option.
- **2026-09-15 · D18 — vision is not stable across subagent instances; a reviewer must prove it can
  see.** Both reviewers dispatched for M2 attempt 2 returned "model does not support images", while
  reviewers earlier in the same session gave detailed, position-referencing visual descriptions. The
  harness routes subagents to different models and only some are sighted. Consequences, now in
  `method.md`'s reviewer protocol:
  (1) a reviewer is first asked for **one fact only a sighted agent could state**, checkable against a
  measurement already in the repo, and an unsighted reviewer's verdict is **void, not negative**;
  (2) when no sighted reviewer is available, the visual half of the gate **was not run** — that is
  recorded explicitly, and measurement plus source-level structure carry the decision;
  (3) **the A/B mapping is logged in the session it is handed over** and confirmed by pixel comparison,
  because a swapped pair inverts the verdict. That gap was real: neither attempt-1 nor attempt-2 round
  recorded it, and the attempt-2 reviewer caught it. Now recorded and verified for both rounds.
- **2026-09-15 · D19 — M2 attempt 2: measurement decides against, visual half untested.** The
  reviewer's refusal to fabricate a verdict is the correct behaviour and is recorded as such. Attempt 2
  fails on the measured half of A1 (region `edge_f1` 0.173 vs 0.422; region coverage 0.585 vs 0.702)
  and is **neither passed nor failed visually**.
- **2026-09-15 · D20 — the teacher step must MATERIALIZE, not depend.** M2 attempt 3 followed D15 and
  beat the head bar decisively (`edge_f1` **0.619** vs 0.422, coverage **0.778** vs 0.702) — by giving
  the spec five `region` nodes that flood-fill `image.jpg` **at render time**. The spec then cannot
  render with the image deleted:
  `relate: region 'face-skin' needs the reference raster (--ref); region is teacher-only and may not
  appear in a reference-free spec`. That violates P18 / invariant 6 outright, and it breaks the test
  `abstraction.md` states for every addition. `abstraction.md` names two supported teacher uses and
  both are *removable* ("measure the reference to fill in the numbers in a spec, then close the
  image"); a live `region` node is a third way that is **not** removable and must not appear in the
  artifact. So the teacher step becomes a materialization: resolve once with `--ref`, **freeze** the
  computed vertices into a sidecar data file with provenance, reference that data by name from the
  spec, and the spec then renders with `image.jpg` gone. Invariant 5 is still satisfied — the vertices
  were *computed by the tracer*, not typed by a human — and the gate finally measures a drawing.
- **2026-09-15 · D21 — a comparison gate must judge an artifact that renders WITHOUT the reference.**
  The M2 gate compared the assembly to the baseline on fidelity to `image.jpg`, and the baseline was
  itself hand-fitted to `image.jpg` — so "beat the baseline" reduced to "trace the reference more
  accurately", which any tracer wins trivially and which teaches nothing about drawing. **The gate was
  measuring copying.** Rule now: if the judged artifact needs `--ref`, the gate result is **void** — it
  is not a pass and not a failure of the drawing, but a failure of the artifact's admissibility. The
  baseline stays unpromoted (attempt 3's whole-frame `edge_f1` 0.271 > 0.252 is a tracing win, not a
  drawing win).
- **2026-09-15 · D23 — G0 now passes, and the artifact is 81% copied: M2 stays OPEN.** The freeze
  slice materialized the raster nodes into provenance-carrying sidecars (`draw freeze` → `traced`
  nodes), verified by me with `image.jpg` moved away: the spec renders, `draw check` exits 0, the
  no-`--ref` render is **byte-identical** to attempt 3's (`785a597d…`), and quality did not move
  (head `edge_f1` 0.619 vs 0.422). So the artifact is **admissible** — and measured:
  **81.0% of the head's painted pixels are reference-derived** (47% of the whole crop; my independent
  polygon-area check agrees). A frozen contour is **not a learned canon**: `vocabulary.md` defines a
  canon as proportion knowledge that transfers to a new subject, and a traced outline transfers to
  nothing. So 81% of the head carries no transferable learning — and that is exactly the 81% M5 would
  have to re-invent, which is what failed at attempts 1 and 2. **The gate as written is met but cannot
  distinguish a drawing from a copy, so M2 is not closed and the baseline is not promoted.**
- **2026-09-15 · D30 — the rubric replaces the pixel metrics as the PRIMARY gate.** The user's
  correction, and it matches this project's own P14 ("judged by looking… zone-distance/edge metrics are
  weak regression signals only") — which the gates contradicted. `edge_f1`/`color_dist`/`coverage` are
  *pixel* measures: they compare edge coincidence and colour distance against a reference, so a traced
  copy scores well and a good drawing of a slightly different subject scores badly. That is how the
  last day spiralled into "the bar can't be cleared without tracing": **the gate was measuring the wrong
  thing and I kept trusting it.** New instrument: `docs/drawing/rubric.md` — six axes (subject identity,
  human figure, silhouette coherence, feature legibility, occlusion correctness, style+composition)
  scored 0–5 against explicit anchors by an **independent, sight-proven** reviewer (two of them;
  contested axes recorded, never averaged). Each review also returns *biggest single defect* and *the
  one change that would most improve it* — the field the next iteration works from. Roadmap: **G8 is
  the primary gate**; G2 stays an alarm (deletion/breakage); **G3b is demoted from a floor to a
  diagnostic** — as a floor it was false, since clearing it provably required near-contour accuracy
  (D26). Milestone exit = the milestone's named axis reaching target **plus** the alarms.
- **2026-09-15 · D31 — the standing stop conditions, and full permission to run to one.** The user
  defined when the work should stop and granted autonomous run permission; recorded in the roadmap as
  S1–S3: **S1 abstraction failure** (describing what to draw starts needing a flood of numbers — the
  coordinate reached-for is the signal, repeatedly is the stop), **S2 comprehension failure** (you can
  no longer say what change would move the drawing toward the reference — you are guessing),
  **S3 perception failure** (the review pipeline cannot report, or cannot distinguish two drafts).
  On any stop: park with status / next step / blocker, leave the round's artefacts and numbers
  committed, and report — do not keep iterating to look busy.
- **2026-09-15 · D28 — the ratchet floor is now PARAMETRIC; the hand-fitted render becomes the fidelity
  reference and teacher.** Approved by direction ("actually draw a proper person", not trace it) after
  D26/D27 proved the old floor could only be cleared by tracing. Two registers now:
  - **the floor** (`baseline/best.png`, `best.json`) = the best artifact *made the way drawings are made
    here* — the M2 assembly, fitted families, **0% traced**: whole-frame `edge_f1` 0.164, coverage 0.571,
    `color_dist` 59.6. This is what a new render is compared against, so the ratchet compares like with
    like and can actually move.
  - **the fidelity reference** (`baseline/fidelity-reference.png` + `.json`) = the 2026-09-11
    hand-fitted render, preserved as the **best match to the target** and as a **teacher**. It is
    hand-fitted, so it is a trace, not a drawing; it is *not* the thing to beat.
  Note the parametric floor already **beats the hand-fit on coverage (0.571 vs 0.514) and colour
  (59.6 vs 62.8)** and trails only on edge correspondence — which is the trace-vs-drawing difference.
- **2026-09-15 · D29 — the body was never drawn, and that is the real state of the artifact.** Measured
  after the user looked at the render: the body region (below y420) has coverage **0.581** but
  `edge_f1` **0.102** — the colour masses are roughly in place and there is almost no drawing inside
  them. Every body node is a flat primitive (one blouse blob, one neck blob, three bow ellipses, two
  skirt blobs, two petal blobs); **no arms, hands, collar, sleeves, cuffs or pleats**, and zero body
  families. M2 spent four attempts on the head while M3 (the body) never started, and the milestone
  reports said "the head passes its bar" without foregrounding that three quarters of the drawing is
  untouched. That is a reporting failure as much as a drawing one. M3a (upper body) is dispatched.
- **2026-09-15 · D26 — the fidelity floor and G7 are mutually exclusive for this subject (PROVEN, with
  a decision pending).** M2 attempt 4c reached **G7 (traced share 0.000)** with fitted families, and the
  head's `edge_f1` fell to **0.340** against a bar of 0.412. That is not a shortfall — it is a
  contradiction, proven by a controlled experiment the writer ran and I reproduced: simplifying the
  *actual* hair trace and changing nothing else, `edge_f1` only reaches 0.413 at **78 vertices /
  IoU 0.957**. So `edge_f1` ≥ 0.412 requires the hair silhouette within ~5px of the reference, i.e.
  essentially the traced contour, while a genuine ≤4-point gesture family tops out at IoU 0.80.
  **Reaching the bar requires tracing, and G7 forbids tracing.**
  **Root cause:** the bar was set at `baseline − 0.01` and the baseline is **hand-fitted to
  `image.jpg`**. A hand-fitted artifact compared against a parametric drawing on edge fidelity is a
  *trace compared against a drawing*, and the trace wins by construction — D21's lesson one level
  deeper (D21 fixed admissibility; this is calibration).
- **2026-09-15 · D27 — the like-for-like picture, which the baseline framing hides.** Comparing the
  parametric head with its own parametric past:
  M1 0.166/0.544 → M2 att2 0.173/0.585 → **M2 att4c 0.340/0.747** (edge_f1 / coverage) with **zero
  traced geometry**. The parametric head **doubled** its edge correspondence and now **beats the
  hand-fitted baseline on coverage** (0.747 vs 0.702). Proposed resolution (needs the user — it changes
  the spine): **the ratchet floor should be the best PARAMETRIC artifact**; the hand-fitted 2026-09-11
  render becomes a **fidelity reference and teacher**, not the competitive floor. A ratchet is only
  meaningful against artifacts made the same way, and today's floor can never be fairly cleared by a
  drawing that does not trace. `hair-mass` also landed: 3 clumps, IoU 0.799, ceiling ≈0.80 because a
  tapered band cannot make the fringe's concave inner corner; face re-fit improved 0.552 → 0.576.
- **2026-09-15 · D25 — Option A APPROVED: fit the families to the traces, then discard the traces.**
  The 81% traced share was raised with the user as a method decision (it was, per D24); the user chose
  fitting over accepting trace-backed artifacts. Consequence now in the roadmap: **gate G7** — at a
  milestone exit the traced share of the artifact must be **0**, every shape a family or a relation.
  A `traced` node may exist *during* work (it is the teacher's measurement) but not in the artifact the
  milestone exits on. M2's AC gains A5: the head's geometry is families whose **canon values are
  written into `vocabulary.md`**, because those values are the transferable knowledge. Work is sliced
  brim → face → hair, brim first because it is the structurally hardest.
  First measurement of that slice: the best ellipse fit to the traced brim outline leaves points **48%
  off** it, and `hat-far-navy` is *crown and far brim in one navy mass* — so the fit instrument must be
  **mask-based (IoU against the family's own render)**, not outline-based, and the family may prove
  structurally unable to express this hat (a real floppy brim droops; its silhouette is not an ellipse).
  A poor best-IoU, honestly reported, is a successful result.
- **2026-09-15 · D24 — the teacher loop must extract parameters, not keep the measurement.** The fix to
  evaluate: use the trace as ground truth to **fit the families**, then discard it — traced brim
  outline → fit `sunhat` (`brim/flat/tilt/lift/crown/crown-h`); traced hair → fit `hair-mass`; traced
  skin → fit `face` (`cheek/jaw/chin-w`). The artifact then becomes family instances carrying measured
  canon values, and M5 has knowledge that can actually transfer. Honesty hinge: **fit to the teacher's
  measurement, never to the evaluation metric** — fitting `sunhat` to the traced outline is parameter
  extraction; nudging `brim` until `edge_f1` rises is invariant 4's optimizer regression. This is a
  method decision and is being raised with the user rather than assumed.
- **2026-09-15 · D22 — attempt 3's real value is the instrument, not the artifact.** Kept: the
  `region` front-end node and `--ref` plumbing (the materialization step needs them), the improved
  `flood_region(fixed, box, eps)`, `z-pom`, 27/27 tests, and above all the **`TEACHER` diagnostic**
  (5 firings) with its loud `SpecError` when `--ref` is absent — the mechanism that made this finding
  catchable, and what will keep M5 honest. The writer's own assessment was correct and is quoted in the
  log: the head is traced detail while the body is flat, so it should not promote the ratchet.

## Where things live

- **direction** — `docs/drawing/roadmap.md` (this file's counterpart)
- **authoring language** — `docs/drawing/abstraction.md` → `scripts/relate.py`
- **object families + canons** — `docs/drawing/vocabulary.md`
- **compiled back end** — `docs/drawing/scene-format.md` → `scripts/scene_render.py`
- **loop, style guide, tier ladder** — `docs/drawing/method.md`
- **transferable lessons** — `docs/drawing/principles.md` (append-only)
- **the ratchet** — `.scratch/00-tooling/baseline/` + `scripts/draw baseline`
- **the assembly** — `.scratch/13-assembly/work/spec.yaml` (M1 complete; this is the live drawing)
- **the gate instrument** — `.scratch/13-assembly/work/measure-composition.py` (placement check)
- **work log per exercise** — `.scratch/NN-slug/{spec.md,work,evidence,log.md}`
