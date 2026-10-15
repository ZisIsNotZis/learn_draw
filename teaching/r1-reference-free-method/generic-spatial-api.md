# Generic spatial drawing API (public)

This is a narrow guide to existing project functions, not a new drawing language, backend, renderer product, or study-case recipe. Use only after the creator's separate role authorization. Inputs are caller-authored geometry and text; this API has no raster/image input. Do not import or call `build_study_case`: it is a frozen, task-specific R1 B example, not a public creator preset or API.

## Validated callable surface

From `scripts.articulated_construction`:

- `Point(u, v)` — local 2D point with basic addition, subtraction, and scaling.
- `SupportFrame(support_id, depth_ref, origin, u_axis, v_axis)` — affine local-to-world support mapping; all axes and origin are world 3-vectors. The axes must span a surface.
- `Camera(...)` — orthographic projection basis; default world X/Y are screen horizontal/vertical and world Z is depth (larger depth is nearer).
- `Component(name, intent, support, outline, fill, attachments=(), anchors=())` — named authored polygon on a support. `outline` is a tuple of local `Point`s; `anchors` is a tuple of `(anchor_name, Point)`; each attachment is `(target_component_name, own_anchor_name, target_anchor_name)`.
- `construct_limb(LimbParameters(...))` — existing two-segment IK and smooth taper construction. `LimbParameters` fields are `shoulder`, `upper_length`, `fore_length`, `hand_target`, `elbow_branch` (`-1` or `+1`), `upper_width_shoulder`, `upper_width_elbow`, `fore_width_elbow`, `fore_width_wrist`, and `support`. It validates finite/reachable target, positive lengths/widths, branch, and support. It returns elbow/wrist, two generated outlines and palm attachment; it is generic math, not a pose preset.
- `triangulate_polygon(outline)` — deterministic triangulation of a simple polygon, rejecting invalid/self-intersecting outlines.
- `component_faces(components, camera)` — maps local component outlines through actual support frames and camera to depth-bearing faces.
- `visible_scene_regions(components, camera)` / `visible_scene(components, camera)` — compute visible fill regions/fragments by depth. These are the only visibility path; no author-specified cuts.

From `scripts.articulated_line_visibility`:

- `visible_segment_spans(q0, q1, faces, owner_component)` — depth-clips an authored 3D segment against the same support-mapped face set and returns visible normalized intervals. Inputs `q0`, `q1` are world/camera-projected `(x,y,depth)` endpoints. It requires faces for the named owner.

No public `build_study_case`, preset parameter table, or generic SVG/file renderer is introduced. Existing callable functions above suffice for constructing and inspecting geometry; a consumer may choose their own output format and destination. Do not bypass computed-depth geometry by using global painter sorting or hand-authored visible intervals.

## Neutral geometry-signature example

A generic support-plane setup has the signature:

```python
from scripts.articulated_construction import (
    Camera, Component, Point, SupportFrame, component_faces,
    triangulate_polygon, visible_scene_regions,
)

surface = SupportFrame(
    support_id="caller-surface", depth_ref="caller-depth",
    origin=(0.0, 0.0, 0.0),
    u_axis=(1.0, 0.0, 0.0), v_axis=(0.0, 1.0, 0.0),
)
shape = Component(
    name="caller-shape", intent="neutral polygon on a declared support",
    support=surface,
    outline=(Point(-1, -1), Point(1, -1), Point(0, 1)),
    fill="#777777",
)
triangulate_polygon(shape.outline)         # deterministic simple-polygon validation
faces = component_faces((shape,), Camera())
visible = tuple(visible_scene_regions((shape,), Camera()))
```

This is only a geometry/API smoke example, not a suggested composition, subject, answer, art target, or heldout hint. The same component path carries depth from its actual support; `depth_ref` does not itself set occlusion.

## Available construction and extension rules

- Existing reusable construction math: vector operations on `Point`, `construct_limb` two-link IK and smoothstep taper, support-frame mapping, polygon triangulation, camera projection, triangle visibility, and semantic-line span clipping. Reuse only these general algorithms; do not copy case-builder logic or constants.
- For a new original generator, define a named input type with semantic anchors/relations and a clear shape intent. It should emit local `(u,v)` points from relations or a typed edge profile. Limit direct hand-authored coordinates to about four per shape; generate additional outline samples from the typed rule rather than typing a dense contour. Validate finite/reachable inputs, deterministic output, simple polygon topology, and support binding. Keep generator math generic, separately testable, and independent of any reference/task-specific case. There is no authority here to modify existing source/backend or add a generator; future source changes need separate authorization.
- Shape generation and visibility are distinct: generators define the local filled artwork; support/camera map it to world and screen; the visibility engine clips by computed depth. Semantic line art is separately authored and then clipped using `visible_segment_spans` as appropriate.

## Output safety and limits

This guide adds no writer, wrapper, renderer, runtime/provider control, or output-path mechanism. If a future separately authorized creator writes output, it must use a newly created dedicated directory, verify the destination file does not already exist, and never target/overwrite a candidate, prior evidence, old learner artifact, or repository baseline. Keep outputs separate from existing evidence. This documentation does not claim any renderer/build/test was run or any image exists.
