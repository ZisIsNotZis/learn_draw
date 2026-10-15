# Fit-centering correction — review follow-up

A fresh blind reviewer reported that the first generated boards looked almost blank/cropped. Parent independently traced the defect to the panel fit translation, not to either drawing rule. The pre-fix boards were **invalid visual-perception evidence** and are preserved byte-for-byte with their prior check bundles and hashes under `evidence/before-fit-fix/`; the bundle's `SHA256SUMS` SHA-256 is `0e32394c05c433a7d6932bc27fadb3766373a38cbf79509339baa3f754be2d64`.

Only the affine panel translation in `scripts/ribbon_drawing.py::_fit_points` changed. For projected support/card bounds and uniform scale `s`, the correct mappings are `x'=ox+s*x` and `y'=oy-s*y`, with `ox=(W-s(min_x+max_x))/2` and `oy=(H+s(min_y+max_y))/2`. No support point, card, camera, case, material, line selection, motif, sampling, or rule changed. `teaching/drawing-card.md` documents that bounds include every support vertex and all four card corners, and are fitted with a 16-pixel panel inset.

The dedicated tests add an independent projection/bounds oracle over all 8 frozen specs and both front/oblique cameras. Expected scale, offsets, center, and margins are computed directly from freshly projected support/card points; `_fit_points` output is only compared against these independently derived values. A small Chromium raster assertion additionally confirms the teaching panel paints its central viewport. Both tests pass.

The renderer SHA changed to `a3569bf9492ab88a5377a25523acbd93adf32069ac02825f8b370ec45cdba2dc`; this changed the cached-export cache key and forced all 24 panels to rebuild. The corrected build had 24 compiled, 0 reused, 0 failed; panel CPU time summed to 209.388s, maximum 21.107s. The direct line-only equivalence check passed again for 3,432 rule-B support-card paths. A second export reused all 24 new panels and reproduced all four corrected board SVGs byte-for-byte.

Corrected board and PNG SHA-256 values:

| output | SHA-256 |
|---|---|
| `comparison-labelled.svg` | `62ab9a281e4c512df8b3c4dee4624cfc5fb435b0a6cb30bea3c75a0098610bed` |
| `comparison-unlabelled.svg` | `af9c67519701018aba08b3328e0f4194f248b3dc2334807cc3db9cd00b880681` |
| `line-only-labelled.svg` | `eafad0579b23f07e2e5c563ca377d85f7fbf798cd14c6d70f82d2ad2053e4922` |
| `line-only-unlabelled.svg` | `773c1757390eb4791051bec8c7c88e0d329d6620bbb2c061378e8e79e2175f10` |
| `comparison-labelled.png` | `ec95dc6045ebfc0e31bf0f041dfb70fea8d5fea97c6d55db65a03b195d61402f` |
| `comparison-unlabelled.png` | `8f3af57948f1e74ae018526b9a2acc2d63f333a4e5817f463c030a1b5a90ae69` |
| `line-only-labelled.png` | `b42286b449ad95797c9bc77d2852c990da8f32e63395896a05b0b05770213e8c` |
| `line-only-unlabelled.png` | `45e4132ab817a03aa2d73691c5743d46b0bebb77e79a90d053f782f1711d7092` |

The four corrected `draw check` runs completed after the rebuild. Their exact image lists remain the same single paths, now generated from the corrected board revision:

- `evidence/check/comparison-labelled/report.txt`: `.scratch/20-ribbon-drawing-rule/evidence/check/comparison-labelled/draft.png  -- the drawing`
- `evidence/check/comparison-unlabelled/report.txt`: `.scratch/20-ribbon-drawing-rule/evidence/check/comparison-unlabelled/draft.png  -- the drawing`
- `evidence/check/line-only-labelled/report.txt`: `.scratch/20-ribbon-drawing-rule/evidence/check/line-only-labelled/draft.png  -- the drawing`
- `evidence/check/line-only-unlabelled/report.txt`: `.scratch/20-ribbon-drawing-rule/evidence/check/line-only-unlabelled/draft.png  -- the drawing`

All four report drafts are full resolution: labelled 1380×2170, unlabelled 1380×2144. Both unlabelled SVGs have no `<text>` nodes. Streaming XML validation found unique IDs across each corrected board. The corrected labelled PNG was rendered twice and matched byte-for-byte. Affected combined suite: 45 tests passed in 20.119s (`test_ribbon_drawing`, ribbon family, vector visibility, and spatial sketch). `git diff --check` passed.

The parent's earlier code review applies to the pre-fix renderer revision. A focused code review of current SHA `a3569bf9492ab88a5377a25523acbd93adf32069ac02825f8b370ec45cdba2dc` and a fresh blind review of these corrected full-frame boards are still required. No visual-quality judgment, line-rule acceptance, transfer, or S2 claim is made by this fit fix.
