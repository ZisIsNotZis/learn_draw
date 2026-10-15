# S1a ribbon-family implementation log

Status: the bounded ribbon generator, geometry tests, render regression and parent-approved
crossback shape-rule correction are implemented. The parent must still
review the refreshed boards; fresh blind readability review and ordinary-model held-out use are
pending. No visual/transfer exit claim, hair claim, reference-route fit, baseline promotion, commit or
push is made.

## Frozen matrix (unchanged through review corrections)

Source: [`work/cases.json`](work/cases.json), SHA-256
`bd2732b806de26cc2d8a261be68e8f30e21e1f8f8bd5301556d85241a8bc5800`.
Both fixed camera poses render the same six cases: `front` yaw 0°/pitch 0° and `oblique` yaw
38°/pitch 22°.

- `teaching-arch`: length 3.0, width 0.36, tip ratio 1.0, bend 0.42, depth 0.12, twist 0,
  arch, root `[-1.5, 0, 0]`.
- `bend-only`: same semantics except bend 1.05.
- `tapered-tip`: same as teaching except tip ratio 0.22.
- `twisted-two-sided`: same as teaching except twist π.
- `awkward-crossing`: length 3, width 0.34, tip ratio 0.78, bend 0.8, depth 0.72, twist 0,
  crossback, root `[-1.5, -0.35, 0]`.
- `body-card`: same continuous crossback values plus one opaque XY card with bounds
  `[-0.52, -0.50, 0.52, 0.45]`; both camera panels compare the full strip against that same strip
  with the card.

No case parameters, palette, camera pose or case order were changed during these corrections.

## Parent-review corrections

Review inputs: `.../0e006982-4f72-43bf-851a-fbdb8aa10a8f/s1a/code-review.md` and
`.../0e006982-4f72-43bf-851a-fbdb8aa10a8f/s1a/blind-visual.md`.

- **P1 clip coordinates:** both support-pane and single-pane `clipPath` rectangles now use `(0,0)`
  in the child group's local coordinates; their parent groups apply the pane translation exactly
  once. The render-level regression writes 380×300 SVGs through the existing Chromium renderer.
  It asserts the full/support panes contain base and stripe fills in both views, plus support fill,
  and probes an actual negative-z stripe triangle inside the card. The same raster sample is stripe
  fill in the unobstructed pane and display-card fill `#526a60` in the occluded pane. Exact palette
  counts (front / oblique) in full and support panes: base pink 1601/2466 and 1446/2204; front stripe
  252/402 and 235/384; support display fill 0/0 and 939/1080 pixels. These are geometric/render
  regression probes, not a perceptual verdict.
- **Crossback self-intersection bound:** `crossback` now rejects `abs(depth) < 2 * width`, as well
  as the existing near-zero bend. At depth zero its symmetric reverse run intersects at a distinct
  pair of `u` values. The `2×width` condition is a conservative bound at the *principal* front-camera
  projected pair near `u=0.19735` and `u=0.80265`: centreline depth gap is about
  `0.63858×abs(depth)`; maximum combined transverse half-width extent there is at most
  `1.25×width` because `tip_ratio≤1.5`. At the threshold the former exceeds the latter. This does
  **not** prove other surface sections or other camera projections are collision-free. Frozen case
  depth/width is `0.72/0.34`, above the required 2.0 ratio.
- **Crossing visibility and declaration order:** tests now pass the actual near and far crossing
  triangles together to `visible_fragments`, in both declaration orders, and assert the positive-depth
  named patch wins. The previous separate card/depth probes remain.
- **Camera-file validation:** malformed camera collections/entries and non-text names now raise
  explicit `ValueError`; duplicate camera names are rejected before `render_board` creates the output
  directory or SVG IDs. Tests assert the no-output behavior.

## Blind-review hypotheses checked against source and coordinates

Board is 1200×1310 with 380×300 cells at x = 20, 410, 800 and row y = 60, 370, 680, 990.
Accordingly, the reviewed crossing panels are front `(410,370,380,300)` and oblique
`(410,990,380,300)`; bend oblique is `(410,680,380,300)`; twist oblique is `(20,990,380,300)`.

- Awkward-crossing front uses base pink `#e68aa4` plus its front stripe `#472639`; bend-only oblique
  uses the same base/stripe pair; twist oblique includes front/back bases and their contrasting stripe
  fills. No cyan/teal artwork fill,
  triangle polygon, or mesh-edge stroke is authored. Other explicit colours in the panel are neutral
  backgrounds, text, and the diagnostic root marker; raster antialiasing may blend those/fill edges.
- At the two mathematically predicted crossing centreline sections in the current front view (near
  `(190,207)` in the 380×300 panel), the 17×17 probe contains 143 exact pink pixels and 104 exact
  plum-stripe pixels. No cyan-like pixel occurs in that crossing-centre probe. Broader
  cyan-like raster samples are near the diagnostic attachment-marker/panel edge or antialiased fill
  boundaries, not a third authored colour. The reported cyan sliver location is therefore not
  confirmed by these probes; no geometry or palette was changed to chase that description.
- Corrected awkward-crossing quads have no within-quad front/back switch in the front camera at 48
  intervals. Oblique twist retains a winding/facing switch across two sampled quads near
  `u=0.275–0.30`, so its pink/blue boundary is a legitimate material-side boundary, not an ink line.
  Oblique bend-only triangles had no sampled
  facing-side transitions and one compound pink fill path; its SVG has no diagonal strokes or
  per-triangle artwork paths. The reviewer’s seam description is not resolved to a source line by the
  evidence available. It may be a perceived contour/fill edge or a raster/renderer issue; no
  resolution increase or seam-hiding stroke/blur was added. Parent should re-review the updated
  report images and isolate a renderer repro if it still blocks readability.

## Public seam and tests

- `scripts/ribbon_family.py` exposes the strict compact ribbon interface, computed frames/mesh,
  facing, camera projection, support card and deterministic `render` / `board` CLI.
- `teaching/ribbon-card.md` records parameter bounds, the narrow crossback depth/width proof, bad
  input examples, intentional facing boundary and non-guarantees. `teaching/learner-packet.md` links
  the same constraint and retains no held-out answer.
- `scripts/tests/test_ribbon_family.py` now contains **17 tests**; the render-level tests use only
  existing Chromium/OpenCV/Numpy project dependencies. Geometry includes connected/shared
  boundaries, attachment and width invariance, winding/twist, finite frames/normals, crossing/card
  depth and declaration order, tessellation bound, invalid spec rejection, duplicate/malformed
  camera files, both-pane rendering, no mesh-edge strokes, and deterministic board generation.
- At 48 intervals, the sampled centreline midpoint/chord deviation stays below 0.04 world units for
  all three families at length 6 and bend/depth magnitude 9. This is not a surface-shading/line
  guarantee.

## Commands and observed results

Commands were run in `/home/z/vibe/learn_draw`, with finite timeouts.

1. `.venv/bin/python -m unittest scripts.tests.test_vector_visibility scripts.tests.test_spatial_sketch scripts.tests.test_figure_scaffold scripts.tests.test_ribbon_family`
   — **38 tests passed in 57.409 seconds**. Five non-fatal open-SVG `ResourceWarning`s originate in
   existing `scripts/draw.py:43` reads; no renderer/S0 source was edited.
2. `.venv/bin/python scripts/tests/test_scene.py` was not rerun for this artwork/presentation-only
   follow-up; it changes neither scene rendering nor the shared renderer. The earlier test run passed
   81/81 smoke tests plus five checks with a non-fatal open_clip QuickGELU warning.
3. `.venv/bin/python -m py_compile scripts/ribbon_family.py scripts/tests/test_ribbon_family.py`
   — passed.
4. `timeout 180 .venv/bin/python scripts/ribbon_family.py board .scratch/19-ribbon-family/work/cases.json --out-dir .scratch/19-ribbon-family/evidence`
   — passed after the local-art and presentation fixes; regenerated all 12 named case/camera SVG+PNG views and both boards.
5. `.venv/bin/python scripts/ribbon_family.py render .scratch/19-ribbon-family/work/teaching-example.json --name front --yaw 0 --pitch 0 -o .scratch/19-ribbon-family/evidence/teaching-example`
   — passed; regenerated teaching SVG/PNG.
6. `scripts/draw check .scratch/19-ribbon-family/evidence/learning-board.svg --outdir .scratch/19-ribbon-family/evidence/check/labelled --pane 1600`
   — passed, reference-free, 1200×1310 full-resolution draft.
7. `scripts/draw check .scratch/19-ribbon-family/evidence/learning-board-unlabelled.svg --outdir .scratch/19-ribbon-family/evidence/check/unlabelled --pane 1600`
   — passed, reference-free, 1200×1310 full-resolution draft.
8. Regenerated both boards with `board --svg-only` in `/tmp/ribbon-family-final-check` and `cmp`ed them with saved SVGs; rendered the labelled board to `/tmp/ribbon-art-final-a.png` and `-b.png`, `cmp`ed the PNGs, and compared the result with the saved board PNG — all byte-identical.
9. Earlier read-only baseline check `scripts/draw check .scratch/00-tooling/baseline/best.png --ref image.jpg` showed all five deltas `+0.000`; baseline itself was unchanged.
10. Final `.venv/bin/python -m py_compile scripts/ribbon_family.py scripts/tests/test_ribbon_family.py && git diff --check` — passed.

Exact image lists remain preserved in the reports:

- `evidence/check/labelled/report.txt`: `.scratch/19-ribbon-family/evidence/check/labelled/draft.png  -- the drawing`
- `evidence/check/unlabelled/report.txt`: `.scratch/19-ribbon-family/evidence/check/unlabelled/draft.png  -- the drawing`

These are the only images in each reference-free `draw check` report. Parent owns the new blind review.

## Final source/render hashes

Computed for the corrected source and refreshed evidence:

- `scripts/ribbon_family.py`: `015ec14ec90da5768dbcdd9486220d3971c55673f0944971ccb3a8a47662bd3e`
- `scripts/tests/test_ribbon_family.py`: `5347078429b19faaa4132a627ea4b967ea6a670bbc26b5841a85519a743b4202`
- `work/cases.json`: `bd2732b806de26cc2d8a261be68e8f30e21e1f8f8bd5301556d85241a8bc5800`
- `teaching/ribbon-card.md`: `6a7f267b845767e061c8e766b93f9d4bc61473fe280d699991f0be638d18aa1f`
- `teaching/learner-packet.md`: `e57dfafb659fdfdb015b3e31edfcaa7e7a6aa5c67d36f6f28ec372cd8e68e8c8`
- `evidence/learning-board.svg`: `af6852c6556e5642f7cae1d3628d64e90e9f27fdc7d5a6ce17aef4786f73d97c`
- `evidence/learning-board.png`: `659b706afb926fb47dc33000cf34aec64f3956aa3d4d5e044265da8440482dd3`
- `evidence/learning-board-unlabelled.svg`: `1aae859b1e1b050bedf2098c3d12b48f62f674a399951ab60d2f561cdfe67e22`
- `evidence/learning-board-unlabelled.png`: `0c5c8e513bdaec50a6760a24db1b014e6f4b6ae75eb1eda8bc545f184c52b244`
- `evidence/views/body-card-front.png`: `6840fc7ea12d637701df39b46ae66e97476eb53df2329f9b9b94c5103ae922dd`
- `evidence/views/body-card-oblique.png`: `a2118493b4eb8ee6bd5188b4e1dba669e6d64be2064f91c8cf8dfc79c5971e1b`

## Boundaries and pending work

Only the new ribbon generator, its dedicated tests, and its S1a exercise artifacts were changed.
Existing visibility, sketch, figure, renderer, vendor, baseline, official docs, the frozen case
matrix, and parent S0/planning changes remain untouched. No dependencies/install, native image
generation, commit, push, manual visibility ranges, or child delegation occurred.

Pre-existing staged `.gitmodules` and vendor additions remain staged and preserved; no task file was
staged, so whole-repository `noStagedFiles` is still false. The baseline `draw check` generated its
normal report bundle under `.scratch/00-tooling/evidence/check/`, without changing the baseline.

Parent still needs to inspect corrected code and the refreshed report images, then run the held-out
learner. Crossback depth/width only separates the principal paired sections; unrestricted surface
self-intersection remains unsupported. The exact reference ribbon route and hair-family competence
remain unresolved. S0 opaque visibility limits, including exact coplanar ties and different-fill
seams, remain in force.

## Pre-correction crossback intersection evidence (preserved before formula edit)

Original crossback centreline source formula before correction (module SHA-256
`39399287ef89b6c942f356485699208367ab2518f062268c449cc2b36fec90ec`): with
`E=sin²(πu)`, local `x=L*(u+0.32*sin(2πu))`, `y=bend*E`, and
`z=depth*sin(2πu)*E`; `origin`/`heading` then rotate the x/y pair. Frozen input was not changed.

Independent actual-tessellation repro: an edge-segment/triangle Möller–Trumbore test on the generated
3D mesh found nonlocal triangle intersections, excluding adjacent u cells. At 48 segments, triangle
`(u-cell 13, half 0)` edge 1 intersected `(u-cell 18, half 1)` at world point
`(0.2008483843, 0.2391740885, 0.3926198181)`; segment-edge parameter `.9406787070`, target triangle
barycentrics `.3911961855, .5694568334, .0393469811`. At 128 segments, another convergent hit was
cells 36/49 at `(0.1967949951, 0.2374991692, 0.3896155371)`, with target barycentrics
`.4947500122, .4821604905, .0230894978`. The crossing is therefore present in actual triangular
support meshes, not a Chromium/SVG paint-order artefact.

Independent continuous-frame probe used a 256-station parallel-transport frame, linearly interpolated
width axes, exact analytic centreline and the surface rule `C(u)+v*h(u)*W(u)`. A bounded
Nelder–Mead minimization on distinct u intervals `.28–.33` and `.35–.40` returned residuals below
`1.3e-12` for distinct surface coordinates, e.g. `(u=.3105994,v=.73869097)` and
`(u=.36773591,v=.75181876)`. Method notes and the pre-fix formula are preserved here before its
implementation change; do not reuse these coordinates as the only regression target.

## Parent-approved crossback construction correction and validation

After reviewing the exact 3D repro, parent approved an internal crossback shape-rule correction while
keeping all `cases.json` values, cameras, root attachment and the principal projected over/under
crossing unchanged. With the pre-fix broad envelope, side displacement `bend*E` folded the finite-
width band during the reverse run. It is now `bend*E^2` (`bend*sin^4(pi*u)`) for crossback only;
the x reverse-run and depth wave are unchanged. Its analytic derivative was updated accordingly.
This is a geometry-derived structural fix for actual nonlocal triangle intersections, not a visual-
score or color-seam adjustment. The case parameter file SHA remains exactly unchanged.

Independent convergence/evidence tests on the corrected frozen input now:

- Detect a synthetic segment/triangle hit as a negative control.
- Scan nonadjacent u-cell triangle pairs in generated 3D meshes at 32, 48, 64 and 96 intervals;
  no nonlocal segment/triangle edge hit was found at any level. This is bounded to the tested mesh
  sequence and non-coplanar hit probe; it is not a continuum or general collision guarantee.
- Verify sampled centreline midpoint/chord error strictly decreases across those levels.
- Derive the principal x-symmetry root from the generated centreline, not an authored station. At
  `u≈0.197350309/.802649691`, projected x/y coincide to floating precision and the unchanged depth
  wave separates z by `0.459780574` world units. Near/far patch visibility still chooses the near
  patch in both declaration orders.

Corrected source-side verification: at 48 intervals the awkward-crossing front view's sampled
quad halves are all front-facing, so the former diagonal front/back slivers from the local fold are
gone. The relevant front panel's path fill is pink only; the principal-pair 17×17 centreline probes
at about `(190,201)` contain only exact authored pink. Oblique bend remains one pink compound fill
with no facing switch; oblique twist retains its two expected material fills and two quads crossing
the winding boundary near `u=.275–.30`. No tessellation count/case value was increased. The cyan
hypothesis was checked against the refreshed source/pixels; the broad antialias/marker mask remains
outside the principal pair. This is not a substitute for parent blind review.

## Fresh blind recheck: small local-artwork and presentation correction

The latest blind review still read the same-pink principal crossing as a merged knot, found the
support card low-contrast, and reported clipped case 5/6 captions. Parent authorized only a narrow
longitudinal local-artwork mark and diagnostic presentation fixes; no support/camera/case geometry or
crossback formula was changed in this step.

- Added one local UV stripe across the complete strip: `v∈[-0.18,+0.18]`, spanning all `u∈[0,1]`.
  Its front-side fill is `#472639` against the pink base (`5.32:1`), and its back-side fill is
  `#fff1b8` against the blue base (`3.11:1`). Winding-derived side selection for the base remains
  unchanged; stripe face color is selected from that same side result.
- Each stripe triangle is clipped in source `(u,v)` and interpolated only inside its original support
  triangle. The original base support triangles are then appended unchanged after the stripe faces;
  the existing exact-depth tie rule lets the authored stripe overlay win on its own co-planar region.
  Tests compare the returned base-face suffix to `ribbon_faces`, check stripe UV coverage and area,
  barycentric reconstruction of every stripe vertex onto the original triangle, both side colors,
  and near/far stripe visibility at the projected crossing in both face-declaration orders. No mesh
  edge is stroked or drawn as ink.
- The body-card drawing now uses display-only muted green-gray `#526a60` for the opaque support card.
  Its frozen `bounds`, z=0 plane, triangulation and depth are untouched and no color was added to
  `cases.json`. The card/background contrast is `5.17:1`.
- Purpose captions wrap at 52 characters into SVG `tspan`s. All words are preserved, the panel
  artwork viewport begins at the same fixed y for labelled/unlabelled panels, and case 5/6 captions
  are two lines (46/47 characters maximum) rather than clipped.
- Corrected board source/hash is current; the prior no-stripe labelled/unlabelled board SVGs were
  restored from the deterministic pre-stripe rerender under
  `evidence/review-before-local-stripe/`. Their rendered PNGs reproduce their previous hashes
  (`4013748a…` labelled, `3e14b501…` unlabelled) byte-for-byte. Current and prior evidence coexist.

Exact-fill pixel counts from the current case views (diagnostic evidence, not a visual verdict):

- `body-card-front`: full base 1601 + stripe 252; support pane base 1446 + stripe 235 + card 939.
- `body-card-oblique`: full base 2466 + stripe 402; support pane base 2204 + stripe 384 + card 1080.
- `twisted-two-sided-oblique`: both material bases and stripe colors are present (front 2160/370,
  back 5628/1153 pixels).
- `awkward-crossing-front`: base pink 11580 and front stripe 2220; the resolved principal-pair
  17×17 neighborhood at `(190,207)` includes 143 exact pink and 104 exact plum stripe pixels.

Parent retains the readability judgment; the image paths listed by the new `draw check` reports are
unchanged and point to the updated local-artwork boards. Fresh findings are from
`.../3ba2025b-1d09-4cef-9e1e-bfb363e2f81c/s1a/code-recheck.md` and
`.../3ba2025b-1d09-4cef-9e1e-bfb363e2f81c/s1a/fresh-visual-recheck.md`; worker did not self-certify
those image judgments.

## Bounded S1a occlusion-perimeter and twist probe

Contract: [`work/occlusion-probe-brief.md`](work/occlusion-probe-brief.md). This adds only
`work/occlusion_probe.py`, `work/test_occlusion_probe.py`, `evidence/probe/`, and this log entry.
Frozen cases, renderer/visibility/figure source, cameras, learner output and official docs are
unchanged.

The cue selector enumerates all 98 semantic perimeter segments for the 48-interval frozen crossing
(two local-v long sides per interval plus two caps). For each projected perimeter line segment it
splits parameters at actual projected support-triangle edge crossings and linear triangle-depth
equality roots. On each resulting interval it tests projected-triangle barycentrics/depth, excludes
the candidate cell and its vertex-sharing neighbours, rejects the cue if any nonadjacent face is
closer, and keeps it only when at least one nonadjacent face is farther. Depth tolerance is the
existing `vector_visibility.EPS` (`1e-7`); projected parallel/edge tolerance is `1e-9` and interior
barycentric tolerance is `1e-8`. No screen box, authored `u` interval, visibility flag or filled-path
patch participates in selection. Stroke width affects only the diagnostic drawing after selection.

Observed geometry-derived selection on frozen front crossing: exactly two merged cue paths, `v=-1`
from computed `u=.210795.. .266432` (source cells 10–12, four farther faces) and `v=+1` from
computed `u=.150294.. .184512` (cells 7–8, six farther faces). Their minimum camera-depth gaps are
about `.4620` and `.3927`. Reversing only depth sign for an explicitly additional control selects
opposite traversal-side paths: `v=-1` at `.721990.. .821105` (cells 34–39) and `v=+1` at
`.781761.. .863086` (cells 37–41). Those numbers are generated provenance, not author-selected
ranges. The teaching arch has the same 82 full-perimeter candidates but zero occlusion cue; a
whole-perimeter-outline negative control would therefore fail the selector regression.

The board pairs before/after views for the frozen crossing, the teaching negative control, an
explicit non-frozen depth-sign reversal, and twist at 40/128 intervals. The twist uses the same
frozen spec and oblique camera; support-frame normal-dot roots are `u=.30087812` and `.30084670`
(resolution difference `.00003143`), with facing signs still opposed on either side. No smoothing,
case/camera edit, mesh-edge line or tessellation change to frozen input was made.

Validation: `.venv/bin/python work/test_occlusion_probe.py -v` — **6 probe tests passed**. They
cover full perimeter candidate construction, actual split/visible/far-face provenance, the
all-perimeter-outline counterexample, teaching negative control, depth-sign source-boundary change,
unchanged filled paths when cue is enabled, and twist root convergence. The labelled and unlabelled
probe boards were generated and `scripts/draw check`ed reference-free at full resolution. Both board
SVGs/manifests were regenerated to `/tmp` and compared; each board was rendered twice and compared
to its saved PNG byte-for-byte. No unrelated suite, scene smoke, baseline or learner gate was rerun.

Exact new report image lists:

- `evidence/probe/check/labelled/report.txt`: `.scratch/19-ribbon-family/evidence/probe/check/labelled/draft.png  -- the drawing`
- `evidence/probe/check/unlabelled/report.txt`: `.scratch/19-ribbon-family/evidence/probe/check/unlabelled/draft.png  -- the drawing`

The labelled manifest contains the computed candidate/triangle provenance and hashes. Before/after
fillable geometry equality is regression-tested. Cue selection and the 40/128 analysis add no claim
of universal perimeter correctness, arbitrary-surface clipping or successful visual readability;
parent owns the blind review.
