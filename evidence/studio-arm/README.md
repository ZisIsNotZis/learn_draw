# Owned upper-body representation study

This is a renderer prototype, not a native component or a public editing API. The source uses a process-local component factory adapter with the existing CPU renderer and depth visibility. Generated scene.json still describes its generic host: it cannot reconstruct this garment without the helper. All report/selection engines are study-only and cannot be accepted as native proposals.

## Decision and actual pictures

A single quadratic sleeve fitted at its wrist bows the entire arm. Explicit shoulder/elbow/wrist joints localize the bend (01–09), but a separate sleeve still meets a generic torso badly. An owned garment combines its collar, shoulder pattern, torso and sleeves while retaining local arm surfaces. Rounded sleeve roots initially leave shoulder bumps/ledges (10–16,21–22); matching the shoulder pattern to a flat internal root removes the visible step (23–24).

The selected next representation is an owned upper-body garment with semantic joints and separate intentional ink. Native controls, attachments, independent operation and a second editable pose are still to implement. No natural anatomy, whole-artwork acceptance or human approval is claimed.

- 23-sewn-garment: connected person offering a flower; improved shoulder join, thick rounded elbow, abrupt large hand/cuff and narrow hanging armpit gap remain.
- 24-sewn-default: recognizable simple long-sleeve top, continuous shoulders/collar/cuffs; asymmetric pose and less explicit elbow remain.
- 17-crossed-union: useful failure. Flattening cloth to one outer silhouette loses the crossing forearm.
- 18-crossed-front-surfaces: intentional front-arm contours restore overlap but can resemble a pocket at their upper end.
- 20-crossed-person-intent: real second pose; hand/stem clarifies the crossing. Bulbous elbow, chest-line endpoint and flower crowding near the face remain.

Fresh image critics saw actual PNGs in phases. reviews.json records parent-captured observations and file digests, not original verbatim transcripts or a portrait gate. The final targeted critic saw 23 and 24 and confirmed shoulder steps are no longer obvious. The author also viewed these images.

Internal surfaces are left arm -1, torso 0, right arm +1. The prototype does NOT implement/verify an external prop passing between these internal planes. Native integration must preserve this boundary explicitly rather than declaring a whole garment one flat plate. Outer material continuity and visible overlap lines are separate concerns.

## Evidence and replay

input-person.json freezes the unchanged published native person study. source-history/ retains source versions used by historical outputs; verify_study.py checks each concatenated source hash. Historical body scope strings say single offering pose even for default/crossed cases: use the case names and actual joints, not that stale scope string. Case19's stale head intent is corrected in20 with identical pixels; its disposition is preserved. Historical study IDs bind source only, with host/configuration recorded separately.

Current replay binds source, frozen input, pose and host engine in a study ID and refuses existing output:

    python evidence/studio-arm/build_body.py default --outdir FRESH
    python evidence/studio-arm/build_body.py offering --outdir FRESH
    python evidence/studio-arm/build_body.py cross-person-corrected --outdir FRESH

replay-verification.json records exact clean PNG reproduction of24/23. The crossed replay uses the newer shoulder construction and is retained as25; it differs from20 and is not a second independent replay under the new safe entry. Historical snapshots require their original module layout; do not run them in source-history or overwrite frozen outputs. All geometry is computed, with no reference image, pixel fitting or GPU inference. check-* retain bounded historical drawing-check outputs; they are not whole-artwork passes.
