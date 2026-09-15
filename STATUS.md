# STATUS — where this project is right now

**One line:** the drawing language got real; the *drawing* regressed, and we only just made that
visible. A full figure from 2026-09-11 is still the best picture the project has — M1 rebuilt the
figure's composition on the relational layer and now covers more of the reference than the baseline
does (0.528 vs 0.514), but as a *drawing* the baseline is still ahead, and it stays the bar.

Last updated: 2026-09-15 · Direction lives in `docs/drawing/roadmap.md` · Milestones M0–M5

## Current best artifact — the ratchet floor

| field | value |
| --- | --- |
| render | `.scratch/00-tooling/baseline/best.png` |
| origin | `.scratch/05-portrait-scene/evidence/current.png` (REBUILD v2, 2026-09-11) |
| spec | `.scratch/05-portrait-scene/work/scene.yaml` (133 nodes) |
| `sha256` | `1a7cae4fa400068725ebbbfce5a1401188aa21b3885fb376332089baec080c7c` |
| metrics | `coverage 0.514 · edge_f1 0.252 · recall 0.207 · color_dist 62.8` |
| provenance | `.scratch/00-tooling/baseline/best.json` |

Reproduce (verified byte-identical, 2026-09-15):

```bash
.venv/bin/python scripts/scene_render.py .scratch/05-portrait-scene/work/scene.yaml \
    -o /tmp/best.png --ref image.jpg
.venv/bin/python scripts/draw.py check /tmp/best.png --ref image.jpg     # prints "vs recorded best: all +0.000"
```

`coverage` = fraction of the reference's content the draft accounts for — the omission alarm.
It is a **floor and an alarm**, never a target (roadmap R6).

## Milestones

| milestone | intent | status |
| --- | --- | --- |
| **M0** baseline recorded | make regression visible | ✅ done 2026-09-15 |
| **M1** recover the baseline's composition | the whole figure, coarsely, flat fills | ✅ **exit criteria met 2026-09-15 — baseline not promoted.** Coverage 0.528 vs 0.514 (nothing deleted); the baseline is still the better drawing (two blind reviewers, and the grid measurement agrees). Artifact: `.scratch/13-assembly/evidence/m1-final.png`; gates + rollbacks in `13-assembly/log.md` |
| **M2** beat the baseline on the head | jaw/eyes/lash/hat crown/hair taper | ⬜ **next** — patches the assembly; promotes on the *head crop* alone |
| **M3** beat the baseline on body & cloth | collar, bow, sleeves, arms, hands, pleats | ⬜ blocked by M2 |
| **M4** beat the baseline on the fields | soft tier last (invariant 2) | ⬜ blocked by M3; the whole-figure promotion belongs here |
| **M5** withdrawal + stress | 15 → 16 → 17, reference-free | ⬜ blocked by M4 |

## In flight

**M2 — beat the baseline on the head.** Entry: M1's exit criteria are met. Work items and the
`face`-family gap are in `.scratch/08-bust/spec.md`; promotion is on the head *crop* alone.

Nothing else is in flight. The 2026-09-14/15 unsupervised research session is **stopped** (P0).

Its work is kept selectively, per `14-abstraction-research/spec.md`:

- **kept as real progress:** `scripts/relate.py` (one resolver: anchors, relations, `sunhat` + `eye`
  families, 4 diagnostics); the measured canons in `vocabulary.md`; `principles.md` P1–P22; the
  declarative-family proposal in `14/work/declarative-families.md`.
- **demoted to probes:** `14/evidence/final/v3.png` (bust) and `14/evidence/final/full-v2.png`
  (full figure) — the two artifacts committed as "FINAL IMAGE". Neither passes the gate; both are
  below the baseline. They are evidence about the language, not the project's drawing.
- **the assembly seed:** `14/work/final/final-full.yaml` is M1's starting point, to be promoted into
  `.scratch/13-assembly/work/spec.yaml`.

## Open defects and questions

1. **The hat's brim meets in a straight seam** through the brim centre (the `sunhat` family's pie-slice
   split) where the reference's teal/navy boundary is diagonal, and the crown barely separates from
   the navy brim. Measured, unfixed — M2's ("hat reads as a hat").
2. **`hair-left` is a straight thin stroke**; the reference's left sweep is a curved wisp. M2/M3.
3. **The missing cream mass is an occlusion problem, not a size problem** — enlarging it made the
   drawing worse (M1 v4, rolled back). The cream the reference shows around the bow is hidden
   *behind* the bow and hair, so it belongs to M3.
4. **`check` has no test of its own** — the bundle logic (bundle paths, crop ranking, baseline delta,
   `coverage`) is verified only by manual runs. `measure-composition.py` is likewise untested.
5. **Line-mode `diff` stays weak for this reference** (no uniform black line art; 12.6 % of pixels
   below gray 95). Region decomposition is the structural source — a known, accepted limitation.
6. **No `style:` header** — deferred until two looks are needed in one project.
7. **`region` / `trace` nodes are teacher-only** (they read the reference raster). By design; they
   must not appear in M5's reference-free specs.
8. **Proportion-vs-placement literal lint** (SA1 finding 6): proportion constants in `vars:` with
   provenance are convention-only; the resolver does not yet warn on raw `frame.*` placement.

## Decisions log (append-only)

- **2026-09-15 · D1 — the night session's completion claim was false.** A bust and then a full
  figure were committed as "FINAL IMAGE" without the gate its own rules require (P22). Both are
  reclassified as probes. Recorded rather than reverted: the artifacts are evidence, and the git
  history is the learning curve.
- **2026-09-15 · D2 — the 2026-09-11 full-figure render is the project's baseline**, not a frozen
  dead end. `05` stays frozen as a *ticket* (it was doing too much at once) but its artifact becomes
  the ratchet floor.
- **2026-09-15 · D3 — the roadmap's milestone gates are adopted** (`docs/drawing/roadmap.md`).
  Milestone exit = gate pass, not slice completion. Spine changes require an entry here.
- **2026-09-15 · D4 — `coverage` adopted as an alarm and a floor**, never a target: the metric that
  would have made a bust visible as a bust. It is a *floor* because deleting content is a regression
  even when the remaining detail improves.
- **2026-09-15 · D5 — the assembly is one artifact** (`.scratch/13-assembly/work/spec.yaml`, seeded
  in M1), patched
  by every milestone. The old ladder's rung directories keep their specs as slice homes, but do not
  each own a separate drawing.
- **2026-09-15 · D6 — `blob` has two legitimate forms** (`poly` closed, or `spine` + `w` ribbon) in
  both the authoring front end and the compiled back end. The front end previously accepted only the
  ribbon form while the back end accepted both — a dialect split that crashed the full-figure spec.
- **2026-09-15 · D7 — the gate was mis-specified, and M1 found it.** G2 originally required
  `edge_f1 ≥ best − 0.01` at every milestone, but M1 is *defined* as flat masses with no line work, so
  the floor failed it for doing its job — and passing it would have meant smuggling M2/M3 work into
  M1, the "one ticket doing several things at once" failure that got 05 frozen. Split into: **G2
  alarm** (coverage deletion floor + color_dist breakage bound; applies always) and **G2b detail
  floor** (`edge_f1`; applies from M2). **Promotion separated from milestone exit** — the baseline
  moves only on a blind A/B preference, never on metrics and never because a milestone passed.
  A gate that fails a drawing for doing what the milestone asked is a gate defect; the fix is
  recorded, not quietly applied.
- **2026-09-15 · D8 — M1 exit criteria met; the baseline was NOT promoted.** The assembly now exists
  at `.scratch/13-assembly/work/spec.yaml` with measured composition, coverage 0.528 (> 0.514, so
  nothing was deleted), diagnostics clean, 17 nodes, byte-deterministic. But two fresh reviewers both
  called the baseline the better *drawing*, and the coarse-grid measurement agrees (32.6 vs 39.1). The
  milestone is complete and the ratchet has not moved: those are different statements, and keeping
  them separate is the whole point of D7. M1 did fix real composition errors the baseline has — its
  dark skirt mass (0.6% of frame vs the target's 7.8%) and its ribbon (0.1%) are essentially missing.
- **2026-09-15 · D9 — the largest remaining M1 deficit is occlusion, not composition.** The target's
  cream mass is 12.5% of the frame against the assembly's ~4.5%, but enlarging the cream shapes made
  the drawing worse (M1 v4: coverage 0.523 → 0.502). The cream the reference shows is *behind* the bow
  and hair, so it is M3's occlusion problem, not an M1 size problem. Recorded so M3 does not
  re-discover it.

## Where things live

- **direction** — `docs/drawing/roadmap.md` (this file's counterpart)
- **authoring language** — `docs/drawing/abstraction.md` → `scripts/relate.py`
- **object families + canons** — `docs/drawing/vocabulary.md`
- **compiled back end** — `docs/drawing/scene-format.md` → `scripts/scene_render.py`
- **loop, style guide, tier ladder** — `docs/drawing/method.md`
- **transferable lessons** — `docs/drawing/principles.md` (append-only)
- **the ratchet** — `.scratch/00-tooling/baseline/` + `scripts/draw baseline`
- **the assembly** — `.scratch/13-assembly/work/spec.yaml` (M1 complete; this is the live drawing)
- **the gate instrument** — `.scratch/13-assembly/work/measure-composition.py` (placement check)
- **work log per exercise** — `.scratch/NN-slug/{spec.md,work,evidence,log.md}`
