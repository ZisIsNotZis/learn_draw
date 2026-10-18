"""Per-part local frames, the two part kinds, and the two-sided paint rule.

A part is authored in its own local (u,v) frame.  `PartFrame` owns the mapping
local -> plane (crop pixels, y up) and the affine depth model of a *plane*
support.  Artwork outline and semantic edges therefore never carry absolute frame
coordinates: they are local points, and the frame is compiler input.

A planar part (cloth lying on a plane) is a closed outline plus semantic edges.
A sheet part (a support that bends through depth, e.g. one ribbon or one hair
sheet) is a parametric surface sample (u,v) -> (plane point, depth); its support
is the parameterization itself, so it may fold back through depth.

The two-sided paint rule is one function shared by both sheet parts: the fill of a
face is chosen by the orientation of its own surface normal against the camera,
i.e. by the projected winding of the triangle.  A sheet that twists shows its
back side where the winding reverses; nothing is painted by declaration.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from scripts.articulated_construction import Camera, Component, Point, SupportFrame

CAMERA = Camera()
HEIGHT = 480.0


def crop(x: float, y: float) -> Point:
    """Observed-crop pixel (y down) -> plane coordinates (y up)."""
    return Point(float(x), HEIGHT - float(y))


def px(p: Point) -> tuple[float, float]:
    """Plane coordinates -> SVG user units (y down)."""
    return (p.u, HEIGHT - p.v)


def dot2(a, b) -> float:
    return a[0] * b[0] + a[1] * b[1]


def unit2(a) -> tuple[float, float]:
    d = math.hypot(a[0], a[1])
    if d <= 1e-12:
        raise ValueError("degenerate part direction")
    return (a[0] / d, a[1] / d)


def _perp(a): return (-a[1], a[0])


def tp(p) -> tuple[float, float]:
    """Point -> plain pair, for the family generators that speak in pairs."""
    return (float(p.u), float(p.v))


def as_points(seq) -> tuple[Point, ...]:
    return tuple(q if isinstance(q, Point) else Point(float(q[0]), float(q[1])) for q in seq)


@dataclass(frozen=True)
class ClothEdge:
    """One semantic line of a part, in the part's local coordinates."""
    type: str
    points: tuple[Point, ...]
    owner: str
    intent: str


def plain_geometry(geom, name: str):
    """A family geometry already expressed in its part's local frame."""
    outline = as_points(geom.outline)
    edges = tuple(ClothEdge(e.type, as_points(e.points), name, e.intent) for e in geom.edges)
    return outline, edges


def to_local_geometry(geom, frame: "PartFrame", name: str):
    """Map a family geometry into its part's local frame, in Point coordinates."""
    outline = as_points(tuple(frame.to_local(Point(*q)) for q in geom.outline))
    edges = tuple(ClothEdge(e.type, as_points(tuple(frame.to_local(Point(*q)) for q in e.points)),
                            name, e.intent) for e in geom.edges)
    return outline, edges


@dataclass(frozen=True)
class PartFrame:
    """Local (u,v) frame of one part, plus its affine depth model.

    Depth is affine in the plane: z(p) = z0 + grad . (p - origin), with `grad`
    the depth gradient in plane coordinates.  The corresponding SupportFrame's
    axis slopes are the projections of `grad` on the frame axes, so depth and
    position always come from the same frame.
    """
    name: str
    origin: Point
    axis_angle_deg: float
    z0: float
    grad: tuple[float, float] = (0.0, 0.0)

    @property
    def axis(self) -> tuple[float, float]:
        a = math.radians(self.axis_angle_deg)
        return (math.cos(a), math.sin(a))

    @property
    def perp(self) -> tuple[float, float]:
        return _perp(self.axis)

    def to_local(self, p: Point) -> Point:
        d = (p.u - self.origin.u, p.v - self.origin.v)
        return Point(dot2(d, self.axis), dot2(d, self.perp))

    def to_plane(self, q: Point) -> Point:
        ax, ay = self.axis
        px_, py_ = self.perp
        return Point(self.origin.u + q.u * ax + q.v * px_,
                     self.origin.v + q.u * ay + q.v * py_)

    def depth_at_local(self, q: Point) -> float:
        return self.z0 + dot2(self.grad, (q.u * self.axis[0] + q.v * self.perp[0],
                                          q.u * self.axis[1] + q.v * self.perp[1]))

    def depth_at_plane(self, p: Point) -> float:
        return self.z0 + dot2(self.grad, (p.u - self.origin.u, p.v - self.origin.v))

    def support(self) -> SupportFrame:
        ax, ay = self.axis
        qx, qy = self.perp
        du = dot2(self.grad, self.axis)
        dv = dot2(self.grad, self.perp)
        return SupportFrame(f"{self.name}-support", f"{self.name}-depth",
                            (self.origin.u, self.origin.v, self.z0),
                            (ax, ay, du), (qx, qy, dv))


def align_depths(a: PartFrame, b: PartFrame, plane_point: Point,
                 tangent: tuple[float, float]) -> tuple[PartFrame, PartFrame]:
    """Make two supports share both depth and depth slope along a seam.

    A declared joint whose two cloth pieces lie on supports with unrelated depth
    planes is not one surface: the engine would tear it.  The correction is the
    same for both parts (mean slope along the seam tangent), so neither part
    keeps a privileged depth.
    """
    t = unit2(tangent)
    gap_a = dot2(a.grad, t)
    gap_b = dot2(b.grad, t)
    common = 0.5 * (gap_a + gap_b)
    fixed = []
    for frame, gap in ((a, gap_a), (b, gap_b)):
        corrected = (frame.grad[0] + (common - gap) * t[0],
                     frame.grad[1] + (common - gap) * t[1])
        z0 = frame.z0
        fixed.append(PartFrame(frame.name, frame.origin, frame.axis_angle_deg, z0, corrected))
    depth = 0.5 * (fixed[0].depth_at_plane(plane_point) + fixed[1].depth_at_plane(plane_point))
    out = []
    for frame in fixed:
        dz = depth - frame.depth_at_plane(plane_point)
        out.append(PartFrame(frame.name, frame.origin, frame.axis_angle_deg,
                             frame.z0 + dz, frame.grad))
    return out[0], out[1]


def align_one(frame: PartFrame, reference: PartFrame, plane_point: Point,
              tangent: tuple[float, float]) -> PartFrame:
    """Make `frame` agree with `reference` in depth and along-seam slope at a seam.

    Only the component along the seam direction is taken from the reference: the
    part keeps its own tilt across the seam, so this is an alignment, not a copy.
    """
    t = unit2(tangent)
    gap = dot2(frame.grad, t) - dot2(reference.grad, t)
    corrected = (frame.grad[0] - gap * t[0], frame.grad[1] - gap * t[1])
    candidate = PartFrame(frame.name, frame.origin, frame.axis_angle_deg, frame.z0, corrected)
    dz = reference.depth_at_plane(plane_point) - candidate.depth_at_plane(plane_point)
    return PartFrame(frame.name, frame.origin, frame.axis_angle_deg, frame.z0 + dz, corrected)


@dataclass(frozen=True)
class Anchor:
    """A named boundary station of a part, in the part's local coordinates."""
    point: Point
    tangent: tuple[float, float] | None = None

    def __post_init__(self):
        if not isinstance(self.point, Point):
            object.__setattr__(self, "point", Point(float(self.point[0]), float(self.point[1])))


@dataclass(frozen=True)
class PlanarPart:
    """One cloth object authored on a plane support in its own local frame."""
    name: str
    intent: str
    frame: PartFrame
    outline: tuple[Point, ...]
    edges: tuple = ()
    fill: str = "#e8e7dc"
    anchors: dict = field(default_factory=dict)
    authored: tuple = ()
    attachments: tuple = ()

    def component(self) -> Component:
        return Component(self.name, self.intent, self.frame.support(), self.outline,
                         self.fill, tuple((s, t, a) for s, t, a in self.attachments),
                         tuple((k, v.point) for k, v in self.anchors.items()))

    def plane_anchor(self, key: str) -> tuple[Point, float, tuple[float, float] | None]:
        a = self.anchors[key]
        p = self.frame.to_plane(a.point)
        t = None if a.tangent is None else (
            a.tangent[0] * self.frame.axis[0] + a.tangent[1] * self.frame.perp[0],
            a.tangent[0] * self.frame.axis[1] + a.tangent[1] * self.frame.perp[1])
        return p, self.frame.depth_at_local(a.point), t


@dataclass(frozen=True)
class SheetPart:
    """One cloth object whose support bends through depth: a parametric sheet.

    `sample(u,v)` returns (plane point, depth).  Faces are generated from a
    (u,v) grid and painted by `two_sided_fill`, so the sheet's two sides are a
    geometric fact, never a declared colour list.
    """
    name: str
    intent: str
    front_fill: str
    back_fill: str
    grid: tuple = ()      # grid[i][j] = ((x, y, z),)
    anchors: dict = field(default_factory=dict)
    authored: tuple = ()

    def faces(self) -> list[tuple[tuple, str, str]]:
        out = []
        for i in range(len(self.grid) - 1):
            for j in range(len(self.grid[i]) - 1):
                p00 = self.grid[i][j]
                p10 = self.grid[i + 1][j]
                p11 = self.grid[i + 1][j + 1]
                p01 = self.grid[i][j + 1]
                fill = two_sided_fill(p00, p10, p01, self.front_fill, self.back_fill)
                out.append(((p00, p10, p11), fill, self.name))
                out.append(((p00, p11, p01), fill, self.name))
        return out

    def plane_anchor(self, key: str):
        xyz, tangent = self.anchors[key]
        return Point(xyz[0], xyz[1]), xyz[2], tangent


def face_normal_z(p00, p10, p01) -> float:
    """z component of the surface normal of one param face (camera axis is +z)."""
    ax, ay, az = p10[0] - p00[0], p10[1] - p00[1], p10[2] - p00[2]
    bx, by, bz = p01[0] - p00[0], p01[1] - p00[1], p01[2] - p00[2]
    return ax * by - ay * bx


def two_sided_fill(p00, p10, p01, front: str, back: str) -> str:
    """Paint a face by its own projected winding: the face turned toward the
    camera gets the front colour, the reverse side the back colour."""
    return front if face_normal_z(p00, p10, p01) >= 0.0 else back


class StripSurface:
    """One continuous strip: a spine, a continuous half width, a depth, a twist.

    `spine(t) -> (x, y)` and `half_width(t)`, `depth(t)`, `twist(t)` are generated
    by the owning part.  `point(t, v)` is the surface itself, so the same relation
    produces both the painted faces and the authored marks lying on the cloth.
    """

    def __init__(self, spine, half_width, depth, twist=None):
        self.spine = spine
        self.half_width = half_width
        self.depth = depth
        self.twist = twist

    def frame_at(self, t: float):
        x, y = self.spine(t)
        before = self.spine(max(0.0, t - 1e-4))
        after = self.spine(min(1.0, t + 1e-4))
        tx, ty = unit2((after[0] - before[0], after[1] - before[1]))
        return (x, y), _perp((tx, ty)), (tx, ty)

    def point(self, t: float, v: float):
        (x, y), (nx, ny), _tan = self.frame_at(t)
        half = self.half_width(t) * v
        z = self.depth(t)
        ang = 0.0 if self.twist is None else self.twist(t)
        return (x + nx * half * math.cos(ang), y + ny * half * math.cos(ang),
                z + half * math.sin(ang))

    def grid(self, samples: int = 48, cols: int = 4):
        rows = []
        for i in range(samples + 1):
            t = i / samples
            rows.append(tuple(self.point(t, -1.0 + 2.0 * j / (cols - 1)) for j in range(cols)))
        return tuple(rows)

    def edge(self, t0: float, t1: float, v: float, steps: int = 24):
        """A polyline on the surface: one cloth edge or one authored crease."""
        return tuple(self.point(t0 + (t1 - t0) * i / steps, v) for i in range(steps + 1))


def grid_edges(grid, col: int) -> tuple[tuple[float, float, float], ...]:
    """One v-index boundary polyline of a sampled sheet, in world 3D points."""
    return tuple(row[col] for row in grid)
