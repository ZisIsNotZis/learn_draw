# Exercise 20 — ribbon drawing rule implementation log

## Status at handoff

**Current output includes two narrow export fixes.** A first monolithic full-board attempt exceeded 120 seconds; the parent authorized an incremental cached exporter. After a blind review reported blank/cropped output, the panel-fit x/y offsets were corrected and the old batch preserved under `evidence/before-fit-fix/`. Parent then caught a second defect: ElementTree serialized line-only paths with `ns0:` prefixes that do not render in inline-HTML SVG. Those broken line-only boards/checks are preserved under `evidence/before-line-serialization-fix/`; the exporter now serializes unprefixed SVG tags and verifies browser pixels against direct compilation. No geometry or drawing-rule change occurred. The failed learner remains unchanged and regression-only; no visual perception, transfer, S2 acceptance, figure migration, or baseline promotion is claimed.

The two frozen hypotheses remain exactly those in `work/cases.json`: A is complete depth-visible semantic perimeter ink; B is A plus the same narrow full-local-UV core/border motif on either facing side. The rule is frozen; there was no style search or source refactor in this continuation.

## Frozen inputs and provenance

At startup, repo HEAD was `24693d4`. Protected staged `.gitmodules`/vendor changes and pre-existing dirty S0/S1a/docs work were preserved. No commit, push, install, or new staged file was made.

- Case plan `work/cases.json`: SHA-256 `8a5a320fcb47ce7c38c8b3d605f480cf6a74e77611f831c4d01f002a5b891776`.
- Original case source `.scratch/19-ribbon-family/work/cases.json`: SHA-256 `bd2732b806de26cc2d8a261be68e8f30e21e1f8f8bd5301556d85241a8bc5800`.
- Unchanged learner spec `.scratch/19-ribbon-family/learner/gentle-s-ribbon.json`: SHA-256 `dd995ab1d1cced202a63092263d489597339ae18d2ea761e77408c5b41e8455c`.
- Generator `scripts/ribbon_family.py`: SHA-256 `015ec14ec90da5768dbcdd9486220d3971c55673f0944971ccb3a8a47662bd3e`.
- Visibility source `scripts/vector_visibility.py`: SHA-256 `6cea919d0c83b1c4ebb9b3ec3379854c910e2758610b449c036c25c9ce8e1ada`.
- Current drawing source `scripts/ribbon_drawing.py`: SHA-256 `a3569bf9492ab88a5377a25523acbd93adf32069ac02825f8b370ec45cdba2dc` (only the panel-fit x/y translation changed after the blind review).
- Current dedicated tests `scripts/tests/test_ribbon_drawing.py`: SHA-256 `e121fe29d22217c3cb6e01320bb7fa5dec5a8c74e00de0a485b94a82a2183286` (independent fit/margins, central raster, and cached-line export raster equivalence).
- Current teaching card `teaching/drawing-card.md`: SHA-256 `4d998aa05837ffe8434d9659f83a997ea367c30ede7cb3d79d2bcea061038ee4`.
- Checkpointed export driver `work/build_cached.py`: SHA-256 `5de2d435a0b18c8a69956a5effd25c6a448079a9d3e5c57d7558c5ce9a8d53dc` (default-namespace SVG serialization and browser raster equivalence).
- Post-review fit record `fit-centering-fix.md`: SHA-256 `d143f42ca3d932614e6cbad5ff1fec9edb9962c18ffdcb79ccb84de36560429b`.
- Inline SVG serialization fix: `work/line-only-serialization-fix.md` (SHA-256 `237adae19564f11eca243f6e3bc86b82a1dbd9b7f599495ecbf9fb5070e272e6`) records the browser pixel regression and preserved broken-batch hashes.
- Uniform compiler override: 128 longitudinal intervals; original author `segments` values and case/camera files are read-only inputs. The depth-reversal case derives only `depth=-abs(original depth)`.
- Camera poses are frozen and hashed in `work/cases.json`: front `(0°,0°)`, oblique `(38°,22°)`.
- `work/support-hashes.json` records all eight 128-interval support-mesh hashes; its case plan hash binds it to the frozen input. The un-reversed crossback and card case share a support hash; front and oblique half-twist views share a support hash. No support coordinates were changed.

## Commands and observed results

All long calls were bounded. The initial monolithic board attempt used 120 seconds; the parent later explicitly authorized the incremental cache build with a 900-second cap and each Chromium draw-check stayed within its 180-second bound.

1. Parent-reported current-source focused rerun before this continuation: `scripts.tests.test_ribbon_drawing` — 9 tests passed in 2.457s; parent also reports `git diff --check` passed. The current-source SHA values above match that checkpoint.
2. A malformed combined invocation, `.venv/bin/python -m unittest ... .scratch.19-ribbon-family.work.test_occlusion_probe`, exited with `ValueError: Empty module name`; it was not treated as a test result. The scene script was subsequently run directly.
3. `.venv/bin/python -m unittest scripts.tests.test_ribbon_drawing scripts.tests.test_ribbon_family scripts.tests.test_vector_visibility scripts.tests.test_spatial_sketch -v` — passed, 43 tests in 19.561s. Existing SVG `ResourceWarning`s were emitted by the old renderer tests; tests passed.
4. `.venv/bin/python .scratch/19-ribbon-family/work/test_occlusion_probe.py` — passed, 6 tests in 7.453s.
5. `.venv/bin/python scripts/tests/test_scene.py` — passed 81/81 smoke checks, then printed its five additional successful ribbon/strand/XML checks. A non-fatal OpenCLIP QuickGELU mismatch warning appeared.
6. First support-hash helper invocation omitted `PYTHONPATH=scripts`, failed with `ModuleNotFoundError: ribbon_drawing`, and wrote no hash artifact. Corrected invocation below succeeded.
7. `PYTHONPATH=scripts .venv/bin/python - <<'PY' ... load_case_plan; build each unchanged spec with sampling=128; SHA-256 canonical mesh tuples; write work/support-hashes.json ... PY` — passed; all 8 cases hashed, each with 256 support triangles. Values are recorded in `work/support-hashes.json`.
8. Board reproduction: `PYTHONPATH=scripts .venv/bin/python -u - <<'PY' ... cases,plan=load_case_plan(work/cases.json); print(start); svg,manifest=_board_svg(cases,True,False); write comparison-labelled.svg/manifest ... PY` with timeout 120s — timed out. Last observed stdout was `generating labelled comparison board: 8 frozen geometry/camera cases, 3 columns, 128 intervals`; no progress within the panel loop, no return value, and no board/manifest write. This is a genuine prohibitively slow declared-output operation. It was not retried using a subset or an alternate shortcut.
9. At the first timeout checkpoint, no draw-check command could run because that attempt wrote no boards. This historical status was superseded by the cached exporter, fit-centering rebuild, and inline-SVG serialization rebuild below; the final corrected report image lists are recorded later in this log. `draw check` generates review bundles but supplies no art verdict.

## Initial checkpoint deliverables (before cached export)

At the first continuation checkpoint, only the implementation, nine focused tests, case plan, support hashes, teaching card, and initial log existed. All visual-output gaps from that checkpoint were subsequently addressed by the cached export recorded below; perception and transfer remain parent gates.

## Cached export continuation — full output and verification

The parent measured an individual frozen-crossback rule-B panel at 15.70 seconds and approved an exercise-only cached export driver. `work/build_cached.py` is export orchestration only: immutable `render_panel` produced each source panel once; the driver wrote each SVG/coverage sidecar and a flushed progress row immediately; the four full-size boards were then assembled from those identical cache entries. It does not change support geometry, line/motif algorithms, cases, camera, or sampling.

`work/build-progress.jsonl` records 24/24 compiled panels, all elapsed durations, line-only equivalence, and board completion. Sum of recorded panel compile time was 192.715 seconds; slowest panel was 19.610 seconds. No individual panel failed. The direct line-only equivalence check rebuilt the external-support-card rule-B panel and compared background and all 3,432 named finite-width line paths against the cached colour-panel path extraction; all path XML matched. These strokes already contain the per-triangle depth clipping, so no cover masks/support visibility were lost by omitting colour-fill paths.

Outputs (all 8 frozen cases × control/A/B, with sampling 128):

- `evidence/comparison-labelled.svg` / `.png` (1380×2170)
- `evidence/comparison-unlabelled.svg` / `.png` (1380×2144; contains zero `<text>` elements)
- `evidence/line-only-labelled.svg` / `.png` (1380×2170)
- `evidence/line-only-unlabelled.svg` / `.png` (1380×2144; contains zero `<text>` elements)
- `evidence/cache/` contains all 24 panel SVGs and coverage/hash sidecars.

The four board SVGs were reassembled from the verified cache. All four output SHA-256 values were byte-identical to their first assembled values. One labelled full-resolution board was rendered again through Chromium; its PNG was byte-identical to the initial draw-check draft. No pixels or spatial claims were judged by this worker.

Exact `draw check` image lists from each `report.txt` (the only image in each reference-free bundle):

- `evidence/check/comparison-labelled/report.txt`: `.scratch/20-ribbon-drawing-rule/evidence/check/comparison-labelled/draft.png  -- the drawing`
- `evidence/check/comparison-unlabelled/report.txt`: `.scratch/20-ribbon-drawing-rule/evidence/check/comparison-unlabelled/draft.png  -- the drawing`
- `evidence/check/line-only-labelled/report.txt`: `.scratch/20-ribbon-drawing-rule/evidence/check/line-only-labelled/draft.png  -- the drawing`
- `evidence/check/line-only-unlabelled/report.txt`: `.scratch/20-ribbon-drawing-rule/evidence/check/line-only-unlabelled/draft.png  -- the drawing`

PNG SHA-256: comparison-labelled `c2052322e71da33ab4322abd84ed3af4a62ab37e6dce0091c759f0159eda90fa`; comparison-unlabelled `dcb31261ceeddcfcfbc64d9eb02723475331229f31bcdb2130eeca8af31fc38b`; line-only-labelled `b42286b449ad95797c9bc77d2852c990da8f32e63395896a05b0b05770213e8c`; line-only-unlabelled `45e4132ab817a03aa2d73691c5743d46b0bebb77e79a90d053f782f1711d7092`. A second labelled PNG render matched `c2052322e71da33ab4322abd84ed3af4a62ab37e6dce0091c759f0159eda90fa` byte-for-byte.

Four SVG SHA-256 values are in their manifests and were compared before/after a cached re-export: comparison-labelled `20a106186d5384e48f807ef2f0c7273e1439cf699eb4ce0a7e45abb32ca14ee2`; comparison-unlabelled `1661e53679795c5615ff165c1239c8245a7300d01a900fbb111ce1847e953170`; line-only-labelled `068729f2ae049734053998951811aaf7a75c9024f75c9ba33cce31f238798d23`; line-only-unlabelled `84f30fbfa18aab253306127e3e545a0dcaa03d350452549200f1adb4ce0a51f1`.

Additional missing old suite now run once: `.venv/bin/python -m unittest scripts.tests.test_figure_scaffold -v` — 4 passed in 37.153 seconds. This was read-only S1 figure smoke; no figure source was changed.

## Commands/results for cached export

1. `PYTHONPATH=scripts .venv/bin/python ...` bounded direct equivalence probe at 24 test intervals — passed; 403 cached/direct line paths and ground XML matched with external card included.
2. `.venv/bin/python -m py_compile .scratch/20-ribbon-drawing-rule/work/build_cached.py` — passed.
3. `.venv/bin/python .scratch/20-ribbon-drawing-rule/work/build_cached.py --case-plan .scratch/20-ribbon-drawing-rule/work/cases.json --out-dir .scratch/20-ribbon-drawing-rule/evidence --progress .scratch/20-ribbon-drawing-rule/work/build-progress.jsonl` — completed within explicitly approved 900-second bound; 24 panels compiled, no panel failures, direct line-only equivalence passed, and all four boards assembled. Total recorded panel compute was 192.715 seconds.
4. Same cached-driver command repeated with a 180-second bound — reused 24/24 panels; direct line-only equivalence passed; all four board SVG hashes matched the first assembly byte-for-byte.
5. `.venv/bin/python scripts/draw.py check .scratch/20-ribbon-drawing-rule/evidence/comparison-labelled.svg --outdir .scratch/20-ribbon-drawing-rule/evidence/check/comparison-labelled` — command completed; generated 1380×2170 PNG/report. The check bundle supplies no verdict.
6. `.venv/bin/python scripts/draw.py check .scratch/20-ribbon-drawing-rule/evidence/comparison-unlabelled.svg --outdir .scratch/20-ribbon-drawing-rule/evidence/check/comparison-unlabelled` — command completed; generated 1380×2144 PNG/report. The check bundle supplies no verdict.
7. `.venv/bin/python scripts/draw.py check .scratch/20-ribbon-drawing-rule/evidence/line-only-labelled.svg --outdir .scratch/20-ribbon-drawing-rule/evidence/check/line-only-labelled` — command completed; generated 1380×2170 PNG/report. The check bundle supplies no verdict.
8. `.venv/bin/python scripts/draw.py check .scratch/20-ribbon-drawing-rule/evidence/line-only-unlabelled.svg --outdir .scratch/20-ribbon-drawing-rule/evidence/check/line-only-unlabelled` — command completed; generated 1380×2144 PNG/report. The check bundle supplies no verdict.
9. `.venv/bin/python` helper calling `draw.render(comparison-labelled.svg, evidence/determinism/comparison-labelled-repeat.png)` followed by `cmp` — passed; initial and repeated PNG hashes are identical.
10. `.venv/bin/python -m unittest scripts.tests.test_figure_scaffold -v` — 4 passed in 37.153 seconds.
11. Final integrity helper checked all four manifests contain 24 unique case/rule panes, all associated PNG/check reports exist, and both unlabelled SVGs have no `<text>` elements. A streaming XML pass found 128,234 unique IDs in each colour board and 128,155 in each line-only board. `git diff --check` passed.

Prior validation remains recorded above. After the fit correction, the affected combined suite was rerun: 45 ribbon drawing/family, vector-visibility, and spatial-sketch tests passed in 20.119 seconds, including the new independent placement and raster assertions. Existing scene/probe/figure suites did not receive source edits.

## Acceptance boundary

The two candidate rules and all required fixed cases/views are present in regenerated boards. The case/spec/camera/support hashes remain bound by `work/cases.json`, `work/support-hashes.json`, per-panel cache metadata, and board manifests. Parent still owns independent image-only review and verification of continuity/two-sided/over-under observations against provenance. The prior blind review judged the pre-fix boards invalid because of placement; it is not evidence of a line-rule failure. No perception success, fresh transfer, or S2 promotion is asserted. Do not use the unchanged failed learner rendering as an unaided pass.

## Post-review fit correction

The fresh reviewer observed that the initial board batch was blank/cropped. Parent identified and approved an exact panel-fit offset fix; no drawing rule, geometry, case, camera, or sampling changed. `scripts/ribbon_drawing.py::_fit_points` now computes both translations with the final `/2` over the whole numerator: `ox=(W-s(min_x+max_x))/2`, `oy=(H+s(min_y+max_y))/2`. `teaching/drawing-card.md` records this fit convention. The pre-fix boards/check bundles and hash list are retained under `evidence/before-fit-fix/`; see `fit-centering-fix.md` for their hash, corrected hashes, and exact checks.

Independent fit/margin assertions cover all 8 frozen specs in both frozen cameras and include support-card corners; a Chromium central-viewport nonempty check supplements the geometric oracle. A browser raster test now compares cached line-only extraction with direct `render_panel(line_only=True)` for the external-card case. The affected combined command `.venv/bin/python -m unittest scripts.tests.test_ribbon_drawing scripts.tests.test_ribbon_family scripts.tests.test_vector_visibility scripts.tests.test_spatial_sketch -v` passed 46 tests in 24.449s. The fit-corrected renderer SHA `a3569bf9492ab88a5377a25523acbd93adf32069ac02825f8b370ec45cdba2dc` and all valid current panel caches remain unchanged. The export-only namespace fix reused all 24 panels and reassembled every board; no `ns0:` tags remain. Direct/export 442×255 external-card raster equality had 0 mismatches and 2,551 non-background pixels. The corrected line-only-unlabelled board has 108 exact authored-ink-color pixels. The four draw-check commands completed and generated reports/drafts; they carry no verdict. The labelled PNG determinism rerender remained byte-identical. `work/support-hashes.json` matches cache metadata for every case and rule. Pre-serialization line-only evidence is preserved under `evidence/before-line-serialization-fix/` and has a hash manifest. The earlier code-review report applies to the fit-corrected but pre-serialization exporter; focused parent code and fresh blind perception reviews of the current revision remain pending.

## Inline SVG line-only serialization correction

A second parent review found that ElementTree's generated `ns0:` prefix produced tags not recognized as SVG by Chromium's inline-HTML parser. The prior line-only PNGs were background-only; this was a serializer defect, not absent line geometry. Those two boards and check bundles are preserved at `evidence/before-line-serialization-fix/` with their original hashes. The exercise exporter now registers the default SVG namespace and rejects prefixed output; it reuses the existing 24 fit-corrected panel caches and serializes only their already-depth-clipped semantic ink polygons plus the ground. All four declared boards were reassembled and the four draw-check commands were rerun; command completion is not an art verdict.

Direct compiler versus extracted cached line-only output for the external-card rule-B panel was rasterized in Chromium at identical 442×255 dimensions: byte/pixel arrays match (0 mismatch pixels), with 2,551 non-background pixels. The persistent regression `test_cached_line_only_export_raster_matches_direct_external_card` checks the direct compiler and cached/export serializer at 24 test intervals; the build exporter repeats the same browser equivalence at frozen 128 intervals. The full unlabelled line-only PNG contains 108 exact `#253746` ink-color pixels. The corrected line-only board hashes and prior broken-batch hashes are recorded in `line-only-serialization-fix.md`.
