# 07 — view-loop: make seeing cheap and reliable

Status: done — agent(pi) 2026-09-14
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

- [x] `draw check` produces the bundle in one invocation, <60s — measured **0.32s** for a 1024² draft
- [x] bundle images each attach successfully: panes ≤600px (whole frame) and ≤256px (regions), always
      exactly 3 regions, grid-ranked by mean colour distance and kept ≥2 cells apart. (The first cut
      ranked regions by connected components, which returned one canvas-sized blob — useless when a
      draft differs globally; grid ranking always yields 3 localized, comparable areas.)
- [x] a fresh-eyes run on the frozen 05 render produced ≥3 actionable findings: it returned **8**, worst
      first, verdict "partly". Its #1 — "no line work; in REF every form is closed by a crisp dark
      outline; in DRAFT those outlines are simply absent" — is the same defect the measurement-based
      diagnosis reached independently. It also flagged the hat's silhouette, the blank pale fields
      where geometry should be, and the "soft rainbow smear" replacing the skirt's hard-edged panels.
- [x] `draw check` refuses to invent a verdict — it emits images + coordinates + the metrics line, and
      `report.txt` states outright that judging is the reviewer's job. It also emits the reviewer
      protocol (fresh context, open question, no leaked intent) so the loop is not left to memory.
- [x] documented in `docs/drawing/method.md` — `check` in the loop and tool sections, the never-self-judge
      guardrail, and the P7 caveat that reviewer *locations* need verifying. Also corrected T1's XDoG
      guidance there, which measurement had falsified.

## Evidence

`.scratch/05-portrait-scene/evidence/check/` — bundle for the frozen render + the fresh-eyes transcript
quoted above (8 findings, verdict "partly").

## Comments

- 2026-09-14 agent(pi): created from the 05 diagnosis (blind iteration was one of the top root causes).
- 2026-09-14 agent(pi): done. Reviewer route that works in this session: `Agent` tool with
  subagent_type `explore` (read-only, can open images). The other delegation tool's `reviewer` agent is
  **not** launchable here — its tool contract needs `read`/`grep`, and this host only offers `find`/`ls`
  to children, so it fails as a lane infrastructure error. Recorded so future sessions do not retry it.
  `explore` reviewers describe what they see reliably and mislabel **where** they saw it (region-1 at
  (768,896) was called "left chest"); the bundle's coordinates are what makes that separable.
