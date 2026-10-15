# R1 research-lane recovery evidence

## Objective and boundaries

Record only recovery evidence for failed native research workflow `0a9cb071-4108-42dd-9362-375091f11ec3`, child `afe394ea-c6ed-4d35-b4e9-0c5f4586fd66`. This is an infrastructure/tool-availability failure, not a completed source investigation and not evidence that no suitable reference exists. Do not treat it as license/pose clearance. Sealed holdout was not inspected. No cleanup, staging, commit, runtime/profile changes, or alternate agent CLI were used.

## Run and actual partial artifacts

Researcher metadata records `exitCode: 1` and error: requested unavailable child tools `web_search`, `fetch_content`, `get_search_content`, `source_check`; tools are strict-allowlisted and unavailable extensions are not loaded by listing names. Transcript shows native launch failed at 2026-10-10T09:11:05Z before research calls. The later output report write succeeded at 09:11:38Z, and child final response at 09:11:41Z; those do not make the failed workflow successful.

Actual output directory: `/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/0a9cb071-4108-42dd-9362-375091f11ec3/r1/` contains:
- `cleared-gesture-source.md`: explicitly says no candidate selected, no sources inspected, no clearance; only missing-evidence and bounded retry recommendation. Metadata lists it as the only changed file and says no repository files changed.
- `cleared-reference-construction.md`: exists and is 816 bytes. Attempts to inspect it were blocked by the same runtime launch/tool error; content and provenance are therefore unaudited and it must not be relied on as research evidence.

The child metadata/claim is run evidence, not an independent pre/post repository baseline. These outputs are external workflow artifacts, not repository modifications.

## Repository boundary and baseline observed

At observation, branch `master`, tracking `origin/master`; no ahead/behind marker was shown. Existing staged entries: added `.gitmodules`, `vendor/huashu-art-motion`, `vendor/huashu-design`. Existing unstaged tracked modifications: `.scratch/active-work.md`, `STATUS.md`, `docs/drawing/{method.md,principles.md,roadmap.md,spatial-model.md}`, `scripts/figure_scaffold.py`, `scripts/spatial_sketch.py`, their two named tests, and `scripts/vector_visibility.py`. Many pre-existing untracked paths were also present, including `.scratch/18...` through `.scratch/35-r1-articulated-study/`, `docs/drawing/vendor-learning-map.md`, and assorted scripts/tests. These changes are not attributed to the failed run; preserve them. Full status/diff was observed but not used to infer authorship.

The failed run's transcript shows no repository reads/writes and metadata says only external report output; thus no evidence it changed R1 public repository files. However, no clean pre-run git snapshot was available, and `.scratch/35-r1-articulated-study/` plus the task docs were already untracked at observation, so older provenance and exact origin of their content cannot be established here.

## Partial snapshot

Safe-scope text snapshot at `.scratch/35-r1-articulated-study/evidence/partial-diff-snapshot.txt`, SHA-256 `49dfcf98cb912a4a958772136eaf8205bb7a80898dff8173bdc60f4dbe02d586`. It captures current untracked public R1 spec, tickets, method card, task-freeze, and `docs/drawing/vendor-learning-map.md` relative to an empty-file baseline; excludes sealed prompt and binary reference images. This is a state snapshot, **not the diff caused by this run** and does not establish authorship/timing.

## Retry handoff

Retry only after repairing/confirming child provider registration and strict allowlist for all four requested research tools. Verify actual availability before launch; do not claim the original run searched. Keep original bounded six-candidate/20-minute source and license verification scope, avoid sealed material and local-data uploads, and report exact source-page/license/pose evidence or explicit no-match after an actual bounded search. Preserve the observed dirty/staged baseline; do not stage, clean, or overwrite prior work.
