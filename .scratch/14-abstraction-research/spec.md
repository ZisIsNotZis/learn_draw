# 14 — night research: deepen the drawing abstraction

Status: claimed — agent(pi), unsupervised research run authorized by user 2026-09-14
Blocked by: —

## Mandate (user directive, verbatim intent — recorded 2026-09-14)

- User authorizes **fully unsupervised autonomous research** on the drawing abstraction for one night
  ("until I come back tomorrow"). Agent is leader / decision-maker / orchestrator for subagents.
- **Keep docs up to date FIRST (SSOT)** at all times — in case auto-compaction happens and the session
  forgets. Every durable decision lands in `docs/` + a commit before moving on.
- Endorse deepseek v4 pro's analysis: work in three levels — **anchors / relations / vocabulary**.
- Brainstorm a lot. Abstract **upward**: humans do not talk or think in coordinates at all.
- Let subagents do the work while the leader keeps mental space clean and critical; spawn checkers/helpers.

## Research questions

1. What does the abstraction need to be for a *face* (L1 hardest part)? For a *complex scene*
   (Starry Night is the stated end-goal complexity test)?
2. What relations are missing (inside/contact/align/junction/flow/negative-space)?
3. What should the **vocabulary** be — object families with drawing-sane structure + **canons**
   (proportion knowledge: eye at half head height, spacing = one eye width...)?
4. How does the **teacher phase** work exactly: reference → measure → extract canon parameters →
   close image → re-instantiate from params (the "scene file = parameter vector in canon space" idea)?
5. Does the abstraction hold on Starry Night (swirl/glow/flame/village/hill), and what new
   families/relations does it demand?
6. Curriculum: do rungs 08–13 actually lead to drawing without a reference?

## Experiments (delegated, parallel)

- **SA1 (design critique, read-only)** — adversarial review of the docs + prototype as a fresh agent
  would meet them. Findings worst-first.
- **SA2 (face prototype)** — `eye` vocabulary family + relational face spec, iterated to "reads as a
  face"; measures anime canons from the reference; reports abstraction gaps for faces.
- **SA3 (starry-night probe)** — parameter-only, reference-free render evoking Starry Night; reports
  which new generator families / relations are needed.

## Leader work in parallel

- Canon extraction from `image.jpg` (eye position/size/spacing as fractions of head).
- Design docs: relation taxonomy, canon concept, vocabulary roadmap, curriculum map.
- Integration of SA reports, decisions, docs-first commits, handoff state.

## Acceptance

- [ ] docs updated and committed FIRST at each decision point (abstraction.md, new vocabulary/curriculum
      content, AGENTS.md pointers if invariants change)
- [ ] face family proven or failed-with-reasons; starry-night probe result recorded
- [ ] canon extraction numbers in docs or ticket
- [ ] handoff doc: what was decided, what's next, open questions — so tomorrow resumes cleanly
- [ ] every subagent deliverable committed in this ticket's `work/` + `evidence/`

## Comments

- 2026-09-14 agent(pi): mandate recorded. Subagent briefs written. Docs-first protocol active.
