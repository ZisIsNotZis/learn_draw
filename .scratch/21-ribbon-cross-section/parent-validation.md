# Transverse-support study — parent validation in progress

Repo master base24693d4 with protected prior dirty work and staged vendor/.gitmodules. User “go”
authorizes one flat/mild-camber geometry hypothesis, no S1a acceptance. Camber .35 and case/camera
plan frozen. Old generator/source/learner/cases remain read-only.

Worker3f6b71f0-45bf-495a-9e95-29262301324e checkpointed incomplete: new module/tests/plan/build
script plus first profiled SVG/PNG pair. Nine dedicated tests pass, but between-station material
width defect found; no full board/card/log/old-suite/check/perception. Parent inspected partial source,
captured /tmp/ribbon-surface-checkpoint.tar.gz, git diff --check exit0. Initial source/test hashes
84aaaf008f97f594a30ab69aa713856654d2c9d40abfbed2aa64967b7fc10773 /
70d77de8e124b92a9044b03cafa1823b0ce892bcb9255159f2ad9e40bc9abb5a.

## Independently reproduced width error

Parent used actual positive-half-twist spec and original build_mesh at N48/96/192; located source
UV triangle by barycentric containment, called current _map_source_point on513 uniformly spaced v
samples and summed512 3D chords at fixed off-station u. Desiredwidth .36:
- N48,u.49 flat .3599997174519, curved .3563020416583 (new loss~1.0271%).
- N48,u.51 flat .3599997251906, curved .3563008044347 (~1.0275%).
- N96,u.49 curved .3597358279293; N192,u.49 .3597445012892.
- Stationu.5: curved .3599999146521 versus flat .36 (dense chord approximation).
Increasing N alone is not an adequate correction; formula assumes straight transverse frame while
barycentric off-row cross-section is piecewise and carries nontrivial finite-frame interpolation.

## Bounded continuation

Native resume worker1cd81a35-8244-4625-a35e-b3d48fdf403c fixes actual off-row arc normalization,
not case/camera/camber/tolerance. Actual curved-profile arc normalization, bounded/cached numerical
or analytic integration allowed. Preserve zero-camber exact old triangles and old material midpoint
v0, root/tip. Explicitly distinguish ideal requested profile, old finite midpoint and triangle/chord
approximation; report any mathematical conflict before weakening constraints. Add independent dense
OFF-station tests beyond .49/.51 and convergence; preserve old defective pair/source and invalidate
cache on source changes. Then required full paired outputs/card/log/tests/smoke/check/determinism.
No new stylistic rule/old-source edit/commit/installs or self visual gate. Native completion wakes
parent; all perception/transfer/S1a gates pending. Runtime acceptance rejection is not project pass.

## Corrected implementation and parent checks

Worker1cd81a35-8244-4625-a35e-b3d48fdf403c completed actual finite-section normalization: preserve
old B(u,0) midpoint, integrate bowed derivative per original diagonal segment, scale whole displacement
by original arc / bowed arc. Zero camber/root/tip bypass remains exact; requested continuous width
vs finite baseline vs mesh chord approximation explicitly distinguished. Failed old pair archived.
All10 panels and both boards/card/log/determinism saved; no old source/cases/learner modifications.

Parent read correction and independently ran CURRENT all six focused suites:
`.venv/bin/python -m unittest scripts.tests.test_ribbon_surface scripts.tests.test_ribbon_drawing
scripts.tests.test_ribbon_family scripts.tests.test_vector_visibility scripts.tests.test_spatial_sketch
scripts.tests.test_figure_scaffold` —63 passed in73.929s, /tmp/ribbon-surface-parent-tests.log.
git diff --check exit0. Module hash5c32715a9359e3228a7cd91e2bed020f47badcc6df949f2f54e6c8ae493df2f4;
tests14bf34a47f3b2cb25e14c2ce481cb7c52829643231c48f720d8fd19916fd59cd;
labelled PNG546cb88d369b57e3625bc7c69cf54edf61af56ee681fdea8a68b9462999901e4.

Fresh review workflow c43924d3-8d6a-4b35-9bce-aafc94865172: code review completed with two P2 findings; blind visual
review edfccb07-713e-495d-b9f3-724be3feb204 reports curved panels noisy/uneven, camber not clearly
legible and pinched transitions persist. No perception benefit established. Image-only follow-up
62dcb18c-dd5d-43e4-bdac-5f03330b2ef6 asks at most2 pixel rectangles/visible colour symptoms to
verify spatial claims before source diagnosis; no intent or suspected cause supplied. Keep .35 fixed,
no camera/value sweep or prescriptive metric optimization. Need distinguish finite sampling/material
facing/visibility fragments before accepting or rejecting as a pure support-family result.
No visual/transfer/S1a gate pass, learner trial unrun. Tests/check completion cannot waive findings.

Code review efde8c91-c401-4b26-a846-6bc2a2117aed confirms normalization/flat limit/facing/provenance,
but selected48x6 rendered-chord deficit needs explicit bound (not only finer96x12); cache must bind
builder and actual raster provenance. Worker04eb4d81-8ab1-41b8-9990-959daefdccb5 assigned these scoped
fixes plus ONE causal diagnostic: same .35 geometry at existing fine convergence and monochrome
visibility-only output, not new palette/camber acceptance condition or an engine patch. Actual mesh
chord test must include off-station sections, declare tested range/tolerance and report failures.

Image-only follow-up completed: no pair more confidently depicts continuous sheet/two faces.
Approx ROIs in labelled PNG are700..840,490..555 and700..850,1570..1640. Parent verifies actual
PNG1020x1818, curved-column translationx517, row1y428,row4y1478, yielding local positive-half-twist-
oblique rectangle183..323,62..127 and untwisted-arch-front183..333,92..162. Observer can't tell
background gaps versus material fragments. Forwarded measured locations to worker via native steer;
regions are diagnostic evidence only, never visibility author masks or optimization targets.
Hypothesis has no demonstrated perception gain yet; unknown noise cause must not be patched by style.

## Selected-mesh tolerance fails; explicit precision re-test authorized

Worker04eb4d81-8ab1-41b8-9990-959daefdccb5 completed chord measurements/provenance fixes and one
arch diagnostic. Actual48x6 mesh widths exceed declared .002world bound at four off-station cases:
positive twist .49/.51 deficits .0042377741/.0042391781; learner regression .49/.51 excess widths
.0021776440/.0021473584. Test now detects/reports these failures; its unit-pass is NOT material-gate
pass. Old48x6 boards retained and not relabelled geometry-compliant. Original96x12 sampled21
measurements pass, no global claim.

Parent broadened to44 fixed u samples per unique spec: endpoints/.19/.49/.5/.51/.81,
(i+.37)/32 for i0..31, plus (i+.5)/96 for i18/46/47/48/77. Independently intersects actual support
triangle UV edges via test helper and sums3D chords. Maxabs flat/camber difference at96x12:
positive .0019738918548; learner .0012332837331; arch .0001554545221, no bound failures.
Raw record /tmp/ribbon-surface-fine-width-parent.json. Camera-independent world check covers same
fixed front/oblique rows, not arbitrary parameter range/continuous proof.

Parent explicitly authorizes ONE full96x12 accuracy re-test, worker a9c23a93-9a34-419b-ad02-019fc9d80beb:
new derived plan under work/cases-fine.json and separate evidence/fine/, both columns refined
identically; old params/cases/camber/cameras/artwork/support algorithm and failed learner unchanged.
This remedies invalid coarse material precision for a clean hypothesis check, not hidden candidate
substitution or a new camber/colour search. Test expanded grid before rendering; all10 panels,
profiled incremental build<=900s/raster180s, deterministic checks and fresh final image-only review.
If test/runtime fails, stop dependent build, no wider tolerance or unbounded refinement.

ROI2 actual face dots allfront and selected/material occupancy equals monochrome mask10500/10500
pixels at declared8-channel threshold; nine point samples match expected paint. No sampled evidence
of coverage holes/back-facing flicker there. ROI1 has manyactualnormal facing-sign transitions;
finite material segmentation implicated, not proof of its complete artistic cause. Diagnostic is
not an alternative acceptance style or viewer verdict. Fine review completed with speckling concern; no learner launch.

## Fine results and independent source-versus-resolver causal probe

Fine worker a9c23a93-9a34-419b-ad02-019fc9d80beb saved all10 fine panels, same .35/specs/cameras,
separate plan and reports. Worker132 actual chord probes pass .002; its44u grid is DIFFERENT from
parent44u grid. Both independently pass and are separate evidence, not one copied grid. Parent
validation document formula is the coordinate source for its checkpoint summary; a summary JSON
alone does not encode coordinates. Reviewer6cd0b366 recheck confirms bounded fine/provenance fixes
and flags that documentation/provenance P2. No old plan overwrite; no global width claim.

Parent CURRENT combined six suites:67 passed in77.513s, /tmp/ribbon-surface-parent-fine-tests.log;
git diff --check exit0. Source unchanged5c32715a…; tests223079c340827edefa8eb3dbcaf2e408913162a9549457516509b65ffc7519d3.
Unlabelled fine PNG4a0f44ca1e58a9d4739bdc449f0579553344e61b49d6955d81d9a42a1678d74c,
worker repeat byteidentical; labelled raster8text-pixel repeat difference disclosed (not normalized).
Fresh fine blind review bd9f6be4 says curved broad bands speckled; no clean perception gain verified.

Parent independent runnable work/parent_raster_probe.py computes pixel-centre barycentric/nearest-
depth UV for one untwisted fine arch, with samples far from true perimeter/stripe but NOT mesh edges.
8495 safe pixels: current authored raster41 deviations>12RGB; raw same-colour support triangles
serialized directly through compound_path yield0; same geometry through visible_regions yields44.
Both have0 full background-colour centres, so partial-coverage flecks evade occupancy-only tests.
Evidence fine/parent-raster-probe.json and parent-{raw,depth}-monochrome.svg/.png. This isolates
clipping/fragment-serialization/raster-stage artefact, NOT a shape or colour diagnosis. Coverage
oracle doesn't use target image; no visual self-judgment or contour optimization.

Pause hypothesis perception decision: kernel artefact confounds the clean comparison. New
.scratch/22-visibility-fragmentation/spec.md is a bounded scratch-only upstream reproduction/
ONE candidate patch study; no canonical edits until parent review/integration. Camber and inputs
remain frozen; existing coarse/fine pictures are retained. No new learner/S1a/S2 claim.
