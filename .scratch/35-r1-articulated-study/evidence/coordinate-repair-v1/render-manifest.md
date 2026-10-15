# WP03/WP04 coordinate repair render evidence

Fresh renders from the authorized single coordinate-interface repair; no reference passed to draw check. Source revision is the current working tree. Reproduction from repository root:

```sh
.venv/bin/python .scratch/35-r1-articulated-study/work/render_r1.py
scripts/draw check .scratch/35-r1-articulated-study/work/artwork-a.svg --outdir .scratch/35-r1-articulated-study/evidence/coordinate-repair-v1/check-a
scripts/draw check .scratch/35-r1-articulated-study/work/artwork-b.svg --outdir .scratch/35-r1-articulated-study/evidence/coordinate-repair-v1/check-b
scripts/draw check .scratch/35-r1-articulated-study/work/artwork.svg --outdir .scratch/35-r1-articulated-study/evidence/coordinate-repair-v1/check-sheet
```

## Frozen coordinate/API contract for this repair

`Camera.project` maps world X→screen horizontal, world Y→screen vertical, world Z→depth, with the three basis vectors independent. `SupportFrame` continues to map local `(u,v)` into world; scene local `v` uses world Y and depth slopes are world Z. Collision validation continues in world XY; no support `v_axis` swap or panel-scale trick. Baseline, variant and control local geometry, contacts, attachments and authored stroke anchors are unchanged. Every art stroke maps through owning support→camera→panel. Art strokes remain authored semantic lines, not depth-clipped visibility geometry; panel artwork-only clip paths guard panel containment and do not encode occlusion cuts. Titles/subtitles are outside clips.

WP03 source SHA-256: `1a339b1a324a406ce030945176e0d8293f15213f75f700adf57f60456a5c1931` (`scripts/articulated_construction.py`). WP04 renderer SHA-256: `65f3d1bad6c38ec6f5a6c1786faf26640babd23a17fc4ebf4bb2daf1579f39c9` (`render_r1.py`). Current tests include 15 construction tests; render checks and explicit anchor/clip assertions passed.

## Numerical checks

Baseline torso projected bbox 1.800×2.400 (height/width 1.333); head 1.100×1.240 (1.127). Variant torso 1.944×2.400 (1.235); head 1.100×1.240 (1.127). Control torso 1.800×2.400 (1.333); head 1.100×1.240 (1.127). Each case validated and produced 274 faces and visible regions. Semantic contact/hand target/elbow remained computed from frozen case relations. Numerical orthogonal-axis regression verifies local-u/horizontal, local-v/vertical, positive/negative world-Z depth ordering; case regression verifies baseline/variant/control and finite planar collision validator. WP05/WP06 prior PASS is not inherited; fresh review required.

Stroke integration check parsed emitted SVG and compared first neckline semantic point after support→camera→panel to SVG coordinates within 0.06px SVG formatting error: emitted `(196.0,471.9)`, expected `(195.9667,471.9333)`. Confirmed named A/B art paths are within panel-clipped artwork groups (4 panel clip paths). Clip is containment only.

## New review list — only newly rendered images

- `.scratch/35-r1-articulated-study/evidence/coordinate-repair-v1/check-a/draft.png`
- `.scratch/35-r1-articulated-study/evidence/coordinate-repair-v1/check-b/draft.png`
- `.scratch/35-r1-articulated-study/evidence/coordinate-repair-v1/check-sheet/draft.png`

Checks are not visual/art acceptance. No self-judgment, milestone or R1 PASS.

## Artifact hashes

- new A PNG: `813806515ef99c9d774fe8d088c5f6cd910449e49fb344f12b261b480ef3dcf1`
- new B PNG: `ddbc6fcfaf3357c7cf8a5584dfb2c243fedee85befe757ae47e5176455b4283d`
- new sheet PNG: `1494a404bd1fc9ffa4dad4d66b6cedf3f900cb536fec9ed454b2c9591ebd4e1e`
- new A SVG: `8ea6167815d3c2893bd545e83b6a2ec2d91c2fa5f8f200575b6f7e6aedd5538a`
- new B SVG: `0c3edd7d1be8603cd6081bea4042c6a3477b19580c1c430ac3a45dd72233d476`
- new sheet SVG: `5da618eaad244ff557510945b6328740b13a969750451bc675acb4c0505dd5f5`
- renderer: `65f3d1bad6c38ec6f5a6c1786faf26640babd23a17fc4ebf4bb2daf1579f39c9`
- WP03 source: `1a339b1a324a406ce030945176e0d8293f15213f75f700adf57f60456a5c1931`

## Preserved failed evidence

Prior manifest copied to `previous-manifest.md`; failed PNGs copied without modification to `failed-a.png`, `failed-b.png`, `failed-sheet.png`, retaining manifest hashes `f165ecc55d2e92a74fc845618a61c6058742c50cbfcd3574eb27f4706bc296da`, `06973df2e1c7ae10a053dc5869101e6baca927ff30faa3dc947c56c870bf7e35`, `b1045103a26c6d0cf9345c172459bb3b4f85eb541470aead25fa7677bd63ddf3`. The original failed SVG had hash `fb056666709d591d18424c409e12ac48783f021eac7c3a6b115fdac6beca89ec` (diagnosis) but was overwritten by the regeneration before a copy was made; its bytes are not preserved. This is an evidence preservation gap; don't claim full failed-SVG preservation.
