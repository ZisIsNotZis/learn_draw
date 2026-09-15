# STATUS — where this project is right now

**One line:** the drawing language got real; the *drawing* regressed, and we only just made that
visible. A full figure from 2026-09-11 is the best picture the project has; the night session's
"final images" measured **4.5–5.6× worse on coverage** and are reclassified as probes.

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
| **M1** beat the baseline on composition | the whole figure, coarsely, flat fills | ⬜ not started — **entry point** |
| **M2** beat it on the head | jaw/eyes/lash/hat crown/hair taper | ⬜ blocked by M1 |
| **M3** beat it on body & cloth | collar, bow, sleeves, arms, hands, pleats | ⬜ blocked by M2 |
| **M4** beat it on the fields | soft tier last (invariant 2) | ⬜ blocked by M3 |
| **M5** withdrawal + stress | 15 → 16 → 17, reference-free | ⬜ blocked by M4 |

## In flight

Nothing. The 2026-09-14/15 unsupervised research session is **stopped** (P0).

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

1. **The gate has never been run end-to-end on a real milestone** — M0 recorded the baseline, but
   G3 (blind A/B) has not yet been exercised in anger. First real test is M1.
2. **`check` has no test of its own** — the bundle logic (bundle paths, crop ranking, baseline delta)
   is verified only by manual runs. `coverage` is likewise untested.
3. **Line-mode `diff` stays weak for this reference** (no uniform black line art; 12.6 % of pixels
   below gray 95). Region decomposition is the structural source — a known, accepted limitation.
4. **No `style:` header** — deferred until two looks are needed in one project.
5. **`region` / `trace` nodes are teacher-only** (they read the reference raster). By design; they
   must not appear in M5's reference-free specs.
6. **Proportion-vs-placement literal lint** (SA1 finding 6): proportion constants in `vars:` with
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

## Where things live

- **direction** — `docs/drawing/roadmap.md` (this file's counterpart)
- **authoring language** — `docs/drawing/abstraction.md` → `scripts/relate.py`
- **object families + canons** — `docs/drawing/vocabulary.md`
- **compiled back end** — `docs/drawing/scene-format.md` → `scripts/scene_render.py`
- **loop, style guide, tier ladder** — `docs/drawing/method.md`
- **transferable lessons** — `docs/drawing/principles.md` (append-only)
- **the ratchet** — `.scratch/00-tooling/baseline/` + `scripts/draw baseline`
- **the assembly** — `.scratch/13-assembly/work/spec.yaml` *(designated home; **does not exist yet** —
  seeding it from `14/work/final/final-full.yaml` is M1's first work item)*
- **work log per exercise** — `.scratch/NN-slug/{spec.md,work,evidence,log.md}`
