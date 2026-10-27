# reviews-r1c — the independent reviews of the whole figure, and what they bind to

This directory holds the rubric reviews of `A-full-figure-v1` and, later, of the advance that follows
it. A review is a record: it is not a fact document and it does not change `docs/`.

## Binding

Both reviews below bind to the same frozen revision:

- commit `bfba8e7` (`work: figure round 28 … all seven terms pass …`)
- `evidence/A-full-figure-v1/artwork.svg` sha256 `b3ca14fddb5d693ab705812de29df400418d3dde51d9e5e1d6e56306208984bc`
- `evidence/A-full-figure-v1/check/draft-fullres.png` sha256 `89133fe4bda3d5b839a277bf3b3c6ad437356052fb4121016b9b14b6e25b5707`
- rebuild: `.venv/bin/python .scratch/35-r1-articulated-study/evidence/A-full-figure-v1/source/build_full.py --out <tmp>.svg` reproduces the same SVG bytes (2m47s on the loaded host); `scripts/draw.py check <svg>` reproduces the PNG to within antialiasing (166 pixels differ, max channel delta 7).

The reviews were dispatched with the target and the draft and no history: no `ACCEPT.md`, no
`review-log.md`, no source, no prior scores. Each reviewer proved sight on the target before scoring.

## The pair, and the contested axes

| axis | reviewer 1 (gemini-3.8-flash) | reviewer 2 (gpt-5.6-sol) | state |
| --- | --- | --- | --- |
| A subject identity | 3 | 3 | mean 3, stands |
| B human figure | 3 | 4 | mean 3.5, stands |
| C silhouette coherence | 2 | 3 | mean 2.5, stands |
| D feature legibility | 0 | 3 | **contested (Δ3)** — unresolved |
| E occlusion correctness | 4 | 5 | mean 4.5, stands |
| F style and composition | 3 | 1 | **contested (Δ2)** — unresolved |

A contested axis may pass or fail no milestone until it is settled by measurement or a third review
(`docs/4_USECASE.md`). The next advance settles D and F on a new revision by construction and by a
further review pair, not by averaging this one.

## What both reviewers see, independent of the rubric

- the hand is a fingerless mitten (both name it, at ~(845, 820));
- the viewer-left shoulder/arm does not read as attached, and the bow, hair and torso collide there;
- the background's sweeping mint wave and floating ribbons are gone, replaced by flat angular fields;
- the face is wide-eyed and frontal where the reference is shy and downcast;
- the lower mass does not read as a seated lap.

Review 2 adds the strongest single sentence: **"the figure does not read as seated"** — the torso drops
into a symmetric bell while the dark mass sits detached at the left. That is an identity-level defect,
not craft, and it is the one the roadmap's previous "T6 cleared" claim missed.

## Files

- `A-full-figure-v1-image-review-1.md` — reviewer 1, full text.
- `A-full-figure-v1-image-review-2.md` — reviewer 2, full text.
