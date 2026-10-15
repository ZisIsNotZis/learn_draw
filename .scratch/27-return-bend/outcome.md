# Exercise27 — finite technical result and unresolved perception

## Current disposition

The bounded Exercise27 center-route implementation, fixed-grid geometry proof, deterministic render artifacts, and corrected blind-review routing are complete for their finite scope. The reviewed source remains `scripts/ribbon_return.py` SHA-256 `618d701c3a26eb1f97d6b6cfd210ffe41eba3fe25032eb216d3c2ead398d2607`, with 12 focused tests in `scripts/tests/test_ribbon_return.py`. Source review run `70dabd7b-90cb-4b9c-949f-aef3fbc2c400` checked the constructor, local UV strip, normal-side selection, actual-depth path, frozen inputs, finite face cap and tests; its report's blind-routing P1 was separately corrected and rechecked by routing review run `d7985bbc-19b7-4b26-bcf0-f2c65caef09b` (OK with notes). This closes only bounded technical/provenance work, not renderer-wide guarantees.

Fresh board-only blind review is now complete. Its text report (`return-board-only-blind.md`, output run `2c07f590-2f5f-4b87-8871-457c38723c28`) describes bands, apparent fold/underlap and a card covering part of the band, but says the path, attachment, and whether examples show the same object remain unclear. The report does not establish a positive perception benefit, reliable source/front/back identity, or S1a readability. S1a perception and learner transfer therefore remain **NOT PASSED**; no new learner run follows.

## Finite geometry and preserved diagnostics

The fixed `16×2` geometry proof at `evidence/proof/geometry-gate-completion.json` (SHA-256 `5c1306b6c0fe37dc8aa22892ea013899ad46689eaa83a4b3750c452f59056ab9`) records D+ facing areas `0.2321336277/0.3945447568`, independent nearest-depth winners `1489/2513`, and D− hidden/near winners `0/2581`. D−'s tiny `2.6385598e-7` hidden-side kernel residual remains non-positive evidence. Support has 64 triangles, support plus complete local stripe/body art submits 160 actual inputs, and the card case submits 162/256. These are finite sampled area/depth facts only; they do not certify unrestricted visibility or perception.

The original D− false-oracle proof recording 611 hidden-side winners remains untouched at `evidence/proof/geometry-gate.json`; its scratch barycentric typo diagnosis and corrected independent mask are preserved at `evidence/diagnostics/dminus-resolution-v2.json`. Do not replace those raw data or reinterpret the failure as geometry evidence.

## Blind-routing provenance

The first board-plus-ordered-raw-panel report is preserved byte-for-byte at `evidence/provenance/invalid-blind-routing/report-leaked-raw-panel-order.txt` (SHA-256 `fd2b1b7638f64b112ec597ace6bbb88c31b5de3b6bd4b544d99e21b2a03ca1bc`) and remains invalid for perception review. Its resulting 452b792b description remains provisional, not acceptance. The current `evidence/report.txt` (SHA-256 `f7a7346f3a962882db499f2d173f4f8be9d78df3af8d13907bcca534c1f30e8b`) routes exactly the existing randomized unlabelled board plus neutral question, with no standalone panels, mappings, roles or expected answer. `evidence/provenance/blind-routing-ledger.json` (SHA-256 `cf6a0b2bffa988bc70fad59240281adc83ffc2b31407baf02eb396596433054f`) separates routing-only source from unchanged render producer/manifest and records all 24 board/panel SVG/PNG hashes unchanged by the correction. `evidence/provenance/determinism.json` binds 12 existing images to repeated matching PNG hashes. The corrected blind description is text observation only; no writer visual inspection is claimed.

## Limits and retained work

The route midpoint remains edge-on in D+; the symmetric D− case retains its hidden-side residual; exact ties and renderer limitations remain as documented in the ticket and proof. The incorrect 611 count, source pins, old axial/untwisted Exercise19/24 controls, frozen cases, images, previous learner answers, and exposure/material/face limits remain preserved. Exercise20's earlier full-perimeter-plus-uniform-motif trial changed combined drawing rules and used the old renderer; it is negative history, not the isolated local-marker comparison proposed in `.scratch/28-local-art-identity/design.md`, and not proof that the new idea works.

No art/S1a/S2, ordinary-model transfer, hair/figure, actual reference route, baseline promotion, or commit is established. A later local-art comparison requires a separate design/review authorization; this outcome authorizes no render or source edit.
