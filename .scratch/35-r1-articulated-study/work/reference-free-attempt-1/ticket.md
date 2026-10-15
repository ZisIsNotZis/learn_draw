# R1 creator attempt — ticket

- Authorization: Main released exactly one fresh, text-only creator attempt. This work is limited to original drawing construction and technical self-evidence; no learner, evaluator, scorer, or task-custody role.
- Isolation: only the released brief and the two authorized public method/API cards were inputs. No reference image, prior case source/parameters, old answer/board, or other sealed material was accessed. The artwork was not viewed by its creator.
- Input provenance: `input-provenance.txt` records the three authorized input SHA-256 values.
- Budget: one attempt within the original 120-minute hard limit; recovery respected the original UTC deadline (no extension). Commands capped below 120 seconds. No second author or image-feedback iteration.
- Allowed implementation surface: generic support-frame, camera, point/component, IK, triangulation, visibility, and semantic-line APIs. No case-builder/preset/render source reuse.
- Commands/results:
  - Initial `py_compile` passed. First generation-plus-suite command generated SVG, then hit the 120-second tool timeout during tests; its partial fail is preserved at `recovery-snapshot/original-failure.txt`.
  - Isolated authored-point test initially failed because the modified semantic mark had no visible interval. An API-only interval probe verified that the tested locations were occluded; source coordinates were adjusted within the same attempt, with no image inspection or external feedback.
  - A later exact-tuple contact assertion caught only IEEE-754 rounding on coincident world points. The test now uses Euclidean distance `<1e-8`, matching the unchanged source contact guard; a deliberately displaced contact remains a negative-control failure.
  - Added bounded memoization for identical immutable visibility and semantic-line queries; every query retains the full face set/occluders.
  - Final compile and source generation passed; all 5 self-tests passed in 33.599 seconds.
  - `scripts/draw render ... --size 600x760` produced `artwork.png`.
  - `scripts/draw check ...` ran with `--ref` omitted and emitted `report/check/report.txt`; its image list names `report/check/draft.png`.
- Artifacts: `source.py`, `test_source.py`, `artwork.svg`, `artwork.png`, `report/check/`, `manifest.json`, `input-provenance.txt`; original six-file recovery snapshot in `recovery-snapshot/`.
- Unknowns: independent actual-image review and all artistic-quality judgments are pending. This attempt claims neither old worksheet/transfer qualification nor R1 PASS. No independent reviewer was dispatched by this creator.
- Repository state: existing staged/dirty work was left intact; this attempt staged and committed nothing.
