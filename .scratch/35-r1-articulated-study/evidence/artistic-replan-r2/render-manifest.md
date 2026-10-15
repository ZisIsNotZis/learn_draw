# Compact grammar repair r2 manifest

Status: scoped repair of issue 14 P1; not visual acceptance or R1 PASS. Prior `artistic-replan-r1` is retained unchanged. r2 source SHA-256 `66fc232d69ab10a0a45de1b609226e84f2ab3f76f8f437ee71b06154b4fd1b93`; test SHA-256 `6cd5986ac69df02fd3988cee9a8342efa99ba8b7d7466b7c5bf053b545313492`.

A `observed-bodice` accepts exactly four semantic point anchors (neckline endpoints and waist endpoints); side/hem/shoulder and Bezier controls derive from measured spans and documented fractions in source. B hand accepts semantic wrist/touch anchors, derives orientation from grip axis and width from axis span, then creates palm/thumb/grouped-finger boundary from normalized stations. No sampling is treated as authoring reduction. A/B visible marks and fill continue through support projection and depth visibility.

Rendered images (for independent visual review only):
- A reviewer list in `check-a/report.txt`: `check-a/side-by-side.png`, `check-a/draft-fullres.png`, `check-a/region-1.png`, `check-a/region-2.png`, `check-a/region-3.png`.
- B: `check-b/draft.png`.
- Combined sheet: `check-sheet/draft.png`.

Hashes: `artwork-a.svg` `838605624fde217d3c3bb5f235e74de760e3b9da034bd4e9eb0cfd2930987ef9`; `artwork-b.svg` `56d484dc01e4aef942343ca5d4169bd99aceb85ad6a7c735f5f24662e84bdd67`; `artwork.svg` `0ae0427c95a3c952dc0d6944319c1d2f699b2819b4b0479390de6521407f787c`; A draft `faeb06fb718ef96aed3ec6c6f6f93229be4db43949ba58c980d53bd5b3994307`; B draft `058f75f51327f08cc56f8c27294a7a8d978faac779b38ff8de50c2d37500a9bc`; sheet `6efc5dd6965cfcb3bc729ecf94026921a78732faf6530afa50b662750f70e20b`.

Tests in `source/test_artistic_grammar.py` run `validate_study_case` on actual replaced B parts in baseline/variant/control, preserve semantic anchor inclusion, successful contact/control gap and variant, generate `component_faces`, invoke `visible_segment_spans` on hand wrist-to-touch line for each case, and test deterministic/reference-independent rendering. This establishes validator and visibility adapter execution, not full visual/depth correctness. The general construction and line-visibility adapter unit suites also pass. The spatial validator's documented geometry checks are XY-footprint attachment/reachability and bounded intersections, not comprehensive 3D solids or artistic contact quality. Tests do not prove expected visible/hidden hand/prop spans at every crossing; WP06 remains open.

Reproduction/check commands used (each completed under 120 seconds):
- `.venv/bin/python .../render_artistic_r2.py --outdir .../artistic-replan-r2/source`
- `cd .../source && PYTHONPATH=/home/z/vibe/learn_draw .../.venv/bin/python -m unittest -v test_artistic_grammar.py` (3 passed)
- `PYTHONPATH=. .venv/bin/python -m unittest -v scripts.tests.test_articulated_construction scripts.tests.test_articulated_render_adapter` (19 passed)
- `scripts/draw check` for artwork-a with `--ref image.jpg`, artwork-b reference-free, and combined artwork reference-free; all generated bundles.

Limitations: no whole-image or readability claim. Other A components (shoulder/sleeve/cuff/trim/bow) retain their existing manually authored contours and were not normalized to compact grammar in this scoped P1 repair; no claim of a whole-renderer coordinate-budget audit. Geometry/depth gates WP05/WP06, independent image review, heldout, integration, and user judgment remain open. No staging or commits were performed; pre-existing staged paths remain untouched.
