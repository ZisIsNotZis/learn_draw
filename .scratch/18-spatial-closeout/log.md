# S0 visibility seam closeout — implementation/evidence log

Status: **S0 implementation plus review follow-ups are present; latest recorded checks pass. Recovery was interrupted at the exact 1,200,000 ms runtime limit. Independent visual review and parent acceptance remain pending; not claiming S0 closed.**

## Recovery follow-up after timeout

The preceding follow-up worker was terminated at exactly **1,200,000 ms**. The parent preserved `/tmp/s0-timeout-partial.patch` and `/tmp/s0-timeout-untracked-evidence.tar.gz`; the current worktree contains the two requested fixes and regenerated diagnostics. In this recovery-only pass I did not edit source, rerun expensive tests, or repeat renders; I verified current file hashes, Git state, and the saved check report. Test/render results below are the already-observed results from before the interruption, not post-recovery reruns.

Review finding 1 is addressed: `spatial_sketch.svg_document()` gives its two `view()` calls explicit `camera-0` / `camera-55` ID scopes. The new `test_two_view_svg_ids_are_unique_across_both_cameras` parses the entire two-view SVG and asserts every ID is unique and both namespaces occur.

Review finding 2 is addressed: the new `test_chromium_raster_has_no_tessellation_seams_or_boundary_leaks` uses the existing `scripts/draw.py` Chromium renderer on the frozen fractional 8×6 grid plus a nearer triangle. It renders both grouped fills and an independent-per-polygon negative control. The far-only 99×186 interior must be exact sheet color in the grouped render (zero mismatches) and must contain mismatches in the old per-face control. It then asserts exact safe-interior pixels for the sheet exterior/background and near/far occlusion boundary. Thus the test exercises raster output, not path count or only geometric samples. It uses existing cv2/numpy and the cached `chrome-headless-shell`; no dependency was added.

The recorded focused suite is **21 tests passed in 39.124 s**. The Chromium test emitted two non-fatal `ResourceWarning`s from existing `scripts/draw.py:43` (`read_text` leaves the temporary SVG file handle open); test assertions passed. The latest board and spatial sketch were regenerated, checked reference-free, and their SVG/PNG determinism comparisons passed. Current hashes are listed below.

Runtime acceptance note: no explicit runtime rejection message was included in the revived-session context. The previous machine-readable handoff reported `noStagedFiles: false` because kickoff already had staged `.gitmodules` and vendor submodule entries, which were expressly protected. If that global-index condition was rejected, that is the exact known reason; no implementation file was staged. The visual gate was not rejected or waived—it remains incomplete because no independent blind reviewer has run.

## Diagnostic presentation follow-up (reviewer feedback)

Before adjusting the diagnostic, I checked `depth_flip_case()`'s source triangles: both have identical x/y vertices `[(60,72),(420,72),(60,276)]`, so their entire projected triangle footprints coincide. The flat face is z=0; the sloped face has z values `[-1,+1,-1]`, crossing equality at x=240. The equal-size result triangles are an occlusion partition of overlapping source faces, not two non-overlapping inputs. `depth_flip_case()` now displays the source footprint as a separately labeled input-only translucent/dashed overlay, its center equal-depth boundary, and both declaration-order visible outputs side by side.

I also checked `strip_faces()` mathematically. The loop centerline is `(cos t, .12 sin(2t), sin t)` and the half-width is `.12 v (cos t,0,sin t)`. In the yaw=0/pitch=0 front view, width is in the XZ plane and contributes no screen-height extent; only the ±.12 Y bend does, so the thin front strip is a real edge-on projection. At the center samples t=π/2 and 3π/2, z is +1 and -1 respectively against the body card z=.55: the near arc overlays the body, while the far arc is occluded. The second same-geometry view now uses yaw 55° plus pitch 35°; pitch projects the radial width into screen height (about 14 px full width at the diagram scale), making the stripe band readable. Both captions state which colored surface is the strip/body and the near/far relation. This is a diagnostic camera variation, not a recovered reference route or visibility edit.

The board is now 1600×640: the overlap input plus two depth-order outputs get a 640-px-wide top-right panel; the two-camera strip view is 1120 px wide below. `visibility_board.py` namespaces path IDs per case/camera and runs `ensure_unique_ids()` over the completed nested board before saving. Generation passed; an independent XML count found **21 IDs, all unique**. The original frozen cases and engine/source tests were left unchanged. No test suite was rerun for this presentation-only change, per scope; the prior 21-test result remains pre-timeout evidence. Board/case PNGs and the reference-free draw-check bundle were regenerated, and saved-board SVG/PNG determinism was rechecked.

## Question / cause / fix

Question: can tested opaque-surface visibility render a continuous triangulated strip in two views without artificial tessellation seams while preserving true occlusion boundaries?

Before changing code, I copied the current `vector_visibility.py`, `spatial_sketch.py`, and spatial test to `work/before/`; hashes are recorded below. I preserved the existing two-camera sketch SVG/PNG under `evidence/before/`. A controlled 320×256 raster case showed dark seams along internal tessellation edges. Geometry probes did not find missing visible regions: all 651 preselected 31×21 interior samples on the independent 3×2 planar tessellation had exactly one covering face. The failure is SVG raster coverage: separately painting each adjacent polygon antialiases its edge against the background even when the vector regions meet.

A fractional-coordinate 8×6 sheet, alternating its cell diagonals, was rendered once as independent `<polygon>`s and once as grouped compound subpaths. In the fixed 248×186 interior rectangle, before had **4,438/46,128** non-fill pixels; after had **0/46,128**. Measurement and hashes: `evidence/raster-measurement.txt`. The true exterior silhouette is excluded.

`visible_regions()` in `scripts/vector_visibility.py` now groups only equal `(component, color)` visible polygons, normalizes each polygon's winding, and emits compound SVG path data. `spatial_sketch.py` writes one named, commented, stroke-free path per semantic fill at full precision. The SVG fill rasterizer cancels shared internal edges. Visibility clipping, depths, fragments, and external/occlusion boundaries are not expanded, blurred, stroked, or repainted. `figure_scaffold.py` was not modified.

## Frozen cases and results

Pre-evaluation case list and tolerances: `work/frozen-cases.md`.

- Adjacent 3×2 triangulation: 31×21 interior sample grid, one visible face/sample. Pass. Raster control: exact interior fill after path grouping. Pass; before/after artifacts retained.
- Partial occlusion: near triangle covers area 2 of far area 8; visible far area is 6 (delta ≤1e-8); probes confirm near fill, visible far fill, and untouched background. Pass.
- Within-triangle depth flip: probes on both sides of crossing select the correct front face in either declaration order. Pass.
- Declaration reversal: fixed 11×11 interior probes match away from equal-depth ties. Pass.
- Self-overlap: closer paint wins for the same component, both source orders. Pass.
- Coplanar overlap tie: first declaration wins deterministically; edge-touching coplanar faces retain both interiors. Pass. Exact coplanar tie and edge tangency are also displayed in `evidence/after/cases/tie-self-occlusion.png`.
- Alternate subdivisions: the 1×1 coarse square and 6×4 retessellation with alternate diagonals agree at 17×23 preselected interior probes. The board also displays two versus 96 triangles.
- Camera: the same uncut, 24-segment three-stripe loop and body card are projected at 0° and 55°. Visible strip fraction changes 0.8755→0.7968 without flags or changing local geometry. Pass; see the board and individual two-view render.

No portrait metric was used as a target. These are bounded opaque-triangle tests, not unrestricted intersection/degeneracy coverage.

## Commands and observed results

All work commands were run with finite timeouts. Python: **3.12.3**. Cached renderer: **Google Chrome for Testing 151.0.7922.34** (`scripts/draw` / headless shell).

| Command | Result |
|---|---|
| `scripts/draw render .scratch/18-spatial-closeout/evidence/before/adjacent-faces.svg -o .scratch/18-spatial-closeout/evidence/before/adjacent-faces.png --size 320x256` | Reproduced per-face seam raster, 320×256. The preceding malformed `--size 320` attempt correctly rejected the missing height; corrected before evidence was used. |
| `.venv/bin/python -m unittest scripts.tests.test_vector_visibility scripts.tests.test_spatial_sketch scripts.tests.test_figure_scaffold` | **21 tests passed in 39.124s** on the follow-up revision. This includes the Chromium raster negative control/boundary test, two-view full-document ID uniqueness, prior geometry regressions, and protected figure-scaffold tests. Two non-fatal `ResourceWarning`s came from existing `scripts/draw.py:43` while reading temporary SVGs. This result was captured before the 1,200,000 ms interruption; it was not rerun during recovery. |
| `.venv/bin/python scripts/tests/test_scene.py` | **81/81 smoke tests passed**, plus 5 additional wave/strand/ring checks passed. It emitted a non-fatal open_clip QuickGELU config warning. |
| `scripts/draw check .scratch/00-tooling/baseline/best.png --ref image.jpg --outdir /tmp/s0-baseline-gate-fix1` | Passed ratchet gate in `/tmp`; every delta was `+0.000`. Baseline artifact was read only. |
| `scripts/draw check .scratch/18-spatial-closeout/evidence/after/visibility-board.svg --outdir .scratch/18-spatial-closeout/evidence/after/check` | Passed reference-free. Report: `evidence/after/check/report.txt`; image list names only `evidence/after/check/draft.png`. No `--ref`; original `image.jpg` remains present. |
| `.venv/bin/python .scratch/18-spatial-closeout/work/visibility_board.py -o .scratch/18-spatial-closeout/evidence/after/visibility-board.svg --cases-dir .scratch/18-spatial-closeout/evidence/after/cases` followed by the render commands below | Regenerated board and five individual cases; board is now 1600×640 and validates globally unique IDs before writing. |
| `.venv/bin/python scripts/spatial_sketch.py -o .scratch/18-spatial-closeout/evidence/after/spatial-sketch.svg` and `scripts/draw render ... --size 1200x630` | Updated two-view same-strip proof rendered at 1200×630. |
| Re-run board generator to `/tmp/s0-visibility-board.svg` and render to `/tmp/s0-visibility-board.png`, then `cmp` each with evidence versions | Source SVG and PNG byte-identical. Hashes below. |
| Re-run `spatial_sketch.py` and `draw render` to `/tmp/s0-spatial-sketch.svg/.png`, then `cmp` with evidence versions | Source SVG and PNG byte-identical. Hashes below. |
| `.venv/bin/python -m py_compile scripts/vector_visibility.py scripts/spatial_sketch.py scripts/tests/test_spatial_sketch.py scripts/tests/test_vector_visibility.py` | Passed. |
| `git diff --check` | Passed after final edits. |
| `git diff --cached --name-only` | Only the pre-existing staged `.gitmodules`, `vendor/huashu-art-motion`, and `vendor/huashu-design` appear. No implementation file was staged; none was staged by this worker. |

Exact final generator/render/determinism invocations:

```bash
.venv/bin/python .scratch/18-spatial-closeout/work/visibility_board.py -o .scratch/18-spatial-closeout/evidence/after/visibility-board.svg --cases-dir .scratch/18-spatial-closeout/evidence/after/cases
scripts/draw render .scratch/18-spatial-closeout/evidence/after/visibility-board.svg -o .scratch/18-spatial-closeout/evidence/after/visibility-board.png --size 1600x640
scripts/draw render .scratch/18-spatial-closeout/evidence/after/cases/retessellation.svg -o .scratch/18-spatial-closeout/evidence/after/cases/retessellation.png --size 480x320
scripts/draw render .scratch/18-spatial-closeout/evidence/after/cases/partial-occlusion.svg -o .scratch/18-spatial-closeout/evidence/after/cases/partial-occlusion.png --size 480x320
scripts/draw render .scratch/18-spatial-closeout/evidence/after/cases/depth-flip-order.svg -o .scratch/18-spatial-closeout/evidence/after/cases/depth-flip-order.png --size 640x320
scripts/draw render .scratch/18-spatial-closeout/evidence/after/cases/tie-self-occlusion.svg -o .scratch/18-spatial-closeout/evidence/after/cases/tie-self-occlusion.png --size 480x320
scripts/draw render .scratch/18-spatial-closeout/evidence/after/cases/two-view-strip.svg -o .scratch/18-spatial-closeout/evidence/after/cases/two-view-strip.png --size 1120x320
scripts/draw check .scratch/18-spatial-closeout/evidence/after/visibility-board.svg --outdir .scratch/18-spatial-closeout/evidence/after/check
.venv/bin/python .scratch/18-spatial-closeout/work/visibility_board.py -o /tmp/s0-board-present-fix1.svg --cases-dir /tmp/s0-board-cases-fix1 && cmp .scratch/18-spatial-closeout/evidence/after/visibility-board.svg /tmp/s0-board-present-fix1.svg && scripts/draw render /tmp/s0-board-present-fix1.svg -o /tmp/s0-board-present-fix1.png --size 1600x640 && cmp .scratch/18-spatial-closeout/evidence/after/visibility-board.png /tmp/s0-board-present-fix1.png
.venv/bin/python - <<'PY'
import xml.etree.ElementTree as ET
root=ET.parse('.scratch/18-spatial-closeout/evidence/after/visibility-board.svg').getroot()
ids=[e.attrib['id'] for e in root.iter() if 'id' in e.attrib]
assert len(ids)==len(set(ids))
print(f'{len(ids)} SVG ids, all unique across nested board')
PY
```

Raster counts were obtained with `.venv/bin/python` + Pillow by loading the before/after PNG as RGB and checking every `(x,y)` in `range(32,280) × range(28,214)` against `(69,201,130)`; exact summary and hashes are in `evidence/raster-measurement.txt`.

Two early shell typos during probing (`--size 320` and entering `image.jpg` as a command) failed immediately and were corrected; neither changed repository/reference files. `test -f image.jpg` confirmed it was present before the final reference-free render.

## Artifact hashes

Before/current source snapshots:

- `work/before/vector_visibility.py`: `ff155bf88fc27a8da550cd34ae9e92a3e0ad54a4e25c23b38d8e3db7574ab20c`
- `work/before/spatial_sketch.py`: `1499d0744dbea2cd84bb7627279bd9f5983ae286b5e94fe36d3766b64e4a0d65`
- `work/before/test_spatial_sketch.py`: `dc079243149864f9e683a69608f2fcc06e716b6ffb9856429fa7122adc1ea19a`

Current reviewed implementation/tests at recovery:

- `scripts/vector_visibility.py`: `6cea919d0c83b1c4ebb9b3ec3379854c910e2758610b449c036c25c9ce8e1ada`
- `scripts/spatial_sketch.py`: `3ee30740672e4c9cbfda0699a1e14d45393b20029e854cdcf0dc847e062c1264`
- `scripts/tests/test_spatial_sketch.py`: `a5689e264aeab8c3e567ecf0418896c4188745867f19aeb32bb709b4a0bba498`
- `scripts/tests/test_vector_visibility.py`: `8977f31fb12e1f9a660f30866bd0ba271e4541f86d29cc091e32cd5a9cd4acd2`

Controlled raster pair:

- Before SVG: `ca25ad71ec0b0834baeeccc0087c5e25554002c95392d73e17166b6a11980df2`
- Before PNG: `735adfd2239443bf8009c1876cdfd5e29ad88ec058488c331f93291bfd4ef2c1`
- After SVG: `137f02dbed08997dd0341b754c7d0bb3ff1ad7776a7660cf9a95f81365bac34f`
- After PNG: `a080bd1835ce50fbdc3c860cb868524729bd51cb7d6b6be0e919496db6a2aefe`

Final diagnostic artifacts:

- `work/visibility_board.py`: `a478e6af8096cd9c83f6f40e7e4ef664623697062486ef75ef04959c08f85aa4`
- `evidence/after/visibility-board.svg`: `f277b8e3abb0ba4d13330fa649e7a03958e3917f2ddd1c8a16efbfe8a05b9d74`
- `evidence/after/visibility-board.png`: `14ec83d13e91781d84a7bac61651a1883e442d7d7f69a6d4e51a0d4233c43187`
- `evidence/after/cases/depth-flip-order.svg`: `ff20783737da99dab490bde2023a8e403f675962e080fd47369bf4b3a45e0edc`
- `evidence/after/cases/depth-flip-order.png`: `78061fa7a347de5317712b7bde1b7cceb3c171b40096db2deddd3c58af6c115e`
- `evidence/after/cases/two-view-strip.svg`: `af33eb278f318c96426134975f65f0545788c7bac9e22664e9970ae2ce6162e6`
- `evidence/after/cases/two-view-strip.png`: `ffdf9a52de1764dceca8bdaa9741e94ded4d3f04b468a5c6b100d8e864866aba`
- `evidence/after/check/draft.png`: `14ec83d13e91781d84a7bac61651a1883e442d7d7f69a6d4e51a0d4233c43187`
- `evidence/after/spatial-sketch.svg` (includes unique camera-scoped IDs): `c6db12fc83a8596c16238ba946221e757c9aa214e801f9ebd2f09c88b4204d67`
- `evidence/after/spatial-sketch.png`: `df9e58c8e1afc023a14101170b7c0b06210eb2e629810ea44977a5475f71afc3`
- `evidence/after/check/report.txt`: `2bcc2888425f43bb27477767000f222b4ae1013ec4126699510341a3bf232185`

## Changed scope and preservation

Implementation changes: `scripts/vector_visibility.py`, `scripts/spatial_sketch.py`, `scripts/tests/test_spatial_sketch.py`, new `scripts/tests/test_vector_visibility.py`. Task evidence/generator/teaching notes are under `.scratch/18-spatial-closeout/{work,evidence}`; the original `spec.md` was not changed. No dependency, figure source, vendor, baseline, `.agents/`, or official-doc edit; no commit/push. Existing unrelated staged vendor/`.gitmodules` changes, docs/STATUS/active-work edits, and `.agents/` were preserved from kickoff.

## Limitations / next step

- This fixes SVG antialias seams only when adjacent visible fills share a component, color, and coordinates. It does not fix geometric gaps, independently diverging tessellation edges, intentional different-color boundaries, or cracks at true component/occlusion edges.
- Depth remains a slow opaque-triangle reference algorithm. Transparent materials, unrestricted intersections/non-manifold surfaces, and production-scale performance are not established. Exact coplanar overlap is intentionally order-sensitive (first declaration wins).
- No independent visual reviewer was run. Use only the image list in `evidence/after/check/report.txt` for a fresh-context review. Parent review/acceptance remains required; no baseline promotion and no finished-art claim.
- Pre-existing user staging remains. No implementation files are staged. Parent can now review the diff and request the independent structural visual gate.
