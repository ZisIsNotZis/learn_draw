# WP04 compound-fill / semantic-line repair — final numerical evidence

## Scope and result

One authorized local WP04 renderer/adapter repair. Unchanged: `scripts/vector_visibility.py`, `scripts/articulated_construction.py`, case geometry, support frames, camera, WP03 scene, and artwork anchors. All pre-existing WP04 SVG/PNG/manifest files were backed up and hash-verified before edits: 19 files under [`coordinate-repair-v2/preserved-before/`](../coordinate-repair-v2/preserved-before/), index [`coordinate-repair-v2/preserved-before-sha256.txt`](../coordinate-repair-v2/preserved-before-sha256.txt). This final evidence is in a new v3 revision; the earlier v2 render artifacts are preserved rather than overwritten. Numerical/render evidence only; no image/art acceptance.

Root cause confirmed in actual engine output: `visible_regions()` serializes each disconnected visibility polygon as its own `M … L … Z` subpath (`scripts/vector_visibility.py::_compound_path`). Prior WP04 code removed every `M`, `L`, and `Z`, flattened all coordinates, and closed one polygon, introducing artificial bridge edges. Baseline forearm had 193 native visible subpaths totaling absolute area `0.34544721` projected²; old flattening formed a single loop with absolute shoelace area `0.20619771` projected² (59.69%). The same failure affected all seven baseline B fill groups. The current SVG uses an affine command-preserving transform; its complete path strings match native compound paths after the panel mapping.

## Region/source coordinates and topology

Bounds are `(min-x, min-y, max-x, max-y)`. “Source” is engine projected coordinate space before panel mapping; output is the emitted panel-space path. Isolated counts are single-component native diagnostics; combined counts include actual depth visibility fragmentation.

| Case / component | Combined engine subpaths | Isolated component subpaths | Source bounds | Panel bounds | Panel scale |
| --- | ---: | ---: | --- | --- | ---: |
| A / observed-bodice | 274 | 46 | `(-0.996011, -1.080000, 1.000000, 1.080000)` | `(120.391345, 413.800000, 483.000000, 806.200000)` | 181.666667 |
| A / observed-sleeve | 148 | 38 | `(-1.400000, -0.340000, -0.540000, 0.956303)` | `(47.000000, 436.271586, 203.233333, 671.766667)` | 181.666667 |
| B baseline / upper_arm | 81 | 71 | `(0.250806, 1.948926, 2.178667, 3.157831)` | `(663.152498, 198.826735, 874.486504, 331.348049)` | 109.620991 |
| B baseline / forearm | 193 | 68 | `(1.450489, 1.500489, 2.152004, 3.097451)` | `(794.662927, 205.445606, 871.563720, 380.506169)` | 109.620991 |

The actual SVG path equality and subpath count were checked for all 6 A components and all 7 components in each B baseline/variant/control panel. The combined native/panel area comparison confirms the expected uniform affine scaling. B case component counts are torso `68/63/71`, neck `30/30/30`, head `30/30/30`, upper arm `81/76/75`, forearm `193/201/224`, hand `46/55/58`, prop `30/30/30` (baseline/variant/control subpaths). A panel counts remain bodice `274`, shoulder `38`, sleeve `148`, dark trim `3`, bow `8`, bow knot `10` in both engine and panel SVG.

Hole preservation is covered by an explicit multi-subpath nonzero-fill regression: the clockwise inner ring remains clockwise after transform (signed areas `96, -24, 3` after affine mapping); all three `M/Z` boundaries remain separate. The disconnected fragment test obtains its path from native `visible_regions()`.

## Semantic line depth

Authored points map through each line's owning component `SupportFrame.local_to_world()` and `Camera.project()`. The local adapter reuses the existing `ribbon_drawing` segment/triangle intersection, barycentric, interpolation, depth-plane and tie-policy probe functions; it partitions at triangle boundaries and depth-plane roots, omits hidden portions, and compares against all non-owner support faces regardless of declaration order. No manual visibility cuts, `intentionally visible` tag, panel-clip occlusion, backend change, or mesh-edge strokes were introduced.

Concrete regression: a semantic line on a back support under a nearer triangular occluder yields visible intervals `[0, .375]` and `[.625, 1]` in both owner-first and occluder-first face order. In the actual B renderer, 65 authored line segments were probed per case; segments with hidden portions: baseline `1`, variant `3` (one fully hidden), control `5` (three fully hidden). This proves the new local visibility adapter is active in the current render chain.

## Geometry checks, validation, and fresh review image list

- B baseline, variant, control each passed existing `validate_study_case`; the bounded planar contact/attachment/intersection contract is unchanged. No actual illegal intersection was reported. This is not general volumetric collision proof.
- `.venv/bin/python -m unittest scripts.tests.test_articulated_render_adapter scripts.tests.test_articulated_construction scripts.tests.test_vector_visibility scripts.tests.test_vector_visibility_oracle scripts.tests.test_ribbon_drawing`: **59 passed**. Existing `ResourceWarning`s from `scripts/draw.py` temporary SVG readers appeared during raster helpers.
- `.venv/bin/python -m compileall -q scripts/articulated_line_visibility.py scripts/tests/test_articulated_render_adapter.py .scratch/35-r1-articulated-study/work/render_r1.py`: passed.
- Actual `scripts/draw check` without `--ref` passed for separate A, separate B, and combined sheet through the project renderer.
- Backup verification rechecked source and backup hashes for all 19 original scoped SVG/PNG/manifest files.

New images only (fresh reviewer should receive this list and nothing else):

- `.scratch/35-r1-articulated-study/evidence/coordinate-repair-v3/check-a/draft.png`
- `.scratch/35-r1-articulated-study/evidence/coordinate-repair-v3/check-b/draft.png`
- `.scratch/35-r1-articulated-study/evidence/coordinate-repair-v3/check-sheet/draft.png`

No PNG was opened or visually judged by the implementation worker. WP04 art, independent whole-image depth review, WP05/WP06, and R1 remain unpassed; reviewer gate remains required.

## Final revision hashes

- `scripts/articulated_line_visibility.py`: `d4c11ff1cdb3244203b5dbd4959ec0059a556f89d240cbcf671bbc784d09c390`
- `scripts/tests/test_articulated_render_adapter.py`: `57669a21da1cc9756d57f2835b434e2b82c60aff2812388fb482732973903884`
- `work/render_r1.py`: `42adfe2bf68d975ab6f41f001d7dec4fc00f6a7055fb88d8c12b6c1d3f42b655`
- A/B/sheet SVG: `bf855274342c15bc080065d7898b7a97f73c96fd1837355b75869c9b4db5b5ec`, `c63b8823618cb22a9f776f0427919944dbd0b3c457a17c386966788028c50433`, `4ec25e8200d026103dc717ea1aea296034848b28ec2f47851d69ed923fdd9394`
- A/B/sheet PNG: `6bf19e73e62adae0247791e66a05c80730721de691089cdc73113c2a47038ba4`, `ca9190d1e7fb8a73fb1eff3c5dfd4d373b7af31e90083a9d6a4b4c0feaf5ab4f`, `ef00b9caad40e5d1c2829306f5755cebe253b8660430d2c08a2aff219cb232f2`
- Original preservation index (in v2): `0eb0c89541969c48351e108841c7188d60810a889594ffec5bdb1e6f5450e067`
