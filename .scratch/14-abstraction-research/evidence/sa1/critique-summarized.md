# SA1 — adversarial design critique (condensed record)

Source: fresh-context `explore` subagent, delivered via user message 2026-09-14 (night-research
session, ticket 14). The reviewer read all docs, 06's resolver + spec + evidence, the ladder tickets
08–13, and the in-flight 14 forks. It edited nothing. Full text was in the session transcript; this
file preserves every finding's claim and fix so it survives compaction.

## Verdict summary

12 findings. The most damaging: the language's only proof artifact (`bust-v2`) fails the project's
own review gates, which were never run on it; the docs and shipped resolver have forked (3 resolvers
in repo); the face rung is not drawable with the implemented language; several documented mechanics
don't work as documented.

## Findings (worst-first, condensed)

1. **06's proof render fails its own gates.** bust-v2: hat inside-out (dome paints over brim; the
   13px rim strip can't occlude the crown's ~28px intrusion), no face (hair-left w=0.85 head-widths
   buries the head; nothing above y≈344 visible), dismembered (shoulders detached ~70px gap; no neck;
   head→shoulders ≈290px of empty bg). Invariant 7 was never run on it; `evidence/` has no `check/`
   bundle; "diagnostics clean" became a substitute for looking. 06's acceptance also claimed
   diagnostics ("fully-occluded", "unintended gap") that were never built. Fix: run the acceptance
   retroactively; fix sunhat occlusion (near-half brim region above dome, or clip dome to far half);
   build the two missing diagnostics; stop writing "diagnostics clean" as if it meant "correct".

2. **Three resolvers have forked.** 06's relate.py + 14's face copy + 14's starry copy (7 new
   families, scene_render passthrough, `--scene`). vocabulary.md marks those families 📋 while code
   exists. The `desc` key relate.py emits is rejected by scene_render.SCHEMA (integration is NOT
   drop-in). `draw.py::_find_relate` picks last-sorted copy — behavior depends on directory names.
   Fix: promote one resolver to scripts/, delete forks, print which resolver `draw check` used, fix
   the `desc` key.

3. **Face rung not drawable; 08 acceptance tests what the tool can't express.** No eye family exists.
   Face needs: mirror/pair, inside, align, junction, arc-of-shape, taper, rotated blobs/strokes.
   Demand-first deadlock: L1 is the drawing that should force these, but they'll burn the whole rung
   budget re-deriving eyes. Fix: land the face-set relations before opening 08 (or re-scope 08);
   08's status is wrong — it depends on the vocabulary work.

4. **Documented mechanics broken.** `head@0.25` / `brim@t` documented but no `@` syntax in the
   evaluator. relate.py docstring's usage example uses `on: head` — YAML parses as boolean True; the
   tool rejects its own usage example. `between` rejects anchor strings (`{between: [head.left,
   head.right, 0.5]}` fails). Family anchors registered as `hat-brim.*`/`hat-dome.*` — no anchor for
   `hat` itself, so `{along: hat}` fails. Fix: implement `@`, coerce `between` inputs, regenerate
   docstring examples from bust.yaml, register the family id itself, match vocabulary.md's anchor
   column to emitted ids.

5. **`along` semantics lie per shape kind.** `out` is the centroid ray, not the outline normal
   (wrong at concave sides). `t` means four different things (ellipse: 72-gon from local +x — so
   `along(brim,0.25)` is the FAR edge; pom-at [0.62,0.88] lands upper-left/upper-right = magic
   numbers; blob/stroke: vertex-index lerp; width-ful blob: same spine point twice; rect: 2-point
   outline = diagonal lerp). `w` (unrotated 2rx) disagrees with `right-left` (rotated extremes) on
   the flagship tilted brim. bust.yaml's comment "tilted 14deg down to the right" is wrong: -14
   rotates the right side up. Fix: arc-length parameterize, true normals, real rect outline,
   distinct names for w vs extent, document t per shape kind, tests.

6. **"No coordinates" is unaudited framing.** bust.yaml carries ~12 literals in the sunhat line;
   13's acceptance crowns `frame.w*0.60` (an eyeballed fraction) as the gold standard. Frame-fractions
   are still absolute placement. Nothing counts/flags literals. Fix: two literal classes — proportion/
   style constants (allowed in `vars:` with provenance comment) vs placement numbers (must derive from
   anchors; resolver warns on raw `frame.*` placement outside `vars`). Enforce the ~4 budget with a
   lint or retract it.

7. **Withdrawal is promised but never trained; no composition vocabulary; gradients inexpressible.**
   No rungs for (a) same subject image-closed or (b) new subject intent-only — the entire skill of
   reference-free drawing has no practice slot. Teacher role assumes a reference exists (who sets the
   frame for a new subject?). Composition knowledge (focal/thirds/horizon/value-key) absent. relate.py
   cannot emit grad/blur/op — "sky fades toward horizon" is inexpressible. Fix: L7/L8 real rungs;
   composition anchors in taxonomy; flow/distribute/gradient work gets a demand DATE.

8. **Error contract violated in exactly the places an LLM trips.** Missing family params → raw
   KeyError traceback. check_intent → ValueError when z not in layers. No `layers:` → intent checks
   silently skip. Unknown keys in draw nodes silently ignored (opposite of scene_render's contract).
   Missing fill/ink → `fill="None"` (renders black). Unknown z silently sorts topmost. Vocab
   sub-shapes (dome/rim/poms) never anchored → P21 diagnostics don't apply. Duplicate ids silently
   overwrite. bools pass as scalars (`pom: yes` → 1). No YAML line numbers. Fix: one validation pass
   — unknown keys = hard error, missing params named in words, unknown z = hard error, anchor every
   emitted shape, duplicate id = hard error, line numbers in SpecError.

9. **SSOT drift doc↔engine.** scene-format.md's `region` example uses `on: ref` — YAML parses as
   boolean True, unreachable; and the code never reads `on` (always floods ref). `trace.fit` in
   SCHEMA + doc, never read. scene_render's "line-numbered" errors are node#idx only. T3 core idiom
   (clip + blend modes) is unimplementable — no clipPath, no blend modes in the back end. 824 vs 825.
   `eyeball` vs `eye`. relate.py's emitted SVG lacks the id/desc attributes the explainability
   contract promises. Fix: doc-vs-code audit with a mechanical check; rename `region.on` → `source:`;
   implement or delete `fit`; add clip or rewrite the idiom; pin the vertex count.

10. **"Object family" is overloaded; coordinates laundered through Python.** The catalog mixes
    anatomy (eye), pose systems (hand), flow fields (swirl), repetition laws (village), rendering
    techniques (glow) as one kind of thing. The 14 fork already shows the junk-drawer trajectory:
    seven bespoke expand_* functions, one computing house polygons in raw Python — coordinates by the
    back door. And the model cannot author a family without writing Python, which contradicts
    "learning is the repo" in spirit: knowledge becomes unreadable code. Fix: split tier 3 —
    (a) DECLARATIVE families (a family is a YAML block: params + sub-shapes whose relations may only
    use the family's own anchors — lets the model author `eye` without Python); (b) generator families
    delegating to scene_render; (c) canon rows as data with provenance; (d) a `style:` header.
    sunhat becomes the migration example.

11. **draw check drops the resolver's diagnostics.** `_rasterize` runs relate.py without --anchors
    and without capturing stdout — OFF-CANVAS/CLIPPED/CONTRADICTION print to the terminal and vanish
    from the bundle the reviewer actually sees; the resolver is never recorded. Fix: capture stdout
    into report.txt as a labeled section, append to log, record resolver path + hash.

12. **Teacher-speak gaps (the completeness bar applied).** Currently inexpressible: unpainted guide
    shapes (Loomis cross, plumb lines — every node paints; blocks the construction method vocabulary.md
    itself validates); construction hierarchy + arc-of-shape; align + mirror/pair + placement along an
    interior arc + 3/4-view asymmetry; taper (lash thick at outer corner); flow/whorl (hair falls from
    the whorl); junction (break the line where the strand crosses the cheek); value/planar language
    ("squint: three values"); edge quality ("softer edge here, lost edge there"); recession law
    ("smaller and lighter as it recedes"); fields as first-class things ("the sky swirls around the
    stars"). Priority: guides, arc, mirror/pair, align, junction, taper (face set), then
    flow/distribute/gradient/value (scene set).

## What is actually good — do not break

North-star litmus + honest ✅/🔨/📋 statuses; two orders kept separate (P20); diagnostics-as-sentences
+ anchor table (P21); the whitelisted AST evaluator with good unknown-anchor errors; YAML boolean-key
rejection with rename advice; sunhat's encapsulated structure knowledge AS A CONCEPT (fix the z bug,
keep the pattern, make it declarative); canons-as-fractions-with-provenance + "learning is the repo";
curriculum sequencing (line art first, soft fields last, one rung per skill, demand-first); the
review protocol itself — its one failure is that it wasn't run on 06's proof; use it, don't weaken it.
