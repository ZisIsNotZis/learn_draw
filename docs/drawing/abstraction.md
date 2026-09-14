# Drawing language — relational front end

How a drawing gets described at object level instead of coordinate level. Resolver:
`.scratch/06-relational-geometry/work/relate.py` (promote to `scripts/` when a drawing needs it),
proof spec `work/bust.yaml` in the same directory. This is the *authoring* layer;
`scene-format.md` documents the compiled node format behind it.

The loop this serves: write/adjust a spec → resolver emits absolute geometry + diagnostics →
`draw check` renders the bundle → a fresh-context reviewer judges it. Coordinates are never typed;
they are what the resolver prints when it is done.

## Why this exists

The portrait failed because the only available way to place geometry was absolute coordinates:
825 hand-typed vertices across 58 polygons, and **zero** uses of the computed `trace` node. A VLM
is strong at naming, grouping, ordering and judging, and weak at coordinate regression — so the
authoring channel was asking for the one thing the author cannot do, at a scale (1024²) where its
own errors are invisible to it.

Measured: computed region decomposition of the same reference reached the character in 2.4s, while
20 hand-authored iterations did not (`05-portrait-scene/evidence/diagnosis/`).

**Hard constraint:** the engine must never depend on the target image. A reference may *seed* the
values in a spec (the teacher role), but a solver that needs the target cannot serve the end goal of
drawing without one. Test for any addition: *does this still work with the image deleted?*

## Three tiers

Ask for the picture the way you would describe it to a person: name the objects, give proportions,
state what overlaps what. The engine resolves everything numeric.

| tier | what it carries | example |
| --- | --- | --- |
| 1. anchors | the canvas frame, and every shape's handles | `frame.w`, `head.rx`, `brim.left`, `head@0.25` |
| 2. relations | positions and sizes expressed *relative to other things* | `{along: brim, t: 0.62}`, `2.70*head.w`, `{between: [A, B, 0.35]}` |
| 3. vocabulary | parametric object families with drawing-sane structure | `{sunhat: hat, host: head, brim: 2.70*head.w, tilt: -14, pom: 2}` |

Relations alone are not enough: they can place a shape but not invent one. Tier 3 is where drawing
knowledge lives — a wide-brim hat *is* a squashed brim ellipse, a dome on the brim's own normal, and
a near edge painted over the crown. The model says "wide-brim sun hat, tilted 14°", not twelve
coordinates. Tier 3 is also what makes a starry-night-complexity scene tractable.

## Two orders, kept separate

- **Resolution order** — a node may reference any shape declared *above* it. Put the ruler first.
- **Paint order** — `layers` bottom→top, then declaration order within a layer (`z:`).

These are different orders on purpose. The head is declared first (everything is sized in units of
it) but painted *under* the hair. Keeping them apart is what removes the manual occlusion surgery
that dominated the portrait: occlusion is the renderer's job, never encoded in a path.

## Forms

Values are numbers, arithmetic, or a relation dict. Strings may reference anchors: `"1.8*head.rx + 4"`.

| form | meaning |
| --- | --- |
| `[x, y]` | point; each component is a number or expression |
| `{at: SHAPE}` | that shape's centre |
| `{along: SHAPE, t: 0.35}` | point on SHAPE's outline at `t` (wraps; works on rotated ellipses) |
| `{along: SHAPE, t: 0.1, out: D}` | same, pushed `D` outward along the outline normal |
| `{between: [A, B, t]}` | point `t` of the way from A to B; `t` outside 0..1 extrapolates |
| `{off: P, angle: 90, d: 40}` | point at angle/distance from P (0° = right, 90° = down) |
| `vars:` | named intermediate scalars, evaluated once, referenced by bare name |

Vocabulary nodes so far: `sunhat` (brim, crown, tilt, lift, drop, front arc, optional poms).
`eyeball`, `strand-mass`, `sleeve`, `fold-set` are **not written yet** — each is added only when a
rung of the ladder fails without it (08-bust is expected to demand `eyeball`-type structure for the
face; 10-cloth the pleat/fold family). See "How it grows".

**YAML caveat:** `on`, `off`, `yes`, `no` parse as booleans, so this language uses `along` for
outline points and `host` for an object family's attachment. `relate.py` rejects boolean keys by
name rather than failing cryptically.

## Diagnostics — the engine is the model's numeric sense

A model cannot check whether a number is off-canvas, so the resolver reports *derived facts as
sentences* instead of leaving it to the author:

- `OFF-CANVAS` / `CLIPPED` — shape entirely outside, or crossing the frame edge (with coordinates)
- `SUB-PIXEL` — rendered smaller than ~3px, i.e. invisible
- `CONTRADICTION` — a declared `relations:` intent (`front: hat, behind: hair`) disagrees with the
  `layers` order; the engine says which layer wins
- anchor table (`--anchors`) — every resolved handle, so the author can reason about what it got

On the first proof render this caught two real defects before the image was looked at.

## The teacher role, and why it can be withdrawn

A reference is used in exactly two supported ways, both removable:

1. **Seeding values** — measure the reference (`measure`, boundary tracer, region decomposition) to
   fill in the numbers in a spec, then close the image. The spec, not the image, is the drawing.
2. **Setting the frame** — the canvas size and where the subject sits in it.

Tracing is never the engine. The curriculum depends on this: reproduce with the reference, then
reproduce the *same* subject from its own spec with the image closed, then a new subject from intent
alone. The ladder runs this withdrawal explicitly — rungs 08–13 draw with the reference available,
and the follow-on after 13 redraws the assembled figure from its own spec with the image closed.

## How it grows

One rule, learned the hard way: **a new relation or vocabulary node is added only when a real
drawing failed without it.** No speculative generality. The renderer's `blur`/T3 machinery is
evidence of what happens otherwise — it was built for soft-field realism, then pointed at flat cel
art, and produced mush.

## Open questions

- Does `along`-at-`t` need a companion for "where this outline crosses that one" (junction points,
  which P4 says carry the character)? Only if a drawing demands it.
- Sizes are currently uniform (`w:`). The portrait needed taper; `scene_render` already has width
  profiles — reach for them when a ribbon or strand actually needs one.
