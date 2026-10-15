# S1a teaching artifact log

## Review disposition

- Independent review (criterion 3, P2; review feedback on `.scratch/31-s1a-teaching-artifact/spec.md`, “Preselected challenge and variation”): requested a stated limitation for the bend variation.
- Fix: clarified that bend demonstrates parameter-to-route mapping, while the selected crossing carries the depth/communication limitation already evidenced in the artifact. No evidence or prior record changed.

One bounded pass, per `spec.md`. No implementation changes, new rule hypotheses, learner run, or visual tuning. Review required independently; this log is writer self-proof only.

## Evidence

- `spec.md` records pre-change interpretation/scope/acceptance plan and links reused source, tests and frozen exercise evidence.
- Contrast is grounded in Exercise 19's outcome plus Exercise 20's card/outcome; awkward crossback and bend-only variation are preselected cases from Exercise 19's case plan. Exercise 21's support-card rationale/limits are linked, not restated as a second invented rule.
- All 14 local Markdown links in `spec.md` resolve.
- Transfer remains UNRUN; no formal S1a readability/transfer claim.

## Commands

- `.venv/bin/python -m unittest scripts.tests.test_ribbon_family` — passed, 17 tests (7.706 s). Existing `draw.py` unclosed-file ResourceWarnings appeared; suite passed.
- `.venv/bin/python -m unittest scripts.tests.test_vector_visibility` — passed, 16 tests (1.119 s). Existing `draw.py` unclosed-file ResourceWarnings appeared; suite passed.
- `.venv/bin/python scripts/ribbon_family.py render .scratch/19-ribbon-family/work/teaching-example.json --name oblique --yaw 38 --pitch 22 -o /tmp/s1a-teaching-example.svg` — passed; SVG and PNG existed and were nonempty. Temporary outputs outside the exercise record.
- Python local-link check over `spec.md` — passed, checked 14 links, missing 0.
- `git status --short` — observed pre-existing staged `.gitmodules` and vendor entries; no staging operation performed. Preserve these unrelated staged files.
