# 1_PROBLEM — why programmatic drawing at all: the pain, the scenario, who it is for, and what the reference is for

What success means is `2_GOAL.md`; the rules that bind the work are `3_REQUIREMENT.md`; what a drawing is
made of is `5_PRODUCT.md`; milestones and the current advance are `0_ROADMAP.md`.

# EXPLICIT

## The point is the drawing, at a detailed level

The project exists to learn to draw, and its point is detailed and reasonable drawing. That is the
level at which a component is drawn and at which a picture is judged.

## His verdict is on the picture, and it is partial

His words on two delivered candidates: *"much better, maybe not the best, but at least somewhat
acceptable"* — a partial acceptance of those images as they stand, explicitly not a claim that they
are best or final. He also accepts an improvement in one part of a picture while naming another part
wrong: he accepted the improvement to hair on `M4j` and called the ribbon's position wrong there. The
candidates are `A-cloth-v8` and `B-hand-v2-r1`; the pictures and their dispositions belong to the
records.

## The bar is a full image, and the build supervises itself

His words: *"the only thing working is the body-ish image, last one, shall continue that directly, at
least until a full image, self-supervise (again, not you, that agent)"*. What works for him is a
body-ish picture of a figure, the bar he names is a full image, and the supervision of the build is
the drawing agent's, not his. The work that carries it starts from `A-cloth-v8` and lives in
`A-full-figure-v1`; the advance and its state are `0_ROADMAP.md`.

# CONFIRMED

## What he confirms reads correctly

A hand holding a dish reads as holding in both SUPPORT and VARIATION; the CONTROL panel's failure
reading is unchanged, and it reads as a near miss. SUPPORT, VARIATION and CONTROL are the three panels
of the B sheet.

# INFERRED

## Why drawing, and not image generation

The deliverable is the drawing skill, built by hand and by agent and expressed as explainable vector
graphics — SVG/CSS, never diffusion or pixel generation. It is built in three stages: recreate a
reference image, then draw with the reference closed, then draw with no reference at all. The stated
end-goal complexity is a Starry-Night-class scene drawn from intent alone.

## The scenario: one flat picture, for a viewer who has only the picture

The target of the imitation stage is a picture an outside observer can name from the image alone: a
person's upper body from below the mouth to the lap, sitting facing the viewer, wearing a white
sailor-collar blouse with a large magenta bow tied on the chest and hair hanging down both sides past
the shoulders. The neck and shoulders are one continuous form; a head sits above the shoulder line;
the shoulders slope away on both sides, round and slightly forward. There is clothing on a body: the
sleeves end at cuffs on two arms, the blouse has soft width below the bow, and the collar is a garment
part that wraps the neck. The magenta object is a small tight knot of gathered ribbon with two wide
lobes spreading from it and two tails leaving the knot, visibly crossed and turned at the knot. The hair is two masses of unequal width hanging from above the frame, narrower at their
ends than at their tops, each carrying interior strand lines, one of them passing in front of the jaw.

## Readings that make a picture a failure

Each of these an outside observer can state on the image alone. A vase, a bottle, a mannequin or a
dress on a stand. A pink column: no chin corner, no jaw line, no head above. A bow that is two closed
pills — each lobe's outline closing on itself, no interior crease, no crossing. Hair that is flat paper
ribbon — constant width end to end, square end cuts, no interior strand lines, a hole the background
colour between the masses. A neck and collar that are geometry rather than anatomy — a ring floating
around a cylinder, no trapezius slope, no skin shading under the jaw. An arm that is a sleeve with
nothing in it — no cuff band, no forearm, no hand or arm mass.

The readings carry one lesson for the project: construction, geometry and art can all pass while an
object is visibly two disconnected pieces, and it is the picture that is judged. The acceptance
questions that close that gap are `2_GOAL.md`.

## Who it is for

The person is the authority for intent and product scope. He reviews a picture together with the
reference crop and gives art feedback, and the judgement of a picture is his. What he is shown, and how
an image is bound to a revision it is shown for, is the flow in `4_USECASE.md`; what counts as success
is `2_GOAL.md`.

## What the reference is for, and what may be shown

`image.jpg` is the drawing target: a third-party anime-style illustration. The component plates
(`head.png`, `head_hat.png`, `hat.png`, `ribbon.png`, `cloth.png`, `dress.png`, `cutout.png`) are
cropped or redrawn from it. The reference serves the imitation stage and is then closed; the last stage
draws with no reference at all.

The project's own code and documentation are free software under the GNU Affero General Public License
v3.0. The reference, the plates and every render that reproduces them are not covered by that grant:
they remain the property of their rights holders and are included only as the reference a study of
this kind requires. That is the constraint on what a picture may reproduce and show.
