# reviews-r1c — the independent reviews of the whole figure, and what they bind to

This directory holds the rubric reviews of `A-full-figure-v1` and `A-full-figure-v2`. A review is a
record: it is not a fact document and it does not change `docs/`.

## The v1 pair

Binding: commit `bfba8e7`; `artwork.svg` sha256 `b3ca14fd…`; `check/draft-fullres.png` sha256
`89133fe4bda3d5b839a277bf3b3c6ad437356052fb4121016b9b14b6e25b5707`.
The SVG rebuilds byte-identically; the PNG re-renders to within antialiasing (166 pixels differ, max
channel delta 7). Reviewers: `gemini-3.8-flash` and `gpt-5.6-sol`, fresh context, given the target, the
draft and `docs/2_GOAL.md` only; each proved sight on the target first.

| axis | reviewer 1 | reviewer 2 | state |
| --- | --- | --- | --- |
| A subject identity | 3 | 3 | 3 |
| B human figure | 3 | 4 | 3.5 |
| C silhouette coherence | 2 | 3 | 2.5 |
| D feature legibility | 0 | 3 | **contested (Δ3)** |
| E occlusion correctness | 4 | 5 | 4.5 |
| F style and composition | 3 | 1 | **contested (Δ2)** |

Both named the hand (fingerless mitten at ~(845,820)), the unreadable viewer-left shoulder, the deleted
background, the frontal face, and — the strongest — **the figure does not read as seated**: the dark
mass sits detached at the left of a symmetrical dress bell.

## The v2 pair (after W1–W2)

Binding: commit `90ff009`; `artwork.svg` sha256 `82e5d2d44f58cc35578c1922fec54452ec0ccac7b276d5b8fadeee6370288405`;
`check/draft-fullres.png` sha256 `23868cd79cebe2a841b97626063e17a834a1b5d5c4c0b79f10def97d6111e355`
(1024×1024). `manifest_full.py --check`: 26/26 entries OK. Reviewers: `gpt-5.6-sol` and
`gemini-4-argon`, fresh context, same input discipline.

| axis | reviewer 1 (sol) | reviewer 2 (gemini-4) | state |
| --- | --- | --- | --- |
| A subject identity | 3 | 3 | 3 |
| B human figure | 4 | 4 | 4 |
| C silhouette coherence | 3 | 3 | 3 |
| D feature legibility | 3 | 1 | **contested (Δ2)** |
| E occlusion correctness | 5 | 4 | 4.5 |
| F style and composition | 4 | 3 | 3.5 |

**Progress against the v1 point, axis by axis:** B 3.5→4, C 2.5→3, D's resolved point is still
contested but the composition improved, F 2.5→3.5, E held, A held. **The advance is real and short of
the R1c targets** (A≥4, C≥4, D≥4).

### Binding anomaly in reviewer 2

It treats `draft-fullres.png` as 2048×2048 and gives coordinates in that space; the file is 1024×1024
(measured). Its target sight proof is sound; its doubled coordinates are halved when read, and its "tiny
almond slits" description of the eyes is not what the 1:1 file shows (the eyes are ~52 px wide). Its
structural observations are used; its D=1 is contested, not adopted.

### What both v2 reviewers name, independent of the rubric

- **The lower half is still the failure**: a pale mint wedge dominates, the dark navy skirt mass is a
  narrow strip / wire loop, so the lap does not read; the reference is the reverse — a dark lap mass
  with the pale apron on top and the pink/orange ribbons crossing it.
- **The face is startled, not shy**: eyes round and frontal, the gaze not down, a jagged fringe and a
  sharp chin.
- **The bow is a rigid tube** (two reviewers across both rounds), not soft ribbon loops with two tails.
- **The hair is stiff rails**, not flowing locks.
- **The left field lost the reference's wave curl and the mid-frame streamers**; three thin squiggles
  stand where the reference has masses.

## Files

- `A-full-figure-v1-image-review-1.md`, `-2.md` — the v1 pair, full text.
- `A-full-figure-v2-stage3-image-review-1.md` — the W1-stage review; **void as a score** because its
  descriptions of the eyes and bow are not of that revision, kept for its three true structural
  observations.
- `A-full-figure-v2-image-review-1.md`, `-2.md` — the v2 pair, full text.
