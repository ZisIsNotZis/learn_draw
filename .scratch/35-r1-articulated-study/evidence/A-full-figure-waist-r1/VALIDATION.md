# Validation and provenance

## Worker actual executions

Interpreter: D:/vibe/learn_draw/repair/cpu-venv/Scripts/python.exe, Python 3.14.10.
Dependencies used: numpy 2.5.4, Pillow 13.0.0. CPU rendering: Edge headless,
explicit --disable-gpu; no GPU processes/reservations launched by worker.

- 3 focused tests: passed, 2026-11-12 09:42:58 (0.186 seconds).
- 9 inherited full-figure tests: passed, 09:50:41–09:52:16 process, 94.186 seconds.
- Total: **12 mechanical tests passed** in separate invocations.
- Focused old/new check proves baseline does NOT satisfy same-material/no-internal-
  section-mark semantics and candidate does; geometry/depth remain exactly unchanged.
- Repeated SVG output byte-identical. Repeated CPU-rendered PNG byte-identical.
- Recovered scripts/articulated_construction.py and scripts/vector_visibility.py each
  exactly equal baseline commit blobs (no-lazy-fetch comparison, 09:51:09).

Run with the interpreter above from this package:

```
python tests/test_waist_continuity.py
python -m unittest discover -s tests -p test_full_figure.py
python reproduce.py
python manifest.py --check
```

## Manager independent executions (not worker assertions of independence)

Manager reported process evidence 2026-11-12 09:50:01 and 09:50:15:
three waist tests passed independently, and all 10 source/parts/*.py files compared
byte-for-byte with HEAD baseline via no-lazy git show (not just copied baseline).

## Image comparison evidence

Original supplied PNG versus rebuilt baseline: 54 differing pixels of 1,048,576,
maximum channel delta 11, mean absolute channel delta 0.0000782013; no delta >32.
Near-identical reproduction, not byte/absolute pixel equivalence. Historical SVG hash
differs; cause unverified, no claim of equality. Candidate vs baseline changes 1834
pixels in [613,625,751,664), all other pixels unchanged. Metrics diagnose change
scope, not aesthetic quality. Independent visual observations are in REVIEW.md.

No overall art pass, no volume/structural repair, no human acceptance, and no baseline
promotion claimed. No sealed brief access, old-package writes, global environment edits,
GPU work, unrelated-file restoration, commits or pushes performed by this worker.
