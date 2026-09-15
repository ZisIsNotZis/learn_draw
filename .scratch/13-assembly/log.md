# 13-assembly — log

## 2026-09-15 — M1: recover the baseline's composition

**Outcome: M1's exit criteria are met; the baseline is NOT promoted.** M1's job was to stop the
project sitting below its own bar and to give every later milestone a measured-correct frame. It did
that. It did **not** produce a better drawing than the 2026-09-11 baseline — with flat masses and no
line work it could not, and requiring that of it would have made the milestone unreachable
(see `STATUS.md` D7/D8, roadmap M1).

| | coverage | edge_f1 | color_dist | coarse-grid distance (8×8) |
| --- | --- | --- | --- | --- |
| target (image.jpg) | 1.000 | — | 0 | 0 |
| **baseline** (2026-09-11) | 0.514 | 0.252 | 62.8 | **32.6** |
| night's "FINAL" (`full-v2`) | 0.091 | 0.082 | 109.4 | — |
| **M1** (`evidence/m1-final.png`) | **0.528** | 0.082 | 68.8 | 39.1 |

So: coverage above the baseline (+0.014, nothing deleted), colour 6.0 units further off, and still
7 grid units behind on overall mass distribution. The ratchet stays where it is.

### Iterations (every render looked at; metrics as alarm only)

| iter | change | coverage | grid (8×8) | verdict |
| --- | --- | --- | --- | --- |
| v1 | first assembly from measured masses (17 nodes) | 0.497 | — | two real diagnostics; field as a bbox-fit ellipse over-filled by 56% |
| v2 | field area-matched; `hair-left` slab → thin stroke; bow → 2 loops + knot; poms recomputed from `on(t)`; petals added | 0.523 | 39.4 | diagnostics clean; **best up to here** |
| v3 | trim the clipped petal | 0.523 | 39.4 | diagnostics clean |
| v4 | enlarge the cream mass toward the measured deficit | **0.502** | 43.2 | **worse — rolled back.** The missing cream is behind the bow and hair: an occlusion problem (M3), not a size problem |
| it5 | enlarge the field toward the measured mint mass | **0.528** | **39.1** | **best — kept** |
| it6 | + `hair-cap` over the skull | 0.528 | 39.4 | slightly worse — dropped |
| it7 | hair reshaped from the reference's measured band profile | — | **42.8** | **much worse — rolled back** |

### Two findings worth more than the milestone

1. **A per-element centroid is a diagnostic, not an objective.** it7 moved the hair centroid from
   `(0.825,0.472)` to `(0.770,0.440)` — much closer to the reference's `(0.713,0.348)` — and made the
   drawing *worse* (grid 39.1 → 42.8). Optimising the indicator against the evidence is exactly the
   failure the project banned in invariant 4, migrated one level up. Filed as `principles.md` P25.
2. **A gate can be wrong, and finding that out is a result, not an excuse.** M1 was gated on
   `edge_f1 ≥ best − 0.01`, but M1 is *defined* as flat masses, so the floor failed it for doing its
   job — and pressure to pass would have pushed M2/M3 work into M1 (the "one ticket doing several
   things at once" failure that got 05 frozen). The gate was split into an alarm that applies always
   and a detail floor that applies once detail is the job, and promotion was separated from milestone
   exit. Recorded as a spine change (D7), not quietly relaxed.

### Reviewer evidence (G3)

Two fresh-context reviewers given the target plus the two renders under neutral names:

- both agreed the **baseline is the better drawing** (finish: eyes, line work, hands, collar);
- they **disagreed on composition** — one said the baseline, one said M1.

Per P7 the disagreement was settled by measurement, not by picking a verdict: the coarse-grid
colour-mass distance puts the baseline ahead (32.6 vs 39.4), agreeing with the first reviewer. The
per-element table (`evidence/m1-placement-check.txt`) shows *why* the two disagreed so easily — M1 is
closer on 7 of 13 masses, several decisively:

| element | target | M1 | baseline | closer |
| --- | --- | --- | --- | --- |
| skirt dark | (0.474,0.878) 7.8% | (0.480,0.864) 9.1% | (0.682,0.662) **0.6%** | **M1** — the baseline barely has the dark skirt at all |
| head/face | (0.675,0.321) 1.2% | (0.676,0.312) 1.3% | (0.670,0.338) 1.5% | **M1** |
| bow magenta | (0.656,0.510) 1.5% | (0.655,0.509) 2.8% | (0.664,0.496) 1.6% | **M1** |
| petal pink | (0.317,0.885) 2.7% | (0.367,0.909) 3.8% | (0.272,0.806) 1.1% | **M1** |
| ribbon blue | (0.245,0.492) 1.0% | (0.279,0.333) 3.8% | (0.066,0.689) **0.1%** | **M1** — the baseline's ribbon is missing too |
| blouse pale | (0.738,0.559) 3.5% | (0.771,0.578) 2.9% | (0.736,0.558) 2.8% | baseline |
| hair blue | (0.713,0.348) 7.5% | (0.825,0.472) 8.2% | (0.785,0.325) 8.0% | baseline |
| mint field | (0.409,0.572) 17.6% | (0.334,0.546) 14.7% | (0.322,0.614) 14.8% | baseline |

The honest reading: M1 fixed real composition errors the baseline has (dark skirt mass, ribbon, bow,
petal mass, face position) and inherited others (under-sized mint field, hair too far right and low).
The baseline wins the aggregate because it spreads the right colours more evenly, not because its
figure is better placed.

### Gate results

| gate | result |
| --- | --- |
| G1 render + bundle | ✅ `evidence/check/` (1:1 draft + subject-weighted crop listed) |
| G2 alarm | ✅ coverage 0.528 ≥ 0.514; color_dist 68.8 ≤ 77.8 |
| G2b detail floor | ✗ edge_f1 0.082 vs 0.252 — **not gating in M1** (D7) |
| G3 placement | ⚠️ partial — 7/13 masses closer than the baseline; recorded above, not claimed as a pass |
| G4 diagnostics | ✅ none |
| G5 authoring budget | ✅ 17 nodes, all with intent; no outline > 4 points; spines 2–3 points |
| G6 determinism | ✅ byte-identical (`53ffff46…`) |

### Carried into M2

- The hat's two-tone brim meets in a straight seam through the brim centre (the family's slice split)
  where the reference's boundary is diagonal; the crown barely separates from the navy brim.
- `hair-left` is still a straight thin stroke; the reference's left sweep is a curved wisp.
- The gate has now been exercised end to end once, including the split-reviewer case.

### Evidence

- `evidence/m1-final.png` (the milestone artifact), `evidence/m1-v1..v3.png` (iteration history)
- `evidence/check/` (G1 bundle + report with the ratchet delta)
- `evidence/m1-composition-reference.txt` (G3 reference measurement)
- `evidence/m1-placement-check.txt` (G3 placement table + grid distances)
- `work/measure-composition.py` (the G3 instrument — reusable, deterministic, no verdict)
