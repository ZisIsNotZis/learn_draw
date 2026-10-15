# Scoped repair v1 report

Scope: only full-edge waist/contact source diagnosis and cuff/sleeve full-section support-depth diagnosis, per Issue 47. Original `A-cloth-construction-v2` remains frozen.

## Findings and bounded change

- Waist joins are not source geometry gaps: both full sections (upper→band, band→continuation) were linearly sampled at 101 evenly spaced points; each corresponding generated outline section matched to <1e-10 in crop coordinates. All share `A-bodice-support`. Rendered PNG diagnostic probes along the computed sloped seams found nearby background-green pixels at some sample offsets, but not on a proven source gap; fill colors differ (`#e8e7dc` bodice/continuation versus `#d9d8ce` waist band), and the requested same-fill compound strategy does not apply. No geometry/color/mask/ordering modification was made for waist. Raster/visibility edge-AA versus fill tessellation cause is therefore NOT RESOLVED; no false diagnosis.
- Cuff/source defect confirmed: sleeve and cuff planes were depth-equal only at center. Across sampled sleeve terminal section endpoints, support depth difference ranged about -0.00502 to +0.00502 scene units; support gradients differed along that complete section. Fixed only new copy's cuff support: preserve center world-depth alignment, adjust gradient component along the seam direction to exactly match sleeve support over the full seam, retaining authored support variation in the direction leaving contact. No component geometry, band ease, color, backend or general engine changed.

## Proof

`tests/test_scoped_repair.py` checks full waist sections at 101 samples and cuff world-depth equality across 101 terminal samples. Build emits 16 semantic parts, 853 projected faces, 16 visible fill regions, max four authored coordinates. Actual 400×480 SVG/PNG and `draw check` comparison bundle were generated once. `check-a/report.txt` and `review-image-list.txt` are for fresh review; writer did not visually judge PNG. Image list contains exactly the five standard check images. Metrics are not used to tune.

Unknown/open: raster green seam cause not resolved; physical global intersections, art/R1, B, heldout and user gates remain open. This scoped candidate is not a visual/art PASS.
