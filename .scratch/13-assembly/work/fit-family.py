#!/usr/bin/env python3
"""fit-family.py — extract object-family parameters from a frozen teacher mask.

The teacher loop (docs/drawing/abstraction.md, STATUS D24) is: measure a subject, use the
measurement to FIT a family, then close the reference and keep only the fitted parameters. This
instrument is the "fit" step. It takes a vocabulary family (currently `sunhat`), a starting
parameter set, and one or more frozen `traced` masks, and searches the family's parameters to
maximise the IoU between the family's own rendered masks and the teacher's masks.

Honesty hinge (invariant 4): the target is the TEACHER'S MEASUREMENT — the frozen traced outline.
It is never `edge_f1`, `color_dist`, or the baseline comparison. Nudging a parameter until an
evaluation metric rises is the optimizer regression the project forbids; fitting a family to the
traced outline is parameter extraction. This tool therefore never looks at image.jpg at all: it
opens the traced sidecars, which carry no raster.

Grouping. A family emits several sub-shapes, and one traced mask may be the union of more than one
of them. For `sunhat` the teacher's `hat-far-navy` is the crown AND the far brim in one connected
navy mass, so the fit target for it is `union(crown-dome, brim-far)`; the two teal masks are the
split top surface, so their union is matched by `brim-near`. Occluders (shapes painted above the
hat, e.g. the front hair) are subtracted from the family mask before the IoU, so the comparison is
visible-to-visible.

Search. Deterministic multi-start coordinate descent followed by a dependency-free Nelder-Mead
polish. Same spec + same sidecars -> same fitted parameters, bit for bit.

Usage:
  .venv/bin/python .scratch/13-assembly/work/fit-family.py \
      --family sunhat --node hat \
      [--spec .scratch/13-assembly/work/spec.yaml] \
      [--targets hat-far-navy:far,hat-near-teal:near,hat-near-teal-right:near] \
      [--occluders hair-mass] [--out /tmp/fit.json]
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
SUNHAT_OCCLUDERS = ["hair-mass"]

REGISTRY = {
    "sunhat": {"params": SUNHAT_PARAMS, "bounds": SUNHAT_BOUNDS, "steps": SUNHAT_STEPS,
               "groups": SUNHAT_GROUPS, "occluders": SUNHAT_OCCLUDERS},
}


def family_kind_of(node: dict) -> str | None:
    """The vocabulary kind of a spec node, if it is a registered family."""
    for key in node:
        if key in REGISTRY:
            return key
    return None


# --------------------------------------------------------------------------------------
# masks
# --------------------------------------------------------------------------------------
def rasterize(node: dict, shape: tuple[int, int]) -> np.ndarray:
    """A full-canvas uint8 mask of one emitted compiled node (poly or ellipse)."""
    h, w = shape
    mask = np.zeros((h, w), np.uint8)
    if "poly" in node:
        pts = np.round(np.asarray(node["poly"], float)).astype(np.int32)
        cv2.fillPoly(mask, [pts], 1)
    elif "ellipse" in node:
        cx, cy = node["at"]
        axes = (int(round(node["rx"])), int(round(node["ry"])))
        cv2.ellipse(mask, (int(round(cx)), int(round(cy))), axes,
                    float(node.get("rot", 0)), 0, 360, 1, -1)
    return mask


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

    def __init__(self, spec: dict, base_dir: Path, kind: str, node_id: str,
                 targets: dict[str, list[str]] | None = None,
                 occluders: list[str] | None = None):
        reg = REGISTRY[kind]
        self.kind = kind
        self.node_id = node_id
        self.params = reg["params"]
        self.bounds = reg["bounds"]
        self.steps = reg["steps"]
        self.spec = spec
        self.base_dir = Path(base_dir)
        self.frame = spec["frame"]
        self.shape = (int(self.frame["h"]), int(self.frame["w"]))

        # the original family node + its host, copied so the search can rewrite parameters
        raw_family = self._raw_family()
        if raw_family is None:
            raise SystemExit(f"fit-family: no {kind} node {node_id!r} in the spec")
        self.family_node = copy.deepcopy(raw_family)
        host_id = str(raw_family.get("host"))
        self.host_node = None
        for raw in spec["draw"]:
            if str(next(iter(raw.values()))) == host_id:
                self.host_node = copy.deepcopy(raw)
        if self.host_node is None:
            raise SystemExit(f"fit-family: family {node_id!r} host {host_id!r} not found in spec")

        # grouping: default from the registry, overridable per run
        self.groups = copy.deepcopy(reg["groups"])
        if targets:
            for name, target_list in targets.items():
                self.groups[name]["targets"] = target_list
        self.occluders = reg["occluders"] if occluders is None else occluders

        # teacher masks
        traced_dir = self.base_dir / "traced"
        self.target_masks: dict[str, list[np.ndarray]] = {}
        for gname, g in self.groups.items():
            self.target_masks[gname] = [sidecar_mask(traced_dir / f"{t}.json", self.shape)
                                        for t in g["targets"]]
        occ = np.zeros(self.shape, np.uint8)
        for name in self.occluders:
            occ |= sidecar_mask(traced_dir / f"{name}.json", self.shape)
        self.occluder = occ > 0

        # starting vector, read from the live spec so the search begins where the drawing is.
        # Parameters may be relational (`2.905*head.w`), so resolve a host+family spec once and
        # evaluate each expression against the resulting anchor environment.
        probe = {"frame": self.frame, "vars": spec.get("vars", {}),
                 "draw": [self.host_node, self.family_node]}
        _emit, env, _notes, _layers = rl.resolve(probe, base_dir=self.base_dir)
        self.start = {p: self._param_from_node(p, self.family_node, env) for p in self.params}

    def _raw_family(self) -> dict | None:
        """The family node from the ORIGINAL spec (used to find the host before copying)."""
        for raw in self.spec["draw"]:
            if family_kind_of(raw) == self.kind and str(raw[self.kind]) == self.node_id:
                return raw
        return None

    @staticmethod
    def _expr(value, env: dict) -> float:
        return rl.eval_expr(value, env) if isinstance(value, str) else float(value)

    @classmethod
    def _param_from_node(cls, param: str, node: dict, env: dict) -> float:
        front = node.get("front", [0.05, 0.45])
        if param == "front0":
            return cls._expr(front[0], env)
        if param == "front1":
            return cls._expr(front[1], env)
        if param == "droop":
            return cls._expr(node.get("droop", 0.0), env)
        return cls._expr(node[param], env)

    def node_from_params(self, x: dict) -> dict:
        node = copy.deepcopy(self.family_node)
        for p in self.params:
            if p not in ("front0", "front1"):
                node[p] = float(x[p])
        node["front"] = [float(x["front0"]), float(x["front1"])]
        return node

    def render(self, x: dict) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        """Resolve a minimal spec (host + family) and return the family's own visible masks.

        Returns (all-shapes mask, {group: mask}) with the occluders already subtracted.
        """
        minimal = {
            "frame": self.frame,
            "vars": self.spec.get("vars", {}),
            "draw": [self.host_node, self.node_from_params(x)],
        }
        emit, _env, _notes, _layers = rl.resolve(minimal, base_dir=self.base_dir)
        allm = np.zeros(self.shape, np.uint8)
        group_masks = {g: np.zeros(self.shape, np.uint8) for g in self.groups}
        for node in emit:
            sid = node.get("blob") or node.get("ellipse") or node.get("stroke") or ""
            if "-pom" in sid or node.get("full"):
                continue
            m = rasterize(node, self.shape)
            allm |= m
            for gname, g in self.groups.items():
                if any(sid.endswith(suf) for suf in g["shapes"]):
                    group_masks[gname] |= m
        keep = ~self.occluder
        return (allm > 0) & keep, {g: (m > 0) & keep for g, m in group_masks.items()}

    def evaluate(self, x: dict) -> tuple[float, dict[str, float]]:
        """Mean group IoU (the fitness) and the per-group breakdown."""
        try:
            _all, groups = self.render(x)
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
        """Extra report: whole visible hat vs the union of every traced hat mask."""
        allm, _ = self.render(x)
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


_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]


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
    ap.add_argument("--node", default="hat")
    ap.add_argument("--spec", default=str(DEFAULT_SPEC))
    ap.add_argument("--targets", default=None,
                    help="comma list name:group (defaults to the family registry)")
    ap.add_argument("--occluders", default=None,
                    help="comma list of traced nodes painted above the family")
    ap.add_argument("--fixed", default=None,
                    help="pin parameters, e.g. droop=0 (for the flat-only comparison)")
    ap.add_argument("--starts", type=int, default=64,
                    help="Halton exploration points (deterministic)")
    ap.add_argument("--refine", type=int, default=6,
                    help="how many promising seeds get the expensive local search")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)

    spec_path = Path(a.spec).resolve()
    spec = rl.load_yaml(spec_path)
    fitter = FamilyFit(spec, spec_path.parent, a.family, a.node,
                       targets=parse_targets(a.targets) if a.targets else None,
                       occluders=a.occluders.split(",") if a.occluders else None)
    if a.fixed:
        for item in a.fixed.split(","):
            key, _, val = item.partition("=")
            if key not in fitter.bounds:
                raise SystemExit(f"fit-family: --fixed names unknown parameter {key!r}")
            fitter.bounds[key] = (float(val), float(val))
            fitter.start[key] = float(val)
    print(f"fit-family: {a.family} node={a.node} spec={spec_path.relative_to(ROOT)}")
    print("  groups:", {g: v["targets"] for g, v in fitter.groups.items()})
    print("  occluders:", fitter.occluders)
    score0, det0 = fitter.evaluate(fitter.start)
    print(f"  start   : mean IoU {score0:.4f}  {det0}  sil {fitter.silhouette_iou(fitter.start):.4f}")

    x, s, trace = fit(fitter.evaluate, fitter.start, fitter.bounds, fitter.steps,
                      fitter.params, explore=a.starts, refine=a.refine)
    _det, det = fitter.evaluate(x)
    sil = fitter.silhouette_iou(x)
    print(f"  fitted  : mean IoU {s:.4f}  {det}  sil {sil:.4f}")
    print("  search  : Halton exploration -> multi-start coordinate descent -> Nelder-Mead")
    for row in trace:
        print(f"    seed {row['start']:3d} raw {row['seed_score']:.4f} -> {row['score']:.4f}")
    print("  params  :")
    for k in fitter.params:
        print(f"    {k:8s} {fitter.start[k]:10.5f} -> {x[k]:10.5f}")
    node = fitter.node_from_params(x)
    print("  node    :", {k: (round(v, 4) if isinstance(v, float) else v)
                          for k, v in node.items() if k in fitter.params or k == "front"})
    if a.out:
        Path(a.out).write_text(json.dumps({
            "family": a.family, "node": a.node, "spec": str(spec_path),
            "start": fitter.start, "start_iou": score0, "start_groups": det0,
            "fitted": x, "fitted_iou": s, "fitted_groups": det, "silhouette_iou": sil,
            "groups": {g: v["targets"] for g, v in fitter.groups.items()},
            "occluders": fitter.occluders,
            "search": "Halton exploration -> multi-start coordinate descent -> Nelder-Mead",
            "trace": trace,
        }, indent=1) + "\n")
        print(f"  wrote   : {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
