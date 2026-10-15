#!/usr/bin/env python3
"""Compile the frozen exercise21 flat/camber matrix with durable per-panel checkpoints."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import cv2
import numpy as np
import ribbon_surface as surface
from ribbon_family import Camera, RibbonSpec, camera_basis, centerline, project

PLAN = Path(__file__).resolve().parent / "cases.json"
EVIDENCE = Path(__file__).resolve().parents[1] / "evidence"
PANEL_WIDTH, PANEL_HEIGHT = 480, 320
BOARD_WIDTH, MARGIN, GAP = 1020, 20, 14
PANELS = (("flat", 0.0), ("camber-035", 0.35))
SVG_NS = "http://www.w3.org/2000/svg"


def _bytes_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _file_hash(path: Path) -> str:
    return _bytes_hash(path.read_bytes())


def _renderer_provenance() -> dict:
    """Bind cache entries to this builder, draw.py, and the installed browser identity."""
    import draw
    browser = Path(draw.CHROME).resolve()
    result = subprocess.run([str(browser), "--version"], capture_output=True, text=True,
                            timeout=5, check=True)
    version = (result.stdout or result.stderr).strip()
    if not version:
        raise RuntimeError(f"Chromium did not report a version: {browser}")
    return {"builder_sha256": _file_hash(Path(__file__).resolve()),
            "draw_py_sha256": _file_hash(SCRIPTS / "draw.py"),
            "chromium": {"path": str(browser), "version": version}}


def _canonical_hash(value) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return _bytes_hash(payload.encode("utf-8"))


def _safe(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "-", value)


def _record(path: Path, event: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, sort_keys=True, allow_nan=False) + "\n")
        stream.flush()


def _frozen_cases(plan: dict) -> list[dict]:
    if plan.get("schema") != 1 or plan.get("frozen_camber") != 0.35:
        raise ValueError("exercise case plan or preselected camber changed")
    for key in ("family_cases", "failed_learner", "old_ribbon_generator", "visibility_resolver"):
        entry = plan["sources"][key]
        if _file_hash(ROOT / entry["path"]) != entry["sha256"]:
            raise ValueError(f"read-only source hash changed: {entry['path']}")
    old_cases_path = ROOT / plan["sources"]["family_cases"]["path"]
    old_cases = json.loads(old_cases_path.read_text(encoding="utf-8"))
    old_by_name = {case["name"]: case for case in old_cases["cases"]}
    learner_path = ROOT / plan["sources"]["failed_learner"]["path"]
    learner_raw = json.loads(learner_path.read_text(encoding="utf-8"))
    for item in plan["cases"]:
        source_name = item["source"].get("case_name")
        input_spec = learner_raw if source_name is None else old_by_name[source_name]["ribbon"]
        if _canonical_hash(input_spec) != item["source_spec_sha256"]:
            raise ValueError(f"frozen input hash mismatch for {item['name']}")
        if item["ribbon"] != input_spec:
            raise ValueError(f"candidate input differs from frozen source: {item['name']}")
        camera_hash = _canonical_hash(item["camera"])
        expected_camera = {camera["name"]: _canonical_hash(camera)
                           for camera in plan["cameras"]}[item["camera"]["name"]]
        if camera_hash != expected_camera or item.get("camera_sha256") != camera_hash:
            raise ValueError(f"camera changed or camera hash is stale for {item['name']}")
        if source_name is None and _file_hash(learner_path) != item["input_file_sha256"]:
            raise ValueError("failed learner input file hash changed")
    return plan["cases"]


def _measure_geometry(spec: RibbonSpec, meshes: tuple, cameras: list[dict]) -> dict:
    """Record physical versus projected width around the original half-twist facing-zero event."""
    station = 0.5
    samples = tuple(-1.0 + 2.0 * index / 512 for index in range(513))
    rows = []
    for camera_data in cameras:
        camera = Camera(camera_data["name"], camera_data["yaw"], camera_data["pitch"])
        facing = camera_basis(camera)[2]
        for condition, mesh in zip(("flat", "camber-035"), meshes):
            section = surface.surface_points(spec, mesh, station, samples)
            world_length = sum(math.dist(a, b) for a, b in zip(section, section[1:]))
            projected = [project(point, camera) for point in section]
            before = project(surface.surface_point(spec, mesh, station - 1e-3, 0), camera)
            after = project(surface.surface_point(spec, mesh, station + 1e-3, 0), camera)
            tangent = (after[0] - before[0], after[1] - before[1])
            tangent_length = math.hypot(*tangent)
            if tangent_length <= 1e-12:
                raise ValueError("projected route tangent is singular in width diagnostic")
            perpendicular = (-tangent[1] / tangent_length, tangent[0] / tangent_length)
            across = [point[0] * perpendicular[0] + point[1] * perpendicular[1]
                      for point in projected]
            facing_values = []
            for triangle in mesh.triangles:
                u = sum(point[0] for point in triangle.uv) / 3
                if abs(u - station) > 1.0 / (len(mesh.base.stations) - 1):
                    continue
                a, b, c = triangle.points
                edge_a, edge_b = tuple(b[i] - a[i] for i in range(3)), tuple(c[i] - a[i] for i in range(3))
                normal = (edge_a[1] * edge_b[2] - edge_a[2] * edge_b[1],
                          edge_a[2] * edge_b[0] - edge_a[0] * edge_b[2],
                          edge_a[0] * edge_b[1] - edge_a[1] * edge_b[0])
                magnitude = math.sqrt(sum(value * value for value in normal))
                if magnitude:
                    facing_values.append(sum(normal[i] * facing[i] for i in range(3)) / magnitude)
            old_center = centerline(spec, station)
            finite_center = surface.surface_point(spec, mesh, station, 0)
            rows.append({
                "camera": camera_data,
                "condition": condition,
                "u": station,
                "material_arc_world_units": world_length,
                "requested_continuous_width_world_units": spec.width * (
                    1 + (spec.tip_ratio - 1) * station),
                "projected_width_perpendicular_to_route_world_units": max(across) - min(across),
                "center_matches_frozen_route_at_station": all(
                    abs(finite_center[i] - old_center[i]) < 1e-12 for i in range(3)),
                "actual_normal_view_dot_range": [min(facing_values), max(facing_values)],
                "facing_samples": len(facing_values),
            })
    return {"purpose": "mechanism measurement, not a pixel/objective fit",
            "event": "original positive half-twist front facing-zero station u=0.5",
            "sampling": {"u_intervals": len(meshes[0].base.stations) - 1,
                         "v_dense_intervals": 512},
            "panels": rows}


def _cache_paths(index: int, case: dict, kind: str) -> tuple[Path, Path, Path, Path]:
    stem = f"case-{index:02d}-{_safe(case['name'])}-{kind}"
    return (EVIDENCE / "cache" / f"{stem}.svg",
            EVIDENCE / "cache" / f"{stem}.json",
            EVIDENCE / "panels" / f"{stem}.svg",
            EVIDENCE / "panels" / f"{stem}.png")


def _cache_key(index: int, case: dict, kind: str, module_hash: str,
               plan_hash: str) -> str:
    return _canonical_hash({
        "case_index": index,
        "case_name": case["name"],
        "source_spec_sha256": case["source_spec_sha256"],
        "input_file_sha256": case.get("input_file_sha256"),
        "camera": case["camera"],
        "support_camber": dict(PANELS)[kind],
        "u_intervals": plan["sampling"]["u_intervals"],
        "v_intervals": plan["sampling"]["v_intervals"],
        "view_size": [PANEL_WIDTH, PANEL_HEIGHT],
        "renderer_sha256": module_hash,
        "builder_sha256": provenance["builder_sha256"],
        "draw_py_sha256": provenance["draw_py_sha256"],
        "chromium": provenance["chromium"],
        "case_plan_sha256": plan_hash,
    })


def _write_panel(index: int, case: dict, kind: str, svg: str, module_hash: str,
                 plan_hash: str, progress: Path) -> dict:
    cache_svg, cache_meta, panel_svg, panel_png = _cache_paths(index, case, kind)
    cache_svg.parent.mkdir(parents=True, exist_ok=True)
    panel_svg.parent.mkdir(parents=True, exist_ok=True)
    cache_svg.write_text(svg, encoding="utf-8")
    panel_svg.write_text(svg, encoding="utf-8")
    from draw import render
    render(str(panel_svg), str(panel_png), size=(PANEL_WIDTH, PANEL_HEIGHT))
    pixels = cv2.imread(str(panel_png), cv2.IMREAD_COLOR)
    if pixels is None or pixels.shape[:2] != (PANEL_HEIGHT, PANEL_WIDTH):
        raise RuntimeError(f"Chromium returned an invalid PNG: {panel_png}")
    background = np.array((239, 245, 244), dtype=np.uint8)
    occupied = int(np.count_nonzero(np.any(np.abs(pixels.astype(np.int16) - background) > 8,
                                           axis=2)))
    if occupied == 0:
        raise RuntimeError(f"browser raster contains only its background: {panel_png}")
    metadata = {
        "case_index": index,
        "case": case["name"],
        "condition": case["condition"],
        "input": case["source"],
        "input_sha256": case["source_spec_sha256"],
        "camera": case["camera"],
        "camber": dict(PANELS)[kind],
        "sampling": {"u_intervals": plan["sampling"]["u_intervals"],
                     "v_intervals": plan["sampling"]["v_intervals"]},
        "renderer_sha256": module_hash,
        "builder_sha256": provenance["builder_sha256"],
        "draw_py_sha256": provenance["draw_py_sha256"],
        "chromium": provenance["chromium"],
        "case_plan_sha256": plan_hash,
        "cache_key": _cache_key(index, case, kind, module_hash, plan_hash),
        "svg_sha256": _file_hash(panel_svg),
        "png_sha256": _file_hash(panel_png),
        "svg_bytes": panel_svg.stat().st_size,
        "png_bytes": panel_png.stat().st_size,
        "nonbackground_pixels": occupied,
    }
    cache_meta.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n",
                          encoding="utf-8")
    _record(progress, {"event": "panel_saved", **metadata})
    return metadata


def _reuse_panel(index: int, case: dict, kind: str, module_hash: str,
                 plan_hash: str, progress: Path) -> dict | None:
    cache_svg, cache_meta, panel_svg, panel_png = _cache_paths(index, case, kind)
    if not (cache_svg.is_file() and cache_meta.is_file() and panel_svg.is_file()
            and panel_png.is_file()):
        return None
    metadata = json.loads(cache_meta.read_text(encoding="utf-8"))
    expected_key = _cache_key(index, case, kind, module_hash, plan_hash)
    if metadata.get("cache_key") != expected_key or _file_hash(cache_svg) != metadata.get("svg_sha256"):
        return None
    if _file_hash(panel_svg) != metadata.get("svg_sha256") or _file_hash(panel_png) != metadata.get("png_sha256"):
        return None
    _record(progress, {"event": "panel_reused", "case": case["name"], "condition": kind,
                      "svg_sha256": metadata["svg_sha256"], "png_sha256": metadata["png_sha256"]})
    return metadata


def _panel_content(path: Path) -> str:
    source = path.read_text(encoding="utf-8")
    if "<ns0:" in source:
        raise ValueError(f"namespace-prefixed panel cannot be embedded: {path}")
    start = source.find(">") + 1
    end = source.rfind("</svg>")
    if start == 0 or end <= start:
        raise ValueError(f"panel is not a complete SVG document: {path}")
    return source[start:end]


def _board(labelled: bool, case_rows: list[dict], metadata: list[dict], out: Path,
           plan_hash: str, module_hash: str) -> dict:
    width = BOARD_WIDTH
    panel_width = (width - 2 * MARGIN - GAP) // 2
    panel_height = PANEL_HEIGHT
    heading = 42 if labelled else 10
    row_caption = 16 if labelled else 0
    height = (heading + MARGIN + len(case_rows) * (panel_height + row_caption)
              + (len(case_rows) - 1) * GAP + MARGIN)
    parts = [f'<svg xmlns="{SVG_NS}" viewBox="0 0 {width} {height}">',
             '<!-- Paired flat/camber support experiment; same local art and camera per row. -->',
             f'<rect id="board-paper" width="{width}" height="{height}" fill="#e8eeea"/>']
    if labelled:
        parts.append('<text id="board-title" x="20" y="24" font-family="sans-serif" '
                     'font-size="16" font-weight="600" fill="#263b4b">Ribbon support · '
                     'ruled cross-section / transverse camber 0.35</text>')
        parts.append('<text id="col-flat" x="25" y="39" font-family="sans-serif" '
                     'font-size="10" fill="#42596a">flat control · original support</text>')
        parts.append('<text id="col-camber" x="535" y="39" font-family="sans-serif" '
                     'font-size="10" fill="#42596a">curved support · one frozen camber</text>')
    panel_manifest = []
    for index, case in enumerate(case_rows):
        y = heading + MARGIN + index * (panel_height + row_caption + GAP) + row_caption
        for column, (kind, _camber) in enumerate(PANELS):
            _cache_svg, _meta, panel_svg, _panel_png = _cache_paths(index, case, kind)
            x = MARGIN + column * (panel_width + GAP)
            prefix = f"row-{index:02d}-{_safe(case['name'])}-{kind}"
            parts.append(f'<g id="{prefix}-group" transform="translate({x} {y})">'
                         f'{_panel_content(panel_svg)}</g>')
            panel_meta = next(item for item in metadata
                              if item["case_index"] == index and item["camber"] == dict(PANELS)[kind])
            panel_manifest.append({"case": case["name"], "condition": kind,
                                   "source_spec_sha256": case["source_spec_sha256"],
                                   "camera": case["camera"],
                                   "svg_sha256": panel_meta["svg_sha256"],
                                   "png_sha256": panel_meta["png_sha256"],
                                   "support_camber": panel_meta["camber"]})
        if labelled:
            parts.append(f'<text id="row-label-{index:02d}" x="{MARGIN + 6}" y="{y - 4}" '
                         'font-family="sans-serif" font-size="9" fill="#263b4b">'
                         f'{escape(case["name"])} · {escape(case["camera"]["name"])} · '
                         f'{escape(case["condition"])}</text>')
    parts.append("</svg>")
    svg = "\n".join(parts)
    if "<ns0:" in svg:
        raise ValueError("comparison board contains prefixed inline SVG children")
    root = ET.fromstring(svg)
    ids = [node.attrib["id"] for node in root.iter() if "id" in node.attrib]
    if len(ids) != len(set(ids)):
        raise ValueError("comparison board contains duplicate SVG IDs")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")
    from draw import render
    png = out.with_suffix(".png")
    render(str(out), str(png), size=(width, height))
    pixels = cv2.imread(str(png), cv2.IMREAD_COLOR)
    if pixels is None or pixels.shape[:2] != (height, width):
        raise RuntimeError(f"Chromium returned an invalid board PNG: {png}")
    background = np.array((234, 238, 232), dtype=np.uint8)
    occupied = int(np.count_nonzero(np.any(np.abs(pixels.astype(np.int16) - background) > 8,
                                           axis=2)))
    if occupied == 0:
        raise RuntimeError(f"board PNG contains only its background: {png}")
    manifest = {"labelled": labelled, "case_plan_sha256": plan_hash,
                "renderer_sha256": module_hash, "renderer_provenance": provenance,
                "view_size": [width, height],
                "svg_sha256": _file_hash(out), "png_sha256": _file_hash(png),
                "svg_bytes": out.stat().st_size, "png_bytes": png.stat().st_size,
                "nonbackground_pixels": occupied, "panel_manifest": panel_manifest}
    out.with_name(out.stem + "-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    global plan, EVIDENCE, provenance
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="profile/cache only the first N frozen cases; 1 profiles one pair")
    parser.add_argument("--plan", type=Path, default=PLAN)
    parser.add_argument("--evidence", type=Path, default=EVIDENCE)
    parser.add_argument("--progress", type=Path,
                        default=Path(__file__).resolve().parent / "build-progress.jsonl")
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    rows = _frozen_cases(plan)
    if args.limit is not None and not 1 <= args.limit <= len(rows):
        raise SystemExit("--limit must select between 1 and the frozen case count")
    rows = rows[:args.limit] if args.limit is not None else rows
    EVIDENCE = args.evidence
    module_hash, plan_hash = _file_hash(SCRIPTS / "ribbon_surface.py"), _file_hash(args.plan)
    provenance = _renderer_provenance()
    _record(args.progress, {"event": "run_started", "utc": datetime.now(timezone.utc).isoformat(),
                            "case_plan_sha256": plan_hash, "renderer_sha256": module_hash,
                            "renderer_provenance": provenance,
                            "case_rows": len(rows), "pairs": len(rows),
                            "panel_size": [PANEL_WIDTH, PANEL_HEIGHT],
                            "sampling": plan["sampling"]})
    outputs = []
    total_started = time.monotonic()
    for index, case in enumerate(rows):
        camera_data = case["camera"]
        camera = Camera(camera_data["name"], camera_data["yaw"], camera_data["pitch"])
        spec = RibbonSpec.from_mapping(case["ribbon"])
        u_count = plan["sampling"]["u_intervals"]
        v_count = plan["sampling"]["v_intervals"]
        pair_start = time.monotonic()
        flat = surface.build_surface(spec, 0.0, u_count, v_count)
        curved = surface.build_surface(spec, plan["frozen_camber"], u_count, v_count)
        pair_triangles = [len(flat.triangles), len(curved.triangles)]
        if index == 0:
            diagnostic = _measure_geometry(spec, (flat, curved), plan["cameras"])
            diagnostic.update({"case_plan_sha256": plan_hash,
                               "renderer_sha256": module_hash})
            diagnostic_path = EVIDENCE / "geometry-mechanism.json"
            diagnostic_path.parent.mkdir(parents=True, exist_ok=True)
            diagnostic_path.write_text(json.dumps(diagnostic, indent=2, sort_keys=True) + "\n",
                                       encoding="utf-8")
            _record(args.progress, {"event": "geometry_diagnostic_saved",
                                    "path": str(diagnostic_path),
                                    "sha256": _file_hash(diagnostic_path),
                                    "panel_count": len(diagnostic["panels"])})
        _record(args.progress, {"event": "pair_geometry_ready", "case": case["name"],
                                "triangle_counts": pair_triangles,
                                "seconds": round(time.monotonic() - pair_start, 3)})
        for kind, camber, mesh in (("flat", 0.0, flat),
                                   ("camber-035", plan["frozen_camber"], curved)):
            old = _reuse_panel(index, case, kind, module_hash, plan_hash, args.progress)
            if old is not None:
                outputs.append(old)
                continue
            render_start = time.monotonic()
            print(f"case {index + 1}/{len(rows)} {case['name']} · {kind}: render start",
                  flush=True)
            fit_pair = (flat, curved)
            svg = surface.render_condition(
                spec, camera, mesh, fit_pair, PANEL_WIDTH, PANEL_HEIGHT,
                f"row-{index:02d}-{_safe(case['name'])}-{kind}")
            metadata = _write_panel(index, case, kind, svg, module_hash, plan_hash, args.progress)
            outputs.append(metadata)
            print(f"case {index + 1}/{len(rows)} {case['name']} · {kind}: saved in "
                  f"{time.monotonic() - render_start:.2f}s", flush=True)
    if args.limit is not None:
        print(f"profiled {len(rows)} flat/camber pair row(s); panel checkpoints in {EVIDENCE}",
              flush=True)
        return
    if len(outputs) != len(plan["cases"]) * len(PANELS):
        raise RuntimeError(f"incomplete matrix: {len(outputs)} panels")
    labelled = _board(True, rows, outputs, EVIDENCE / "comparison-labelled.svg",
                      plan_hash, module_hash)
    unlabelled = _board(False, rows, outputs, EVIDENCE / "comparison-unlabelled.svg",
                        plan_hash, module_hash)
    summary = {"case_plan_sha256": plan_hash, "renderer_sha256": module_hash,
               "renderer_provenance": provenance,
               "panels": outputs, "boards": [labelled, unlabelled],
               "elapsed_seconds": round(time.monotonic() - total_started, 3)}
    (EVIDENCE / "build-manifest.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _record(args.progress, {"event": "build_complete", "panels": len(outputs),
                            "elapsed_seconds": summary["elapsed_seconds"],
                            "board_hashes": [labelled["svg_sha256"], unlabelled["svg_sha256"]]})
    print(f"complete: {len(outputs)} deterministic panels; labelled and unlabelled boards; "
          f"{summary['elapsed_seconds']:.2f}s", flush=True)


if __name__ == "__main__":
    main()
