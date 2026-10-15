# S1a parent validation — in progress, not accepted

Repo master base HEAD 24693d4, dirty inherited S0/docs and user vendor work preserved. New S1a source
worker dc1c8b29-b244-4779-9ae3-a654b6309946 completed. Code and image-only review workflow
0e006982-4f72-43bf-851a-fbdb8aa10a8f completed, both block required occlusion demonstration;
ordinary-model held-out gate not run.

Parent read generator, tests and teaching/learner cards. Parent command:
`.venv/bin/python -m unittest scripts.tests.test_ribbon_family`
Observed 11 tests passed in 1.770s, exit 0. `git diff --check` exit 0.

## Verified current rendering defect

In make_panel's support comparison, clipPath rectangles use panel x/area_y coordinates but are
applied to a g already translated to (x,area_y). Content inside that g uses local coordinates.
This double-offset clips the right comparison out of its local half-width. Non-support panels also
repeat area_y in their local clip and risk top cropping. Correct by choosing one coordinate space,
not adjusting geometry. Source inspection supports P1: required occluded evidence is blank.

Independent parent raster probes on saved body-card-front.png and body-card-oblique.png (380x300):
right x=190..367, y=55..277 has ZERO pixels of support colour (216,228,218), front colour
(230,138,164), or back colour (113,136,189). Left view front pixels: 2119 and 3219 respectively.
Geometry unit tests pass despite this SVG presentation failure; add raster evidence assertions.
No visual gate claim. Parent accepts code findings: local clipping fix + raster regression;
reject unsupported crossback depth=0 and bound collision claims; add near+far self-crossing visibility
assertions with reversed declaration order; reject duplicate camera names. Blind reports of coloured
slivers/diagonal seams require coordinate/geometry verification, not automatic acceptance of diagnosis.
Worker revived as 2c0da02c-e968-4953-a983-5a4f35fe67ca for these scoped corrections, preserving frozen
case geometry/cameras. Engine changes remain forbidden without isolated evidence and parent decision.
Revised-source code review remains running; refreshed blind review returned (see below); held-out
learner remains unrun. Parent locked the unseen task in held-out-task.md before any learner launch.

## Authorized upstream construction correction

Worker supervisor request 8669926c-fe1c-485e-965c-7d0c047a2710 reports true surface self-intersection
in the unchanged frozen crossback case: local coordinates (.31009383,.74501844) and
(.36846037,.75803982) coincide with solver residual approximately 3e-13; another solution near
(.32717,.6485)/(.35156,.6527). This is worker evidence requiring preserved reproduction and independent
checks, not yet parent-certified. Principal crossing depth separation alone does not establish
collision-free full-width geometry.

Parent authorized a bounded crossback construction-rule correction, keeping exact frozen spec values,
cameras, attachment semantics and principal projected crossing. Preserve original failure/formula;
regress coincident patches, crossing visibility/order, facing and attachment; exercise tessellation
convergence and document limits. No metric optimization, case substitution, renderer patch or
universal collision guarantee. Derive revised crossing probes from geometry rather than insist on
obsolete magic u values. If no sound bounded correction, leave gate blocked with evidence.

## Corrected revision and fresh perception finding

Parent reran all focused suites: `.venv/bin/python -m unittest scripts.tests.test_vector_visibility
scripts.tests.test_spatial_sketch scripts.tests.test_figure_scaffold scripts.tests.test_ribbon_family`
36 tests passed in 45.853s, exit 0; existing draw.py ResourceWarnings remain non-fatal.
`git diff --check` passed. Source hashes match worker: ribbon_family.py
eae4ac491c716b9480b35127b2cefa504fcec02a2bb5a329457b79dd0523074b; tests
6042c88755ea173b0e04a7f46d0ac9922652fbe6795d0123bea19a72923d713e. Frozen cases hash remains
bd2732b806de26cc2d8a261be68e8f30e21e1f8f8bd5301556d85241a8bc5800.

Fresh blind review 181e9cfa-c21a-4787-b6cf-c1440e81c012 still finds case 5 same-colour crossing reads
as a knot with unclear front section; low-contrast support in case 6; clipped long captions.
These are perceptual/interface findings, not proof depth calculation is wrong. Geometric tests
cannot waive readability. Need verified presentation/artwork remedy after code-review synthesis;
no S1a visual or transfer acceptance yet.

Code recheck 5ffe4331-0d60-4b9a-8803-bf68fbfad788 confirms all prior P1/P2 corrections, new P2:
raw case names can normalize into colliding IDs. Parent accepts fixing it via identifier-safe names.
Follow-up writer a0d06881-1cbc-41ba-9740-ffe98c60bbb3 is authorized to add only simple continuous
local-UV stripe artwork for crossing readability, preserving original support triangle geometry and
computed depth/facing. Contrast on both sides, no hand-specified visible cuts/contact strokes or
new line engine. Also fix diagnostic support contrast and clipped captions. Freeze case inputs,
cameras and geometry formulas; preserve prior images and disclose presentation treatment. This is
an artwork identity cue, not a visibility workaround.

Worker completed this pass: local v[-.18,.18] stripe clipped/barycentrically mapped within original
support triangles, coplanar material artwork submitted before unchanged base fills; diagnostic card
contrast/wrapped captions/ID-safe cases fixed. Parent reran 38 focused tests in 57.982s, all passed,
log /tmp/s1a-parent-stripe-tests.log; git diff --check passed. Original draw.py ResourceWarnings remain.
Current source SHA: 015ec14ec90da5768dbcdd9486220d3971c55673f0944971ccb3a8a47662bd3e;
test SHA: 5347078429b19faaa4132a627ea4b967ea6a670bbc26b5841a85519a743b4202.
Reviewed labelled draft hash: 659b706afb926fb47dc33000cf34aec64f3956aa3d4d5e044265da8440482dd3;
unlabelled: 0c5c8e513bdaec50a6760a24db1b014e6f4b6ae75eb1eda8bc545f184c52b244.
Final code/blind review workflow f0c1f767-fbb7-4c3b-9c91-687827428efd completed. Code recheck
confirms corrections and local artwork mapping/tie handling, remaining P2 custom colours can lose
contrast against fixed stripe. Parent documented that limitation in teaching card (no source change).
Blind review still cannot clearly read crossing and twist transition despite aggregate OK-with-notes;
required visual criterion stays open. No S1a acceptance claim.

Parent changed the internal sequencing, not task/criteria: stop speculative appearance patches and
run two independent diagnostics in c530e822-b48d-4480-b1f4-8ad4ac16ac0e: read-only Luna Designer
verifies projection/mesh/depth versus missing artistic boundary cues; fresh gpt-5.4-mini authors
prelocked unseen combination with only teaching packet/card/schema and black-box CLI. Learner success
cannot waive failed crossing readability; full transfer perception remains separate. This proceeds
useful interface evidence while isolating the visual blocker. No production source writer running.

## Diagnosis and independent learner evidence

Designer 4f09fd69-2743-416b-85b4-74949a9ca90b measured smooth camera-facing normal sign change:
oblique twist near u=.30084 (panel ~127,162), front near u=.5321; edge-on pinch expected, mesh can
accentuate appearance. Principal crossing pair depths +/- .2298903, both front-facing, same material.
Missing selected occlusion silhouette is a defensible next experiment, not a contact line (surfaces
are separated). Parent accepts bounded diagnostic, not all suggested hand-picked locations: entire
semantic perimeter must generate depth-selected visible masking edges, no u/box author cuts.

Ordinary learner gpt-5.4-mini completed untouched gentle-s-ribbon.json and same-spec two-camera
renders; parent asserts family s-curve, taper 1/3, root [.5,-.25,.2], heading pi/6, negative pi twist,
length4 width.4, requested colours and bend range, measured root/width ratio and both material sides.
Spec hash dd995ab1d1cced202a63092263d489597339ae18d2ea761e77408c5b41e8455c. No parent rescue.
This does not prove learner output readability, independent reference understanding or universal use.

Workflow 61ad0c77-508d-4a7b-8ec2-a3552ec917b3: existing Luna worker implements scratch-only
work/occlusion-probe-brief.md; fresh image-only review assesses learner check bundles. Production
source/frozen cases/cameras/learner outputs read-only. S1a visual/transfer gates remain open; probe
is a minimal readability dependency, not S2 milestone promotion.

## Probe implementation and learner perception result

Probe worker 675be33f-af70-47bb-b1c6-bf7a22ac2161 completed scratch-only perimeter candidate
selection from whole UV boundaries, projected face intersections and depth-equality roots. No
manual visibility intervals or mesh-diagonal ink. Parent inspected selection source and reran six
probe tests: all passed in 7.378s, /tmp/s1a-parent-probe-tests.log. git diff --check passed. Production
ribbon/visibility and learner spec SHA hashes remain unchanged. Probe blind reviewer
e57c8177-f33f-4a57-b54b-98c374da2e31 completed: no crossing concern reported, teaching negative
control unchanged; twist40 stripe visibly scalloped versus smoother twist128. This is deliberately
coarse/fine diagnostic, not acceptance of 40 as usable twisted-art quality. Absence of a reported
crossing defect does not itself establish order identification; image-only follow-up
 a8160e52-eb3d-4be1-9eef-5299852e312e asked for actual visible over/under/continuity descriptions
without source or geometry. It recognizes original crossing order with some cue benefit but cannot
resolve reversed-depth control; twisted band appears connected while stripe transition not continuous.
No all-case perception acceptance or production promotion.

Learner blind reviewer 7d9840cb-f354-4e85-afbc-08bdc1abeb62 recognizes connected path/attachment but
blocks readability: near-point pinch at material transition, oblique back section too thin. Parent
retains original learner answer and does not rescue it. API authoring subclaim passes measured
criteria; full visual-transfer claim fails/pending. Projection diagnosis for frozen example cannot
automatically dismiss this learner image's perception finding; no full S1a acceptance.

Final learner image-only description 47d1624c-b0ef-406f-b3ca-1590276836a7 again cannot confidently
identify one sheet and two faces. Parent separately measured its actual support: positive world width
at facing sign crossings and smooth sampled axes/tangents; data in evidence/parent-learner-projection.json.
This supports physical edge-on cause, not a visual waiver. All runs terminal; S1a remains open at
perception stop condition. Consolidated parent outcome and coverage: outcome.md. Official status,
roadmap/active record now distinguish tested construction/API from unpassed readability/transfer.
No source, frozen case, reference, saved learner answer, baseline, vendor or Git index rescue edits.
