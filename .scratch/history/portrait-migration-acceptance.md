# Historical — the portrait migration acceptance criteria

A record, copied out of the retired `docs/drawing/scene-format.md`. Not a contract: it was superseded
as a target by the L1–L6 exercise ladder after that exercise was frozen. Its criterion 3 is the one
part that survived as a standing test, and it now lives in `docs/9_IMPLEMENTATION.md`.

## Migration acceptance (portrait)

Historical record. Superseded as a target by the L1–L6 ladder (`.scratch/08-bust` … `13-assembly`)
after that exercise was frozen; kept because criterion 3 — "a parameter change re-renders the intended
change and nothing else" — remains the standing test for object-level iteration, and `13-assembly`
re-states it as an acceptance criterion.

1. Scene render vs v20 render: every zone's color distance within +15% of v20's (no regression), overall ≤ 65.
2. Node count ≤ ~80 for the whole portrait (vs ~150 paths).
3. A parameter change demo: adjust `flower-1 curl` 0.4→0.7 and `skirt` poly by moving 2 points — re-render shows the intended change without touching anything else (proves object-level iteration).
4. All probe scripts (pixel checks) unchanged and passing.
