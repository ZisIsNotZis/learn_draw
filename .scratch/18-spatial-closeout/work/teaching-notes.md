# Why triangle seams appeared, and what removes them

## Observation

The geometric visibility routine returns a complete tessellated sheet. In the fixed 8×6 flat-sheet probe, all 651 predeclared interior sample points had exactly one covering visible triangle, and no pixels were missing because of the visibility clipping. The rasterized SVG nevertheless showed darkened seams at internal diagonals and cell boundaries: Chrome antialiases every independently painted polygon edge against the page below it. Adjacent polygons can each contribute fractional coverage at their shared edge, exposing the contrasting background. This is a raster-coverage artifact, not a depth or topology gap.

The controlled 320×256 pair uses the same 96 triangles, fill, background and coordinates. Counting non-fill pixels in the fixed 248×186 interior rectangle (x=32..279, y=28..213, strictly within the exterior silhouette) gave **4,438 before** and **0 after**. Remaining antialiasing belongs to the true outside silhouette, not internal tessellation. The saved SVG/PNG pair is under `evidence/{before,after}/adjacent-faces.*`.

## Rule

Keep depth clipping and every visible polygon exactly as computed. For SVG output, gather polygons only when both semantic component and fill color match, normalize their winding, and emit them as subpaths of one `fill-rule="nonzero"` path. At a shared edge, adjacent subpaths have opposite directed edges; the SVG fill rasterizer cancels that internal edge before antialiasing. No geometric union backend, stroke, blur, background paint, or hidden-surface enlargement is needed. Different components and different stripe colors remain separate fills, so real contact/occlusion and material boundaries are preserved.

This only addresses internal edges where the emitted polygons share matching coordinates. It does not solve geometric intersections, transparent layers, non-manifold support surfaces, or production-scale performance. Exact coplanar overlap is a policy tie: first declared face wins. Edge-only tangency has no occluded area.
