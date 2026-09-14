# Drawing principles — transferable lessons

Append-only. One lesson per entry: the principle, where it was learned, and the observation that taught it.

These are the bridge to drawing without a reference — with one distinction that everything after P17
turns on: a *principle* is knowledge the model carries, so it survives the reference being closed; a
*tool* that needs the target does not. P18 is the test that separates them. Rules distilled from these
entries live as numbered invariants in `AGENTS.md`; this file is why those rules exist.

## P1 — Occlusion is drawn, not implied (T1, warmup-duck)

Overlapping shapes must be drawn with explicit occlusion: arcs interrupted where covered (head arc broken at beak), path ends tucked behind the covering shape (body ends inside head circle), background strokes split into segments (waterline behind duck). A line drawn "through" a shape in front of it is always wrong.
Learned: v1/v2 — dark waterline crossed the hull; head outline crossed the beak.

## P2 — Not every visual edge is a stroke (T1/T2, warmup-duck)

Distinguish *outlines* (drawn strokes) from *fill boundaries* (color changes only): waterline = thin darker stroke on top of a fill boundary; blush, belly shade, water shadow = pure color regions, no outline. Before drawing any line ask: "is this an outline, or a boundary between two fills?"
Learned: v1 drew blush/belly outlines; v3 drew grey waterline stroke where ref has fill boundary + subtle edge stroke.

## P3 — Compute geometry, never eyeball it (T1, warmup-duck)

Eyeballed arc endpoints let the SVG arc solver invent a different circle center (head came out squashed). Measure circles with `measure --hough`, compute arc endpoints from the measured center, verify color values with `measure --point`. The tool is a ruler — semantics stay mine.
Learned: v2 head-arc bug; v3 measured (385,299,r112) fixed it in one step.

## P4 — Junctions and negative spaces carry the character (T1, warmup-duck)

The sky gap under the lifted tail petal, the thin notch between head and body, the open mouth showing sky — these small negative spaces are what make it read as "rubber duck" rather than a generic yellow blob. Zoom-compare crops (`compare --region ... --zoom`) on junctions reveal semantic truth invisible at full scale.
Learned: beak/tail crops in warmup-duck; critic independently flagged head-body merge as its #1 finding.

## P5 — Scan shading before assuming it (T2, warmup-duck)

My mental model of the belly shading was inverted: the darker band sits mid-body with a *bright rim below it* (water reflection), not darker at the bottom. `measure --scan col:x:y0:y1` along a few rows/columns through a region reveals true shading structure cheaply.
Learned: pixel scans at x=350/380/420/560 in warmup-duck.

## P6 — When metric and eye disagree, trust semantics (warmup-duck)

Edge-F1 preferred the semantically wrong dark waterline (strong canny edge) over the correct light one. Metrics are signal for progress tracking only; when they diverge from visual/semantic judgment, write down why and move on.
Learned: v2→v3 metric drop despite clear visual improvement.

## P7 — Fresh-eyes critic: trust silhouette reads, discount impossible spatial claims (warmup-duck)

A no-context reviewer catches character-level truths my staring misses ("chubby chick, not classic rubber duck"). But it can also make spatial claims that are geometrically impossible ("larger and shifted right" at identical canvas scale) — verify every critic claim against measurements before acting.
Learned: warmup-duck close-out review; 3 of ~9 findings actionable, rest perceptual/minor.

## P8 — Model silhouettes, not assemblies of parts (T2, portrait-face)

A hair mass with strand tips is ONE silhouette whose bottom edge zigzags (tips down, notches up); the "pockets" of shadow between strands are the underlying skin showing through notches — not shapes to draw separately. v2 drew base+strands+pockets as separate outlined shapes and produced boxy artifacts; v3's single zigzag path fixed it in one step.
Learned: portrait-face v2→v3.

## P9 — Trace boundaries, don't guess coordinates (T1/T2, portrait-face)

For complex regions, scanline-trace the actual boundary from the reference (color-classify pixels per column/row, find edge points) and build the path from measured points; verify ambiguous areas with a coarse color-class grid map. Eyeball estimates were off by 20-60px repeatedly (right mass edge x375-390 not 350; left mass ends y270 not 330; hat is a large triangle).
Learned: portrait-face boundary tracer; three structural errors caught before v3.

## P10 — Line refs fail on layered interiors; zoom + observe (T1, portrait-face)

XDoG line extraction turns anime eyes into noise — unusable. Interior-layered structures (eyes: sclera→lid-band→iris→glints→outline) must be read from direct zoomed observation (`measure --point` grid + 3.5x crops), not derived from line refs. Line refs stay useful for coarse outer boundaries.
Learned: portrait-face eye study.

## P11 — Shared edges: fill-only + separate edge stroke (T2, portrait-face)

Two adjacent filled shapes both carrying their outline stroke produce a double-line seam through solid fill (hair-top vs right mass at x352). Give one side fill-only, then draw the visible edge as its own stroke path — only where a real boundary exists.
Learned: portrait-face v4 seam fix.

## P12 — Feature marks are tiny but positional (T1, portrait-face)

A nose can be a 5px vertical tick and a mouth a 15px horizontal dash — swappable without a zoom crop. Locate small marks programmatically (dark-component scan within a region) before assigning identity; verify with a zoom.
Learned: portrait-face nose/mouth were initially swapped until 4.5x crop.

## P13 — Outlines are free: stroke the shape you already own (user insight, portrait-face)

When REF shows an outline the draft lacks, first ask "do I already have this shape, unstroked?" Face/neck/collar outlines were missing not because shapes were missing but because I never stroked them. 描边 = reusing the existing path with a stroke — measure only the stroke color/width (near-black #101018, ~5px here).
Learned: portrait-face v8/v9.

## P14 — Draw the object, not the pixels (user insight, 05-portrait-scene reframe)

The goal is a proper drawing in a similar style, not pixel/edge correspondence with one reference photo. Holistic semantic shapes (a whole ribbon, a whole hair mass with parameterized strands) beat fragmented point-matching patches; being a *coherent artwork* outranks being *close* to the reference. Overlay-based zone-distance compare is a calibration aid, never the objective; judge by looking at the drawing as a whole. Learned: user reframe after scene-format migration — "you don't need to match its location... it should be a proper drawing first, not necessarily as close as possible."

## P15 — Physics-ish generation over hand-drawn geometry (user insight, scene-format design)

Regular, structured things (ribbons, curtains, hair strands, water ripples) should be GENERATED from few parameters (a spine, gravity direction, wave length, taper) rather than hand-placed point-by-point. Hand coordinates only for genuinely irregular anchors. This is what makes the drawing read as "drawn as the whole thing" instead of assembled fragments. Learned: user proposing gravity/wave ribbon generation in the scene-format discussion.

## P16 — Component plates: align before trusting (REBUILD v2, 05-portrait-scene)

User-supplied component plates (crops of the ref or redrawn versions) must be template-matched against the reference before being used as geometry sources — a plate's alignment tells you whether it is a position-true trace (usable for placement) or a redraw (usable for style/shape only). Matching = masked TM_SQDIFF over a scale scan; scale 2.0 on a 2048→1024 plate means 1:1. Redrawn plates match nothing and must not be force-fit.
Learned: dress.png/cloth.png are redraws (style refs); hat/ribbon/head_hat are position-true.

## P17 — z-plane split for wrap-around elements (user spec, REBUILD v2 #6/#3/#5)

Elements that wrap AROUND the figure (ribbon circling the body, hair behind vs in front, hands tucked behind) are modeled as ONE continuous shape split by z-plane, never pre-split paths: two node instances sharing geometry (+seed), complementary arc/angle ranges, different `z`. For the ring generator the zigzag phase is purely angular, so complementary arcs re-join seamlessly. Occlusion stays the renderer's job (scene-format rule).
Learned: ribbon ring back/front halves; green hair mass moved from front overlay to hair-behind layer.

## P18 — The engine must not need the target (user constraint, 06-relational-geometry)

A reference image is a *teacher*, never the engine. Tracing can seed values for a drawing spec,
but if the solver needs the target to produce geometry, it is worthless for the end goal (drawing
without a reference). So the test for every abstraction is: *does this still work with the image
deleted?* Learned: user, on accepting the computed-geometry reframe.

## P19 — Geometry by computation, semantics by eye (05-portrait-scene diagnosis)

A VLM is strong at naming/grouping/z-order/judging and weak at coordinate regression. Any shape
needing more than ~4 hand-typed coordinates must come from a computed source (trace, region,
generator, or a relation), never from the model's head. The portrait's 824 hand-typed vertices
produced mush; 119 computed contours produced the character in 2.4s.
Learned: `evidence/diagnosis/` comparison.

## P20 — Two orders, kept separate (06-relational-geometry)

*Resolution* order (a node may use any shape declared before it) and *paint* order (`layers` + z)
are different orders and must never be conflated. Separating them is what removed the portrait's
occlusion surgery: a shape is declared where it is convenient to reason about it, and placed in
the stack where it belongs visually.
Learned: `sunhat` needs the head declared first but painted after the hair.

## P21 — The engine reports in words (06-relational-geometry)

A model has no numeric sense of a 1024² canvas, so the resolver must hand back derived facts as
sentences: OFF-CANVAS / CLIPPED / SUB-PIXEL shapes, and CONTRADICTION when a declared
`front/behind` relation disagrees with the layer stack. In the first bust render this caught two
defects (my own wrong layer order, and shoulders clipped 68px past the frame edge) before the
image was ever looked at.
Learned: `relate.py` diagnostics on bust v1.

## P22 — A proof must pass the gates it exists to enforce (06, SA1 re-assessment)

The relational language's proof render was declared readable with "diagnostics clean" — but the
project's own acceptance (`draw check` + fresh-context reviewer, invariant 7) was never run on it.
The render was in fact not readable: the hat's occlusion was inside-out, the face was buried under
hair, and the shoulders were detached — every defect invisible to the four shipped diagnostics.
Diagnostics are a *subset* of the evidence, never a substitute for the gate. Rule: **a mechanism's
own demo runs the same acceptance as real work** — build the check bundle, ask the fresh reviewer,
and only then claim "readable". "Clean" means "no rule fired", which is not "correct".
Learned: SA1 found it; I had written invariant 7 and then skipped it on the one artifact the whole
language rests on.
