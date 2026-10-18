# Issue 54 — User review of A v4 / B sheet: scope revision, hair mechanism regression, B hand level

Opened 2026-10-15. Trigger: user reviewed the A v4 image, the reference crop and the B sheet, and gave
direct art feedback. The user is the authority for intent and product scope; this issue records those
decisions and the investigation that followed. It does not accept any artwork and does not by itself
authorize implementation.

## User decisions recorded in this session

1. **A includes two sleeves.** The user rejects the earlier reading that the reference shows one sleeve:
   the second sleeve is small and partially covered, not absent. "hand goes according to our original
   plan is fine, but there are two sleeves, not one, the other one is not invisible, it's just small,
   partially covered, but not fully." A keeps its existing no-hand-claim scope; both sleeves must be
   present, with the second one's visible shape produced by depth occlusion rather than a hand-drawn cut.
2. **Hair uses the curved design** — the two-sided head-attached sheet, i.e. the S1 mechanism, not the
   flat single-colour band currently in A v4. "Yes use the curve design. If you can implement
   blocking/covering properly, that would be nice."
3. **B's hand is built at the detailed level** (palm + four fingers + thumb, contact geometry), because
   the project's point is detailed and reasonable drawing. The hold concept itself is confirmed as
   readable in both SUPPORT and VARIATION; the CONTROL panel's failure reading is unchanged.
4. **Environment restored with uv** — see below.

## What the investigation established

- **Component separation already exists; connection does not.** A v4 builds each part as its own
  `Component` with its own support frame, local (u,v) and `intent` (collar left/right, bodice, waist
  band, sleeve, cuff, gather, two loops, two tails, local pink band, anonymous blue band, two hair
  bands). But every part is constructed inside one `build_scene()` sharing one parameter file, and
  `attachment` stores three name strings with no geometric requirement. Declared separation is not
  visual connection.
- **The bow reads as detached by construction, with numbers.** `gather_patch` is a 12×15 px quad; the
  two `folded_loop` lobes are separate solids; `tension_tail` starts at `G + (-4,+5)` with half-width
  8.4 px, i.e. a 16.8 px band **wider than the 12 px knot** and offset from it, so its root edge is a
  straight cut beside the knot instead of an emergence from it. The physical object is one ribbon
  visiting knot → lobe → knot → lobe → knot → tails; the reference's lobes are solid cloth with visible
  crease/fold lines and the tails emerge from the knot.
- **Hair is a mechanism regression.** S1 `scripts/figure_scaffold.py:hair_sheet()` is a head-attached
  curved sheet whose normal twists and whose fill is chosen by projected face orientation (blue/mint),
  generalised by `scripts/ribbon_surface.py` triangle-winding paint. A v4 uses `_band_from_stations()`:
  a flat polyline extrusion with one fill, no curvature across the width, no twist, no two-sided paint.
- **The second cuff exists and is occluded.** In the registered 400×480 crop (`image.jpg` source bbox
  `500,320,900,800`) a second sleeve with a dark navy cuff is visible at roughly
  `(84,257)-(105,271)` crop coordinates, mostly covered by the pink bow tail with only a dark wedge and
  a white sleeve sliver surviving. This is exactly the case the depth engine exists for: the component
  is authored whole and depth decides its surviving visible shape.
- **The existing acceptance questions do not cover object cohesion.** Roadmap's construction/geometry/
  art triple can all pass while an object is visibly two disconnected pieces. Recorded as a gap.

## Environment repair (performed, this session)

The documented loop could not run: `.venv/` was absent, `scripts/draw` hard-coded it, `draw.py` imports
`cv2` (missing), and `scripts/draw.py` / `scripts/scene_render.py` pinned a playwright browser revision
(`chromium_headless_shell-1234`) that no longer exists in the cache (1248 present). No dependency file
had ever been committed, so the environment was unrecoverable from the tree.

Repairs: `pyproject.toml` declares the dependencies; `uv venv .venv` + `uv pip install` restored
numpy/opencv-python-headless/pillow/pyyaml; `scripts/draw` falls back to `python3` when `.venv` is
absent; `scripts/renderer.py` resolves the newest cached `chromium_headless_shell-*` (with
`CHROME_HEADLESS_SHELL` override) and both render call sites use it. Verified by running
`scripts/draw check <A v4 svg> --ref image.jpg`, which reproduced metrics and wrote a bundle.

Side effect disclosed and reverted: the first verification run wrote into the pre-existing tracked
bundle `.scratch/35-r1-articulated-study/evidence/check/`, overwriting its `draft.png` and
`report.txt`. Both were restored from git and the run's untracked images were deleted; that bundle is
byte-identical to HEAD again.

## Proposed direction (not yet executed, pending an advance instruction)

1. Split the A build into a **part library**: one family module per object (collar strip, bodice, sleeve,
   cuff, bow ribbon, hair sheet), each authored in its own local frame with named seam anchors.
2. Add a **seam contract** the compiler checks: at every declared joint the two boundaries must coincide
   within ε and share tangent; failure is a failed build, not a visual nag. This is the missing
   falsifiable check that would have caught the detached bow tail.
3. Rebuild the **bow as one continuous ribbon** (one centerline visiting knot, lobes and tails; overlaps
   come from depth, creases are authored interior marks), and the **hair as one two-sided curved sheet**.
4. Author **both sleeves**, with the second cuff's surviving shape produced by the existing depth
   visibility, and add **object cohesion** as an acceptance dimension separate from the current three.
5. Rebuild **B's hand** from palm + finger/thumb primitives with grip contact derived from the dish,
   reusing the same primitive family that A uses to imitate the observed hand.

## Boundaries

No artwork is accepted here, no candidate is replaced, no sealed/heldout content was read, and no
promotion of the recorded best is implied. A v4 and the B caption derivative remain byte-preserved at
their recorded hashes. R1, transfer, heldout, integrated depth/geometry, reproduction and user
acceptance remain open.

## Advance entered

The user then gave the advance instruction for this R1 advance. The approved milestone list, in order, is **M1a, M1b, M2, M3, M4**, and the plan to first level is frozen at
[`work/m1a-m1b-plan.md`](../work/m1a-m1b-plan.md): milestone outcomes, deliverables, acceptance and synchronisation points, the M1a/M1b writer work packages with exact
directory scope and numeric budget, the fresh independent image-only and structural review work packages that follow each writer, and the integration step. M2 needs the user to
release the sealed reference-free task and authorize its separate creator role before anything starts; M3 and M4 are later milestones and are not started.

The gap recorded above is closed on the roadmap side: `docs/drawing/roadmap.md` now carries a fourth acceptance question, object cohesion, alongside construction/attachment/pose,
physical geometry and visibility, and drawing/art. The earlier "not yet executed" framing of the proposed direction is superseded only by this advance record; no artwork is accepted
and no gate is claimed passed.
