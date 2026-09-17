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

## 2026-09-15 — M2 attempt 4c: G7 reached, and the fidelity bar is proven unreachable without tracing

Delegated; verified by me, including reproducing the decisive experiment.

### The hair family

`hair-mass` is now a real family in `relate.py`: a **tapered band around a gesture spine** (2–4
relation-valued points), with `w` as a per-point width profile, `side` (both/left/right), `zig`+`tips`
for strand separation, optional `strands`, and normal handles plus `rootx/rooty`, `tipx/tipy`. The
spec says "hair, this big, sweeping here"; it carries the silhouette logic. 12 new tests, 63/63.

Fitted to the hair trace with occluders applied (never to `edge_f1`):

| decomposition | IoU vs the teacher mask |
| --- | --- |
| 1 ribbon | 0.670 |
| 2 instances (fall + lock) | 0.751 |
| **3 instances (fringe + fall + lock) — shipped** | **0.799** |

**Ceiling ≈0.80 for this family form**, and the reason is specific: it captures the mass *extent*
almost exactly (2.49×2.89 head-widths vs the teacher's 2.48×2.93) but cannot make the **concave inner
boundary** — the fringe/hairline corner. A tapered band is convex along its spine.

### G7 is now met: traced share = 0.000

```text
traced   0 px  (0.000 of drawn)
G0: 0 TEACHER diagnostics with image.jpg moved away
```

The artifact is a drawing again: every shape a family or a relation. The three teacher sidecars stay on
disk as evidence. The `face` re-fit also improved once the hair was a family (IoU 0.552 → 0.576), which
is the coupling the fitter predicted.

### The finding: the detail floor and G7 are MUTUALLY EXCLUSIVE for this subject

Head `edge_f1` **0.340** against a bar of **0.412**. That is not a shortfall to grind at — it is a
contradiction, and the writer proved it with a controlled experiment that I then reproduced myself:

```text
simplify the ACTUAL hair trace and put it back, changing nothing else:
  eps  5 ->  78 verts, IoU 0.957     ->  head edge_f1 0.413   (just at the bar)
  eps  8 ->  62 verts, IoU 0.917     ->  head edge_f1 0.378
  eps 12 ->  51 verts, IoU 0.854     ->  head edge_f1 0.336
```

**Reaching `edge_f1` ≥ 0.412 requires the hair silhouette within ~5px of the reference — IoU ≈0.96,
≈78 vertices — i.e. essentially the traced contour.** A genuine ≤4-point gesture family tops out at
IoU 0.80. So the bar can only be met by tracing, and G7 forbids tracing. The gate set is
self-contradictory for this subject.

**Why the bar was wrong.** It was set at `baseline − 0.01`, and the baseline is **hand-fitted to
`image.jpg`**. A hand-fitted artifact compared against a parametric drawing on edge fidelity is a
**trace compared against a drawing**, and the trace wins by construction. This is D21's lesson one
level deeper: D21 fixed *admissibility* (don't compare an artifact that reads the raster), and this is
*calibration* (don't derive the threshold from a hand-fitted artifact either).

### The honest like-for-like picture

Compare the parametric head against its own parametric past, and the progress is large and real:

| | head `edge_f1` | head coverage |
| --- | --- | --- |
| M1 (fully parametric) | 0.166 | 0.544 |
| M2 attempt 2 (parametric) | 0.173 | 0.585 |
| **M2 attempt 4c (parametric, fitted families)** | **0.340** | **0.747** |
| baseline (hand-fitted — *not* the same kind of artifact) | 0.422 | 0.702 |

The parametric head **doubled** its edge correspondence (0.173 → 0.340) and now **beats the hand-fitted
baseline on coverage** (0.747 vs 0.702) — with **zero** traced geometry. That is the milestone's real
result, and the "vs baseline" framing hides all of it.

### Status

M2 meets **G0, G4, G5, G6, G7** and the coverage floor, and fails **only** the fidelity floor that has
now been *proven* to be tracing-only. So M2 is **blocked on a gate defect, not on the drawing** — and I
am not inventing a number to close it. The fix is a spine change and is with the user (D26).

## 2026-09-15 — rubric pipeline validated, and it caught what the metrics could not

First run of `docs/drawing/rubric.md` (D30), on the frozen parametric floor
(`evidence/m2-final.png`), by two independent sight-proven reviewers given only the target and the
draft. This is the demonstration that the metric-first gating was wrong.

| axis | reviewer 1 | reviewer 2 |
| --- | --- | --- |
| A · subject identity | 3 | 4 |
| **B · human figure** | **1** | **2** |
| C · silhouette coherence | 1 | 2 |
| D · feature legibility | 3 | 3 |
| E · occlusion correctness | 1 | 2 |
| F · style + composition | 3 | 3 |

No axis differs by ≥2, so **no axis is contested** — the rubric's agreement rule holds on its first
use. Both reviewers independently proved sight by placing the mint field's right edge at ≈x700–720,
matching the measured x718 in `work/measure-composition.py`.

**The point of the exercise:** the pixel metrics said the body region had **coverage 0.581** — colours
present, nothing missing — and that read as fine. The rubric says **B ≈1.5, C ≈1.5, E ≈1.5**. Both
reviewers, unprompted, named the same biggest defect and the same fix:

> *"The figure is dismembered — a detached head floats above a cream dress shape and a separate dark
> skirt mass, so no body, neck, arms or hands exist at all."*
> *"Trace **one continuous silhouette of the whole seated figure** — head → neck → shoulders → torso →
> skirt → legs — as a single connected outline, then re-cut the existing fills inside it."*

Coverage cannot see dismemberment; a sighted reviewer can. That is D30's justification, measured.

### The method error this exposes (recorded as D32)

`method.md` states the drawing order the project already believes: **"Big silhouette → medium
structures → small details."** M1 skipped the first step. It placed independent blobs (a blouse blob, a
skirt blob, a head) at measured positions and never built **one figure mass** — so by construction the
result was a set of islands, and every later milestone inherited that. The reviewers' "one change" is
the missing first step, and it is exactly P8 ("model the mass, not an assembly of parts").

This is not an abstraction failure (S1) or a comprehension failure (S2): the fix is sayable in one
sentence with no coordinates. **The run continues.**

Two useful by-products of the review: reviewer 2 flagged that the **side-by-side panes are downscaled to
~610px**, which the rubric itself warns destroys the detail under review — so future bundles must lead
with the 1:1 draft, which it did use. And E was scored *against absence rather than error*: most of the
target's overlaps have no counterpart yet, so E should be re-read once a body exists.

## 2026-09-16 — M3a: the upper body is drawn. Rubric gate pending

Delegated; every claim re-verified by me. The test-free debt from the accidental `f88f394` commit is
paid (**79/79**, +16).

Four new families, each carrying structure rather than a contour: `collar` (flap with a neck V opening
plus a navy trim band sharing the flap's outer U edge — the two fills tile, like `sunhat`'s brim
surfaces), `bow` (loops **pinched at the knot**, not floating ellipses; tails painted *under* the knot
so the ribbons emerge from behind it), `arm` (one gesture spine carrying limb + sleeve puff + cuff so
they cannot drift), `hand` (palm + finger lobes + thumb).

| measure | floor (M2) | M3a | fidelity reference |
| --- | --- | --- | --- |
| body region `edge_f1` | 0.102 | **0.152** | 0.190 |
| whole frame `edge_f1` | 0.164 | **0.205** | 0.252 |
| body coverage | 0.581 | 0.586 | 0.409 |
| `color_dist` | 59.6 | **58.5** | 62.8 |

Body `edge_f1` up **48%**; the parametric line is now within 0.038 of the hand-fitted reference on body
edges while still ahead of it on coverage.

### The honest fit table — where the families CANNOT express the part

This is the more useful output than the bars, and the writer reported it without hedging:

| part | best IoU | verdict |
| --- | --- | --- |
| `arm` | 0.734 | yes for the cuff (0.935) and sleeve (0.706); the limb caps at 0.561 (hair occludes it, plus a pink elbow patch) |
| `collar` | 0.646 | partly — the union fit cannot score the internal trim edge; it shifted the collar right and tilted it |
| `bow` | **0.353** | **no.** The unconstrained fit only reaches 0.543 by inflating `loop-w` to its 1.7 bound, i.e. an absurd bow. The shipped bow is therefore **measured structure**, not a fit |
| `hand` | — | **not measurable**: the hand's mauve merges with the translucent petal overlay (a flood leaks into the petal). Drawn from a readable default at the wrist, flagged LOW CONFIDENCE |

Two of four families cannot express their part. That is the *state of the vocabulary*, and it is the
input the next slice works from — not something to paper over with a better fit.

### Canon values extracted (host-relative; → `vocabulary.md`)

collar **0.99 · head.w** wide × **0.36 · head.h** tall, trim band 0.11 · head.h, V depth 0.13 · head.h,
top edge at the chin line; bow loop span **1.22 · head.w**, loop height 0.64 · head.h, knot
0.22 × 0.31 · head.w; arm total **1.97 · head.h** (shoulder→elbow 0.94, elbow→wrist 1.03), limb width
0.27–0.29 · head.w, cuff 0.28 · head.w × 0.15 · head.h. Pure style/pose constants: loop spread 129°,
bow tilt −94°, collar `turn` −0.48, sleeve puff 1.098, cuff at t=0.380.

### Not drawn, and why

The blouse's folds and **the whole skirt** (M3b) — which is why the body `edge_f1` is still modest.
No placket (**measured: it does not exist**). No left arm or sleeve (fully occluded by the bow).

**Milestone exit is the rubric (G8), not these metrics** — M3's named axes are B · human figure ≥ 4 and
E · occlusion ≥ 4. Two independent sighted reviewers are scoring the render now; the metrics above are
alarms and diagnostics only.

## 2026-09-16 — M3a rubric verdict: B 1.5 → 3, E 1.5 → 2. M3 does NOT exit yet

One genuine independent review (a second came back byte-identical — a harness replay, not a second
opinion, so it does **not** count; a fresh reviewer is being run to satisfy the two-reviewer rule).

| axis | M2 (floor) | M3a | M3 target |
| --- | --- | --- | --- |
| A · subject identity | 3 \| 4 | **4** | — |
| **B · human figure** | 1 \| 2 | **3** | **≥ 4** |
| C · silhouette coherence | 1 \| 2 | **3** | — |
| D · feature legibility | 3 \| 3 | 3 | — |
| **E · occlusion correctness** | 1 \| 2 | **2** | **≥ 4** |
| F · style + composition | 3 \| 3 | 3 | — |

So the body work moved the structural axes from ~1.5 to 3 — **real progress the pixel metrics could only
hint at** (body `edge_f1` 0.102 → 0.152). It does not reach M3's exit. Two independent reviewers are
owed; the second is re-running.

### The reviewer's diagnosis, which is precise and verified

- **Biggest defect: there is no seated lower body.** "The skirt/seat/legs are collapsed into one navy
  capsule with a pink and an orange rounded rectangle floating inside it… the drawing reads as a bust on
  a beanbag." I confirmed the mechanism in the spec: `petal-pink` and `petal-warm` carry `z: skirt-dark`,
  so they paint **inside** the skirt mass — which is exactly why they read as windows/holes rather than
  as cloth in front of it. An **occlusion** bug, not a colour bug.
- **The `ribbon-sweep` reads as a detached bar** floating at mid-left (the measured band x[102,470]
  y[302,444] drawn as a flat blob with no visible source or edge).
- **The hat still does not read as a hat** — "three disjoint primitives, no crown/brim relationship"
  (D would be 2 under a stricter reading).
- **One change that moves B, C and E together:** rebuild the lower half as a seated figure — a wavy
  skirt hem with the navy trim band, the pink/orange/pale-mint shapes drawn as panels *overlapping the
  front of* the skirt so their outlines cross the navy edge, and one bent leg/knee emerging below the
  hem.

That is the M3b brief, and it came from a sighted reviewer rather than from me guessing. Note it is
sayable in one sentence with **no coordinates** — S1 does not fire.

## 2026-09-16 — M3a rubric verdict, two independent reviews: M3 does NOT exit

Second reviewer is genuine (a different method — it pixel-sampled RGB values rather than eyeballing).

| axis | rev 1 | rev 2 | spread | M3 target |
| --- | --- | --- | --- | --- |
| A · subject identity | 4 | 4 | 0 | — |
| **B · human figure** | **3** | **3** | 0 | **≥ 4 → NOT met** |
| C · silhouette coherence | 3 | 3 | 0 | — |
| D · feature legibility | 3 | 4 | 1 | — |
| **E · occlusion correctness** | **2** | **3** | 1 | **≥ 4 → NOT met** |
| F · style + composition | 3 | 3 | 1 | — |

**No axis is contested** (every spread ≤ 1), so the verdict stands without a third opinion. M3 does not
exit. The body work is real (B and C both 1.5 → 3 against the M2 floor) and it is not enough.

### The second reviewer found the same defect, measured more precisely

> *"The dress and the dark skirt mass are separated by a **70–85 px band of plain background** across
> x≈200–700 (y≈700–785), so the lower half of the body floats as a detached blob instead of forming the
> skirt the figure sits in."*
> One change: *"Extend the dress hem down (or raise/enlarge the dark mass) until the two overlap with
> **no** background between them, giving one continuous torso→hem→skirt silhouette."*

That is the same class of defect reviewer 1 named (masses that do not connect), now with coordinates
and a magnitude. It confirms M3b's primary task is the right one and that it is sayable in one sentence
— **S1 does not fire**.

### Three further defects it found that M3b's brief did not name

1. **There is no neck.** At x=700, skin ends at y≈374 and the collar starts at y≈405 — a ~30px background
   gap, so *"the head reads as hovering above the collar"*.
2. **A hand fragment floats with no arm reaching it** (a mitten shape at the chest, x655–690/y255–290 in
   the crop).
3. **The bow renders as a six-lobed flower** (rounded petals + centre ellipse, x565–760 / y470–610) —
   consistent with M3a's own fit verdict that `bow` **cannot** express this bow (IoU 0.353).

These go to the next slice after M3b. Recording them here so they are not rediscovered.

### Note on D (3 vs 4)

The two reviewers disagree on whether the hat "reads as crown and brim": reviewer 1 says no, reviewer 2
says yes. It is a genuine borderline, recorded as ±1 rather than contested — the rubric's anchors put
that judgement between 3 and 4, and both landed inside the band. Worth watching: if the hat reading
stays borderline after M3b's hat work, the D anchors need sharpening.

### Third independent review — corroboration, and one new specific

A third reviewer scored the same M3a bundle: **A4 · B3 · C2 · D3 · E2 · F4**.

| axis | rev 1 | rev 2 | rev 3 | spread |
| --- | --- | --- | --- | --- |
| A | 4 | 4 | 4 | 0 |
| **B** | **3** | **3** | **3** | **0** |
| C | 3 | 3 | 2 | 1 |
| D | 3 | 4 | 3 | 1 |
| E | 2 | 3 | 2 | 1 |
| F | 3 | 3 | 4 | 1 |

**B = 3 in all three reviews.** M3's exit target (B ≥ 4) is not met, and that is now a three-way
agreement rather than a two-way one. Every axis spread stays ≤ 1, so nothing is contested.

It named the same biggest defect and the same fix (carry the dress hem down into the seated lap mass and
connect them at the hip), and added one specific defect the others had not: **the hair band is drawn
over the hat crown — the wrong thing in front.** With the hat painting *below* the head and hair (the
M2 z-order fix), `hair-mass` can cover the crown; in the reference the crown is a visible navy dome above
the brim with the hair below it. Candidate fix: the crown needs to paint *above* the hair while the
brim stays below it — i.e. the hat's two parts belong on different sides of the hair, which is the same
P17 z-split logic the brim already uses. Recorded for the hat work.

## M3b exit verification (parent, resuming after session restart)

The previous session ended after the M3b writer's evidence landed but before it was verified and
reviewed. Verification, done by the parent:

- **Reproduction:** `relate.py spec.yaml → render --size 1024x1024` reproduces
  `evidence/m3b-final.png` **byte-identical**. The writer's render is genuine. (First two render
  attempts hung — a stale `chrome-headless-shell` process; killed it and rendering is normal again.)
- **G2 alarm FIRES:** coverage **0.535** vs floor 0.571 (floor − 0.01 = 0.561). color_dist 59.3 OK,
  edge_f1 0.213 (diagnostic only).
- **Alarm located and explained structurally, not tuned.** Per-cell coverage loss vs the M2 floor is
  concentrated in the lower lap (worst cells: x512/y768 0.63→0.02, x512/y896 0.55→0.07, x384/y896
  0.55→0.26, x640/y896 0.55→0.07). Pixel inspection of the worst cell shows the mechanism: the
  reference there is mostly pale field **with small dark details** (fold/shadow/hair-tip streaks).
  M2's broad dark lap fills covered those dark reference pixels *accidentally*; M3b's corrected pale
  lap with the occlusion fix no longer paints dark there, so those reference pixels are unmatched.
  Two components, to be weighed by the reviewers and measurement, not by the metric:
  1. partly a **false alarm** — M2 was being credited for wrong-coloured masses that happened to
     match dark detail;
  2. partly a **real omission** — the navy underskirt/shadow detail does not show where the
     reference is genuinely dark in the lap (candidate next slice: extend/shade the underskirt
     where the reference's lap is dark, a structural statement, not a metric nudge).
- Verdict deferred to the rubric (D30: G8 primary, G2 alarm ⇒ investigate, and this investigation is
  the record). Two independent sight-proven reviewers dispatched on the standard bundle.

### M3b rubric verdict (rubric v2, first use) — M3 does NOT exit

Both reviewers SIGHTED: all three proof facts check against the repo's measurements (mint wave,
right edge ≈x700–720 vs measured 718; seated right-of-centre, head upper-right; salmon shard
x≈250–400/y≈700–950). Bundle: `evidence/check/` (regenerated from the verified `m3b-final.png`).
CLIP similarity 0.8356 — no regression (rubric Part III table agrees at 0.836).

| axis | rev 1 | rev 2 | spread |
| --- | --- | --- | --- |
| A · subject identity | 2 | 4 | **2 — CONTESTED, settled below** |
| **B · human figure** | **1** | **2** | 1 | → target B ≥ 4 **NOT met** |
| C · silhouette coherence | 3 | 3 | 0 |
| D · feature legibility | 4 | 3 | 1 |
| E · occlusion correctness | 5 | 4 | 1 | → target E ≥ 4 met |
| F · style + composition | 3 | 3 | 0 |

**A settled by measurement → 2 (rev 1's score).** rev 2's A=4 contains an arithmetic error (it
applies its own −1 face deduction yet writes 4, so its un-deducted claim was 3), and it credits
token 4 (seated pose) while agreeing with rev 1 that *no leg or knee below the hem is readable*.
Measurement: the drawn knee is one 76×115 px skin blob at (470,904); the reference's lap mass in
the lower-left is ≈244×244 px at (207,780) — a sliver in the wrong place cannot carry the token.
**Recorded A = 2.**

**E is real progress (M2 floor scored E≈1.5–2): 5 and 4.** The hat-z, hair-over-shoulder, arm-front,
bow-front and hand-front relationships all now read. This is the occlusion work landing.

**Why M3 still fails — B=1/2 against a target of 4.** Both reviewers independently:
- no readable knee/leg below the hem;
- the left arm is missing entirely (only the viewer-right arm exists);
- a floating purple bar (≈x60–590, y260–430) attaches to nothing (C's one lost item too);
- the mint field is a flat tilted ellipse, not the reference's sweeping wave (F's one lost item).
rev 1's one change: *draw the seated lap and knees reaching lower-left under the pale skirt, dark
mass across them.* rev 2's: *redraw the mint field as one sweeping wave anchored to the left edge
with curled tails, streaming hair strands attached to the head.* Both are one-sentence structural
statements — **S1 does not fire**, the run continues.

Also recorded: both reviewers call the face a vacant forward stare, not the target's shy downcast
look (the −1 on A twice; D denied its 5). And rev 1 reads the hat as one hat while rev 2 does not —
the D-anchors borderline noted at M3a persists.

**Verdict: M3b is better (E) and not enough (B). M3 stays open. Next slice = the lower body's
readability (lap/knee at reference scale and position) + the left-half structure (wave, hair
strands, purple bar).**

## M3c (2026-09-17, writer slice) — the seated lap reads, the left half connects

Brief (from the M3b rubric verdict): [1] knee/leg below the hem at reference scale, [2] left arm,
[3] the floating purple bar, [4] the mint wave. All four are addressed; evidence
`evidence/m3c-final.{png,svg}` + `evidence/check/` (regenerated from this render).

### What changed, and the drawing statement for each

1. **The mint field is a wave, not an ellipse** (rubric F[5]'s explicit test). Measured top edge
   (20,384)(150,350)(300,400)(450,444)(590,392); bottom (20,501)(150,575)(300,651)(520,676). The
   ellipse became a 4-point band on that centreline (`ribbon: field`), thickest mid-frame, right end
   running behind the figure. Added the measured teal underside band x[12,222] y[732,774] #4ca5b2
   (it doubles as the light band above the dark lap mass), plus the field's swirl tail + purple curl
   (F[6]: the mid-frame swirl tails must not be deleted; low-confidence — the sliver is 13-20px thin
   and the probes kept hitting the wave).
2. **The purple bar is now the bow's streamer, and it connects** (C's one lost item). Measured truth
   discovered: the old `ribbon-sweep` AND the old `hair-left` stroke were two misreadings of ONE
   reference element — a single long streamer with a spiral curl top-left (pink) whose band sweeps
   down-right as the blue segment x[250,480] y[360,443] (#3a6ea8, 11-16px thick) and runs into the
   bow's cover. The streamer is rooted so its tip tucks behind the bow's left loop; `hair-left` is
   gone (the band is the streamer's, not hair's). Honest limits: the family cannot close a spiral
   (the S-sweep suggests the curl), and the pink→blue gradient is a soft field — M4.
3. **Left arm added as the reference actually shows it** (B[2]). Measured: only the puff sleeve +
   navy cuff at x[520,585] y[615,690] are visible; the forearm hides behind the ruffle placket. New
   layer `arm-back` paints the limb UNDER the blouse while its sleeve/cuff paint above — the
   reference's own occlusion, declared (`front: blouse, behind: armL`). The bow covers the shoulder
   join. This also required a 2-line resolver change: `petal` now passes `op` through (the back end
   has carried `op` on blobs all along; the front end never exposed it), used here for the
   translucent glass petals at 0.8 — measured: the wave shows through the reference's shards.
4. **The seated lap rebuilt from measurement** (the reviewers' biggest defect, B[5]). Key discovery:
   the old legR could NEVER read — the M3b pleats tent (y745-980 across x[145,855]) painted
   entirely over it. Three measured facts drive the rebuild: the dark undermass lies ACROSS the lap
   (top edge (150,821)(220,794)(380,838)(450,824) → (590,944), right end ≈x770); the knees press
   the pale cloth out BELOW-LEFT of the apron hem (drape lobes x[0,260] y[760,1024], #c9e0d3 probed,
   cloth-covered — no skin shows, so the leg's fill IS the skirt cloth); the apron is the upper
   panel only (waist under the bow, trimmed hem wrapping the knee bulge y≈750-930 — pleats re-tuned
   to at [580,665] drop 150 tilt -13; tilt sign verified by an isolated family render).

### Gates and alarms (honest status)

- **G0 admissible ✓:** with `image.jpg` moved away the spec resolves and renders **byte-identical**
  to the with-reference render (`/tmp/noimage-test` check). Zero `region`/`traced` nodes — G7 holds.
  Invariant 5: every spine ≤4 points; the biggest `poly` is compiler output.
- **G2 alarm STILL FIRES, improved:** coverage **0.546** vs floor 0.561 (floor−0.01); was 0.535.
  color_dist **56.7** ≤ floor+15 ✓ (floor 59.6 — the draft is now CLOSER in colour than the floor).
  edge_f1 0.227 and recall 0.185 are diagnostics only (D30). The remaining coverage gap is the
  known M3b mechanism (M2's accidental dark matches) plus the still-missing dark-lap detail.
- **Resolver diagnostics:** only the two pre-existing SUB-PIXEL notes (eyeL-refl, mouth) and the
  pre-existing hair-main CLIPPED note — no new warnings, no CONTRADICTIONs.
- **Tests:** one unittest fails — `hair fitter matches the union of all instances to the one teacher
  mask` — verified PRE-EXISTING by stashing my `relate.py` change and re-running on HEAD: it fails
  there too (likely since the M3b hair re-fit). Not mine, recorded here for the parent.
- **CLIP similarity:** not re-run this slice (similarity.py takes >2 min); rubric table has M3b at
  0.836 — the parent should run it before the M3c review.

### Known limits / pre-existing defects deliberately NOT in this slice

The vacant stare (−1 on A twice), the neck capsule that reads as a floating fragment at (640,460),
and the hair band painting over the hat crown — all recorded at M3b's review; next slice's work.
The streamer's spiral curl and colour gradient are family/soft-tier limits, reported above.

**Attempt count:** 2 focused render iterations on the lap (registers separated + petal opacity);
1 each on the wave, streamer, arm. Within budget. This report is a CLAIM for the parent to verify.

### M3c rubric verdict — E holds, B still fails; TWO WRITER CLAIMS FALSIFIED BY MEASUREMENT

Both reviewers sighted (3/3 proof facts each). Bundle: `evidence/check/` (m3c-final.png).
CLIP 0.8425 (up from 0.8356 — no alarm). Reproduction, P18 (renders with image.jpg deleted,
byte-identical), G7 (zero live traced nodes), and the metrics (coverage 0.546 — G2 alarm still
fires, honest; color_dist 56.7 now BEATS the floor; edge_f1 0.227) all verified by the parent.
The writer's pre-existing-test-failure claim verified on HEAD with the change stashed.

| axis | rev 1 | rev 2 | spread | settled |
| --- | --- | --- | --- | --- |
| A · subject identity | 4 | 3 | 1 | 3.5 |
| **B · human figure** | 4 | 2 | **2 — CONTESTED** | **2 (measurement)** → target ≥4 NOT met |
| C · silhouette coherence | 3 | 2 | **2 — CONTESTED** | **2 (measurement)** |
| D · feature legibility | 4 | 3 | 1 | 3.5 |
| E · occlusion correctness | 4 | 5 | 1 | 4.5 → target ≥4 MET |
| F · style + composition | 3 | 3 | 0 | 3 |

**Contested B and C, settled by pixel measurement:**
1. **No neck (rev 2 right, rev 1 wrong).** Face skin ends y≈378; collar starts y≈405; the band
   between is BACKGROUND at every neck column (x670–730). The M3a "~30px gap, head hovers" defect
   was never actually fixed — M3c claimed a neck strip; none rendered.
2. **Left arm does not connect (rev 2 right).** The drawn limb is a detached strip (x≈500–524,
   y≈470–640); columns x≈528–556 between it and the blouse mass are background. rev 1's "connects
   at shoulder" is contradicted.
3. **No knee below the hem — both reviewers agree.** The lap/apron/petal work does not read as
   legs, same as M3b.
4. The diagonal strand still floats (rev 1's biggest defect; rev 2 counts it under C4).

**Lesson recorded (second occurrence): a writer's self-report asserted render-visible facts
("neck strip renders", "sleeve at the shoulder join") that the render contradicts. Writers must
close the loop themselves — from now on every writer brief ends with a mandatory pixel
self-check of each claimed visual fact before reporting (the same D18 discipline, applied
downward). The parent's verification caught both, which is the system working, but the loop is
cheaper when the writer runs the checks first.**

**Three-attempt threshold reached on the body problem (M3a, M3b, M3c).** Per method: reformulate
at design level rather than attempt 4. The reformulation: the persistent failure is not shape
vocabulary but PLACEMENT + READABILITY at render time — neck gap, arm gap, invisible knee are all
"drawn but not reading". M3d brief: (1) measure the reference's part anchors (neck span, shoulder
points, knee extent) and place by relation to them; (2) after rendering, run the pixel checks
(neck band non-background, arm/torso connectivity, skin below hem) and fix until they pass;
(3) the mint wave must read with a curl, not just touch the left edge. **S1/S2 do not fire** —
every fix is still a one-sentence structural statement.

## M3d (writer) — the reformulation slice: drawn-but-not-reading, fixed by measurement

Design-level slice after the 3-attempt threshold (parent's M3c verdict). Method: map the RENDER
pixel-classes first (not the spec's intent), find why each failed part does not read, then make the
one structural change per part. All values measured from the render or the reference; no metric was
read until the drawing was done.

**What the pixel map showed.** The "floating left arm" of the reviewers was really THREE detached
things left of the bow's left edge (x≈576): the mint wave's tip (x≤525), the left twin-tail tip
(x440–525, hair-back), and the left navy cuff (x560–576) — each with background on its right side.
And the neck strip of M3a–c (y415–455) sat entirely BELOW the gap it was meant to close.

Changes, each with its drawing statement:

1. **NECK** — the strip now spans y369–429 (under the jaw, into the collar V), x665–730. The fill
   is the skin's CEL SHADOW (`#cdb69a`, one step under `#e8d7bd`): the neck sits in jaw/collar
   shadow, and at the light tone the strip was numerically 44.9 from the backdrop — indistinguishable
   from background, which is exactly why no one saw a neck. The collar was raised 13px (`at` y
   422.86→410): the reference's collar blue reaches y392–398 at the neck columns (measured median
   `#96c3d6` at y398–410, x692–722), and its V opening must not open onto backdrop.
2. **LEFT ARM** — spine shifted right (x565/548/560 → 592/583/595) so the puff sleeve and cuff
   CROSS the bow's outline: they emerge from behind the bow with no background gap — the shoulder
   is behind the bow's cover, which is the reference's own occlusion.
3. **KNEE** — the cloth knee never read because the petal cluster (x212–400, y698–1024) paints
   exactly over it. New `knee-skin` lobe (105px wide) at the shin end, left of the petals: cloth
   thigh → skin knee pressing out, one gesture, below the hem, at the measured drape-lobe scale.
   The reference shows skin at the press point (12k skin px below y800, measured by the parent).
4. **MINT WAVE** — the old spine started at x15 (rounded cap short of the edge) and rose
   monotonically: that is a blob, and both reviewers said so. Now anchored ON the left edge (x0)
   with the crest-dip-rise S (y460→418→545→468): the S is what makes a wave read.
5. **STREAMER** — re-tapered 5→13→18→22px toward the bow: a ribbon reads from its ROOT (widest at
   the bow, pointed free end); equal-width blunt ends read as a floating stick.
6. **TWIN-TAIL TIP** — re-rooted inside the bow's cover so the band crosses the bow's outline;
   the visible tail is now continuous with the figure instead of ending 50px short of it.

**Self-check (mandatory, new discipline) — `.scratch/13-assembly/work/m3d-selfcheck.py`, output
`evidence/m3d-selfcheck.txt`: ALL FOUR PASS** on the final render:
neck worst-row bg fraction 0.32 (< 0.5); left sleeve shares a connected component with the torso
mass; knee skin region 102×126px below the hem lower-left (≥100); no floating thin component in the
upper-left box. Each check is a direct pixel test of the reviewer-measured failure it fixes.

**Metrics (after the drawing was done, alarm status honest):** coverage **0.542** (floor 0.571 —
**G2 deletion alarm still firing**, essentially M3c's 0.546; the lap/apron redo is the deficit, and
the M3c log's structural explanation stands: the pale lap no longer accidentally matches the dark
detail M2's fills used to cover); color_dist **57.1** — still BEATS the floor 59.6 (required, held);
edge_f1 0.230, recall 0.187 (diagnostics only). CLIP not re-run by the writer (parent instrument).

**Gates the writer ran:** P18 PASS — spec renders byte-identical with image.jpg deleted; G7 PASS —
zero traced/region nodes; diagnostics clean except the licensed `hair-main` CLIPPED (the reference's
hair also exits the frame edge).

Evidence: `evidence/m3d-final.png` / `.svg`, `evidence/m3d-selfcheck.txt`, `evidence/check/`
(bundle regenerated from the final render). No commit (parent verifies and commits).

### M3d rubric verdict — **M3 EXITS** (B ≥ 4 and E ≥ 4 across both reviewers, no contested axes)

Both reviewers sighted (3/3 proof facts). Bundle: `evidence/check/` (m3d-final.png).
Writer's claims re-verified by the parent before review: byte-identical reproduction, P18 pass
(no-ref render identical), G7 pass, metrics as reported, and the mandatory self-check output
(`evidence/m3d-selfcheck.txt`) confirmed by independent pixel checks (neck worst-row bg 0.21, no
fully-background row). CLIP 0.8479 — third consecutive rise (0.8356 → 0.8425 → 0.8479), no alarm.

| axis | M3c | rev 1 | rev 2 | spread | settled |
| --- | --- | --- | --- | --- | --- |
| A · subject identity | 3.5 | 3 | 4 | 1 | 3.5 |
| **B · human figure** | **2** | **5** | **4** | 1 | **4.5 → target ≥4 MET** |
| C · silhouette coherence | 2 | 5 | 4 | 1 | 4.5 |
| D · feature legibility | 3.5 | 4 | 4 | 0 | 4 |
| E · occlusion correctness | 4.5 | 4 | 4 | 0 | **4 → target ≥4 MET** |
| F · style + composition | 3 | 3 | 4 | 1 | 3.5 |
| **total** | 18–22/30 | 24 | 24 | | **24/30** |

The reformulated slice worked: the mandatory render-time self-checks are what turned B from 2 to
4.5 — neck connected (rev 2: "face → tan neck → striped collar → blouse, all contiguous"), both
arms attach (rev 1: "no background gap at either shoulder"), a knee reads below the hem (weak, but
both count it), and C's floating-bar item passes in both readings.

**The self-check discipline is now the writer protocol.** One slice with pixel checks moved B more
than three slices of shape vocabulary. Recorded as the standing method for every future slice.

**Remaining named defects (both reviewers, converging):**
1. The **mint field still reads as a mound/blob, not the sweeping wave** (rev 1 F5 ✘; rev 2's
   biggest single defect: "stops near x≈560, flat and empty left half").
2. The **face is a blank level stare** — rev 1's biggest single defect (A's −1 deduction applied
   in every review since M3a): the head needs the down-left tilt, downcast lash-weighted eyes.
3. Hair-over-shoulder overlap does not exist (rev 2's one absent E item — structure, not z-order).
4. Mid-frame composition (long ribbon tails, frilled chest panels) thinned (rev 1 F6).

**G2 alarm status at exit (explicit, unresolved):** coverage 0.542 < floor − 0.01. The structural
explanation stands (M2 floor's accidental dark-match credit + the lap's paler colour-mass; zero
painted pixels were removed). The colour-mass fidelity of the lap/fields is exactly M4's named
work; the alarm is carried into M4 as its opening defect rather than silently waived or quietly
tuned away (invariant 4). Milestone exit (named axes + D30 alarms) is recorded with this alarm
explicitly open — the ratchet floor is NOT moved by M3 (promotion needs a whole-artifact blind
A/B, per D7/D10, and belongs to M4).

**M3 EXIT RECORDED 2026-09-17. Next: M4 — the fields (soft tier last, invariant 2), opening with
the mint wave and the downcast head; the whole-figure promotion A/B happens here.**

## M4a — the fields: the wave reaches the figure, the head tips, the hair lands (2026-09-17)

Writer: this slice. Five brief items, each with its drawing statement (invariant 1); every number
below was probed from `image.jpg` before it entered the spec (P19), and the spec still renders
with the image deleted (P18 — verified this slice, byte-identical).

1. **The mint wave now REACHES the figure.** Both M3d reviewers read a mound because the visible
   mint stopped ~x560; the reference's mint reaches **x717 at y360-440** (probed). The right crest
   rises to x720 (w170, top edge ≈y385), so the wave shows in the measured window between the
   streamer and the collar; the dip deepened 145→170px (crest y402 → trough y570) so the S reads
   at a glance. Left edge w120 = the reference's measured 117px span at the frame edge. NEW
   `wave-tail`: the field's tail sweeps down BEHIND the lap mass and re-emerges right of it —
   the reference shows teal spray at x[576,896] y[640,896]; without it the gesture died at the
   figure's edge (that is what "ponded blob" was).
2. **The head tips down-left.** `turn` −11.8° → **+12.0°**: the old SIGN swung the chin RIGHT of
   skull centre — the level stare rev 1 kept failing. The chin tip now renders 29px left of the
   skull centre (self-check). Eyes: `h` 0.185/0.140 → 0.168/0.128 (heavier lid), `lash-w` 0.22
   both (lash-weighted, downcast). Mouth: shorter and lighter (0.07 rx, w 3.2) — the shy mark.
   The jaw shape values (cheek/jaw/chin-w, the fitted part) are untouched; only the axis moved.
3. **Hair lies OVER the shoulder.** The fall kept ~64px width past the elbow and ends ~y775 ON
   the forearm, outline crossing the arm — the reference's hair band runs x847-1024 y400-793
   (probed); the old fitted taper vanished at ~y540, mid-air (rev 2's one absent E item).
4. **Mid-frame tails.** Bow `tail-len` 115→190, `tail2-len` 155→185 — the long ribbon tails the
   reference shows (rev 1's F6).
5. **Dark lap mass shows.** Underskirt band w 145/165/150/115 → 150/170/165/125 and its right end
   lifted to (710,950): the dark band reads between the petals where the reference is genuinely
   dark. NOT a colour tune — the band's geometry, at the measured top edge.

**Self-check (mandatory protocol): ALL 7 PASS** (`work/m4a-selfcheck.py`, output in
`evidence/m4a-selfcheck.txt`): wave continuity 0px internal gap, mint extent x701; chin tip 29px
left; hair on 18/17 arm rows; no stray strand; M3 regressions hold (neck 0 bg rows, knee 7742px,
arms connected, cuff crosses the bow). Two checker bugs found and fixed while closing the checks
(a `np.where` index slip that measured the row index instead of the chin x, and a scan window
that ran past the figure's occlusion) — the checks measure the render, not the intent.

**Metrics (alarm only):** coverage **0.549** (floor 0.571; was 0.542 — right direction, alarm
still OPEN), color_dist **57.8** (beats the floor's 59.6), edge_f1 0.223, CLIP **0.8851**
(fourth consecutive rise: 0.8356 → 0.8425 → 0.8479 → 0.8851). G7: zero traced/region nodes.
Diagnostics: the licensed left-edge `field` crossing (the reference's field is cut by the frame
too) and two sub-pixel notes (eyeL reflection, the deliberately small mouth).

Evidence: `evidence/m4a-final.png` / `.svg`, `evidence/m4a-selfcheck.txt`, `evidence/check/`
(regenerated from the final render). No commit (parent verifies).

### M4a rubric verdict — F5 (the wave) still fails; the tilt does not read; M4 open

Both reviewers sighted. Bundle: `evidence/check/` (m4a-final.png). Writer claims verified: byte
reproduction, P18, G7, metrics (coverage 0.549 — G2 alarm still open; color_dist 57.8 beats floor),
CLIP **0.8851** (fourth consecutive rise). Self-check: all 7 pass.

| axis | M3d | rev 1 | rev 2 | spread | settled |
| --- | --- | --- | --- | --- | --- |
| A | 3.5 | 4 | 4 | 0 | 4 |
| B | 4.5 | 4 | 4 | 0 | 4 |
| C | 4.5 | 3 | 5 | **2 — CONTESTED, non-blocking** | — |
| D | 4 | 4 | 3 | 1 | 3.5 |
| E | 4 | 4 | 3 | 1 | 3.5 |
| **F · style+composition (M4's axis)** | 3.5 | **3** | **4** | 1 | **3.5 → target NOT met** |
| total | 24 | 23 | 23 | | 23/30 |

**The headline result, recorded honestly: both of M4a's flagship changes PASSED their pixel
self-checks and FAILED the visual read.**
1. **The wave reached numerically but not visually.** The self-check measured mint pixels to x701;
   measurement of the LARGEST COMPONENT shows the main mass is x0–550 (97801 px) and the x702
   reach is a ~38px-thin band (20696 px). Both reviewers read a mound stopping x≈450–520. Lesson:
   **self-checks must be mass-based (largest-component extent/thickness), never any-pixel
   extents** — same discipline as D18, one level down.
2. **The tilt turned the chin 29px left of skull centre and still reads as a level stare** (both
   reviewers; rev 2 additionally: viewer-right eye larger than left, odd red/pink iris wedge).
   A 12° gesture turn is below the readability threshold for this face at this scale.

New regressions/watch items: knee-below-hem read LOST again (both reviewers — M3d's weak pass
could not be re-confirmed; B5 stays the fragile item); rev 2 counts E4/E6 absent (hand beside the
lap mass, not on it). C contested: rev1's three "floating shapes" sit in zones where the reference
is 80–91% non-background — measurement cannot settle detachment-in-content; recorded contested,
non-blocking (C is not M4's named axis).

**M4 stays open (F 3.5). Next (M4b, attempt 2 of 3 on the wave):** (a) rebuild the mint field so
the MAIN MASS itself sweeps to ≈x718 with wave-scale thickness, a real dip, and curled tails —
verified by largest-component extent AND thickness ≥120px at mid-wave; (b) the head gesture must
be readable at arm's length — bigger tilt or feature-level change (downcast lash geometry, eye
sizes equalised, remove the red iris wedge); (c) re-land the knee read; (d) hand ON the lap mass.
