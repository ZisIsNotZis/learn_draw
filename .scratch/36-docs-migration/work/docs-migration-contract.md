# Docs migration — the contract every writer of this pass works from

Owner of the contract: the project manager (`learn_draw`). This document is a plan for one pass; it is
not a fact document, and it is deleted with the rest of `.scratch/36-docs-migration/` once the pass is
landed and reviewed.

## Why

The doc base does not obey the rule it is supposed to practice: no level numbering (`docs/drawing/`
is one flat pile of nine topic files), no provenance zoning, dates inside statements, run narrative
written as fact, and the same fact stated in several places (`STATUS.md`, `docs/drawing/roadmap.md`,
`.scratch/active-work.md`, package READMEs). A newcomer cannot tell which file owns what, and the
duplicates drift — `.scratch/active-work.md` records one such drift already.

## The rule being migrated to (short form)

1. `docs/<N>_<NAME>.md`, one file per level; lower N is closer to purpose and higher priority.
2. Inside each file the top-level zones are `EXPLICIT` (the person proposed it or rephrased it),
   `CONFIRMED` (the person agreed without rephrasing), `INFERRED` (we inferred it), in that order.
3. One home per meaning. A fact is stated once and pointed at from everywhere else, by name.
4. A doc states what is true. No dates, no "round N", no "this session", no diary, no version history.
   Records (logs, reviews, run evidence) are not docs and keep their dates — that is their job.
5. Every doc opens by naming what it owns and what it does not, with a pointer for each thing it does
   not own.
6. Keep every existing referent: `P1`–`P40`, `R1a`, `R1b`, `M2`–`M4`, `T1`–`T7`, package and study
   names, gate names. This migration renames files, never concepts.

## Target tree, and what each file owns

| file | owns | does not own |
| --- | --- | --- |
| `docs/0_STAGING.md` | the unfiled-fact buffer | anything already filed |
| `docs/0_ROADMAP.md` | milestones and their promises, gates, workpackage contract, current state, the next entry | why the work matters, what good means |
| `docs/1_PROBLEM.md` | why programmatic drawing at all: the pain, the scenario, who it is for, what the reference is for | goals, features |
| `docs/2_GOAL.md` | what success means: the four acceptance questions, the rubric's axes and thresholds, alarms vs gates, milestone-is-an-artwork rule | how a review is run, how anything is built |
| `docs/3_REQUIREMENT.md` | the binding rules and constraints: `P1`–`P40`, the project invariants | how they are implemented, how they were discovered |
| `docs/4_USECASE.md` | who does what: the drawing loop, the review protocol, the person's judgement gate, delegation and harness limits as they shape a flow | commands, file layout |
| `docs/5_PRODUCT.md` | what the author can express and the decisions behind it: the relational language, the vocabulary and canons, adopted and rejected design directions, scope decisions | the compiled format, the algorithms |
| `docs/6_ARCHITECTURE.md` | subsystem boundaries, support surfaces, the visibility principle, open design choices | formats, algorithms, commands |
| `docs/7_INTERFACE.md` | contracts: compiled node format, spec fields that cross a boundary, traced-data format, renderer contract, diagnostic output | language rationale, internals |
| `docs/8_DETAIL.md` | module-internal algorithms and data: relation resolution, materialization, visibility clipping, generators, coordinate conventions | anything a second module depends on |
| `docs/9_IMPLEMENTATION.md` | environment, commands, gates to run, testing and build, determinism, where the record areas live, machine-local facts | product decisions |

`docs/drawing/` ceases to exist. `docs/drawing/history/*.md` and `.scratch/active-work.md` are
records and move into the records area; `docs/drawing/handoff-3d.md` is a superseded prescription and
is deleted, its text recoverable from git.

## Section-level allocation (nothing may be orphaned)

- `docs/1_PROBLEM.md` ← `README.md` header and §Where this project is right now (the *why* half only),
  the person's own statement of what works and what he wants next, `work/a-art-direction-brief.md`'s
  framing, `README.md` §Licensing (as the constraint on what may be shown).
- `docs/2_GOAL.md` ← `roadmap.md` §Product goal and invariants, `rubric.md` §Part I (the six axes and
  their anchors), §How the scores are used, the alarm gates named there.
- `docs/3_REQUIREMENT.md` ← `principles.md` in full (`P1`–`P40`), `README.md` §Invariants in one
  breath, `AGENTS.md` invariant rules 1–8 by reference (not copied).
- `docs/4_USECASE.md` ← `method.md` §Current learning unit, §Current spatial learning loop, §Legacy 2D
  loop, §The loop, §Judging, §Running the loop by delegation; `rubric.md` §How to run a rubric review,
  §What the reviewer is given, §Part II; the presentation-and-judgement flow.
- `docs/5_PRODUCT.md` ← `abstraction.md` in full except its CLI/tool-usage paragraphs; `vocabulary.md`
  in full; the scope decisions and their rejected branches.
- `docs/6_ARCHITECTURE.md` ← `spatial-model.md` §Goal and boundary, §Representations and
  responsibilities, §Minimum scene schema, §Open design choices. Its §Historical S0/S1 section is a
  record, not architecture: it goes to the records area.
- `docs/7_INTERFACE.md` ← `scene-format.md` §File format, §Layers & occlusion, §Node types, §Renderer
  contract, §Explainability contract; `abstraction.md` §Materializing a teacher measurement (the traced
  JSON fields and their provenance); `scene-format.md` §Migration acceptance is a record, not a
  contract.
- `docs/8_DETAIL.md` ← `scene-format.md` §Generators (`wave`, `strands`, `ring`); `method.md`
  §Historical legacy 2D resolver tier ladder; `abstraction.md` §Diagnostics (what the engine prints and
  how to read it) — pointer only if `7` owns the field list; the coordinate/transform conventions.
- `docs/9_IMPLEMENTATION.md` ← `WORKSPACE.md` in full; `method.md` §Guardrails, §Legacy resolver tool
  usage, §Legacy resolver SVG/CSS output notes; `README.md` §Current toolchain, §Running it;
  `AGENTS.md` §Layout and §Command cheat sheet; the baseline/ratchet procedure; the record-area layout.
- `docs/0_ROADMAP.md` ← `roadmap.md` §Milestone path, §Work-package and autonomy contract,
  §Historical mapping and current state (current-state half only); the current advance, the open
  gates, and the one decision standing before the person. Written by the integrator, after all level
  files land.

## How to write a file

- First line: `# <N>_<NAME> — <what this file owns, one line>`.
- Then `# EXPLICIT`, `# CONFIRMED`, `# INFERRED` as the only H1s, in that order, topics as `##` inside
  them. Omit a zone whose content is empty; never reorder.
- Zone by what the source says about provenance, and never upgrade it: a fact is `EXPLICIT` only where
  the source text marks it as the person's words or direction ("user directive", "user correction",
  "user insight", "the person's direction"), `CONFIRMED` only where the source says the person agreed,
  and `INFERRED` otherwise. An empty zone is honest; a guessed one is not.
- Strip dates, iteration numbers, commit ids and version numbers from statements. Keep names of
  records and packages (`issue 54`, `A-full-figure-v1`, `wave 15`) when they are the pointer to the
  evidence. Evidence is pointed at, never restated: "measured in `B-hand-study-v2-rimwrap`, 3527 px
  against 2175" is a statement plus a pointer; "as of 2026-10-21" is not allowed.
- Present tense. If a past fact is no longer true, it is not a fact: drop it from the doc, and the
  record keeps it.
- No new facts. No gate, threshold, floor or scope may be weakened, moved or dropped. If a source
  paragraph cannot be classified without a decision, write it into `docs/0_STAGING.md` with one line of
  why, and say so in the report.
- Length: keep 60–130 % of the source tokens allocated to the file. Under 60 % is silent loss, over
  130 % is invention.

## Packages of this pass

| id | writer's file | sources |
| --- | --- | --- |
| W1 | `docs/1_PROBLEM.md` | README, the person's scope words, `work/a-art-direction-brief.md` |
| W2 | `docs/2_GOAL.md` | `roadmap.md` §Product goal and invariants, `rubric.md` |
| W3 | `docs/3_REQUIREMENT.md` | `principles.md`, README invariants |
| W4 | `docs/4_USECASE.md` | `method.md`, `rubric.md` protocol half, the judgement flow |
| W5 | `docs/5_PRODUCT.md` | `abstraction.md`, `vocabulary.md`, scope decisions |
| W6 | `docs/6_ARCHITECTURE.md` | `spatial-model.md` |
| W7 | `docs/7_INTERFACE.md` | `scene-format.md`, `abstraction.md` traced JSON |
| W8 | `docs/8_DETAIL.md` | generators, resolver tier ladder, diagnostics, conventions |
| W9 | `docs/9_IMPLEMENTATION.md` | `WORKSPACE.md`, `method.md` tool half, README toolchain, AGENTS layout |
| W10 | `docs/0_ROADMAP.md`, `AGENTS.md`, `README.md`, records moves, `STATUS.md` | integrator (manager) |

Writers don't run git, don't edit a source file, don't touch another writer's target, and don't write
`docs/0_ROADMAP.md`, `AGENTS.md`, `README.md` or `docs/0_STAGING.md`.

## Acceptance for each writer package

1. The target file exists and its first three lines are the title line and the first zone H1.
2. `grep -nE '20[0-9]{2}-[0-9]{2}|round [0-9]+|this session|as of' <target>` returns nothing.
3. Every allocated source section has a home: report the mapping `source §X → target §Y` per section,
   and name any section that was dropped with the reason (a record, a dead fact, or a fact owned by
   another file).
4. Length inside 60–130 % of the allocated source text.
5. `grep -c '^# ' <target>` equals the number of zones written, and they are in order.
6. The report states the two or three facts that could not be classified, if any.

## What this pass does not do

Vendor content under `vendor/` is third-party and is never edited. `.scratch/**` and `inbox/**` are
records: they are moved only when a file is a second home for a fact, and their internal links are not
rewritten — a frozen record that points at an old path is a fact about when it was written, and git
holds the old file. No drawing, no code behaviour, no gate, no threshold changes. `evidence/`,
`teaching/` and `mail/` keep their shape; `mail/README.md` remains the mailbox protocol's one home.

## Per-package briefs

**W1 `docs/1_PROBLEM.md`** — why programmatic drawing at all: the pain, the scenario, who it is for,
what the reference is for. Sources: `README.md` (header, §Where this project is right now — the why
half only, §Licensing as what may be shown), `work/a-art-direction-brief.md`'s framing,
`issues/54-user-review-scope-hair-and-hand.md` (the person's own words about what works and what he
wants), and `STATUS.md` only where a sentence is the person's voice. Short is right here: one screen.

**W2 `docs/2_GOAL.md`** — what success means. Sources: `roadmap.md` §Product goal and invariants;
`rubric.md` in full except §How to run a rubric review, §What the reviewer is given, §Part II (those
are W4's). Owns the four acceptance questions, milestone-is-an-artwork, the six axes with their
anchors, how the vector is read, why metrics are alarms, the alarm gates, the similarity alarm as
instrument. No threshold or axis may be weakened.

**W3 `docs/3_REQUIREMENT.md`** — `principles.md` in full: 40 sections land, each `## Pn — …`, grouped
by theme inside its zone, P-number preserved so repo-wide P-references resolve. Zone by provenance as
the source marks it (user insight/constraint/correction/direction → EXPLICIT; the person's agreement →
CONFIRMED; else INFERRED). Plus `README.md` §Invariants in one breath. Evidence pointers (issue
numbers, exercise slugs, package names) stay; dates, rounds and session words go.

**W4 `docs/4_USECASE.md`** — who does what and in which flow. Sources: `method.md` §Current learning
unit, §Current spatial learning loop, §Legacy 2D loop, §The loop, §Judging, §Running the loop by
delegation; `rubric.md` §How to run a rubric review, §What the reviewer is given, §Part II;
`work/r1a-images-for-the-person.md`; `STATUS.md` for the presentation-and-judgement gate as a flow
(what the person is shown, how an image is bound to a revision, why an unpassed picture is not shown).
Not commands (point at `9`), not what good means (point at `2`).

**W5 `docs/5_PRODUCT.md`** — `abstraction.md` in full (drop literal CLI invocations, point at `9`),
`vocabulary.md` in full, plus the scope decisions and rejected branches from
`issues/54-user-review-scope-hair-and-hand.md`. Owns north star, why the language exists, the three
tiers, the two orders, relation taxonomy, forms, the four primitive shapes, the teacher role and its
withdrawal, how the language grows, the canons, the family catalog, the rules for adding a family, the
families-vs-relations boundary, adopted and rejected directions. Not the compiled format (`7`), not
algorithms (`8`), not commands (`9`).

**W6 `docs/6_ARCHITECTURE.md`** — `spatial-model.md` in full except its §Historical S0/S1 section,
which is a record: stage one line for the integrator instead of copying it. Plus `README.md`'s
architecture half (components on planes/curves, depth computes visibility, the current 2D pipeline is
not that engine). Owns boundary, representations, minimum schema, open design choices. No open choice
may be closed and no principle weakened.

**W7 `docs/7_INTERFACE.md`** — `scene-format.md` §File format, §Layers & occlusion, §Node types,
§Renderer contract, §Explainability contract; `abstraction.md` §Materializing a teacher measurement
(the traced-JSON fields and provenance). Not §Generators (`8`), not §Migration acceptance (record).
Field names, formats and guarantees copied exactly; a renamed field or softened guarantee is a defect.

**W8 `docs/8_DETAIL.md`** — `scene-format.md` §Generators; `method.md` §Historical legacy 2D resolver
tier ladder (state what the code does now and check it against `scripts/relate.py`; a tier the code no
longer has is dropped and the discrepancy reported, not repeated); `abstraction.md` §Diagnostics;
coordinate/transform conventions. You may read `scripts/relate.py` and `scripts/scene_render.py` to
check a claim; you change no code and invent no algorithm description.

**W9 `docs/9_IMPLEMENTATION.md`** — `WORKSPACE.md` in full; `method.md` §Guardrails, §Legacy resolver
tool usage, §Legacy resolver SVG/CSS output notes, §Historical legacy 2D curriculum (as the exercise
sequence the tools support, pointing at `0_ROADMAP.md` for milestones); `README.md` §Current toolchain
and §Running it; `AGENTS.md` §Layout and §Command cheat sheet (they become pointers at your file);
`rubric.md` §Part III; the baseline/ratchet procedure; the record areas. Verify every command you
document against `scripts/draw`, the script headers or `--help`; a documented command that cannot run
is a defect (P38).
