# REBUILD v2 — user defect list (verbatim intent, 2026-09-11)

Source: user viewed full side-by-side compare (`/tmp/full-compare.png`: ref left | draft right) and gave 7 numbered defects. This file is the authoritative work order for the next session(s). Philosophy: P14 (proper drawing > pixel match), P15 (generate from parameters). User provided component plates in repo root: `hat.png`, `head.png`, `head_hat.png`, `dress.png`, `cloth.png`, `ribbon.png`, `cutout.png` (2048x2048, ~2x-upscaled ref crops with filled bg; `dress.png` matches ref only 4% — likely redrawn; PRESUMED black-dress layer reference, `cloth.png` presumed white shirt+dress — CONFIRM with user if ambiguous).

## The 7 defects (user's words, condensed)

1. **Hair blown toward left is not drawn at all.** The ref has hair mass blowing left; draft has nothing there. Must be added — BEHIND the person (see #5).

2. **Clothing has fold-like structure/feeling in ref; draft is flat.** White shirt+dress needs fold structure: shadows/highlights along fabric tension lines, not uniform fills. Use strand/shadow generators along fold directions.

3. **Both hands are too small. The left hand (drawn to the right side) isn't even connected to body.** In ref the hand is ~90% hidden BEHIND the body — that occlusion is where depth should "glow". Fix: enlarge hands, tuck behind body silhouette, add depth shadow at the tuck line. This is the killer use of the layer/z-plane system.

4. **The dress is two layers — white area AND black area. Draft fully skipped the black area.** Draw `dress-black` underlayer (ref: dark navy mass under/behind the white dress). User's `dress.png` plate likely shows it.

5. **The large green/cyan area is ALSO hair — very long hair with inner surface glowing a weird/cool color. It is BEHIND the person, not a semitransparent overlay in front.** Current draft draws the green mass as an overlay on top of the body — WRONG z-order. Restructure: `hair-behind` layer (green glow mass + blown-left hair) sits behind body/torso.

6. **The rainbow-ish curved ribbon at the bottom wraps AROUND the person: part of it is BEHIND the person, not non-existing.** Model: continuous color-changing circle with zig-zag edge, tunable zig-zag depth + density + random jitter. Split into `ribbon-back` / `ribbon-front` at the body silhouette (z-plane, not manual path splitting). Likely needs a new `ring` generator node (center, radii, width, zigzag depth/density/jitter seeded, hue rotation along arc, back/front mask split).

7. **Layer-first workflow (user mandate):** split components into layers and draw each one well, one at a time. Proposed layer stack (bottom→top): bg → hair-behind (blown-left + green glow) → ribbon-back → dress-black → dress-white (folds) → body (torso/arms/hands w/ depth) → hair-front (bangs/curtain) → hat → ribbon-front.

## Execution plan (agreed with user)

- Phase 0: component intake — mask-extract each plate (diff vs blurred ref), downscale to 1024-space, save to `work/components/{name}-plate.png` + `{name}-mask.png`; confirm dress/cloth plate meaning with user
- Phase 1: restructure scene.yaml into the layer stack above (z-order fix for #3/#5/#6 even before new content)
- Phase 2: build `ring` generator node (#6) — zigzag circle ribbon w/ hue walk, back/front split
- Phase 3: per-component passes in user priority order: dress-black (#4) → ribbon ring (#6) → hair behind (#1+#5) → hands (#3) → cloth folds (#2) → hat refinement (against hat.png plate)
- Phase 4: whole-frame judgment per P14 — fresh-eyes critic + orchestrator view loop; iterate on visible wrongness, not metrics

## Session-ops notes (hard-won)
- `worker` subagent profile is broken (no read/bash — confirmed twice). Use Agent tool `general-purpose` profile instead.
- Renderer: `python scripts/scene_render.py scene.yaml -o out.png --ref image.jpg` (scene = FIRST positional arg). Tests: `python scripts/tests/test_scene.py` (15 green).
- Image viewing: read() attachments can come back empty late in long sessions — retry once smaller (≤48KB JPEG), else fall back to pixel probes and SAY SO. Never claim to have seen.
- Workers don't commit; orchestrator verifies independently then commits.
- Current state at handoff: scene.yaml 133 nodes, Phase A+B done (wave/strands generators live, ribbon = 2 waves, strands generators), overall 60.8, commit 6401ca9.
