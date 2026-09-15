#!/usr/bin/env python3
"""relate.py — relational geometry resolver (ticket 06 prototype).

Turns a drawing spec written in *relations* into absolute geometry. No numeric coordinate
literals are needed anywhere in a spec: every position is expressed relative to the canvas
frame or to another already-declared shape.

    - {ellipse: head, at: [frame.w*0.60, frame.h*0.34], rx: frame.w*0.098, ry: frame.w*0.128}
    - {sunhat: hat, host: head, brim: 2.6*head.w, tilt: -14, crown: head.w*0.78, pom: 2}

The resolver does NOT look at any reference image. Tracing a reference is only ever a way to
seed *values* for a spec like this (the teacher role); the engine itself stays target-free.

Two orders, kept separate on purpose:
    resolution  = declaration order (a node may use any shape declared above it)
    painting    = `layers` order, then declaration order within a layer

Anchors a shape exposes (usable by any later node):
    at  cx cy  left right top bottom  w h  w2 h2 (half extents)  rx ry  rot
    <shape>@<t>  via {along: shape, t: 0.35} — point on the outline, wraps, optional `out: D`

Relation forms (value of any positional or size key):
    number                      relative or absolute scalar
    "expr"                      arithmetic over anchors: "1.8*head.rx + 4", "frame.w*0.62"
    {between: [A, B, t]}        point at t along A->B (t may be <0 or >1: extrapolates)
    {at: SHAPE}                  a shape's own centre
    {along: SHAPE, t: 0.35}     point on SHAPE's outline at parameter t (wraps)
    {along: SHAPE, t: 0.1, out: D}  same, pushed D outward along the outline normal
    {polar: P, angle: 90, d: 40}  point at angle/distance from P (0=right, 90=down, degrees)

Note: `on`, `off`, `yes`, `no` are YAML 1.1 booleans, so this language uses `along` for points
on an outline and `host` for the shape an object family attaches to.

Usage:
    .venv/bin/python .scratch/06-relational-geometry/work/relate.py SPEC.yaml -o out.png [--anchors]
"""
from __future__ import annotations

import argparse
import ast
import datetime
import hashlib
import json
import math
import os
from pathlib import Path

import numpy as np
import yaml

import sys

# same directory as scene_render.py when installed in scripts/; the path insert covers the
# .scratch prototype locations this file historically lived in.
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))
from scene_render import chrome, smooth_path, flood_region  # noqa: E402

# --------------------------------------------------------------------------------------
# guarded conversions + file IO (the resolver's whole job is numeric, so it validates)
# --------------------------------------------------------------------------------------
class SpecError(SystemExit):
    """A spec the resolver cannot honour — reported in words, never as a traceback."""


def num(value: object, what: str = "value") -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise SpecError(f"relate: {what} is not a number: {value!r}") from exc


def whole(value: object, what: str = "value") -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise SpecError(f"relate: {what} is not an integer: {value!r}") from exc


def read_text(path: Path) -> str:
    try:
        return path.read_text()
    except OSError as exc:
        raise SpecError(f"relate: cannot read {path}: {exc}") from exc


def write_text(path: Path, text: str) -> None:
    try:
        path.write_text(text)
    except OSError as exc:
        raise SpecError(f"relate: cannot write {path}: {exc}") from exc


def load_yaml(path: Path) -> object:
    try:
        spec = yaml.safe_load(read_text(path))
    except yaml.YAMLError as exc:
        raise SpecError(f"relate: bad YAML in {path}: {exc}") from exc
    return _reject_bool_keys(spec)


_YAML_BOOL_WORDS = ("on", "off", "yes", "no", "y", "n", "true", "false")


def _reject_bool_keys(node: object) -> object:
    """YAML 1.1 silently turns keys like `on:`/`off:` into True/False — name the culprit."""
    if isinstance(node, dict):
        for key, val in node.items():
            if isinstance(key, bool):
                word = "true" if key else "false"
                raise SpecError(
                    f"relate: a key parsed as the boolean {word!r} — YAML reserved word "
                    f"(one of {', '.join(_YAML_BOOL_WORDS)}). Rename it, e.g. `along:` or `host:`."
                )
            _reject_bool_keys(val)
    elif isinstance(node, list):
        for item in node:
            _reject_bool_keys(item)
    return node


# --------------------------------------------------------------------------------------
# expression evaluation (whitelisted AST — no arbitrary code execution)
# --------------------------------------------------------------------------------------
_FUNCS: dict[str, object] = {
    "min": min, "max": max, "abs": abs, "hypot": math.hypot,
    "deg": math.degrees, "rad": math.radians,
}
_ALLOWED_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name, ast.Attribute,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.USub, ast.UAdd,
    ast.Call, ast.Load,
)


def eval_expr(expr: str, env: dict[str, float]) -> float:
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as exc:
        raise SpecError(f"relate: cannot parse expression {expr!r}: {exc}") from exc
    for node in ast.walk(tree):
        if not isinstance(node, _ALLOWED_NODES):
            raise SpecError(f"relate: forbidden syntax in {expr!r}: {type(node).__name__}")
    return _eval_node(tree.body, env)


def _eval_node(node: ast.AST, env: dict[str, float]) -> float:
    if isinstance(node, ast.Constant):
        return num(node.value, "literal")
    if isinstance(node, ast.Name):
        if node.id in _FUNCS:
            raise SpecError(f"relate: bare function name {node.id!r}")
        return _lookup(node.id, env)
    if isinstance(node, ast.Attribute):
        return _lookup(_dotted(node), env)
    if isinstance(node, ast.UnaryOp):
        val = _eval_node(node.operand, env)
        return -val if isinstance(node.op, ast.USub) else val
    if isinstance(node, ast.BinOp):
        left, right = _eval_node(node.left, env), _eval_node(node.right, env)
        op = node.op
        if isinstance(op, ast.Add):
            return left + right
        if isinstance(op, ast.Sub):
            return left - right
        if isinstance(op, ast.Mult):
            return left * right
        if isinstance(op, ast.Div):
            if right == 0:
                raise SpecError("relate: division by zero in expression")
            return left / right
        if isinstance(op, ast.Mod):
            return left % right
        return left**right
    if isinstance(node, ast.Call):
        fn = _dotted(node.func)
        if fn not in _FUNCS:
            raise SpecError(f"relate: unknown function {fn!r}")
        target = _FUNCS[fn]
        if not callable(target):
            raise SpecError(f"relate: {fn!r} is not callable")
        return num(target(*[_eval_node(a, env) for a in node.args]))
    raise SpecError(f"relate: unsupported expression node {type(node).__name__}")


def _lookup(name: str, env: dict[str, float]) -> float:
    if name not in env:
        raise SpecError(f"relate: unknown anchor {name!r}; declared so far: {sorted(env)}")
    return env[name]


def _dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_dotted(node.value)}.{node.attr}"
    raise SpecError("relate: bad dotted name")


# --------------------------------------------------------------------------------------
# anchors
# --------------------------------------------------------------------------------------
class Anchor:
    """A resolved shape. Its handles are merged into the shared env as `<id>.<handle>`."""

    def __init__(self, sid: str, handles: dict[str, float],
                 outline: list[tuple[float, float]] | None = None):
        self.id = sid
        self.env: dict[str, float] = {f"{sid}.{k}": num(v, f"{sid}.{k}") for k, v in handles.items()}
        self._outline = outline

    def on(self, t: float) -> tuple[float, float]:
        pts = self._require_outline("on")
        n = len(pts)
        u = (t % 1.0) * (n - 1)          # u >= 0, so truncation is floor
        i = min(whole(u), n - 2)
        f = u - i
        j = min(i + 1, n - 1)
        return (pts[i][0] + (pts[j][0] - pts[i][0]) * f, pts[i][1] + (pts[j][1] - pts[i][1]) * f)

    def normal(self, t: float) -> tuple[float, float]:
        px, py = self.on(t)
        cx, cy = self._centroid()
        dx, dy = px - cx, py - cy
        n = math.hypot(dx, dy) or 1.0
        return (dx / n, dy / n)

    def _centroid(self) -> tuple[float, float]:
        pts = self._require_outline("centroid")
        return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))

    def _require_outline(self, why: str) -> list[tuple[float, float]]:
        if not self._outline:
            raise SpecError(f"relate: shape {self.id!r} has no outline, so {why}() is unavailable")
        return self._outline

    def handles(self) -> dict[str, float]:
        return {k.split(".", 1)[1]: v for k, v in self.env.items()}


def ellipse_outline(cx, cy, rx, ry, rot_deg=0.0, n=72) -> list[tuple[float, float]]:
    a = math.radians(rot_deg)
    ca, sa = math.cos(a), math.sin(a)
    return [
        (cx + rx * math.cos(th) * ca - ry * math.sin(th) * sa,
         cy + rx * math.cos(th) * sa + ry * math.sin(th) * ca)
        for th in (2 * math.pi * i / n for i in range(n + 1))
    ]


def ellipse_anchor(sid, cx, cy, rx, ry, rot=0.0) -> Anchor:
    """Extreme points of a rotated ellipse, so `left/right/top/bottom` stay truthful."""
    a = math.radians(rot)
    ca, sa = math.cos(a), math.sin(a)
    hx, hy = math.hypot(rx * ca, ry * sa), math.hypot(rx * sa, ry * ca)
    return Anchor(sid, {
        "cx": cx, "cy": cy, "rx": rx, "ry": ry, "w": 2 * rx, "h": 2 * ry,
        "w2": rx, "h2": ry, "rot": rot,
        "left": cx - hx, "right": cx + hx, "top": cy - hy, "bottom": cy + hy,
    }, outline=ellipse_outline(cx, cy, rx, ry, rot))


def droop_outline(cx, cy, rx, ry, rot_deg=0.0, droop=0.0, n=72) -> list[tuple[float, float]]:
    """A flat brim ellipse whose near edge sags along the brim's own normal.

    A real floppy wide brim is not a flat disc, so its silhouette is not an ellipse: the near edge
    droops. `droop` (0 = flat, so every existing spec is unchanged) is the sag at the near edge in
    half-brim-widths; the far edge and the two tips stay put, so the bend dies out smoothly and the
    brim still reads as one closed curve. The sag is applied along the brim's local +v axis, i.e.
    its own normal, so rotating the brim rotates the droop with it.
    """
    if not droop:
        return ellipse_outline(cx, cy, rx, ry, rot_deg, n)
    a = math.radians(rot_deg)
    ca, sa = math.cos(a), math.sin(a)
    pts: list[tuple[float, float]] = []
    for i in range(n + 1):
        th = 2 * math.pi * i / n
        u = rx * math.cos(th)
        v = ry * math.sin(th) + droop * rx * max(0.0, math.sin(th))
        pts.append((cx + u * ca - v * sa, cy + u * sa + v * ca))
    return pts


def droop_anchor(sid, cx, cy, rx, ry, rot=0.0, droop=0.0) -> Anchor:
    """`ellipse_anchor` with an optional drooping outline; the handles stay the ellipse's.

    Keeping the handles from the flat ellipse means `hat.left/right/top/bottom` and the poms do not
    silently move when `droop` changes: droop reshapes the silhouette, it is not a re-fit.
    """
    base = ellipse_anchor(sid, cx, cy, rx, ry, rot)
    if droop:
        base._outline = droop_outline(cx, cy, rx, ry, rot, droop)
    return base


def bbox_anchor(sid, pts: list[tuple[float, float]]) -> Anchor:
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    return Anchor(sid, {
        "cx": (x0 + x1) / 2, "cy": (y0 + y1) / 2, "left": x0, "right": x1,
        "top": y0, "bottom": y1, "w": x1 - x0, "h": y1 - y0,
        "w2": (x1 - x0) / 2, "h2": (y1 - y0) / 2,
    }, outline=pts)


# --------------------------------------------------------------------------------------
# relation resolution
# --------------------------------------------------------------------------------------
class Ctx:
    def __init__(self, frame: dict[str, float]):
        self.env: dict[str, float] = {
            "frame.w": num(frame["w"], "frame.w"), "frame.h": num(frame["h"], "frame.h"),
            "frame.cx": num(frame["w"], "frame.w") / 2, "frame.cy": num(frame["h"], "frame.h") / 2,
        }
        self.anchors: dict[str, Anchor] = {}
        self.meta: dict[str, dict] = {}
        # nodes whose geometry is computed FROM the reference raster — the teacher. They are
        # legal while the reference is open, and forbidden in an M5 reference-free spec (P18).
        self.teacher: list[str] = []

    def add(self, anchor: Anchor) -> Anchor:
        self.env.update(anchor.env)
        self.anchors[anchor.id] = anchor
        return anchor

    def shape(self, sid: str) -> Anchor:
        if sid not in self.anchors:
            raise SpecError(f"relate: unknown shape {sid!r}; declared so far: {sorted(self.anchors)}")
        return self.anchors[sid]

    def scalar(self, value: object) -> float:
        if isinstance(value, bool):
            raise SpecError("relate: a bool is not a scalar")
        if isinstance(value, (int, float)):
            return num(value)
        if isinstance(value, str):
            return eval_expr(value, self.env)
        raise SpecError(f"relate: not a scalar: {value!r}")

    def point(self, value: object) -> tuple[float, float]:
        if isinstance(value, dict):
            return self._relation(value)
        if isinstance(value, (list, tuple)):
            if len(value) != 2:
                raise SpecError(f"relate: a point needs 2 components, got {value!r}")
            return (self.scalar(value[0]), self.scalar(value[1]))
        raise SpecError(f"relate: not a point: {value!r}")

    def endpoint(self, value: object) -> tuple[float, float]:
        """A between() endpoint: point forms, or a bare shape/handle string.

        `{between: [head.left, head.right, 0.5]}` reads naturally, so handle strings
        coerce to extent points (left/right at cy, top/bottom at cx); size scalars
        are rejected — they are not points.
        """
        if isinstance(value, str):
            sid, _, handle = value.partition(".")
            shape = self.anchors.get(sid)
            if shape is not None:
                cx, cy = shape.env[f"{sid}.cx"], shape.env[f"{sid}.cy"]
                if not handle or handle in ("cx", "cy", "at", "center", "centre"):
                    return (cx, cy)
                if handle == "left":
                    return (shape.env[f"{sid}.left"], cy)
                if handle == "right":
                    return (shape.env[f"{sid}.right"], cy)
                if handle == "top":
                    return (cx, shape.env[f"{sid}.top"])
                if handle == "bottom":
                    return (cx, shape.env[f"{sid}.bottom"])
                raise SpecError(f"relate: {value!r} is a size scalar ({handle}), not a point")
            raise SpecError(f"relate: {value!r} is not a point or a known shape")
        return self.point(value)

    def _relation(self, value: dict) -> tuple[float, float]:
        if "between" in value:
            spec = list(value["between"])
            if len(spec) < 3:
                raise SpecError("relate: between needs [A, B, t]")
            pa = self.endpoint(spec[0])
            pb = self.endpoint(spec[1])
            t = self.scalar(spec[2])
            return (pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t)
        if "at" in value:
            sh = self.shape(str(value["at"]))
            return (sh.env[f"{sh.id}.cx"], sh.env[f"{sh.id}.cy"])
        if "along" in value:
            sh = self.shape(str(value["along"]))
            t = self.scalar(value.get("t", 0.0))
            px, py = sh.on(t)
            if "out" in value:
                d = self.scalar(value["out"])
                nx, ny = sh.normal(t)
                return (px + nx * d, py + ny * d)
            return (px, py)
        if "polar" in value:
            px, py = self.point(value["polar"])
            ang = math.radians(self.scalar(value.get("angle", 0.0)))
            d = self.scalar(value["d"])
            return (px + math.cos(ang) * d, py + math.sin(ang) * d)
        if "mirror" in value:
            p = self.point(value["mirror"])
            ax = value.get("across")
            if isinstance(ax, str):
                sh = self.shape(ax)
                axis = sh.env[f"{sh.id}.cx"]
            else:
                axis = self.scalar(ax)
            return (2 * axis - p[0], p[1])
        raise SpecError(f"relate: unknown relation keys {sorted(value)}")


def taper_band(spine: list[tuple[float, float]], widths: list[float],
               side: str = "both") -> list[tuple[float, float]]:
    """Closed polygon around an open spine with a per-point width (a tapered ribbon).

    `ribbon` above gives one constant width; lashes, brows and strands want a profile.
    side="both" straddles the spine; side="left"/"right" grows the band to one side only,
    leaving the spine itself as one edge — a lash must sit ON the lid line, not through it.
    """
    pts = [np.array(p, float) for p in spine]
    left: list[list[float]] = []
    right: list[list[float]] = []
    for i, p in enumerate(pts):
        if i == 0:
            tangent = pts[1] - pts[0]
        elif i == len(pts) - 1:
            tangent = pts[-1] - pts[-2]
        else:
            tangent = pts[i + 1] - pts[i - 1]
        tangent = tangent / (np.linalg.norm(tangent) or 1.0)
        normal = np.array([-tangent[1], tangent[0]])
        if side == "left":
            left.append((p + normal * widths[i]).tolist())
            right.append(p.tolist())
        elif side == "right":
            left.append(p.tolist())
            right.append((p - normal * widths[i]).tolist())
        else:
            normal = normal * (widths[i] / 2)
            left.append((p + normal).tolist())
            right.append((p - normal).tolist())
    return [tuple(num(v) for v in p) for p in left + right[::-1]]


def bez3(p0, p1, p2, p3, n=20) -> list[tuple[float, float]]:
    """Cubic bezier sampled at n+1 points."""
    out = []
    for i in range(n + 1):
        t = i / n
        s = 1 - t
        out.append((s**3 * p0[0] + 3 * s * s * t * p1[0] + 3 * s * t * t * p2[0] + t**3 * p3[0],
                    s**3 * p0[1] + 3 * s * s * t * p1[1] + 3 * s * t * t * p2[1] + t**3 * p3[1]))
    return out


def ribbon(spine: list[tuple[float, float]], width: float) -> list[tuple[float, float]]:
    """Closed constant-width outline around an open spine (tapers not needed yet)."""
    pts = [np.array(p, float) for p in spine]
    left: list[tuple[float, float]] = []
    right: list[tuple[float, float]] = []
    for i, p in enumerate(pts):
        if i == 0:
            tangent = pts[1] - pts[0]
        elif i == len(pts) - 1:
            tangent = pts[-1] - pts[-2]
        else:
            tangent = pts[i + 1] - pts[i - 1]
        tangent = tangent / (np.linalg.norm(tangent) or 1.0)
        normal = np.array([-tangent[1], tangent[0]]) * (width / 2)
        left.append((num(p[0] + normal[0]), num(p[1] + normal[1])))
        right.append((num(p[0] - normal[0]), num(p[1] - normal[1])))
    return left + right[::-1]


# --------------------------------------------------------------------------------------
# vocabulary (tier 3): parametric object families — drawing knowledge lives here
# --------------------------------------------------------------------------------------
def expand_eye(node: dict, ctx: Ctx, emit: list[dict]) -> Anchor:
    """A layered anime eye — the drawing knowledge is IN the engine.

    Structure a model should not re-derive: an eye is an almond aperture (sclera), a
    two-tone iris that sits low and is partly capped by the lid, a pupil under the iris
    top, a highlight on the nose side, a tapered upper lash with an outer wing, and a
    thin lower lash line. The whole aperture is one generated curve (corners, lid arcs).

    Placement/size are relations in host units; an eye has zero authored coordinates.
    `mirror-of` builds the matching eye: same every param, centre reflected across the
    host axis, tilt and outer/inner sides flipped.

    Exposed anchors (usable by later nodes): cx cy left right top bottom w h w2 h2
    (aperture bbox) plus outerx/outery, innerx/innery (corners), irisx/irisy,
    topx/topy, botx/boty; the aperture outline is usable with {along: eye, t: ...}.
    """
    sid = str(node["eye"])
    host_id = str(node["host"])
    host = ctx.shape(host_id)
    axis_x = host.env[f"{host_id}.cx"]
    z = str(node.get("z", "default"))

    style_keys = ("sclera-fill", "iris-top-fill", "iris-bot-fill", "pupil-fill",
                  "lash-fill", "glint-fill", "iris-w", "iris-h", "lash-w",
                  "line-w", "glints", "almond", "w", "h", "tilt")

    if "mirror-of" in node:
        other = str(node["mirror-of"])
        m = ctx.meta.get(f"eye:{other}")
        if m is None:
            raise SpecError(f"relate: {sid}.mirror-of names {other!r}, but that eye has no stored "
                            f"params — declare it first")
        P = dict(m["P"])
        P["cx"] = 2 * axis_x - m["P"]["cx"]
        P["facing"] = -m["P"]["facing"]
        P["tilt"] = -m["P"]["tilt"]
        style = dict(m["style"])
        for k in style_keys:          # explicit overrides beat the mirror
            if k in node:
                style[k] = node[k]
    else:
        at = ctx.point(node["at"])
        w = ctx.scalar(node["w"])
        P = {"cx": at[0], "cy": at[1],
             "w": w,
             "h": ctx.scalar(node["h"]) if "h" in node else w * 0.62,
             "tilt": ctx.scalar(node.get("tilt", 0)),
             "almond": ctx.scalar(node.get("almond", 0.55))}
        P["facing"] = -1.0 if at[0] <= axis_x else 1.0   # -1: outer corner on screen-left
        style = {k: node[k] for k in node if k not in P and k not in
                 ("eye", "host", "at", "mirror-of", "z", "desc", "h")}

    cx, cy = P["cx"], P["cy"]
    w, h = P["w"], P["h"]
    a = w / 2
    f = P["facing"]
    almond = P["almond"]
    tilt = P["tilt"]

    def place(u: float, v: float) -> tuple[float, float]:
        """Eye-local (u: inner(-a)..outer(+a), v: screen-down) -> screen, rotated by tilt."""
        t = math.radians(tilt)
        x0, y0 = f * u, v
        return (cx + x0 * math.cos(t) - y0 * math.sin(t), cy + x0 * math.sin(t) + y0 * math.cos(t))

    # ---- the aperture: one generated almond curve (two lid arcs sharing the corners) ----
    sharp = 0.35 + 0.65 * almond            # almond=1 -> controls hug corners -> pointed
    rise = h * (0.50 + 0.14 * almond)       # top-lid arch height
    drop = h * (0.46 - 0.04 * almond)       # bottom-lid drop
    reach_in = a * 0.55 * sharp
    reach_out = a * 0.50 * sharp
    inner, outer = (-a, 0.0), (a, 0.0)
    top_pts = bez3(inner, (-a + reach_in, -rise * 0.55), (a - reach_out, -rise * 0.88), outer)
    bot_pts = bez3(outer, (a - reach_out * 0.9, drop * 0.88), (-a + reach_in * 0.9, drop * 0.94), inner)
    almond_pts = [place(u, v) for (u, v) in top_pts + bot_pts[1:]]

    emit.append({"blob": f"{sid}-sclera", "poly": almond_pts,
                 "fill": style.get("sclera-fill", "#fdf2f9"), "z": z,
                 "desc": f"{sid} sclera: the almond aperture, pale"})

    # ---- iris: two-tone (dark top under the lid, light bottom), sits low ----
    # the iris must stay inside the aperture: clamp its ry so the bottom lid never shows
    # a gaping white band under it (the lid rises toward the corners)
    irx = w * float(style.get("iris-w", 0.44))
    iry = h * float(style.get("iris-h", 0.46))
    # gaze is a WORLD side (like the light): both eyes look the same screen way.
    # local u: +a is the outer corner, so screen-right is f*a, screen-left is -f*a.
    gaze = float(style.get("gaze", -1))                 # -1: looks screen-left (like the ref)
    iu, iv = gaze * f * a * 0.10, -h * 0.02
    icx, icy = place(iu, iv)
    lid_edge = min(bot_pts, key=lambda p: abs(abs(p[0]) - irx))[1]
    iry = min(iry, max(iry * 0.55, lid_edge - iv + h * 0.02))
    irx = min(irx, a * 0.92)
    emit.append({"ellipse": f"{sid}-iris-lo", "at": [icx, icy], "rx": irx, "ry": iry,
                 "fill": style.get("iris-bot-fill", "#ef92ae"), "z": z,
                 "desc": f"{sid} iris lower tone"})
    # top cap: upper half of the iris + a chord, so the boundary is a curve not a line
    cf = 0.02
    cap = [(icx + irx * math.cos(th), icy + iry * math.sin(th))
           for th in (math.pi + math.pi * i / 20 for i in range(21))]
    cap += [(icx + irx, icy + cf * iry), (icx - irx, icy + cf * iry)]
    emit.append({"blob": f"{sid}-iris-hi", "poly": cap,
                 "fill": style.get("iris-top-fill", "#4470b3"), "z": z,
                 "desc": f"{sid} iris upper tone (under the lid shadow)"})

    # ---- pupil + reflection + glints: positions computed first, painted bottom to top.
    # The glint tracks the LIGHT (a world side, `glint-side`), not the eye's inner/outer:
    # both eyes of a face catch the same lamp. ----
    gs = float(style.get("glint-side", -1))          # -1: light from screen-left
    g1u = f * gs * a * 0.24
    g1x, g1y = place(g1u, -h * 0.30)
    g2x, g2y = place(f * a * 0.30, h * 0.14)
    emit.append({"ellipse": f"{sid}-pupil", "at": [icx, icy + iry * 0.12],
                 "rx": irx * 0.22, "ry": iry * 0.30,
                 "fill": style.get("pupil-fill", "#2b2233"), "z": z,
                 "desc": f"{sid} small dark pupil (cel eyes barely show one)"})
    if style.get("refl-fill"):
        emit.append({"ellipse": f"{sid}-refl",
                     "at": [g1x, g1y + iry * 0.95],
                     "rx": irx * 0.18, "ry": iry * 0.18,
                     "fill": style["refl-fill"], "z": z,
                     "desc": f"{sid} coloured reflection just below the glint"})
    r1 = w * 0.075
    emit.append({"ellipse": f"{sid}-glint1", "at": [g1x, g1y], "rx": r1, "ry": r1 * 1.3,
                 "fill": style.get("glint-fill", "#ffffff"), "z": z,
                 "desc": f"{sid} main glint, nose-side upper"})
    if whole(style.get("glints", 2), f"{sid}.glints") >= 2:
        r2 = w * 0.055
        emit.append({"ellipse": f"{sid}-glint2", "at": [g2x, g2y], "rx": r2, "ry": r2 * 1.2,
                     "fill": style.get("glint-fill", "#ffffff"), "z": z,
                     "desc": f"{sid} small glint, outer lower"})

    # ---- upper lash: a band anchored ON the top lid line, growing outward (up),
    #      thin at the inner corner, thick through the middle, wing past the outer corner.
    #      Growing one-sided keeps black out of the eye interior. ----
    lw = h * float(style.get("lash-w", 0.16))
    wing1, wing2 = (a + 0.12 * a, -0.05 * h), (a + 0.26 * a, -0.13 * h)
    lash_spine = [place(u, v) for (u, v) in top_pts] + [place(*wing1), place(*wing2)]
    n_main = len(top_pts)
    widths = [lw * (0.40 + 0.60 * min(1.0, (i / (n_main - 1)) * 2.6)) for i in range(n_main)]
    widths += [lw * 0.75, lw * 0.55]
    lash_poly = taper_band(lash_spine, widths, side="right" if f >= 0 else "left")
    emit.append({"blob": f"{sid}-lash", "poly": lash_poly,
                 "fill": style.get("lash-fill", "#0a0e18"), "z": z,
                 "desc": f"{sid} upper lash: one-sided tapered band + outer wing"})

    # ---- lower lash line + a sealing outline (thin, so the top stays the lash's job) ----
    line_w = max(2.0, h * float(style.get("line-w", 0.05)))
    emit.append({"stroke": f"{sid}-lower", "spine": [place(u, v) for (u, v) in bot_pts[1:]],
                 "w": line_w, "ink": style.get("lash-fill", "#0a0e18"), "z": z,
                 "desc": f"{sid} lower lash line"})
    emit.append({"stroke": f"{sid}-outline", "spine": almond_pts,
                 "w": line_w * 0.55, "ink": style.get("lash-fill", "#0a0e18"), "z": z,
                 "desc": f"{sid} aperture outline"})

    # ---- anchors other shapes can hang off ----
    anchor = bbox_anchor(sid, almond_pts)
    ox, oy = place(a, 0.0)
    nx, ny = place(-a, 0.0)
    tx, ty = place(0.0, -rise)
    bx, by = place(0.0, drop)
    for name, val in {"outerx": ox, "outery": oy, "innerx": nx, "innery": ny,
                      "irisx": icx, "irisy": icy, "topx": tx, "topy": ty,
                      "botx": bx, "boty": by, "facing": f}.items():
        anchor.env[f"{sid}.{name}"] = num(val, f"{sid}.{name}")
    ctx.add(anchor)
    ctx.meta[f"eye:{sid}"] = {"P": P, "style": style}
    return anchor


def expand_sunhat(node: dict, ctx: Ctx, emit: list[dict]) -> Anchor:
    """A wide-brim hat from ~6 parameters.

    The structure knowledge the model should not have to re-derive: a wide brim seen at an
    angle is a squashed ellipse; the crown is a dome sitting up the brim's own normal; and the
    brim is ONE shape split into two complementary slices around the dome (P17 z-plane split,
    not a path split): the far slice paints first, the dome over it, the near slice over the
    dome's base. That near slice is what makes it read as a hat (fixed 2026-09-14, SA1 finding
    1a: the old full-ellipse + thin rim strip let the dome paint over the near brim).

    The two fills are the brim's own two surfaces, and the split between them is the brim's FAR
    EDGE curling over — NOT a chord across the disc (fixed 2026-09-15, M2 attempt 2): a disc cut
    by a straight chord gives two pointed half-lobes that only touch at the tips, so once hair or
    the crown covers the chord the top surface reads as a detached lozenge (both M2 reviewers saw
    exactly that). The far slice is instead the rim band that hugs the brim's far outline, and the
    near slice is the top surface it borders: `front` picks the near arc and `rim` how far the top
    surface is inset from the far edge, so the two fills still tile the ellipse exactly.

    `droop` (default 0 = the flat ellipse, backward compatible) is a family change demanded by the
    13-assembly brim: a real floppy wide brim is not a flat disc, so its silhouette is not an
    ellipse. It sags the near edge along the brim's own normal (see `droop_outline`); the fit of
    `sunhat` to the reference's frozen brim masks is what asked for it.
    """
    sid = str(node["sunhat"])
    host_id = str(node["host"])
    host = ctx.shape(host_id)

    brim_w = ctx.scalar(node["brim"])
    tilt = ctx.scalar(node.get("tilt", 0))
    crown_w = ctx.scalar(node["crown"])
    flat = ctx.scalar(node.get("flat", 0.30))
    droop = ctx.scalar(node.get("droop", 0.0))
    drop = ctx.scalar(node.get("drop", 0.62))
    lift = ctx.scalar(node.get("lift", 0.42))
    z = str(node.get("z", "hat"))
    z_front = str(node.get("z-front", z))
    # poms are the hat's topmost feature. When the brim surfaces are reference-seeded regions that
    # paint over the family's own brim (M2 attempt 3), the poms must still sit above them; the
    # default z keeps every historical spec rendering exactly as before.
    z_pom = str(node.get("z-pom", z))

    brim_rx = brim_w / 2
    brim_ry = brim_rx * flat
    bx = host.env[f"{host_id}.cx"]
    by = host.env[f"{host_id}.cy"] - host.env[f"{host_id}.h2"] * lift
    brim = ctx.add(droop_anchor(f"{sid}-brim", bx, by, brim_rx, brim_ry, tilt, droop))

    crown_rx = crown_w / 2
    crown_ry = ctx.scalar(node.get("crown-h", 0.62)) * crown_rx
    # step `drop` crown-radii up the brim's own normal, i.e. rotate local -Y by tilt
    a = math.radians(tilt)
    dist = crown_ry * drop
    dome = ctx.add(ellipse_anchor(f"{sid}-dome", bx + dist * math.sin(a), by - dist * math.cos(a),
                                  crown_rx, crown_ry, tilt))

    # P17 z-split: ONE brim, two complementary slices tiling the ellipse exactly.
    # `front` [t0, t1] picks the near (top-surface) arc; the far slice is its complement
    # (t1 -> t0+1), the rim band along the brim's far edge.
    # Paint order below: far rim -> dome -> near top surface, so the dome sits behind the
    # near brim and in front of the far rim, with no seam (same ellipse, same anchor).
    front = node.get("front", [0.05, 0.45])
    if not isinstance(front, (list, tuple)) or len(front) != 2:
        raise SpecError(f"relate: {sid}.front must be [t0, t1], got {front!r}")
    t0, t1 = ctx.scalar(front[0]), ctx.scalar(front[1])
    if not (0.0 <= t0 < t1 <= 1.0):
        raise SpecError(f"relate: {sid}.front must satisfy 0 <= t0 < t1 <= 1, got [{t0}, {t1}]")
    # `rim` = how far the brim's far edge folds over, as a fraction of the way from that edge to
    # the brim centre. It must be > 0 (0 would lay the seam along the outline itself and collapse
    # the far band); the default folds a visible band in, so the near surface keeps the brim's own
    # near edge all the way round.
    rim = ctx.scalar(node.get("rim", 0.45))
    if not (0.0 < rim < 1.0):
        raise SpecError(f"relate: {sid}.rim must satisfy 0 < rim < 1, got {rim}")

    def outer_arc(a: float, b: float, n: int = 48) -> list[tuple[float, float]]:
        return [brim.on(a + (b - a) * i / n) for i in range(n + 1)]

    def seam(a: float, b: float, n: int = 48) -> list[tuple[float, float]]:
        # The border between the brim's two surfaces: the outer arc of the far edge pulled toward
        # the brim centre, so it follows the outline instead of cutting across the disc. It meets
        # the outline at both ends (the fold dies out there), so the far band tapers to nothing
        # at the fold's ends and the two slices still share every seam point exactly.
        span = (a + 1.0) - b
        out: list[tuple[float, float]] = []
        for i in range(n + 1):
            px, py = brim.on(b + span * i / n)
            f = rim * math.sin(math.pi * i / n)
            out.append((px + f * (bx - px), py + f * (by - py)))
        return out

    border = seam(t0, t1)
    emit.append(
        {"blob": f"{sid}-brim-far", "poly": outer_arc(t1, t0 + 1.0) + border[-2:0:-1],
         "fill": node.get("brim-fill", "#3b7f92"), "z": z,
         "desc": f"brim far edge (the surface folding away from the viewer): a flat disc seen at "
                 f"{tilt:+.0f}deg -> ellipse {brim_w:.0f} wide, {2 * brim_ry:.0f} deep, folded in "
                 f"{rim:.2f} of the way to the centre; painted under the crown"})
    emit.append(
        {"ellipse": f"{sid}-dome", "at": [dome.env[f"{sid}-dome.cx"], dome.env[f"{sid}-dome.cy"]],
         "rx": crown_rx, "ry": crown_ry, "rot": tilt,
         "fill": node.get("crown-fill", "#32405b"), "stroke": node.get("crown-stroke"),
         "sw": node.get("crown-sw"),
         "z": z, "desc": f"crown: dome {drop:.2f} crown-radii up the brim normal, "
                         "between the brim's far edge and its top surface"})
    emit.append(
        {"blob": f"{sid}-brim-near", "poly": outer_arc(t0, t1) + border[1:-1],
         "fill": node.get("rim-fill", "#4d94a6"), "z": z_front,
         "desc": "brim top surface: shares the brim's near outline, borders the far edge along "
                 "the fold, and covers the crown's base so the crown does not float"})

    for i in range(whole(node.get("pom", 0), f"{sid}.pom")):
        poms = node.get("pom-at", [0.62, 0.88])
        if i >= len(poms):
            raise SpecError(f"relate: {sid} asked for {node.get('pom')} poms but pom-at has {len(poms)} entries")
        t = ctx.scalar(poms[i])
        px, py = brim.on(t)
        r = ctx.scalar(node.get("pom-r", 0.09)) * brim_rx
        emit.append({"ellipse": f"{sid}-pom{i + 1}", "at": [px, py], "rx": r, "ry": r * 0.86,
                     "fill": node.get("pom-fill", "#df9199"), "z": z_pom,
                     "desc": f"pom at t={t:.2f} along the brim outline, r={r:.0f}"})

    # the family id itself is an anchor: "the hat" = its brim footprint, so `{along: hat, t}` works
    ctx.add(Anchor(sid, {k.split(".", 1)[1]: v for k, v in brim.env.items()},
                   outline=brim._outline))
    return brim


def expand_face(node: dict, ctx: Ctx, emit: list[dict]) -> Anchor:
    """A head: cranium ball + jaw wedge (Loomis ball-and-plane, mechanically).

    The ellipse host was the round-chin cause (SA2's honest gap: "ellipse host -> round chin").
    A head is not an ellipse. Measured from image.jpg, the visible face is 128px wide at the cheek
    line (y306) and tapers to a 7px chin at y377; an ellipse of the same bounding box gives a
    ~60px round bottom instead.

    The two shapes must be sized so the JAW IS OUTSIDE THE CRANIUM below the cheek line — the first
    version drew a full-height cranium whose round bottom *was* the silhouette, so the jaw wedge sat
    invisibly inside it and two independent reviewers both reported "round blob, no chin". The
    cranium now stops just below the cheek line, and the jaw is wider than the cranium there.

    params: rx, ry (head half-axes; the anchor box is unchanged) · cheek (jaw half-width at the
    cheek line, as a fraction of rx) · jaw (the cheek line, as a fraction of ry below cy) ·
    chin-w (chin half-width / rx) · turn (deg; rotates the jaw axis for 3/4 views)

    Exposes the ellipse handles (so `head.rx`, `head.w`, ... keep working for every node that
    measured itself against the old ellipse) plus `chin`, `cheek-y`, `jaw.left/right`.
    """
    sid = str(node["face"])
    cx, cy = ctx.point(node["at"])
    rx = ctx.scalar(node["rx"])
    ry = ctx.scalar(node.get("ry", rx))
    cheek = ctx.scalar(node.get("cheek", 0.68))
    jaw = ctx.scalar(node.get("jaw", 0.37))
    chin_w = ctx.scalar(node.get("chin-w", 0.035))
    turn = math.radians(ctx.scalar(node.get("turn", 0)))
    fill = node.get("fill")
    stroke, sw = node.get("stroke"), node.get("sw")
    z = node.get("z", "default")

    ct, st = math.cos(turn), math.sin(turn)

    def place(u: float, v: float) -> tuple[float, float]:
        """u = fraction of rx (right positive), v = fraction of ry below cy; rotated by `turn`."""
        x, y = u * rx, v * ry
        return cx + x * ct - y * st, cy + x * st + y * ct

    # The jaw silhouette: u as a fraction of `cheek` (or of rx at the top), v as a fraction of ry
    # below cy, interpolated between the cheek line and the chin. This is drawing knowledge, not a
    # per-node fudge — from the reference, the face is a broad column (half-width 64 -> 56 -> 49 ->
    # 47) that ends in a small chin point (27 -> 3.5), which is exactly what an ellipse cannot do.
    profile = ((0.00, 0.95, "rx"), (0.20, 0.80, "rx"),
               (jaw, cheek, "cheek"),
               (jaw + (1 - jaw) * 0.418, cheek * 0.766, "cheek"),
               (jaw + (1 - jaw) * 0.695, cheek * 0.734, "cheek"),
               (jaw + (1 - jaw) * 0.834, cheek * 0.421, "cheek"),
               (jaw + (1 - jaw) * 0.972, chin_w, "rx"))
    scaled = [(u, v) for v, u, _unit in profile]
    left = [place(-u, v) for u, v in reversed(scaled)]
    jaw_pts = left + [place(0.0, 1.0)] + [place(u, v) for u, v in scaled]

    # the cranium stops just past the cheek line, so the jaw below it is the silhouette
    cran_ry = ry * (1 + jaw + 0.12) / 2
    cran_cy = cy - ry + cran_ry
    emit.append({"ellipse": f"{sid}-cranium", "at": [cx, cran_cy], "rx": rx, "ry": cran_ry,
                 "rot": 0, "fill": fill, "stroke": stroke, "sw": sw, "z": z,
                 "desc": f"cranium ball — {2 * cran_ry:.0f}px tall, ending just below the cheek "
                         f"line so the jaw below it is the visible silhouette"})
    emit.append({"blob": f"{sid}-jaw", "poly": jaw_pts, "fill": fill, "stroke": stroke,
                 "sw": sw, "z": z,
                 "desc": f"jaw: from the cheek line (y=cy+{jaw:.2f}ry, half-width {cheek:.2f}rx) "
                         f"tapering to a {chin_w:.3f}rx chin"})

    anchor = ellipse_anchor(sid, cx, cy, rx, ry)
    anchor.env.update({
        f"{sid}.chinx": cx, f"{sid}.chiny": cy + ry,
        f"{sid}.cheek-y": cy + jaw * ry, f"{sid}.jaw.left": cx - cheek * rx,
        f"{sid}.jaw.right": cx + cheek * rx,
    })
    return ctx.add(anchor)


def _hair_outline(spine: list[tuple[float, float]], widths: list[float],
                  side: str = "both", zig: float = 0.0, tips: int = 0) -> list[tuple[float, float]]:
    """The silhouette of one hair mass: a per-point-width band around the gesture spine.

    `side` decides which edge the width grows from: `both` straddles the spine (a centre-line
    clump), `left`/`right` keep the spine as one edge and grow one side only. `zig`/`tips` add a
    sawtooth to the OUTER edge (windowed from the root to the tip) — the strand separation that
    keeps a mass reading as hair rather than a slab. With `zig=0` the outline is the plain tapered
    band, which is what the fitter optimises; `zig` is the drawing-time detail.
    """
    pts = [np.array(p, float) for p in spine]
    n = len(pts)
    L: list[np.ndarray] = []
    R: list[np.ndarray] = []
    normals: list[np.ndarray] = []
    for i, p in enumerate(pts):
        if i == 0:
            t = pts[1] - pts[0]
        elif i == n - 1:
            t = pts[-1] - pts[-2]
        else:
            t = pts[i + 1] - pts[i - 1]
        t = t / (np.linalg.norm(t) or 1.0)
        nrm = np.array([-t[1], t[0]])
        normals.append(nrm)
        w = float(widths[i])
        if side == "left":
            L.append(p + nrm * w)
            R.append(p.copy())
        elif side == "right":
            L.append(p.copy())
            R.append(p - nrm * w)
        else:
            L.append(p + nrm * (w / 2))
            R.append(p - nrm * (w / 2))
    if zig and n > 1 and side in ("both", "right"):
        for i in range(n):
            win = i / (n - 1)
            R[i] = R[i] + normals[i] * (zig * win * (widths[i] / 2) * (1.0 if i % 2 else -1.0))
    out = [tuple(num(v) for v in p) for p in L] + \
          [tuple(num(v) for v in p) for p in reversed(R)]
    return out


def expand_hair_mass(node: dict, ctx: Ctx, emit: list[dict]) -> Anchor:
    """A hair mass — one clump of hair as a tapered band along a gesture spine.

    The structure knowledge the model should not re-derive: hair is drawn as *clumps*, and a clump
    is a gesture (a spine of 2-4 points) whose cross-section has a width — thick at the root, often
    tapering to a tip. It is one silhouette, not a contour of vertices. Vocabulary.md sketches the
    family as "silhouette spine, width profile, tip zigzag, strand count":

      spine    the gesture (2-4 relation-valued points; the sanctioned gesture form)
      w        the width profile — one full width per spine point (or one scalar for a constant)
      side     which edge the width grows from: both (centre-line), left, or right
      tips/zig strand separation on the outer edge (a sawtooth windowed root -> tip)
      strands  interior strand lines, for the tonal structure (default 0)

    A big sweeping mass and a narrow cheek lock are two instances of this family, exactly as the
    two eyes are two `eye` instances — the family carries the structure, the spec states intent.

    Exposes the bbox handles (`cx/cy/left/right/top/bottom/w/h/w2/h2`) so later nodes can hang off
    it, plus `rootx/rooty` (the gesture's first point) and `tipx/tipy` (its last), and the outline
    itself, so `{along: hair, t}` works on the silhouette.
    """
    sid = str(node["hair-mass"])
    if "spine" not in node:
        raise SpecError(f"relate: hair-mass {sid!r} needs `spine` (2-4 points, the gesture)")
    spine = [ctx.point(p) for p in node["spine"]]
    n = len(spine)
    if not 2 <= n <= 4:
        raise SpecError(f"relate: {sid}.spine needs 2-4 points (the gesture form), got {n}")
    raw_w = node.get("w", node.get("width"))
    if raw_w is None:
        raise SpecError(f"relate: hair-mass {sid!r} needs `w` (a width or a per-point profile)")
    if isinstance(raw_w, (list, tuple)):
        widths = [ctx.scalar(v) for v in raw_w]
        if len(widths) != n:
            raise SpecError(f"relate: {sid}.w has {len(widths)} entries but the spine has {n} points")
    else:
        widths = [ctx.scalar(raw_w)] * n
    side = str(node.get("side", "both"))
    if side not in ("both", "left", "right"):
        raise SpecError(f"relate: {sid}.side must be both/left/right, got {side!r}")
    zig = ctx.scalar(node.get("zig", 0.0))
    tips = whole(node.get("tips", 0), f"{sid}.tips")
    strands = whole(node.get("strands", 0), f"{sid}.strands")
    fill = node.get("fill")
    stroke, sw = node.get("stroke"), node.get("sw")
    z = str(node.get("z", "default"))

    poly = _hair_outline(spine, widths, side=side, zig=zig, tips=tips)
    emit.append({"blob": sid, "poly": poly, "fill": fill, "stroke": stroke, "sw": sw, "z": z,
                 "desc": f"hair mass: a {n}-point gesture spine with a width profile "
                         f"({'/'.join(f'{w:.0f}' for w in widths)}), side {side}; one clump, not a "
                         f"contour"})

    # interior strand lines (tonal structure) — optional, drawn along the spine, offset laterally
    if strands > 0 and side in ("both", "right"):
        ink = node.get("ink", "#274f77")
        sw2 = ctx.scalar(node.get("strand-w", 2))
        for k in range(1, strands + 1):
            f = (k / (strands + 1)) * 2 - 1          # -1..1 across the band
            sp_sub = []
            for i, p in enumerate(spine):
                if i == 0:
                    t = np.array(spine[1]) - np.array(spine[0])
                elif i == n - 1:
                    t = np.array(spine[-1]) - np.array(spine[-2])
                else:
                    t = np.array(spine[i + 1]) - np.array(spine[i - 1])
                t = t / (np.linalg.norm(t) or 1.0)
                nrm = np.array([-t[1], t[0]])
                if side == "both":
                    base = np.array(p) - nrm * (f * widths[i] / 2)
                else:                                # right: spine is the left edge
                    base = np.array(p) - nrm * ((f + 1) / 2 * widths[i])
                sp_sub.append(tuple(num(v) for v in base))
            emit.append({"stroke": f"{sid}-strand{k}", "spine": sp_sub, "w": sw2, "ink": ink,
                         "z": z, "desc": f"interior strand line {k} of the hair mass"})

    anchor = bbox_anchor(sid, poly)
    anchor.env.update({f"{sid}.rootx": spine[0][0], f"{sid}.rooty": spine[0][1],
                       f"{sid}.tipx": spine[-1][0], f"{sid}.tipy": spine[-1][1]})
    return ctx.add(anchor)


def _spine_at(spine: list[tuple[float, float]], t: float):
    """Point + unit tangent at progress t in [0,1] along an open polyline.

    The sanctioned gesture form for a limb (scene-format.md): a 2-4 point spine whose bend IS the
    joint, rather than a hand-laid corner in a path. Shared by `arm` (elbow/wrist) and its sleeve.
    """
    pts = [np.array(p, float) for p in spine]
    segs = [pts[i + 1] - pts[i] for i in range(len(pts) - 1)]
    lens = [float(np.linalg.norm(s)) for s in segs]
    total = sum(lens) or 1.0
    d = max(0.0, min(1.0, t)) * total
    acc = 0.0
    for i, L in enumerate(lens):
        if d <= acc + L or i == len(lens) - 1:
            f = (d - acc) / (L or 1.0)
            return pts[i] + segs[i] * f, segs[i] / (L or 1.0)
        acc += L
    return pts[-1], np.array([1.0, 0.0])


def _spine_width(widths: list[float], t: float) -> float:
    """Linear interpolation of a per-point width profile at progress t in [0,1]."""
    n = len(widths)
    if n == 1:
        return float(widths[0])
    u = max(0.0, min(1.0, t)) * (n - 1)
    i = min(int(u), n - 2)
    f = u - i
    return float(widths[i] * (1 - f) + widths[i + 1] * f)


def expand_collar(node: dict, ctx: Ctx, emit: list[dict]) -> Anchor:
    """A sailor collar: a flap with a neck U/V opening and a trim band along its outer edge.

    Structure the model should not re-derive: a sailor collar is a flat flap over the shoulders
    whose outer edge is a shallow U and whose neck opening is a V notch; the navy trim is a band
    hugging that U edge. `turn` shifts the V sideways — a 3/4 view does not put the opening at the
    centre. The flap and the trim share the U edge exactly, so the two fills tile without a seam.

    params: at, w, h · neck (V half-width / w) · v (V depth / h) · trim (band width / h) ·
            turn (V centre offset in u) · tilt · fill/trim-fill
    Exposes the bbox handles plus `frontx/fronty` (the V bottom) and `neckx/necky`.
    """
    sid = str(node["collar"])
    cx, cy = ctx.point(node["at"])
    w = ctx.scalar(node["w"])
    h = ctx.scalar(node["h"])
    neck = ctx.scalar(node.get("neck", 0.46))
    v = ctx.scalar(node.get("v", 0.66))
    trim = ctx.scalar(node.get("trim", 0.20))
    turn = ctx.scalar(node.get("turn", 0.0))
    tilt = ctx.scalar(node.get("tilt", 0))
    fill = node.get("fill", "#96c3d6")
    trim_fill = node.get("trim-fill", "#374b68")
    stroke, sw = node.get("stroke"), node.get("sw")
    z = str(node.get("z", "default"))
    z_trim = str(node.get("z-trim", z))
    hw = w / 2
    ca, sa = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))

    def place(u: float, vv: float) -> tuple[float, float]:
        x, y = u * hw, vv * h
        return (cx + x * ca - y * sa, cy + x * sa + y * ca)

    def bottom_u(u: float) -> float:
        du = abs(u - turn)
        return 0.40 + 0.60 * math.cos(math.pi / 2 * min(1.0, du / 1.05))

    n = 28
    us = [-1.0 + 2.0 * i / n for i in range(n + 1)]
    bottom = [(u, bottom_u(u)) for u in us]
    body = [place(turn - neck, 0.0), place(-1.0, 0.0), place(-1.0, bottom_u(-1.0))]
    body += [place(u, vv) for u, vv in bottom]
    body += [place(1.0, 0.0), place(turn + neck, 0.0), place(turn, v)]
    trim_poly = [place(u, vv) for u, vv in bottom]
    trim_poly += [place(u, max(0.0, vv - trim)) for u, vv in reversed(bottom)]

    emit.append({"blob": f"{sid}-body", "poly": body, "fill": fill, "stroke": stroke,
                 "sw": sw, "z": z,
                 "desc": f"collar flap: {w:.0f}px shoulder span with a neck V ({neck:.2f} wide, "
                         f"{v:.2f} deep) shifted {turn:+.2f} for the 3/4 view"})
    emit.append({"blob": f"{sid}-trim", "poly": trim_poly, "fill": trim_fill, "z": z_trim,
                 "desc": "collar trim: the navy band along the flap's outer U edge"})
    anchor = bbox_anchor(sid, body)
    fx, fy = place(turn, v)
    anchor.env.update({f"{sid}.frontx": fx, f"{sid}.fronty": fy,
                       f"{sid}.neckx": cx - neck * hw * ca, f"{sid}.necky": cy - neck * hw * sa})
    return ctx.add(anchor)


def expand_bow(node: dict, ctx: Ctx, emit: list[dict]) -> Anchor:
    """A ribbon bow: two pinched loops, a knot, and tails.

    Structure: a bow's loops meet AT the knot and pinch there (a loop is not an ellipse floating
    beside a box); the knot wraps the middle; the ribbon ends leave the knot as tapered tails.
    Loop angles are screen degrees from the knot (0 = right, 90 = down), so a 3/4 view is stated
    directly — the reference's loops are ~129deg apart about an up axis, not a symmetric 180.

    params: at, w, h · spread (deg between the loop axes) · tilt · loop-len (reach / (w/2)) ·
            loop-w (half-width / (h/2)) · knot-w, knot-h · tail-angle/len/w · tail2-* ·
            loop-fill/knot-fill/tail-fill
    Exposes bbox + `knot.*` + `tail-tipx/tipy`.
    """
    sid = str(node["bow"])
    cx, cy = ctx.point(node["at"])
    w = ctx.scalar(node["w"])
    h = ctx.scalar(node["h"])
    spread = ctx.scalar(node.get("spread", 128))
    tilt = ctx.scalar(node.get("tilt", -90))
    loop_len = ctx.scalar(node.get("loop-len", 0.95))
    loop_w = ctx.scalar(node.get("loop-w", 0.95))
    knot_w = ctx.scalar(node.get("knot-w", 0.20)) * w
    knot_h = ctx.scalar(node.get("knot-h", 0.85)) * h
    loop_fill = node.get("loop-fill", node.get("fill", "#d35081"))
    knot_fill = node.get("knot-fill", "#c04a78")
    stroke, sw = node.get("stroke"), node.get("sw")
    z = str(node.get("z", "default"))
    reach = loop_len * (w / 2)
    half_w = loop_w * (h / 2)
    knot = np.array([cx, cy])

    def loop_poly(ang_deg: float) -> list[tuple[float, float]]:
        a = math.radians(ang_deg)
        d = np.array([math.cos(a), math.sin(a)])
        p = np.array([-d[1], d[0]])
        tip = knot + d * reach
        top = bez3(tuple(knot), tuple(knot + d * (reach * 0.42) + p * half_w),
                   tuple(tip + p * half_w * 0.5), tuple(tip))
        bot = bez3(tuple(tip), tuple(tip - p * half_w * 0.5),
                   tuple(knot + d * (reach * 0.42) - p * half_w), tuple(knot))
        return [tuple(q) for q in top + bot[1:]]

    for name, ang in (("loop1", tilt - spread / 2), ("loop2", tilt + spread / 2)):
        emit.append({"blob": f"{sid}-{name}", "poly": loop_poly(ang), "fill": loop_fill,
                     "stroke": stroke, "sw": sw, "z": z,
                     "desc": f"bow loop at {ang:+.0f}deg from the knot — pinched at the knot, "
                             f"not a floating ellipse"})
    emit.append({"ellipse": f"{sid}-knot", "at": [cx, cy], "rx": knot_w / 2, "ry": knot_h / 2,
                 "rot": tilt, "fill": knot_fill, "z": z,
                 "desc": "bow knot: the wrap where both loops and the tails meet"})

    def tail(name: str, ang: float, length: float, width: float, fill) -> None:
        a = math.radians(ang)
        d = np.array([math.cos(a), math.sin(a)])
        p = np.array([-d[1], d[0]])
        mid = knot + d * (length * 0.5) + p * (width * 0.20)
        tip = knot + d * length + p * (width * 0.06)
        poly = taper_band([tuple(knot + d * (knot_w * 0.2)), tuple(mid), tuple(tip)],
                          [width * 0.55, width, width * 0.42], "both")
        emit.append({"blob": f"{sid}-{name}", "poly": poly, "fill": fill, "stroke": stroke,
                     "sw": sw, "z": z,
                     "desc": f"bow tail at {ang:+.0f}deg — a ribbon end leaving the knot"})

    tail("tail1", ctx.scalar(node.get("tail-angle", 122)),
         ctx.scalar(node.get("tail-len", 0.6 * h)),
         ctx.scalar(node.get("tail-w", 0.42 * h)), node.get("tail-fill", loop_fill))
    if ctx.scalar(node.get("tail2-len", 0.0)) > 0:
        tail("tail2", ctx.scalar(node.get("tail2-angle", 90)),
             ctx.scalar(node.get("tail2-len", 0.0)),
             ctx.scalar(node.get("tail2-w", 0.2 * h)),
             node.get("tail2-fill", "#2f3c58"))

    pts = loop_poly(tilt - spread / 2) + loop_poly(tilt + spread / 2)
    anchor = bbox_anchor(sid, pts)
    return ctx.add(anchor)


def expand_arm(node: dict, ctx: Ctx, emit: list[dict]) -> Anchor:
    """An arm: a bent limb (shoulder -> elbow -> wrist) carrying a puff sleeve and a cuff.

    Structure: the limb is a tapered band along a 2-3 point gesture spine (the elbow is a spine
    point, not a corner in a path); the sleeve is a puff over the shoulder end of the same spine,
    widest at the shoulder and gathered where the cuff wraps; the cuff is a band across the spine
    at the sleeve's end. All three share the spine, so an arm, its sleeve and its cuff cannot
    drift apart. The three are emitted as `-limb`, `-sleeve` and `-cuff` sub-shapes.

    params: spine (2-3 points) · w (per-point width) · side · sleeve (fraction under the sleeve) ·
            puff (extra half-width at the shoulder) · cuff-h, cuff-at, cuff-pad ·
            fill/sleeve-fill/cuff-fill
    Exposes bbox + shoulder/elbow/wrist/cuff handles.
    """
    sid = str(node["arm"])
    spine = [ctx.point(p) for p in node["spine"]]
    n = len(spine)
    if not 2 <= n <= 3:
        raise SpecError(f"relate: {sid}.spine needs 2-3 points (shoulder, elbow, wrist), got {n}")
    raw_w = node.get("w")
    if raw_w is None:
        raise SpecError(f"relate: arm {sid!r} needs `w` (a width or per-point profile)")
    if isinstance(raw_w, (list, tuple)):
        widths = [ctx.scalar(q) for q in raw_w]
        if len(widths) != n:
            raise SpecError(f"relate: {sid}.w has {len(widths)} entries but the spine has {n} points")
    else:
        widths = [ctx.scalar(raw_w)] * n
    side = str(node.get("side", "both"))
    if side not in ("both", "left", "right"):
        raise SpecError(f"relate: {sid}.side must be both/left/right, got {side!r}")
    sleeve = ctx.scalar(node.get("sleeve", 0.0))
    puff = ctx.scalar(node.get("puff", 0.6))
    cuff_h = ctx.scalar(node.get("cuff-h", 0.0))
    cuff_at = ctx.scalar(node.get("cuff-at", sleeve))
    cuff_pad = ctx.scalar(node.get("cuff-pad", 0.0))
    skin_fill = node.get("fill", "#d7decc")
    sleeve_fill = node.get("sleeve-fill", "#e1e7dc")
    cuff_fill = node.get("cuff-fill", "#2d3b58")
    stroke, sw = node.get("stroke"), node.get("sw")
    z = str(node.get("z", "default"))
    z_sleeve = str(node.get("z-sleeve", z))
    z_cuff = str(node.get("z-cuff", z))

    limb = taper_band(spine, widths, side)
    emit.append({"blob": f"{sid}-limb", "poly": limb, "fill": skin_fill, "stroke": stroke,
                 "sw": sw, "z": z,
                 "desc": f"arm limb: {n}-point gesture spine, width profile "
                         f"{'/'.join(f'{x:.0f}' for x in widths)}"})
    if sleeve > 0:
        k = 14
        sub, swid = [], []
        for i in range(k + 1):
            t = sleeve * i / k
            p, _tan = _spine_at(spine, t)
            sub.append(tuple(p))
            swid.append(_spine_width(widths, t) * (1 + puff * (1 - i / k)))
        emit.append({"blob": f"{sid}-sleeve", "poly": taper_band(sub, swid, "both"),
                     "fill": sleeve_fill, "stroke": stroke, "sw": sw, "z": z_sleeve,
                     "desc": f"puff sleeve over the first {sleeve:.2f} of the limb, "
                             f"{puff:.2f} wider than the arm at the shoulder"})
    if cuff_h > 0:
        p, tan = _spine_at(spine, cuff_at)
        perp = np.array([-tan[1], tan[0]])
        hw2 = _spine_width(widths, cuff_at) / 2 + cuff_pad
        emit.append({"blob": f"{sid}-cuff",
                     "poly": [tuple(p + perp * hw2 - tan * (cuff_h / 2)),
                              tuple(p + perp * hw2 + tan * (cuff_h / 2)),
                              tuple(p - perp * hw2 + tan * (cuff_h / 2)),
                              tuple(p - perp * hw2 - tan * (cuff_h / 2))],
                     "fill": cuff_fill, "z": z_cuff,
                     "desc": f"cuff band {cuff_h:.0f}px tall across the limb at t={cuff_at:.2f}"})
    anchor = bbox_anchor(sid, limb)
    anchor.env.update({f"{sid}.shoulderx": spine[0][0], f"{sid}.shouldery": spine[0][1],
                       f"{sid}.wristx": spine[-1][0], f"{sid}.wristy": spine[-1][1]})
    if n >= 3:
        anchor.env[f"{sid}.elbowx"] = spine[1][0]
        anchor.env[f"{sid}.elbowy"] = spine[1][1]
    cp, _ = _spine_at(spine, cuff_at)
    anchor.env[f"{sid}.cuffx"] = num(cp[0])
    anchor.env[f"{sid}.cuffy"] = num(cp[1])
    return ctx.add(anchor)


def expand_hand(node: dict, ctx: Ctx, emit: list[dict]) -> Anchor:
    """A simple readable hand: a palm mass with finger lobes and a thumb.

    Structure: a hand reads as a palm with separated fingers — one blob reads as a mitten. The
    family draws the palm and `fingers` lobes along the finger direction plus a thumb on the
    `thumb` side, all flat cel shapes. `at` is the palm centre, `tilt` the finger direction.

    params: at, w, h · tilt · fingers (2-4) · spread (deg) · thumb (0/1) · fill
    Exposes bbox + `tipx/tipy`.
    """
    sid = str(node["hand"])
    cx, cy = ctx.point(node["at"])
    w = ctx.scalar(node["w"])
    h = ctx.scalar(node["h"])
    tilt = ctx.scalar(node.get("tilt", 90))
    fingers = whole(node.get("fingers", 3), f"{sid}.fingers")
    spread = ctx.scalar(node.get("spread", 24))
    thumb = whole(node.get("thumb", 1), f"{sid}.thumb")
    fill = node.get("fill", "#e8d7bd")
    stroke, sw = node.get("stroke"), node.get("sw")
    z = str(node.get("z", "default"))
    a = math.radians(tilt)
    d = np.array([math.cos(a), math.sin(a)])
    parts: list[tuple[str, np.ndarray, float, float, float]] = [
        ("palm", np.array([cx, cy]), 0.34 * w, 0.40 * h, tilt)]
    for i in range(max(0, min(4, fingers))):
        fa = tilt + (i - (fingers - 1) / 2) * spread
        fd = np.array([math.cos(math.radians(fa)), math.sin(math.radians(fa))])
        c = np.array([cx, cy]) + d * (h * 0.36) + fd * (h * 0.14)
        parts.append((f"finger{i + 1}", c, 0.11 * w, 0.22 * h, fa))
    if thumb:
        ta = tilt - 80
        td = np.array([math.cos(math.radians(ta)), math.sin(math.radians(ta))])
        c = np.array([cx, cy]) + td * (w * 0.36)
        parts.append(("thumb", c, 0.12 * w, 0.24 * h, ta))
    for name, c, rx, ry, rot in parts:
        emit.append({"ellipse": f"{sid}-{name}", "at": [float(c[0]), float(c[1])],
                     "rx": float(rx), "ry": float(ry), "rot": float(rot), "fill": fill,
                     "stroke": stroke, "sw": sw, "z": z,
                     "desc": f"hand {name} lobe"})
    xs = [cx - w / 2, cx + w / 2]
    ys = [cy - h / 2, cy + h / 2]
    anchor = bbox_anchor(sid, [(x, y) for x in xs for y in ys])
    tip = np.array([cx, cy]) + d * (h * 0.55)
    anchor.env.update({f"{sid}.tipx": num(tip[0]), f"{sid}.tipy": num(tip[1])})
    return ctx.add(anchor)


VOCAB = {"sunhat": expand_sunhat, "eye": expand_eye, "face": expand_face,
         "hair-mass": expand_hair_mass, "collar": expand_collar, "bow": expand_bow,
         "arm": expand_arm, "hand": expand_hand}
SHAPES = ("ellipse", "blob", "stroke", "rect")
# `region` is a computed shape: its outline is flooded from the reference raster at resolve time,
# so it is a TEACHER node and needs `--ref`. It is listed apart from the primitives because it
# has no authored geometry at all (only a seed, a tolerance and an optional clip box).
COMPUTED = ("region",)
# `traced` is the REMOVABLE form of a computed shape: its outline was computed once by the
# teacher (a `region` flood) and frozen to a sidecar data file, so it never opens a raster.
# A spec full of `traced` nodes is reference-free (P18 / invariant 6); it is a normal anchor,
# so later nodes can hang off it exactly as they could off the `region` it replaces (roadmap D20).
TRACED = ("traced",)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_traced(path: Path, rel: str, base_dir: Path) -> list[tuple[float, float]]:
    """Load frozen vertices written by `draw freeze`; refuse a stale or malformed sidecar.

    The frozen data is the teacher made removable. It records the sha256 of the raster it was
    traced from, so a changed reference is caught loudly instead of silently rendering yesterday's
    geometry (D20). A missing raster is the *reference-free* case and is fine — the frozen
    vertices are self-contained, which is the whole point of materializing them.
    """
    try:
        text = path.read_text()
    except OSError as exc:
        raise SpecError(
            f"relate: traced node references {rel!r} but the frozen file is missing ({path}): "
            f"{exc}. Run `scripts/draw freeze <spec> --ref <image>` to materialize it.") from exc
    try:
        data = json.loads(text)
    except ValueError as exc:
        raise SpecError(f"relate: traced file {path} is malformed JSON: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("vertices"), list) or not data["vertices"]:
        raise SpecError(f"relate: traced file {path} is malformed: expected a non-empty `vertices` list")
    img, recorded = data.get("image"), data.get("image_sha256")
    if img and recorded:
        img_path = Path(img)
        if not img_path.is_absolute():
            img_path = base_dir / img_path
        if img_path.exists():
            actual = sha256_file(img_path)
            if actual != recorded:
                raise SpecError(
                    f"relate: traced file {path} is STALE: it was frozen from {img!r} at "
                    f"{str(recorded)[:12]}…, but that raster is now {actual[:12]}… . The frozen "
                    f"geometry no longer matches its source; re-run `scripts/draw freeze`. "
                    f"(A silently stale trace is worse than no trace.)")
    poly: list[tuple[float, float]] = []
    for i, p in enumerate(data["vertices"]):
        if not isinstance(p, (list, tuple)) or len(p) != 2:
            raise SpecError(f"relate: traced file {path}: vertex {i} is not [x, y]: {p!r}")
        poly.append((num(p[0], f"{path} vertex x"), num(p[1], f"{path} vertex y")))
    return poly


def freeze(spec: dict, *, spec_path: Path, ref_path: str, ref_bgr,
           out_dir: str | None = None) -> list[tuple[str, Path, int]]:
    """Materialize every `region` node's computed outline into a sidecar data file (D20).

    Resolves the spec with the reference OPEN, then writes each region's vertices plus
    provenance — node id, the seed/tol/eps used, source raster, its sha256, the date and the
    code path that produced it — to <spec-dir>/traced/<node>.json. The spec can then swap each
    `region` for a `traced` node that reads the sidecar and never opens a raster.
    """
    emit, _env, _notes, _layers = resolve(spec, ref=ref_bgr, base_dir=spec_path.parent)
    image_sha = sha256_file(Path(ref_path))
    base = os.path.abspath(spec_path.parent)
    try:
        image_rel = os.path.relpath(os.path.abspath(ref_path), base)
    except ValueError:  # different drive on some platforms
        image_rel = os.path.abspath(ref_path)
    today = datetime.date.today().isoformat()
    out = Path(out_dir) if out_dir else spec_path.parent / "traced"
    written: list[tuple[str, Path, int]] = []
    for node in emit:
        if "region" not in node:
            continue
        sid = str(node["region"])
        payload = {
            "version": 1,
            "node": sid,
            "kind": "region",
            "spec": str(spec_path),
            "image": image_rel,
            "image_sha256": image_sha,
            "date": today,
            "seed": [num(v) for v in node.get("seed", [])],
            "tol": node.get("tol"),
            "fixed": node.get("fixed"),
            "eps": node.get("eps"),
            "box": node.get("box"),
            "method": "scripts/relate.py:resolve(kind=region) -> "
                      "scripts/scene_render.py:flood_region(fixed-range) -> cv2.approxPolyDP",
            "vertex_count": len(node["poly"]),
            "vertices": [[num(p[0]), num(p[1])] for p in node["poly"]],
        }
        out.mkdir(parents=True, exist_ok=True)
        dest = out / f"{sid}.json"
        write_text(dest, json.dumps(payload, indent=1) + "\n")
        written.append((sid, dest, len(node["poly"])))
    return written


# --------------------------------------------------------------------------------------
# resolve
# --------------------------------------------------------------------------------------
def resolve(spec: dict, ref=None, base_dir=None) -> tuple[list[dict], dict[str, float], list[str], list[str]]:
    if not isinstance(spec, dict):
        raise SpecError("relate: spec must be a mapping with `frame` and `draw`")
    if "frame" not in spec or "draw" not in spec:
        raise SpecError("relate: spec needs both `frame` and `draw`")
    frame = spec["frame"]
    if not isinstance(frame, dict) or "w" not in frame or "h" not in frame:
        raise SpecError("relate: `frame` needs w and h")
    base = Path(base_dir) if base_dir else Path(".")
    ctx = Ctx({k: num(v, f"frame.{k}") for k, v in frame.items()})
    # named intermediate scalars — a drawing wants to say "head_half" once, not 0.098 frame widths
    raw_vars = spec.get("vars", {}) or {}
    if not isinstance(raw_vars, dict):
        raise SpecError("relate: `vars` must be a mapping of name -> expression")
    for name, expr in raw_vars.items():
        if not isinstance(name, str) or "." in name:
            raise SpecError(f"relate: var name must be a plain identifier, got {name!r}")
        ctx.env[name] = ctx.scalar(expr)
    emit: list[dict] = []

    for raw in spec["draw"]:
        if not isinstance(raw, dict) or not raw:
            raise SpecError(f"relate: every draw node must be a non-empty mapping, got {raw!r}")
        kind = next(iter(raw))
        if kind in VOCAB:
            VOCAB[kind](raw, ctx, emit)
            continue
        if kind not in SHAPES and kind not in COMPUTED and kind not in TRACED:
            raise SpecError(f"relate: unknown node kind {kind!r}; known: "
                            f"{sorted(VOCAB) + list(SHAPES) + list(COMPUTED) + list(TRACED)}")
        sid = str(raw[kind])

        if kind == "traced":
            # A region whose outline was computed once by the teacher and FROZEN to a sidecar data
            # file (roadmap D20). It is a normal anchor, and it never opens a raster, so a spec
            # full of `traced` nodes renders with the reference deleted (P18 / invariant 6).
            if "from" not in raw:
                raise SpecError(f"relate: traced {sid!r} needs `from:` (a frozen sidecar data file)")
            rel = str(raw["from"])
            path = Path(rel)
            if not path.is_absolute():
                path = base / path
            poly = load_traced(path, rel, base)
            ctx.add(bbox_anchor(sid, poly))
            emit.append({"traced": sid, "poly": poly, "fill": raw.get("fill"),
                         "stroke": raw.get("stroke"), "sw": raw.get("sw"),
                         "z": raw.get("z", "default"), "desc": raw.get("desc", "")})
            continue

        if kind == "region":
            # "This shape is the reference's <colour> area around <seed>, clipped to <box>."
            # The seed and box are ordinary relations, so the node carries ZERO typed
            # coordinates; the reference supplies the outline. Teacher-only: without a raster
            # there is nothing to flood, and an M5 reference-free spec must not contain it.
            if ref is None:
                raise SpecError(f"relate: region {sid!r} needs the reference raster (--ref); "
                                f"region is teacher-only and may not appear in a reference-free spec")
            seed = ctx.point(raw["seed"])
            tol = ctx.scalar(raw.get("tol", 30))
            box = raw.get("box")
            if box is not None:
                if not isinstance(box, (list, tuple)) or len(box) != 4:
                    raise SpecError(f"relate: region {sid!r} box must be [x0, y0, x1, y1]")
                box = [ctx.scalar(v) for v in box]
            fixed = bool(raw.get("fixed", False))
            eps = ctx.scalar(raw.get("eps", 6))
            try:
                poly = [tuple(p) for p in flood_region(ref, seed, tol, fixed=fixed, box=box,
                                                        eps=eps)]
            except ValueError as exc:
                raise SpecError(f"relate: region {sid!r}: {exc}") from exc
            ctx.add(bbox_anchor(sid, poly))
            ctx.teacher.append(sid)
            emit.append({"region": sid, "poly": poly, "fill": raw.get("fill"),
                         "z": raw.get("z", "default"), "desc": raw.get("desc", ""),
                         "seed": list(seed), "tol": tol, "fixed": fixed, "eps": eps, "box": box})
            continue

        if kind == "ellipse":
            at = ctx.point(raw["at"])
            rx = ctx.scalar(raw["rx"])
            ry = ctx.scalar(raw.get("ry", raw["rx"]))
            rot = ctx.scalar(raw.get("rot", 0))
            ctx.add(ellipse_anchor(sid, at[0], at[1], rx, ry, rot))
            emit.append({"ellipse": sid, "at": list(at), "rx": rx, "ry": ry, "rot": rot,
                         "fill": raw.get("fill"), "stroke": raw.get("stroke"), "sw": raw.get("sw"),
                         "z": raw.get("z", "default"), "desc": raw.get("desc", "")})
        elif kind == "blob":
            # Two legitimate blob forms, matching scene-format.md: a closed `poly`, or an open
            # `spine` (+ `w`) ribbon. A closed shape (blouse, skirt panel, brim slice) has no
            # spine, and demanding one made those shapes unexpressible in the front end while the
            # back end accepted them — the dialect mismatch that crashed the full-figure spec.
            if "poly" in raw:
                poly = [ctx.point(p) for p in raw["poly"]]
            elif "spine" in raw:
                spine = [ctx.point(p) for p in raw["spine"]]
                width = ctx.scalar(raw.get("w", 0))
                poly = ribbon(spine, width) if width else spine
            else:
                raise SpecError(f"relate: blob {sid!r} needs `poly` (closed polygon) "
                                f"or `spine` (+ `w`)")
            ctx.add(bbox_anchor(sid, poly))
            emit.append({"blob": sid, "poly": poly, "fill": raw.get("fill"),
                         "stroke": raw.get("stroke"), "sw": raw.get("sw"),
                         "z": raw.get("z", "default"), "desc": raw.get("desc", "")})
        elif kind == "stroke":
            spine = [ctx.point(p) for p in raw["spine"]]
            ctx.add(bbox_anchor(sid, spine))
            emit.append({"stroke": sid, "spine": spine, "w": ctx.scalar(raw.get("w", 4)),
                         "ink": raw.get("ink"), "z": raw.get("z", "default"),
                         "desc": raw.get("desc", "")})
        else:  # rect
            if raw.get("full"):
                emit.append({"rect": sid, "full": True, "fill": raw.get("fill"),
                             "z": raw.get("z", "default"), "desc": raw.get("desc", "")})
                continue
            at = ctx.point(raw["at"])
            w = ctx.scalar(raw["w"])
            h = ctx.scalar(raw["h"])
            ctx.add(bbox_anchor(sid, [(at[0] - w / 2, at[1] - h / 2), (at[0] + w / 2, at[1] + h / 2)]))
            emit.append({"rect": sid, "at": list(at), "w": w, "h": h, "fill": raw.get("fill"),
                         "z": raw.get("z", "default"), "desc": raw.get("desc", "")})

    layers = [str(x) for x in spec.get("layers", [])]
    notes = check_intent(spec, layers) + diagnose(emit, layers, ctx)
    for tid in ctx.teacher:
        notes.append(f"TEACHER     {tid}: geometry computed from the reference raster — legal while "
                     f"the reference is open, forbidden in a reference-free (M5) spec (P18)")
    return emit, ctx.env, notes, layers


# --------------------------------------------------------------------------------------
# semantic diagnostics — the model has no numeric sense of a 1024^2 canvas; this is its ruler
# --------------------------------------------------------------------------------------
def _sid(node: dict) -> str:
    for key, val in node.items():
        if key != "desc" and isinstance(val, (str, bool)):
            return str(val)
    return "?"


def _bbox(node: dict, ctx: Ctx) -> tuple[float, float, float, float] | None:
    shape = ctx.anchors.get(_sid(node))
    if shape and shape._outline:
        xs = [p[0] for p in shape._outline]
        ys = [p[1] for p in shape._outline]
        return (min(xs), min(ys), max(xs), max(ys))
    if "at" in node and "rx" in node:
        at, rx, ry = node["at"], node["rx"], node.get("ry", node["rx"])
        return (at[0] - rx, at[1] - ry, at[0] + rx, at[1] + ry)
    return None


def diagnose(emit: list[dict], layers: list[str], ctx: Ctx) -> list[str]:
    width, height = ctx.env["frame.w"], ctx.env["frame.h"]
    notes: list[str] = []
    for node in emit:
        box = _bbox(node, ctx)
        if not box:
            continue
        sid = _sid(node)
        x0, y0, x1, y1 = box
        span = (x0, y0, x1, y1)
        if x1 < 0 or y1 < 0 or x0 > width or y0 > height:
            notes.append(f"OFF-CANVAS  {sid}: ({span[0]:.0f},{span[1]:.0f})-({span[2]:.0f},{span[3]:.0f}) lies entirely outside the frame")
        elif x0 < 0 or y0 < 0 or x1 > width or y1 > height:
            notes.append(f"CLIPPED     {sid}: ({span[0]:.0f},{span[1]:.0f})-({span[2]:.0f},{span[3]:.0f}) crosses the frame edge")
        if (x1 - x0) < 3 or (y1 - y0) < 3:
            notes.append(f"SUB-PIXEL   {sid}: {x1 - x0:.1f}x{y1 - y0:.1f}px — below the perceptible size")
    return notes


def check_intent(spec: dict, layers: list[str]) -> list[str]:
    """Verify declared occlusion intent against the actual paint order.

    The model states what should be in front in words; the engine checks whether the layer
    stack agrees. Silence here is the interesting case: it means intent and render agree.
    """
    notes: list[str] = []
    for rel in spec.get("relations", []) or []:
        if not isinstance(rel, dict) or "front" not in rel or "behind" not in rel:
            raise SpecError(f"relate: each relation needs `front` and `behind`, got {rel!r}")
        front, behind = str(rel["front"]), str(rel["behind"])
        if not layers:
            continue
        zf = _layer_of(front, spec)
        zb = _layer_of(behind, spec)
        if zf is None or zb is None:
            notes.append(f"UNKNOWN-Z   relation {front} in front of {behind}: one has no `z` in the spec")
            continue
        if layers.index(zf) < layers.index(zb):
            notes.append(f"CONTRADICTION  you declared {front} in front of {behind}, but layer order "
                         f"paints {zf} before {zb} -> {behind} wins. Fix the `layers` list or the node's `z`.")
    return notes


def _layer_of(sid: str, spec: dict) -> str | None:
    for raw in spec["draw"]:
        if not isinstance(raw, dict):
            continue
        for key, val in raw.items():
            if key == "desc":
                continue
            if isinstance(val, str) and val == sid:
                return str(raw.get("z", "default"))
    return None


# --------------------------------------------------------------------------------------
# emit
# --------------------------------------------------------------------------------------
def emit_svg(emit: list[dict], layers: list[str], frame: dict[str, float]) -> str:
    width, height = frame["w"], frame["h"]

    def zindex(node: dict) -> int:
        z = str(node.get("z", "default"))
        return layers.index(z) if z in layers else len(layers)

    order = sorted((n for n in emit if not n.get("full")), key=zindex)
    order = [n for n in emit if n.get("full")] + order
    body: list[str] = []
    for node in order:
        comment = f'<!-- {node.get("desc")} -->' if node.get("desc") else ""
        if "rect" in node and node.get("full"):
            body.append(f'{comment}<rect x="0" y="0" width="{width}" height="{height}" fill="{node.get("fill")}"/>')
        elif "region" in node or "traced" in node:
            fill = node.get("fill") or "none"
            body.append(f'{comment}<path d="{smooth_path(node["poly"], closed=True)}" fill="{fill}"/>')
        elif "ellipse" in node:
            at, rx, ry = node["at"], node["rx"], node["ry"]
            rot = node.get("rot", 0)
            tr = f' transform="rotate({rot} {at[0]:.1f} {at[1]:.1f})"' if rot else ""
            stroke = f' stroke="{node["stroke"]}" stroke-width="{node.get("sw", 2)}"' if node.get("stroke") else ""
            body.append(f'{comment}<ellipse cx="{at[0]:.1f}" cy="{at[1]:.1f}" rx="{rx:.1f}" '
                        f'ry="{ry:.1f}" fill="{node.get("fill")}"{stroke}{tr}/>')
        elif "blob" in node:
            pts = ribbon(node["spine"], node["w"]) if node.get("w") else node["poly"]
            fill = node.get("fill") or "none"
            stroke = (f' stroke="{node["stroke"]}" stroke-width="{node.get("sw", 2)}"'
                      if node.get("stroke") else "")
            if node.get("fill") is None and not node.get("stroke"):
                stroke = ' stroke="#101820" stroke-width="2"'
            body.append(f'{comment}<path d="{smooth_path(pts, closed=True)}" fill="{fill}"{stroke}/>')
        elif "stroke" in node:
            body.append(f'{comment}<path d="{smooth_path(node["spine"], closed=False)}" fill="none" '
                        f'stroke="{node.get("ink")}" stroke-width="{node["w"]:.1f}" stroke-linecap="round"/>')
    return "\n".join(
        [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
         f'width="{width}" height="{height}">']
        + body + ["</svg>"]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="resolve a relational drawing spec to a render")
    parser.add_argument("spec")
    parser.add_argument("-o", "--out", default=None)
    parser.add_argument("--anchors", action="store_true", help="print the resolved anchor table")
    parser.add_argument("--ref", default=None,
                        help="reference raster for computed `region` nodes (teacher-only)")
    parser.add_argument("--freeze", action="store_true",
                        help="materialize every `region` node into a `traced` sidecar (needs --ref)")
    parser.add_argument("--outdir", default=None,
                        help="freeze: sidecar directory (default: <spec-dir>/traced)")
    args = parser.parse_args()

    spec = load_yaml(Path(args.spec))
    if not isinstance(spec, dict):
        raise SpecError("relate: spec must be a mapping")
    ref = None
    if args.ref:
        import cv2
        ref = cv2.imread(args.ref)
        if ref is None:
            raise SpecError(f"relate: cannot read reference raster {args.ref}")

    if args.freeze:
        if ref is None:
            raise SpecError("relate: --freeze needs --ref: there is nothing to materialize "
                            "without the reference raster")
        written = freeze(spec, spec_path=Path(args.spec), ref_path=args.ref, ref_bgr=ref,
                         out_dir=args.outdir)
        if not written:
            raise SpecError("relate: --freeze found no `region` nodes in the spec; nothing to freeze")
        for sid, dest, n in written:
            print(f"froze {sid:20s} {n:5d} vertices -> {dest}")
        return

    if not args.out:
        raise SpecError("relate: -o/--out is required unless --freeze is given")
    emit, env, notes, layers = resolve(spec, ref=ref, base_dir=Path(args.spec).parent)
    frame = spec["frame"]

    svg = emit_svg(emit, layers, frame)
    svg_path = Path(args.out).with_suffix(".svg")
    write_text(svg_path, svg)
    size = (whole(frame["w"], "frame.w"), whole(frame["h"], "frame.h"))
    chrome(str(svg_path), args.out, size)

    print(f"resolved {len(emit)} nodes across {len(layers) or 1} layer(s) -> {args.out}")
    if args.anchors:
        print("\nanchors:")
        for key in sorted(env):
            print(f"  {key:28s} {env[key]:9.2f}")
    print("\ndiagnostics:" if notes else "\ndiagnostics: none")
    for note in notes:
        print("  " + note)


if __name__ == "__main__":
    main()
