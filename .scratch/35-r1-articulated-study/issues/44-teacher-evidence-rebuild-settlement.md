# Issue 44 — teacher evidence rebuild settlement

**Owner:** single writer. **Status:** v2 evidence package rebuilt and regression-checked; semantic gate remains NOT RUN / NOT PASS. **Authority:** Main authorized a 20-minute evidence-only consistency repair. No new point/trace, source crop/patch edit, fit, artwork/final-art render, backend/environment/network/vendor/staging/commit, or PASS.

## Scope and disposition

The independent report `.pi/.../teacher-v2-limited-correction-review.md` BLOCKed issue 43's corrected sibling as a current complete evidence delivery: its point/provenance writer still represented LTI2 as pink interior and regenerated the full left-tail centerline as eligible; its reproduction command pointed at the historical writer. The approved whitelist itself was correct. Preserve issue 43's `teacher-only-corrected/` byte-for-byte as historical evidence of the bounded correction, not as current rebuild entry.

Created current package `evidence/A-teacher-reconstruction-v2/teacher-only-corrected-v2/`. One writer definition supplies all 24 point records/locations, trace dispositions and overlay styling; it writes only v2 by default, refuses v1, supports explicit `--out` scratch destinations, rebuilds evidence crop/patches/overlay (not final art), and does not draw withdrawn annotations as accepted colors. The unchanged point set retains all prior accepted/unknown boundaries. LTI2 remains `(104,222)`, unknown for fitting and WITHDRAWN as pink interior; entire `leftward-tail-centerline-visible` including `(116,220)` is withdrawn as source-backed centerline/width/axis; TBE2 remains only limited station/local edge neighborhood, not exact edge; blue identity and DTO2 remain UNKNOWN. Provenance identifies current controlling `fit-correction.md`, rebuilder, test and all actual current package files, excluding only itself to avoid recursive hash. History/lineage cannot restore current roles.

## Revision-bound evidence and commands

Current source SHA-256: `322ad77c0cfd28fa040c625c55c592a54b3052ac4bea61fc31d967d8acff81fb`. Run from repository root:

- `python3 .scratch/35-r1-articulated-study/evidence/A-teacher-reconstruction-v2/teacher-only-corrected-v2/rebuild_teacher_evidence.py --out /tmp/teacher-v2-check1` — PASS, exact source/crop hash, 24 points, 4 regions.
- `python3 .scratch/35-r1-articulated-study/evidence/A-teacher-reconstruction-v2/teacher-only-corrected-v2/rebuild_teacher_evidence.py` — PASS, same checks; output restricted to v2.
- `python3 .scratch/35-r1-articulated-study/evidence/A-teacher-reconstruction-v2/teacher-only-corrected-v2/rebuild_teacher_evidence.py --out /tmp/teacher-v2-check2` — PASS, same checks.
- `python3 .../teacher-only-corrected-v2/rebuild_teacher_evidence.py` — PASS, same checks; final manifest includes final checked code/docs.
- `python3 -B -m pytest -q -p no:cacheprovider .scratch/35-r1-articulated-study/evidence/A-teacher-reconstruction-v2/teacher-only-corrected-v2/tests` — PASS, 2 tests.
- Independent byte/evidence comparison — PASS: v1 pristine crop, every raw point patch and raw region byte-identical in v2; 24 records retained; LTI2 unknown + withdrawn, whole trace withdrawal retained, manifest lists all current files including fit doc/script/tests and excludes itself.

A first draft test run failed two assertions because test wording/index expectations mismatched the existing qualified record text, not because evidence behavior failed. Assertions were corrected to the existing data contract, then the final rebuild and tests passed. No acceptance boundary was weakened.

## Remaining gate

No semantic review was rerun and no semantic PASS is claimed. Current fresh semantic gate and subsequent fit remain pending Main. Original teacher, v1 corrected package, source image, registered crop, fitted art, B and sealed materials were not edited. Only this ticket plus current pointers in STATUS/task-freeze/active-work were updated. Do not use v1 writer as current source.
