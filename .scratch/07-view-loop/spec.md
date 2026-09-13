# 07 — view-loop: make seeing cheap and reliable

Status: ready-for-agent
Blocked by: —

## Issue

The portrait was drawn largely blind. `STATUS.md` records that image attachments returned EMPTY late
in long sessions (3 retries at decreasing sizes), so iteration fell back to pixel probes and ASCII
hue-class maps — and the agent explicitly was told to "never claim to have seen". Nobody looked at
the picture while drawing it. Separately, the *only* visual verdict mechanism (`compare`) produces
large full-frame images that are expensive and hard to read.

## Scope

One command that produces the whole visual feedback bundle for a drawing, sized for a fresh-context
reviewer, plus the rule that visual judgment always happens in a fresh session.

- `scripts/draw check <art> [--ref REF]` → renders, then writes into `evidence/`:
  - a side-by-side at ≤600px per pane (what "does this read?" needs)
  - per-region 2x crops for the 3 worst areas, each ≤512px
  - the metrics line (edge-F1, color distance) as a *breakage alarm only*, never a target
- All images small enough to attach reliably, even late in a session
- Documented rule: the main session never self-judges a render; a fresh-context subagent gets only
  REF + DRAFT with the open question "what is wrong here?" (P7 framing — no leaked intent)

## Acceptance

- [ ] `draw check` produces the bundle in one invocation, <60s
- [ ] bundle images are each ≤600px and each attaches successfully in a fresh subagent session
- [ ] a fresh-eyes run on the frozen 05 render produces ≥3 actionable findings if fed the bundle
- [ ] `draw check` refuses to invent a verdict — it emits images + numbers, no prose judgment
- [ ] documented in `docs/drawing/method.md` (tool usage) and referenced from the exercise loop

## Comments

- 2026-09-14 agent(pi): created from the 05 diagnosis (blind iteration was one of the top root causes).
