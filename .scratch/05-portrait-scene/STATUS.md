# Portrait step-1 status (2026-09-10, post rebuild)

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
