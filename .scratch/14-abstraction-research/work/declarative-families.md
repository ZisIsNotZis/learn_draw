# Declarative families — design proposal (14 D3 / D12)

Status: proposal — becomes `docs/drawing/abstraction.md` content when implemented (post-consolidation).
Author: leader, from SA1 finding 10 + SA3's generator-bridge verdict + the sunhat migration example.

## The mechanism

Today a vocabulary family is an imperative Python function inside the resolver (`expand_sunhat`).
That has two failures (SA1): the model cannot author a family without writing Python, so "learning is
the repo" stores knowledge as unreadable code; and nothing stops coordinates being computed by hand in
Python — invariant 5 is unauditable inside a function body.

A **declarative family** is data. The resolver interprets it; nothing is hand-computed:

```yaml
# families.yaml — loaded by the resolver; every family follows the same rules
families:
  sunhat:
    params: [brim, crown, tilt, lift, drop, flat, crown-h, front, pom, pom-at, pom-r]
    host: required                      # the shape it attaches to (head)
    anchors: [left, right, top, bottom, cx, cy, w, h]   # exported, on the family id
    sub:                                # sub-shapes; may reference ONLY own anchors + params
      - {ellipse: brim, at: [host.cx, host.cy - host.h2*lift], rx: brim/2, ry: brim/2*flat, rot: tilt}
      - {ellipse: dome, at: polar-to-brim-normal(…), rx: crown/2, ry: crown-h*crown/2, rot: tilt}
      - {ribbon: near-edge, along: brim, t: front, w: rim-w}
      - {ellipse: pom-N, along: brim, t: pom-at, rx: pom-r*brim/2}
    parts:                              # named export anchors that are themselves points
      - {dome-centre: dome.at}
```

Rules (from vocabulary.md's family rules, made mechanical):

1. **Sub-shapes may reference only the family's own anchors and params** (+ `frame`, + the host's
   anchors). Reference to any outer shape is a validation error — that is the encapsulation boundary
   (SA1 finding 10), enforced rather than preached.
2. **Params are scalars; the spec passes them by name.** Unknown param = hard error naming the family
   and the spec line (SA1 finding 8's error contract applies here too).
3. **Every sub-shape and every exported anchor is registered** — so P21 diagnostics (OFF-CANVAS,
   CLIPPED, SUB-PIXEL, CONTRADICTION) apply *inside* families, which today they do not (SA1 finding 8:
   a misplaced pom is unreported).
4. **Families may emit groups** (`<g>` per instance), keeping compiled scenes readable (SA3: village
   emitted 3–4 nodes per house; 115 nodes for one scene).
5. **`pair:` wrapper** for mirrored instances with per-side tweaks (3/4 view), replacing a raw mirror
   relation for the common case.

## The generator bridge (SA3 D12)

A spec-level node that declares "compile me as back-end generator X with these resolved params":

```yaml
- {generator: swirl, backend: swirl, at: …, bands: 5, seed: 3}   # params resolved, then passed through
```

The resolver resolves relations → numbers, passes them to `scene_render`'s generator, and asks it for
**true bounds** (not a bbox guess) so diagnostics stay honest (SA3: a wrong bbox guess produced false
CLIPPED warnings). This kills the hand-written passthrough boilerplate (`expand_swirl` etc.) and makes
every back-end generator authorable from the spec with zero Python.

## Migration order

1. Consolidate to ONE resolver (D6) — single pipeline, compile-down only (SA3 D15).
2. Interpreter for declarative families + the generator bridge; validation + worded errors.
3. Migrate `sunhat` as the example — and **fix its occlusion defect in the migration** (near/far brim
   split per P17), not as a Python patch (06 SA1 note).
4. Land the face set (mirror/pair, inside, align, arc, taper) as relations first — the `eye` family
   from SA2 is then authored declaratively (D4), reusing SA2's measured canons.
5. Only then: the scene set (swirl/flow/burst/glow/flame/village/hill/stars) at 17-starry-stress.

## Non-goals

- No constraint solver: resolution stays single-pass in declaration order (P20). A family references
  only what is declared above it.
- No new expression language: the whitelisted AST evaluator (arithmetic over anchors) is the only
  math, everywhere — families included.
- No style header yet: `style:` presets wait for a drawing that needs two looks in one project.
