"""Constructed surface family: one loft primitive for every limb-like mass.

A limb is a centreline polyline through a handful of semantic points, carrying a
width law. Offsetting the centreline to both sides by that law and closing the
two ends with elliptic caps produces the outline. Digits, the palm pad, the arm,
the neck and the skull are all instances of this one primitive; none of them is a
traced contour and none carries more than three semantic points.

Coordinate convention: every point is local (u, v) on the component's own
support frame, which is what the project's spatial engine consumes.
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


def smooth_centerline(points: tuple[Point, ...], samples: int, rounds: int = 2) -> tuple[Point, ...]:
    """Round a sparse semantic polyline (knuckle) into a smooth, evenly spaced centreline."""
    rounded = tuple(points)
    for _ in range(rounds):
        grown = [rounded[0]]
        for a, b in zip(rounded, rounded[1:]):
            grown.append(mix(a, b, 0.25))
            grown.append(mix(a, b, 0.75))
        grown.append(rounded[-1])
        rounded = tuple(grown)
    lengths = [0.0]
    for a, b in zip(rounded, rounded[1:]):
        lengths.append(lengths[-1] + math.hypot(b.u - a.u, b.v - a.v))
    total = lengths[-1]
    if total <= 1e-9:
        raise ValueError("hand-family centreline has no length")
    result: list[Point] = []
    cursor = 0
    for index in range(samples):
        target = total * index / (samples - 1)
        while cursor < len(rounded) - 2 and lengths[cursor + 1] < target:
            cursor += 1
        span = lengths[cursor + 1] - lengths[cursor]
        t = 0.0 if span <= 1e-12 else (target - lengths[cursor]) / span
        result.append(mix(rounded[cursor], rounded[cursor + 1], t))
    return tuple(result)


def knots_width(knots: tuple[tuple[float, float], ...]):
    """Width law from (t, half-width) knots, smoothstep between them.

    A knot list is the whole authored input to a limb's thickness: how wide it is
    where it starts, at the joint, and at the end. Nothing else sets the shape.
    """
    ordered = tuple(sorted(knots))
    if ordered[0][0] != 0.0 or ordered[-1][0] != 1.0:
        raise ValueError("width knots must start at t=0 and end at t=1")

    def law(t: float) -> float:
        for (t0, w0), (t1, w1) in zip(ordered, ordered[1:]):
            if t0 - 1e-12 <= t <= t1 + 1e-12:
                span = t1 - t0
                local = 0.0 if span <= 1e-12 else (t - t0) / span
                smooth = local * local * (3 - 2 * local)
                return w0 + (w1 - w0) * smooth
        return ordered[-1][1]

    return law


@dataclass(frozen=True)
class Station:
    """One cross-section: where the limb is, which way it runs, and its width either side."""
    center: Point
    tangent: Point
    half_left: float
    half_right: float


@dataclass(frozen=True)
class Loft:
    """A constructed limb: arc-length stations and the closed outline they emit."""
    stations: tuple[Station, ...]
    outline: tuple[Point, ...]
    def end(self) -> Point:
        return self.stations[-1].center
    def station_at(self, t: float) -> Station:
        index = min(len(self.stations) - 1, max(0, int(round(t * (len(self.stations) - 1)))))
        return self.stations[index]


def _stations(centers: tuple[Point, ...], left, right) -> tuple[Station, ...]:
    stations = []
    count = len(centers)
    for index, center in enumerate(centers):
        t = index / (count - 1)
        previous = centers[max(0, index - 1)]
        following = centers[min(count - 1, index + 1)]
        tangent = unit(Point(following.u - previous.u, following.v - previous.v))
        half_left, half_right = left(t), right(t)
        if min(half_left, half_right) <= 0:
            raise ValueError("hand-family width must stay positive")
        stations.append(Station(center, tangent, half_left, half_right))
    return tuple(stations)


def _cap(center: Point, tangent: Point, half_left: float, half_right: float,
         start: bool, steps: int) -> list[Point]:
    """Elliptic end cap: sweeps from the left edge, round the end, back to the right edge."""
    sign = -1.0 if start else 1.0
    radius_along = 0.5 * (half_left + half_right)
    across = perp(tangent)
    points = []
    for index in range(steps + 1):
        phi = math.pi * index / steps
        side = half_left if math.cos(phi) >= 0 else half_right
        points.append(shifted(shifted(center, tangent, sign * radius_along * math.sin(phi)),
                              across, side * math.cos(phi)))
    return points


def loft_tube(points: tuple[Point, ...], knots, *, samples: int = 19,
              right_knots=None, cap_steps: int = 6, rounds: int = 2,
              start_flat: bool = False) -> Loft:
    """Build a limb from a semantic centreline polyline and its width knots."""
    centers = smooth_centerline(tuple(points), samples, rounds)
    left = knots_width(tuple(knots))
    right = knots_width(tuple(right_knots)) if right_knots is not None else left
    stations = _stations(centers, left, right)
    left_side = [shifted(s.center, perp(s.tangent), s.half_left) for s in stations]
    right_side = [shifted(s.center, perp(s.tangent), -s.half_right) for s in stations]
    end_cap = _cap(stations[-1].center, stations[-1].tangent, stations[-1].half_left,
                   stations[-1].half_right, False, cap_steps)
    start_cap = [] if start_flat else _cap(stations[0].center, stations[0].tangent,
                                          stations[0].half_left, stations[0].half_right, True, cap_steps)
    # walk: left side out, round the end cap, right side back, round the start cap.
    ordered = left_side + end_cap + list(reversed(right_side)) + list(reversed(start_cap))
    outline: list[Point] = []
    for point in ordered:
        if not outline or math.hypot(point.u - outline[-1].u, point.v - outline[-1].v) > 1e-9:
            outline.append(point)
    if math.hypot(outline[0].u - outline[-1].u, outline[0].v - outline[-1].v) <= 1e-9:
        outline.pop()
    return Loft(stations, tuple(outline))


def digit_tube(base: Point, joint: Point, tip: Point, *, base_half: float, joint_half: float,
               tip_half: float, samples: int = 17) -> Loft:
    """One finger or thumb: base -> knuckle joint -> tip, tapering, with a bulb at the joint."""
    return loft_tube((base, joint, tip),
                     ((0.0, base_half), (0.46, joint_half), (0.58, joint_half * 0.97), (1.0, tip_half)),
                     samples=samples)


def arm_tube(shoulder: Point, elbow: Point, wrist: Point, *, shoulder_half: float,
             elbow_half: float, wrist_half: float, samples: int = 33) -> Loft:
    """The whole arm as one continuous limb: shoulder cap, bend at the elbow, taper to the wrist."""
    return loft_tube((shoulder, elbow, wrist),
                     ((0.0, shoulder_half), (0.42, elbow_half * 1.06), (0.52, elbow_half),
                      (1.0, wrist_half)),
                     samples=samples, cap_steps=7, rounds=3)


def profile_tube(bottom: Point, top: Point, *, knots, samples: int = 21,
                 start_flat: bool = False) -> Loft:
    """A vertical mass (skull, neck, hair) from its bottom point to its top point."""
    return loft_tube((bottom, top), knots, samples=samples, rounds=1, start_flat=start_flat)


@dataclass(frozen=True)
class PalmPad:
    """The palm: contact rim on the dish's foot line, pad back to the wrist, thenar on one flank."""
    outline: tuple[Point, ...]
    contact_edge: tuple[Point, ...]
    wrist_edge: tuple[Point, Point]
    knuckle_edge: tuple[Point, Point]
    axis: Point


def palm_pad(contact_edge: tuple[Point, ...], wrist: Point, *, wrist_half: float,
             knuckle_drop: float, thenar_bulge: float) -> PalmPad:
    """Build the palm from the dish-derived contact rim and the wrist, nothing else.

    The wrist end is a shallow rounded heel, deliberately shorter along the axis than the
    sleeve's own cap, so the forearm's cuff covers it and the palm emerges from the sleeve
    instead of butting it.

    The contact rim (derived from the dish's own foot) is the palm's distal edge, so
    the pad ends exactly where the dish's underside begins; the pad widens from the
    narrowing wrist to the knuckles, and the thenar flank carries the thumb root.
    """
    edge = tuple(contact_edge)
    if len(edge) < 3:
        raise ValueError("palm pad needs at least three derived contact stations")
    foot_mid = mix(edge[0], edge[-1], 0.5)
    axis = unit(Point(foot_mid.u - wrist.u, foot_mid.v - wrist.v))
    across = perp(axis)
    wrist_up = shifted(wrist, across, wrist_half)
    wrist_down = shifted(wrist, across, -wrist_half)

    def spline(span, steps: int = 7) -> list[Point]:
        a, c1, c2, b = span
        points = []
        for index in range(steps + 1):
            t = index / steps
            s = 1 - t
            points.append(Point(s ** 3 * a.u + 3 * s * s * t * c1.u + 3 * s * t * t * c2.u + t ** 3 * b.u,
                                s ** 3 * a.v + 3 * s * s * t * c1.v + 3 * s * t * t * c2.v + t ** 3 * b.v))
        return points

    # distal knuckle pad: from the rim's far end the palm continues briefly, then turns
    knuckle_end = shifted(edge[-1], across, -knuckle_drop)
    distal = spline((edge[-1],
                     shifted(mix(edge[-1], knuckle_end, 0.40), axis, 0.008),
                     shifted(mix(edge[-1], knuckle_end, 0.74), axis, 0.004),
                     knuckle_end))
    # ulnar flank: knuckle pad back to the wrist's lower side, bulging outward
    ulnar = spline((knuckle_end,
                    shifted(mix(knuckle_end, wrist_down, 0.32), across, -0.028),
                    shifted(mix(knuckle_end, wrist_down, 0.70), across, -0.022),
                    wrist_down))
    wrist_cap = [shifted(wrist,
                         Point(across.u * math.cos(theta) - axis.u * math.sin(theta),
                               across.v * math.cos(theta) - axis.v * math.sin(theta)),
                         wrist_half if math.cos(theta) >= 0 else wrist_half * 0.45)
                 for theta in (math.pi - math.pi * k / 5 for k in range(6))]
    # thenar flank: the thumb side, bulging out from the wrist toward the rim's near end
    thenar = spline((wrist_up,
                     shifted(mix(wrist_up, edge[0], 0.36), across, thenar_bulge),
                     shifted(mix(wrist_up, edge[0], 0.76), across, thenar_bulge * 0.42),
                     edge[0]))

    outline: list[Point] = []
    for point in list(edge) + distal + ulnar + wrist_cap + thenar:
        if not outline or math.hypot(point.u - outline[-1].u, point.v - outline[-1].v) > 1e-9:
            outline.append(point)
    if math.hypot(outline[0].u - outline[-1].u, outline[0].v - outline[-1].v) <= 1e-9:
        outline.pop()
    return PalmPad(tuple(outline), edge, (wrist_up, wrist_down), (edge[-1], knuckle_end),
                   axis)
