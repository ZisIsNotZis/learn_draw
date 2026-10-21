# B hand-and-dish object study, r1 — independent image-only review (wave 15, package K)

verdict: FAIL — image at check/draft-fullres.png sha256 4dbcad2ec517191c73c75057f948f0a73aeec5566566df922e1f9ac8e8354083, verified with sha256sum before judging.
binding note: the revision named at dispatch was 34b31b4; the owner reported mid-review that the tree advanced to 91782af with the image bytes unchanged. This verdict binds to the image hash only and does not extend to the difference between the two revisions.
binding note: the third binding item did not resolve. .scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1/manifest.sha256 hashes to 8a47f0f097f16e6a9588751ffe7aff9eb0a234ab43203ae3561261d0144d70f5, and no file in the worktree outside .git (files under 2 MB) hashes to 6127712360946cd1072ae59bf00548cbcc3175826aca5bcfa8e622d511d907b7. Recorded as unverified, not assumed wrong; the image binding is intact and is what this reading rests on.
inputs read: check/draft-fullres.png (900x700, RGB) and check/draft.png (900x700, RGB). Nothing else. The two files decode to identical pixels (`Image.tobytes()` equal, sha256 4dbcad2e… vs 174d7455…), so the detail I cite below is present at 1:1 in both.
method: whole image at 1:1, then nearest-neighbour crops at 2x, 3x, 4x, 6x, 10x (PIL, Image.NEAREST), plus pixel measurements recomputable with the commands given. No reference image exists; I judged whether the study reads, not whether it matches a photograph. Every reproduction below runs from .scratch/35-r1-articulated-study/evidence/B-hand-study-v1-r1/; each crop box and scale factor below was executed against this exact image file before the verdict was written, written to /tmp and then deleted.

## Verdict question 1 — does it read as a hand holding a plate?

partly, and the grasping relation does not survive.

what reads: the dish is supported, not floating. The hand and plate share a silhouette with no gap, and the skin mass disappears behind the plate's underside, so the plate visibly rests on the hand.

what does not read: the digits are 4-5 parallel tapered blades that never cross the rim. One skin pixel falls inside the plate's interior ellipse, an antialiasing artefact at the rim edge, and none elsewhere; the hand's topmost pixel is y=426 and the plate's underside at x=450 ends at y=482, so every digit is occluded from below and nothing opposes the plate from above. The silhouette below the rim is a fan of straight wedges that merge into one column, with no knuckle, no joint, no pad, no nail, no thenar form and no wrist. The failure reading that fires is "five prongs" / "a dish on a stick".
location: prong array x 288-644, y 426-700.
reproduction: `python3 -c "from PIL import Image; im=Image.open('check/draft-fullres.png').convert('RGB'); c=im.crop((270,440,660,700)); c.resize((c.width*2,c.height*2),Image.NEAREST).save('/tmp/c2_prongs.png')"`
reproduction: silhouette runs, bladed count. Skin mask `(r>g+8)&(g>b+8)&(r>120)`. Horizontal runs longer than 4 px: y=455 → 2 runs, y=480 → 5 runs [(298-386),(399-407),(492-508),(520-528),(537-620)], y=500 → 4, y=560 → 3, y=600 → 1 (everything merged into the column).
reproduction: no grip. `(skin & ((((X-450)/300)**2+((Y-258)/205)**2) < 1)).sum()` = 1 pixel, the rim-edge antialiasing; the plate's underside probe is the last grey pixel in column x=450, at y=482.
criterion violated: "a hand holding a plate — a hand with distinguishable digits whose relation to the plate is legible". Counting distinguishes the digits; anatomy does not, and the relation that is legible is resting-on rather than holding.

## Verdict question 2 — does the object read as one connected thing?

mostly, with one defect.

reading: plate and hand are adjacent and read as one composite object, not as two pictures pasted together. That part of the criterion is met.

defect: there is a background-coloured hole through the hand where two digits meet the rim, at fullres x 533-545, y 470-482. The brightest pixel is (539,473) = (243,238,230), the exact background colour, and it is visible at 4x as a white wedge inside the hand silhouette.
reproduction: `python3 -c "from PIL import Image; im=Image.open('check/draft-fullres.png').convert('RGB'); c=im.crop((510,455,570,500)); c.resize((c.width*4,c.height*4),Image.NEAREST).save('/tmp/sliver4x.png')"`
severity: nonblocking. It is small against a 900x700 frame and the connectivity reading survives it; it is listed so the next revision does not have to rediscover it.

## Verdict question 3 — does the image read as a drawing rather than an exposed mesh?

no. This is the blocking failure.

finding B1 — the dish reads as an exposed triangle fan with a dithered grid.
location: bowl interior, whole of x 160-740, y 60-430; the fan apex is at (452,314); the rim carries a dashed stipple seam, clearest at x 300-700, y 60-200.
what is visible at 1:1: a radial fan of wedge facets converging on a small quad at the apex, plus a grid of dashes and radial stipple over the whole bowl, plus a dashed concentric seam on the rim. These are the seams of the mesh and the dither of the render, presented as the drawing's texture, so the surface reads as a shaded triangle fan rather than as a drawn plate.
reproduction: `python3 -c "from PIL import Image; im=Image.open('check/draft-fullres.png').convert('RGB'); c=im.crop((420,290,480,335)); c.resize((c.width*10,c.height*10),Image.NEAREST).save('/tmp/apex10x.png')"` — the apex bullseye and the dash grid.
reproduction: `python3 -c "from PIL import Image; im=Image.open('check/draft-fullres.png').convert('RGB'); c=im.crop((300,60,700,200)); c.resize((c.width*3,c.height*3),Image.NEAREST).save('/tmp/rim3x.png')"` — the rim's dashed seam and the wedge fan edge-on.
reproduction: recomputable measurement. Horizontal scan of luminance at y=312, x 340-600: mean 179.5, std 7.28, min 165, max 193, and 25 local bright maxima in 260 px. A drawn gradient cannot produce 25 turning points in 260 px; a striated fan and a dither grid do.
criterion violated: "the image reads as a drawing rather than as an exposed mesh".

finding B2 — the hand reads as flat-shaded planes with hard polyline edges.
location: hand mass x 288-644, y 426-700, worst at the serrated silhouette x 538-548, y 482-560.
what is visible at 1:1: long planar facets with abrupt luminance steps instead of form shading, and a saw-toothed, stair-stepped silhouette on the right-hand digit that no drawn contour would produce.
reproduction: `python3 -c "from PIL import Image; im=Image.open('check/draft-fullres.png').convert('RGB'); c=im.crop((500,440,600,580)); c.resize((c.width*6,c.height*6),Image.NEAREST).save('/tmp/artifact_edge.png')"`
reproduction: measurement. Skin mask gives 51105 px with 2141 distinct RGB values, 397 after quantising to a 4-level step — a flat-shaded facet palette, not blended form shading. Adjacent-pixel horizontal luminance jumps greater than 6 inside the hand: 4801 of 50323 px = 9.54%.
criterion violated: "the image reads as a drawing rather than as an exposed mesh", same criterion as B1, a second independent site.

## Nonblocking findings (do not repair under this verdict)

N1: background-coloured hole through the hand at (533-545, 470-482), stated above.
N2: contact is a hard cut with no contact shading. Skin luminance immediately under the rim is at full value (x=450, first twelve skin rows 182-183; x=580, 183/180/181), so the junction carries no occlusion and reinforces the resting-on reading of the hand finding.
N3: scale. Plate silhouette spans 623 px in x (138-761) against a hand mass 356 px wide at the contact (288-644). The plate is large against the hand by roughly the margin of a serving platter against one hand; it still reads, but it leans the composition toward "object on a stand".
N4: object identity. The dish reads as a wide shallow bowl with a thick lip as readily as a plate. Legible as a dish either way; naming it a plate is not settled by the picture alone.
N5: the right-hand digit is a single large blade angled 30 degrees off vertical, which is the only form that could be taken for a thumb. It does not read as a thumb, because it carries no opposition, no joint and no pad; if a viewer does read a thumb there, the hand reading improves without changing B1 or B2.

## Residual risk

The blocking findings rest on texture and silhouette, not on tone, so a change of palette, lighting or background would not clear them; they would need the mesh seams and the flat shading removed, which I did not verify is achievable in this pipeline. My reading of "drawing" is a judgement of what the marks look like, and a second reader who accepts faceting as a drawing style would downgrade B2 and keep B1, since the dithered grid and the apex quad are rendering artefacts rather than style. The hand failure is the softer of the two judgements: it depends on what "holding" is taken to require. If the brief accepts "supported from below with no opposing digit" as holding, then the first question is met and only B1 and B2 block. I could not check the manifest binding, and I could not verify the revision by git, since this review ran no git command and read no file outside its two inputs; a reader who needs the revision claim should confirm commit 91782af against the image hash independently.

## Verdict

FAIL.
blocking: B1 (exposed triangle fan and dither grid in the dish), B2 (flat-shaded facets and polyline serration on the hand), and the hand reading in question 1 (prongs with no grasp).
not blocking: N1-N5.
nothing was repaired; nothing was committed; no file other than this one was written; the /tmp crops are deleted.
