#!/usr/bin/env python3
"""fit-family.py — extract object-family parameters from a frozen teacher mask.

The teacher loop (docs/drawing/abstraction.md, STATUS D24) is: measure a subject, use the
measurement to FIT a family, then close the reference and keep only the fitted parameters. This
instrument is the "fit" step. It takes a vocabulary family (`sunhat`, `face`), a starting
parameter set, and one or more frozen `traced` masks, and searches the family's parameters to
maximise the IoU between the family's own rendered masks and the teacher's masks.

Honesty hinge (invariant 4): the target is the TEACHER'S MEASUREMENT — the frozen traced outline.
It is never `edge_f1`, `color_dist`, or the baseline comparison. Nudging a parameter until an
evaluation metric rises is the optimizer regression the project forbids; fitting a family to the
traced outline is parameter extraction. This tool therefore never looks at image.jpg at all: it
opens the traced sidecars, which carry no raster.

Occluders (generalised 2026-09-15). A family's teacher mask is the subject's VISIBLE pixels, so
the family's rendered mask has to be clipped to what stays visible after everything painted above
it. Which shapes those are is read from the spec's own `layers:` order — every node painted after
the family's shapes occludes it — instead of a hard-coded list (the old one said only `hair-mass`,
which was wrong the moment the hat moved under the head). The same pass renders the whole spec at
each candidate, so the occluders that are themselves head-relative (eyes, hair) move with the
family being fitted.

Grouping. A family emits several sub-shapes, and one traced mask may be the union of more than one
of them. For `sunhat` the teacher's `hat-far-navy` is the crown AND the far brim in one connected
navy mass, so the fit target for it is `union(crown-dome, brim-far)`; the two teal masks are the
split top surface, so their union is matched by `brim-near`. `face` emits cranium + jaw, matched to
the one `face-skin` mask.

Search. Deterministic multi-start coordinate descent followed by a dependency-free Nelder-Mead
polish. Same spec + same sidecars -> same fitted parameters, bit for bit.

Usage:
  .venv/bin/python .scratch/13-assembly/work/fit-family.py \
      --family sunhat --node hat \
      [--spec .scratch/13-assembly/work/spec.yaml] \
      [--targets hat-far-navy:far,hat-near-teal:near,hat-near-teal-right:near] \
      [--out /tmp/fit.json]

  .venv/bin/python .scratch/13-assembly/work/fit-family.py \
      --family face --node head --targets face-skin:face --out /tmp/face-fit.json
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import relate as rl  # noqa: E402

DEFAULT_SPEC = ROOT / ".scratch/13-assembly/work/spec.yaml"

# --------------------------------------------------------------------------------------
# the family registry: which parameters the search owns, and how one becomes a spec node
# --------------------------------------------------------------------------------------
# Ordered so the search (and any log) is reproducible.
SUNHAT_PARAMS = ["brim", "crown", "tilt", "lift", "drop", "crown-h", "flat",
                 "front0", "front1", "rim", "droop"]

SUNHAT_BOUNDS = {
    "brim": (300.0, 1000.0), "crown": (80.0, 450.0), "tilt": (-30.0, 70.0),
    "lift": (-0.4, 2.6), "drop": (-1.5, 3.0), "crown-h": (0.1, 1.6),
    "flat": (0.03, 1.0), "front0": (0.0, 0.6), "front1": (0.15, 1.0),
    "rim": (0.02, 0.98), "droop": (-1.5, 2.5),
}
# coordinate-descent step schedule, in the parameter's own units
SUNHAT_STEPS = {
    "brim": 40.0, "crown": 30.0, "tilt": 8.0, "lift": 0.2, "drop": 0.2,
    "crown-h": 0.1, "flat": 0.06, "front0": 0.06, "front1": 0.08,
    "rim": 0.08, "droop": 0.3,
}
# family sub-shape suffix -> group name; sub-shapes not listed (poms) are ignored by the fit
SUNHAT_GROUPS = {
    "far": {"targets": ["hat-far-navy"], "shapes": ["-dome", "-brim-far"]},
    "near": {"targets": ["hat-near-teal", "hat-near-teal-right"], "shapes": ["-brim-near"]},
}

# `face` emits a cranium ellipse + a jaw blob; the teacher's one `face-skin` mask is their union.
# `cx`/`cy` are the fitted centre (the node's `at`), so the search can move the head box.
FACE_PARAMS = ["cx", "cy", "rx", "ry", "cheek", "jaw", "chin-w", "turn"]
FACE_BOUNDS = {
    "cx": (560.0, 840.0), "cy": (170.0, 360.0), "rx": (50.0, 140.0), "ry": (50.0, 170.0),
    "cheek": (0.30, 1.05), "jaw": (0.05, 0.85), "chin-w": (0.005, 0.40), "turn": (-35.0, 35.0),
}
FACE_STEPS = {
    "cx": 8.0, "cy": 8.0, "rx": 6.0, "ry": 6.0, "cheek": 0.05, "jaw": 0.05,
    "chin-w": 0.03, "turn": 4.0,
}
FACE_GROUPS = {"face": {"targets": ["face-skin"], "shapes": ["-cranium", "-jaw"]}}

# `hair-mass` emits one tapered band per instance; the assembly's hair is a big sweeping mass and a
# narrow cheek lock, i.e. TWO instances matched to the one `hair-mass` teacher mask. The spine is
# variable length (2-4 points), so the parameter names are built per node rather than fixed.
HAIR_BOUNDS = {"x": (400.0, 1030.0), "y": (0.0, 820.0), "w": (2.0, 420.0)}
HAIR_STEPS = {"x": 20.0, "y": 20.0, "w": 15.0}
HAIR_GROUPS = {"mass": {"targets": ["hair-mass"],
                        "shapes": ["hair-main", "hair-fringe", "hair-lock"]}}

# `collar` emits a flap + a trim band. The pale body, the right trim and the left trim are three
# frozen teacher masks (the fold shadows split the navy band into components); their union is the
# collar footprint the family must match.
COLLAR_PARAMS = ["cx", "cy", "w", "h", "neck", "v", "trim", "turn", "tilt"]
COLLAR_BOUNDS = {"cx": (680.0, 820.0), "cy": (395.0, 460.0), "w": (150.0, 270.0),
                 "h": (55.0, 125.0), "neck": (0.10, 0.70), "v": (0.05, 0.45),
                 "trim": (0.10, 0.50), "turn": (-0.80, 0.20), "tilt": (-15.0, 15.0)}
COLLAR_STEPS = {"cx": 8.0, "cy": 8.0, "w": 16.0, "h": 10.0, "neck": 0.06, "v": 0.08,
                "trim": 0.05, "turn": 0.10, "tilt": 5.0}
COLLAR_GROUPS = {"collar": {"targets": ["collar-pale", "collar-trim", "collar-trim-left"],
                            "shapes": ["-body", "-trim"]}}

# `bow` emits two loops, a knot, a magenta tail and a navy tail. The magenta mask is one connected
# mass (loops + knot + tail); the navy tail is its own teacher mask, so it is a second group.
BOW_PARAMS = ["cx", "cy", "w", "h", "spread", "tilt", "loop-len", "loop-w",
              "knot-w", "knot-h", "tail-angle", "tail-len", "tail-w",
              "tail2-angle", "tail2-len", "tail2-w"]
BOW_BOUNDS = {"cx": (480.0, 840.0), "cy": (430.0, 660.0), "w": (120.0, 380.0),
              "h": (80.0, 250.0), "spread": (60.0, 180.0), "tilt": (-170.0, 20.0),
              "loop-len": (0.40, 1.60), "loop-w": (0.40, 1.80), "knot-w": (0.05, 0.50),
              "knot-h": (0.30, 1.60), "tail-angle": (40.0, 220.0), "tail-len": (0.0, 260.0),
              "tail-w": (0.0, 160.0), "tail2-angle": (40.0, 160.0), "tail2-len": (0.0, 180.0),
              "tail2-w": (0.0, 80.0)}
BOW_STEPS = {"cx": 8.0, "cy": 8.0, "w": 20.0, "h": 16.0, "spread": 8.0, "tilt": 8.0,
             "loop-len": 0.10, "loop-w": 0.10, "knot-w": 0.04, "knot-h": 0.10,
             "tail-angle": 10.0, "tail-len": 20.0, "tail-w": 15.0, "tail2-angle": 10.0,
             "tail2-len": 15.0, "tail2-w": 8.0}
BOW_GROUPS = {"loops": {"targets": ["bow-loops"], "shapes": ["-loop1", "-loop2", "-knot"]},
              "tail": {"targets": ["bow-tail"], "shapes": ["-tail1"]},
              "navy": {"targets": ["bowtail-navy"], "shapes": ["-tail2"]}}

# `arm` emits a limb, a puff sleeve and a cuff, all on one spine. Three groups, one per sub-shape —
# the limb matches the forearm cream + the pink elbow patch, the sleeve its (approximate) mask, and
# the cuff the high-confidence navy band.
ARM_EXTRA_PARAMS = ["sleeve", "puff", "cuff-at", "cuff-h", "cuff-pad"]
ARM_AXIS_BOUNDS = {"x": (400.0, 1030.0), "y": (380.0, 960.0), "w": (20.0, 240.0)}
ARM_AXIS_STEPS = {"x": 16.0, "y": 16.0, "w": 10.0}
ARM_EXTRA_BOUNDS = {"sleeve": (0.0, 0.90), "puff": (0.0, 1.60), "cuff-at": (0.0, 0.90),
                    "cuff-h": (10.0, 130.0), "cuff-pad": (0.0, 40.0)}
ARM_EXTRA_STEPS = {"sleeve": 0.06, "puff": 0.12, "cuff-at": 0.06, "cuff-h": 8.0,
                   "cuff-pad": 4.0}
ARM_GROUPS = {"sleeve": {"targets": ["sleeve-R"], "shapes": ["-sleeve"]},
              "cuff": {"targets": ["cuff-R"], "shapes": ["-cuff"]},
              "limb": {"targets": ["arm-R", "armskin-R"], "shapes": ["-limb"]}}

REGISTRY = {
    "sunhat": {"params": SUNHAT_PARAMS, "bounds": SUNHAT_BOUNDS, "steps": SUNHAT_STEPS,
               "groups": SUNHAT_GROUPS},
    "face": {"params": FACE_PARAMS, "bounds": FACE_BOUNDS, "steps": FACE_STEPS,
             "groups": FACE_GROUPS},
    "hair-mass": {"params": [], "bounds": HAIR_BOUNDS, "steps": HAIR_STEPS,
                  "groups": HAIR_GROUPS},
    "collar": {"params": COLLAR_PARAMS, "bounds": COLLAR_BOUNDS, "steps": COLLAR_STEPS,
               "groups": COLLAR_GROUPS},
    "bow": {"params": BOW_PARAMS, "bounds": BOW_BOUNDS, "steps": BOW_STEPS,
            "groups": BOW_GROUPS},
    "arm": {"params": [], "bounds": {**ARM_AXIS_BOUNDS, **ARM_EXTRA_BOUNDS},
            "steps": {**ARM_AXIS_STEPS, **ARM_EXTRA_STEPS}, "groups": ARM_GROUPS},
}

# family parameter defaults, used when the spec node omits an optional key (must match relate.py)
COLLAR_DEFAULTS = {"neck": 0.40, "v": 0.30, "trim": 0.25, "turn": 0.0, "tilt": 0.0}
BOW_DEFAULTS = {"spread": 128.0, "tilt": -90.0, "loop-len": 0.95, "loop-w": 0.95,
                "knot-w": 0.20, "knot-h": 0.85, "tail-angle": 122.0, "tail-len": 60.0,
                "tail-w": 55.0, "tail2-angle": 90.0, "tail2-len": 0.0, "tail2-w": 22.0}
ARM_DEFAULTS = {"sleeve": 0.0, "puff": 0.6, "cuff-at": 0.0, "cuff-h": 0.0, "cuff-pad": 0.0}


def params_for_node(kind: str, node: dict) -> list[str]:
    """The fitted parameter names for one family instance (hair/arm spines vary in length)."""
    if kind == "hair-mass":
        n = len(node["spine"])
        return [f"{ax}{j}" for j in range(n) for ax in ("sx", "sy")] + [f"w{j}" for j in range(n)]
    if kind == "arm":
        n = len(node["spine"])
        return ([f"{ax}{j}" for j in range(n) for ax in ("sx", "sy")] + [f"w{j}" for j in range(n)]
                + list(ARM_EXTRA_PARAMS))
    return list(REGISTRY[kind]["params"])


def family_kind_of(node: dict) -> str | None:
    """The vocabulary kind of a spec node, if it is a registered family."""
    for key in node:
        if key in REGISTRY:
            return key
    return None


# --------------------------------------------------------------------------------------
# masks and paint order
# --------------------------------------------------------------------------------------
def rasterize(node: dict, shape: tuple[int, int]) -> np.ndarray:
    """A full-canvas uint8 mask of one emitted compiled node (poly / ellipse / stroke).

    A full-frame background rect yields an all-zero mask: it is the ground, never an occluder.
    """
    h, w = shape
    mask = np.zeros((h, w), np.uint8)
    if node.get("full"):
        return mask
    if "poly" in node:
        pts = np.round(np.asarray(node["poly"], float)).astype(np.int32)
        if len(pts) >= 3:
            cv2.fillPoly(mask, [pts], 1)
    elif "ellipse" in node:
        cx, cy = node["at"]
        axes = (max(1, int(round(node["rx"]))), max(1, int(round(node["ry"]))))
        cv2.ellipse(mask, (int(round(cx)), int(round(cy))), axes,
                    float(node.get("rot", 0)), 0, 360, 1, -1)
    elif "stroke" in node:
        pts = np.round(np.asarray(node["spine"], float)).astype(np.int32)
        th = max(1, int(round(node.get("w", 2))))
        cv2.polylines(mask, [pts], False, 1, th)
        for p in (pts[0], pts[-1]):  # round caps, matching the renderer
            cv2.circle(mask, (int(p[0]), int(p[1])), th // 2, 1, -1)
    return mask


def paint_order(emit: list[dict], layers: list[str]) -> list[dict]:
    """Emitted nodes in the order `relate.emit_svg` actually paints them.

    Full-frame rects first, then a STABLE sort by layer index — identical to the renderer, so
    'painted above' has one meaning for the fitter and the drawing.
    """
    def zindex(node: dict) -> int:
        z = str(node.get("z", "default"))
        return layers.index(z) if z in layers else len(layers)

    return [n for n in emit if n.get("full")] + \
        sorted((n for n in emit if not n.get("full")), key=zindex)


def group_occluders(emit: list[dict], layers: list[str], group_suffixes: list[str],
                    target_names: set[str]) -> tuple[list[str], list[str]]:
    """The generalised occluder rule, in one place.

    Returns (group_sids, occluder_sids) for one family group:
      * `group_sids` — every emitted shape whose id ends with one of `group_suffixes`;
      * `occluder_sids` — every OTHER node painted after the group's last shape, in the spec's
        own paint order, EXCLUDING the teacher targets themselves (the mask being fitted to is
        not an occluder of the thing being fitted). Nothing is hard-coded: a node painted above
        the family occludes it because `layers:` says so.
    """
    order = paint_order(emit, layers)
    sids = [rl._sid(n) for n in order]
    group = [s for s in sids if any(s.endswith(suf) for suf in group_suffixes)]
    if not group:
        return [], []
    last = max(i for i, s in enumerate(sids) if s in set(group))
    occ: list[str] = []
    for s in sids[last + 1:]:
        if s in target_names or s in group or s in occ:
            continue
        occ.append(s)
    return group, occ


def sidecar_mask(path: Path, shape: tuple[int, int]) -> np.ndarray:
    """Fill a frozen traced sidecar's vertices into a mask (no raster is opened)."""
    data = json.loads(Path(path).read_text())
    pts = np.round(np.asarray(data["vertices"], float)).astype(np.int32)
    h, w = shape
    mask = np.zeros((h, w), np.uint8)
    cv2.fillPoly(mask, [pts], 1)
    return mask


def iou(a: np.ndarray, b: np.ndarray) -> float:
    """Intersection-over-union of two boolean masks."""
    a, b = a > 0, b > 0
    union = np.logical_or(a, b).sum()
    return float(np.logical_and(a, b).sum() / union) if union else 0.0


# --------------------------------------------------------------------------------------
# the objective
# --------------------------------------------------------------------------------------
class FamilyFit:
    """Maximise mask IoU between a family instance and the teacher's traced masks."""

    def __init__(self, spec: dict, base_dir: Path, kind: str, node_id,
                 targets: dict[str, list[str]] | None = None,
                 occluders: list[str] | None = None):
        reg = REGISTRY[kind]
        self.kind = kind
        node_ids = [node_id] if isinstance(node_id, str) else list(node_id)
        self.node_ids = node_ids
        self.multi = len(node_ids) > 1
        self.spec = spec
        self.base_dir = Path(base_dir)
        self.frame = spec["frame"]
        self.shape = (int(self.frame["h"]), int(self.frame["w"]))

        # locate every family instance in the spec — the search swaps them each evaluation
        self.node_indices: list[int] = []
        for nid in node_ids:
            found = None
            for i, raw in enumerate(spec["draw"]):
                if family_kind_of(raw) == kind and str(raw[kind]) == nid:
                    found = i
                    break
            if found is None:
                raise SystemExit(f"fit-family: no {kind} node {nid!r} in the spec")
            self.node_indices.append(found)
        self.nodes = [copy.deepcopy(spec["draw"][i]) for i in self.node_indices]

        # parameter space: per instance, prefixed with its index when there is more than one
        self.params: list[str] = []
        self.bounds: dict[str, tuple[float, float]] = {}
        self.steps: dict[str, float] = {}
        for i, node in enumerate(self.nodes):
            pre = f"{i}." if self.multi else ""
            for p in params_for_node(kind, node):
                q = f"{pre}{p}"
                self.params.append(q)
                if kind == "hair-mass":
                    base = p.rstrip("0123456789")
                    axis = "x" if base == "sx" else "y" if base == "sy" else "w"
                    self.bounds[q] = HAIR_BOUNDS[axis]
                    self.steps[q] = HAIR_STEPS[axis]
                elif kind == "arm":
                    base = p.rstrip("0123456789")
                    if base in ("sx", "sy", "w") and base != p:
                        axis = "x" if base == "sx" else "y" if base == "sy" else "w"
                        self.bounds[q] = ARM_AXIS_BOUNDS[axis]
                        self.steps[q] = ARM_AXIS_STEPS[axis]
                    else:
                        self.bounds[q] = ARM_EXTRA_BOUNDS[p]
                        self.steps[q] = ARM_EXTRA_STEPS[p]
                else:
                    self.bounds[q] = reg["bounds"][p]
                    self.steps[q] = reg["steps"][p]

        # grouping: default from the registry, overridable per run
        self.groups = copy.deepcopy(reg["groups"])
        if targets:
            for name, target_list in targets.items():
                self.groups[name]["targets"] = target_list
        self.target_names: set[str] = set()
        for g in self.groups.values():
            self.target_names.update(g["targets"])
        # an explicit extra occluder list, unioned with the derived set (mostly for experiments)
        self.extra_occluders = list(occluders or [])
        self.last_occluders: list[str] = []

        # teacher masks
        traced_dir = self.base_dir / "traced"
        self.target_masks: dict[str, list[np.ndarray]] = {}
        for gname, g in self.groups.items():
            self.target_masks[gname] = [sidecar_mask(traced_dir / f"{t}.json", self.shape)
                                        for t in g["targets"]]

        # starting vector, read from the live spec so the search begins where the drawing is.
        # Parameters may be relational (`2.905*head.w`), so resolve the spec once and evaluate
        # each expression against the resulting anchor environment.
        _emit, env, _notes, _layers = rl.resolve(spec, base_dir=self.base_dir)
        self.start: dict[str, float] = {}
        for i, node in enumerate(self.nodes):
            pre = f"{i}." if self.multi else ""
            for p in params_for_node(kind, node):
                self.start[f"{pre}{p}"] = self._param_from_node(p, node, env)

    @staticmethod
    def _expr(value, env: dict) -> float:
        return rl.eval_expr(value, env) if isinstance(value, str) else float(value)

    def _param_from_node(self, param: str, node: dict, env: dict) -> float:
        if self.kind == "hair-mass":
            if param[:2] == "sx":
                return self._expr(node["spine"][int(param[2:])][0], env)
            if param[:2] == "sy":
                return self._expr(node["spine"][int(param[2:])][1], env)
            w = node["w"]
            j = int(param[1:])
            return self._expr(w[j] if isinstance(w, (list, tuple)) else w, env)
        if self.kind == "arm":
            if param[:2] == "sx":
                return self._expr(node["spine"][int(param[2:])][0], env)
            if param[:2] == "sy":
                return self._expr(node["spine"][int(param[2:])][1], env)
            if param[0] == "w":
                return self._expr(node["w"][int(param[1:])], env)
            return self._expr(node.get(param, ARM_DEFAULTS[param]), env)
        if self.kind in ("collar", "bow"):
            at = node.get("at", [0.0, 0.0])
            if param == "cx":
                return self._expr(at[0], env)
            if param == "cy":
                return self._expr(at[1], env)
            defaults = COLLAR_DEFAULTS if self.kind == "collar" else BOW_DEFAULTS
            if param in node:
                return self._expr(node[param], env)
            return self._expr(defaults[param], env)
        if self.kind == "face":
            at = node.get("at", [0.0, 0.0])
            if param == "cx":
                return self._expr(at[0], env)
            if param == "cy":
                return self._expr(at[1], env)
            defaults = {"cheek": 0.68, "jaw": 0.37, "chin-w": 0.035, "turn": 0.0}
            if param == "ry":
                return self._expr(node.get("ry", node["rx"]), env)
            return self._expr(node[param] if param == "rx" else node.get(param, defaults[param]),
                              env)
        front = node.get("front", [0.05, 0.45])
        if param == "front0":
            return self._expr(front[0], env)
        if param == "front1":
            return self._expr(front[1], env)
        if param == "droop":
            return self._expr(node.get("droop", 0.0), env)
        return self._expr(node[param], env)

    def node_from_params(self, x: dict, i: int = 0) -> dict:
        node = copy.deepcopy(self.nodes[i])
        pre = f"{i}." if self.multi else ""
        if self.kind == "hair-mass":
            npt = len(node["spine"])
            node["spine"] = [[float(x[f"{pre}sx{j}"]), float(x[f"{pre}sy{j}"])]
                              for j in range(npt)]
            node["w"] = [float(x[f"{pre}w{j}"]) for j in range(npt)]
            return node
        if self.kind == "arm":
            npt = len(node["spine"])
            node["spine"] = [[float(x[f"{pre}sx{j}"]), float(x[f"{pre}sy{j}"])]
                              for j in range(npt)]
            node["w"] = [float(x[f"{pre}w{j}"]) for j in range(npt)]
            for p in ARM_EXTRA_PARAMS:
                node[p] = float(x[f"{pre}{p}"])
            return node
        if self.kind in ("collar", "bow"):
            node["at"] = [float(x[f"{pre}cx"]), float(x[f"{pre}cy"])]
            for p in params_for_node(self.kind, node):
                if p in ("cx", "cy"):
                    continue
                node[p] = float(x[f"{pre}{p}"])
            return node
        if self.kind == "face":
            node["at"] = [float(x[f"{pre}cx"]), float(x[f"{pre}cy"])]
            for p in ("rx", "ry", "cheek", "jaw", "chin-w"):
                node[p] = float(x[f"{pre}{p}"])
            node["turn"] = float(x.get(f"{pre}turn", 0.0))
            return node
        for p in params_for_node(self.kind, node):
            if p not in ("front0", "front1"):
                node[p] = float(x[f"{pre}{p}"])
        node["front"] = [float(x[f"{pre}front0"]), float(x[f"{pre}front1"])]
        return node

    def render(self, x: dict) -> dict[str, np.ndarray]:
        """Resolve the WHOLE spec with the candidate family and return each group's visible mask.

        The whole spec (not a host+family fragment) is resolved because the occluders may be
        head-relative — the eyes and hair move when the face is re-fitted — and because the
        occluder rule is "whatever the spec's paint order puts above the family". The group mask
        is then the family's own shapes with every later-painted non-target node subtracted.
        """
        spec = copy.deepcopy(self.spec)
        for i, idx in enumerate(self.node_indices):
            spec["draw"][idx] = self.node_from_params(x, i)
        emit, _env, _notes, layers = rl.resolve(spec, base_dir=self.base_dir)
        order = paint_order(emit, layers)

        # Work out which sids each group needs BEFORE rasterizing: the family's own shapes plus
        # whatever the layer order paints above it. Rasterizing only those (instead of every node
        # in the spec) is the difference between a minute and an hour for an 18-parameter hair fit.
        per_group: dict[str, tuple[list[str], list[str]]] = {}
        needed: set[str] = set(self.extra_occluders)
        for gname, g in self.groups.items():
            gs, occ = group_occluders(emit, layers, g["shapes"], self.target_names)
            per_group[gname] = (gs, occ)
            needed.update(gs)
            needed.update(occ)
        by_sid: dict[str, np.ndarray] = {}
        for node in order:
            sid = rl._sid(node)
            if sid not in needed:
                continue
            m = rasterize(node, self.shape)
            by_sid[sid] = (by_sid[sid] | m) if sid in by_sid else m

        # explicit extras are subtracted from every group, on top of the layer-derived set
        extra = np.zeros(self.shape, np.uint8)
        for name in self.extra_occluders:
            extra |= by_sid.get(name, np.zeros(self.shape, np.uint8))
        zero = np.zeros(self.shape, np.uint8)

        out: dict[str, np.ndarray] = {}
        occ_names: set[str] = set(self.extra_occluders)
        for gname, g in self.groups.items():
            group_sids, occ_sids = per_group[gname]
            gm = np.zeros(self.shape, np.uint8)
            for sid in group_sids:
                gm |= by_sid.get(sid, zero)
            occ = extra.copy()
            for sid in occ_sids:
                occ_names.add(sid)
                occ |= by_sid.get(sid, zero)
            out[gname] = (gm > 0) & (occ == 0)
        self.last_occluders = sorted(occ_names)
        return out

    def evaluate(self, x: dict) -> tuple[float, dict[str, float]]:
        """Mean group IoU (the fitness) and the per-group breakdown."""
        try:
            groups = self.render(x)
        except Exception:
            return -1.0, {g: 0.0 for g in self.groups}
        det: dict[str, float] = {}
        for gname in self.groups:
            target = np.zeros(self.shape, bool)
            for tm in self.target_masks[gname]:
                target |= tm > 0
            det[gname] = iou(groups[gname], target)
        return float(sum(det.values()) / max(len(det), 1)), det

    def silhouette_iou(self, x: dict) -> float:
        """Extra report: the whole visible family vs the union of every teacher mask."""
        try:
            groups = self.render(x)
        except Exception:
            return 0.0
        allm = np.zeros(self.shape, bool)
        for gm in groups.values():
            allm |= gm
        target = np.zeros(self.shape, bool)
        for tl in self.target_masks.values():
            for tm in tl:
                target |= tm > 0
        return iou(allm, target)


# --------------------------------------------------------------------------------------
# deterministic search: coordinate descent + dependency-free Nelder-Mead
# --------------------------------------------------------------------------------------
def _clamp(x: dict, bounds: dict[str, tuple[float, float]]) -> dict:
    out = {}
    for k, v in x.items():
        lo, hi = bounds[k]
        out[k] = min(max(v, lo), hi)
    if "front0" in out and "front1" in out and out["front1"] < out["front0"] + 0.05:
        out["front1"] = min(out["front0"] + 0.05, 1.0)
    return out


def coordinate_descent(evaluate, start: dict, bounds: dict, steps: dict,
                       max_rounds: int = 60) -> tuple[dict, float]:
    """Greedy axis-wise descent with a halving step schedule. Fully deterministic."""
    x = _clamp(dict(start), bounds)
    best, _ = evaluate(x)
    step = dict(steps)
    for _ in range(max_rounds):
        improved = False
        for k in x:
            for sgn in (1.0, -1.0):
                cand = _clamp({**x, k: x[k] + sgn * step[k]}, bounds)
                score, _ = evaluate(cand)
                if score > best + 1e-9:
                    x, best, improved = cand, score, True
        if not improved:
            for k in step:
                step[k] *= 0.5
            if all(v < 1e-3 for v in step.values()):
                break
    return x, best


def nelder_mead(evaluate, start: dict, bounds: dict, step: dict,
                max_iter: int = 300) -> tuple[dict, float]:
    """A small deterministic Nelder-Mead (no scipy), with box clamping.

    `evaluate` takes a dict and returns (score, detail); we maximise. The initial simplex is the
    start plus one axis probe per parameter, scaled by `step`.
    """
    keys = list(start)
    x0 = np.array([start[k] for k in keys], float)

    def obj(vec: np.ndarray) -> float:
        x = _clamp({k: float(v) for k, v in zip(keys, vec)}, bounds)
        score, _ = evaluate(x)
        return -score

    n = len(keys)
    simplex = [x0]
    for i in range(n):
        p = x0.copy()
        p[i] += step[keys[i]]
        simplex.append(p)
    simplex = np.array(simplex)
    fvals = np.array([obj(p) for p in simplex])

    for _ in range(max_iter):
        order = np.argsort(fvals)
        simplex, fvals = simplex[order], fvals[order]
        if np.max(np.abs(simplex[1:] - simplex[0])) < 1e-3:
            break
        centroid = simplex[:-1].mean(axis=0)
        xr = centroid + (centroid - simplex[-1])
        fr = obj(xr)
        if fr < fvals[0]:
            xe = centroid + 2.0 * (centroid - simplex[-1])
            fe = obj(xe)
            simplex[-1], fvals[-1] = (xe, fe) if fe < fr else (xr, fr)
        elif fr < fvals[-2]:
            simplex[-1], fvals[-1] = xr, fr
        else:
            xc = centroid + 0.5 * (simplex[-1] - centroid)
            fc = obj(xc)
            if fc < fvals[-1]:
                simplex[-1], fvals[-1] = xc, fc
            else:
                simplex[1:] = simplex[0] + 0.5 * (simplex[1:] - simplex[0])
                fvals[1:] = np.array([obj(p) for p in simplex[1:]])
    order = np.argsort(fvals)
    best = simplex[order[0]]
    return _clamp({k: float(v) for k, v in zip(keys, best)}, bounds), float(-fvals[order[0]])


def _halton(index: int, base: int) -> float:
    """Deterministic low-discrepancy scalar in [0,1): the Halton sequence."""
    f, r, i = 1.0, 0.0, index
    while i > 0:
        f /= base
        r += f * (i % base)
        i //= base
    return r


_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71]


def halton_seeds(params: list[str], bounds: dict, count: int, skip: int = 7) -> list[dict]:
    """`count` deterministic low-discrepancy points in the family's parameter box."""
    seeds = []
    for k in range(count):
        seeds.append({p: bounds[p][0] + (bounds[p][1] - bounds[p][0])
                      * _halton(k + skip, _PRIMES[i]) for i, p in enumerate(params)})
    return seeds


def fit(evaluate, start: dict, bounds: dict, steps: dict, params: list[str],
        explore: int = 64, refine: int = 6) -> tuple[dict, float, list[dict]]:
    """Deterministic global-ish search: Halton exploration, then coordinate descent +
    Nelder-Mead from the most promising points. Returns best point, score, and a trace."""
    trace: list[dict] = []
    seeds = [dict(start)]
    seeds += halton_seeds(params, bounds, explore)
    # cheap pass: score every seed, keep the best few for the expensive local search
    scored = sorted(((evaluate(_clamp(s, bounds))[0], i) for i, s in enumerate(seeds)),
                    reverse=True)
    for rank, (s0, i) in enumerate(scored[:refine]):
        seed = _clamp(seeds[i], bounds)
        x, s = coordinate_descent(evaluate, seed, bounds, steps)
        x, s2 = nelder_mead(evaluate, x, bounds, {k: v * 0.3 for k, v in steps.items()})
        if s2 > s:
            s = s2
        trace.append({"start": i, "rank": rank, "seed_score": s0, "score": s, "params": x})
    best = max(trace, key=lambda row: row["score"])
    x, s = best["params"], best["score"]
    # the landscape is flat-ish and multimodal, so polish the winner to a fixed point
    for _ in range(12):
        x2, s2 = coordinate_descent(evaluate, x, bounds, steps)
        x2, s2b = nelder_mead(evaluate, x2, bounds,
                              {k: v * 0.3 for k, v in steps.items()})
        if s2b > s2:
            s2 = s2b
        if s2 <= s + 1e-5:
            break
        x, s = x2, s2
    trace.append({"start": -1, "rank": -1, "seed_score": s, "score": s, "params": x})
    return x, s, trace


# --------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------
def parse_targets(text: str) -> dict[str, list[str]]:
    """`hat-far-navy:far,hat-near-teal:near` -> {'far': [...], 'near': [...]}."""
    groups: dict[str, list[str]] = {}
    for item in text.split(","):
        item = item.strip()
        if not item:
            continue
        name, _, group = item.partition(":")
        groups.setdefault(group or name, []).append(name)
    return groups


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--family", default="sunhat", choices=sorted(REGISTRY))
    ap.add_argument("--node", default=None,
                    help="family node id (defaults: hat, head, hair-main,hair-lock)")
    ap.add_argument("--nodes", default=None,
                    help="comma-separated ids for a family fitted as several instances "
                         "(e.g. hair-main,hair-lock); overrides --node")
    ap.add_argument("--spec", default=str(DEFAULT_SPEC))
    ap.add_argument("--targets", default=None,
                    help="comma list name:group (defaults to the family registry)")
    ap.add_argument("--occluders", default=None,
                    help="extra node ids to subtract, on top of the layer-derived occluders")
    ap.add_argument("--fixed", default=None,
                    help="pin parameters, e.g. droop=0 (for the flat-only comparison)")
    ap.add_argument("--starts", type=int, default=64,
                    help="Halton exploration points (deterministic)")
    ap.add_argument("--refine", type=int, default=6,
                    help="how many promising seeds get the expensive local search")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    node_text = a.nodes or a.node
    if node_text:
        node = [s.strip() for s in node_text.split(",") if s.strip()]
    elif a.family == "face":
        node = "head"
    elif a.family == "hair-mass":
        node = ["hair-main", "hair-lock"]
    else:
        node = "hat"

    spec_path = Path(a.spec).resolve()
    spec = rl.load_yaml(spec_path)
    fitter = FamilyFit(spec, spec_path.parent, a.family, node,
                       targets=parse_targets(a.targets) if a.targets else None,
                       occluders=a.occluders.split(",") if a.occluders else None)
    if a.fixed:
        for item in a.fixed.split(","):
            key, _, val = item.partition("=")
            if key not in fitter.bounds:
                raise SystemExit(f"fit-family: --fixed names unknown parameter {key!r}")
            fitter.bounds[key] = (float(val), float(val))
            fitter.start[key] = float(val)
    print(f"fit-family: {a.family} node={node} spec={spec_path.relative_to(ROOT)}")
    print("  groups:", {g: v["targets"] for g, v in fitter.groups.items()})
    score0, det0 = fitter.evaluate(fitter.start)
    print(f"  start   : mean IoU {score0:.4f}  {det0}  sil {fitter.silhouette_iou(fitter.start):.4f}")
    print("  occluders (derived from layers):", fitter.last_occluders)
    x, s, trace = fit(fitter.evaluate, fitter.start, fitter.bounds, fitter.steps,
                      fitter.params, explore=a.starts, refine=a.refine)
    _det, det = fitter.evaluate(x)
    sil = fitter.silhouette_iou(x)
    print(f"  fitted  : mean IoU {s:.4f}  {det}  sil {sil:.4f}")
    print("  occluders (derived from layers):", fitter.last_occluders)
    print("  search  : Halton exploration -> multi-start coordinate descent -> Nelder-Mead")
    for row in trace:
        print(f"    seed {row['start']:3d} raw {row['seed_score']:.4f} -> {row['score']:.4f}")
    print("  params  :")
    for k in fitter.params:
        print(f"    {k:10s} {fitter.start[k]:10.5f} -> {x[k]:10.5f}")
    out_nodes = [fitter.node_from_params(x, i) for i in range(len(fitter.node_ids))]
    for i, out_node in enumerate(out_nodes):
        if a.family == "hair-mass":
            keys = ["spine", "w", "side", "zig", "tips", "strands"]
        elif a.family == "face":
            keys = ["at", "rx", "ry", "cheek", "jaw", "chin-w", "turn"]
        elif a.family == "collar":
            keys = ["at", "w", "h", "neck", "v", "trim", "turn", "tilt"]
        elif a.family == "bow":
            keys = ["at", "w", "h", "spread", "tilt", "loop-len", "loop-w", "knot-w",
                    "knot-h", "tail-angle", "tail-len", "tail-w", "tail2-angle", "tail2-len",
                    "tail2-w"]
        elif a.family == "arm":
            keys = ["spine", "w", "sleeve", "puff", "cuff-at", "cuff-h", "cuff-pad"]
        else:
            keys = ["brim", "crown", "tilt", "lift", "drop", "crown-h", "flat",
                    "front", "rim", "droop"]
        print(f"  node[{i}] :", {k: out_node.get(k) for k in keys if k in out_node})
    if a.out:
        Path(a.out).write_text(json.dumps({
            "family": a.family, "node": node, "spec": str(spec_path),
            "start": fitter.start, "start_iou": score0, "start_groups": det0,
            "fitted": x, "fitted_iou": s, "fitted_groups": det, "silhouette_iou": sil,
            "groups": {g: v["targets"] for g, v in fitter.groups.items()},
            "occluders": fitter.last_occluders,
            "search": "Halton exploration -> multi-start coordinate descent -> Nelder-Mead",
            "trace": trace,
        }, indent=1) + "\n")
        print(f"  wrote   : {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
