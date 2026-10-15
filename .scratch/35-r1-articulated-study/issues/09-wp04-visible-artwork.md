# Ticket — WP04 visible artwork (bounded implementation)

## Interpretation, migration and ownership

WP04 owns only `work/artwork.svg`, `work/render_r1.py`, its generated image/check evidence, and this ticket. WP03's `work/scene.yaml` and geometry API are frozen; no geometry edits. WP01 migration used: semantic IK shoulder–elbow–wrist and smooth taper generate sleeve silhouettes, while line/art decisions stay separate from depth geometry. A is limited to the frozen visible shoulder/upper-torso garment features in task-freeze; no arm/hand pose is inferred. B is an original clothed bust, bent arm, authored palm/finger marks and prop contact; baseline, frozen target/proportion variant, and labeled short-control. No Huashu appearance/coordinates or sealed heldout access.

One bounded construction hypothesis: build semantic depth-backed fills from actual `visible_scene_regions`, then author compact semantic art strokes/highlights separately; compose a single readable A panel and three matched B panels. No path visibility cuts or pixel metric tuning. Render/reference engine receives no image pixels. Finite budget: one implementation/validation round; if not independently judged, leave visual gate blocked rather than appearance-patch indefinitely. No staging/commit and preserve all pre-existing work.

## Interfaces inspected

`build_study_case(case)`, `validate_study_case`, `visible_scene_regions`, `Camera`, `Component`, `Point`, `SupportFrame` in `scripts/articulated_construction.py`; `visible_regions` depth-fragment backend in `scripts/vector_visibility.py`. `work/scene.yaml` is the public WP03 fixture and declares support frames/world projection/depth clipping. Actual visibility is calculated from mapped 3D vertices and camera-projected depth; the WP03 API is not modified.

## Evidence state / bounded result

Created `work/render_r1.py`; it outputs independent A and B SVGs plus the combined SVG sheet. All semantic fills are converted through WP03's `visible_scene_regions`; line art marks are separately authored rather than inferred from every mesh edge. A is limited to observed-garment study language and contains no hand. B has baseline, frozen variant and explicitly labeled control; prop/hand art marks remain compact and no geometry API was altered. Render output and reproduction are documented in `evidence/wp04-render-manifest.md`.

Commands and results: `.venv/bin/python .scratch/35-r1-articulated-study/work/render_r1.py` passed; all three `scripts/draw check ... --outdir ...` commands passed without `--ref`; `.venv/bin/python -m unittest scripts.tests.test_articulated_construction` passed (14 tests); `git diff --check -- <owned paths>` passed. Rendered PNGs: `evidence/check-a/draft.png`, `evidence/check-b/draft.png`, `evidence/check-sheet/draft.png`; each corresponding `report.txt` lists only its own drawing as reviewer input. Engine version and PNG/SVG hashes are in the manifest. The geometry test is existing WP03 evidence, not a new WP04 test.

No qualified fresh visual reviewer has assessed these outputs in this work package. Accordingly WP04's visual/art gate and R1 remain BLOCKED pending independent fresh review; do not infer image quality from successful rendering or geometry validation. No heldout access. No scene/interface edits. Pre-existing staged `.gitmodules` and vendor entries were untouched; this task staged no files.
