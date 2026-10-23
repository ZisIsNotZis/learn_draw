# Wave 16 — the crossing's shape, stated before it is built

Why this file exists: root's `inbox/2026-10-21-stop-point.md` (read, landed, deleted 2026-10-23) ends the
night at one variable and one order — *the next advance moves the crossing's shape and placement and
nothing else, states before it builds what would make the crossing read as wrapping rather than as a
tab, and puts the resulting picture to a fresh image-only review. The floor, the mixed-order rule and
the joint route do not move.*

This file is that statement, and the contract cut from it. **Nothing in it is launched as of this
commit**: the session that wrote it had 25 minutes wall clock and a 15-minute cut-off, and a writer
package on this harness has never finished inside 12. The package is dispatchable as written.

## 1. The fact this wave starts from, re-verified in the tree at `17994ea`

| what | command | result |
| --- | --- | --- |
| hand, current revision | `cd evidence/B-hand-study-v2-rimwrap && .venv/bin/python -m unittest discover -s tests -t .` | `Ran 28 tests … OK` |
| its joint audit, line 1 of `check/report.txt` | `head -1 check/report.txt` | `cross_px 3527 / floor 2175 … contour_breaks 0 of 6 … -> PASS` |
| its art verdict | `evidence/reviews-r1a/B-hand-study-v2-rimwrap-image-review-1.md` | crossing present, **holds only weakly**, "pasted-on tab" — failure route (a) |
| hand, first study | `cd evidence/B-hand-study-v1 && … -m unittest discover -s tests -t .` | `Ran 23 tests … OK` |
| its artefacts and manifest | `sha256sum -c manifest.sha256` | `19/19` OK; `artwork.svg` `cce47a84…`, `check/draft-fullres.png` `e428bb0d…` |

So the hand's crossing exists and its floor is met; what fails is the crossing's *shape*. The bow is not
touched by this wave: root's order is the hand first, and the bow's fourth attempt is refused as the
next thing, not forever.

**One premise corrected, with the command above.** A belief carried into the session of 2026-10-23 was
that `B-hand-study-v1` produced no artefact and had never run. It is false: the package is in the tree
with 21 tracked files, its suite is `23/23` green, its manifest verifies `19/19`, and its
`check/draft-fullres.png` is `e428bb0d…` — byte-for-byte the revision `reviews-r1a/B-hand-study-v1-image-review-1.md`
is bound to and BLOCKED at `5e12d36`. Re-dispatching it buys nothing; the study ran, and the object
that is short is its *repair's picture*, not its existence. The three documents that were said to claim
it exists are right and are left standing: `STATUS.md` § R1 advance state, `evidence/acceptance-ledger.md`
§ R1a — object study, `work/wave-log.md` row 24.

## 2. The statement root asked for, before anything is built

H2, the shape hypothesis, stated so a writer can be judged against it and so a reviewer can refute it:

> **A crossing reads as a wrap only where four things are visible at once in the picture's plane, and
> the rim-wrap has exactly one of them.** They are: (1) a **crest** — the digit's silhouette rises
> *above* the rim's top edge, so part of the finger is seen against what lies beyond the plate rather
> than only inside the plate's own fill; (2) an **overshoot** — the pad's outline continues past the
> rim's inner corner onto the bowl's interior and *ends* there, so the eye can see where the finger
> stops; (3) a **two-term order at the near edge already measured** — the digit's contour terminates on
> the rim's inner contour and runs unbroken elsewhere (`contour_breaks 0 of 6`); and (4) a **press** —
> a junction where the surface yields under the tip, carried in the plane as a contact band on the pad's
> lower edge plus compression of the pressed surface's own shading across the pad's width.

What the rim-wrap has is (3) alone, which is why `cross_px 3527 / 2175` is green and the reviewer still
says "pasted-on tab": the whole crossing happens *inside* the dish's fill, the pad stops at the inner
corner instead of passing it, and nothing at the junction says the surface is being pressed.

Each term is decidable by observation on the delivered 1:1 PNG, with a control that turns it off:

| term | observation | floor | control (must read 0) |
| --- | --- | --- | --- |
| crest | columns in which the wrapped digit's own rasterised polygon has a pixel above the rim band's top edge at that column | ≥ 30 columns, and the crest's height above that edge ≥ 8 px at its maximum | the same measurement run on `B-hand-study-v2-rimwrap`'s pose, where the reviewer saw no cresting finger |
| overshoot | the pad's outline extended past the rim's inner corner, measured on the projected outline from the piece's own geometry, in px along the digit's axis | ≥ 12 px | the same digit on the v1-r1 underside route, which has no pad on the top surface at all |
| order | inherited unchanged: `contour_breaks 0 of 6`, `cross_px ≥ 2175` | — | inherited: the v1-r1 route falls below the floor |
| press | the pad's lower-edge band (a fill distinct from the pad's body, 2–3 px) present across ≥ 80 % of the pad's contact width, plus the pressed surface's shading stepped (not blended) within ±2 px of the pad's outline | as written | the same fill with the pad lifted 4 px off the surface must show no band |

The three new numbers are *signal with a control*, not targets (invariant 4): the writer may not tune a
figure, and a floor met with a picture that still reads as a tab refutes H2 at the shape route and is
failure route (a) again.

## 3. Package P — `r1a-b-hand-v3-wrapshape` (writer) — cut, unlaunched

- **kind** — one writer package on one frozen copy; the aim is a picture, and the numbers are its floor.
- **goal** — make the rim-wrap's crossing read as a finger hooking the rim rather than a tab pasted on,
  by adding the three terms the picture is missing (crest, overshoot, press) to the one digit that
  already crosses, and by nothing else.
- **boundary (the not-doing list)** — no bow v4 and no bow change; no second digit and no palm change;
  no palette, framing, tessellation, stroke weight or camera change; no move of the floor (`2175`), of
  the mixed-order rule, of `contact.pressed_ring`'s route or of `contact.wrap_finger`'s derivation
  apart from the pad's last knots; no change to `B-hand-study-v2-rimwrap`, `B-hand-study-v1-r1` or
  `B-hand-study-v1`, all of which stay byte-identical; no new art criterion invented by the writer; no
  art verdict claimed by the writer; nothing pushed.
- **accept** — `python source/build.py` twice gives identical bytes and the delivered `artwork.svg`;
  `sha256sum -c manifest.sha256` all OK after manifest regeneration; `-m unittest discover -s tests -t .`
  green including three new tests, one per new term, **each of which fails on `B-hand-study-v2-rimwrap`'s
  geometry** (the negative control that makes the term mean something); `check/report.txt` line 1 still
  carries `cross_px` and `contour_breaks` and adds the three new numbers, `-> PASS` on all four;
  `check/draft-fullres.png` is a fresh 1:1 render of the delivered SVG; the README names its own review
  image and the command that rebuilds it. The art gate is not the writer's: it is package Q's verdict.
- **context the child cannot look up** — the reviewer's own words are the aim, quoted here so the child
  need not be trusted with the archive: "the crossing digit has no wrapping, overshoot or contact
  shadow, so it reads as a pasted-on tab rather than a finger hooking the rim." The four earlier
  verdicts' blocking findings were each a relation **between two masses in the plane**; every green
  measurement here is one mass against a surface in space. That is what H2 fixes.
- **paths** — a new directory
  `.scratch/35-r1-articulated-study/evidence/B-hand-study-v3-wrapshape/` only. Nothing else in the tree
  may be written; if the solve cannot stay local, the package stops and reports the blocker instead of
  widening.
- **spend** — machine_time, idle class; no device held exclusively; no money; one writer, wall clock
  20 min, lands what exists at 15; one fresh reviewer afterwards ~12 min.
- **stop** — attempts 1, review rounds 1, no-progress rounds 1. At the wall clock the writer lands what
  builds and reports what does not, and no second variant is attempted before the report is read.

## 4. Package Q — `r1a-b-hand-v3-image-review` (fresh image-only judge, read-only) — chained to P

- One fresh context, sight-capable, given **one** input: package P's `check/draft-fullres.png` at 1:1.
  No producer document, no numbers, no archived verdict, no reference image, no git command.
- It prints its own binding line (path, sha256, commit) and the rebuild command
  (`.venv/bin/python scripts/draw.py check …/B-hand-study-v3-wrapshape/artwork.svg`) **before** it
  judges, so the drift class cannot recur.
- It answers two questions and nothing else: *is a finger visibly hooking the near rim — cresting it,
  passing its inner corner, and pressing it?* and *what in this picture breaks that reading?*
- Verdict form: exactly one of pass / fail with the violated term from §2 and a reproduction / blocked
  with what is missing. It writes
  `evidence/reviews-r1a/B-hand-study-v3-wrapshape-image-review-1.md` and nothing else; the owner of
  this directory commits it.
- **Stop** — one review round. A fail is failure route (a) at the shape route and goes up as a report
  with the six-finding pattern, not into a third variant inside this wave.
- **Spend** — idle compute, ~12 min, no device, no money, nothing for the person.

## 5. What this wave does not do

It does not move R1a's exit gate, does not put any picture in front of the person, does not open
`.scratch/35-r1-articulated-study/work/holdout-brief.sealed.md` (sealed until R1a's two studies exist),
and does not re-dispatch `B-hand-study-v1`, whose artefact is in the tree and verified. It spends no
writer this session: the contract is the deliverable, and the writer slot opens in the next one.
