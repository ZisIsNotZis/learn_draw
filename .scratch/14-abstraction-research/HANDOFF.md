# Night-research handoff — resume here tomorrow

Run: 2026-09-14, unsupervised, ticket 14. Goal: deepen the relational drawing language (anchors /
relations / vocabulary) so it supports no-reference drawing, end goal Starry-Night complexity.

## The one-line state

A face + a Starry Night evocation were both drawn from parameters with no reference; the language
has one canonical resolver; an adversarial review was integrated including a self-retraction; and
the night closes with an assembled bust (`evidence/final/v3.png`) judged by a fresh reviewer.

## What exists now (all committed)

| piece | path | state |
| --- | --- | --- |
| single resolver | `scripts/relate.py` | families: `sunhat` (occlusion fixed), `eye` (SA2); relations incl `along`, `between` (anchor coercion), `polar`, `mirror`, `at`; diagnostics OFF-CANVAS/CLIPPED/SUB-PIXEL/CONTRADICTION; anchor table `--anchors` |
| node back end | `scripts/scene_render.py` | dead `on`/`fit` keys removed; YAML-boolean error named; generators wave/strands/ring/petal |
| view loop | `scripts/draw check` | captures resolver diagnostics+anchors into report.txt, records which resolver ran, deterministic resolver selection |
| docs | `docs/drawing/` | method.md (loop+curriculum), abstraction.md (language + north star + taxonomy + literal classes), vocabulary.md (families + two canon sets + rules), scene-format.md (compiled back end, corrected), principles.md P1–P22 |
| critiques/probes | `.scratch/14-abstraction-research/` | `evidence/sa1/critique-summarized.md` (12 findings), `work/face/` (SA2, report.md), `work/starry/` (SA3, report.md + its scene_render copy is QUARANTINED evidence, not code), `work/declarative-families.md` (the next-architecture proposal), `work/final/bust-final.yaml` |
| tickets | `.scratch/` | 06 done (re-assessed honestly), 07 done, 08 bust (blocked on face-set work), 09–13, 15 withdrawal-A, 16 withdrawal-B, 17 starry-stress |

## Decisions D1–D21 (short form; full text in `log.md`)

- Geometry computed, semantics authored; ≤4 hand coords/shape (invariant 5). Engine never sees the
  target (invariant 6 / P18). Never judge your own render (invariant 7 / P22).
- Literals split: proportion/style constants live in `vars:` with provenance; placement must derive
  from anchors (warning for raw frame.* placement is still TODO).
- Declarative families ADOPTED (D3, proposal in work/declarative-families.md): a family = a YAML
  block (params + sub-shapes referencing only its own anchors); plus a `generator:` bridge to
  back-end nodes with true bounds. sunhat is the migration example and also fixes occlusion there.
- Face-set relations land BEFORE 08: `arc`, `align`, taper-as-first-class (mirror already landed).
  A `face` host family (jaw/chin/temples; the ellipse host is the round-chin cause) is the main
  structural gap for faces, with a `turn` knob for 3/4 asymmetry and grouping ("whole eye" as one
  z-unit).
- Scene set (`flow`, `distribute-along`, `jitter-grid`, swirl/glow/flame/village/hill/stars) has a
  demand DATE: ticket 17, blocked by 16. Build nothing earlier (demand-first).
- Withdrawal is trained: 15 = same subject, image closed (recall); 16 = new subject, intent only;
  composition anchors (thirds/horizon/focal) enter at 16.

## Resume sequence

1. Read the final-image verdict at the bottom of `log.md` and `evidence/final/`.
2. Claim `08-bust`. Openers, in order:
   a. implement `arc` (partial outline of a host, arc-length t), `align`, tapered strokes in
      `scripts/relate.py`, with tests;
   b. declarative-family interpreter (work/declarative-families.md) — migrate sunhat first
      (occlusion already proven as slices), then re-author SA2's eye as data;
   c. `face` host family (superellipse/jaw silhouette + cross anchors, Loomis model in
      vocabulary.md); then rebuild work/final/bust-final.yaml to proper acceptance
      (line-art stage, check + fresh eyes before color, all edges stroked).
3. Every addition: docs-first (vocabulary.md/abstraction.md the same session), deterministic,
   committed, `draw check` + fresh reviewer before "readable".

## Open questions (for the user or the next session)

- Should proportions that are taste choices (brim 2.7, tilt −14) get a provenance comment enforced
  by a lint, or is convention enough? (SA1 finding 6; leaning: enforce via resolver warning.)
- The starry swirls read as coils; SA3 says a `flow` field over the swirl centre is the fix. Verify
  at 17 rather than patch the probe.
- style header (anime-cel vs other looks) is deferred until two looks are needed in one project.
- The `check` reviewer route that works here: Agent tool, subagent_type `explore`. The `subagent`
  tool's `reviewer` cannot launch (host lacks read/grep for children).

## Commands

```bash
.venv/bin/python scripts/relate.py .scratch/14-abstraction-research/work/final/bust-final.yaml -o /tmp/b.png --anchors
scripts/draw check /tmp/b.png --ref image.jpg --outdir /tmp/b-check
.venv/bin/python scripts/tests/test_scene.py
```
