kind:    report — the next advance is stated and cut, not launched; one decision asked (when the writer slot opens)
from:    learn_draw (owner of the go package)
to:      root
spend:   machine_time, idle class, no device held exclusively; ~20 min of my own run, no writer and no
         reviewer dispatched, no money, no person-attention
id:      contract `inbox/2026-10-21-stop-point.md` (read, landed, deleted at `4050e4d`) -> wave 16

## The milestone this moves toward, and where it now stands

**R1a — object studies, the exit gate** (`docs/drawing/roadmap.md` § R1a): both studies' four acceptance
questions pass on one frozen revision each; a reference-free study reproduces reference-free; one
manifest binds each study's revision; each study is presented for the person's judgement. Nothing in
this session passes any of that. What it does is answer the condition your stop-point contract put in
front of the next build — *state, before it builds, what would make the crossing read as wrapping
rather than as a tab* — and leave the package that follows from that statement dispatchable as written.

## What is now true, and the command that shows it

    cd .scratch/35-r1-articulated-study/evidence/B-hand-study-v2-rimwrap && \
      PYTHONDONTWRITEBYTECODE=1 ../../../../.venv/bin/python -m unittest discover -s tests -t .
    # Ran 28 tests … OK
    head -1 check/report.txt
    # joint audit: cross_px 3527 / floor 2175 (dish outline 217540 px, 1.62 %), contour_breaks 0 of 6 … -> PASS

So the hand's crossing exists with its floor met and its art verdict is failure route (a). The bow is
untouched: your order — the hand repaired before the bow's fourth attempt — is honoured, and the bow's
fourth attempt stays refused as the next thing, not forever.

**The statement, in one paragraph** (`work/wave16-contracts.md` § 2). H2: a crossing reads as a wrap
only where four things are visible at once in the picture's plane — a **crest**, the digit's silhouette
rising above the rim's top edge so part of the finger is seen against what lies beyond the plate; an
**overshoot**, the pad's outline continuing past the rim's inner corner and ending on the bowl; the
**two-term order** already measured; and a **press**, a junction where the surface yields under the tip.
The rim-wrap has the third alone, and that is exactly why 3527 px against 2175 is green while the
reviewer still says "pasted-on tab": the whole crossing sits inside the dish's fill, the pad stops at
the inner corner, and nothing at the junction says the surface is pressed. Each new term is given a
number with a control that turns it off (crest ≥ 30 columns and ≥ 8 px high, overshoot ≥ 12 px, a
2–3 px contact band across ≥ 80 % of the pad's width plus shading stepped within ±2 px of the pad's
outline), so the next picture is judged on shape by measurement *and* by a fresh eye, and a floor met
with a tab is failure route (a) again. The floor, the mixed-order rule and the joint route are held
fixed, as you ordered.

**Package P (`r1a-b-hand-v3-wrapshape`, writer) and package Q (its fresh image-only review) are cut,
with the seven contract lines, and unlaunched.** Nothing in this session dispatches them: 25 minutes of
wall clock with a 15-minute cut-off is less than this harness has ever needed for a writer (~20 min),
and a killed child writes nothing — your own words from the stop-point contract.

## The premise that was wrong, corrected with the command

A belief carried into this session was that `B-hand-study-v1` produced no artefact and should be
treated as never run. It is false, and I checked it before acting on it:

    cd .scratch/35-r1-articulated-study/evidence/B-hand-study-v1 && \
      PYTHONDONTWRITEBYTECODE=1 ../../../../.venv/bin/python -m unittest discover -s tests -t .
    # Ran 23 tests … OK
    sha256sum -c manifest.sha256            # 19/19 OK
    sha256sum artwork.svg check/draft-fullres.png
    # cce47a84… artwork.svg ; e428bb0d… check/draft-fullres.png

**Where it is:** `.scratch/35-r1-articulated-study/evidence/B-hand-study-v1/` — 21 tracked files,
`artwork.svg`, `artwork.png`, `check/draft-fullres.png`, `manifest.sha256`, `source/`, `tests/`.
**What verifies it:** the commands above, and the binding line of its archived verdict
(`evidence/reviews-r1a/B-hand-study-v1-image-review-1.md`), which is bound to `5e12d36` and to
`check/draft-fullres.png` `e428bb0d…` — the same hash the tree carries now, so the artefact is the
revision that review BLOCKED, not a later or a missing one. The three documents that claim it exists
are right and are left standing (`STATUS.md`, `evidence/acceptance-ledger.md`, `work/wave-log.md` row 24).
Re-dispatching it would rebuild a study that already ran and already has a verdict; what is short is its
*repair's picture*. I record this as a correction rather than a re-dispatch, and the check is the command,
not a search.

## What I did not do

No writer, no reviewer, no bow v4, no second digit, no gate moved, nothing in front of the person,
nothing read from or written to `work/holdout-brief.sealed.md` (still sealed until R1a's two studies
exist — it was not opened), nothing outside `learn_draw/`, nothing pushed.

## The decision I need

**One, and it is a routing decision about the writer slot, not a taste question: does the next session
open with package P, or does the person's eye come first.** Package P is one writer (~20 min idle) plus
one reviewer (~12 min idle), and it is the only thing in R1a that is currently unblocked — the bow has
no path without its own decision, and the hand has no path except this one. My recommendation, offered
as inference: **run P now**, because H2 is the first hypothesis in five verdicts that names the missing
thing in the picture's own terms rather than in a metric's, and because a fail is cheap and informative
(it would put failure route (a) at the shape route, not at the joint route). The alternative — show the
person the rim-wrap's picture as it stands with its verdict attached — spends his attention on an image
its own reviewer already called a tab, which is the thing your ruling of 2026-10-21 stopped.

The second thing is still not mine to put a default on: **when he looks.** R1a's exit ends with him
judging, and there is no picture in the tree worth his look until P's review lands.

## Effort, so you can price the answer

P and Q are one writer and one reviewer, idle compute, ~32 minutes total, no device, no money, nothing
for the person. Declining costs nothing and leaves R1a where it is: a floor met and no picture that
reads.

## Evidence pointers

- `git log --oneline -1` → `4050e4d` (this wave's contract and the correction; tree clean on `master`,
  nothing pushed).
- [`work/wave16-contracts.md`](.scratch/35-r1-articulated-study/work/wave16-contracts.md) — § 1 the
  re-verified state, § 2 the statement with each term's observation and control, § 3 package P, § 4
  package Q, § 5 what the wave does not do.
- [`evidence/reviews-r1a/B-hand-study-v2-rimwrap-image-review-1.md`](.scratch/35-r1-articulated-study/evidence/reviews-r1a/B-hand-study-v2-rimwrap-image-review-1.md)
  — the verdict H2 is written against, in the reviewer's own words.

---

**Superseded, not answered.** The person's direction of 2026-10-23 moved the advance to the full figure
(`evidence/A-full-figure-v1/`), so the question this message asks — package P or the person's eye first — no
longer routes anything: his eye came first by his own instruction, and P stays cut and unlaunched.
Moved here from `mail/`, where an upward report does not belong. `STATUS.md` carries the fact.
