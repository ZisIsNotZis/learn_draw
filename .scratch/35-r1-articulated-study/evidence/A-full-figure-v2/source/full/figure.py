"""The full figure: the inherited A-cloth-v8 torso, placed in the reference's own frame,
plus the parts that frame needs and the torso crop could not contain.

Nothing here authors absolute coordinates by hand beyond a stated handful of landmarks
per part: the outlines come from generators (ellipse, annulus, dome, catmull, strip),
because the invariant is that geometry is computed and only a few landmarks are typed.

The build reads no image.  The reference seeded the numbers below while the landmarks
were picked; after that it is closed, and `tests/test_full_figure.py` proves it by
building with the reference absent.
"""
from __future__ import annotations

import dataclasses
import html
import math

from scripts.articulated_construction import Camera, Point, component_faces, triangulate_polygon
from scripts.vector_visibility import visible_regions

from ..lines import Occluders, visible_runs_of_mark
from ..parts import bodice, bow, collar, hair, head, skin, sleeve
from ..parts.frames import (ClothEdge, PartFrame, PlanarPart, SheetPart, StripSurface,
                           plain_geometry)

WIDTH, HEIGHT = 1024, 1024
CAMERA = Camera()

# The crop is image pixels (500,320)-(900,800) at 1:1, and the crop's plane is y-up with
# HEIGHT 480, so the same point in this frame is the crop's plane point plus this shift.
CROP_SHIFT = (500.0, 224.0)

# ---- palette: inherited values are the A-cloth-v8 ones, unchanged -------------------
BACKGROUND_SKY = "#c6d8dc"
BACKGROUND_TEAL = "#56adb8"
BACKGROUND_GREEN = "#add5b1"
HAT_NAVY = "#33405c"
HAT_CROWN = "#3a4a68"
HAT_UNDER = "#262f45"
BRIM_TEAL = "#569cae"
BRIM_TEAL_DARK = "#437c8c"
HAIR_LIT = "#3e73a5"
HAIR_SHADE = "#2f5f92"
HAIR_DEEP = "#27606b"
SHADOW_BLUE = "#16406a"
HAIR_INK = "#233c60"
SKIN = "#f2e3d3"
SKIN_SHADE = "#e3c9bd"
CREAM = "#e2ebe0"
CREAM_SHADE = "#d3e0d5"
MINT = "#cbdfd3"
MINT_SHADE = "#b9d0c6"
DEEP_TEAL = "#20505c"
PALE_BLUE = "#a8c4d4"
COLLAR_BLUE = "#a8c9d7"
EYE_WHITE = "#fbf6ee"
NOSE_SHADE = "#e0b9a4"
PUPIL_GREEN = "#6f9c86"
LINING_PINK = "#e59295"
LINING_ORANGE = "#e0a95f"
BOW_MAGENTA = "#cf4b79"
BOW_DARK = "#a8405f"
PUFF_PINK = "#e0a3ac"
PUFF_PINK_DARK = "#cf8b96"
CUFF_NAVY = "#29354d"
EYE_DARK = "#2c2436"
IRIS = "#dd7f9b"
IRIS_DEEP = "#b8527a"
IRIS_LIGHT = "#7fc4b4"
HIGHLIGHT = "#fdfbf4"
CONTOUR_INK = "#2f3d47"
FOLD_INK = "#5b6a72"

LINE_POLICY = {
    # One readable hierarchy, with no duplicate widths: the outer silhouette carries the
    # figure, free edges turn inside it, and contact/fold marks recede.  Material-specific
    # edges keep their own weight rather than making the whole picture uniformly inked.
    "silhouette": (CONTOUR_INK, 2.4),
    "free_edge": (CONTOUR_INK, 1.9),
    "closure": (CONTOUR_INK, 1.6),
    "contact": (FOLD_INK, 1.35),
    "fold_edge": (FOLD_INK, 0.95),
    "trim": (CUFF_NAVY, 3.5),
    "hair_edge": (HAIR_INK, 2.1),
    "hat_edge": (HAT_UNDER, 2.7),
    "lash": (EYE_DARK, 3.1),
    "hem": (CUFF_NAVY, 9.5),
}

# ---- frame helpers ------------------------------------------------------------------


def full(x: float, y: float) -> Point:
    """Image pixel (y down) -> plane point (y up) in the 1024 frame."""
    return Point(float(x), HEIGHT - float(y))


def frame(name: str, z: float, grad: tuple[float, float] = (0.0, 0.0)) -> PartFrame:
    """A part frame with local == plane, so authored points are plane points."""
    return PartFrame(name, Point(0.0, 0.0), 0.0, z, grad)


def _rot(x: float, y: float, cx: float, cy: float, deg: float) -> tuple[float, float]:
    a = math.radians(deg)
    dx, dy = x - cx, y - cy
    return (cx + dx * math.cos(a) - dy * math.sin(a), cy + dx * math.sin(a) + dy * math.cos(a))


def ellipse(cx, cy, rx, ry, rot=0.0, n=72):
    """Closed ellipse in image pixels, as plane points."""
    out = []
    for i in range(n):
        th = 2 * math.pi * i / n
        x, y = cx + rx * math.cos(th), cy + ry * math.sin(th)
        x, y = _rot(x, y, cx, cy, rot)
        out.append(full(x, y))
    return tuple(out)


def annulus(cx, cy, rx, ry, thickness, rot=0.0, n=112):
    """A closed band: outer ellipse, then the inner ellipse reversed."""
    k = 1.0 - thickness
    outer = list(ellipse(cx, cy, rx, ry, rot, n))
    inner = list(ellipse(cx, cy, rx * k, ry * k, rot, n))
    return tuple(outer + inner[::-1])


def dome(cx, cy, rx, ry, rot=0.0, n=64):
    """The upper half of an ellipse, closed along its own chord: a crown."""
    pts = []
    for i in range(n + 1):
        th = math.pi + math.pi * i / n
        x, y = cx + rx * math.cos(th), cy + ry * math.sin(th)
        x, y = _rot(x, y, cx, cy, rot)
        pts.append(full(x, y))
    return tuple(pts)


def catmull(landmarks, steps=12, closed=True):
    """A smooth closed/open route through landmarks given in image pixels."""
    from ..parts import families as fam
    pairs = [(float(x), float(HEIGHT - y)) for x, y in landmarks]
    if closed:
        pts = fam._catmull_open(tuple(pairs) + (pairs[0],), steps)
    else:
        pts = fam._catmull_open(tuple(pairs), steps)
    return tuple(Point(float(u), float(v)) for u, v in pts)


def puffs(cx, cy, r, n=3, spread=0.78):
    """A clover of n lobes: the pink bow clusters on the hat brim."""
    return tuple(
        (cx + r * spread * math.cos(2 * math.pi * i / n - math.pi / 2),
         cy + r * spread * math.sin(2 * math.pi * i / n - math.pi / 2))
        for i in range(n))


def fringe(anchors, teeth=3, depth=(232.0, 268.0), arc_samples=10):
    """A fringe from four landmarks: a hairline arc, then teeth whose points are generated.

    The authored input is where the fringe starts and ends, where it peaks, and how far its
    lowest tooth reaches.  How many teeth there are, and how deep each one hangs, is the
    generator's business, so the fringe is not a hand-typed station table.
    """
    left, apex, right, low = anchors
    top = []
    for i in range(arc_samples + 1):
        f = i / arc_samples
        # a quadratic through the two temples with the apex as the control point
        x = (1 - f) ** 2 * left[0] + 2 * (1 - f) * f * apex[0] + f * f * right[0]
        y = (1 - f) ** 2 * left[1] + 2 * (1 - f) * f * apex[1] + f * f * right[1]
        top.append((x, y))
    lower = []
    shallow, deepest = depth
    # Soft scallops, not a saw.  The reference's fringe hangs in rounded waves of unequal
    # depth: the depth is a raised cosine per tooth, and each tooth's amplitude and centre
    # come from a fixed irrational pattern, so the comb never repeats and the build is still
    # identical every time.  A first attempt put sharp V teeth on the brow line and read as
    # a broken hairline; a second put a single deep tooth between the eyes; this is neither.
    samples_per_tooth = 6
    n = teeth * samples_per_tooth
    for i in range(n + 1):
        f = i / n
        tooth = f * teeth
        phase = tooth % 1.0
        amplitude = (1.00, 0.66, 0.88, 0.74, 0.92, 0.60)[int(tooth) % 6]
        wave = (0.5 - 0.5 * math.cos(2 * math.pi * phase)) ** 1.15
        lean = 7.0 * math.sin(int(tooth) * 2.399963)
        x = right[0] + (left[0] - right[0]) * f + lean * math.sin(math.pi * phase)
        taper = 1.0 - (abs(f - 0.5) * 2.0) ** 2 * 0.28
        lower.append((x, shallow + (deepest - shallow) * wave * amplitude * taper))
    return tuple(full(x, y) for x, y in (top + lower))


def fringe_arc(anchors, arc_samples=10):
    """The fringe's hairline: the quadratic the generator draws before the teeth."""
    left, apex, right, _low = anchors
    out = []
    for i in range(arc_samples + 1):
        f = i / arc_samples
        x = (1 - f) ** 2 * left[0] + 2 * (1 - f) * f * apex[0] + f * f * right[0]
        y = (1 - f) ** 2 * left[1] + 2 * (1 - f) * f * apex[1] + f * f * right[1]
        out.append((x, y))
    return out


def ellipse_arc(cx, cy, rx, ry, rot=0.0, t0=0.06, t1=0.94, n=64):
    """The near half of an ellipse, in image pixels, from t0 to t1 times pi.

    t runs 0..1 over the *lower* half (image y grows downward), which is the edge of the
    brim that the hair passes behind.
    """
    out = []
    for i in range(n + 1):
        th = math.pi * (t0 + (t1 - t0) * i / n)
        x = cx + rx * math.cos(th)
        y = cy + ry * math.sin(th)
        x, y = _rot(x, y, cx, cy, rot)
        out.append((x, y))
    return out


def band(centreline, deepest, shallow=3.0, power=0.55):
    """A closed band hanging off a line: the shadow the brim lays where it crosses the hair.

    The centreline is the junction itself, so the band cannot float: one edge is the line
    the brim's silhouette makes and the other is that line let fall by a generated depth.
    """
    n = len(centreline)
    top, bottom = [], []
    for i, (x, y) in enumerate(centreline):
        u = i / max(1, n - 1)
        d = shallow + (deepest - shallow) * math.sin(math.pi * u) ** power
        top.append((x, y))
        bottom.append((x, y + d))
    return tuple(full(x, y) for x, y in (top + bottom[::-1]))


def windowed(points, x0, x1):
    return [(x, y) for x, y in points if x0 <= x <= x1]


def clover(cx, cy, r, rot=0.0, lobes=3, spread=0.80, n=120):
    """The exact boundary of n overlapping circles round a centre, as a polar function.

    A union of discs arranged round one point is star-shaped about that point, so its
    boundary is one closed curve with no self-intersection: for each direction the
    radius is the furthest intersection with any lobe.  No arc stitching, no crossing.
    """
    d = r * spread
    phis = [2 * math.pi * i / lobes - math.pi / 2 + math.radians(rot) for i in range(lobes)]
    out = []
    for k in range(n):
        th = 2 * math.pi * k / n
        best = 0.0
        for phi in phis:
            a = th - phi
            b = d * math.cos(a)
            c2 = r * r - d * d * math.sin(a) ** 2
            if c2 <= 0.0:
                continue
            best = max(best, b + math.sqrt(c2))
        out.append((cx + best * math.cos(th), cy + best * math.sin(th)))
    return tuple(full(x, y) for x, y in out)


def lerp2(a, b, f: float):
    return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)


def flat_mark(points, z: float):
    """Plane points -> the 3D polyline a sheet mark is, sitting just in front of its part."""
    return tuple((p.u, p.v, z) for p in points)


def edges(name: str, rows) -> tuple:
    """`rows` = [(class, points, intent)] -> ClothEdges in the part's own coordinates."""
    return tuple(ClothEdge(cls, tuple(points), name, intent) for cls, points, intent in rows)


def planar(name, intent, z, outline, rows=(), fill=CREAM, authored=(), grad=(0.0, 0.0)):
    return PlanarPart(name=name, intent=intent, frame=frame(name, z, grad), outline=outline,
                      edges=edges(name, rows), fill=fill,
                      anchors={}, authored=authored)


# ---- inherited torso, shifted -------------------------------------------------------


def _shift_frame(f: PartFrame) -> PartFrame:
    return dataclasses.replace(f, origin=Point(f.origin.u + CROP_SHIFT[0],
                                               f.origin.v + CROP_SHIFT[1]))


def shift_planar(part: PlanarPart) -> PlanarPart:
    return dataclasses.replace(part, frame=_shift_frame(part.frame))


def shift_sheet(part: SheetPart) -> SheetPart:
    dx, dy = CROP_SHIFT
    grid = tuple(tuple((x + dx, y + dy, z) for (x, y, z) in row) for row in part.grid)
    anchors = {k: ((v[0][0] + dx, v[0][1] + dy, v[0][2]), v[1]) for k, v in part.anchors.items()}
    return dataclasses.replace(part, grid=grid, anchors=anchors)


# The torso is a composition transform, not an edit: the inherited parts keep their own
# bytes, and the frame places them.  The reference's shoulder mass is wider than the crop
# frame's, so the whole torso group is scaled about one point on the body's axis.
# Tried at 1.10 and rejected: scaling the torso group about the body's axis pushed the
# chest bow up over the collar and the chin (the bow is a sheet whose own grid carries the
# knot's place), and the collar disappeared under it.  The figure is composed, not scaled:
# the torso's width is set by where the inherited parts land, and widening it has to be done
# by re-cutting the bodice, not by a single factor over a group.
TORSO_SCALE = 1.0
BOW_SCALE = 1.16
TORSO_ABOUT_XY = (700.0, 560.0)


def scale_about_xy(points):
    """Scale authored image-pixel points about the torso's axis."""
    cx, cy = TORSO_ABOUT_XY
    return tuple((cx + (x - cx) * TORSO_SCALE, cy + (y - cy) * TORSO_SCALE) for x, y in points)


def _scale_local(points, origin, cx, cy, factor):
    out = []
    for p in points:
        lx, ly = p.u - origin.u, p.v - origin.v
        out.append(Point(origin.u + cx + (lx - cx) * factor,
                         origin.v + cy + (ly - cy) * factor))
    return tuple(out)


def scale_planar(part: PlanarPart, factor, plane_cx, plane_cy) -> PlanarPart:
    origin = part.frame.origin
    cx, cy = plane_cx - origin.u, plane_cy - origin.v
    edges = tuple(dataclasses.replace(e, points=_scale_local(e.points, origin, cx, cy, factor))
                  for e in part.edges)
    anchors = {k: dataclasses.replace(a, point=_scale_local((a.point,), origin, cx, cy, factor)[0])
               for k, a in part.anchors.items()}
    return dataclasses.replace(part,
                               outline=_scale_local(part.outline, origin, cx, cy, factor),
                               edges=edges, anchors=anchors)


def scale_sheet(part: SheetPart, factor, plane_cx, plane_cy, plane_y) -> SheetPart:
    def f(xyz):
        return (plane_cx + (xyz[0] - plane_cx) * factor,
                plane_cy + (xyz[1] - plane_cy) * factor, xyz[2])
    grid = tuple(tuple(f(p) for p in row) for row in part.grid)
    return dataclasses.replace(part, grid=grid)


def shift_points(points):
    dx, dy = CROP_SHIFT
    return tuple((x + dx, y + dy, z) for (x, y, z) in points)


def inherited():
    """The A-cloth-v8 assembly, unchanged, moved into this frame."""
    head_parts = head.build()
    collar_parts, opening = collar.build()
    left_root = collar_parts["A-collar-left"].plane_anchor("R")[0]
    right_root = collar_parts["A-collar-right"].plane_anchor("R")[0]
    bodice_parts = bodice.build(opening["Q_plane"], left_root, right_root)
    skin_parts, _ = skin.build(collar_parts, head_parts)
    sleeve_parts = sleeve.build(bodice)
    bow_parts, bow_marks, bow_meta = bow.build()
    hair_parts, hair_marks, hair_meta = hair.build()

    parts, marks = {}, []
    for group in (head_parts, collar_parts, bodice_parts, skin_parts, sleeve_parts, bow_parts,
                  hair_parts):
        for name_, part in group.items():
            parts[name_] = shift_sheet(part) if isinstance(part, SheetPart) else shift_planar(part)
    for name_, owner, cls, points, ink in list(bow_marks) + list(hair_marks):
        marks.append((name_, owner, cls, shift_points(points), ink))
    return parts, marks, dict(opening=opening, bow=bow_meta, hair=hair_meta)


# ---- the composition's landmarks ----------------------------------------------------
# One dict, so a tuning round is an edit here and nowhere else.  Every number is an
# image-pixel landmark read off the reference's crop while the layout was authored; the
# build itself never opens the image.

LAYOUT = dict(
    # the hat: a wide brim seen from below-left, its underside teal, its top face navy
    brim_centre=(680.0, 146.0), brim_rx=286.0, brim_ry=168.0, brim_rot=23.0,
    crown_centre=(806.0, 148.0), crown_rx=152.0, crown_ry=134.0,
    puff_top=(658.0, 52.0), puff_top_r=31.0,
    puff_right=(906.0, 190.0), puff_right_r=41.0,
    # the face, and the fringe that leaves only the lower half of it showing
    chin=(684.0, 384.0),
    # Measured off the reference at 4x (ref/face-4x.png): the far eye is 33 px wide and the
    # near eye 47, the chin is at (685,370), the far cheek is behind the hair at 616 and the
    # near jaw runs to 775.  The face is a three-quarter view, not a frontal oval with a
    # turned gaze: the far side is compressed, the near cheek bulges, and the features sit
    # right of the centre line.
    # Four landmarks drive the whole three-quarter face: chin, compressed far temple,
    # skull top and full near cheek.  The sampled boundary is generated below.
    face_ring=((686.0, 374.0), (622.0, 276.0), (690.0, 174.0), (766.0, 292.0)),
    eye_left=(640.0, 286.0), eye_right=(728.0, 282.0),
    eye_left_r=(16.0, 22.0), eye_right_r=(23.5, 24.0),
    bangs_anchors=((552.0, 212.0), (662.0, 116.0), (812.0, 220.0), (688.0, 292.0)),
    bang_teeth=4, bang_depth=(246.0, 286.0),
    # the neck
    neck_q=((660.0, 372.0), (710.0, 372.0), (714.0, 428.0), (658.0, 428.0)),
    neck_hollow=((624.0, 398.0), (748.0, 398.0), (756.0, 486.0), (616.0, 486.0)),
    # the sailor collar, cut for this frame's neck opening (the inherited pair was cut for a
    # chin 58 px lower and reads as a sliver here)
    collar_left=((692.0, 386.0), (628.0, 406.0), (566.0, 456.0), (556.0, 528.0),
                 (614.0, 506.0), (664.0, 470.0), (686.0, 440.0)),
    collar_right=((700.0, 386.0), (766.0, 404.0), (822.0, 452.0), (826.0, 526.0),
                  (766.0, 502.0), (718.0, 466.0), (706.0, 438.0)),
    _torso_note="the collar, neck and hollow follow TORSO_SCALE, so no seam opens",
    # hair: a mass behind the head, and two falls that hang in front of the shoulders
    hair_back_route=((500.0, 1052.0), (548.0, 300.0), (700.0, 214.0), (930.0, 1052.0)),
    # The falls flare at the shoulders and gather at the hem.  Straight-sided curtains were
    # the first shape and they read as a wig: the reference's hair is a lens — wide where it
    # passes the shoulders, gathered where it ends.
    # The two falls are not the same length: in the reference the hair on her right ends in
    # a curl at the waist while the fall on her left runs to the frame's bottom.  Two equal
    # curtains read as a wig; the asymmetry is what makes it hair.
    fall_left_poly=((598.0, 194.0), (534.0, 300.0), (452.0, 486.0), (470.0, 646.0),
                    (566.0, 688.0), (596.0, 640.0), (540.0, 470.0), (566.0, 372.0)),
    fall_right_poly=((762.0, 192.0), (824.0, 296.0), (890.0, 470.0), (952.0, 704.0),
                     (968.0, 1044.0), (910.0, 1032.0), (876.0, 700.0), (806.0, 400.0)),
    lock_left=((574.0, 250.0), (528.0, 486.0), (516.0, 736.0)),
    curl_left=((572.0, 664.0), (524.0, 700.0), (500.0, 674.0), (516.0, 640.0)),
    streamer=((556.0, 300.0), (446.0, 402.0), (278.0, 516.0), (300.0, 580.0)),
    lock_right=((760.0, 258.0), (786.0, 492.0), (800.0, 740.0)),
    fall_wave=(9.0, 1.6, 0.4),
    # the seated lower mass: skirt over the knees, under-layer, and the fold bands
    # The reference's lower mass, read off ref-lower.png: a large deep-teal field across
    # the centre-bottom, pale mint and cream cloth over its upper right, and the pink and
    # orange lining ribbons crossing the teal diagonally.
    # The reference's lower mass is cloth that has been sat on: its silhouette is not a
    # dome.  The near knee pushes a peak out at (872,806), the far knee a second at
    # (430,930), the valleys between them are where the cloth falls back, and the mass runs
    # off the frame's left and bottom edges instead of closing on itself.
    # Four landmarks per cloth shape.  `lap_outline` expands the skirt anchors into the
    # two knee peaks, the valley and the off-frame hem; no station table is authored.
    skirt=((548.0, 666.0), (812.0, 680.0), (872.0, 810.0), (408.0, 916.0)),
    skirt_teal=((340.0, 704.0), (844.0, 770.0), (902.0, 1050.0), (-36.0, 1050.0)),
    fold_cream=((520.0, 706.0), (650.0, 772.0), (690.0, 1038.0), (516.0, 1038.0)),
    fold_mint=((432.0, 814.0), (596.0, 852.0), (642.0, 1038.0), (410.0, 1038.0)),
    fold_shadow=((558.0, 664.0), (810.0, 680.0), (798.0, 738.0), (570.0, 724.0)),
    underskirt=((650.0, 936.0), (850.0, 900.0), (812.0, 1040.0), (622.0, 1040.0)),
    lining_pink=((214.0, 786.0), (354.0, 824.0), (486.0, 1038.0), (330.0, 1038.0)),
    lining_orange=((360.0, 930.0), (542.0, 900.0), (632.0, 1038.0), (454.0, 1038.0)),
    fold_lines=((0.14, 0.04), (0.32, 0.08), (0.50, 0.12), (0.68, 0.16)),
    # the waist: a gathered band across the blouse, with its peplum flaring below
    waist_band=((590.0, 666.0), (700.0, 660.0), (812.0, 672.0), (809.0, 700.0),
                (700.0, 694.0), (587.0, 700.0)),
    # the blouse's own sides, which the crop's frame cut inside: the reference's bodice is a
    # blouse from shoulder to waist, not the narrow column the inherited part lands as here
    bodice_left=((604.0, 452.0), (572.0, 470.0), (560.0, 560.0), (566.0, 650.0),
                 (592.0, 700.0), (616.0, 690.0), (610.0, 520.0)),
    bodice_right=((800.0, 450.0), (834.0, 468.0), (846.0, 558.0), (840.0, 648.0),
                  (812.0, 700.0), (788.0, 690.0), (794.0, 518.0)),
    # Her left arm carries the visible hand at viewer-right.  Her right arm leaves the
    # viewer-left cuff and disappears behind the skirt, exactly where the reference hides
    # the hand; both routes are generated strips from three attachment landmarks.
    arm_route=((860.0, 556.0), (876.0, 700.0), (866.0, 790.0)),
    far_arm_route=((588.0, 544.0), (568.0, 630.0), (548.0, 724.0)),
    palm=((846.0, 786.0), (884.0, 790.0), (888.0, 834.0), (846.0, 842.0)),
    finger_origin=(850.0, 832.0), finger_step=(9.5, 2.0), finger_r=(6.8, 24.0),
    thumb=((842.0, 800.0), (830.0, 812.0), (836.0, 838.0), (850.0, 828.0)),
)


def field_ribbon(route, half_width):
    """A thin generated background ribbon from at most four centreline landmarks."""
    centre = catmull(route, steps=12, closed=False)
    left, right = [], []
    for i, p in enumerate(centre):
        a = centre[max(0, i - 1)]
        b = centre[min(len(centre) - 1, i + 1)]
        dx, dy = b.u - a.u, b.v - a.v
        n = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / n, dx / n
        taper = math.sin(math.pi * i / max(1, len(centre) - 1)) ** 0.35
        w = half_width * taper
        left.append(Point(p.u + nx * w, p.v + ny * w))
        right.append(Point(p.u - nx * w, p.v - ny * w))
    return tuple(left + right[::-1])


def field():
    """Curved sky/ground masses and floating ribbons, all behind the figure."""
    # The teal horizon and mint bank are generated curves, not angular horizontal bands.
    ground_edge = catmull(((0.0, 354.0), (310.0, 314.0), (650.0, 398.0), (1024.0, 310.0)),
                          steps=14, closed=False)
    ground = tuple(ground_edge) + (full(1024, 1024), full(0, 1024))
    mint_edge = catmull(((0.0, 518.0), (176.0, 592.0), (420.0, 506.0), (574.0, 430.0)),
                        steps=14, closed=False)
    bank = (full(0, 1024), full(0, 518)) + tuple(mint_edge) + (full(418, 1024),)
    return [
        ("A-field-ground", ground, BACKGROUND_TEAL),
        ("A-field-bank", bank, BACKGROUND_GREEN),
        ("A-field-ribbon-high", field_ribbon(((8.0, 430.0), (116.0, 398.0),
                                               (244.0, 444.0), (332.0, 410.0)), 5.0),
         LINING_PINK),
        ("A-field-ribbon-low", field_ribbon(((-8.0, 690.0), (98.0, 650.0),
                                              (210.0, 706.0), (304.0, 668.0)), 4.0),
         CREAM),
        ("A-field-ribbon-curl", field_ribbon(((46.0, 774.0), (126.0, 730.0),
                                               (206.0, 782.0), (252.0, 748.0)), 3.2),
         LINING_ORANGE),
    ]


# ---- the hat -----------------------------------------------------------------------

def hat_parts():
    L = LAYOUT
    bx, by = L["brim_centre"]
    underside = planar("A-hat-brim-under", "the brim's teal underside, seen from below-left",
                       0.20, ellipse(bx, by, L["brim_rx"], L["brim_ry"], L["brim_rot"]),
                       rows=[("silhouette",
                              ellipse(bx, by, L["brim_rx"], L["brim_ry"], L["brim_rot"]),
                              "the brim's outer edge")],
                       fill=BRIM_TEAL, authored=(("brim_centre", L["brim_centre"]),))
    brim_top = dome(bx, by, L["brim_rx"], L["brim_ry"], L["brim_rot"])
    top = planar("A-hat-brim-top", "the brim's navy top face on the far side of its axis", 0.21,
                 brim_top,
                 rows=[("free_edge", brim_top, "the top face's exposed far edge")],
                 fill=HAT_NAVY, authored=(("brim_top_axis", L["brim_centre"]),))
    cx, cy = L["crown_centre"]
    crown_shape = dome(cx, cy, L["crown_rx"], L["crown_ry"], L["brim_rot"])
    crown = planar("A-hat-crown", "the crown dome standing on the brim's top face", 0.22,
                   crown_shape,
                   rows=[("hat_edge", crown_shape, "the crown meeting the brim")],
                   fill=HAT_CROWN, authored=(("crown_centre", L["crown_centre"]),))
    px, py = L["puff_top"]
    puff_top = planar("A-hat-puff-top", "the pink cluster at the crown's back", 0.24,
                      clover(px, py, L["puff_top_r"], rot=14.0),
                      rows=[("free_edge", clover(px, py, L["puff_top_r"], rot=14.0),
                             "the puff's edge")],
                      fill=PUFF_PINK, authored=(("puff_top", L["puff_top"]),))
    qx, qy = L["puff_right"]
    puff_right = planar("A-hat-puff-right", "the pink cluster at the brim's right edge", 0.24,
                        clover(qx, qy, L["puff_right_r"], rot=-16.0),
                        rows=[("free_edge", clover(qx, qy, L["puff_right_r"], rot=-16.0),
                               "the puff's edge")],
                        fill=PUFF_PINK, authored=(("puff_right", L["puff_right"]),))
    return {"A-hat-brim-under": underside, "A-hat-brim-top": top, "A-hat-crown": crown,
            "A-hat-puff-top": puff_top, "A-hat-puff-right": puff_right}


def shadow_parts():
    """T4's missing relation: where the brim crosses the hair, the hair carries its shadow.

    The reference answers this narrowly.  Sampling it along the junction — (600,215),
    (720,205), (800,250), (840,280), (860,310) — gives the *same* lit blue everywhere,
    with one very dark line (0,50,91) exactly at the junction.  So the brim's shadow here
    is a contact line on the hair, not a soft band across it: the hair goes into the
    brim's shadow at the line and comes out of it as a line's width of dark, which is what
    the reference draws.  A broad band was tried first and deleted: the brim's near edge
    is at eye height on the falls, where the hair is in front of the brim and cannot be
    shaded by it.
    """
    L = LAYOUT
    line = fringe_arc(L["bangs_anchors"])
    return {
        "A-shadow-fringe": planar(
            "A-shadow-fringe", "the brim's shadow on the fringe: a contact line along their "
                               "junction, as the reference draws it", 0.51,
            band(line, deepest=7.0, shallow=2.0, power=0.4), fill=SHADOW_BLUE),
    }


# ---- the head ----------------------------------------------------------------------

def head_parts():
    L = LAYOUT
    chin, far_temple, skull_top, near_cheek = L["face_ring"]
    # A generated asymmetric oval through four measured landmarks.  The far side stays
    # compressed while the near cheek carries the turn, so the head cannot read frontal.
    ring = catmull((chin, far_temple, skull_top, near_cheek))
    face = planar("A-face", "the narrow three-quarter face: compressed far side and full near cheek", 0.30,
                  ring, rows=[("silhouette", ring, "the face's outer boundary")],
                  fill=SKIN, authored=tuple((f"face_{i}", p) for i, p in enumerate(L["face_ring"])))
    neck_q = L["neck_q"]
    neck = planar("A-neck", "the neck between the chin and the collar's opening", 0.315,
                  catmull(scale_about_xy(neck_q)), fill=SKIN_SHADE,
                  rows=[("contact", (full(*neck_q[0]), full(*neck_q[1])), "the jaw's underside")],
                  authored=tuple((f"neck_{i}", p) for i, p in enumerate(neck_q)))
    anchors = L["bangs_anchors"]
    edge = fringe(anchors, teeth=L["bang_teeth"], depth=L["bang_depth"])
    # The collar's opening is wider than the neck, and the inherited collar was cut for a
    # chin 58 px lower, so background showed through the two gaps beside the neck (sampled:
    # #56adb8 at (640,395) and (720,415)).  The hollow fills the opening behind the neck.
    hollow = planar("A-neck-hollow", "the shadowed hollow of the collar's opening, behind the "
                                     "neck", 0.29, catmull(scale_about_xy(L["neck_hollow"])),
                    fill=SKIN_SHADE,
                    authored=(("hollow_top", L["neck_hollow"][0]),))
    collar_out = {}
    for side, poly in (("left", scale_about_xy(L["collar_left"])),
                       ("right", scale_about_xy(L["collar_right"]))):
        name = f"A-collar-{side}"
        collar_out[name] = planar(
            name, f"the {side} leaf of the sailor collar, from the neck opening over the "
                  f"shoulder", 0.47, catmull(poly),
            rows=[("free_edge", catmull(poly), "the leaf's own edge")],
            fill=COLLAR_BLUE, authored=(("neck", poly[0]), ("shoulder", poly[1]),
                                        ("front", poly[3])))
    bang = planar("A-hair-bangs", "the fringe: hair falling over the forehead in points", 0.34,
                  edge, rows=[("hair_edge", edge, "the fringe's edge")],
                  fill=HAIR_SHADE,
                  authored=tuple((f"bang_{i}", a) for i, a in enumerate(anchors)))
    return {"A-face": face, "A-neck": neck, "A-neck-hollow": hollow,
            "A-hair-bangs": bang, **collar_out}


def nose_mark():
    """The nose: one short stroke where the face turns, off the centre line."""
    return ("A-nose", "A-face", "fold_edge",
            flat_mark(catmull(((674.0, 316.0), (678.0, 323.0), (675.0, 328.0)),
                              steps=8, closed=False), 0.345), NOSE_SHADE)


def eye_parts():
    L = LAYOUT
    radii = {"left": L["eye_left_r"], "right": L["eye_right_r"]}
    out = {}
    for side, (ex, ey) in (("left", L["eye_left"]), ("right", L["eye_right"])):
        rx, ry = radii[side]
        # An eye is a sclera, an iris that does not fill it, a pupil and a catchlight, with
        # the lash as a separate heavy line above.  A dark disc behind a pink disc reads as
        # a goggle: that is what it was, and that is what this replaces.
        # The downcast eye is a shallow almond, not the inherited full-height disc.  Its
        # iris sits low and off-centre, so the upper lid covers its top by reading rather
        # than by an authored visibility cut; every layer remains its own owned shape.
        sclera_ry = ry * 0.43
        gaze_x, gaze_y = ex - rx * 0.20, ey + ry * 0.18
        out[f"A-eye-{side}"] = planar(f"A-eye-{side}", f"the {side} eye's shallow sclera", 0.36,
                                      ellipse(ex, ey, rx * 1.02, sclera_ry, -6),
                                      fill=EYE_WHITE, authored=((f"eye_{side}", (ex, ey)),))
        out[f"A-iris-{side}"] = planar(f"A-iris-{side}", f"the {side} iris, down and toward "
                                                          f"her own right under the lid",
                                       0.365,
                                       ellipse(gaze_x, gaze_y, rx * 0.52, sclera_ry * 0.82, -6),
                                       fill=IRIS)
        out[f"A-iris-deep-{side}"] = planar(f"A-iris-deep-{side}",
                                            f"the lower shade of the {side} iris", 0.37,
                                            ellipse(gaze_x, gaze_y + sclera_ry * 0.28,
                                                    rx * 0.38, sclera_ry * 0.36, -6),
                                            fill=IRIS_DEEP)
        out[f"A-pupil-{side}"] = planar(f"A-pupil-{side}", f"the {side} pupil", 0.372,
                                        ellipse(gaze_x, gaze_y, rx * 0.16, sclera_ry * 0.28, -6),
                                        fill=PUPIL_GREEN)
        out[f"A-glint-{side}"] = planar(f"A-glint-{side}", f"the {side} eye's catchlight", 0.375,
                                        ellipse(gaze_x - rx * 0.20, gaze_y - sclera_ry * 0.18,
                                                rx * 0.11, sclera_ry * 0.15, -6),
                                        fill=HIGHLIGHT)
    lash_marks = []
    for side, (ex, ey) in (("left", L["eye_left"]), ("right", L["eye_right"])):
        rx, ry = radii[side]
        # Three anchors describe each generated curve.  The heavy upper lash slopes down
        # toward the nose; the lighter crease echoes it above, making the shy lowered lid
        # legible at 1:1 without turning the whole eye into a black outline.
        lash = ((ex - rx, ey - 1.0), (ex, ey - ry * 0.48), (ex + rx, ey + 1.5))
        lid = ((ex - rx * 0.82, ey - ry * 0.42),
               (ex, ey - ry * 0.68), (ex + rx * 0.78, ey - ry * 0.34))
        lash_marks.append((f"A-lash-{side}", f"A-eye-{side}", "lash",
                           flat_mark(catmull(lash, steps=10, closed=False), 0.38), EYE_DARK))
        lash_marks.append((f"A-lid-{side}", f"A-eye-{side}", "fold_edge",
                           flat_mark(catmull(lid, steps=10, closed=False), 0.38), EYE_DARK))
    out["_lash_marks"] = lash_marks
    out["A-brow-left"] = planar("A-brow-left", "the far eyebrow, softly lowered", 0.335,
                                catmull(((610.0, 247.0), (634.0, 242.0), (658.0, 247.0)),
                                        steps=8, closed=False), fill=HAIR_INK)
    out["A-brow-right"] = planar("A-brow-right", "the near eyebrow, softly lowered", 0.335,
                                 catmull(((710.0, 245.0), (736.0, 240.0), (760.0, 247.0)),
                                         steps=8, closed=False), fill=HAIR_INK)

    out["A-mouth"] = planar("A-mouth", "the small downturned mouth", 0.35,
                            ellipse(690.0, 348.0, 5.5, 1.7, -8), fill="#c98a84")
    return out


# ---- hair: the mass behind, the two falls in front ---------------------------------

def _strip(route, width, depth, wave=None, samples=48):
    from ..parts import families as fam
    dense = fam._catmull_open(tuple((x, HEIGHT - y) for x, y in route), 14)
    count = len(dense) - 1

    def _offset(t):
        if wave is None:
            return 0.0
        amplitude, cycles, phase = wave
        # ramped in over the first quarter, so the attachment at the head is unbroken
        return amplitude * min(1.0, t / 0.28) * math.sin(2 * math.pi * cycles * t + phase)

    def spine(t):
        u = t * count
        i = min(count - 1, int(u))
        f = u - i
        a, b = dense[i], dense[i + 1]
        x = a[0] + (b[0] - a[0]) * f
        y = a[1] + (b[1] - a[1]) * f
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if length > 1e-12:
            off = _offset(t)
            x += (-dy / length) * off
            y += (dx / length) * off
        return (x, y)

    def half_width(t):
        # the wave moves the spine and shrinks the width by the same amount, so the
        # outer edge stays where the route put it and only the inner edge breaks
        return max(2.0, width(t) - abs(_offset(t)))

    def depth_at(t):
        return depth(t)

    return StripSurface(spine=spine, half_width=half_width, depth=depth_at)


def hair_parts():
    L = LAYOUT
    out, marks = {}, []
    back = _strip(L["hair_back_route"],
                  lambda t: 10.0 + 96.0 * math.sin(math.pi * min(1.0, max(0.0, t))) ** 0.5,
                  lambda t: 0.12)
    out["A-hair-back"] = SheetPart(
        name="A-hair-back", intent="the hair mass behind the head and above the shoulders",
        front_fill=HAIR_LIT, back_fill=HAIR_SHADE,
        grid=back.grid(samples=56, cols=3), anchors={},
        authored=tuple((f"hair_back_{i}", p) for i, p in enumerate(L["hair_back_route"])))
    # The falls are closed curtains, not strips.  A strip's two edges are one generator's
    # offset, so its inner edge is a straight line however the width is tuned; a fall of
    # hair needs its outer edge on the figure's silhouette and its inner edge clear of the
    # bodice.  That is two shapes, so it is two polygons.
    for name, poly, fill, shade in (
            ("A-hair-fall-left", L["fall_left_poly"], HAIR_LIT, HAIR_SHADE),
            ("A-hair-fall-right", L["fall_right_poly"], HAIR_SHADE, HAIR_DEEP)):
        outer = (poly[0], poly[1], poly[2], poly[3])
        inner = (poly[0], poly[7], poly[6], poly[5])
        out[name] = planar(name, "one long fall of hair hanging in front of the shoulder "
                                 f"({name.split('-')[-1]})", 0.50, catmull(poly),
                           rows=[("hair_edge", catmull(poly), "the fall's own edge")],
                           fill=fill, authored=(("fall_top", poly[0]), ("fall_outer", poly[3]),
                                                ("fall_hem", poly[4])))
        # The fall's rounded read: a shaded band along its inner edge, inset from that edge
        # by a fraction of the way to the outer edge, so the curtain is lit on the outside
        # and dark where it turns away.  Two tones on one mass, not a flat fill.
        turn = 0.42
        shade_poly = (inner[0], inner[1], inner[2], inner[3],
                      lerp2(inner[3], outer[3], turn), lerp2(inner[2], outer[2], turn),
                      lerp2(inner[1], outer[1], turn))
        out[name + "-shade"] = planar(
            name + "-shade", "the shaded turn of the same fall, along its inner edge", 0.501,
            catmull(shade_poly), fill=shade,
            authored=(("turn", 0.0),))
        # Strands run inside the curtain: each one is a fraction of the way from the
        # outer edge to the inner edge, at three heights, from the parting down.  Offsetting
        # the landmarks instead put them outside the curtain and across the hat brim.
        for k, share in enumerate((0.30, 0.55, 0.78)):
            marks.append((f"{name}-strand-{k}", name, "fold_edge",
                          flat_mark(catmull((lerp2(outer[0], inner[0], share),
                                             lerp2(outer[1], inner[1], share),
                                             lerp2(outer[2], inner[2], share),
                                             lerp2(outer[3], inner[3], share)),
                                            steps=10, closed=False), 0.505),
                          HAIR_INK))
    streamer = _strip(L["streamer"],
                      lambda t: 0.7 + 20.3 * (1.0 - t) ** 1.25, lambda t: 0.53)
    out["A-hair-streamer"] = SheetPart(
        name="A-hair-streamer",
        intent="the thin lock that sweeps out to her left and hooks at the end",
        front_fill=HAIR_LIT, back_fill=HAIR_SHADE,
        grid=streamer.grid(samples=44, cols=3), anchors={},
        authored=tuple((f"streamer_{i}", p) for i, p in enumerate(L["streamer"])))
    marks.append(("A-hair-streamer-edge-front", "A-hair-streamer", "hair_edge",
                  streamer.edge(0, 1, 1.0, 80), HAIR_INK))
    marks.append(("A-hair-streamer-edge-back", "A-hair-streamer", "hair_edge",
                  streamer.edge(0, 1, -1.0, 80), HAIR_INK))
    curl = _strip(L["curl_left"], lambda t: 17.0 - 9.0 * t, lambda t: 0.545)
    out["A-hair-curl-left"] = SheetPart(
        name="A-hair-curl-left",
        intent="the curl the fall on her right ends in, instead of a cut hem",
        front_fill=HAIR_LIT, back_fill=HAIR_SHADE,
        grid=curl.grid(samples=26, cols=3), anchors={},
        authored=tuple((f"curl_{i}", p) for i, p in enumerate(L["curl_left"])))
    marks.append(("A-hair-curl-left-edge-front", "A-hair-curl-left", "hair_edge",
                  curl.edge(0, 1, 1.0, 50), HAIR_INK))
    marks.append(("A-hair-curl-left-edge-back", "A-hair-curl-left", "hair_edge",
                  curl.edge(0, 1, -1.0, 50), HAIR_INK))
    for name, route, w in (("A-hair-lock-left", L["lock_left"], 13.0),
                           ("A-hair-lock-right", L["lock_right"], 14.0)):
        surface = _strip(route, lambda t, w=w: w * (1.15 - 0.9 * t), lambda t: 0.52,
                         wave=(4.0, 1.1, 0.9))
        out[name] = SheetPart(name=name, intent="one thin lock of hair in front of the shoulder",
                              front_fill=HAIR_LIT, back_fill=HAIR_DEEP,
                              grid=surface.grid(samples=28, cols=3), anchors={},
                              authored=tuple((f"{name}_{i}", p) for i, p in enumerate(route)))
        marks.append((f"{name}-edge-front", name, "hair_edge", surface.edge(0, 1, 1.0, 60),
                      HAIR_INK))
        marks.append((f"{name}-edge-back", name, "hair_edge", surface.edge(0, 1, -1.0, 60),
                      HAIR_INK))
    marks.append(("A-hair-back-edge-front", "A-hair-back", "hair_edge",
                  back.edge(0, 1, 1.0, 100), HAIR_INK))
    marks.append(("A-hair-back-edge-back", "A-hair-back", "hair_edge",
                  back.edge(0, 1, -1.0, 100), HAIR_INK))
    return out, marks


# ---- the seated lower mass ---------------------------------------------------------

def waist_parts():
    """The waist the blouse has and this figure did not.

    The reference's torso is not a column: the blouse gathers into a band at the waist
    (sampled at (700,690) it is the same cream as the bodice, so the band is read from its
    edges, not its tone) and the skirt flares below it.  The band is a new part laid over
    the inherited bodice, with the gather's own strokes on it, because the inherited bodice
    is a shared part and is not edited.
    """
    L = LAYOUT
    sides = {}
    for side, poly in (("left", L["bodice_left"]), ("right", L["bodice_right"])):
        name = f"A-bodice-side-{side}"
        sides[name] = planar(name, f"the {side} tonal continuation of the same blouse", 0.30,
                             catmull(poly), rows=[], fill=CREAM,
                             authored=(("shoulder", poly[0]), ("waist", poly[4])))
    band = planar("A-waist-band", "the gathered waist tone, without a boxed perimeter", 0.32,
                  catmull(L["waist_band"]), rows=[], fill=CREAM_SHADE,
                  authored=(("band_left", L["waist_band"][0]),
                            ("band_right", L["waist_band"][2])))
    gathers = []
    for i in range(6):
        x = 606.0 + 33.0 * i
        gathers.append((f"A-waist-gather-{i}", "A-waist-band", "fold_edge",
                        flat_mark((full(x, 664.0 + 2.0 * (i % 2)),
                                   full(x + 3.0, 706.0 - 2.0 * (i % 3))), 0.325), FOLD_INK))
    sides["A-waist-band"] = band
    return sides, gathers


def lap_outline(anchors):
    """Generate a seated skirt from waist-left/right, near knee and far knee.

    The hem exits left and bottom by relation to the two knees; the intermediate valley
    keeps the cloth lateral rather than closing it into a bell.
    """
    waist_left, waist_right, near_knee, far_knee = anchors
    valley = lerp2(near_knee, far_knee, 0.46)
    valley = (valley[0], valley[1] + 58.0)
    left_exit = (-32.0, min(1010.0, far_knee[1] + 104.0))
    bottom_exit = (near_knee[0] - 116.0, 1050.0)
    return catmull((waist_left, waist_right, near_knee, bottom_exit,
                    valley, far_knee, left_exit))


def lower_parts():
    """The seated lower mass: one mint skirt, a deep-teal fold behind it, cream and mint
    wedges crossing it, and the lining bands inside the teal, with fold lines generated
    from the waist gather rather than typed as parallel strokes.

    The first version of this was five axis-aligned panels with five parallel strokes on
    top, which read as a cushion: a fold is a wedge whose two edges are not parallel and
    whose boundary curves, so each piece here is a catmull with no two edges parallel and
    the strokes fan from one point at the waist.
    """
    L = LAYOUT
    skirt_shape = lap_outline(L["skirt"])
    skirt = planar("A-skirt-front", "the pale skirt crossing laterally over two seated knees", 0.262,
                   skirt_shape,
                   rows=[("silhouette", skirt_shape, "the skirt's outer edge and off-frame hem")],
                   fill=MINT, authored=(("skirt_near_knee", L["skirt"][2]),
                                        ("skirt_far_knee", L["skirt"][3])))
    teal = planar("A-skirt-teal", "the connected deep-teal cloth beneath the skirt", 0.22,
                  catmull(L["skirt_teal"]), rows=[], fill=DEEP_TEAL,
                  authored=(("teal_top", L["skirt_teal"][0]),
                            ("teal_hem", L["skirt_teal"][2])))
    cream_shape = catmull(L["fold_cream"])
    cream = planar("A-fold-cream", "a cream tonal plane in the same skirt cloth", 0.274,
                   cream_shape, rows=[], fill=CREAM,
                   authored=(("cream_top", L["fold_cream"][0]),
                             ("cream_hem", L["fold_cream"][3])))
    mint_shape = catmull(L["fold_mint"])
    mint = planar("A-fold-mint", "a mint shaded turn in the same skirt cloth", 0.272,
                  mint_shape, rows=[], fill=MINT_SHADE)
    shadow_shape = catmull(L["fold_shadow"])
    shadow = planar("A-fold-shadow", "the tone under the waist where the skirt turns", 0.268,
                    shadow_shape, rows=[], fill=MINT_SHADE)
    under = planar("A-underskirt", "the deep-teal under-layer continuing under the hem", 0.24,
                   catmull(L["underskirt"]), rows=[], fill=DEEP_TEAL,
                   authored=(("under_left", L["underskirt"][0]),
                             ("under_right", L["underskirt"][2])))
    pink_shape = catmull(L["lining_pink"])
    pink = planar("A-lining-pink", "the pink lining ribbon crossing the teal", 0.235,
                  pink_shape, rows=[], fill=LINING_PINK)
    orange_shape = catmull(L["lining_orange"])
    orange = planar("A-lining-orange", "the orange lining ribbon crossing the teal", 0.236,
                    orange_shape, rows=[], fill=LINING_ORANGE)
    return {"A-skirt-front": skirt, "A-skirt-teal": teal, "A-fold-cream": cream,
            "A-fold-mint": mint, "A-fold-shadow": shadow, "A-underskirt": under,
            "A-lining-pink": pink, "A-lining-orange": orange}


def hem_trim():
    """The heavy navy band along the skirt's hem.

    The reference's skirt reads as cloth because its hem carries a thick dark border, not
    because of its tone: sampling the reference at its hem gives (44,58,85) across a band
    about ten pixels wide.  It is one stroke of the `trim` class along the skirt's own hem,
    so the band follows whatever shape the skirt is cut to.
    """
    L = LAYOUT
    _waist_left, _waist_right, near_knee, far_knee = L["skirt"]
    valley = lerp2(near_knee, far_knee, 0.46)
    valley = (valley[0], valley[1] + 58.0)
    hem = ((near_knee[0] - 116.0, 1050.0), valley, far_knee,
           (-32.0, min(1010.0, far_knee[1] + 104.0)))
    return ("A-skirt-hem-trim", "A-skirt-front", "hem",
            flat_mark(catmull(hem, steps=14, closed=False), 0.272), CUFF_NAVY)


def fold_marks():
    """Fold lines: long curves following the drape, each one offset from the last.

    The first version radiated them from one point at the waist and they read as a fan.
    Cloth folds run *along* the drape: here three curves leave the waist at intervals and
    run down-right across the skirt, converging slightly, each with its own sag.
    """
    L = LAYOUT
    top = L["skirt"][0]
    marks = []
    for i in range(2):
        start = (top[0] + 72.0 + 104.0 * i, top[1] + 42.0 + 10.0 * i)
        end = (448.0 + 174.0 * i, 1018.0)
        a = lerp2(start, end, 0.38)
        b = lerp2(start, end, 0.72)
        bend = 38.0 - 13.0 * i
        marks.append((f"A-skirt-foldline-{i}", "A-skirt-front", "fold_edge",
                      flat_mark(catmull((start, (a[0] + bend, a[1]),
                                                (b[0] + bend * 0.35, b[1]), end),
                                        steps=14, closed=False), 0.285), FOLD_INK))
    return marks


def arm_parts():
    L = LAYOUT
    surface = _strip(L["arm_route"], lambda t: 31.0 - 13.0 * t ** 1.6, lambda t: 0.29)
    arm = SheetPart(name="A-arm", intent="her left arm hanging out of the viewer-right cuff, "
                                          "tapering into a readable wrist",
                    front_fill=SKIN, back_fill=SKIN_SHADE,
                    grid=surface.grid(samples=30, cols=3), anchors={},
                    authored=tuple((f"arm_{i}", p) for i, p in enumerate(L["arm_route"])))
    far_surface = _strip(L["far_arm_route"], lambda t: 24.0 - 9.0 * t,
                         lambda t: 0.49 - 0.24 * t)
    far_arm = SheetPart(name="A-far-arm", intent="her right arm attached to the viewer-left "
                                                   "cuff and passing behind the skirt",
                        front_fill=SKIN, back_fill=SKIN_SHADE,
                        grid=far_surface.grid(samples=26, cols=3), anchors={},
                        authored=tuple((f"far_arm_{i}", p)
                                       for i, p in enumerate(L["far_arm_route"])))
    palm_shape = catmull(L["palm"])
    palm = planar("A-hand", "the visible hand's palm and heel at the wrist", 0.295,
                  palm_shape, rows=[("contact", palm_shape, "the palm's own edge")],
                  fill=SKIN, authored=(("wrist", L["palm"][0]),
                                       ("finger_root", L["palm"][3])))
    thumb_shape = catmull(L["thumb"])
    thumb = planar("A-thumb", "the thumb separated from the palm's near side", 0.307,
                   thumb_shape, rows=[("free_edge", thumb_shape, "the thumb's free edge")],
                   fill=SKIN, authored=(("thumb_tip", L["thumb"][1]),))
    parts = {"A-arm": arm, "A-far-arm": far_arm, "A-hand": palm, "A-thumb": thumb}
    ox, oy = L["finger_origin"]
    sx, sy = L["finger_step"]
    frx, fry = L["finger_r"]
    for i in range(4):
        # Four overlapping capsules share the palm root but retain four outlined tips.  Their
        # centres and lengths derive from one origin/step/radius relation, not a station table.
        name = f"A-finger-{i + 1}"
        shape = ellipse(ox + sx * i, oy + sy * i, frx - 0.45 * i,
                        fry - 1.8 * i, -7.0 + 2.0 * i)
        parts[name] = planar(name, f"visible finger {i + 1}, rooted in the palm", 0.304 + i * 0.0005,
                             shape, rows=[("free_edge", shape, "the finger's separable edge")],
                             fill=SKIN, authored=(("finger_index", float(i)),))
    marks = [("A-arm-edge-front", "A-arm", "contact", surface.edge(0, 1, 1.0, 50), FOLD_INK),
             ("A-arm-edge-back", "A-arm", "contact", surface.edge(0, 1, -1.0, 50), FOLD_INK),
             ("A-far-arm-edge-front", "A-far-arm", "contact",
              far_surface.edge(0, 1, 1.0, 50), FOLD_INK),
             ("A-far-arm-edge-back", "A-far-arm", "contact",
              far_surface.edge(0, 1, -1.0, 50), FOLD_INK)]
    return parts, marks


# ---- the assembly ------------------------------------------------------------------

def build():
    parts = {}
    waist, waist_marks = waist_parts()
    parts.update(waist)
    parts.update(lower_parts())
    inherited_parts, inherited_marks, meta = inherited()
    # The reference's puff sleeves are cream and the blue at the shoulders is hair.  The
    # inherited sleeve geometry is untouched; only its fill is re-read here, so
    # A-cloth-v8 keeps its own bytes and this figure carries the corrected reading.
    for name_ in ("A-left-sleeve", "A-right-sleeve"):
        if name_ in inherited_parts:
            inherited_parts[name_] = dataclasses.replace(inherited_parts[name_], fill=CREAM)
    for name_ in ("A-left-cuff", "A-right-cuff"):
        if name_ in inherited_parts:
            inherited_parts[name_] = dataclasses.replace(inherited_parts[name_], fill=CUFF_NAVY)
    # Two inherited parts are dropped here, and the reason is geometric, not aesthetic:
    # `A-head-face` ends its jaw at image y 442 (the crop's own chin), 58 px below where
    # the full figure's chin sits, so it drew a second jaw line across the neck; and
    # `A-hair-sheet` crosses in front of what is chest in this frame, which at crop scale
    # was "in front of the face".  Both are replaced by parts authored for this frame.
    torso = ("A-bodice-upper", "A-derived-waist-band", "A-bodice-continuation",
             "A-left-sleeve", "A-left-cuff", "A-right-sleeve", "A-right-cuff", "A-bow-ribbon")
    _pcx, _py = TORSO_ABOUT_XY[0], HEIGHT - TORSO_ABOUT_XY[1]
    for part_name in torso:
        if part_name not in inherited_parts:
            continue
        part_ = inherited_parts[part_name]
        inherited_parts[part_name] = (scale_sheet(part_, TORSO_SCALE, _pcx, _py,
                                                  TORSO_ABOUT_XY[1])
                                      if isinstance(part_, SheetPart)
                                      else scale_planar(part_, TORSO_SCALE, _pcx, _py))
    # The bow is a principal shape in the reference and it alone may grow: scaling the whole
    # torso group was rejected because it moved the bow against the collar, so the scale is
    # applied to the bow about its own centre and to nothing else.
    if "A-bow-ribbon" in inherited_parts:
        bow_part = inherited_parts["A-bow-ribbon"]
        grid = bow_part.grid
        k = BOW_SCALE
        cx = sum(p[0] for row in grid for p in row) / sum(len(row) for row in grid)
        cy = sum(p[1] for row in grid for p in row) / sum(len(row) for row in grid)
        inherited_parts["A-bow-ribbon"] = dataclasses.replace(
            bow_part, grid=tuple(tuple((cx + (p[0] - cx) * k, cy + (p[1] - cy) * k, p[2])
                                       for p in row) for row in grid))
    for dropped in ("A-head-face", "A-hair-sheet", "A-collar-left", "A-collar-right"):
        inherited_parts.pop(dropped, None)
    # These are tonal subdivisions of one blouse, not separate objects.  Their inherited
    # perimeters made a polygon mesh across the torso; keep the fills and omit the seams.
    same_garment = {"A-bodice-upper", "A-bodice-continuation", "A-derived-waist-band"}
    for part_name in same_garment:
        part_ = inherited_parts.get(part_name)
        if isinstance(part_, PlanarPart):
            inherited_parts[part_name] = dataclasses.replace(part_, edges=())
    inherited_marks = [m for m in inherited_marks
                       if m[1] not in ("A-head-face", "A-hair-sheet",
                                       "A-collar-left", "A-collar-right")
                       and m[1] not in same_garment]
    parts.update(inherited_parts)
    parts.update(hat_parts())
    parts.update(shadow_parts())
    parts.update(head_parts())
    eyes = eye_parts()
    lash_marks = eyes.pop("_lash_marks")
    parts.update(eyes)
    hair, hair_marks = hair_parts()
    parts.update(hair)
    arm, arm_marks = arm_parts()
    parts.update(arm)
    marks = (list(inherited_marks) + list(hair_marks) + list(arm_marks)
             + list(fold_marks()) + list(lash_marks) + list(waist_marks)
             + [nose_mark(), hem_trim()])
    return dict(parts=parts, sheet_marks=tuple(marks), field=tuple(field()), meta=meta)


OBJECTS = {
    "hat-brim": (["A-hat-brim-under", "A-hat-brim-top"],
                 "the wide brim: teal underside near the camera, navy top face beyond"),
    "hat-crown": (["A-hat-crown"], "the crown standing on the brim"),
    "hat-shadow": (["A-shadow-fringe"],
                   "the brim's shadow on the fringe, along the junction between them"),
    "hat-puff-top": (["A-hat-puff-top"], "the pink cluster at the crown's back"),
    "hat-puff-right": (["A-hat-puff-right"], "the pink cluster on the brim's right"),
    "hair-back": (["A-hair-back"], "the hair mass behind the head"),
    "hair-bangs": (["A-hair-bangs"], "the fringe over the forehead"),
    "hair-falls": (["A-hair-fall-left", "A-hair-fall-right",
                    "A-hair-fall-left-shade", "A-hair-fall-right-shade"],
                   "the outer falls: closed curtains, each lit on the outside and shaded "
                   "along its inner turn"),
    "hair-locks": (["A-hair-lock-left", "A-hair-lock-right"],
                   "the thin locks in front of each shoulder"),
    "hair-streamer": (["A-hair-streamer"],
                      "the thin lock sweeping out to her left, hooking at the end"),
    "hair-curl": (["A-hair-curl-left"], "the curl the shorter fall ends in"),
    "face": (["A-face"], "the face field"),
    "neck": (["A-neck", "A-neck-hollow", "A-visible-neck-skin"],
             "the neck between chin and collar, and the hollow of the collar's opening"),
    "eye-left": (["A-eye-left", "A-iris-left", "A-iris-deep-left", "A-pupil-left",
                  "A-glint-left"],
                 "the left eye: sclera, iris, its shade, pupil, catchlight, lash and lid"),
    "eye-right": (["A-eye-right", "A-iris-right", "A-iris-deep-right", "A-pupil-right",
                   "A-glint-right"],
                  "the right eye: sclera, iris, its shade, pupil, catchlight, lash and lid"),
    "brows": (["A-brow-left", "A-brow-right"], "the eyebrows"),
    "mouth": (["A-mouth"], "the mouth"),
    "collar": (["A-collar-left", "A-collar-right"],
               "the sailor collar: two leaves cut for this frame's neck opening"),
    "bodice": (["A-bodice-upper", "A-derived-waist-band", "A-bodice-continuation"],
               "the cream blouse, inherited"),
    "waist": (["A-waist-band"], "the gathered band at the waist, laid over the blouse"),
    "bodice-sides": (["A-bodice-side-left", "A-bodice-side-right"],
                     "the blouse's own sides, from shoulder to waist"),
    "left-sleeve": (["A-left-sleeve", "A-left-cuff"], "one puff sleeve and its navy cuff"),
    "right-sleeve": (["A-right-sleeve", "A-right-cuff"], "the other puff sleeve and cuff"),
    "chest-bow": (["A-bow-ribbon"], "the magenta bow on the collar's V, inherited"),
    "arm-left": (["A-arm"], "her left arm out of the viewer-right cuff"),
    "arm-right": (["A-far-arm"], "her right arm from the viewer-left cuff behind the skirt"),
    "hand-left": (["A-hand", "A-thumb", "A-finger-1", "A-finger-2", "A-finger-3",
                   "A-finger-4"],
                  "her visible left hand: palm, thumb and four separately outlined fingers"),
    "skirt-front": (["A-skirt-front"], "the cream skirt over her knees"),
    "skirt-folds": (["A-fold-cream", "A-fold-mint", "A-fold-shadow"],
                    "the cream and mint wedges crossing the skirt, and its shaded turn"),
    "skirt-teal": (["A-skirt-teal"], "the deep-teal fold behind the skirt at her left"),
    "underskirt": (["A-underskirt"], "the deep-teal under-layer"),
    "lining": (["A-lining-pink", "A-lining-orange"], "the lining bands between the folds"),
}

FIELD = ("the frame's flat field: the teal ground and the near green bank, painted behind "
         "every part because a full-frame quad put through the depth engine decides nothing")


def declared_parts() -> set:
    return {part for parts, _why in OBJECTS.values() for part in parts}
