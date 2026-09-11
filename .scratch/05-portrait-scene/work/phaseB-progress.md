# Phase B progress

- [x] ribbon body → wave node (broad cloth band: spine [[-60,585],[300,565],[520,585],[400,720]], w 400, amp 16, len 260, sag 0.03; start cap parked off-canvas, end cap tucks under skirt)
- [x] ribbon tail → wave node (taper end, tailGrad light→mauve; repositioned to the ref's left-edge streak x0-45 y390-560)
- [x] hair strands → strands generators (right wall n9/dir92, wing n8/dir95)
- [x] curtain → strands generator (n10/dir88, inks 2c4a6e+6f9ecb)
- [x] skirt creases → strands generator (n6/dir105, reads as faint as ref)
- [x] render rounds by looking (pixel-probe maps + zone distances; image viewing broken mid-session — see report caveat)
- [x] node count 142 → 133 (see report: ≤70 target predates the shading+density passes)
- [x] polys ≤30 pts: no NEW polys >30 (4 legacy blobs 45-48 pts untouched)
- [x] param demo: amp 16→32, sag 0.03→0.3 on a copy — ribbon edge-profile stddev 28.3→39.7, zero change right of x=640; demo values REVERTED
- [x] RENDERER FIX (Phase A bug): strands emitter emitted opacity twice → invalid XML → chrome dropped all content; fixed + regression test (h)
