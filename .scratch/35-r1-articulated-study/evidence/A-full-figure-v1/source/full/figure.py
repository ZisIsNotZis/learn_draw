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
    "silhouette": (CONTOUR_INK, 1.7),
    "free_edge": (CONTOUR_INK, 1.7),
    "contact": (FOLD_INK, 1.3),
    "fold_edge": (FOLD_INK, 1.0),
    "trim": (CUFF_NAVY, 3.4),
    "hair_edge": (HAIR_INK, 1.6),
    "hat_edge": (HAT_UNDER, 1.4),
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
    for i in range(2 * teeth + 1):
        f = i / (2 * teeth)
        x = right[0] + (left[0] - right[0]) * f
        y = shallow if i % 2 == 0 else deepest      # a notch, then a tooth tip
        # the two ends of the fringe are shorter: the hair leaves the temples higher up
        taper = 1.0 - (abs(f - 0.5) * 2.0) ** 2 * 0.30
        lower.append((x, shallow + (y - shallow) * taper))
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
    brim_centre=(686.0, 150.0), brim_rx=286.0, brim_ry=168.0, brim_rot=20.0,
    crown_centre=(806.0, 148.0), crown_rx=152.0, crown_ry=134.0,
    puff_top=(658.0, 52.0), puff_top_r=31.0,
    puff_right=(906.0, 190.0), puff_right_r=41.0,
    # the face, and the fringe that leaves only the lower half of it showing
    chin=(684.0, 384.0),
    face_ring=((684.0, 390.0), (622.0, 334.0), (600.0, 262.0), (614.0, 196.0),
               (692.0, 172.0), (766.0, 208.0), (760.0, 306.0), (718.0, 362.0)),
    eye_left=(638.0, 264.0), eye_right=(732.0, 268.0), eye_r=(27.0, 30.0),
    bangs_anchors=((552.0, 212.0), (662.0, 116.0), (812.0, 220.0), (688.0, 286.0)),
    bang_teeth=4, bang_depth=(230.0, 252.0),
    # the neck
    neck_q=((660.0, 372.0), (710.0, 372.0), (714.0, 428.0), (658.0, 428.0)),
    neck_hollow=((624.0, 398.0), (748.0, 398.0), (756.0, 486.0), (616.0, 486.0)),
    # the sailor collar, cut for this frame's neck opening (the inherited pair was cut for a
    # chin 58 px lower and reads as a sliver here)
    collar_left=((692.0, 386.0), (628.0, 406.0), (566.0, 456.0), (556.0, 528.0),
                 (614.0, 506.0), (664.0, 470.0), (686.0, 440.0)),
    collar_right=((700.0, 386.0), (766.0, 404.0), (822.0, 452.0), (826.0, 526.0),
                  (766.0, 502.0), (718.0, 466.0), (706.0, 438.0)),
    # hair: a mass behind the head, and two falls that hang in front of the shoulders
    hair_back_route=((500.0, 1052.0), (486.0, 640.0), (556.0, 320.0), (686.0, 232.0),
                     (826.0, 340.0), (902.0, 640.0), (930.0, 1052.0)),
    fall_left_poly=((598.0, 194.0), (546.0, 300.0), (494.0, 472.0), (452.0, 706.0),
                    (488.0, 1044.0), (572.0, 1032.0), (566.0, 762.0), (606.0, 400.0)),
    fall_right_poly=((762.0, 192.0), (824.0, 296.0), (890.0, 470.0), (952.0, 704.0),
                     (968.0, 1044.0), (910.0, 1032.0), (876.0, 700.0), (806.0, 400.0)),
    lock_left=((574.0, 250.0), (528.0, 486.0), (516.0, 736.0)),
    lock_right=((760.0, 258.0), (786.0, 492.0), (800.0, 740.0)),
    fall_wave=(9.0, 1.6, 0.4),
    # the seated lower mass: skirt over the knees, under-layer, and the fold bands
    # The reference's lower mass, read off ref-lower.png: a large deep-teal field across
    # the centre-bottom, pale mint and cream cloth over its upper right, and the pink and
    # orange lining ribbons crossing the teal diagonally.
    skirt=((560.0, 664.0), (818.0, 676.0), (884.0, 872.0), (700.0, 956.0),
           (512.0, 884.0), (494.0, 748.0)),
    skirt_teal=((252.0, 792.0), (700.0, 862.0), (762.0, 1024.0), (296.0, 1024.0)),
    fold_cream=((430.0, 792.0), (612.0, 812.0), (712.0, 1004.0), (536.0, 1024.0),
                (416.0, 890.0)),
    fold_mint=((470.0, 726.0), (640.0, 742.0), (700.0, 900.0), (540.0, 918.0)),
    fold_shadow=((600.0, 668.0), (776.0, 690.0), (800.0, 830.0), (652.0, 840.0)),
    underskirt=((700.0, 900.0), (884.0, 872.0), (806.0, 1020.0), (700.0, 1010.0)),
    lining_pink=((300.0, 846.0), (470.0, 872.0), (548.0, 1008.0), (352.0, 1012.0)),
    lining_orange=((508.0, 948.0), (640.0, 930.0), (690.0, 1024.0), (556.0, 1024.0)),
    fold_lines=((0.14, 0.04), (0.32, 0.08), (0.50, 0.12), (0.68, 0.16)),
    # her right arm, out of the cuff and down past the skirt
    arm_route=((860.0, 556.0), (876.0, 700.0), (868.0, 792.0)),
    hand=(864.0, 832.0),
)


def field():
    """The frame's flat field: ground and bank, painted behind every part.

    These are not parts: they are the picture's field, drawn as plain paths before the
    depth engine runs.  A full-frame quad put through the triangle engine would be tested
    against every face in the scene to decide nothing.
    """
    return [
        ("A-field-ground", (full(0, 336), full(360, 320), full(780, 338), full(1024, 318),
                            full(1024, 1024), full(0, 1024)), BACKGROUND_TEAL),
        ("A-field-bank", (full(0, 548), full(196, 646), full(238, 868), full(0, 1024)),
         BACKGROUND_GREEN),
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
    top = planar("A-hat-brim-top", "the brim's navy top face on the far side of its axis", 0.21,
                 dome(bx, by, L["brim_rx"], L["brim_ry"], L["brim_rot"]),
                 rows=[],
                 fill=HAT_NAVY, authored=(("brim_top_axis", L["brim_centre"]),))
    cx, cy = L["crown_centre"]
    crown = planar("A-hat-crown", "the crown dome standing on the brim's top face", 0.22,
                   dome(cx, cy, L["crown_rx"], L["crown_ry"], L["brim_rot"]),
                   rows=[("hat_edge", dome(cx, cy, L["crown_rx"], L["crown_ry"], L["brim_rot"]),
                          "the crown meeting the brim")],
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
    ring = L["face_ring"]
    face = planar("A-face", "the face field: chin, cheeks, temples, under the fringe", 0.30,
                  catmull(ring),
                  rows=[("silhouette", catmull(ring), "the face's own boundary")],
                  fill=SKIN, authored=tuple((f"face_{i}", p) for i, p in enumerate(ring)))
    neck_q = L["neck_q"]
    neck = planar("A-neck", "the neck between the chin and the collar's opening", 0.315,
                  catmull(neck_q), fill=SKIN_SHADE,
                  rows=[("contact", (full(*neck_q[0]), full(*neck_q[1])), "the jaw's underside")],
                  authored=tuple((f"neck_{i}", p) for i, p in enumerate(neck_q)))
    anchors = L["bangs_anchors"]
    edge = fringe(anchors, teeth=L["bang_teeth"], depth=L["bang_depth"])
    # The collar's opening is wider than the neck, and the inherited collar was cut for a
    # chin 58 px lower, so background showed through the two gaps beside the neck (sampled:
    # #56adb8 at (640,395) and (720,415)).  The hollow fills the opening behind the neck.
    hollow = planar("A-neck-hollow", "the shadowed hollow of the collar's opening, behind the "
                                     "neck", 0.29, catmull(L["neck_hollow"]), fill=SKIN_SHADE,
                    authored=(("hollow_top", L["neck_hollow"][0]),))
    collar_out = {}
    for side, poly in (("left", L["collar_left"]), ("right", L["collar_right"])):
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


def eye_parts():
    L = LAYOUT
    rx, ry = L["eye_r"]
    out = {}
    for side, (ex, ey) in (("left", L["eye_left"]), ("right", L["eye_right"])):
        out[f"A-eye-{side}"] = planar(f"A-eye-{side}", f"the {side} eye's lid and lash line",
                                      0.36, ellipse(ex, ey, rx, ry, -6), fill=EYE_DARK,
                                      authored=((f"eye_{side}", (ex, ey)),))
        out[f"A-iris-{side}"] = planar(f"A-iris-{side}", f"the {side} iris", 0.365,
                                       ellipse(ex + 1, ey + 3, rx * 0.84, ry * 0.88, -6),
                                       fill=IRIS)
        out[f"A-iris-deep-{side}"] = planar(f"A-iris-deep-{side}",
                                            f"the shade under the {side} iris", 0.37,
                                            ellipse(ex + 1, ey + 13, rx * 0.5, ry * 0.33, -6),
                                            fill=IRIS_DEEP)
        out[f"A-glint-{side}"] = planar(f"A-glint-{side}", f"the {side} eye's catchlight", 0.375,
                                        ellipse(ex - 8, ey - 9, rx * 0.2, ry * 0.17, -6),
                                        fill=HIGHLIGHT)
    out["A-brow-left"] = planar("A-brow-left", "the left eyebrow", 0.35,
                                catmull(((614.0, 226.0), (636.0, 218.0), (658.0, 224.0)),
                                        steps=8, closed=False), fill=HAIR_SHADE)
    out["A-brow-right"] = planar("A-brow-right", "the right eyebrow", 0.35,
                                 catmull(((712.0, 226.0), (736.0, 220.0), (758.0, 228.0)),
                                         steps=8, closed=False), fill=HAIR_SHADE)
    out["A-mouth"] = planar("A-mouth", "the mouth", 0.35,
                            ellipse(690.0, 352.0, 8.0, 3.5, 0), fill="#c98a84")
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
    skirt = planar("A-skirt-front", "the mint skirt over her knees", 0.262,
                   catmull(L["skirt"]),
                   rows=[("silhouette", catmull(L["skirt"]), "the skirt's own edge")],
                   fill=MINT, authored=(("skirt_seat", L["skirt"][2]),
                                        ("skirt_hem", L["skirt"][4])))
    teal = planar("A-skirt-teal", "the deep-teal cloth below and left of the skirt", 0.22,
                  catmull(L["skirt_teal"]),
                  rows=[("free_edge", catmull(L["skirt_teal"]), "the fold's own edge")],
                  fill=DEEP_TEAL, authored=(("teal_top", L["skirt_teal"][0]),
                                            ("teal_hem", L["skirt_teal"][2])))
    cream = planar("A-fold-cream", "the cream wedge crossing the skirt from the waist", 0.274,
                   catmull(L["fold_cream"]), fill=CREAM,
                   authored=(("cream_top", L["fold_cream"][0]),
                             ("cream_hem", L["fold_cream"][3])))
    mint = planar("A-fold-mint", "the mint wedge below it, its own edge unparallel", 0.272,
                  catmull(L["fold_mint"]), fill=MINT_SHADE)
    shadow = planar("A-fold-shadow", "the shade where the skirt turns under at the waist", 0.268,
                    catmull(L["fold_shadow"]), fill=MINT_SHADE)
    under = planar("A-underskirt", "the deep-teal under-layer at the skirt's right hem", 0.24,
                   catmull(L["underskirt"]),
                   rows=[("silhouette", catmull(L["underskirt"]), "the under-layer's edge")],
                   fill=DEEP_TEAL, authored=(("under_left", L["underskirt"][0]),
                                             ("under_right", L["underskirt"][2])))
    pink = planar("A-lining-pink", "the pink lining ribbon crossing the teal", 0.235,
                  catmull(L["lining_pink"]), fill=LINING_PINK)
    orange = planar("A-lining-orange", "the orange lining band below the pink", 0.236,
                    catmull(L["lining_orange"]), fill=LINING_ORANGE)
    return {"A-skirt-front": skirt, "A-skirt-teal": teal, "A-fold-cream": cream,
            "A-fold-mint": mint, "A-fold-shadow": shadow, "A-underskirt": under,
            "A-lining-pink": pink, "A-lining-orange": orange}


def fold_marks():
    """Fold lines fanning from the waist gather: one origin, a generated spread, curves."""
    L = LAYOUT
    origin = (L["skirt"][0][0] + 60.0, L["skirt"][0][1] + 26.0)
    marks = []
    for i, (spread, sag) in enumerate(L["fold_lines"]):
        start = (origin[0] + 18.0 * i, origin[1] - 6.0 * i)
        end = (470.0 + 300.0 * spread, 1018.0 - 40.0 * spread)
        mid_a = lerp2(start, end, 0.35)
        mid_b = lerp2(start, end, 0.70)
        marks.append((f"A-skirt-foldline-{i}", "A-skirt-front", "fold_edge",
                      flat_mark(catmull((start, (mid_a[0] + 26.0, mid_a[1] + sag),
                                         (mid_b[0] - 18.0, mid_b[1] + sag), end),
                                        steps=12, closed=False), 0.285),
                      FOLD_INK))
    return marks


def arm_parts():
    L = LAYOUT
    surface = _strip(L["arm_route"], lambda t: 31.0 - 9.0 * t, lambda t: 0.29)
    arm = SheetPart(name="A-arm", intent="her right arm hanging out of the cuff",
                    front_fill=SKIN, back_fill=SKIN_SHADE,
                    grid=surface.grid(samples=30, cols=3), anchors={},
                    authored=tuple((f"arm_{i}", p) for i, p in enumerate(L["arm_route"])))
    hx, hy = L["hand"]
    hand = planar("A-hand", "her right hand: a soft mitten mass at the wrist", 0.295,
                  catmull(((hx - 24.0, hy - 22.0), (hx + 6.0, hy - 34.0), (hx + 28.0, hy - 8.0),
                           (hx + 24.0, hy + 26.0), (hx - 8.0, hy + 32.0), (hx - 26.0, hy + 6.0))),
                  rows=[("contact",
                         catmull(((hx - 24.0, hy - 22.0), (hx + 6.0, hy - 34.0),
                                  (hx + 28.0, hy - 8.0), (hx + 24.0, hy + 26.0),
                                  (hx - 8.0, hy + 32.0), (hx - 26.0, hy + 6.0))),
                         "the hand's own edge")], fill=SKIN)
    marks = [("A-arm-edge-front", "A-arm", "contact", surface.edge(0, 1, 1.0, 50), FOLD_INK),
             ("A-arm-edge-back", "A-arm", "contact", surface.edge(0, 1, -1.0, 50), FOLD_INK)]
    return {"A-arm": arm, "A-hand": hand}, marks


# ---- the assembly ------------------------------------------------------------------

def build():
    parts = {}
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
    for dropped in ("A-head-face", "A-hair-sheet", "A-collar-left", "A-collar-right"):
        inherited_parts.pop(dropped, None)
    inherited_marks = [m for m in inherited_marks
                       if m[1] not in ("A-head-face", "A-hair-sheet",
                                       "A-collar-left", "A-collar-right")]
    parts.update(inherited_parts)
    parts.update(hat_parts())
    parts.update(shadow_parts())
    parts.update(head_parts())
    parts.update(eye_parts())
    hair, hair_marks = hair_parts()
    parts.update(hair)
    arm, arm_marks = arm_parts()
    parts.update(arm)
    marks = (list(inherited_marks) + list(hair_marks) + list(arm_marks)
             + list(fold_marks()))
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
    "face": (["A-face"], "the face field"),
    "neck": (["A-neck", "A-neck-hollow", "A-visible-neck-skin"],
             "the neck between chin and collar, and the hollow of the collar's opening"),
    "eye-left": (["A-eye-left", "A-iris-left", "A-iris-deep-left", "A-glint-left"],
                 "the left eye: lid, iris, its shade, catchlight"),
    "eye-right": (["A-eye-right", "A-iris-right", "A-iris-deep-right", "A-glint-right"],
                  "the right eye: lid, iris, its shade, catchlight"),
    "brows": (["A-brow-left", "A-brow-right"], "the eyebrows"),
    "mouth": (["A-mouth"], "the mouth"),
    "collar": (["A-collar-left", "A-collar-right"],
               "the sailor collar: two leaves cut for this frame's neck opening"),
    "bodice": (["A-bodice-upper", "A-derived-waist-band", "A-bodice-continuation"],
               "the cream blouse and its waist, inherited"),
    "left-sleeve": (["A-left-sleeve", "A-left-cuff"], "one puff sleeve and its navy cuff"),
    "right-sleeve": (["A-right-sleeve", "A-right-cuff"], "the other puff sleeve and cuff"),
    "chest-bow": (["A-bow-ribbon"], "the magenta bow on the collar's V, inherited"),
    "arm-right": (["A-arm"], "her right arm out of the cuff"),
    "hand-right": (["A-hand"], "her right hand"),
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
