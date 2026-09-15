# 13-assembly — log

## 2026-09-15 — M1: recover the baseline's composition

**Outcome: M1's exit criteria are met; the baseline is NOT promoted.** M1's job was to stop the
project sitting below its own bar and to give every later milestone a measured-correct frame. It did
that. It did **not** produce a better drawing than the 2026-09-11 baseline — with flat masses and no
line work it could not, and requiring that of it would have made the milestone unreachable
(see `STATUS.md` D7/D8, roadmap M1).

| | coverage | edge_f1 | color_dist | coarse-grid distance (8×8) |
| --- | --- | --- | --- | --- |
| target (image.jpg) | 1.000 | — | 0 | 0 |
| **baseline** (2026-09-11) | 0.514 | 0.252 | 62.8 | **32.6** |
| night's "FINAL" (`full-v2`) | 0.091 | 0.082 | 109.4 | — |
| **M1** (`evidence/m1-final.png`) | **0.528** | 0.082 | 68.8 | 39.1 |

So: coverage above the baseline (+0.014, nothing deleted), colour 6.0 units further off, and still
7 grid units behind on overall mass distribution. The ratchet stays where it is.

### Iterations (every render looked at; metrics as alarm only)

| iter | change | coverage | grid (8×8) | verdict |
| --- | --- | --- | --- | --- |
| v1 | first assembly from measured masses (17 nodes) | 0.497 | — | two real diagnostics; field as a bbox-fit ellipse over-filled by 56% |
| v2 | field area-matched; `hair-left` slab → thin stroke; bow → 2 loops + knot; poms recomputed from `on(t)`; petals added | 0.523 | 39.4 | diagnostics clean; **best up to here** |
| v3 | trim the clipped petal | 0.523 | 39.4 | diagnostics clean |
| v4 | enlarge the cream mass toward the measured deficit | **0.502** | 43.2 | **worse — rolled back.** The missing cream is behind the bow and hair: an occlusion problem (M3), not a size problem |
| it5 | enlarge the field toward the measured mint mass | **0.528** | **39.1** | **best — kept** |
| it6 | + `hair-cap` over the skull | 0.528 | 39.4 | slightly worse — dropped |
| it7 | hair reshaped from the reference's measured band profile | — | **42.8** | **much worse — rolled back** |

### Two findings worth more than the milestone

1. **A per-element centroid is a diagnostic, not an objective.** it7 moved the hair centroid from
   `(0.825,0.472)` to `(0.770,0.440)` — much closer to the reference's `(0.713,0.348)` — and made the
   drawing *worse* (grid 39.1 → 42.8). Optimising the indicator against the evidence is exactly the
   failure the project banned in invariant 4, migrated one level up. Filed as `principles.md` P25.
2. **A gate can be wrong, and finding that out is a result, not an excuse.** M1 was gated on
   `edge_f1 ≥ best − 0.01`, but M1 is *defined* as flat masses, so the floor failed it for doing its
   job — and pressure to pass would have pushed M2/M3 work into M1 (the "one ticket doing several
   things at once" failure that got 05 frozen). The gate was split into an alarm that applies always
   and a detail floor that applies once detail is the job, and promotion was separated from milestone
   exit. Recorded as a spine change (D7), not quietly relaxed.

### Reviewer evidence (G3)

Two fresh-context reviewers given the target plus the two renders under neutral names:

- both agreed the **baseline is the better drawing** (finish: eyes, line work, hands, collar);
- they **disagreed on composition** — one said the baseline, one said M1.

Per P7 the disagreement was settled by measurement, not by picking a verdict: the coarse-grid
colour-mass distance puts the baseline ahead (32.6 vs 39.4), agreeing with the first reviewer. The
per-element table (`evidence/m1-placement-check.txt`) shows *why* the two disagreed so easily — M1 is
closer on 7 of 13 masses, several decisively:

| element | target | M1 | baseline | closer |
| --- | --- | --- | --- | --- |
| skirt dark | (0.474,0.878) 7.8% | (0.480,0.864) 9.1% | (0.682,0.662) **0.6%** | **M1** — the baseline barely has the dark skirt at all |
| head/face | (0.675,0.321) 1.2% | (0.676,0.312) 1.3% | (0.670,0.338) 1.5% | **M1** |
| bow magenta | (0.656,0.510) 1.5% | (0.655,0.509) 2.8% | (0.664,0.496) 1.6% | **M1** |
| petal pink | (0.317,0.885) 2.7% | (0.367,0.909) 3.8% | (0.272,0.806) 1.1% | **M1** |
| ribbon blue | (0.245,0.492) 1.0% | (0.279,0.333) 3.8% | (0.066,0.689) **0.1%** | **M1** — the baseline's ribbon is missing too |
| blouse pale | (0.738,0.559) 3.5% | (0.771,0.578) 2.9% | (0.736,0.558) 2.8% | baseline |
| hair blue | (0.713,0.348) 7.5% | (0.825,0.472) 8.2% | (0.785,0.325) 8.0% | baseline |
| mint field | (0.409,0.572) 17.6% | (0.334,0.546) 14.7% | (0.322,0.614) 14.8% | baseline |

The honest reading: M1 fixed real composition errors the baseline has (dark skirt mass, ribbon, bow,
petal mass, face position) and inherited others (under-sized mint field, hair too far right and low).
The baseline wins the aggregate because it spreads the right colours more evenly, not because its
figure is better placed.

### Gate results

| gate | result |
| --- | --- |
| G1 render + bundle | ✅ `evidence/check/` (1:1 draft + subject-weighted crop listed) |
| G2 alarm | ✅ coverage 0.528 ≥ 0.514; color_dist 68.8 ≤ 77.8 |
| G2b detail floor | ✗ edge_f1 0.082 vs 0.252 — **not gating in M1** (D7) |
| G3 placement | ⚠️ partial — 7/13 masses closer than the baseline; recorded above, not claimed as a pass |
| G4 diagnostics | ✅ none |
| G5 authoring budget | ✅ 17 nodes, all with intent; no outline > 4 points; spines 2–3 points |
| G6 determinism | ✅ byte-identical (`53ffff46…`) |

### Carried into M2

- The hat's two-tone brim meets in a straight seam through the brim centre (the family's slice split)
  where the reference's boundary is diagonal; the crown barely separates from the navy brim.
- `hair-left` is still a straight thin stroke; the reference's left sweep is a curved wisp.
- The gate has now been exercised end to end once, including the split-reviewer case.

### Evidence

- `evidence/m1-final.png` (the milestone artifact), `evidence/m1-v1..v3.png` (iteration history)
- `evidence/check/` (G1 bundle + report with the ratchet delta)
- `evidence/m1-composition-reference.txt` (G3 reference measurement)
- `evidence/m1-placement-check.txt` (G3 placement table + grid distances)
- `work/measure-composition.py` (the G3 instrument — reusable, deterministic, no verdict)

## 2026-09-15 — M2 attempt 1: the head. NOT COMPLETE (parked with a precise next step)

**Outcome: the gate was not passed.** The head region got real structure, but the measurement says it
is still further from the reference than the baseline's head is. Both facts are recorded; nothing is
promoted.

| head-region colour-mass distance (lower = closer) | M2 | baseline |
| --- | --- | --- |
| 16px cells | 52.1 | **33.1** |
| 32px cells | 48.4 | **28.6** |
| 64px cells | 40.7 | **22.4** |

| structural check | target | M2 | baseline |
| --- | --- | --- | --- |
| visible face skin bbox | 151×153 | 164×180 | **150×151** |
| hair covering the eye band (x620-790, y240-300) | 17.6% | 31.3% | 33.7% |

Two fresh-context reviewers **split** on the head crop (one preferred the head's hat/crown and called
M2 the better drawing; one called the baseline structurally closer and M2's hair a "solid cap").
Per the roadmap rule the split was settled by measurement — and the measurement sides with the
baseline, decisively, at every grid scale. So: reviewers split, measurement against, **not promoted**.

### What M2 landed and is kept

- **`face` vocabulary family** (new, in `scripts/relate.py`): cranium ball + jaw wedge, with the jaw
  profile taken from the measured taper. The anchor box is unchanged (`head.rx/ry/w/h` still work),
  so every node M1 measured against the ellipse kept working.
- **Two eyes placed independently**, not `mirror-of`: this is a 3/4 view, so the far eye is 0.75× the
  near one. Using the mirror relation here would have forced them equal — a case where the language's
  convenience would have produced a wrong drawing.
- **Fringe + both cheek locks.** Not decoration: the reference's *visible* face is 151×153 only
  because hair covers the forehead and both cheeks. The same head without that hair renders 190×203.
- Brows, nose and mouth from the measured canons.
- Totals moved: `edge_f1` 0.082 → 0.106, `color_dist` 68.8 → 66.4, coverage 0.519, diagnostics clean
  except two honest SUB-PIXELs (the far eye's reflection dot; a 2.3px-tall mouth).

### Bug the gate caught (this is why the gate exists)

The first `face` implementation drew a **full-height cranium plus a jaw wedge inside it**, so the
cranium's round bottom *was* the silhouette and the jaw was invisible. Both reviewers independently
reported "round blob, no chin" — and both were right. Fixed: the cranium now stops just past the
cheek line, so the jaw below it is the silhouette. Verified against the reference's own row profile:

```text
target  y318:108  y330:100  y342:98  y354:97  y366:57  y378:0
M2      y316:117  y328:105  y340:97  y352:91  y364:59  y376:0
```

### The biggest unfixed defect (next step)

**The brim does not read as one piece.** The `sunhat` near-slice is painted teal and the far slice
navy, and with this hat's tilt (+17°) and lift, the teal piece visually *detaches* — both reviewers
saw "a teal wedge floating left of a navy blob", and one called it "no hat at all" in the baseline,
"a detached lozenge" in M2. The chord-segment fix (M1) removed the converging-V seam but did not make
the two slices read as one brim. Root cause to investigate next: the brim is one ellipse with two
fills, but the *crown* merges into the navy slice while the teal slice has no shared edge with either,
so there is no continuous silhouette line. Candidate fix: stroke the brim outline as one shape
(one continuous edge over both slices) rather than relying on fill adjacency.

Secondary, unfixed: the fringe still reads as a cap/band to both reviewers; the face is 9% too wide
and 18% too tall; the far eye is partly occluded by a cheek lock.

### Evidence

`evidence/m2-*.png` renders · `evidence/check-m2/` gate bundle · head-crop A/B crops were handed to
the reviewers with neutral names (`A` = baseline, `B` = M2) and no context.

## 2026-09-15 — M2 attempt 2: the brim split was the cause. Better, still not passed

**The defect was real and is fixed.** A writer subagent found the actual root cause, which was not
what I had guessed. `sunhat` split the brim with a **straight chord across the disc** (perpendicular to
the brim's long axis), so the two fills met only at the two tips — and the tips plus the chord are
exactly where the hair and crown sit. Hence "detached teal lozenge". The fix replaces the chord with
the brim's **far edge folding over**: the far slice is now the rim band hugging the far outline, the
near slice is the top surface it borders, and a new optional `rim` parameter (default 0.45) sets how
far the fold comes in. The two fills still share every seam vertex in opposite directions and tile the
ellipse exactly. **I had proposed stroking the brim outline as one shape; the subagent evaluated that
and rejected it, correctly** — it connects the brim but draws a hard line across exposed skin where
this drawing's brim edge crosses the face. Good call, and it is the kind of pushback I want.

Also fixed: `lift` 1.22 → 1.05 (the crown mass was floating above the skull — crown at y58 vs the
reference's y92), and `pom-at` corrected so both poms land on the reference's measured pom centroids.

| | whole-frame edge_f1 | coverage | color_dist | head-crop colour-mass dist (64px) |
| --- | --- | --- | --- | --- |
| baseline | **0.252** | 0.514 | **62.8** | **22.4** |
| M2 attempt 1 | 0.106 | 0.519 | 66.4 | 40.7 |
| **M2 attempt 2** | 0.108 | **0.529** | 65.6 | 36.2 |

Every alarm moved the right way vs attempt 1. **The gate is still not passed**, and the reason is
now precise and measured, not a matter of taste:

```text
head-region edge_f1     baseline 0.422   M2 0.173
head-region coverage    baseline 0.702   M2 0.585
```

### The strategic finding (this is the important output of attempt 2)

The baseline wins the head region **because it was hand-fitted to the reference.** Its 133 nodes were
traced and fitted against `image.jpg`, so of course its edges sit near the reference's edges and its
colours near the reference's colours. M2 is a from-scratch relational rebuild, so it is *more
coherent* (reviewers said so) and *less accurate* (the metrics say so). Both are true.

That exposes an error in how M1/M2 were done: **I threw away reference-accurate seeded values and
re-derived them coarsely from colour components.** `abstraction.md` explicitly supports using the
reference to *seed values* ("measuring the reference to fill in the numbers in a spec, then closing
the image") — and a `trace`/`region` node is the documented, sanctioned way to do it. The 824-coordinate
failure was about **hand-typing** coordinates, not about using traced ones. So the assembly re-invented,
badly, values that were already measured accurately and were sitting in the repo.

Corrected strategy for M2 attempt 3 / M3 (recorded as `STATUS.md` D15): keep the relational structure
and the vocabulary, and **seed the geometry from the reference where the relational approximation is
measurably far off** — the values are the teacher's, the structure is ours. This is not a retreat from
the reframe; it is what the reframe said to do and I did not do it.

### Gate-scoping defect, third occurrence (D14)

G2b ("detail floor") was written as a whole-frame `edge_f1` floor applying "from M2 onward" — but M2
owns only the head, so a whole-frame floor fails it for work it was never asked to do. This is the
**third** time the same defect has appeared (D7 for M1, D7's G2b for M2, now again). The general rule,
now recorded: **every comparison gate is evaluated on the region the milestone owns; the whole-frame
alarm (G2) always applies as well.** A gate whose measurement window is wider than the milestone's
scope is a defect in the gate, not a failure of the work.

### Kept / not kept

Kept: the `sunhat` fold fix (`rim`), the `lift`/`pom` corrections, all of attempt 1's face/eye/fringe
work. Not fixed: the brim is still much shallower than the reference's crescent droop (a flat ellipse
cannot express it — stated honestly by the worker rather than force-fitted); the fringe covers the
mid-brim; the crown reads as a small bump.

Worker notes worth recording: it also had to **reinstall the playwright/chrome-headless-shell cache**,
which had been deleted mid-session (a chrome coredump was present) — renders were impossible until it
did. Environment repair, no repo files involved.

## 2026-09-15 — M2 attempt 2: no visual verdict obtainable; measurement decides

Both fresh-context reviewers dispatched for attempt 2 **could not see the images** — every render
read returned "model does not support images". Earlier reviewers in this same session *did* give
detailed visual descriptions (they quoted colours, positions, malformations), so **vision is not
stable across subagent instances**: the harness routes subagents to different models and some are
sighted, some are not. The orchestrator itself has no vision at all (D17).

This is a first-class change to the method, recorded as D18. What matters here is narrower:

- **No visual verdict exists for attempt 2, so G3 was not run.** The measurement decided instead, and
  it says the baseline's head is still ahead (region `edge_f1` 0.422 vs 0.173, region coverage 0.702
  vs 0.585). Attempt 2 therefore fails on the measured half of A1 and is untested on the visual half.
  It is **not** recorded as a visual pass, and not recorded as a visual failure either.
- The right response was exactly what the reviewer did: **refuse to invent a verdict**. Both reported
  the blocker, labelled the rest as inherited-from-the-repo rather than observed, and asked for the
  A/B identity to be confirmed before anything was acted on. That is the culture the project is for.

### A/B provenance — a real gap the reviewer caught, now closed

Neither round recorded which file was handed over as A and which as B. Fixed here, and the identity
was verified by pixel comparison rather than from memory:

| round | A | B | verified |
| --- | --- | --- | --- |
| M2 attempt 1 | baseline `best.png` | `evidence/m2-v7.png` | maxdiff 190 vs attempt 2 — confirmed distinct |
| M2 attempt 2 | baseline `best.png` | `evidence/m2-att2.png` | pixel-identical to both sources (maxdiff 0) |

Rule for the future: **the A/B mapping is recorded in the log in the same session it is handed over**,
and confirmed by pixel comparison against the two source files, never from memory.

### Source-level findings from the attempt-2 review (no sight required, still useful)

The reviewer could not look, so it read the two specs instead and produced a structural comparison
that stands on its own:

- **The baseline's brim has no single outline.** `.scratch/05-portrait-scene/work/scene.yaml:141-148`
  is four independent filled polys (`brim-underside`, `hat-dome`, `brim-band`, `brim-teal-rim`) plus
  **two disjoint open strokes** `brim-edge-1`/`brim-edge-2`; only the dome carries a stroke. That is
  a structural reason "the brim is not one piece" that no amount of fill-tuning in M2 would fix — and
  it is now independent support for attempt 2's chord→fold fix in `sunhat`.
- **The baseline's brim is clipped by the canvas** at `x=1024`, where the reference's brim mass ends
  at x982 (`evidence/m1-composition-reference.txt`) — a ~42px frame-trespass the reference does not
  have. Recorded as a baseline defect; it does not change the ratchet, but it is worth knowing that
  the current best artifact is wrong at the frame edge.
- The baseline's `skin` is one 15-point poly whose lowest run is ~75px wide at y392-394, against the
  reference's 7px chin at y377 — independent confirmation of the blunt-chin defect, by reading the
  spec rather than the pixels.

## 2026-09-15 — M2 attempt 3: the gate was PASSED, and that is the problem

The strategy correction (D15) worked, technically and completely. A writer subagent added a `region`
front-end node to `relate.py` (flood-fill on the reference raster, `seed`/`tol`/`box`/`eps`, all
relation-valued, zero hand-typed coordinates), forwarded `--ref` through `relate.py` and `draw.py`,
and improved `scene_render.flood_region` (fixed-range flood, clip box, contour eps). Then it seeded
the head's geometry from the reference.

**It beat the bar decisively:**

| head region (x400..1020, y0..420) | baseline | attempt 3 | bar |
| --- | --- | --- | --- |
| `edge_f1` | 0.422 | **0.619** | ≥ 0.412 |
| coverage | 0.702 | **0.778** | ≥ 0.692 |
| `color_dist` | 43.1 | **32.9** | — |

Whole-frame too: coverage 0.580 ≥ 0.514, `edge_f1` 0.271 vs the baseline's 0.252 — the first time the
assembly leads the baseline on whole-frame edge correspondence.

**And it must not be accepted, because of how it was achieved.** Five spec nodes are `region` floods of
`image.jpg`, and:

```text
$ .venv/bin/python scripts/relate.py .scratch/13-assembly/work/spec.yaml -o /tmp/noref.png
relate: region 'face-skin' needs the reference raster (--ref);
        region is teacher-only and may not appear in a reference-free spec
```

The spec **does not render with the image deleted.** That is a direct violation of P18 / invariant 6
("the engine must never depend on the target"), and it breaks the test `abstraction.md` states for
every addition. The artifact is no longer a drawing that stands alone — it is a live copy of the
reference in five regions, with the invented families hidden underneath it.

### Why the gate did not catch this, and what that means

The gate compared the assembly to the baseline **on fidelity to the reference**, and the baseline was
itself hand-fitted to the reference. So "beat the baseline" reduced to "trace the reference more
accurately" — which any tracer wins trivially, and which teaches the model nothing about drawing. The
gate was measuring **copying**, not drawing. A gate that can be passed by copying the answer is not a
gate.

### The correction (D20/D21) — materialize, don't depend

`abstraction.md` already names the supported teacher uses, and both are *removable*: "measure the
reference to fill in the numbers in a spec, then close the image." A live `region` node is a **third**
way that is not removable, and it is the one that must not be used in the artifact.

So the teacher step becomes a **materialization**:

1. resolve once with `--ref` (the tracer computes the geometry);
2. **freeze** the computed vertices into a sidecar data file with provenance (source, date, method,
   digest);
3. the spec references the frozen data by name;
4. **the spec now renders with `image.jpg` deleted** — invariant 5 is satisfied (the vertices were
   *computed* by the tracer, not typed by a human), P18 is satisfied (no live raster dependency), and
   the gate finally measures a drawing.

New gate rule (D21): **the artifact a comparison gate judges must render without the reference.** If
it needs `--ref`, the gate result is void — reporting it is not a pass, and it is not a failure of the
drawing either; it is a failure of the artifact's admissibility.

### Kept from attempt 3 (real work, and it is a lot)

- The `region` front-end node and `--ref` plumbing — genuinely useful, and it is the tool the
  materialization step needs to exist at all.
- **The `TEACHER` diagnostic** (5 firings above) and the loud `SpecError` without `--ref`. This is the
  single most valuable thing attempt 3 produced: it is the mechanism that made this finding catchable
  at all, and it is what will keep M5 honest.
- `scene_render.flood_region(fixed, box, eps)`; `sunhat z-pom`; 27/27 tests; byte-identical
  determinism; the three historical specs still resolve **and render byte-identically**.
- The writer's own honest assessment, which was right: *"the drawing is now unbalanced — the head is
  traced detail while the body remains M1 flat masses… it may pass M2's region gate but should not
  promote the ratchet."* Correct, and it is why the ratchet did not move.

**Baseline NOT promoted.** Next slice: implement the freeze step and re-run M2's gate on an artifact
that stands up with the image deleted.

## 2026-09-15 — M2 attempt 3 materialized: the artifact is ADMISSIBLE, and 81% copied

The freeze slice worked exactly as designed. Verified by me, not taken on report:

```text
$ mv image.jpg /tmp/hidden.jpg
$ .venv/bin/python scripts/relate.py .scratch/13-assembly/work/spec.yaml -o /tmp/noref.png
resolved 48 nodes across 14 layer(s)      # diagnostics: only the two honest SUB-PIXELs, no TEACHER
$ scripts/draw check …/spec.yaml --outdir …            # exit 0
$ mv /tmp/hidden.jpg image.jpg                          # restored, sha256 intact
```

**G0 now passes.** `draw freeze <spec> --ref image.jpg` writes each raster node's computed outline to
`.scratch/13-assembly/work/traced/<node>.json` with full provenance (`image_sha256`, seed, tol, eps,
method, vertex_count) and a new `traced` front-end node loads it with **no raster opened**. Staleness
is loud: a changed `image.jpg` sha256, a missing file or a malformed file all raise `SpecError`.
`region` and its `TEACHER` diagnostic are untouched.

Quality is unchanged: the no-`--ref` render is **byte-identical** to attempt 3's live-region render
(`785a597d…`). Head bar met (`edge_f1` 0.619 vs the baseline's 0.422; coverage 0.778 vs 0.702);
whole-frame `edge_f1` 0.271 vs 0.252. Deterministic across three no-ref resolutions. Tests 34/34.

### The number that matters: 81% of the head is copied, not drawn

Attempt 3 gave M2 a measurable pass by flood-filling the reference. The freeze made that **legal**
(admissible, provenance-carrying, reproducible) — and measured it:

| measure | value |
| --- | --- |
| traced share of the head crop's **painted** pixels | **81.0%** (120 749 of 149 052) |
| traced polygons as a share of the whole head crop | 47% (123 055 of 260 400 px) |
| my independent cross-check | 123 055 traced px ≈ their 120 749 painted — **consistent** |

Instrument: `work/measure-trace-debt.py` (kept; it should become a gate instrument).

### Why this is a problem, stated precisely

A **frozen contour is not a learned canon.** `vocabulary.md` defines a canon as proportion knowledge
as a fraction of a host measure ("brim ≈ 2.9 head-widths", "eyes at half head height") — knowledge that
**transfers to a new subject**. A traced outline transfers to nothing: it is one specific shape, and it
says nothing about how to draw the next head. So 81% traced means 81% of the head carries **no
transferable learning**, and it is precisely the 81% that M5's withdrawal would have to re-invent from
scratch — the thing that failed at attempts 1 and 2.

The teacher loop `abstraction.md` describes is: **measure → extract canon parameters → close the
image → re-instantiate from parameters.** Freezing a contour skips the "extract parameters" step and
keeps the measurement as the drawing. That is the drift: the ladder heading from *learn to draw*
toward *learn to trace*.

**Therefore M2 is NOT closed.** Its gate as written is met on measurement, but the gate has no
transferability criterion, so it cannot tell a drawing from a copy. Baseline not promoted.

### The fix to evaluate (proposal, needs a decision)

Use the trace as the teacher's **ground truth to fit the families to**, then throw the trace away:

- traced brim outline → **fit `sunhat`** (`brim`, `flat`, `tilt`, `lift`, `crown`, `crown-h`) → the brim
  becomes a family instance with measured canon values, and the values are the transferable knowledge;
- traced hair silhouette → fit the `hair-mass` family (spine, width profile, tip zigzag);
- traced face skin → fit `face` (`cheek`, `jaw`, `chin-w`).

Then the artifact is **100% family instances with measured canons**, the traces are kept as the
teacher's evidence (not as the drawing), and M5 has something that can actually transfer. The
distinction that keeps this honest: **fit to the teacher's measurement, never to the evaluation
metric** — fitting the sunhat to the traced outline is parameter extraction; tuning `brim` until
`edge_f1` rises is the optimizer regression invariant 4 forbids.

## 2026-09-15 — M2 attempt 4: the brim becomes a family, and the real bug was Z-ORDER

Option A (fit the families to the traces, then discard the traces) sliced brim-first, since the brim
was the structurally hardest. Delegated; everything below re-verified by me.

### What the fit proved

New instrument `work/fit-family.py`: given a family and its frozen `traced` targets, it searches the
family's parameters to maximise **IoU against the teacher's mask** — deterministic (Halton exploration
→ axis-wise coordinate descent → dependency-free Nelder-Mead), and it never reads `edge_f1`. It also
handles the union explicitly: `hat-far-navy` is **crown + far brim in one navy mass**, so `far` is
fitted as `union(hat-dome, hat-brim-far)`.

| | mean IoU | far | near |
| --- | --- | --- | --- |
| starting params (flat ellipse, as shipped) | 0.393 | 0.407 | 0.380 |
| best possible FLAT ellipse | 0.589 | 0.646 | 0.532 |
| after adding `droop` | **0.720** | **0.846** | 0.594 |

**`sunhat` could NOT express this brim.** 0.589 is the ceiling for the family's structural model, and it
is far from the ≥0.85 that would mean "this family can draw this hat". I independently confirmed the
outline is not an ellipse either: the best ellipse leaves points **48% off** it. So the family gained a
**`droop`** parameter (signed; the fitted value is −0.476, a slight *curl-up*, because this hat is worn
tilted back so the brim's near edge rises in the middle) — **default 0 = the old flat ellipse**, so it is
backward compatible. This is R5 demand-first working as intended: the drawing failed without it.

### The near group's ceiling was a Z-ORDER bug, not a shape bug

The near surface capped at 0.594 and the fitter's report explained why: the reference's visible teal
surface is **two disjoint pieces** (x430–653 and x897–1023) split by the head and hair, and the family
paints one continuous near surface — because **the hat was painting ABOVE the head**, so the brim's near
surface had to cover the face gap. I tested that directly by moving `hat`/`hat-front` **below** `head` in
the layer list:

| | head `edge_f1` | head coverage | whole-frame `edge_f1` |
| --- | --- | --- | --- |
| baseline | 0.422 | 0.702 | 0.252 |
| hat above head (fitted) | 0.381 | 0.731 | 0.185 |
| **hat BELOW head** | **0.479** | **0.744** | 0.219 |

Zero hard diagnostics. The reference is the same fact seen from the other side: the hat is worn high and
**its brim passes behind the skull**, while the crown and the brim's left/right lobes stay visible above
and beside it. The declared relation was corrected from `front: hat` to `front: head` with that reasoning
in its `desc` — otherwise the engine's own CONTRADICTION diagnostic fires, which is exactly its job.

### Where M2 stands

- Head region: **`edge_f1` 0.479 ≥ bar 0.412 and ≥ baseline 0.422**; coverage 0.744 ≥ 0.692. **Passes.**
- Traced share of the drawn head: **0.810 → 0.391** (the two remaining traces are `face-skin`,
  `hair-mass`).
- Tests 44/44 (10 new for the fitter and `droop`); deterministic ×3 with no `--ref`; G0 holds;
  historical specs unaffected.

**Not yet M2's exit, for two measured reasons:** G7 requires the traced share to reach **0**, so the face
and hair must be fitted too; and the `sunhat` parameters were fitted under the *old* z-order, when the
hat was above the head and the only occluder was `hair-mass`. Now that the head occludes the brim as
well, the fit must be redone with `head` and `hair-mass` as occluders — the near group should improve
beyond 0.594, and until it does the fitted values are known-stale.

## 2026-09-15 — M2 attempt 4b: sunhat re-fitted, face fitted, and the ruler must stay pinned

Delegated; all numbers below re-verified by me. The `face-skin` trace is gone; only `hair-mass` remains.

### The fitter's occluder logic was wrong, and that made the previous fit stale

`fit-family.py` had a **hard-coded** occluder (`hair-mass`). Since the z-order fix (attempt 4) the
`head`, `features` and hair all paint above the hat, so the brim's fit had been scored against an
occlusion that no longer existed. It now derives occluders from the spec's own `layers:` order
(`group_occluders` + a `paint_order` that replicates the renderer exactly, full-rects first, then a
stable sort by layer index) and re-resolves the whole spec per candidate — so head-relative occluders
move with a face being fitted. Changing `layers` changes the answer, and that is what the new test `t`
asserts.

| `sunhat` | mean IoU | far | near |
| --- | --- | --- | --- |
| shipped params, old occlusion (hair only) | 0.7199 | 0.8456 | **0.5943** |
| shipped params, corrected layer-derived occlusion | 0.7284 | 0.7713 | **0.6856** |
| **re-fit, corrected occlusion** | **0.7414** | 0.7801 | **0.7028** |

The near group rose **0.594 → 0.686 → 0.703**. The far group *falls* 0.846 → 0.780, and that is
correct: the old 0.846 was cheating — it never subtracted the head, features or hair that actually
cover the navy, and it let the near surface cover the face gap.

### `face`: fitted, and honestly reported as unable to express this head

The brief named one ill-posedness (the `face-skin` trace is the **visible** skin, so the fit must be
scored with occluders applied — it was). The writer found a **second one the brief did not name**:

> the `face` node is the **ruler**; the hat, eyes and hair are all placed off `head.*`. If `at/rx/ry`
> are free the optimiser moves the whole head to chase the hair-occluded skin.

Measured, and this is the important table:

| fit | IoU | head `edge_f1` | head coverage |
| --- | --- | --- | --- |
| head box pinned, `cheek/jaw/chin-w` only | 0.538 | 0.478 | 0.744 |
| + `turn` (a real 3/4-view parameter, doesn't move the ruler) | **0.552** | 0.474 | **0.759** |
| all of `at/rx/ry` free | 0.691 | **0.328** | **0.385** |

So the free fit buys IoU 0.691 by shrinking the head (rx 95 → 52) and **collapses the head gate**. The
spec uses the constrained fit; the ruler stays at the measured skull box. Verdict, stated plainly:
**`face` cannot express this visible skin — best IoU 0.552 at a fixed ruler**, for two measured
reasons: the `hair-mass` teacher is one coarse contour that misses the fringe strands (so skin shows
through them and is penalised), and the family is near-symmetric against a 3/4 view even with `turn`.
Filed as `principles.md` P28.

### Where M2 stands

- Head region: **`edge_f1` 0.474 ≥ bar 0.412 and ≥ baseline 0.422; coverage 0.759 ≥ 0.692.**
- Traced share of the drawn head: **0.391 → 0.309**, and the remaining node is **`hair-mass` only**.
- Tests 51/51 (+7 for the generalised occluders and the face registry); deterministic; G0 holds;
  historical specs unaffected (`05/scene.yaml` still reproduces `1a7cae4f…`).
- **Not M2's exit yet**: G7 needs the traced share at **0**, so the hair is the last slice.

### A bug in MY tool, found by the writer

`draw baseline` was recording `sha256` = the digest of the **source** file while storing a **re-encoded**
copy as the artifact. So `best.json` claimed a hash the artifact did not have (`1a7cae4f…` vs the
stored `6c550f…`), pixels identical, bytes not — which quietly breaks the one property the baseline
exists for: that the documented render reproduces it exactly. Fixed in `scripts/draw.py`: the artifact
is now a **byte copy** (`shutil.copyfile`) with an assertion that it reproduces the source, and the two
digests are recorded separately and named `source_sha256` / `artifact_sha256`. Re-recorded, verified
equal, and the baseline is still self-consistent (`vs recorded best:` all `+0.000`).
