# conformance-log — A-cloth-v8, two measured fixes on top of v6-closeout

This package is `evidence/A-cloth-v6-closeout/` copied and brought to conformance on two
points the user's review fixed (issue 54: two sleeves, the second "not invisible, it's
just small, partially covered"; and the hair facts in `work/a-art-direction-brief.md`,
"no background-coloured hole may appear inside a hair mass").  Nothing else was touched:
every other shape, proportion, palette and composition decision is byte-for-byte the v6
decision as expressed in `source/`, and no art verdict is recorded here.

Two source files and three test files differ from v6; `README.md`, `source/build-report.json`,
`artwork-a.svg`, `artwork-a.png`, `check-a/` and the manifest were regenerated.

## FIX 1 — the second cuff's wedge survives

**What changed.** `source/parts/sleeve.py`: the left sleeve's one authored coordinate,
`LEFT["cuff_xy"]`, moved from `(95, 263)` to `(81, 271)` — 14 px along the arm and 6 px
down.  The cuff stays one whole band sewn to the sleeve's terminal section (seams S9/S10
still check out), and nothing is cut: its surviving wedge is what the depth engine leaves
in front of the left hair fall and the bow's left tail.  The justification is about the
drawing, not a metric: the second sleeve hangs a little further out of the hair fall, so
its cuff is the small, partly covered band the user asked for, instead of disappearing
under the fall.

`source/authored.py` declares the new coordinate, so the AST inventory test still holds
the source and the declaration equal.

| measure | v6-closeout | v8 |
| --- | --- | --- |
| second cuff authored area | 331.5 px² | 331.5 px² (unchanged: whole band) |
| second cuff surviving area | 3.6e-12 px² | **88.37 px²** |
| surviving as a fraction of the first cuff (539.5 px²) | 0.0 % | **16.4 %** |
| reference target (`a-art-direction-brief.md`: 345 px of 2036 = 17 %) | — | 16.4 %, inside the 10-25 % band |
| first (right) cuff surviving area | 525.85 px² | 525.85 px² (untouched) |

**Commands.**

```bash
PKG=.scratch/35-r1-articulated-study/evidence/A-cloth-v8
cd $PKG
python3 -m unittest tests.test_two_sleeves -v      # prints the fraction it measures
scripts/draw check artwork-a.svg --ref ref/crop-400x480.png --outdir check-a
```

**Test, and the pair of mutations that make it falsifiable.**
`tests/test_two_sleeves.py`:

- `test_second_cuff_is_authored_whole` prints and asserts the delivered fraction.
  It fails when the cuff is fully hidden (`< 0.10` of the first cuff) and when it is
  fully exposed (`> 0.25`).  The v6 assertion `visible < authored * 0.01` — i.e. "the
  cuff must be entirely hidden" — is retired here because it states the defect.
- `test_the_small_cuff_band_rejects_both_failures` moves the same numbers twice:
  sliding the cuff's faces back to the v6 authored coordinate `(95,263)` (+14, +8 in the
  plane) gives **0.000** and the lower end rejects it; lifting the bow ribbon and the
  hair sheet gives **0.614** (the whole authored cuff, 331.5 px² — the wholeness
  ablation) and the upper end rejects it.  The delivered drawing sits at **0.164**.
- `test_second_cuff_extent_is_a_depth_result` (unchanged, still green) keeps proving the
  authored shape is the shape that reappears when the front cloth is lifted, so the wedge
  is depth's output and not an authored cut.

## FIX 2 — no background-coloured island inside the drawing

**What changed.** `source/parts/hair.py`: the hair sheet now reaches the face where it
passes it.  The sheet is one strip of a single symmetric half width, and at this route
its edge stopped short of the face field — up to 39 px short at the left temple and about
6 px short where the sheet crosses in front of the face — leaving background showing
through a gap that the surrounding ink closed into two islands.  A generator term
`FACE_REACH = ((0.39, 0.065, 44.0), (0.62, 0.050, 14.0))` (route fraction, half window,
px of reach) adds a smooth pulse at each place, half of it as a spine shift toward the
face and half as width, so the outer silhouette keeps its position and no new coordinate
is hand-typed.  Both islands are closed by **routing the hair sheet's outline to the
face**; no cloth was added and no visibility cut was authored.

| measure (delivered 400×480 PNG) | v6-closeout | v8 |
| --- | --- | --- |
| background islands enclosed by the drawing | **2** | **0** |
| largest island | 1023 px at bbox (162,39,35,60) | — |
| second island | 17 px at bbox (243,82,4,9) | — |

**The rule, as the test applies it** (`tests/test_no_background_holes.py`): a pixel is
background when every channel is within `TOLERANCE = 6` of `assemble.BACKGROUND`
(#78a49b, the one flat composition field); background pixels are grouped as 4-connected
components; a component that touches the image border is the page's own background and is
ignored; any other component of at least `MIN_HOLE_PX = 4` pixels is enclosed by the
drawing and fails.  The rule is stricter than the requirement — it rejects *any* enclosed
background, not only one enclosed by a hair fill.

**Commands.**

```bash
PKG=.scratch/35-r1-articulated-study/evidence/A-cloth-v8
cd $PKG
python3 -m unittest tests.test_no_background_holes -v
#   artwork-a.png: 0 enclosed background component(s) at tolerance 6, minimum 4 px
#   rule applied to A-cloth-v6-closeout/artwork-a.png: [(1023, (162,39,35,60)), (17, (243,82,4,9))]
```

**Mutation evidence.** The same rule run against the previous package's delivered render
reports both islands, so the detector can fail
(`test_the_rule_fails_on_the_v6_render`, which reads
`evidence/A-cloth-v6-closeout/artwork-a.png`, read-only).  Rebuilding this package with
the reach removed reproduces exactly the same two islands:

```bash
python3 - <<'EOF'
import sys; sys.path.insert(0, "<repo>"); sys.path.insert(0, "<pkg>")
from source.parts import hair
hair.FACE_REACH = ()                      # the mutation
from source import assemble
open("/tmp/mut.svg", "w").write(assemble.render_svg(assemble.build())[0])
EOF
scripts/draw check /tmp/mut.svg --ref $PKG/ref/crop-400x480.png --outdir /tmp/mutcheck
#   -> [(1023, (162,39,35,60)), (17, (243,82,4,9))]   (restoring FACE_REACH returns 0)
```

## What stayed, and the evidence that it did

- **47 tests pass**: the 44 of v6-closeout (one of them rewritten in place, see FIX 1,
  and one new mutation-pair test added), plus the 2 hole tests.  No assertion was weakened;
  the only assertion removed was the one that required the defect.
- `source/build_a.py` exits 0 with the seam contract and anchor inventory intact:
  13 parts, 2018 faces, 18 declared joints, 0 failed, 36 anchors = 34 joint endpoints + 2
  stated non-joints + 0 unaccounted.
- Two builds into separate paths are byte-identical to the shipped `artwork-a.svg`
  (sha256 `120579a26adb1d2e4bc20cdc3a5a4559344cd637485d0bccca7510554014bba2`), and
  `artwork-a.png` equals `check-a/draft-fullres.png` from the current `scripts/draw`
  (sha256 `da9d92c9935697a6a8fa70e25f61b7a2218e7dbd414817433a8f0bd39febd38b`).
- The authoring inventory is unchanged in kind: the left sleeve still declares exactly
  one authored pair (`C`), now at its new value; `FACE_REACH` is a generator constant like
  `WIDTH_MAX` or `CURL_AMPLITUDE`, not a station.
- The bow, bodice, collar, neck, head, right sleeve and both cuffs are untouched: the
  delivered pixels differ only at the left hair fall's inner edge and under the second
  cuff.

## Unverified at this revision

- **No art verdict.**  Nobody has judged these images at this revision; `check-a/report.txt`
  lists the four images for a fresh reviewer and its metrics (edge-F1, coverage) are a
  breakage alarm, never a target.
- The reach pulses change the hair sheet's silhouette at the temple and where it crosses
  the face; the *appearance* of those two regions is a judgement this log cannot make —
  only that they are filled now and were not before.
- The hole rule uses one flat background fill and a tight tolerance.  A background island
  thinner than `MIN_HOLE_PX = 4` px would not be reported; a background-coloured fill drawn
  by the artwork itself would be reported as a hole, and no such fill exists here.
- The v6 tangent-clause limit (an outline rotating about a static anchor is not detected)
  and the two-number-literal limit of the authoring scan carry over unchanged.
