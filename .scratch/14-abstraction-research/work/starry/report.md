# SA3 — Starry Night abstraction probe (reference-free)

**Question:** does the relational/parametric authoring language express a complex,
non-portrait scene from pure intent, with no reference image — and where does it break?

**Setup:** copies of `scene_render.py` and `relate.py` live beside this report
(`work/starry/`); the original `scripts/` and `.scratch/06/...` files are untouched.
Spec: `work/starry/spec.yaml` (parameter-only, see below). 9 iterations, every render
looked at; renders in `evidence/starry/v1..v9.png` (v9 = final), check bundle in
`evidence/starry/check/`.

## The spec — what was authored, not computed

- **Hand-authored geometry:** the village ground curve (4 points, one shape) and nothing
  else. Every other coordinate is a frame fraction, a `vars:` scalar, or a relation
  (`{"off": P, angle: 272, d: frame.h*0.65}` for the cypress tip; region lists for star
  fields / wind bands).
- **Everything else is parameters + seeds.** 115 compiled nodes, ~10 hand numbers.
- Determinism: re-render is byte-identical to v9 (`cmp` clean).

## Generator families built (in the scene_render copy) and vocabulary (relate copy)

| family | params | anchors | what it carries |
| --- | --- | --- | --- |
| `swirl` (g) | at, rx, ry, rot, a0, sweep, bands, w, gap, wob, cap, hue, sat, val, seed | at, rx/ry, rot (bbox) | nested Archimedean spiral ribbons around an elliptical flow centre, hue walking inner(bright)→outer; **centre cap** kills the "eye pupil" hole (v2 fix) |
| `flow` (g+v) | region, n, dir, spread, w, wj, len, curv, waves, ink, seed | region bbox | broad curved ribbons FOLLOWING a direction field — the `flow` relation. v5 proved `strands` (straight jittered lines) is not flow: it read as scratches |
| `burst` (g) | at, rays, len, w0, w1, a0, spread, ink, seed | — | radial rays tapering core→tip, seeded jitter |
| `glow` (v) | at, r, rays, len, color, core, halo, seed | centre, halo radius | a star/moon = radial-grad halo BEHIND tapered rays BEHIND bright core (occlusion inside the family) |
| `flame` (v) | base, tip (relations), w, lobes, bend, scal, color, stroke, wisps, seed | bbox | cypress: quadratic spine, envelope width (bulge low, sharp tip), scalloped edges, detached side wisps leaning with the trunk |
| `village` (v) | curve (≤4 pts), count, seed, size, sizej, church t, fills, win-chance | curve bbox, row@t | houses distributed along the ground curve, tilted to its tangent, body+roof+lit window; one church with steeple |
| `hill` (g+v) | y0, bands, amp, wl, colors, seed | bbox | stacked rolling bands far(light)→near(dark), two-harmonic sine, seeded phases |
| `stars` (v) | region, n, r, rj, seed, fills | region bbox | seeded dot field with jittered size/opacity — jitter-grid made concrete |

(g) = scene_render generator node, (v) = relate.py vocabulary family. Also added a sharp
`poly` node type (un-smoothed polygons — gable roofs/steeples need corners; `blob`'s
smoothing rounds them).

## New RELATIONS the language needs (specific, with why)

1. **`flow` (direction-field following)** — the biggest gap. The sky's wind/brush strokes
   are neither straight lines (`strands`) nor rings (`ring`); they *follow a direction
   field with curvature*. Implemented as `flow` (seed a walk in region, relax heading to
   field dir + travelling meander, render as filled ribbon). Any hair/water/wind family
   wants the same primitive.
2. **`distribute-along` (curve + seeded jitter)** — `village` needed "n instances on this
   curve, jittered, one of them special (church)". Today it's a whole vocabulary family;
   the relation under it (arc-length parameter + tangent frame + jitter) should be
   reusable for pleats, fences, trees. Family is fine, the *relation* is the missing rung.
3. **`jitter-grid` / scatter-in-region** — `stars` and `flow` both implement "n seeded
   points in a rect" ad hoc. Should be one relation both consume.
4. **`tangent/contact`** — the village family internally computes "sit ON the curve,
   tilted to its tangent". A spec cannot currently say "house touches ground line here" —
   only the family can. Expose `row@t` (already anchored) + a `contact` relation so a spec
   can pin *other* objects to a curve.
5. **`align`** — mild: the horizon line wants to be "the same y" across hills band 0 and
   the village row's far edge. Currently implicit in parameters.
6. **YAML wart (not a relation but real):** the `off` polar relation is a YAML 1.1 boolean
   word and must be written `{"off": ...}`. This will bite every author; rename to
   `polar`/`at-angle` in the language.

## Where the current 3-level model strained

- **Generators are tier-2.5 and unreachable.** `swirl`/`burst`/`hill` had to be added to
  the *back end* (scene_render), but the *front end* (relate) is what authors write — so
  every new generator needed a hand-written passthrough family (`expand_swirl` etc.) just
  to accept relations and frame fractions. The bridge is thin but it is boilerplate, and
  `strands`/`wave`/`ring`/`petal` still have none. **The abstraction has no concept of
  "a spec-level node that compiles to a back-end generator".** Minimal fix: a generic
  `generator:` wrapper that declares which back-end node it is and passes resolved params.
- **The resolver's emitter is a second SVG path.** relate.py originally wrote its own SVG
  and called chrome directly; this probe rerouted it to compile DOWN to the scene-format
  and render through scene_render (one pipeline, gradients + new generators for free).
  The old duplicate emitter is now dead weight — the compiled-node path should be the only
  path.
- **Node count.** 115 nodes for one scene (portrait budget was ~80). `village` alone emits
  3-4 nodes per house. Fine for a machine, but it shows tier-3 families that emit *groups*
  (a `<g>`) would keep the compiled scene readable; scene_render already does this for
  petal/strands/ring.
- **Anchor bookkeeping.** Pass-through families must fabricate bbox anchors for
  diagnostics/references; my first attempt over-estimated swirl extents and produced false
  CLIPPED warnings (caught, fixed). Diagnostic honesty depends on anchor fidelity — a
  generator returning a true bounds would be better than a bbox guess.
- **Looking is the loop.** 8 of 9 fixes came from LOOKING, not from the resolver's
  diagnostics (which were clean after v1). The two real generator bugs (eye-hole swirls,
  straight scratches) were only visible in the raster. Confirmed: this abstraction needs
  the human-in-the-loop render, every iteration.

## Verdict

**Yes — it scales, with one structural addition.** v9 renders a credible Starry Night
evocation (swirling sky, glowing moon and stars, flame cypress, sleeping village, rolling
hills) from ~10 hand numbers + 115 parameterized nodes, no reference anywhere. The
tier-3 vocabulary carried the scene: each family encoded the structure a model cannot
re-derive (star = halo/rays/core, cypress = scalloped taper + wisps, house = body/roof/
window on a tangent frame, hill = stacked far-light bands).

**The minimal addition that makes it comfortable:** a spec-level `generator` bridge —
"this node is back-end generator X with these resolved params, give me its bounds" —
plus promoting the three relations `flow`, `distribute-along`, `jitter-grid` to first-class
forms (they exist once each inside a family today). With that, Starry-Night complexity is
not just expressible but ergonomic; without it, every new family pays a hand-written
bridge + anchor fee.

**Honest limitations:** the village is *legible*, not *beautiful* — houses are boxes and
the roofs are flat triangles; character (chimneys, dormers, eaves) would need the family,
not the spec. The swirls read as coils rather than van Gogh's brush comma-shapes — a
closer `flow`-field over the same centre would do it, but 9 iterations were enough to
answer the abstraction question. This was judged by one agent's look-pass each iteration
(no fresh-context reviewer available in this run; check bundle is in
`evidence/starry/check/` for one).

## Render paths per iteration

| iter | path | fix |
| --- | --- | --- |
| v1 | `evidence/starry/v1.png` | first full scene: all families, eye-hole swirls, invisible cypress, flat village |
| v2 | `evidence/starry/v2.png` | cypress wider/lighter + rim, village bigger |
| v3 | `evidence/starry/v3.png` | swirl centre cap (no eye-pupil) |
| v4 | `evidence/starry/v4.png` | cypress scallops (lobes 4, scal .24), wisps bigger, roofs taller |
| v5 | `evidence/starry/v5.png` | sky wind via `strands` → reads as scratches (negative result) |
| v6 | `evidence/starry/v6.png` | `flow` family (curved ribbons) replaces strands |
| v7 | `evidence/starry/v7.png` | village warmth: town-glow halo, more lit windows |
| v8 | `evidence/starry/v8.png` | cypress rooted in foreground band |
| v9 | `evidence/starry/v9.png` | top-gap star; **final**; byte-identical determinism check |

Check bundle: `evidence/starry/check/` (reference-free: draft.png + report.txt).
