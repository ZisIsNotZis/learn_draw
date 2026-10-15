# Ribbon drawing rule — experimental card (readability hypotheses not accepted)

## Question and boundary

**Observed outcome:** corrected full-frame blind comparison found that complete perimeter ink
crowds crossing/twist regions and the side-consistent motif does not clarify front order. Neither
candidate is accepted as the S1a readability solution. Keep these commands as reproducible failed-
hypothesis controls, not a recommended finished drawing method. See `../outcome.md`.

This slice compares the unchanged continuous ribbon artwork under three frozen treatments: **control** (existing two-sided base fill and face-dependent stripe), **rule A** (control plus complete depth-visible semantic perimeter ink), and **rule B** (same ink plus a side-consistent local-UV motif). It is not a general line-art system, finished art, a transfer result, or S2 acceptance.

The existing compact ribbon JSON remains the author interface: choose `length`, `width`, `tip_ratio`, `bend`, `depth`, `twist`, `family`, `origin`, `heading`, and front/back base colours within `ribbon_family.py`'s existing ranges. This drawing layer adds no authored contour, visibility interval, crossing location, or camera-specific cut. Camera yaw/pitch selects a view. `--sampling 128` is a **compiler override**: it replaces only the sampled interval count during compilation; it does not edit the input spec or change its shape parameters.

Each panel fits the projected bounds of all support vertices and, when present, all four external card corners into a 16-pixel inset with one uniform scale. If projected bounds are `min_x..max_x`, `min_y..max_y`, the scale is the smaller available-width/width-span and available-height/height-span ratio. The canvas offsets are `ox=(W-scale*(min_x+max_x))/2` and `oy=(H+scale*(min_y+max_y))/2` (SVG y points downward). The artwork and included card therefore share a centered fixed framing.

## Why and where ink is drawn

The compiler makes candidates from the four actual local-domain boundaries only: `v=-1`, `v=+1`, `u=0`, and `u=1`. There are `2N+2` candidates for `N` longitudinal intervals. Triangle diagonals and other internal mesh edges have no line identity.

Each candidate is projected and split at actual projected support-edge intersections, depth-equality roots, and the resolver's tie threshold. Its owning support triangle is its provenance; every other ribbon triangle and each external support-card triangle participates in visibility. No neighboring-cell range is discarded. A candidate interval hidden by a closer opaque surface is omitted. The existing first-declared opaque tie bias (`1e-5`, with `EPS=1e-7`) is retained.

A visible contour with no farther nonadjacent surface beneath it receives restrained **silhouette ink** (1.2 canvas pixels). A visible foreground boundary that covers a farther nonadjacent ribbon section or external surface receives stronger **overlap ink** (1.8 canvas pixels). These widths are fixed in canvas pixels, not tuned by screen location or `u` interval. The stroke is represented as finite-width screen-space polygons. Their coverage is subtracted against every projected triangle region that is closer than the owning edge's support-triangle depth plane; that plane is explicitly extended across the small artistic stroke footprint. This clips stroke width at self- and external-occluder edges without expanding physical geometry. Hidden gaps receive no bridge caps.

## Rule B: local motif

Rule B retains the ribbon's original front/back base palette and replaces the old face-dependent stripe with the same full-local-UV motif on either material side:

- light core: `v ∈ [-0.08, +0.08]`, fill `#fff1b8`;
- dark local borders: `v ∈ [-0.16, -0.08]` and `v ∈ [+0.08, +0.16]`, fill `#472639`.

`v` is dimensionless over the existing ribbon domain `[-1,1]`; these widths are proportions of the full ribbon width. The bands are clipped inside each unchanged support triangle using its `(u,v)` provenance and inherit the existing depth-visible fill pipeline. Their fill does not switch at a front/back colour-side transition, so the motif identity itself is side-consistent. Palette contrast beyond the listed frozen cases is not certified.

## Commands

Single compact-spec render, deterministic SVG and (unless `--svg-only`) Chromium PNG:

```bash
.venv/bin/python scripts/ribbon_drawing.py render \
  .scratch/19-ribbon-family/work/teaching-example.json \
  --rule B --name front --yaw 0 --pitch 0 --sampling 128 \
  --out .scratch/20-ribbon-drawing-rule/evidence/teaching-B.svg
```

Build the frozen comparison set with the exercise-specific checkpointed exporter. It compiles each of the 24 case/rule panels once, saves the panel SVG and coverage metadata immediately, records progress per pane, and then assembles the same cached content into labelled/unlabelled colour and line-only boards:

```bash
.venv/bin/python .scratch/20-ribbon-drawing-rule/work/build_cached.py \
  --case-plan .scratch/20-ribbon-drawing-rule/work/cases.json \
  --out-dir .scratch/20-ribbon-drawing-rule/evidence \
  --progress .scratch/20-ribbon-drawing-rule/work/build-progress.jsonl
```

The first monolithic board compilation exceeded 120 seconds. The checkpointed exporter completed all 24 panels in one bounded run, verified cached line-only paths against direct line-only rendering with the external support card, and assembled the four full 8-row boards without recomputing panels. See `log.md` for actual durations, hashes, draw-check image lists, and renderer limits.

## Tested scope and limits

The frozen comparison plan references the original teaching arch, crossback, half-twist, external-card case, and unchanged failed learner spec. The depth-reversed crossback is explicitly a derived test with only the sign of original `depth` reversed. Both frozen cameras are front `(yaw=0°, pitch=0°)` and oblique `(yaw=38°, pitch=22°)`. Cases and source files are SHA-256 identified in `work/cases.json`; no reference image is read at runtime.

The new focused tests exercise perimeter provenance, depth reversal, full-UV motif clipping on both sides, unique deterministic SVG IDs, and finite-width card clipping with an unmasked-overpaint negative control. Those tests do not establish that a viewer recognizes a turning sheet. This remains a small opaque-triangle experiment: exact ties retain declaration order; unusual degeneracies, complex transparent/intersecting objects, and line-art style outside the tested ribbon cases are not established. The old learner output is regression context only, never an unaided transfer pass.

## Learner-facing use deferred

No new transfer attempt is authorized on these unaccepted candidates. If a later method actually
passes the parent-owned perception gate, give a fresh learner its updated card, the existing compact ribbon schema, and a **new held-out task** selected by the parent. Ask it for a compact JSON spec and a selected camera, then render with the same `--sampling 128` and rule B. Do not repair the saved failed learner answer and relabel it as transfer. Parent owns all perception review and any future transfer attempt.
