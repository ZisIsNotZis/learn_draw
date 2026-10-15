# WP04 render manifest

Authored from the WP03 public fixture; geometry reference isolation: `render_r1.py` imports only project semantic geometry and does not read `image.jpg`. A artwork is authored from the task-freeze's textual observed-scope description, not pixel sampling. B case geometry calls `build_study_case` with frozen semantic values. The sheet SVG embeds A and B panels; separate A and B SVGs are also emitted.

Reproduction (from repository root):

```sh
.venv/bin/python .scratch/35-r1-articulated-study/work/render_r1.py
scripts/draw check .scratch/35-r1-articulated-study/work/artwork-a.svg --outdir .scratch/35-r1-articulated-study/evidence/check-a
scripts/draw check .scratch/35-r1-articulated-study/work/artwork-b.svg --outdir .scratch/35-r1-articulated-study/evidence/check-b
scripts/draw check .scratch/35-r1-articulated-study/work/artwork.svg --outdir .scratch/35-r1-articulated-study/evidence/check-sheet
```

Renderer: `scripts/draw check` / `scripts/draw.py` using cached `chrome-headless-shell`; executable reports `Google Chrome for Testing 151.0.7922.34`; Playwright Python 1.62.0. All checks omit `--ref`, so engine receives no target.

Artwork projection coordinates: Camera is `Camera()` from WP03 (orthographic, azimuth 30°, elevation 8°). For each panel, component local outlines are mapped by each `SupportFrame.local_to_world`, then `Camera.project`, and panel fit is computed from projected component extents with 34px horizontal/65px vertical inset. SVG screen mapping is panel center plus/minus the fit scale. A panel is x=30,y=100,w=470,h=1020; B baseline x=520,y=100,w=410,h=480; B variant x=970,y=100,w=410,h=480; control x=520,y=610,w=410,h=480. B's support/world geometry/depth-derived fragments come from `visible_scene_regions`; SVG doesn't reproduce reference pixels or specify visibility intervals. Authored line marks are separate named art strokes, not mesh edges.

SHA-256:

- `work/artwork.svg`: `fb056666709d591d18424c409e12ac48783f021eac7c3a6b115fdac6beca89ec`
- `work/artwork-a.svg`: `fdcee3b90c221e3507574ed7546eddf5a44f8e76163385410828827bf1923d28`
- `work/artwork-b.svg`: `d093c9674235ca21dc5af78c198b7bb669b2ebfb6cbf3353e1cef5c1f65fb9e8`
- `work/render_r1.py`: `228a1f59126a04cf86472f23839b3a559a1fe1d672bee5aed10cbdf7d2c6b05b`
- `check-a/draft.png`: `f165ecc55d2e92a74fc845618a61c6058742c50cbfcd3574eb27f4706bc296da`
- `check-b/draft.png`: `06973df2e1c7ae10a053dc5869101e6baca927ff30faa3dc947c56c870bf7e35`
- `check-sheet/draft.png`: `b1045103a26c6d0cf9345c172459bb3b4f85eb541470aead25fa7677bd63ddf3`

Fresh-review handoff lists, with no author context:

- `.scratch/35-r1-articulated-study/evidence/check-a/draft.png`
- `.scratch/35-r1-articulated-study/evidence/check-b/draft.png`
- `.scratch/35-r1-articulated-study/evidence/check-sheet/draft.png`

No visual verdict has been made here. These lists are not an artwork acceptance or R1 PASS.
