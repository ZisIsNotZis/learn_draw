# Portrait step-1 status (2026-09-10, post rebuild)

> FROZEN 2026-09-14 — historical record. The exercise is superseded; see `spec.md` banner,
> `evidence/diagnosis/` for why, and `.scratch/06-relational-geometry/` + the L1–L6 ladder for what replaced it.
> Nothing below should be resumed.

## Achieved

- Full-figure assembly, all anatomy present (neck, hands, hat brim 帽檐, dark skirt, colorful translucent ribbons)
- XML well-formed; single torso; verified layer order
- overall color distance vs ref: 74 → 61.1
- per-zone: hat 31.7 (good) · face 68.7 · ribbon 63.1 · curtain 79.2 · torso 86.3 · skirt 88.4
- skirt navy amount matches ref (32.9k vs 32.0k)
- critic loop operational (downscaled copies → delegate → triage)

## Honest gap (why it still looks "very off" side by side)

1. Skirt dark/light ARRANGEMENT differs (amount correct, placement drifts; left flank fixed partially)
2. Detail density: ref has 3-5x more strand/fold/highlight elements
3. Shading: no light-direction modeling (T3 shading layer not started)
4. Ribbon: needs tapered ends, wave line, softer gradient luminosity
5. Water: absent (ref: pale luminous field + ripples)

## Proven method to close it (mechanical, unexecuted)

zone-diff-grid (32px cells, ranked) → gridded-observation crop → anchor reading → smooth_path
→ assert-verified edit → ET parse → render → full-frame view → re-probe. Repeat per zone
(skirt arrangement, ribbon taper, petals, water, then shading pass: light from upper-left).

## Files

- assembly: .scratch/05-portrait-scene/work/v20.svg
- render: evidence/v17-render.png (latest full render: /tmp/v20d.png — copy to evidence next session)
- briefs: REBUILD-BRIEF.md, FIX-BRIEF-v21.md, SHADING-BRIEF-v22.md (reusable protocol)

## UPDATE (scene format migration, same day)

- docs/drawing/scene-format.md: spec for object-level scene DSL (inline-YAML list)
- scripts/scene_render.py: renderer (spine/taper/petal/blob/region/trace/grad/blur, z-sort, schema validation) + 11 smoke tests all green
- Portrait migrated: .scratch/05-portrait-scene/work/scene-traced.yaml — 77 nodes vs ~150 SVG paths, overall parity with v20 (61.5 vs 61.5), 2 zones improved
- Param-level iteration VERIFIED: 2 value edits → exactly 2 local changes, zero side effects
- Converter: bezier-flatten v20 paths → dense polys (scripts used inline; consider promotion if needed)
- Remaining: same visual-fidelity backlog as before (arrangement, density, shading) — now attackable at parameter level

## Phase A+B complete (2026-09-11)

- Generators live: `wave` (amp/wavelength/sag/taper), `strands` (seeded, deterministic) — 15/15 tests green
- Phase B landed (133 nodes): ribbon = 2 waves, hair/curtain/skirt = 4 strand generators; ribbon top edge within ~25px of ref
- Worker-profile bug found twice: `worker` agent allowlist lacks read/bash — use Agent tool general-purpose profile instead
- Judging per P14: coherent drawing > pixel match; next = Phase D (fresh-eyes critic loop on visible wrongness)

## REBUILD v2 — Phases 0-2 complete (2026-09-11, handoff state)

Authoritative work order: REBUILD-v2-BRIEF.md (user's 7 defects + plan). Done so far:

- **Phase 0 (component intake)** — plates extracted to `work/components/{name}-plate|mask.png`
  (1024-space) via `work/extract-components.py`; alignment in `work/components/REGISTRY.md`.
  Key facts: hat/ribbon/head_hat = position-true 1:1; head = illustrative; dress.png = dark
  pleated SKIRT plate (= dress-black), cloth.png = white BLOUSE plate; both redrawn (style-only).
- **Phase 1 (layer stack)** — scene.yaml layers now bg → hair-behind → ribbon-back →
  dress-black → dress-white → body → hair-front → hat → ribbon-front (user mandate #7).
  Green masses → hair-behind (#5 z fix); pink field → ribbon-back; yellow → ribbon-front.
- **Phase 2 (ring generator)** — new `ring` node (zigzag annulus, elliptical via rx/ry/rot,
  hue walk, seeded jitter, nseg slices). Ribbon placed from plate fit: ellipse (595,883)
  rx347 ry103 rot7 w95; back arc a0=180-360 (z ribbon-back), front arc 0-180 (z ribbon-front),
  hue 170→350 east→west. Dress-black split into left+right bands to open the ref's pink
  ribbon panel (x215-420). Pixel-probe verified: pink front arc over skirt at ref location.

- Tests 16/16 green (`python scripts/tests/test_scene.py`). color_dist 60.8→62.8 (signal only, P14).
- Commits: 0d96361 (P0) 7cfb695 (P1) 599a745 (P2) b017892 (log). Docs: scene-format.md updated
  with wave/strands/ring generator section; principles.md P16 (plate alignment), P17 (z-plane split).

## REBUILD v2 — remaining work (Phase 3, user priority order)

1. dress-black plate detail (#4) — pleats + teal ruffle trim from dress.png plate (style ref)
2. ribbon ring fine-tune (#6) — band edges ~20-30px off ref panel at y870 west/y950 south; tunable via at/rx/ry/w
3. hair-behind mass (#1+#5) — blown-left hair (x0-344, y562-810) still absent; strands generator on hair-behind layer
4. hands (#3) — enlarge, tuck behind body silhouette, depth shadow at tuck line (killer z-plane use)
5. cloth folds (#2) — fold shadows/highlights on blouse via strands along tension lines (cloth.png = style ref)
6. hat refinement — against hat.png plate (position-true)
Then Phase 4: whole-frame judgment per P14 (fresh-eyes critic loop on visible wrongness).

## Session-ops (confirmed again this session)

- Image attachments return EMPTY late in long sessions (3 retries at decreasing sizes all failed).
  Fallback that works: pixel probes + ASCII hue-class grid maps (see log.md iter 15). Never claim to have seen.
- `scripts/draw` wrapper needs bash; direct call `.venv/bin/python scripts/draw.py diff ...` works.
- Renderer CLI: `.venv/bin/python scripts/scene_render.py <scene.yaml> -o out.png --ref image.jpg`
