# Head primitive usability review

Date: 2026-11-12

## Purpose and scope

This is a purpose-specific tool usability review of a simple, flat-colour, front-facing cartoon head primitive for VLM authorship. An unattached avatar head is allowed. Realistic light, a body, and a finished portrait are not requirements. This is not an artwork acceptance gate, heldout test, or transfer pass. No sealed brief, source code, or older image was read. No source or older image was modified.

## Commands

Working directory for both commands: `D:/vibe/learn_draw_studio`.

```powershell
.venv/Scripts/python.exe examples/studio/head_probe.py --hair side-part --outdir evidence/studio-head/usability/default
.venv/Scripts/python.exe examples/studio/head_probe.py --hair side-part --eye-scale 0.92 --outdir evidence/studio-head/usability/smaller-eyes
```

Both exited 0. The authored interface input was a hairstyle selector and, in the second case, one eye scale value; no paths or point coordinates were supplied by the reviewer. I directly viewed both generated `artwork.png` files at their 640 x 640 display size.

## Visible facts

- The default reads immediately as a coherent frontal cartoon head: a bounded face and chin, two ears, paired brows and eyes, a small nose and mouth, a surrounding hair mass, and a recognisable side part. Features are centred consistently enough to read as one head. There are no detached facial parts or obvious holes.
- The pale skin, blue hair, brown eyes and dark contours are differentiated clearly. Flat fills and the spare nose/mouth fit this stated primitive use. A standalone head without neck/body is acceptable under the supplied purpose.
- In the smaller-eyes image, both eye apertures and their contents are visibly smaller about the same facial positions. The difference is modest but visible when comparing the two images. The brows, face outline, ears, nose, mouth, hair silhouette and framing appear unchanged. This supports a real, local control in these two samples; it is not evidence about extreme values or every hairstyle.
- The large fringe covers almost the entire right-side forehead and leaves that brow close to the hair edge. It still reads as hair over a face, but it limits the visible brow/forehead area and the room available for expression.
- The hair reads as several broad panels. Thin interior lines describe their joins; the side sections have a long, narrow pointed termination on each side. A straight horizontal rear-hair bottom is visible behind the lower face. These are strong geometric simplifications, especially at the side-to-cap joins and exposed lower edge.
- The eye treatment is heavier than the mouth/nose treatment: thick dark upper contours and outer lash marks, white almond apertures, round brown irises and tiny highlights. It is recognisable, but gives the head a specific cosmetic/cartoon style rather than a neutral base.

## Decision

**The default has actual minimum practical use as the requested flat frontal head primitive. A redraw of the underlying geometry is not necessary to establish that minimum.** It offers a recognisable coherent avatar through the supported interface without manual path authoring. The demonstrated eye adjustment is real and visibly local. This verdict does not mean the image is polished or that the full tool is validated.

### Blocking defects for this stated use

None observed in the two rendered samples. I would not reject an otherwise suitable tool solely because this component has no body, uses flat fills, or has a stylised face.

### Tool-design issues worth correcting

- Hair panel attachment and endpoint rules deserve improvement: the paired needle-like ends and abrupt rear-hair horizontal termination make the default feel constructed from rigid pieces. Correct these through shared hairstyle/join/termination rules if improving the default, rather than asking VLM callers to patch paths. These are quality weaknesses, not blockers to the stated minimum.
- Exposing a semantic fringe-clearance or forehead/brow-visibility control would be useful if the tool is expected to support expressions. The current visible fringe crowds one brow. These samples establish the crowding, not whether such a control already exists.
- If a neutral base is promised, lash/upper-lid style should be selectable semantically. The present eye style is a valid choice; the issue would be lack of choice for users needing another style. The two probes do not establish the existing style-control surface.

### Optional finished-art refinements

Hair colour, a softer or more angular chin, thinner eye outlines, less symmetrical side tips, stronger expression, highlights, shading and a neck/body are artistic choices or composition finishing work here. None is required to make this primitive recognisable. The hair joins and termination rules above are more reusable tool concerns than colour or decoration.

## Limits

Only the requested side-part default and eye-scale 0.92 were exercised. No parameter extremes, other hairstyles, poses, attachment to a body, text-only invention task, API discoverability session, occlusion stress case, or reference independence was tested. The local-change assessment is visual; no pixel-difference measurement was used. This review supplies a usability judgement for the named purpose and must not be cited as a whole-drawing pass or heldout/transfer result.
