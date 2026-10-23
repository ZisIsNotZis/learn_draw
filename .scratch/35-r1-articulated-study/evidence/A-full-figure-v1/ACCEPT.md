# A-full-figure-v1 — the acceptance line, written before the build

**Why this file exists.** The person's direction of 2026-10-23 says the only output that works is
`A-cloth-v8/artwork-a.png`, that it is to be continued directly, and that the bar is *"at least until a
full image"*. Self-supervision is delegated, which means the thing a self-review fails against has to be
written down before any iteration runs. This is that line. It is the accept for this package and it does
not move to fit what the code can produce; the code moves to it.

Nothing here asks the person for a verdict. The person gets one thing: the finished figure.

## The target

One image, 1024×1024 — the reference's own frame — of the same girl, from the same viewpoint, made of
parts this project already has (the `A-cloth-v8` torso, its bow, its collar, its sleeves, its hand
studies) plus the parts the torso crop could not contain (hat, upper head, face, hair mass above the
crop, skirt, legs, arms). Every part stays traceable to the study that authored it; every number in the
build comes from a relation or a generator, and the build reads no image.

## The accept line — seven terms, each decidable by observation

| # | term | how it is observed | floor |
| --- | --- | --- | --- |
| T1 | **it is a whole figure** | the drawn figure has a top and a bottom inside 1024×1024: the hat crown clears the top edge by a margin and the seated lower mass reaches the bottom edge; the figure's silhouette bbox covers ≥ 88 % of the reference figure's bbox in each dimension | bbox ratio, both axes |
| T2 | **the parts are all present** | every named object in `source/full/figure.py:OBJECTS` has its part in the scene and its fill region in the render: hat brim (two faces), crown, two puffs, back hair mass, fringe, two falls, two locks, face, neck, two eyes (lid, iris, iris shade, catchlight), brows, mouth, sailor collar, bodice, chest bow, both sleeves and cuffs, right arm, hand, skirt, skirt fold, underskirt, two lining bands | inventory test fails if one is missing |
| T3 | **proportions** | measured on the render: head (chin→crown) ÷ frame height, shoulder width ÷ frame width, hat brim width ÷ frame width, and the eye line's height ÷ frame height are each within ±15 % of the same ratio measured on the reference | four ratios |
| T4 | **the hat/hair/bow relationship** | the brim overhangs the face on both sides; the hair falls pass *in front of* the shoulders and *behind* the brim; the chest bow sits on the collar's V, not on the bodice's chest; the two puffs sit on the brim, not floating off it | four relations, each a yes/no on the render |
| T5 | **the palette is hers** | eight fills sampled from the render match the reference's own values within ΔRGB ≤ 28 per channel: hat navy, hair lit, hair shade, skin, dress cream, bow magenta, cuff navy, background teal | eight samples |
| T6 | **it reads as her** | my own side-by-side: I name every mismatch I can see against the reference, ranked by whether it changes identity or only craft; a round ends when the identity list is empty | named list, then empty (`review-log.md`) |
| T7 | **the discipline holds** | byte-identical rebuild, manifest verifies, no image library and no image read in `source/`, every part declared in `OBJECTS`, the sealed brief unread | tests |

T6 is the only term a machine cannot decide, so it is the one I run myself, in rounds, against the
reference. Rounds are numbered; every round's mismatch list is kept in `review-log.md` with the render it
judged, so an iteration that made the figure worse is visible rather than remembered.

## What I do if three rounds do not improve it

The figure is compared round to round by the two things that can be counted — the T3 ratios and the
count of *identity-level* entries in the T6 list. If round 3's identity list is not shorter than round
1's, I stop grinding and report the blocker concretely: which term fails, on which render, what each
attempt changed, and what the next attempt would have to assume that I cannot verify alone. A blocker
report names the part, its numbers and the two routes I rejected, not "it still doesn't look right".

## What is out of scope here

No tracing or sampling from `image.jpg` in the build (the reference seeds authored numbers once, then is
closed — and the build proves it by running with the image absent). No new object study. No change to
`A-cloth-v8` or any other package's bytes. No bow v4 and no further hand variant. The sealed brief at
`.scratch/35-r1-articulated-study/work/holdout-brief.sealed.md` stays closed.

## Where the starting point is, exactly

- The continued render: `.scratch/35-r1-articulated-study/evidence/A-cloth-v8/artwork-a.png`
  (`sha256 da9d92c9…`, 400×480, 13 parts, 8 objects).
- Its parts library is copied here **byte-for-byte** at `source/parts/` and is not edited; this package
  composes it into a bigger frame and adds parts. `A-cloth-v8` therefore keeps its own bytes and its own
  verdict, and every inherited part stays traceable to it.
