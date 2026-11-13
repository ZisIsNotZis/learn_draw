# Cylindrical contact study — geometry improves, mesh drawing is not adopted

2026-11-13. Continuation of `../studio-grasp/`, from the actual 83-vertex rod
penetration failure. CPU geometry/resvg only; no image target, GPU or generation model.
This is a study record. Current product decisions belong in `docs/`.

## Actual experiments

| Record | What it tests / what happened |
| --- | --- |
| `pose-01.*`, `01-tangent-phalanges/` | Recover phalanx lengths and skin rings from the licensed bind mesh. Construct successive tangent segments around an offset rod circle. Old thumb hypothesis remains. One vertex / six skin triangles still enter the rod. |
| `pose-02.*`, `02-opposed-thumb/` | Two-link thumb reach plus distal direction targets the index/middle pads; rod defects remain in the middle proximal phalanx. |
| `pose-03-failure.json` | A maximum whole-ring support envelope overstates the pad near the real tangent point and makes the fixed thumb target unreachable. Failed before export; no pose/image 03 is invented. Source is `contact_03_failed.py`. |
| `pose-04.*`, `04-surface-response/` | Median capsule initializes pose; bounded response reserves extra space for the phalanx whose actual skin triangle penetrates. No skin/rod-volume intersection remains. Thumb orientation is still only a hypothesis. Two fresh image critics still find loose grip, ambiguous thumb, stray ink and a long empty palm. |
| `05-geometric-contours/` | Same pose, fix apparent-contour detection: real facet orientation, not averaged lighting normals. Removes false triangular interior ink. |
| `bind-06.npz`, `pose-06.*`, `06-loop-surface/` | Reuse hash-pinned Trimesh Loop subdivision, preserving all 25 skin-weight channels. Smooth bind surface has 4,630 vertices / 9,256 hand triangles. Rod checks pass, but geometry alone does not settle illustration. |
| `pose-07.*`, `07-actual-joint-frames/` | Recover the asset's actual joint -Y palm directions. The earlier thumb frame inferred roll from the rod axis and twisted it incorrectly. Rod checks pass; 69 non-neighbor transverse skin crossings remain on this refined mesh. Not a collision-free hand rig. |
| `08-opaque-partition/` | Same pose, separate opaque material coverage from fragment boundaries; clip exterior skin ink where the rod is in front. White numerical cracks are not hand highlights. Connected ink omits sub-ink specks. |
| `pose-09.*`, `09-thinner-handle/` | Semantic correction: thinner rod, fingers reconstructed around it, same renderer/camera as 08. Rod-volume checks still pass. Blind critique still sees draped fingers and a broad thumb. |
| `10-crossed-assembly*` | First real-scene assembly captured before painting. A pi rotation reversed bar endpoint order but not vessel port pairing: handle chords cross, painted overlap 55.88156 px². The known-invalid live paint process was deliberately canceled after this diagnosis, not restarted because of an observation timeout. No finished image is claimed. |
| `11-watering-paired/` | Correct end pairing. Cloth then obscures much of the hand because the wrist was chosen on the wrong approach side. |
| `12-watering-wrist/` | Choose wrist toward the sleeve root, leave space for the whole hand, raise spout. Real scene now includes the candidate, but blind review still finds a knot of fingers / unclear enclosure. |
| `13-proxy-camera-views/` | Inexpensive base-mesh discrimination of under-palm, thumb-side and back views. View proxy, not a final default. |
| `14-back-grip/`, `15-watering-back/` | Refined back view in the composition. Critique still finds a mitten-like mass. Stop multiplying mesh views; this route is not adopted as a default. |

The geometry observations do not establish visual success. Physical checks also
have distinct scopes: rod-volume/skin intersections, bone lengths, and transverse
skin crossings are separate from thumb opposition, coplanar contact, enclosed
volumes and anatomical plausibility. A vertex-only test was insufficient.

## Source, checks and safe reproduction

`contact_01.py`, `contact_02.py`, `contact_03_failed.py`, `contact_04.py` and
`contact_06.py` freeze the corresponding construction versions. Renderer snapshots
`render_contact_04.py`, `_06.py`, `_07.py` preserve pre-correction behavior. Saved
bind/pose arrays preserve the actual geometry used for the named pictures.
The historical scripts are records and can overwrite their named outputs: do not
run their old mains against this frozen directory. Use a separate checkout for
exact historical replay. The current entry points require fresh output locations:

```
python evidence/studio-grasp-contact/contact.py --outdir FRESH --radius .006
python evidence/studio-grasp-contact/render_contact.py --pose FRESH/pose.npz --outdir FRESH_RENDER
python evidence/studio-grasp-contact/render_contact.py --pose evidence/studio-grasp-contact/pose-09.npz --bind evidence/studio-grasp-contact/bind-06.npz --outdir FRESH_REFINED --pitch 35
python evidence/studio-grasp-contact/test_contact.py
python evidence/studio-grasp-contact/test_geometry_checks.py
```

The four contact tests check an actual surface crossing missed by vertex samples,
finite-cap cases, the tangent construction, actual joint roll and bone lengths.
Three independent self-crossing tests cover transverse/separated/grazing geometry
and topological neighbors. Both suites pass. The posed base surface has 34 strict
non-neighbor crossing pairs against zero in its bind pose (`self-contact-04.json`).
Do not compare that count directly with the refined mesh's 69: resolution differs.

Early JSON calls radial clearance inside the rod's axial slab
`minimum_surface_clearance`. The current implementation/tests rename it
`minimum_radial_clearance_in_slab` and explicitly distinguish it from a full
finite-cylinder signed distance. Cap-only contact is not volume penetration.
The actual study hand is within the long rod's axial span, so this naming/cap
clarification does not turn its prior numerical observations into a full SDF claim.

The optional study-only package installs outside the locked project environment:

```
uv pip install --python .venv/Scripts/python.exe --target .tmp/grasp-deps --no-deps --require-hashes -r evidence/studio-grasp-contact/study-requirements.txt
```

No production code imports that package or this study. The MIT-licensed hand bind
asset remains unmodified in `../studio-grasp/third-party/`. Primary documentation
consulted: [Trimesh Loop subdivision](https://trimesh.org/trimesh.remesh.html#trimesh.remesh.subdivide_loop)
and [WebXR joint orientation](https://www.w3.org/TR/webxr-hand-input-1/#xrjointspace).
The standard's palm -Y direction, not a guessed common rod axis, supplies joint roll.

## What changed next

These experiments improve explanatory geometry and expose renderer mistakes, but
the pictures remain poor default illustrations. The next route studies compact
vector drawing grammar and becomes the native `grip` candidate in
`../studio-grasp-glyph/`. It does not silently rebrand this mesh as a solved grasp.
Blind qualitative reviews and process observations are preserved in `reviews.json`;
they are not scored whole-artwork gates or human acceptance. `manifest.json` binds
the actual frozen bytes, not a success verdict.
