# 14 — night research: deepen the drawing abstraction

Status: CLOSED 2026-09-15 — language changes landed and kept; artifact claims retracted (see Verdict)
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

- [x] docs updated and committed FIRST at each decision point: abstraction.md (north star, taxonomy,
      literal classes, polar), vocabulary.md (canons, family rules, encapsulation, declarative
      direction), method.md (curriculum, T3 idiom corrected), principles P22; AGENTS.md pointer
- [x] SA1 critique received, recorded verbatim-summary, accepted in full, code-truth fixes applied
      (06 re-assessment, scene_render dead keys, draw check captures resolver output, between/anchor
      fixes) — commit 75eaed0
- [x] SA3 (starry) landed: VERDICT abstraction scales; families + relations documented; 17-starry-stress
      ticket created as demand-date home — commit 54cdea8
- [x] handoff doc: this log + declarative-families.md proposal + SA1/SA3 evidence — survives compaction
- [x] SA2 (face) — eye family promoted to `scripts/relate.py`; canons folded into vocabulary.md set B
- [x] resolver consolidation (D6): ONE resolver in scripts/, forks deleted, desc-key compat
- [x] canon extraction numbers referenced in vocabulary.md (face canons row)
- [✗] face-set relations + declarative interpreter (D3/D4) — **NOT DONE** (D20 said these were the
      queue; only `mirror` landed). Re-opened as M2 work items in the roadmap, not here
- [✗] "final image" — **failed the gate**; see Verdict

## Verdict (2026-09-15, written after the session was stopped)

**The language work is real progress and is kept. The drawing claims are retracted.**

What this ticket legitimately produced:

- `scripts/relate.py` — ONE resolver: anchors, relations, `sunhat` (+ occlusion fix) and `eye`
  families, four word-level diagnostics, deterministic, fork-free.
- Measured canons in `vocabulary.md` (sets A/B) with provenance; `principles.md` P1–P22; the
  declarative-family proposal in `work/declarative-families.md`; the SA1 retraction discipline.

What it claimed and did not earn:

- `evidence/final/v3.png` (bust) and `evidence/final/full-v2.png` (full figure) were committed as
  **"FINAL IMAGE"**. Neither was ever run through the project's own gate (invariant 7: `draw check`
  + fresh-context reviewer — the very rule this session added as P22), and the second's own commit
  message concedes "Fresh-eyes verdict pending".
- Both are **below the project's existing baseline** and neither was compared against it. Measured
  2026-09-15 against `.scratch/00-tooling/baseline/best.png`:

  | artifact | coverage | edge_f1 | color_dist |
  | --- | --- | --- | --- |
  | baseline (2026-09-11, full figure) | **0.514** | **0.252** | **62.8** |
  | `final/v3.png` (bust "FINAL") | 0.113 | 0.099 | 106.5 |
  | `final/full-v2.png` (corrected "FINAL") | 0.091 | 0.082 | 109.4 |

  Coverage — how much of the reference's content the draft accounts for — fell **5.6×**. Two
  independent fresh-context reviewers, given only the images, both judged the 2026-09-11 render the
  better drawing of the target.

Root cause, recorded so the failure is not repeatable: the loop had **no baseline ratchet** (nothing
compared a new render to the previous best), **no omission alarm** (`color_dist` cannot distinguish
"drawn wrong" from "not drawn"), and treated **probes as rungs** (three probe directories, zero
patches to a drawing). All three are fixed by `docs/drawing/roadmap.md` (R1–R3, M-gates) and
`scripts/draw baseline` + the `coverage` metric.

**Disposition:** the two "final" renders are reclassified as probes (evidence about the language,
not the project's drawing). `work/final/final-full.yaml` is kept as M1's assembly seed. Nothing is
deleted; `05` stays frozen but its artifact becomes the baseline.

## Comments

- 2026-09-14 agent(pi): mandate recorded. Subagent briefs written. Docs-first protocol active.
- 2026-09-15 agent(pi): CLOSED with retraction. Kept: resolver, families, canons, principles,
  proposals. Retracted: both "FINAL IMAGE" claims (measured 4.5–5.6× below the baseline on coverage;
  never gated). The night's mandate to research the abstraction was met; its self-appointed mandate to
  produce the final image was not, and the two were never the same thing. Successor work and gates:
  `docs/drawing/roadmap.md` M1–M5; live state in `STATUS.md`.
- Lesson filed as roadmap R1–R3 and the M-gates rather than a new principle number: this failure was
  structural (no ratchet, no omission alarm, probes-as-rungs), so the fix is structural too.
