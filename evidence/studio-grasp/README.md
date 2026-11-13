# Grasp investigation — rejected defaults, an imported rig, no shipped preset

2026-11-13. This is an investigation record, not a whole-art pass or a new studio
kind. The human accepted the simple flat head as one default; that does not accept
these hands, the watering scene, or a general style. No baseline was promoted.
Production studio source and its accepted defaults are unchanged in this unit.

The problem is the ambiguous mass/thumb/crease carrying hand in the watering scene.
The intended next product capability remains one simple grasp with useful adjustment
and named wrist/prop connections, demonstrated in an actual composition and reused
by a fresh skill-only operator. None of the studies below meets that checkpoint.

## What was tested

| Plate | Actual construction / result |
| --- | --- |
| `01-cylindrical/default.png` | Independent curved finger tubes, ellipsoidal palm, opposed thumb, cylindrical rod; all visibility computed in 3D. |
| `02-wrapped-views/` | Refined loops and alternate views. Outlining fragment unions incorrectly amplifies numerical holes into dotted ink. Retained failure. |
| `03-intentional-ink/` | Fills and art lines separated, but full-projection interior holes still receive false ink. |
| `04-exterior-ink/` | Exterior-only ink removes that defect. Palm-side action reads, but fresh reviewers find a mitten and unclear thumb; back view is worse. |
| `05-articulated-contours/` | Smaller palm, rounded thumb tip, more articulation; still ambiguous. |
| `06-contact-contours/` | Projected digit exteriors clipped to their true visibility; four fingers become much clearer. |
| `07-exterior-contact/` | Unquantized full projections unioned before precision reduction; interior holes excluded from art contours. Two fresh reviews still find an ambiguous thumb and inflated loops. |
| `08-buried-thumb-root/` | Root cap moved into palm, narrower palm and smoother tubes. |
| `09-thumb-side-camera/` | Thumb-side views after burying the root further. Gesture is recognized, but two fresh reviews still reject thumb articulation and assembled finger/palm seams. |
| `10-established-surface/` | Unmodified licensed WebXR hand bind mesh, CPU joint posing, three-tone vector lighting. Import works; arbitrary flexion does not solve contact. |
| `11-mesh-contact-contours/` | Same continuous surface with a rod, flat fills and visible apparent contours instead of every mesh edge. Fresh review calls the fingers draped, thumb unopposed. Geometry independently detects 83 skin vertices inside the rod, maximum sampled penetration about 0.01044 model metres against radius 0.011. Rejected as a grasp default. |

The last penetration value is a vertex diagnostic, not a full surface collision
test. Zero would not prove enclosure or absence of triangle/surface intersections.
No pose was tuned against image similarity, edge scores, or a target picture.

## Source and reproduction

Run from the repository root with the locked project Python (NumPy/Shapely/resvg;
CPU only). The prototype script writes its declared study directory. Use a separate
checkout/output tree to preserve the frozen evidence when repeating a study.

```
python evidence/studio-grasp/probe_3d.py
python evidence/studio-grasp/probe_webxr_initial.py
python evidence/studio-grasp/probe_webxr.py
python evidence/studio-grasp/verify_study.py
```

`probe_3d.py` is the exact final tube experiment (09); its yaw options do not make
back-side views good defaults. `probe_webxr_initial.py` is the exact source for 10;
`probe_webxr.py` reproduces 11 and checks actual glTF joint matrices against inverse
bind matrices, rather than merely asserting that a zero deformation returns its input.
The largest bind-matrix identity error is about 2.54e-7. Bone chains retain their
lengths, but the chosen rotations are hypotheses and do not solve physical contact.

Earlier source provenance: `probe_3d_first.py` is the captured first experiment;
`probe_3d_second.py` was reconstructed from recorded replacements, not captured
before execution. `probe_3d_third.py`, `probe_3d_sixth.py`,
`probe_3d_seventh.py`, and `probe_3d_eighth.py` are actual preserved snapshots.
The exact 04/05 source was not frozen before editing; their SVG/PNG/JSON bytes are
retained, but no claim of exact regeneration is made. A delayed copy intended for
05 captured 06 instead; that redundant misleading copy was removed. Later source
copies were awaited before mutations. Timings in JSON are execution observations,
not a performance benchmark or acceptance target.

The `*-check/` bundles were created with `scripts/draw.py check`, without a reference.
`reviews.json` records fresh-context image-only review provenance and conclusions.
Reviewers received only their bundle's image list and the open question; no history,
intent, construction explanation, suspected verdict or source code. No picture in
this unit received a human aesthetic pass. The later mesh artifact has a fresh
review; the first open-mesh plate is an import diagnostic, not a judged open-hand
preset. See `manifest.json` for the frozen file bytes.

## Reuse and outside sources

`third-party/webxr-generic-hand-1.0.20/` preserves the exact unmodified `right.glb`,
profile and package-specific MIT license from `@webxr-input-profiles/assets@1.0.20`.
URLs, sizes and SHA256 are in its `provenance.json`. This is a mathematical 3D bind
mesh, not a generated picture, traced reference or texture. No new production
dependency has been installed and the asset has not been adopted as a studio kind.

Primary sources consulted:

- [WebXR Input Profiles assets](https://github.com/immersive-web/webxr-input-profiles/tree/main/packages/assets),
  including its package-specific license rather than assuming the repository-wide
  document license applies to the model.
- [Meta's WebXR Hands documentation](https://developers.meta.com/vr/documentation/web/webxr-hands/)
  identifies the standard generic-hand assets and 25-joint skeleton.
- [FAA HFDS chapter 14, exhibit 14.4.3(a), printed page 14-38](https://hf.tc.faa.gov/hfds/download-hfds/hfds_pdfs/Ch14_Anthropometry_and_biomechanics_Oct2009.pdf)
  text distinguishes hook grip and power grasp. Its diagram was not successfully
  visually inspected here: web screenshots returned references without image data,
  and both the project and bundled Python lacked PyMuPDF. No visual anatomical
  conclusion is attributed to that unread diagram. The PDF was only temporary study
  material and is not redistributed.

## What changed in the approach

Independent 3D tubes improve depth ordering but do not supply useful anatomy or
select art lines. More creases, a new view, and merely importing an established mesh
did not solve the actual default. Keep those failures rather than multiplying them
into a preset catalog. The next discriminating experiment is a hand-space contact
pose: fit articulated phalanges/pads to a declared cylindrical grip, test clearance
and thumb opposition, then judge the flat-vector picture. A contact-segment macro
with wrist/end ports is only a candidate interface. Do not implement compiled
templates, broad rig controls or cross-object contact promises before this one
grasp works and survives a real scene. Current decisions live in `docs/`, not here.
