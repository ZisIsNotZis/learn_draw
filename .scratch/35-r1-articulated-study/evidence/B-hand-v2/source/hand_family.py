"""Constructed hand primitive family: tapered tube digits and a palm cup.

One primitive does the work: a tube -- a centreline of stations offset to both
sides by a width law that tapers along the length, closed by round end caps.
Palm, four fingers and thumb are all instances of that family, each generated
from a couple of semantic points (where it starts, where it ends) plus a few
proportion numbers. No contour is traced and no digit is drawn on top of a blob.

Coordinate convention: every point is local (u, v) on the component's own
support frame, exactly as the project's spatial engine consumes it.
"""
from __future__ import annotations
from dataclasses import dataclass
import math

from scripts.articulated_construction import Point


def unit(vector: Point) -> Point:
    length = math.hypot(vector.u, vector.v)
    if length <= 1e-12:
        raise ValueError("hand-family direction is degenerate")
    return Point(vector.u / length, vector.v / length)


def perp(vector: Point) -> Point:
    return Point(-vector.v, vector.u)


def mix(a: Point, b: Point, t: float) -> Point:
    return Point(a.u + (b.u - a.u) * t, a.v + (b.v - a.v) * t)


def shifted(point: Point, direction: Point, distance: float) -> Point:
    return Point(point.u + direction.u * distance, point.v + direction.v * distance)


@dataclass(frozen=True)
class TubeStation:
    """One cross-section of a tube: where the limb is, and how wide it is there."""
    center: Point
    half_width: float
    tangent: Point


@dataclass(frozen=True)
class Tube:
    """A constructed digit: arc-length stations plus the closed outline they generate."""
    stations: tuple[TubeStation, ...]
    outline: tuple[Point, ...]
    def tip(self) -> Point:
        return self.stations[-1].center
    def base(self) -> Point:
        return self.stations[0].center


def _chaikin_open(points: tuple[Point, ...], iterations: int = 2) -> tuple[Point, ...]:
    """Round a sparse knuckle polyline into a smooth centreline, keeping both end points."""
    rounded = tuple(points)
    for _ in range(iterations):
        grown = [rounded[0]]
        for a, b in zip(rounded, rounded[1:]):
            grown.append(mix(a, b, 0.25))
            grown.append(mix(a, b, 0.75))
        grown.append(rounded[-1])
        rounded = tuple(grown)
    return rounded


def _resample(points: tuple[Point, ...], count: int) -> tuple[Point, ...]:
    """Even arc-length stations so the width law is measured along the digit, not per control point."""
    lengths = [0.0]
    for a, b in zip(points, points[1:]):
        lengths.append(lengths[-1] + math.hypot(b.u - a.u, b.v - a.v))
    total = lengths[-1]
    if total <= 1e-9:
        raise ValueError("hand-family centreline has no length")
    targets = [total * index / (count - 1) for index in range(count)]
    result: list[Point] = []
    cursor = 0
    for target in targets:
        while cursor < len(points) - 2 and lengths[cursor + 1] < target:
            cursor += 1
        span = lengths[cursor + 1] - lengths[cursor]
        t = 0.0 if span <= 1e-12 else (target - lengths[cursor]) / span
        result.append(mix(points[cursor], points[cursor + 1], t))
    return tuple(result)


def taper_width(t: float, base_half: float, tip_half: float, joint_dip: float,
                joint_at: float = 0.40) -> float:
    """Width law: smoothstep taper from base to tip, with one local narrowing at the knuckle."""
    smooth = t * t * (3 - 2 * t)
    width = base_half + (tip_half - base_half) * smooth
    dip = math.exp(-((t - joint_at) / 0.14) ** 2)
    return width * (1 - joint_dip * dip)


def _stations(centers: tuple[Point, ...], widths: tuple[float, ...]) -> tuple[TubeStation, ...]:
    stations = []
    for index, (center, width) in enumerate(zip(centers, widths)):
        if width <= 0:
            raise ValueError("hand-family width must stay positive")
        previous = centers[max(0, index - 1)]
        following = centers[min(len(centers) - 1, index + 1)]
        stations.append(TubeStation(center, width, unit(Point(following.u - previous.u,
                                                             following.v - previous.v))))
    return tuple(stations)


def tube_outline(stations: tuple[TubeStation, ...], cap_steps: int = 5) -> tuple[Point, ...]:
    """Offset the centreline to both sides and close each end with a round cap."""
    left = [shifted(s.center, perp(s.tangent), s.half_width) for s in stations]
    right = [shifted(s.center, perp(s.tangent), -s.half_width) for s in stations]
    end, start = stations[-1], stations[0]
    end_cap = [shifted(end.center,
                       Point(perp(end.tangent).u * math.cos(step) + end.tangent.u * math.sin(step),
                             perp(end.tangent).v * math.cos(step) + end.tangent.v * math.sin(step)),
                       end.half_width)
               for step in (math.pi * k / cap_steps for k in range(cap_steps + 1))]
    start_cap = [shifted(start.center,
                         Point(perp(start.tangent).u * math.cos(step) - start.tangent.u * math.sin(step),
                               perp(start.tangent).v * math.cos(step) - start.tangent.v * math.sin(step)),
                         start.half_width)
                 for step in (math.pi - math.pi * k / cap_steps for k in range(cap_steps + 1))]
    ordered = left + end_cap + list(reversed(right)) + start_cap
    outline: list[Point] = []
    for point in ordered:
        if not outline or math.hypot(point.u - outline[-1].u, point.v - outline[-1].v) > 1e-9:
            outline.append(point)
    if math.hypot(outline[0].u - outline[-1].u, outline[0].v - outline[-1].v) <= 1e-9:
        outline.pop()
    return tuple(outline)


def tapered_digit(base: Point, knuckle: Point, tip: Point, *, base_half: float, tip_half: float,
                  joint_dip: float = 0.10, samples: int = 15) -> Tube:
    """One digit: base -> knuckle -> tip centreline, tapered, with a round fingertip."""
    centers = _resample(_chaikin_open((base, knuckle, tip)), samples)
    widths = tuple(taper_width(index / (samples - 1), base_half, tip_half, joint_dip)
                   for index in range(samples))
    stations = _stations(centers, widths)
    return Tube(stations, tube_outline(stations))


@dataclass(frozen=True)
class PalmCup:
    """The palm as a cup: its rim edge is the contact line derived from the dish underside."""
    outline: tuple[Point, ...]
    contact_edge: tuple[Point, ...]
    wrist: Point
    axis: Point
    length: float


def palm_cup(contact_edge: tuple[Point, ...], wrist: Point, *, wrist_half: float,
             side_bow: float = 0.045) -> PalmCup:
    """Build the palm from the dish-derived contact edge and the wrist, nothing else.

    The contact edge (left to right, derived elsewhere from the dish's underside)
    is the palm's distal rim; the two sides follow the axis from that rim back to
    a centred wrist cap, so the pad narrows toward the arm.
    """
    edge = tuple(contact_edge)
    if len(edge) < 3:
        raise ValueError("palm cup needs at least three derived contact stations")
    foot_mid = mix(edge[0], edge[-1], 0.5)
    axis = unit(Point(foot_mid.u - wrist.u, foot_mid.v - wrist.v))
    across = perp(axis)
    length = math.hypot(foot_mid.u - wrist.u, foot_mid.v - wrist.v)
    def side(start: Point, end: Point, outward: float) -> tuple[Point, ...]:
        delta = Point(end.u - start.u, end.v - start.v)
        return (start,
                shifted(mix(start, end, 0.34), across, outward),
                shifted(mix(start, end, 0.74), across, outward * 0.55),
                end)

    def spline(span: tuple[Point, ...], steps: int = 6) -> list[Point]:
        a, c1, c2, b = span
        points = []
        for index in range(steps):
            t = index / steps
            s = 1 - t
            points.append(Point(s ** 3 * a.u + 3 * s * s * t * c1.u + 3 * s * t * t * c2.u + t ** 3 * b.u,
                                s ** 3 * a.v + 3 * s * s * t * c1.v + 3 * s * t * t * c2.v + t ** 3 * b.v))
        points.append(b)
        return points

    upper_side = spline(side(shifted(wrist, across, wrist_half), edge[0], side_bow * length))
    lower_side = spline(side(shifted(wrist, across, -wrist_half), edge[-1], -side_bow * length * 0.8))
    wrist_cap = [shifted(wrist,
                         Point(across.u * math.cos(theta) - axis.u * math.sin(theta),
                               across.v * math.cos(theta) - axis.v * math.sin(theta)),
                         wrist_half)
                 for theta in (math.pi - math.pi * k / 5 for k in range(6))]

    # walk: derived contact rim (left -> right), lower flank back to the wrist,
    # the rounded wrist cap, then the upper flank out to the rim's left end.
    outline: list[Point] = []
    for point in list(edge) + list(reversed(lower_side)) + wrist_cap + upper_side:
        if not outline or math.hypot(point.u - outline[-1].u, point.v - outline[-1].v) > 1e-9:
            outline.append(point)
    if math.hypot(outline[0].u - outline[-1].u, outline[0].v - outline[-1].v) <= 1e-9:
        outline.pop()
    return PalmCup(tuple(outline), edge, wrist, axis, length)
