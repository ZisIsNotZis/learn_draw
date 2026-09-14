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
import math
from pathlib import Path

import numpy as np
import yaml

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from scene_render import chrome, smooth_path  # noqa: E402

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
        raise SpecError(f"relate: unknown relation keys {sorted(value)}")


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
def expand_sunhat(node: dict, ctx: Ctx, emit: list[dict]) -> Anchor:
    """A wide-brim hat from ~6 parameters.

    The structure knowledge the model should not have to re-derive: a wide brim seen at an
    angle is a squashed ellipse; the crown is a dome sitting up the brim's own normal; the
    near edge of the brim is drawn OVER the crown (a z-plane split, not a path split).
    """
    sid = str(node["sunhat"])
    host_id = str(node["host"])
    host = ctx.shape(host_id)

    brim_w = ctx.scalar(node["brim"])
    tilt = ctx.scalar(node.get("tilt", 0))
    crown_w = ctx.scalar(node["crown"])
    flat = ctx.scalar(node.get("flat", 0.30))
    drop = ctx.scalar(node.get("drop", 0.62))
    lift = ctx.scalar(node.get("lift", 0.42))
    z = str(node.get("z", "hat"))
    z_front = str(node.get("z-front", z))

    brim_rx = brim_w / 2
    brim_ry = brim_rx * flat
    bx = host.env[f"{host_id}.cx"]
    by = host.env[f"{host_id}.cy"] - host.env[f"{host_id}.h2"] * lift
    brim = ctx.add(ellipse_anchor(f"{sid}-brim", bx, by, brim_rx, brim_ry, tilt))

    crown_rx = crown_w / 2
    crown_ry = ctx.scalar(node.get("crown-h", 0.62)) * crown_rx
    # step `drop` crown-radii up the brim's own normal, i.e. rotate local -Y by tilt
    a = math.radians(tilt)
    dist = crown_ry * drop
    dome = ctx.add(ellipse_anchor(f"{sid}-dome", bx + dist * math.sin(a), by - dist * math.cos(a),
                                  crown_rx, crown_ry, tilt))

    emit += [
        {"ellipse": f"{sid}-brim", "at": [bx, by], "rx": brim_rx, "ry": brim_ry, "rot": tilt,
         "fill": node.get("brim-fill", "#3b7f92"), "z": z,
         "desc": f"brim: a flat disc seen at {tilt:+.0f}deg -> ellipse {brim_w:.0f} wide, "
                 f"{2 * brim_ry:.0f} deep"},
        {"ellipse": f"{sid}-dome", "at": [dome.env[f'{sid}-dome.cx'], dome.env[f'{sid}-dome.cy']],
         "rx": crown_rx, "ry": crown_ry, "rot": tilt,
         "fill": node.get("crown-fill", "#32405b"), "stroke": node.get("crown-stroke"),
         "sw": node.get("crown-sw"),
         "z": z, "desc": f"crown: dome {drop:.2f} crown-radii up the brim normal"},
    ]

    # near edge of the brim, painted over the dome — this is what makes it read as a hat
    front = node.get("front", [0.05, 0.45])
    if not isinstance(front, (list, tuple)) or len(front) != 2:
        raise SpecError(f"relate: {sid}.front must be [t0, t1], got {front!r}")
    t0, t1 = ctx.scalar(front[0]), ctx.scalar(front[1])
    arc = [brim.on(t0 + (t1 - t0) * i / 40) for i in range(41)]
    emit.append({"blob": f"{sid}-front-rim", "spine": arc,
                 "w": ctx.scalar(node.get("rim-w", 0.05)) * brim_rx,
                 "fill": node.get("rim-fill", "#4d94a6"), "z": z_front,
                 "desc": "near brim edge, over the dome (near edge occludes the crown)"})

    for i in range(whole(node.get("pom", 0), f"{sid}.pom")):
        poms = node.get("pom-at", [0.62, 0.88])
        if i >= len(poms):
            raise SpecError(f"relate: {sid} asked for {node.get('pom')} poms but pom-at has {len(poms)} entries")
        t = ctx.scalar(poms[i])
        px, py = brim.on(t)
        r = ctx.scalar(node.get("pom-r", 0.09)) * brim_rx
        emit.append({"ellipse": f"{sid}-pom{i + 1}", "at": [px, py], "rx": r, "ry": r * 0.86,
                     "fill": node.get("pom-fill", "#df9199"), "z": z,
                     "desc": f"pom at t={t:.2f} along the brim outline, r={r:.0f}"})

    # the family id itself is an anchor: "the hat" = its brim footprint, so `{along: hat, t}` works
    ctx.add(Anchor(sid, {k.split(".", 1)[1]: v for k, v in brim.env.items()},
                   outline=brim._outline))
    return brim


VOCAB = {"sunhat": expand_sunhat}
SHAPES = ("ellipse", "blob", "stroke", "rect")


# --------------------------------------------------------------------------------------
# resolve
# --------------------------------------------------------------------------------------
def resolve(spec: dict) -> tuple[list[dict], dict[str, float], list[str], list[str]]:
    if not isinstance(spec, dict):
        raise SpecError("relate: spec must be a mapping with `frame` and `draw`")
    if "frame" not in spec or "draw" not in spec:
        raise SpecError("relate: spec needs both `frame` and `draw`")
    frame = spec["frame"]
    if not isinstance(frame, dict) or "w" not in frame or "h" not in frame:
        raise SpecError("relate: `frame` needs w and h")
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
        if kind not in SHAPES:
            raise SpecError(f"relate: unknown node kind {kind!r}; known: {sorted(VOCAB) + list(SHAPES)}")
        sid = str(raw[kind])

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
            spine = [ctx.point(p) for p in raw["spine"]]
            width = ctx.scalar(raw.get("w", 0))
            poly = ribbon(spine, width) if width else spine
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
    parser.add_argument("-o", "--out", required=True)
    parser.add_argument("--anchors", action="store_true", help="print the resolved anchor table")
    args = parser.parse_args()

    spec = load_yaml(Path(args.spec))
    if not isinstance(spec, dict):
        raise SpecError("relate: spec must be a mapping")
    emit, env, notes, layers = resolve(spec)
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
