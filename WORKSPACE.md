# WORKSPACE — machine-local facts for this project

Coordination mode: **M2 (remote)** — set 2026-09-15 on explicit user instruction.

Reason: the user asked for the repository to be public at `zisisnotzis/learn_draw`, so the baseline
(`.scratch/00-tooling/baseline/`) and the ticket statuses are now a *shared* floor and shared state
rather than local-only. `docs/policy/remote-coordination.md` is not present in this repository; the
policy core inlined in the session prompt applies, and per S5 nothing is blocked for lack of it.

Remote: `origin` → `git@github.com:ZisIsNotZis/learn_draw.git` (public, AGPL-3.0, default `master`).

## Gate commands

Run before any commit that touches code or a drawing. Record each command **and its observed
result** in the ticket / commit message (policy R-REP.4).

| gate | command | passes when |
| --- | --- | --- |
| smoke tests | `.venv/bin/python scripts/tests/test_scene.py` | `N/N smoke tests passed`, no `FAIL` |
| ratchet floor | `scripts/draw check .scratch/00-tooling/baseline/best.png --ref image.jpg` | `vs recorded best:` shows all deltas `+0.000` |
| determinism | render the same spec twice, compare `sha256` | identical |

Milestone-specific gates (G1–G6) are owned by `docs/drawing/roadmap.md`; the rows above are the
subset that applies to every commit.

## Notes

- Policy docs (`docs/policy/…`) are not vendored here; the policy core ships with the session.
- Shared state (docs, tickets, the recorded baseline) lands on `master`. Concurrent writers use
  `git worktree`, one writer per tree.
- The reference imagery is third-party study material and is not covered by the AGPL grant — see
  `README.md` → Licensing.
