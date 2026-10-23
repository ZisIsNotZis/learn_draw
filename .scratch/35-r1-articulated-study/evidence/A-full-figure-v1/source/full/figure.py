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
BACKGROUND_SKY = "#cfdade"
BACKGROUND_TEAL = "#78a49b"
BACKGROUND_GREEN = "#8fc0a0"
HAT_NAVY = "#33405c"
HAT_CROWN = "#3a4a68"
HAT_UNDER = "#262f45"
BRIM_TEAL = "#8cb8bd"
BRIM_TEAL_DARK = "#5c93a0"
HAIR_LIT = "#3a72b4"
HAIR_SHADE = "#2f5f9b"
HAIR_DEEP = "#24487d"
HAIR_INK = "#233c60"
SKIN = "#e6c4bd"
SKIN_SHADE = "#d9aca9"
CREAM = "#e9ead9"
CREAM_SHADE = "#dfe2d2"
MINT = "#d8e6cf"
MINT_SHADE = "#c9dcc4"
DEEP_TEAL = "#1f4a55"
PALE_BLUE = "#a8c4d4"
LINING_PINK = "#e8858f"
LINING_ORANGE = "#e0a95f"
BOW_MAGENTA = "#cf4b79"
BOW_DARK = "#a8405f"
PUFF_PINK = "#e9a2ae"
PUFF_PINK_DARK = "#d98b9a"
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
    face_ring=((684.0, 390.0), (648.0, 366.0), (618.0, 330.0), (600.0, 282.0),
               (606.0, 214.0), (640.0, 180.0), (700.0, 176.0), (744.0, 206.0),
               (764.0, 268.0), (752.0, 330.0), (716.0, 364.0)),
    eye_left=(638.0, 264.0), eye_right=(732.0, 268.0), eye_r=(27.0, 30.0),
    bangs=((556.0, 206.0), (592.0, 156.0), (660.0, 132.0), (736.0, 146.0), (794.0, 190.0),
           (806.0, 216.0), (770.0, 232.0), (740.0, 258.0), (712.0, 226.0), (686.0, 264.0),
           (656.0, 228.0), (626.0, 260.0), (596.0, 230.0), (572.0, 240.0)),
    # the neck
    neck_q=((656.0, 372.0), (714.0, 372.0), (718.0, 432.0), (652.0, 432.0)),
    # hair: a mass behind the head, and two falls that hang in front of the shoulders
    hair_back_route=((500.0, 1052.0), (486.0, 640.0), (556.0, 320.0), (686.0, 232.0),
                     (826.0, 340.0), (902.0, 640.0), (930.0, 1052.0)),
    fall_left=((600.0, 190.0), (520.0, 430.0), (466.0, 742.0), (492.0, 1052.0)),
    fall_right=((774.0, 188.0), (874.0, 430.0), (950.0, 726.0), (968.0, 1052.0)),
    lock_left=((616.0, 228.0), (566.0, 470.0), (548.0, 712.0)),
    lock_right=((742.0, 236.0), (768.0, 480.0), (790.0, 726.0)),
    # the seated lower mass: skirt over the knees, under-layer, and the fold bands
    skirt=((610.0, 654.0), (806.0, 666.0), (872.0, 862.0), (742.0, 1006.0),
           (492.0, 1012.0), (446.0, 878.0), (524.0, 736.0)),
    skirt_drop=((528.0, 672.0), (664.0, 800.0), (648.0, 992.0), (486.0, 996.0),
                (470.0, 828.0)),
    underskirt=((236.0, 846.0), (566.0, 830.0), (724.0, 1000.0), (250.0, 1020.0)),
    lining_pink=((286.0, 862.0), (438.0, 846.0), (492.0, 976.0), (326.0, 998.0)),
    lining_orange=((430.0, 930.0), (548.0, 906.0), (612.0, 1016.0), (470.0, 1020.0)),
    # her right arm, out of the cuff and down past the skirt
    arm_route=((856.0, 596.0), (872.0, 716.0), (866.0, 796.0)),
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
                 rows=[("hat_edge", dome(bx, by, L["brim_rx"], L["brim_ry"], L["brim_rot"]),
                        "where the top face meets the underside")],
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
    bangs = L["bangs"]
    fringe = planar("A-hair-bangs", "the fringe: hair falling over the forehead in points", 0.34,
                    catmull(bangs),
                    rows=[("hair_edge", catmull(bangs), "the fringe's edge")],
                    fill=HAIR_SHADE, authored=(("bang_apex", bangs[2]), ("bang_left", bangs[0]),
                                               ("bang_right", bangs[4])))
    return {"A-face": face, "A-neck": neck, "A-hair-bangs": fringe}


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
                                        steps=8, closed=False), fill=HAIR_DEEP)
    out["A-brow-right"] = planar("A-brow-right", "the right eyebrow", 0.35,
                                 catmull(((712.0, 226.0), (736.0, 220.0), (758.0, 228.0)),
                                         steps=8, closed=False), fill=HAIR_DEEP)
    out["A-mouth"] = planar("A-mouth", "the mouth", 0.35,
                            ellipse(690.0, 352.0, 8.0, 3.5, 0), fill="#c98a84")
    return out


# ---- hair: the mass behind, the two falls in front ---------------------------------

def _strip(route, width, depth, samples=48):
    from ..parts import families as fam
    dense = fam._catmull_open(tuple((x, HEIGHT - y) for x, y in route), 14)
    count = len(dense) - 1

    def spine(t):
        u = t * count
        i = min(count - 1, int(u))
        f = u - i
        a, b = dense[i], dense[i + 1]
        return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)

    def half_width(t):
        return width(t)

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
    for name, route, widths, z, fill_front, fill_back in (
            ("A-hair-fall-left", L["fall_left"], (66.0, 44.0, 14.0), 0.50, HAIR_LIT, HAIR_SHADE),
            ("A-hair-fall-right", L["fall_right"], (70.0, 48.0, 16.0), 0.50,
             HAIR_SHADE, HAIR_DEEP)):
        t0, tm, t1 = widths
        surface = _strip(route,
                         lambda t, t0=t0, tm=tm, t1=t1:
                         t0 + (tm - t0) * min(1.0, t / 0.45) + (t1 - tm) * max(0.0, (t - 0.45) / 0.55),
                         lambda t, z=z: z)
        out[name] = SheetPart(name=name, intent=f"one long fall of hair hanging in front of the "
                                                f"shoulder ({name.split('-')[-1]})",
                              front_fill=fill_front, back_fill=fill_back,
                              grid=surface.grid(samples=44, cols=3), anchors={},
                              authored=tuple((f"{name}_{i}", p) for i, p in enumerate(route)))
        marks.append((f"{name}-edge-front", name, "hair_edge", surface.edge(0, 1, 1.0, 90), HAIR_INK))
        marks.append((f"{name}-edge-back", name, "hair_edge", surface.edge(0, 1, -1.0, 90), HAIR_INK))
        marks.append((f"{name}-fold", name, "fold_edge",
                      tuple(surface.point(0.18 + 0.5 * i / 10, 0.4 - 1.0 * i / 10)
                            for i in range(11)), HAIR_INK))
    for name, route, w in (("A-hair-lock-left", L["lock_left"], 13.0),
                           ("A-hair-lock-right", L["lock_right"], 14.0)):
        surface = _strip(route, lambda t, w=w: w * (1.15 - 0.9 * t), lambda t: 0.52)
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
    L = LAYOUT
    skirt = planar("A-skirt-front", "the cream skirt over her knees", 0.26,
                   catmull(L["skirt"]),
                   rows=[("silhouette", catmull(L["skirt"]), "the skirt's own edge")],
                   fill=MINT, authored=(("skirt_seat", L["skirt"][2]),
                                        ("skirt_hem", L["skirt"][4])))
    drop = planar("A-skirt-drop", "the cream fold running down the skirt's left", 0.25,
                  catmull(L["skirt_drop"]), fill=CREAM)
    under = planar("A-underskirt", "the deep-teal under-layer below and left of the skirt", 0.22,
                   catmull(L["underskirt"]),
                   rows=[("silhouette", catmull(L["underskirt"]), "the under-layer's edge")],
                   fill=DEEP_TEAL, authored=(("under_left", L["underskirt"][0]),
                                             ("under_right", L["underskirt"][2])))
    pink = planar("A-lining-pink", "the pink lining band showing between the folds", 0.23,
                  catmull(L["lining_pink"]), fill=LINING_PINK)
    orange = planar("A-lining-orange", "the orange lining band below the pink", 0.23,
                    catmull(L["lining_orange"]), fill=LINING_ORANGE)
    return {"A-skirt-front": skirt, "A-skirt-drop": drop, "A-underskirt": under,
            "A-lining-pink": pink, "A-lining-orange": orange}


def arm_parts():
    L = LAYOUT
    surface = _strip(L["arm_route"], lambda t: 34.0 - 6.0 * t, lambda t: 0.55)
    arm = SheetPart(name="A-arm", intent="her right arm hanging out of the cuff",
                    front_fill=SKIN, back_fill=SKIN_SHADE,
                    grid=surface.grid(samples=30, cols=3), anchors={},
                    authored=tuple((f"arm_{i}", p) for i, p in enumerate(L["arm_route"])))
    hx, hy = L["hand"]
    hand = planar("A-hand", "her right hand at the end of that arm", 0.56,
                  ellipse(hx, hy, 28.0, 30.0, 18.0), fill=SKIN,
                  rows=[("contact", ellipse(hx, hy, 28.0, 30.0, 18.0), "the hand's own edge")])
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
    for dropped in ("A-head-face", "A-hair-sheet"):
        inherited_parts.pop(dropped, None)
    inherited_marks = [m for m in inherited_marks if m[1] not in ("A-head-face", "A-hair-sheet")]
    parts.update(inherited_parts)
    parts.update(hat_parts())
    parts.update(head_parts())
    parts.update(eye_parts())
    hair, hair_marks = hair_parts()
    parts.update(hair)
    arm, arm_marks = arm_parts()
    parts.update(arm)
    marks = list(inherited_marks) + list(hair_marks) + list(arm_marks)
    return dict(parts=parts, sheet_marks=tuple(marks), field=tuple(field()), meta=meta)


OBJECTS = {
    "hat-brim": (["A-hat-brim-under", "A-hat-brim-top"],
                 "the wide brim: teal underside near the camera, navy top face beyond"),
    "hat-crown": (["A-hat-crown"], "the crown standing on the brim"),
    "hat-puff-top": (["A-hat-puff-top"], "the pink cluster at the crown's back"),
    "hat-puff-right": (["A-hat-puff-right"], "the pink cluster on the brim's right"),
    "hair-back": (["A-hair-back"], "the hair mass behind the head"),
    "hair-bangs": (["A-hair-bangs"], "the fringe over the forehead"),
    "hair-falls": (["A-hair-fall-left", "A-hair-fall-right"],
                   "the outer falls hanging past the shoulders"),
    "hair-locks": (["A-hair-lock-left", "A-hair-lock-right"],
                   "the thin locks in front of each shoulder"),
    "face": (["A-face"], "the face field"),
    "neck": (["A-neck", "A-visible-neck-skin"], "the neck between chin and collar"),
    "eye-left": (["A-eye-left", "A-iris-left", "A-iris-deep-left", "A-glint-left"],
                 "the left eye: lid, iris, its shade, catchlight"),
    "eye-right": (["A-eye-right", "A-iris-right", "A-iris-deep-right", "A-glint-right"],
                  "the right eye: lid, iris, its shade, catchlight"),
    "brows": (["A-brow-left", "A-brow-right"], "the eyebrows"),
    "mouth": (["A-mouth"], "the mouth"),
    "collar": (["A-collar-left", "A-collar-right"], "the sailor collar, inherited"),
    "bodice": (["A-bodice-upper", "A-derived-waist-band", "A-bodice-continuation"],
               "the cream blouse and its waist, inherited"),
    "left-sleeve": (["A-left-sleeve", "A-left-cuff"], "one puff sleeve and its navy cuff"),
    "right-sleeve": (["A-right-sleeve", "A-right-cuff"], "the other puff sleeve and cuff"),
    "chest-bow": (["A-bow-ribbon"], "the magenta bow on the collar's V, inherited"),
    "arm-right": (["A-arm"], "her right arm out of the cuff"),
    "hand-right": (["A-hand"], "her right hand"),
    "skirt-front": (["A-skirt-front"], "the cream skirt over her knees"),
    "skirt-drop": (["A-skirt-drop"], "the shaded fold down the skirt's left"),
    "underskirt": (["A-underskirt"], "the deep-teal under-layer"),
    "lining": (["A-lining-pink", "A-lining-orange"], "the lining bands between the folds"),
}

FIELD = ("the frame's flat field: the teal ground and the near green bank, painted behind "
         "every part because a full-frame quad put through the depth engine decides nothing")


def declared_parts() -> set:
    return {part for parts, _why in OBJECTS.values() for part in parts}
