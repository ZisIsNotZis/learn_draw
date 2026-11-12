# Observed validation — 2026-11-12

Environment: isolated `.venv`, Python 3.14, numpy 2.5.4, Pillow 13.0.0,
opencv-python-headless 5.0.0.93, PyYAML 6.0.3. Installed Edge rendered through an isolated profile
with explicit GPU disable and device scale 1. No GPU or local model inference was used.

## Mechanical results

- `python -m unittest scripts.tests.test_studio scripts.tests.test_vector_visibility scripts.tests.test_vector_visibility_oracle -v`
  — **36 tests passed** (13 new operation checks, 16 inherited visibility checks, 7 inherited oracle checks).
  This covers selected-side motion, unaffected edge/objects/terminals, opposite correction, invalid
  collapse refusal, stale input/implementation refusal, accept/undo, external-change protection,
  one-sided width, deterministic SVG and depth-order changes inside shared footprints.
- `python -X utf8 scripts/tests/test_scene.py` — **81/81 CPU smoke checks passed**, plus the
  existing wave/strand presence and repeated-render assertions. The contextual CLIP model alarm
  was explicitly skipped, not counted as passed. It is opt-in via `--with-similarity`.
- Current study scene SHA256:
  `8b7c54306fe359d7bbffde5a8504e0e22d23b8a6842a268c685065603f6c3dce`.
- Current implementation SHA256:
  `b42e14ec60747eda5d91e54a2668361bf95c2a8922759263f5d566007a7a6469`.
- Current SVG regenerated exactly from its scene. A second isolated CPU PNG was byte-identical,
  SHA256 `c7afa155402bcb6ae7d97912950c52e27aeaae87f5fe54f063c96be32ba4afd0`.
- Legacy `draw.py check` ran on the current isolated and each final context PNG. Those bundles give
  image lists, never aesthetic verdicts. Portrait-context edge-F1/colour alarms are in `alarms.json`.

## Failures encountered and corrected

- Installed `relate.py` indexed parents[4], which does not exist in a shallow Windows checkout.
  The optional prototype-root fallback now checks depth and existence; sibling imports remain primary.
- Windows Chromium laid out an SVG at a larger minimum viewport than its screenshot. The inherited
  raster-seam test failed with a scaled/clipped image. Explicit wrapper canvas dimensions corrected
  it; the existing positive/negative seam test now passes. Browser profiles are isolated across calls.
- Legacy IO assumed the system text encoding; reads/writes used by draw/relate now declare UTF-8.
- The old smoke suite mixed a GPU-capable contextual model alarm into geometry checks and used fixed
  Unix /tmp names. Model inference is opt-in; portable unique test paths retain the original assertions.
- Sparse recovery omitted required source/numeric fixtures. Only the fitter, its spec/15 traced JSON
  fixtures and the two oracle plans were restored from their tracked blobs in this worktree. No old
  artwork or sealed brief was read/fetched to satisfy the smoke suite.

## Limits

Visual review rejected the hair/portrait integration; see README. The tests cannot establish a good
default hair primitive. Contour validity is sampled; support is planar. Multi-file history writes are
not crash-transactional. The old portrait ratchet was not fetched, changed or promoted, so its frozen
baseline command is not reported as run. Current source-bound operation evidence is `current/`;
intermediate studies preserve compiled SVGs/images and are not current-code reproduction claims.
