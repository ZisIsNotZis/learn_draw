#!/usr/bin/env python3
"""relate.py — relational geometry resolver (ticket 06 prototype).

Turns a drawing spec written in *relations* into absolute geometry. No numeric coordinate
literals are needed anywhere in a spec: every position is expressed relative to the canvas
frame or to another already-declared shape.

    - {ellipse: head, at: [frame.w*0.60, frame.h*0.34], rx: frame.w*0.098, ry: frame.w*0.128}
    - {sunhat: hat, on: head, brim: 2.6*head.w, tilt: -14, crown: head.w*0.78, pom: 2}

The resolver does NOT look at any reference image. Tracing a reference is only ever a way to
seed *values* for a spec like this (the teacher role); the engine itself stays target-free.

Two orders, kept separate on purpose:
    resolution  = declaration order (a node may use any shape declared above it)
    painting    = `layers` order, then declaration order within a layer

Anchors a shape exposes (usable by any later node):
    at  cx cy  left right top bottom  w h  w2 h2 (half extents)  rx ry  rot
    <shape>@<t>  via {on: shape, t: 0.35} — point on the outline, wraps, optional `out: D`

Relation forms (value of any positional or size key):
    number                      relative or absolute scalar
    "expr"                      arithmetic over anchors: "1.8*head.rx + 4", "frame.w*0.62"
    {between: [A, B, t]}        point at t along A->B (t may be <0 or >1: extrapolates)
    {at: SHAPE}                  a shape's own centre
    {along: SHAPE, t: 0.35}     point on SHAPE's outline at parameter t (wraps)
    {along: SHAPE, t: 0.1, out: D}  same, pushed D outward along the outline normal
    {off: P, angle: 90, d: 40}  point at angle/distance from P (0=right, 90=down, degrees)

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

sys.path.insert(0, str(Path(__file__).resolve().parent))  # MY scene_render copy, not scripts/
from scene_render import chrome, smooth_path, compile_scene  # noqa: E402

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

    def _relation(self, value: dict) -> tuple[float, float]:
        if "between" in value:
            spec = list(value["between"])
            if len(spec) < 3:
                raise SpecError("relate: between needs [A, B, t]")
            pa = self.point(spec[0])
            pb = self.point(spec[1])
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
        if "off" in value:
            px, py = self.point(value["off"])
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
    return brim


# --------------------------------------------------------------------------------------
# SA3 starry vocabulary: swirl / hill / burst pass-throughs + glow / flame-tree /
# village / stars object families. Each carries drawing structure the spec must not
# re-derive, exposes anchors, and emits nodes the compiled node format understands.
# --------------------------------------------------------------------------------------
def _hex_rgb(c: str) -> tuple[int, int, int]:
    c = c.lstrip("#")
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def _rgba(c: str, a: float) -> str:
    r, g, b = _hex_rgb(c)
    return f"rgba({r},{g},{b},{a:.3f})"


def _lighten(c: str, f: float) -> str:
    r, g, b = _hex_rgb(c)
    r, g, b = (round(v + (255 - v) * f) for v in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def _passthrough(node: dict, ctx: Ctx, point_keys=(), scalar_keys=(), int_keys=(),
                 list_keys=(), keep=()) -> dict:
    """Resolve a generator node's relation-valued params, pass the rest through unchanged."""
    out: dict = {}
    for key in point_keys:
        if key in node:
            out[key] = list(ctx.point(node[key]))
    for key in scalar_keys:
        if key in node:
            out[key] = ctx.scalar(node[key])
    for key in int_keys:
        if key in node:
            out[key] = whole(ctx.scalar(node[key]), key)
    for key in list_keys:
        if key in node:
            out[key] = node[key]
    for key in keep:
        if key in node:
            out[key] = node[key]
    return out


def expand_swirl(node: dict, ctx: Ctx, emit: list[dict]) -> Anchor:
    """A sky swirl: nested spiral ribbon bands around an elliptical flow centre.
    Geometry lives in the scene_render generator; the spec states centre, extent, coils."""
    sid = str(node["swirl"])
    d = _passthrough(node, ctx, point_keys=("at",),
                     scalar_keys=("rx", "ry", "rot", "a0", "sweep", "w", "gap", "wob"),
                     int_keys=("bands", "n", "seed"), list_keys=("hue",),
                     keep=("sat", "val", "ink", "cap", "z", "op"))
    d = {"swirl": sid, **d}
    d.update({"z": node.get("z", "default"),
              "desc": node.get("desc", "")})
    emit.append(d)
    rx = ctx.scalar(node.get("rx", 300)); bands = whole(ctx.scalar(node.get("bands", 4)))
    w = ctx.scalar(node.get("w", 26)); gap = ctx.scalar(node.get("gap", 18))
    rmax = bands * (w + gap)
    fill = ((bands - 1) * (w + gap) + w) / rmax      # actual outer extent of the outer band
    return ctx.add(ellipse_anchor(sid, *d["at"], rx * fill * 1.06,
                                  ctx.scalar(node.get("ry", rx)) * fill * 1.06,
                                  ctx.scalar(node.get("rot", 0))))


def expand_hill(node: dict, ctx: Ctx, emit: list[dict]) -> Anchor:
    """Rolling hill bands below a horizon; stacked far(light)->near(dark), seeded phases."""
    sid = str(node["hill"])
    d = _passthrough(node, ctx, scalar_keys=("y0", "amp", "wl"), int_keys=("bands", "seed"),
                     list_keys=("colors",), keep=("z", "op"))
    d = {"hill": sid, **d}
    d.update({"z": node.get("z", "default"), "desc": node.get("desc", "")})
    emit.append(d)
    y0 = ctx.scalar(node.get("y0", 640)); amp = ctx.scalar(node.get("amp", 40))
    return ctx.add(bbox_anchor(sid, [(0, y0 - 2 * amp), (ctx.env["frame.w"], ctx.env["frame.h"])]))


def expand_glow(node: dict, ctx: Ctx, emit: list[dict]) -> Anchor:
    """A star or moon: soft radial halo + tapered rays + bright core.
    Structure knowledge: halo behind rays behind core; rays taper outward; halo is a
    radial gradient of the ray colour, not a flat disc."""
    sid = str(node["glow"])
    at = ctx.point(node["at"])
    r = ctx.scalar(node.get("r", 24))
    rays = whole(ctx.scalar(node.get("rays", 8)), f"{sid}.rays")
    ray_len = ctx.scalar(node.get("len", 3.2 * r))
    color = str(node.get("color", "#ffd75e"))
    core = str(node.get("core", _lighten(color, 0.55)))
    halo = ctx.scalar(node.get("halo", 2.4))
    seed = whole(ctx.scalar(node.get("seed", 7)), f"{sid}.seed")
    z = str(node.get("z", "default"))
    gid = f"{sid}-halo"
    emit.append({"grad": gid, "dir": "radial",
                 "stops": [[0, _rgba(color, 0.95)], [0.45, _rgba(color, 0.38)], [1, _rgba(color, 0.0)]],
                 "desc": f"{sid}: radial halo, ray colour fading out"})
    emit.append({"ellipse": gid, "at": list(at), "rx": halo * r, "ry": halo * r,
                 "fill": f"grad:{gid}", "z": z, "desc": f"{sid}: soft halo {halo:.1f}x core"})
    emit.append({"burst": f"{sid}-rays", "at": list(at), "rays": rays, "len": ray_len,
                 "w0": 0.42 * r, "w1": 1.2, "ink": color, "seed": seed, "z": z,
                 "desc": f"{sid}: {rays} rays tapering core->tip, len {ray_len:.0f}"})
    emit.append({"ellipse": f"{sid}-core", "at": list(at), "rx": 0.62 * r, "ry": 0.62 * r,
                 "fill": core, "z": z, "desc": f"{sid}: bright core"})
    return ctx.add(ellipse_anchor(sid, at[0], at[1], halo * r, halo * r))


def _flame_poly(base, ctrl, tip, w, lobes, phase, n=48, scal=0.14):
    """One flame lobe column: quadratic spine, envelope width (bulge low, sharp tip),
    scalloped edges via sin(2*pi*lobes*t + phase). Returns a closed polygon."""
    import numpy as _np
    b, c, t0 = _np.array(base, float), _np.array(ctrl, float), _np.array(tip, float)
    left, right = [], []
    for k in range(n + 1):
        t = k / n
        p = (1 - t) ** 2 * b + 2 * (1 - t) * t * c + t ** 2 * t0
        d1 = 2 * (1 - t) * (c - b) + 2 * t * (t0 - c)
        ln = _np.linalg.norm(d1) or 1.0
        nrm = _np.array([-d1[1], d1[0]]) / ln
        env = (0.32 + 0.68 * math.sin(math.pi * min(1.0, t * 1.12)) ** 0.85) * (1 - t ** 3)
        scal_t = 1 + scal * math.sin(2 * math.pi * lobes * t + phase)
        half = w * env * scal_t / 2
        left.append(tuple(p + nrm * half))
        right.append(tuple(p - nrm * half))
    return [(float(x), float(y)) for x, y in left + right[::-1]]


def expand_flame(node: dict, ctx: Ctx, emit: list[dict]) -> Anchor:
    """A flame-tree (cypress): tapered silhouette with scalloped edges and a sharp tip,
    plus small detached wisps leaning the same way. Base/tip may be relations."""
    sid = str(node["flame"])
    base = ctx.point(node["base"])
    tip = ctx.point(node["tip"])
    w = ctx.scalar(node.get("w", 60))
    lobes = ctx.scalar(node.get("lobes", 3))
    bend = ctx.scalar(node.get("bend", 0.05))   # lateral S-curve, fraction of height
    color = str(node.get("color", "#12283a"))
    wisps = whole(ctx.scalar(node.get("wisps", 2)), f"{sid}.wisps")
    seed = whole(ctx.scalar(node.get("seed", 7)), f"{sid}.seed")
    rng = np.random.default_rng(seed)
    z = str(node.get("z", "default"))
    bx, by = base; tx, ty = tip
    mx, my = (bx + tx) / 2, (by + ty) / 2
    dx, dy = tx - bx, ty - by
    h = math.hypot(dx, dy) or 1.0
    ctrl = (mx - dy / h * bend * h, my + dx / h * bend * h)
    poly = _flame_poly(base, ctrl, tip, w, lobes, rng.uniform(0, 2 * math.pi),
                       scal=ctx.scalar(node.get("scal", 0.14)))
    ctx.add(bbox_anchor(sid, poly))
    emit.append({"blob": sid, "poly": poly, "fill": color,
                 "stroke": node.get("stroke"), "sw": node.get("sw", 3), "z": z,
                 "desc": f"{sid}: flame-tree, w {w:.0f}, lobes {lobes:.0f}, "
                         f"bend {bend:+.2f} — scalloped tapered silhouette, sharp tip"})
    # wisps: detached small flames on alternating sides, leaning outward like the trunk
    for i in range(wisps):
        t = 0.30 + 0.22 * i
        bxp = (1 - t) ** 2 * bx + 2 * (1 - t) * t * ctrl[0] + t ** 2 * tx
        byp = (1 - t) ** 2 * by + 2 * (1 - t) * t * ctrl[1] + t ** 2 * ty
        side = 1 if i % 2 == 0 else -1
        wtip = (bxp + side * w * (0.70 + 0.14 * i), byp - h * (0.14 + 0.05 * i))
        wbase = (bxp + side * w * 0.12, byp + h * 0.02)
        wpoly = _flame_poly(wbase, ((wbase[0] + wtip[0]) / 2 + side * w * 0.10,
                                    (wbase[1] + wtip[1]) / 2), wtip,
                            w * (0.42 - 0.08 * i), 2, rng.uniform(0, 2 * math.pi),
                            n=32, scal=0.22)
        emit.append({"blob": f"{sid}-wisp{i + 1}", "poly": wpoly, "fill": color, "z": z,
                     "desc": f"{sid}: side wisp {i + 1}, detached flame leaning with the trunk"})
    return ctx.anchors[sid]


def _catmull(pts: list[tuple[float, float]], samples: int = 160) -> list[tuple[float, float]]:
    """Smooth curve through control points (Catmull-Rom), densely sampled."""
    import numpy as _np
    P = _np.array(pts, float)
    if len(P) < 3:
        ts = _np.linspace(0, 1, samples)
        return [tuple(P[0] + (P[-1] - P[0]) * t) for t in ts]
    out = []
    for i in range(len(P) - 1):
        p0 = P[max(i - 1, 0)]; p1 = P[i]; p2 = P[i + 1]; p3 = P[min(i + 2, len(P) - 1)]
        for u in _np.linspace(0, 1, samples // (len(P) - 1), endpoint=False):
            u2, u3 = u * u, u * u * u
            out.append(tuple(0.5 * ((2 * p1) + (-p0 + p2) * u
                                    + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u2
                                    + (-p0 + 3 * p1 - 3 * p2 + p3) * u3)))
    out.append(tuple(P[-1]))
    return [(float(x), float(y)) for x, y in out]


def expand_village(node: dict, ctx: Ctx, emit: list[dict]) -> Anchor:
    """A sleeping village: houses distributed along a ground curve with seeded jitter.
    Structure knowledge: body + roof + occasional lit window; one church with a steeple;
    houses sit ON the curve, tilted to its tangent, sized in jittered steps."""
    sid = str(node["village"])
    curve_ctl = [ctx.point(p) for p in node["curve"]]
    count = whole(ctx.scalar(node.get("count", 12)), f"{sid}.count")
    seed = whole(ctx.scalar(node.get("seed", 3)), f"{sid}.seed")
    size = ctx.scalar(node.get("size", 26))
    sizej = ctx.scalar(node.get("sizej", 0.3))
    body_fill = str(node.get("body-fill", "#26364e"))
    roof_fill = str(node.get("roof-fill", "#3d4f6b"))
    win_fill = str(node.get("win-fill", "#ffd35c"))
    win_chance = ctx.scalar(node.get("win-chance", 0.55))
    church_t = ctx.scalar(node.get("church", 0.5))
    church_h = ctx.scalar(node.get("church-h", 1.8))
    z = str(node.get("z", "default"))
    rng = np.random.default_rng(seed)
    line = _catmull(curve_ctl)

    def ground(t: float) -> tuple[float, float, float, float]:
        i = min(max(int(t * (len(line) - 1)), 0), len(line) - 2)
        p = line[i]
        q = line[i + 1]
        tx, ty = q[0] - p[0], q[1] - p[1]
        ln = math.hypot(tx, ty) or 1.0
        return p[0], p[1], tx / ln, ty / ln

    xs = [p[0] for p in line]; ys = [p[1] for p in line]
    ctx.add(bbox_anchor(sid, [(min(xs), min(ys) - size), (max(xs), max(ys))]))
    for i in range(count):
        t = (i + 0.5) / count + rng.uniform(-0.3, 0.3) / count
        t = min(max(t, 0.02), 0.98)
        gx, gy, tx, ty = ground(t)
        ux, uy = ty, -tx                      # up = tangent rotated -90deg (y-down frame)
        is_church = abs(t - church_t) < 0.5 / count
        w = size * rng.uniform(1 - sizej, 1 + sizej) * (1.35 if is_church else 1.0)
        h = w * rng.uniform(0.72, 1.0) * (church_h if is_church else 1.0)
        roof_h = w * (0.78 if is_church else rng.uniform(0.60, 0.80))
        jx, jy = rng.uniform(-3, 3), rng.uniform(-2, 2)
        bx0, by0 = gx - tx * w / 2 + ux * 2 + jx, gy - ty * w / 2 + uy * 2 + jy
        bx1, by1 = gx + tx * w / 2 + ux * 2 + jx, gy + ty * w / 2 + uy * 2 + jy
        body = [(bx0, by0 - h), (bx1, by1 - h), (bx1, by1), (bx0, by0)]
        roof = [(bx0 - tx * w * 0.16, by0 - h - uy * 0),
                (bx1 + tx * w * 0.16, by1 - h - uy * 0),
                ((bx0 + bx1) / 2 + tx * 2, (by0 + by1) / 2 - h - roof_h)]
        hid = f"{sid}-h{i + 1}"
        emit.append({"poly": hid, "pts": [(round(x, 1), round(y, 1)) for x, y in body],
                     "fill": body_fill, "z": z,
                     "desc": f"{hid}: house body at t={t:.2f} on the ground curve" +
                             (" (church)" if is_church else "")})
        emit.append({"poly": f"{hid}-roof", "pts": [(round(x, 1), round(y, 1)) for x, y in roof],
                     "fill": roof_fill, "z": z, "desc": f"{hid}: gable roof"})
        if is_church:
            apex = ((bx0 + bx1) / 2, (by0 + by1) / 2 - h - roof_h)
            steeple = [((bx0 + bx1) / 2 - w * 0.16, by0 - h),
                       ((bx0 + bx1) / 2 + w * 0.16, by1 - h),
                       (apex[0], apex[1] - h * 0.42)]
            emit.append({"poly": f"{hid}-steeple",
                         "pts": [(round(x, 1), round(y, 1)) for x, y in steeple],
                         "fill": roof_fill, "z": z, "desc": f"{hid}: church steeple"})
        elif rng.uniform(0, 1) < win_chance:
            wx, wy = (bx0 + bx1) / 2 + tx * rng.uniform(-w * 0.2, w * 0.2), (by0 + by1) / 2
            ws = max(2.5, w * 0.14)
            emit.append({"poly": f"{hid}-win",
                         "pts": [(round(wx - ws, 1), round(wy - ws * 1.3, 1)),
                                 (round(wx + ws, 1), round(wy - ws * 1.3, 1)),
                                 (round(wx + ws, 1), round(wy + ws * 1.3, 1)),
                                 (round(wx - ws, 1), round(wy + ws * 1.3, 1))],
                         "fill": win_fill, "z": z, "desc": f"{hid}: lit window"})
    return ctx.anchors[sid]


def expand_stars(node: dict, ctx: Ctx, emit: list[dict]) -> Anchor:
    """A star field: n seeded dots scattered in a region (jitter-grid relation made concrete)."""
    sid = str(node["stars"])
    region = [ctx.scalar(v) for v in node["region"]]
    n = whole(ctx.scalar(node.get("n", 24)), f"{sid}.n")
    seed = whole(ctx.scalar(node.get("seed", 5)), f"{sid}.seed")
    r = ctx.scalar(node.get("r", 3.2))
    rj = ctx.scalar(node.get("rj", 0.8))
    fills = node.get("fill", ["#fdf6d8", "#ffe9a8", "#cfe4ff"])
    if isinstance(fills, str):
        fills = [fills]
    z = str(node.get("z", "default"))
    rng = np.random.default_rng(seed)
    for i in range(n):
        x = rng.uniform(region[0], region[2]); y = rng.uniform(region[1], region[3])
        rr = max(2.6, r * rng.uniform(1 - rj, 1 + rj * 1.6))
        emit.append({"ellipse": f"{sid}-s{i + 1}", "at": [round(x, 1), round(y, 1)],
                     "rx": round(rr, 1), "ry": round(rr, 1),
                     "fill": fills[i % len(fills)], "op": round(rng.uniform(0.45, 1.0), 2),
                     "z": z, "desc": f"{sid}: star dot {i + 1}"})
    return ctx.add(bbox_anchor(sid, [(region[0], region[1]), (region[2], region[3])]))


VOCAB = {"sunhat": expand_sunhat, "swirl": expand_swirl, "hill": expand_hill,
         "glow": expand_glow, "flame": expand_flame, "village": expand_village,
         "stars": expand_stars}
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
        if kind == "grad":
            emit.append({"grad": str(raw["grad"]), "dir": raw.get("dir"),
                         "stops": raw["stops"], "desc": raw.get("desc", "")})
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
    parser.add_argument("--scene", action="store_true", help="only write the compiled scene yaml")
    args = parser.parse_args()

    spec = load_yaml(Path(args.spec))
    if not isinstance(spec, dict):
        raise SpecError("relate: spec must be a mapping")
    emit, env, notes, layers = resolve(spec)
    frame = spec["frame"]

    # SA3: compile DOWN to the node format and render through scene_render (one back end),
    # so generator nodes (swirl/burst/hill) and gradients share the chrome pipeline.
    scene = ([{"layers": layers}] if layers else []) + emit
    if args.scene:
        write_text(Path(args.out).with_suffix(".scene.yaml"),
                   yaml.safe_dump(scene, sort_keys=False, width=200))
    size = (whole(frame["w"], "frame.w"), whole(frame["h"], "frame.h"))
    svg = compile_scene(scene, size)
    svg_path = Path(args.out).with_suffix(".svg")
    write_text(svg_path, svg)
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
