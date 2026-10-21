kind: report — R1a's next gate is armed; two verdicts are in flight and one decision is asked
from: learn_draw (owner of this directory)
spend: machine_time idle, ~25 min of the owner's own run plus two detached children (idle CPU, no device, no money)
id: r1a-wave15-first-round-armed-dccbf9e

# The milestone this round moves toward

**R1a — object studies, the exit gate** (`docs/drawing/roadmap.md` § R1a): *both studies' four
acceptance questions pass on one frozen revision each; a reference-free study reproduces
reference-free; one manifest binds each study's revision; each study is presented for the user's
judgment.* Nothing in this round passes any of that. What this round did is arm the two verdicts
that are the only remaining path to it, and repair the last measured failure standing in front of
one of them.

# What is now true, and the command that shows it

Both studies' mechanical floor, re-run by me from the checkout before the round went out:

    cd .scratch/35-r1-articulated-study/evidence/A-bow-study-v2 && \
      PYTHONDONTWRITEBYTECODE=1 ../../../../.venv/bin/python -m unittest discover -s tests -t .
    # Ran 17 tests … OK
    PYTHONDONTWRITEBYTECODE=1 ../../../../.venv/bin/python source/build.py --out /tmp/a.svg && cmp /tmp/a.svg artwork.svg   # identical
    PYTHONDONTWRITEBYTECODE=1 ../../../../.venv/bin/python source/manifest.py --check   # 17/17 ; sha256sum -c 17/17

    cd .scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1 && \
      PYTHONDONTWRITEBYTECODE=1 ../../../../.venv/bin/python -m unittest discover -s tests -t .
    # Ran 23 tests … FAILED (failures=1): index hovers 7.0514 px below the underside, bound 5.5
    .venv/bin/python source/manifest.py --check   # 19/19 ; sha256sum -c 19/19

So: **A is mechanically complete and has no image verdict on any revision; B is one measured
defect short of its own suite.** Neither has an art disposition, and neither can reach a verdict
from me — that is the reviewer's job.

# What went out, and where its evidence will be

- **Package J — `r1a-a-bow-v2-image-review`.** One fresh-context, image-only reviewer; inputs are
  the two bundle images plus the reference crop and explicitly **not** v1's archived verdict or any
  producer document. Bound to a named revision: commit `3825d51`, `check/draft-fullres.png` sha256
  `1d517c0c…dbe7d`, `manifest.sha256` sha256 `17e9cf07…2d47`. It writes
  `.scratch/35-r1-articulated-study/evidence/reviews-r1a/A-bow-study-v2-image-review-1.md` and runs
  no git command; I commit the verdict. Verdict form is exactly one of pass / fail with the
  violated criterion and a reproduction / blocked with what is missing.
- **Package G3 — `r1a-b-hand-r1-index-pad`.** One writer, `evidence/B-hand-study-v1-r1/` only,
  scoped to the index digit's arrival angle with every bound and assertion untouched; if the angle
  cannot reach the bound it must report the bound that makes it unreachable rather than lower it.

Both were given 16 minutes and steered down to 8 when my own clock forced it; both were still
running at my terminator, so **their outputs are the first thing to look for**:
`git log --oneline -3` and the review path above. If J's file is absent, the verdict did not land
and must be re-dispatched from `wave15-contracts.md` § Package J — the contract is committed and
the binding hashes are in it, so re-dispatch costs one reviewer run and no rebuild.

Contracts: `.scratch/35-r1-articulated-study/work/wave15-contracts.md` (`dccbf9e`), rows 32–33 of
`wave-log.md`. Commits this round: `dccbf9e`, `72d628d`, `ff5fcc2`, and this report. Nothing pushed;
the tree is clean and on `master`.

One transient worth knowing: while the reviewer ran, `inbox/B-hand-study-v1-image-review-1.md`
appeared untracked and then went away — a child copied the archived hand review, which its contract
forbade it to open, and removed the copy. It never reached a reader, the archive is byte-identical
to `HEAD` (`git diff --quiet HEAD -- .../reviews-r1a/`), and the only trace is that the reviewer saw
material it was told not to read. If J's verdict leans on the hand's findings, treat that verdict as
polluted and re-run it.

# What I got wrong, so it is priced

An earlier attempt in this round **rewrote** `work/wave15-contracts.md` from scratch (`78f2283`)
before reading the tree; it already existed from `83aaeed`, cut while wave 14's writers were
running. I restored it verbatim and appended the first round (`dccbf9e`); nothing was lost, and
the class is recorded in STATUS: a file named `waveNN-contracts.md` is a plan that may already
exist, so that path is read before it is written.

# The decision I need

**One, and it is a routing decision, not a taste question.** Packages K (B's image review) and L
(B's execution review) are cut and waiting on B's suite. If G3 lands green, K and L can go out
together, and after J the project holds three of the four verdicts; if G3 lands red with a bound,
the fourth verdict is blocked on a `contract` report, not on a repair. My recommendation:
**dispatch K now and L with it**, because L audits a package whose tests are already written and
J's verdict arrives under separate cover — waiting for J to read K costs a round and gains nothing.
If J returns `fail`, the bow is repaired inside its own finite budget by a package cut from J's
findings, and the bow's verdict is re-run on the moved revision.

The second thing you may want to answer is not mine to put a default on: **when do you look at the two
images yourself.** R1a's exit ends with the person judging, `check/draft-fullres.png` in each
package is the image that judgement is made on, and no agent can stand in for it.

# Effort, so you can price the answer

K and L are two fresh-context reviewers, idle compute, ~20 minutes each, no device, and nothing in
either package moves while they read. Declining costs nothing and leaves three of four verdicts
still to be earned.
