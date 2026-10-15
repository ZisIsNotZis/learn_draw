"""Revision-local composition of sampled smooth contours and project spatial visibility APIs."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Iterable

from scripts.articulated_construction import Camera, Component, Point, SupportFrame, component_faces
from scripts.articulated_line_visibility import visible_segment_spans
from scripts.vector_visibility import visible_regions

_VENDOR = Path(__file__).resolve().parent.parent / "vendor-smooth-spatial"
if str(_VENDOR) not in sys.path:
    sys.path.insert(0, str(_VENDOR))
from smooth_spatial import sample_closed_curve, validate_closed_contour


@dataclass(frozen=True)
class VisibleSmoothComponent:
    component: Component
    validated_sampled_contour: tuple[Point, ...]
    projected_faces: tuple
    visible_fill_regions: tuple[tuple[str, str, str], ...]
    authored_boundary_spans: tuple[tuple[tuple[float, float, float], tuple[float, float, float]], ...]


def build_visible_smooth_component(
    semantic_controls: Iterable[Point],
    component_name: str,
    support: SupportFrame,
    camera: Camera,
    occluding_components: Iterable[Component],
    *,
    intent: str = "authored semantic contour",
    fill: str = "#ffffff",
    steps_per_segment: int = 6,
) -> VisibleSmoothComponent:
    """Sample and guard the actual contour, then derive its fill and ink from shared spatial faces."""
    controls = tuple(semantic_controls)
    if len(controls) < 3:
        raise ValueError("a closed smooth component needs at least three semantic controls")
    sampled = sample_closed_curve(controls, steps_per_segment=steps_per_segment)
    # Deliberately guard the exact value consumed below; the sampler also guards internally.
    validate_closed_contour(sampled)
    occluders = tuple(occluding_components)
    component = Component(component_name, intent, support, sampled, fill)
    scene = (component, *occluders)
    faces = component_faces(scene, camera)
    fills = tuple(region for region in visible_regions(faces) if region[2] == component_name)
    spans = []
    world = tuple(camera.project(support.local_to_world(point)) for point in sampled)
    for start, end in zip(world, world[1:] + world[:1]):
        for lo, hi in visible_segment_spans(start, end, faces, component_name):
            p0 = tuple(start[i] + (end[i] - start[i]) * lo for i in range(3))
            p1 = tuple(start[i] + (end[i] - start[i]) * hi for i in range(3))
            spans.append((p0, p1))
    return VisibleSmoothComponent(component, sampled, faces, fills, tuple(spans))


def project_visible_semantic_segment(
    start: Point,
    end: Point,
    owner: Component,
    camera: Camera,
    occluding_components: Iterable[Component],
) -> tuple[tuple[tuple[float, float, float], tuple[float, float, float]], ...]:
    """Project an authored semantic line and clip it against the same support-mapped face scene."""
    scene = (owner, *tuple(occluding_components))
    faces = component_faces(scene, camera)
    q0 = camera.project(owner.support.local_to_world(start))
    q1 = camera.project(owner.support.local_to_world(end))
    output = []
    for lo, hi in visible_segment_spans(q0, q1, faces, owner.name):
        p0 = tuple(q0[i] + (q1[i] - q0[i]) * lo for i in range(3))
        p1 = tuple(q0[i] + (q1[i] - q0[i]) * hi for i in range(3))
        output.append((p0, p1))
    return tuple(output)
