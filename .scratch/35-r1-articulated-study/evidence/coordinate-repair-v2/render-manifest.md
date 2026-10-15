# WP04 compound-fill / semantic-line repair — numerical evidence

## Scope and result

One authorized local renderer/adapter repair; no change to `scripts/vector_visibility.py`, `scripts/articulated_construction.py`, case geometry, support frames, camera, or artwork coordinates. Old WP04 SVG/PNG/manifests remain byte-for-byte as backed up and hash-verified before edits (19 source files and copies; index: [`preserved-before-sha256.txt`](preserved-before-sha256.txt)). This is numerical source/render evidence only, not image/art acceptance.

Root cause confirmed: `vector_visibility.visible_regions()` serializes each disconnected visibility polygon as its own `M … L … Z` subpath (`scripts/vector_visibility.py::_compound_path`). The prior WP04 conversion removed every `M`, `L`, and `Z`, gathered all coordinates, and emitted one closed polygon. That connected disconnected fragments with artificial bridge edges. The repaired adapter applies panel coordinates to each absolute `M/L/Z` coordinate while retaining each move, closure, ordering and winding. It does not alter visibility geometry or draw mesh edges.

A concrete pre-fix repro from the unchanged baseline engine output: baseline `forearm` had 193 native visible subpaths, total absolute fragment area `0.34544721` projected²; flattening all vertices into one loop produced absolute shoelace area `0.20619771` projected² (59.69% of fragment area). The same flattening affected all seven baseline component fills. The current transformed SVG has the exact native command-preserving transformed path for every fill component.

## Region/source coordinates and topology

Bounds are `(min-x, min-y, max-x, max-y)`. “Source” coordinates are backend projected coordinates before panel transform; output coordinates are the serialized panel-space SVG path. Independent single-component counts are diagnostic only; combined paths include real depth visibility fragments.

| Case / component | Combined engine subpaths | Isolated component subpaths | Source bounds | Panel bounds | Panel scale |
| --- | ---: | ---: | --- | --- | ---: |
| A / observed-bodice | 274 | 46 | `(-0.996011, -1.080000, 1.000000, 1.080000)` | `(120.391345, 413.800000, 483.000000, 806.200000)` | 181.666667 |
| A / observed-sleeve | 148 | 38 | `(-1.400000, -0.340000, -0.540000, 0.956303)` | `(47.000000, 436.271586, 203.233333, 671.766667)` | 181.666667 |
| B baseline / upper_arm | 81 | 71 | `(0.250806, 1.948926, 2.178667, 3.157831)` | `(663.152498, 198.826735, 874.486504, 331.348049)` | 109.620991 |
| B baseline / forearm | 193 | 68 | `(1.450489, 1.500489, 2.152004, 3.097451)` | `(794.662927, 205.445606, 871.563720, 380.506169)` | 109.620991 |

Serialized output M/Z counts exactly match engine subpath counts: A bodice `274/274`, A sleeve `148/148`, B baseline upper-arm `81/81`, baseline forearm `193/193`; numerical checks compared the complete transformed path strings and fragment areas with the computed panel affine transform. B baseline/variant/control all passed existing `validate_study_case`; geometry, declared contact, attachments, and the bounded planar intersection checks were not changed. No current illegal intersection was reported by those checks. This remains the declared finite support/XY check, not general volumetric collision proof.

Hole preservation is checked with a multi-subpath nonzero-fill regression: the clockwise inner ring remains clockwise after transform (signed areas `96, -24, 3` after affine mapping), and its `M/Z` boundaries are retained. The engine's actual disconnected-fragment path is separately regression-tested through `visible_regions()`.

## Semantic line depth

Authored stroke points are mapped through their owning component's `SupportFrame.local_to_world()` and `Camera.project()`. A renderer-local segment probe splits at projected triangle boundaries and depth-plane roots and applies the same `EPS` / first-declared tie rule as the unchanged fill backend. All non-owner support faces participate, independent of whether their declaration precedes or follows the authored line. Hidden intervals are omitted; no manual cuts, `intentionally visible` switch, panel-clip occlusion, or mesh-edge strokes were introduced.

The concrete regression places a semantic line on a back support under a nearer triangular occluder; expected visible parameter spans are `[0, .375]` and `[.625, 1]` for both owner-first and occluder-first face declaration order. For current authored B strokes, 65 line segments were probed per case; segments with computed hidden portions: baseline `1`, variant `3` (one fully hidden), control `5` (three fully hidden). This verifies that the semantic stroke path is depth-tested in the current engine chain.

## Validation and fresh review image list

- `.venv/bin/python -m unittest scripts.tests.test_articulated_render_adapter scripts.tests.test_articulated_construction scripts.tests.test_vector_visibility scripts.tests.test_vector_visibility_oracle`: **42 passed**. Two pre-existing `ResourceWarning`s from `scripts/draw.py` temporary SVG readers appeared in visibility tests.
- `.venv/bin/python -m compileall -q scripts/articulated_line_visibility.py scripts/tests/test_articulated_render_adapter.py .scratch/35-r1-articulated-study/work/render_r1.py`: passed.
- `scripts/draw check` without `--ref`: A, B, and combined sheet all passed; rendered with actual project engine chain.
- Preservation verification checked every source and backup hash for all 19 archived SVG/PNG/manifest files.

New images only (fresh reviewer should receive this list and nothing else):

- `.scratch/35-r1-articulated-study/evidence/coordinate-repair-v2/check-a/draft.png`
- `.scratch/35-r1-articulated-study/evidence/coordinate-repair-v2/check-b/draft.png`
- `.scratch/35-r1-articulated-study/evidence/coordinate-repair-v2/check-sheet/draft.png`

No PNG was opened or visually judged by the implementation worker. WP04 art, whole-image depth review, WP05/WP06, and R1 remain unpassed; the reviewer gate remains required.

## Revision hashes

- `scripts/articulated_line_visibility.py`: `ee6649e8b560bf8567fae45c58dbbefe87c3ed6629745ddc70720ffe76ab878c`
- `scripts/tests/test_articulated_render_adapter.py`: `57669a21da1cc9756d57f2835b434e2b82c60aff2812388fb482732973903884`
- `work/render_r1.py`: `92bd05267c82ee503085c28c28f802d7f0733aca7ae174e807393cc2ddacfb4e`
- A/B/sheet SVG: `bf855274342c15bc080065d7898b7a97f73c96fd1837355b75869c9b4db5b5ec`, `c63b8823618cb22a9f776f0427919944dbd0b3c457a17c386966788028c50433`, `4ec25e8200d026103dc717ea1aea296034848b28ec2f47851d69ed923fdd9394`
- A/B/sheet PNG: `6bf19e73e62adae0247791e66a05c80730721de691089cdc73113c2a47038ba4`, `ca9190d1e7fb8a73fb1eff3c5dfd4d373b7af31e90083a9d6a4b4c0feaf5ab4f`, `ef00b9caad40e5d1c2829306f5755cebe253b8660430d2c08a2aff219cb232f2`
- Preservation index: `0eb0c89541969c48351e108841c7188d60810a889594ffec5bdb1e6f5450e067`
