"""Strict small scene schema, observable selections and optimistic edit transactions."""
from __future__ import annotations

import copy
import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path

from .geometry import bounds, geometry_issues, lock_rows, outline, resolve_root


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def fingerprint(scene):
    return hashlib.sha256(canonical(scene).encode()).hexdigest()


@lru_cache(maxsize=1)
def engine_fingerprint():
    """An unchanged scene can render differently after a primitive implementation edit."""
    directory = Path(__file__).parent
    sources = {str(p.relative_to(directory.parent)): p.read_text(encoding="utf-8")
               for p in sorted(directory.glob("*.py"))}
    for name in ("vector_visibility.py", "articulated_construction.py", "renderer.py"):
        sources[name] = (directory.parent / name).read_text(encoding="utf-8")
    return hashlib.sha256(canonical(sources).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    # Replace, never partially overwrite a working scene.
    temp = p.with_suffix(p.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    temp.replace(p)


def number(value, label, low, high):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label}: expected a finite number")
    if not low <= value <= high:
        raise ValueError(f"{label}: must be between {low} and {high}")


def keys(value, allowed, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label}: expected an object")
    unknown = set(value) - set(allowed)
    if unknown:
        raise ValueError(f"{label}: unknown fields {sorted(unknown)}")


def validate(scene):
    keys(scene, ("format", "canvas", "background", "nodes"), "scene")
    if scene.get("format") != "learn-draw/studio-1":
        raise ValueError("scene: unsupported format")
    canvas = scene.get("canvas", [640, 640])
    if not isinstance(canvas, list) or len(canvas) != 2:
        raise ValueError("canvas: needs width and height")
    for n in canvas:
        number(n, "canvas", 64, 4096)
    color(scene.get("background", "#f5eee4"))
    if not isinstance(scene.get("nodes"), list) or not 1 <= len(scene["nodes"]) <= 24:
        raise ValueError("scene: needs 1–24 nodes")
    ids = set()
    for node in scene["nodes"]:
        keys(node, ("id", "kind", "intent", "at", "length", "width", "width_side", "angle", "sweep", "depth",
                    "depth_slope", "palette", "edits"), "node")
        sid = node.get("id", "")
        if not isinstance(sid, str) or not sid or not sid.replace("-", "").replace("_", "").isalnum() or sid in ids:
            raise ValueError("node: ID must be unique and contain letters, digits, - or _")
        ids.add(sid)
        if node.get("kind") != "hair-lock":
            raise ValueError(f"{sid}: supported kind is hair-lock")
        if node.get("width_side", "both") not in ("both", "left", "right"):
            raise ValueError(f"{sid}.width_side: both/left/right")
        if not isinstance(node.get("intent"), str) or not node["intent"].strip():
            raise ValueError(f"{sid}: intent is required")
        for name, default, low, high in (("length", .68, .1, 1.2), ("width", .19, .03, .65),
                                       ("angle", -8, -180, 180), ("sweep", .16, -.45, .45),
                                       ("depth", 0, -100, 100), ("depth_slope", 0, -10, 10)):
            number(node.get(name, default), f"{sid}.{name}", low, high)
        at = node.get("at", {})
        keys(at, ("anchor", "offset"), f"{sid}.at")
        if at.get("anchor", "upper_center") not in ("upper_center", "center", "upper_left", "upper_right"):
            raise ValueError(f"{sid}: unknown canvas anchor")
        offset = at.get("offset", [0, 0])
        if not isinstance(offset, list) or len(offset) != 2:
            raise ValueError(f"{sid}.offset: needs two canvas-relative values")
        for n in offset:
            number(n, "offset", -2, 2)
        palette = node.get("palette", {})
        keys(palette, ("fill", "shade", "light", "ink"), f"{sid}.palette")
        for c in palette.values():
            color(c)
        if not isinstance(node.get("edits", []), list):
            raise ValueError(f"{sid}.edits: expected a list")
        for edit in node.get("edits", []):
            keys(edit, ("side", "at", "radius", "dx", "dy", "reason"), "edit")
            if edit.get("side") not in ("left", "right"):
                raise ValueError("edit.side: left or right")
            number(edit.get("at"), "edit.at", .01, .99)
            number(edit.get("radius"), "edit.radius", .025, .49)
            if edit["at"] - edit["radius"] <= 0 or edit["at"] + edit["radius"] >= 1:
                raise ValueError("edit influence must stay inside root/tip locks")
            for axis in ("dx", "dy"):
                number(edit.get(axis), "edit." + axis, -2, 2)
            if not isinstance(edit.get("reason"), str) or not edit["reason"].strip():
                raise ValueError("edit: state a drawing reason")
        problems = geometry_issues(lock_rows(node, canvas))
        if problems:
            raise ValueError(f"{sid}: " + "; ".join(problems))
    return scene


def color(value):
    if not isinstance(value, str) or len(value) != 7 or value[0] != "#":
        raise ValueError("colour: expected #rrggbb")
    try:
        int(value[1:], 16)
    except ValueError:
        raise ValueError("colour: expected #rrggbb") from None


def node_by_id(scene, sid):
    for node in scene["nodes"]:
        if node["id"] == sid:
            return node
    raise ValueError(f"unknown object {sid!r}")


def select(scene, sid, side="left", at=.55, radius=.30):
    validate(scene)
    # Validate the selection through the same local operation contract.
    selection = dict(base=fingerprint(scene), engine=engine_fingerprint(), object=sid, side=side, at=at, radius=radius)
    node = node_by_id(scene, sid)
    probe = copy.deepcopy(scene)
    node_by_id(probe, sid).setdefault("edits", []).append(dict(side=side, at=at, radius=radius, dx=0, dy=0, reason="selection"))
    validate(probe)
    rows = lock_rows(node, scene.get("canvas", [640, 640]))
    region = [getattr(r, side) for r in rows if abs(r.t - at) <= radius]
    selection.update(bounds=bounds(region), object_bounds=bounds(outline(rows)),
                     locks={"root": resolve_root(node, scene.get("canvas", [640, 640])), "tip": rows[-1].left},
                     units="push amount = fraction of this object's nominal full width; directions are screen directions")
    return selection


def preview(scene, selection, direction, amount, reason):
    validate(scene)
    if selection["base"] != fingerprint(scene):
        raise ValueError("stale selection: inspect the current scene again")
    if selection.get("engine") != engine_fingerprint():
        raise ValueError("stale selection: primitive implementation changed; inspect again")
    if direction not in ("left", "right", "up", "down"):
        raise ValueError("direction: left/right/up/down")
    number(amount, "amount", 0, 2)
    dx, dy = {"left": (-amount, 0), "right": (amount, 0), "up": (0, -amount), "down": (0, amount)}[direction]
    candidate = copy.deepcopy(scene)
    node = node_by_id(candidate, selection["object"])
    edit = {k: selection[k] for k in ("side", "at", "radius")}
    edit.update(dx=dx, dy=dy, reason=reason)
    node.setdefault("edits", []).append(edit)
    validate(candidate)
    return dict(base=fingerprint(scene), engine=engine_fingerprint(), result=fingerprint(candidate), scene=candidate,
                selection=selection, operation=edit)


def accept(path, candidate):
    scene = validate(read(path))
    if candidate["base"] != fingerprint(scene):
        raise ValueError("stale preview: working scene has changed; preview again")
    if candidate.get("engine") != engine_fingerprint():
        raise ValueError("stale preview: primitive implementation changed; preview again")
    validate(candidate["scene"])
    if candidate["result"] != fingerprint(candidate["scene"]):
        raise ValueError("candidate hash mismatch")
    p = Path(path)
    history = p.parent / (p.stem + ".history")
    write(history / (fingerprint(scene) + ".json"), scene)
    journal_path = history / "journal.json"
    journal = read(journal_path) if journal_path.exists() else []
    journal.append({k: candidate[k] for k in ("base", "result", "operation")})
    write(journal_path, journal)
    write(p, candidate["scene"])
    return candidate["result"]


def undo(path):
    p = Path(path)
    scene = validate(read(p))
    history = p.parent / (p.stem + ".history")
    journal_path = history / "journal.json"
    journal = read(journal_path) if journal_path.exists() else []
    if not journal:
        raise ValueError("no accepted edit to undo")
    item = journal[-1]
    if item["result"] != fingerprint(scene):
        raise ValueError("scene changed outside edit history; refusing unsafe undo")
    previous = validate(read(history / (item["base"] + ".json")))
    if fingerprint(previous) != item["base"]:
        raise ValueError("history hash mismatch")
    write(p, previous)
    write(journal_path, journal[:-1])
    return fingerprint(previous)
