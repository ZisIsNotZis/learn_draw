# Transverse-camber ribbon support — bounded S1a experiment

## What this changes

One existing ribbon spec still owns the centre route, attachment, twist, taper, colors, and local longitudinal stripe. This experiment adds one dimensionless support value, `camber`, in `[0, 0.5]`. The comparison freezes it at **0.35**; do not search or tune this value against a picture. The envelope is `c(u) = camber * sin²(πu)`, so root and tip are unchanged. This is a candidate support family, not the recovered 3D truth of any reference ribbon.

The artwork remains one connected `(u,v)` domain, `u∈[0,1]`, `v∈[-1,1]`. There are no hand-authored mesh vertices, view-dependent cuts, new line styles, shadows, or width inflation. Front/back paint follows the generated triangle winding after camber, and existing opaque visibility compares the resulting depths.

## Width and finite-mesh construction

For an ideal orthonormal cross-section

`Q(u,v) = C(u) + k(u) [v W(u) + c(u) v² N(u)]`,

where `C` is the existing route, `W` the transported/twisted width axis, and `N` its perpendicular support normal. The continuous requested width is

`w(u) = width * [1 + (tip_ratio - 1)u]`.

The analytic full arc factor for this ideal section is

`F(c) = sqrt(1+4c²) + asinh(2c)/(2c)`, with `F(0)=2`,

so its scale is `k = w/F(c)`. These are world-length units for `w` and `k`; `u`, `v`, `camber`, and `c` are dimensionless.

The real renderer must preserve the old *finite piecewise-triangle* support exactly at zero camber. Between longitudinal stations, an old cross-section is not always a straight orthonormal segment: it can pass through the old diagonal and its transverse slope changes there. The implementation therefore does not pretend the finite baseline is the ideal formula. At a fixed `u`, it:

1. Gets the old barycentric section `B(u,v)` from its existing source triangles, with material centre `M(u)=B(u,0)`.
2. Adds the bounded rise `h(u)v²N`, where `h=w(u)c(u)/2`, to form `R(u,v)`.
3. Integrates the actual piecewise section speed `|dB/dv + 2h v N|` separately on each old triangle side using fixed composite Simpson integration. Its zero-camber length is `L₀(u)` and its bowed length is `L₁(u)`.
4. Emits `M(u) + [L₀(u)/L₁(u)] [R(u,v)-M(u)]`.

The positive scale is geometry-only, cached for each sampled `u`, and preserves the original `v=0` material point. At `camber=0` the mapping bypasses normalization and is the exact old source triangles; at root/tip the envelope is exactly zero and the original rows are retained. The normalized continuous curved section has the old finite baseline arc length. `L₀(u)` approximates the continuous requested `w(u)` with the old mesh's sampling error; independent 512-step checks on the frozen and tapered probes bound that difference below `1e-5` world units. Rendered chords approximate the normalized continuous curve, so their measured length converges with more transverse samples.

Do not replace the old barycentric centre with a smoother analytic `C(u)` between stations. The old finite material centre and the continuous requested route are distinct representations; the station rows remain attached to the requested route, and the zero limit remains exact.

## Use

`teaching/example-ribbon.json` is the unchanged positive half-twist family example (frozen source hash in `work/cases.json`). Render either limiting control or the selected curved condition:

```bash
.venv/bin/python scripts/ribbon_surface.py \
  .scratch/21-ribbon-cross-section/teaching/example-ribbon.json \
  --camber 0 --yaw 0 --pitch 0 \
  -o .scratch/21-ribbon-cross-section/evidence/example-flat

.venv/bin/python scripts/ribbon_surface.py \
  .scratch/21-ribbon-cross-section/teaching/example-ribbon.json \
  --camber 0.35 --yaw 38 --pitch 22 \
  -o .scratch/21-ribbon-cross-section/evidence/example-camber
```

A spec plus `--camber` are the only authoring inputs. `--u-intervals` / `--v-intervals` are bounded compiler-sampling overrides. They do not add shape parameters. The frozen pair matrix is generated incrementally with `.venv/bin/python .scratch/21-ribbon-cross-section/work/build.py`; its JSONL progress, SVG/PNG panel cache, labelled and unlabelled board, and hashes stay in this exercise.

## What the mechanism measured

At the positive half-twist's old front facing-zero station `u=0.5`, dense section measurement gives material arc `0.36` world units flat and about `0.3599999` with camber. In the front view, projected width perpendicular to the route is about `0.02870` flat and `0.07243` cambered, while the sampled actual-normal view dot range changes from roughly `[-0.023,0.172]` to `[-0.495,0.622]`. The oblique measurements are also recorded in `evidence/geometry-mechanism.json`. These are mechanism measurements, not drawing-quality objectives. Camber can affect projections differently by view; it does not guarantee legibility.

## Limits and bad examples

- A first finite-mesh attempt used the analytic `k` directly on barycentric points. It read only about `0.35630` world units at `u=.49/.51` rather than the requested `0.36`. This is preserved in `evidence/before-width-fix/`; merely increasing longitudinal resolution was not accepted as the correction. The current implementation normalizes the actual finite bowed cross-section about its original material centre. Dense off-station tests cover both half-twist signs and a tapered probe.
- Using the old `width/2` with a nonzero bow would make the ideal section length `w*F(c)/2`, artificially widening material. Tests include this counterexample.
- Zero camber deliberately reproduces the old triangulated support rather than an ideal smooth centreline patch. The material-centre interpolation and finite chord tolerance must not be hidden as geometry truth.
- The original 48×6 panels are retained as **coarse, width-bound-failing precision evidence**, not a clean width verdict: direct intersections with their emitted triangles exceed the declared 0.002 world-unit chord difference at four fixed off-station probes. The separate `cases-fine.json` retest changes only compiler sampling to96×12, retains camber0.35 and every original spec/camera/material, and has 44 fixed actual-mesh section probes per unique geometry. Its results are in `evidence/fine/fine-mesh-width.json`; all132 flat-versus-curved comparisons pass 0.002. This is a bounded sample result, not a continuous/global guarantee or a new shape/style/learner candidate.
- The chosen matrix is five views: original positive half-twist front/oblique, the untouched failed negative-half-twist learner front/oblique as regression only, and the untwisted teaching arch front control. It is not a new held-out learner result.
- Finite samples, connectivity, and local normal checks do **not** prove continuous nonintersection. The opaque visibility reference renderer retains its prior limits and exact-tie policy. No hair, figure, route recovery, broad engine, line-art or visual acceptance is claimed.

## Review boundary

The labelled/unlabelled paired boards and `draw check` reports are diagnostic artifacts. Code tests, numerical projection measurements, and raster nonemptiness do not certify that a viewer reads a continuous two-sided turn. Parent review and a fresh image-only review remain necessary; do not self-certify the S1a perception gate.
