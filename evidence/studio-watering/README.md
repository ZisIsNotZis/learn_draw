# A person watering a plant — interaction beyond separate icons

## Intent and boundary

An original flat illustration should show a person by a window actually holding a watering can
and pouring into a planter. This tests support/grasp, pose, material cues and spatial grouping.
It is authored geometry, not a reference copy or generated bitmap. The Studio engine is unchanged
from c686e3b, fingerprint 0cc7aaea74f48c03ebcbb080d3adf42d3d1de2618d36493e2407c17b8085903b.
The accepted simple head preset is reused; its earlier human acceptance is not scene acceptance.

## What was authored and actually revised

build_first.py generated the initial 21-part relational scene using existing presets, masses and
strokes. Two global frame placements establish person/window; other parts mostly use named pins.
The prior version build-before-aspect-refusal.py was refused for a width ratio of 21. Long shallow
window members were instead expressed by existing flat-cap strokes. No engine range was changed.
These are frozen build records; do not rerun them over the live working.json/history.

01-first has a visibly misplaced stream and an open greeting palm over the handle. Public logged
edits 02/03 raise the spout, and 04/05 send the stream into the planter. The first fresh critic
recognizes watering but rejects the implied open-palm support: the can appears suspended.

06/07 inspect and remove that hand while retaining the vessel and stream in place. 08/09 shape a
compact colour mass; 10/11 inspect both wrist mounts and join it to the sleeve. 12/13 attach the
vessel beneath the new hand. 14 proposes a crossing thumb and one finger fold using two existing
strokes. 14-grip-detail is the actual selected hand closeup used during authoring. This is a
root-authored custom insertion group, not a public multi-node insertion command.

Both closed-grip critics still find the pouring attitude weak and the grasp schematic. 15/16
inspect and lift the carrying wrist with its shoulder fixed; all held descendants follow. 17/18
tip the reservoir toward the plant and 19/20 lower the outlet. This exposes a floating free end of
the handle: a one-point pin does not inherit the parent's rotation. 21/22 visibly move that free
terminal down onto the vessel while protecting its root. 23 adds a soil opening and related stem/
leaf depth changes, so the water has an actual projected landing plane. This is a second explicit
root-authored compound proposal, not a general transaction feature.

The pour review pair finds direction/destination legible but still asks for an explicit grip.
24/25 thread the handle between palm and thumb depths and increase its bow without moving ends;
26/27 soften the rectangular knuckle mass. All clean proposals were viewed before CLI acceptance.
run.py records the logged public CLI edits/inspections. The direct 14-grip-detail inspection
was outside that logger; its actual scene/report/images remain. The initial relational draft, the two compound
proposals and verifier use the model/render API; this study does not claim CLI-only authorship.

## Current image disposition

open-hand-review.md is the first fresh critique. closed-grip-review-a/b.md preserve the intermediate
pouring/hand failures. pouring-review-a/b.md recognize the corrected pour but retain the hand's
ambiguous enclosure. threaded-grip-review-a/b.md are the final fresh image-only pair: both see a
readable watering action without a structural blocker; grip certainty remains the weakest part.
The hand can read as a hooked grip but is crowded at thumbnail size. Stiff gesture, detailed
head versus unoutlined body, the window crossbar behind the contact, and tube-like water remain
refinements. This is bounded flat-illustration evidence, not a general closed-hand rig, mastery of
anatomy, finished-portrait acceptance or human taste approval. The user's optional scene-level
style question is pending asynchronously; silence is not acceptance.

## Rebuild and inspect

Run from any directory with the locked environment:

    python examples/studio/watering.py --outdir FRESH

Use the repository script's absolute path when outside the repository. It creates an editable
working.json and actual clean/alignment/grip-detail views, and refuses an existing output directory.
The current semantic input is examples/studio/watering.json. verification/fresh-cwd ran the helper
from an empty working directory with no reference image and reproduced the observed PNG exactly.

verify_current.py rebuilds working.json and checks repeat SVG/CPU PNG identity, water endpoint in
the projected soil, a descending stream, both handle end-cap contacts and palm/handle/thumb depth
order. These are construction facts, not fluid dynamics, load-bearing proof or image judgment.
The inherited 113-test engine suite was passed in the preceding source commit; no engine was
modified here and those tests were not gratuitously rerun for picture edits.

## Independent edit test and next design question

usability/ holds a fresh operator given only the previous skill, public help and this scene. It
moves the person left while preserving a working pour. It read the old frozen skill, public help
and supplied scene only. The newer interaction reference was written afterward from the observed
evidence; that new teaching branch is not claimed as independently forward-tested.

The root's handle drift after tipping the vessel and the operator's stream drift after moving the
person expose a specific limit: one-point attachment preserves one point, not both ends of a bridge.
Current terminal editing can repair a static drawing. A two-target gesture would preserve a
semantic connection during later changes; it should be tested against these actual edits, not
sold as a general physics or gripping solution.

The independent operator accepted three visible edits: person left .05, free water tip right .065,
then up .008 after inspecting a near-rim landing. The first intermediate breaks the pour and is
explicitly retained as such. Actual corroboration in verification/independent-reframe.json checks
12 stationary parts, 11 translated held parts and the restored spout/soil relation; actor PNG
rebuilds exactly. Fresh image-review-a/b in usability/ retain grip uncertainty, joint stiffness,
framing and line-language mismatch while finding the spout-to-soil action coherent. This is
reframing from a supplied scene, not independent generation of the complete new subject.

The published example helper also refuses an existing directory without changing its working
scene; verification/example-safety.json records this actual check. The drawing skill validator
passed after adding the selectively disclosed object-interaction reference. Human feedback remains
pending, and the legacy portrait/baseline were not replaced or promoted.
