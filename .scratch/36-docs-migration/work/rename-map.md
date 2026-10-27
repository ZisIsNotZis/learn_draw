# Rename map of the docs migration

One pass, one commit series. This file exists so a reader who follows a link inside a frozen record
(under `.scratch/`, `inbox/`, `mail/`, `teaching/`) can find where the target went. It is kept as the
pass's record; the retired doc text is in git at `d464eba^`.

| before | after |
| --- | --- |
| `docs/drawing/roadmap.md` | `docs/0_ROADMAP.md` (milestones, gates, contract, current state) |
| `docs/drawing/rubric.md` | `docs/2_GOAL.md` (axes, anchors, thresholds, alarms) + `docs/4_USECASE.md` (how a review is run) |
| `docs/drawing/principles.md` | `docs/3_REQUIREMENT.md` (`P1`–`P40`, unchanged numbers) |
| `docs/drawing/method.md` | `docs/4_USECASE.md` (the loop, judging, delegation) + `docs/9_IMPLEMENTATION.md` (tools, guardrails) + `docs/8_DETAIL.md` (resolver tiers) |
| `docs/drawing/abstraction.md` | `docs/5_PRODUCT.md` (the language) + `docs/7_INTERFACE.md` (traced-data format) + `docs/8_DETAIL.md` (diagnostics) |
| `docs/drawing/vocabulary.md` | `docs/5_PRODUCT.md` (canons, families, directions) |
| `docs/drawing/spatial-model.md` | `docs/6_ARCHITECTURE.md` |
| `docs/drawing/scene-format.md` | `docs/7_INTERFACE.md` (format, nodes, renderer) + `docs/8_DETAIL.md` (generators) |
| `docs/drawing/vendor-learning-map.md` | `docs/2_GOAL.md`'s coverage rule and `docs/3_REQUIREMENT.md`'s source rule; the coverage table itself is curriculum state, kept as `docs/5_PRODUCT.md` §Curriculum coverage |
| `docs/drawing/handoff-3d.md` | deleted — a superseded prescription; its text is in git |
| `docs/drawing/history/roadmap-before-spatial-model.md` | `.scratch/history/roadmap-before-spatial-model.md` (record) |
| `docs/drawing/history/status-before-spatial-model.md` | `.scratch/history/status-before-spatial-model.md` (record) |
| `WORKSPACE.md` | `docs/9_IMPLEMENTATION.md` (environment and gates), file deleted |
| `README.md` | thinned to what-the-repo-is + licensing; its toolchain and invariants moved to `9` and `3` |
| `STATUS.md` | dissolved: state and the next entry in `docs/0_ROADMAP.md`, run narrative stays in `.scratch/35-r1-articulated-study/work/wave-log.md`, the recorded facts in their level files; file deleted |
| `.scratch/active-work.md` | deleted (it was a second state home, and said so itself) |
| `evidence/vendor-smooth-study/`, `evidence/curve-garment-application/` | `.scratch/history/early-studies/` (record) |
| `AGENTS.md` | rewritten: rule overrides and must-knows only, with every operational detail pointed at its `docs/` home |
