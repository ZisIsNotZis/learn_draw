# Frozen S0 visibility/raster cases (pre-fix)

Question: does the opaque projected-triangle path preserve coverage, and do SVG tessellation boundaries create false gaps? Cases and tolerances below are fixed before evaluating any change.

## Geometry fixtures and assertions

1. **Adjacent tessellated surface:** a 3×2 planar quadrilateral tessellated on both diagonals; sample a 31×21 interior grid (excluding the exact outer boundary) and require exactly one visible face at each point. Separately raster the prewritten fractional-coordinate 8×6 checker-diagonal sheet (320×256 PNG); every pixel in the fixed 248×186 interior rectangle must equal the fill color exactly. Background is a contrasting color.
2. **Partial occlusion / true boundaries:** a small near triangle covers only the central part of a larger far triangle. Fixed probes on near, visible-far, and uncovered-background points must return the expected surface set; the geometric fragment area must preserve the far triangle's visible area to 1e-8.
3. **Within-face depth flip:** preserve existing crossing test: far at (0.5,0.5), near at (2.6,0.3); add probes either side of equality. No raster gap is permitted at the actual crossing line.
4. **Declaration reversal:** reverse two overlapping crossing faces and sample a predeclared 11×11 grid; visible color at every probe must be invariant except at exact equal-depth ties. At an exact tie, first declaration wins, explicitly tested.
5. **Self-occlusion:** two projected portions of one named component cover the same sample area at different depths; the near paint must survive and the far paint must not.
6. **Tangency and coplanar tie:** edge-touching coplanar triangles both remain visible at interior probes. Exact coplanar full overlap has a deterministic first-declared-wins tie; this is supported policy, not geometric ordering. Non-manifold intersections/transparency remain unsupported.
7. **Alternate subdivision:** the same planar whole strip is emitted as coarse and fine triangulations; fixed geometric probes must agree. At raster scale 2 px/world-unit, zero incorrect-color interior pixels is the raster tolerance.
8. **Two cameras / same whole strip:** generate both views from one uncut strip function, without visibility flags; the view projections and visible masks must differ while local-strip connectivity remains unchanged. No author cut or view-specific geometry is permitted.

No pixel metrics against the portrait are used. The color alarm is only an exact fill/background check on controlled synthetic geometry.
