# Teaching card — center-route return bend

## When to choose this shape rule

Use a return bend when a continuous flat ribbon changes direction along its centre route and a side of the sheet must face away and later return toward the viewer. This is not a longitudinal twist: the centre-route tangent turns while the material-width axis `W` stays fixed. It is one support for one connected local `(u,v)` strip, not separate front/back pieces.

## Meaningful parameters

- `root`: world-space attachment point `C0`.
- `root_tangent`: normalized tangent `e_x` at the attachment.
- `bend_normal`: normalized `W`, perpendicular to `e_x`; derive `e_d = W × e_x` so `e_x × e_d = W`.
- `length` `L`: route length in world units.
- `width` `w`: root material width in world units.
- `tip_ratio`: tip/root material-width ratio; the strip width changes linearly along `u`.
- `alpha`: total centre-route turn in radians, from straight `0` through at most `π`.

The teaching implementation bounds `L` to `[1,3]`, `w` to `[0.1,0.6]`, `tip_ratio` to `[0.5,1]`, `alpha` to `[0,π]`, each root coordinate to `[-10,10]`, and sampling to `16≤Nu≤32`, `2≤Nv≤4`, with no more than 256 opaque input faces including artwork and occluder pieces. The frozen image-free experiment uses `Nu=16`, `Nv=2` so the complete local stripe and fixed two-triangle card remain inside that total cap.

## Generated geometry

For `u∈[0,1]`, `v∈[-1,1]`:

```text
q(u) = 3u² − 2u³
theta(u) = alpha * q(u)
T(u) = cos(theta) * e_x + sin(theta) * e_d
C(u) = C0 + L * integral_0^u T(t) dt
w(u) = w * (1 − (1 − tip_ratio) * u)
P(u,v) = C(u) + 0.5 * v * w(u) * W
```

The integral uses fixed deterministic 256-step composite Simpson quadrature. The finite support mesh is compiler output; keep the entire UV rectangle connected. The continuous Jacobian magnitude is `L*w(u)/2`, at least `.025` over the constructor domain. Material width `w(u)` is not the same as projected width: an orthographic camera sees `w(u)*sqrt(1−(D·W)^2)`.

## Surface sides and overlap

Choose the two-sided base/stripe fill from each actual finite support-face normal and the frozen camera direction. Then submit the complete opaque strip and any real opaque card triangles to the depth resolver. Greater actual camera depth wins; never specify visible intervals, hand-split a crossing, duplicate front/back strips, or use SVG element order to override depth. Exact ties keep the resolver’s first-declared rule, and its existing EPS/deadbands remain.

The primary `alpha=π`, `D+=(0,cos10°,sin10°)` fixture has positive clipped area and independent nearest-depth winners on both off-centre facing sides. Its exact symmetric `D−=(0,1,0)` mate is a negative: one side has zero independent depth winners; a tiny kernel residual is retained but is not visible-side evidence. The route midpoint is edge-on in `D+`; it is not a broad-facing teaching point. The fixed root-local card is actual geometry and is resolved by depth.

## Limits and failure cues

This is one finite mechanism study on opaque triangles. A stylized image cannot determine a unique 3D route; no reference image enters the engine. A failed positive area/oracle gate stops the dependent render. The D-minus case must remain a negative; do not tune its view or geometry. The lesson does not establish figure placement, correct reference reconstruction, hair construction, line selection, S1a readability, or ordinary-model transfer. Treat the labelled/unlabelled panel boards as pending independent observations, not as self-approved examples.
