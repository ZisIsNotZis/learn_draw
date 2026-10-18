"""Composition glue for the smooth spatial and depth/line APIs (copied from

goal-recovery-r1-v2-completion/spatial_adapter.py; only the vendor path is repointed at

the shared evidence/vendor-smooth-spatial copy)."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Iterable

from scripts.articulated_construction import Camera, Component, Point, SupportFrame, component_faces
from scripts.articulated_line_visibility import visible_segment_spans
from scripts.vector_visibility import visible_regions

_VENDOR = Path(__file__).resolve().parents[2] / "vendor-smooth-spatial"
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
    *, intent: str, fill: str,
    attachments: tuple[tuple[str, str, str], ...] = (),
    anchors: tuple[tuple[str, Point], ...] = (),
    steps_per_segment: int = 4,
) -> VisibleSmoothComponent:
    """Guard generated local contour; consumed fill and edge spans share that mapped contour."""
    controls = tuple(semantic_controls)
    if len(controls) < 3:
        raise ValueError("closed semantic family needs at least three generated controls")
    sampled = sample_closed_curve(controls, steps_per_segment=steps_per_segment)
    validate_closed_contour(sampled)
    component = Component(component_name, intent, support, sampled, fill, attachments, anchors)
    faces = component_faces((component, *tuple(occluding_components)), camera)
    fills = tuple(region for region in visible_regions(faces) if region[2] == component_name)
    world = tuple(camera.project(support.local_to_world(point)) for point in sampled)
    spans = []
    for start, end in zip(world, world[1:] + world[:1]):
        for lo, hi in visible_segment_spans(start, end, faces, component_name):
            spans.append((tuple(start[i] + (end[i]-start[i])*lo for i in range(3)),
                          tuple(start[i] + (end[i]-start[i])*hi for i in range(3))))
    return VisibleSmoothComponent(component, sampled, faces, fills, tuple(spans))


def project_visible_semantic_path(points: Iterable[Point], owner: Component, camera: Camera,
                                  scene_components: Iterable[Component]):
    """Clip each generated semantic line segment against the actual shared depth scene."""
    path = tuple(points)
    faces = component_faces(tuple(scene_components), camera)
    world = tuple(camera.project(owner.support.local_to_world(point)) for point in path)
    spans = []
    for start, end in zip(world, world[1:]):
        for lo, hi in visible_segment_spans(start, end, faces, owner.name):
            spans.append((tuple(start[i] + (end[i]-start[i])*lo for i in range(3)),
                          tuple(start[i] + (end[i]-start[i])*hi for i in range(3))))
    return tuple(spans)
