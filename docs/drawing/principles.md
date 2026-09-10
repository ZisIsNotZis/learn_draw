# Drawing principles — transferable lessons

Append-only. One lesson per entry: the principle, where it was learned, and the observation that taught it. These are the bridge to drawing without a reference.

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
