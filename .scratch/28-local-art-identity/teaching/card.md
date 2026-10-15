# Exercise28 — local artwork identity comparison card

## Question and limited scope

One proposed cause to isolate: the fixed local stripe currently changes pigment with the visible material side. Compare that existing side-dependent treatment with the exact same local-UV stripe filled by one fixed pigment on both faces. The intent is to test a hypothesis, not to assert that the shared pigment is clearer or that identity has passed.

## Frozen support and artwork contract

- Use only the four preregistered Exercise27 cases: `primary-dplus` (`alpha=π`, D+), `variation-2pi3-dplus` (`alpha=2π/3`, D+), `negative-dminus` (exact symmetric D−), and `card-dplus` (the original opaque root-attached card, D+).
- Keep the exact 16×2 support, 64 support triangles, route/frame/width (`0.36` world units), cameras, base pigments (`#e68aa4`, `#7188bd`), opaque depth kernel, existing full local strip `u=[0,1]`, `v=[-0.18,0.18]`, and card. Add neither geometry nor marks; actual inputs remain 160 or 162, below 256.
- `SIDE_DEPENDENT` uses existing `#472639` on front-facing local stripe and `#fff1b8` on back-facing local stripe. `SHARED_FIXED_LOCAL` uses `#472639` on the complete same local mask, without consulting side/camera for stripe pigment. It does not change support fill or visibility.
- Geometry/depth proof is only a technical artifact-integrity gate. D− has zero actual-depth hidden-side winners; its raw kernel hidden-area residual is `+2.6385598046880347e-7`, within the recorded `1e-6` tolerance, not exact zero area.

## Gates and non-claims

Technical source, support, triangle-order/UV/frame/camera, depth-fragment/area/oracle, card winner, face-cap, deterministic-render, blind-payload, and board-placement checks are not artistic or perceptual acceptance. The local sight-capability control is not a review of the comparison board. Only a later, separately authorized, verified sight-capability dispatch can qualify a reviewer for the exact one-board neutral payload. No reviewer has been dispatched from this leaf; no provider receipt, response, capability score, formal perception result, artistic PASS, or S1a transfer result exists. Learner execution and milestone/baseline promotion are out of scope.
