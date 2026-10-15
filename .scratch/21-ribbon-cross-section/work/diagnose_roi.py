#!/usr/bin/env python3
"""Compare one frozen no-twist ROI's materials, depth-only fill, and same-camber convergence."""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import cv2
import numpy as np
import ribbon_surface as surface
from draw import CHROME, render
from ribbon_family import (BACK_STRIPE_COLOR, FRONT_STRIPE_COLOR, Camera, RibbonSpec,
                           camera_basis, project)
from vector_visibility import visible_regions

PLAN = Path(__file__).resolve().with_name("cases.json")
EVIDENCE = Path(__file__).resolve().parents[1] / "evidence" / "diagnostics"
WIDTH, HEIGHT = 480, 320
BOARD_WIDTH, GAP, MARGIN = 1500, 10, 20
BACKGROUND = "#f4f5ef"
MONO_FILL = "#87958e"
SVG_NS = "http://www.w3.org/2000/svg"
ROI_MAP = {
    "positive-half-twist-oblique": {
        "camera": {"name": "oblique", "yaw": 38, "pitch": 22},
        "parent_board_panel_origin": {"x": 517, "y": 428},
        "parent_global_roi": {"left": 700, "top": 490, "right": 840, "bottom": 555},
        "panel_local_roi": {"left": 183, "top": 62, "right": 323, "bottom": 127},
        "selected_for_render": False,
    },
    "untwisted-teaching-arch-front-control": {
        "camera": {"name": "front", "yaw": 0, "pitch": 0},
        "parent_board_panel_origin": {"x": 517, "y": 1478},
        "parent_global_roi": {"left": 700, "top": 1570, "right": 850, "bottom": 1640},
        "panel_local_roi": {"left": 183, "top": 92, "right": 333, "bottom": 162},
        "selected_for_render": True,
    },
}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_hash(value) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return _hash_bytes(data.encode())


def _safe(text: str) -> str:
    return "".join(char if char.isalnum() or char in "-_" else "-" for char in text)


def _clip_content(svg: str) -> str:
    if "<ns0:" in svg:
        raise ValueError("inline SVG contains a prefixed namespace element")
    return svg[svg.index(">") + 1:svg.rfind("</svg>")]


def _mono_svg(spec: RibbonSpec, camera: Camera, mesh, fit, prefix: str) -> str:
    scale, offset_x, offset_y = fit
    faces = []
    for triangle in mesh.triangles:
        projected = []
        for point in triangle.points:
            x, y, depth = project(point, camera)
            projected.append((offset_x + scale * x, offset_y - scale * y, depth))
        faces.append((projected, MONO_FILL, spec.name))
    paths = []
    for index, (path, color, component) in enumerate(visible_regions(faces)):
        paths.append(f'<!-- {escape(component)}: one fill, opaque depth visibility only; '
                     f'no side color or local mark -->'
                     f'<path id="{prefix}-{index}" d="{path}" fill="{color}" '
                     f'fill-rule="nonzero" data-component="{escape(component)}"/>')
    return (f'<svg xmlns="{SVG_NS}" viewBox="0 0 {WIDTH} {HEIGHT}">'
            f'<rect id="{prefix}-paper" width="{WIDTH}" height="{HEIGHT}" fill="{BACKGROUND}"/>'
            f'{"".join(paths)}</svg>')


def _clip_axis(polygon, axis: int, boundary: float, keep_greater: bool):
    if not polygon:
        return []
    result = []
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        da, db = a[axis] - boundary, b[axis] - boundary
        inside_a = da >= -1e-10 if keep_greater else da <= 1e-10
        inside_b = db >= -1e-10 if keep_greater else db <= 1e-10
        if inside_a != inside_b:
            amount = da / (da - db)
            result.append((a[0] + amount * (b[0] - a[0]),
                           a[1] + amount * (b[1] - a[1])))
        if inside_b:
            result.append(b)
    return result


def _roi_intersection_area(projected, roi):
    left, top, right, bottom = (roi[key] for key in ("left", "top", "right", "bottom"))
    clipped = list(projected)
    clipped = _clip_axis(clipped, 0, left, True)
    clipped = _clip_axis(clipped, 0, right, False)
    clipped = _clip_axis(clipped, 1, top, True)
    clipped = _clip_axis(clipped, 1, bottom, False)
    if len(clipped) < 3:
        return 0.0
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(clipped, clipped[1:] + clipped[:1]))) / 2.0


def _normal_and_dot(triangle, view):
    a, b, c = triangle.points
    ab = tuple(b[i] - a[i] for i in range(3))
    ac = tuple(c[i] - a[i] for i in range(3))
    normal = (ab[1] * ac[2] - ab[2] * ac[1], ab[2] * ac[0] - ab[0] * ac[2],
              ab[0] * ac[1] - ab[1] * ac[0])
    magnitude = math.sqrt(sum(x * x for x in normal))
    unit = tuple(value / magnitude for value in normal)
    return unit, sum(unit[i] * view[i] for i in range(3))


def _screen_barycentric(point, triangle):
    a, b, c = triangle
    ab, ac = (b[0] - a[0], b[1] - a[1]), (c[0] - a[0], c[1] - a[1])
    ap = (point[0] - a[0], point[1] - a[1])
    determinant = ab[0] * ac[1] - ab[1] * ac[0]
    if abs(determinant) < 1e-12:
        return None
    wb = (ap[0] * ac[1] - ap[1] * ac[0]) / determinant
    wc = (ab[0] * ap[1] - ab[1] * ap[0]) / determinant
    return 1.0 - wb - wc, wb, wc


def _triangle_roi_record(spec: RibbonSpec, camera: Camera, mesh, fit,
                         roi: dict, name: str, full_raster: np.ndarray) -> dict:
    """Join camera-space ROI pixels to actual face, UV, and winding-normal provenance."""
    left, top, right, bottom = (roi[key] for key in ("left", "top", "right", "bottom"))
    scale, offset_x, offset_y = fit
    view = camera_basis(camera)[2]
    records = []
    side_by_face = []
    for face_id, triangle in enumerate(mesh.triangles):
        unit_normal, dot_view = _normal_and_dot(triangle, view)
        side = "front" if dot_view > 0 else "back"
        side_by_face.append((side, dot_view))
        projected = []
        for point in triangle.points:
            x, y, _depth = project(point, camera)
            projected.append((offset_x + scale * x, offset_y - scale * y))
        box = {"left": min(p[0] for p in projected), "right": max(p[0] for p in projected),
               "top": min(p[1] for p in projected), "bottom": max(p[1] for p in projected)}
        if box["right"] < left or box["left"] > right or box["bottom"] < top or box["top"] > bottom:
            continue
        area_in_roi = _roi_intersection_area(projected, roi)
        if area_in_roi <= 1e-10:
            continue
        uv_box = {"u_min": min(p[0] for p in triangle.uv),
                  "u_max": max(p[0] for p in triangle.uv),
                  "v_min": min(p[1] for p in triangle.uv),
                  "v_max": max(p[1] for p in triangle.uv)}
        records.append({"mesh_triangle": face_id,
                        "legacy_source_triangle": triangle.source_triangle,
                        "uv_vertices": triangle.uv,
                        "uv_centroid": [sum(p[0] for p in triangle.uv) / 3,
                                        sum(p[1] for p in triangle.uv) / 3],
                        "actual_unit_normal": unit_normal,
                        "camera_view_dot": dot_view,
                        "actual_side": side,
                        "base_fill": spec.front if side == "front" else spec.back,
                        "stripe_fill_if_intersecting": FRONT_STRIPE_COLOR if side == "front" else BACK_STRIPE_COLOR,
                        "stripe_can_intersect_face": uv_box["v_min"] < 0.18 and uv_box["v_max"] > -0.18,
                        "panel_projected_bounds": box,
                        "projected_overlap_area_px2": area_in_roi})
    # Side-label transitions are expected artwork segmentation only when adjacent actual faces
    # have opposite camera-facing signs. Mesh diagonals without this transition are not art lines.
    edge_faces = {}
    for face_id, triangle in enumerate(mesh.triangles):
        for index in range(3):
            a, b = triangle.uv[index], triangle.uv[(index + 1) % 3]
            edge = tuple(sorted(((round(a[0] * 1e12), round(a[1] * 1e12)),
                                 (round(b[0] * 1e12), round(b[1] * 1e12)))) )
            edge_faces.setdefault(edge, []).append(face_id)
    face_ids_roi = {record["mesh_triangle"] for record in records}
    transitions = []
    for edge, faces in edge_faces.items():
        if len(faces) < 2:
            continue
        for first in faces:
            for second in faces:
                if first >= second or first not in face_ids_roi or second not in face_ids_roi:
                    continue
                if side_by_face[first][0] != side_by_face[second][0]:
                    transitions.append({"mesh_triangles": [first, second],
                                        "legacy_source_triangles": [mesh.triangles[first].source_triangle,
                                                                     mesh.triangles[second].source_triangle],
                                        "uv_edge": [[value / 1e12 for value in point] for point in edge],
                                        "view_dots": [side_by_face[first][1], side_by_face[second][1]]})
    sides = {side: sum(record["actual_side"] == side for record in records)
             for side in ("front", "back")}
    dots = [record["camera_view_dot"] for record in records]
    by_id = {record["mesh_triangle"]: record for record in records}
    center = ((left + right) / 2.0, (top + bottom) / 2.0)
    representative_ids = set()
    for side in ("front", "back"):
        same_side = [record for record in records if record["actual_side"] == side]
        if same_side:
            representative_ids.add(min(same_side, key=lambda record: abs(record["camera_view_dot"]))[
                                   "mesh_triangle"])
            representative_ids.add(max(same_side, key=lambda record: record["camera_view_dot"])[
                                   "mesh_triangle"])
            representative_ids.add(min(same_side, key=lambda record: (
                ((record["panel_projected_bounds"]["left"]
                  + record["panel_projected_bounds"]["right"]) / 2 - center[0]) ** 2
                + ((record["panel_projected_bounds"]["top"]
                    + record["panel_projected_bounds"]["bottom"]) / 2 - center[1]) ** 2))[
                    "mesh_triangle"])
    samples = []
    for fy in (0.2, 0.5, 0.8):
        for fx in (0.2, 0.5, 0.8):
            pixel = (left + fx * (right - left), top + fy * (bottom - top))
            hits = []
            for face_id in face_ids_roi:
                triangle = mesh.triangles[face_id]
                projected = []
                for point in triangle.points:
                    x, y, _depth = project(point, camera)
                    projected.append((offset_x + scale * x, offset_y - scale * y))
                weights = _screen_barycentric(pixel, projected)
                if weights is None or min(weights) < -1e-8:
                    continue
                uv = tuple(sum(weights[j] * triangle.uv[j][axis] for j in range(3))
                           for axis in range(2))
                world = tuple(sum(weights[j] * triangle.points[j][axis] for j in range(3))
                              for axis in range(3))
                depth = project(world, camera)[2]
                normal, dot_view = _normal_and_dot(triangle, view)
                side = "front" if dot_view > 0 else "back"
                in_stripe = abs(uv[1]) < 0.18
                color = ((FRONT_STRIPE_COLOR if side == "front" else BACK_STRIPE_COLOR)
                         if in_stripe else (spec.front if side == "front" else spec.back))
                bgr_expected = tuple(int(color[index:index + 2], 16)
                                     for index in (5, 3, 1))
                x_pixel, y_pixel = int(pixel[0]), int(pixel[1])
                observed = tuple(int(value) for value in full_raster[y_pixel, x_pixel])
                hits.append({"mesh_triangle": face_id,
                             "legacy_source_triangle": triangle.source_triangle,
                             "barycentric": weights, "uv": uv, "world_point": world,
                             "depth_toward_camera": depth, "actual_unit_normal": normal,
                             "camera_view_dot": dot_view, "actual_side": side,
                             "expected_local_fill": color, "expected_bgr": bgr_expected,
                             "raster_bgr": observed,
                             "within_8_channel_levels": max(abs(observed[i] - bgr_expected[i])
                                                             for i in range(3)) <= 8})
            nearest_depth = max((hit["depth_toward_camera"] for hit in hits), default=None)
            nearest = [hit for hit in hits if nearest_depth is not None
                       and abs(hit["depth_toward_camera"] - nearest_depth) <= 1e-5]
            samples.append({"panel_pixel": pixel, "covering_surface_triangles": len(hits),
                            "nearest_visible_face_candidates": nearest})
    return {"case": name, "camera": {"name": camera.name, "yaw": camera.yaw,
                                      "pitch": camera.pitch},
            "panel_local_roi": roi, "mesh_sampling": {"u": len(mesh.base.stations) - 1,
                                                         "v": mesh.v_intervals},
            "view_dot_range": [min(dots), max(dots)] if dots else None,
            "face_side_counts": sides,
            "stripe_candidate_face_count": sum(record["stripe_can_intersect_face"] for record in records),
            "adjacent_actual_side_transitions_in_roi": transitions,
            "transition_count": len(transitions),
            "representative_face_provenance": [by_id[index] for index in sorted(representative_ids)],
            "roi_grid_point_provenance": samples,
            "candidate_triangle_count": len(records),
            "reading": "front/back color changes are expected only across the listed actual-normal sign changes; mesh subdivisions alone are not authored seams"}


def _coverage_metrics(png_path: Path, roi: dict) -> dict:
    image = cv2.imread(str(png_path), cv2.IMREAD_COLOR)
    if image is None or image.shape[:2] != (HEIGHT, WIDTH):
        raise RuntimeError(f"missing/incorrect diagnostic panel raster: {png_path}")
    x0, y0, x1, y1 = (roi[key] for key in ("left", "top", "right", "bottom"))
    crop = image[y0:y1, x0:x1]
    background = np.array((239, 245, 244), dtype=np.uint8)
    mask = np.any(np.abs(crop.astype(np.int16) - background) > 8, axis=2)
    return {"occupied_pixels": int(mask.sum()), "roi_pixels": int(mask.size),
            "occupancy_fraction": float(mask.mean()), "mask": mask}


def _render_diagnostic(plan: dict, case: dict, cameras: list[dict]) -> dict:
    spec = RibbonSpec.from_mapping(case["ribbon"])
    cam_raw = case["camera"]
    camera = Camera(cam_raw["name"], cam_raw["yaw"], cam_raw["pitch"])
    flat48 = surface.build_surface(spec, 0.0, 48, 6)
    camber48 = surface.build_surface(spec, 0.35, 48, 6)
    camber96 = surface.build_surface(spec, 0.35, 96, 12)
    fit = surface._projected_fit((flat48, camber48), camera, WIDTH, HEIGHT)
    scale, ox, oy = fit
    for face in camber96.triangles:
        for point in face.points:
            x, y, _depth = project(point, camera)
            px, py = ox + scale * x, oy - scale * y
            if px < 0 or px > WIDTH or py < 0 or py > HEIGHT:
                raise RuntimeError("96x12 convergence geometry falls outside the original 48x6 frame")
    full48 = surface._render_faces(spec, camera, camber48, WIDTH, HEIGHT, fit,
                                   "arch-full-48x6", True)
    mono48 = _mono_svg(spec, camera, camber48, fit, "arch-mono-48x6")
    full96 = surface._render_faces(spec, camera, camber96, WIDTH, HEIGHT, fit,
                                   "arch-full-96x12", True)
    panels = (("authored materials · 48×6", "full-48x6", full48),
              ("one monochrome fill · visibility only · 48×6", "mono-48x6", mono48),
              ("same camber · finer mesh · 96×12", "full-96x12", full96))
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    panel_records = []
    for caption, stem, svg in panels:
        path = EVIDENCE / f"roi-arch-{stem}.svg"
        png = path.with_suffix(".png")
        path.write_text(svg, encoding="utf-8")
        render(str(path), str(png), size=(WIDTH, HEIGHT))
        panel_records.append({"caption": caption, "svg": path.name, "png": png.name,
                              "svg_sha256": _sha(path), "png_sha256": _sha(png)})
    row_local_roi = ROI_MAP[case["name"]]["panel_local_roi"]
    counts = [_coverage_metrics(EVIDENCE / row["png"], row_local_roi) for row in panel_records]
    masks = [record.pop("mask") for record in counts]
    coverage_differences = {}
    for label, index in (("monochrome48x6", 1), ("full96x12", 2)):
        comparison = masks[0] != masks[index]
        coverage_differences[label] = {
            "mask_mismatch_pixels": int(comparison.sum()),
            "full_material_only": int((masks[0] & ~masks[index]).sum()),
            "comparison_only": int((masks[index] & ~masks[0]).sum()),
            "roi_pixels": int(comparison.size),
        }
    title = (f'<text id="diag-title" x="20" y="25" font-family="sans-serif" '
             f'font-size="16" font-weight="600" fill="#263b4b">Untwisted arch ROI · '
             f'material / visibility / sampling diagnostic</text>')
    parts = [f'<svg xmlns="{SVG_NS}" viewBox="0 0 {BOARD_WIDTH} 400">',
             '<rect id="diag-paper" width="100%" height="100%" fill="#e8eeea"/>', title]
    for i, (caption, stem, _svg) in enumerate(panels):
        x = MARGIN + i * (WIDTH + GAP)
        parts.append(f'<text id="diag-caption-{i}" x="{x}" y="48" font-family="sans-serif" '
                     f'font-size="10" fill="#42596a">{escape(caption)}</text>')
        panel_svg = EVIDENCE / f"roi-arch-{stem}.svg"
        content = panel_svg.read_text(encoding="utf-8")
        if "<ns0:" in content:
            raise ValueError("namespace-prefixed diagnostic SVG child")
        parts.append(f'<g id="diag-panel-{i}" transform="translate({x} 62)">'
                     f'{content[content.index(">") + 1:content.rfind("</svg>")]}</g>')
    parts.append("</svg>")
    board = "\n".join(parts)
    root = ET.fromstring(board)
    ids = [node.attrib["id"] for node in root.iter() if "id" in node.attrib]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate diagnostic SVG ID")
    board_path = EVIDENCE / "roi-arch-material-visibility-convergence.svg"
    board_png = board_path.with_suffix(".png")
    board_path.write_text(board, encoding="utf-8")
    render(str(board_path), str(board_png), size=(BOARD_WIDTH, 400))

    rois = []
    for case_name, roi_plan in ROI_MAP.items():
        roi_case = next(item for item in plan["cases"] if item["name"] == case_name)
        roi_spec = RibbonSpec.from_mapping(roi_case["ribbon"])
        roi_camera_data = roi_plan["camera"]
        roi_camera = Camera(roi_camera_data["name"], roi_camera_data["yaw"], roi_camera_data["pitch"])
        if case_name == case["name"]:
            roi_mesh = camber48
            roi_fit = fit
            roi_raster = cv2.imread(str(EVIDENCE / "roi-arch-full-48x6.png"), cv2.IMREAD_COLOR)
        else:
            roi_flat = surface.build_surface(roi_spec, 0.0, 48, 6)
            roi_mesh = surface.build_surface(roi_spec, 0.35, 48, 6)
            roi_fit = surface._projected_fit((roi_flat, roi_mesh), roi_camera, WIDTH, HEIGHT)
            original_panel = ROOT / ".scratch/21-ribbon-cross-section/evidence/panels/case-01-positive-half-twist-oblique-camber-035.png"
            roi_raster = cv2.imread(str(original_panel), cv2.IMREAD_COLOR)
        if roi_raster is None or roi_raster.shape[:2] != (HEIGHT, WIDTH):
            raise RuntimeError(f"missing exact-source panel raster for ROI diagnostic: {case_name}")
        rois.append(_triangle_roi_record(roi_spec, roi_camera, roi_mesh, roi_fit,
                                         roi_plan["panel_local_roi"], case_name, roi_raster))

    diag_py = Path(__file__).resolve()
    browser_result = subprocess.run([str(Path(CHROME).resolve()), "--version"],
                                    capture_output=True, text=True, timeout=5, check=True)
    browser_identity = {"path": str(Path(CHROME).resolve()),
                        "version": (browser_result.stdout or browser_result.stderr).strip()}
    data = {
        "diagnostic_only_not_acceptance_artifact": True,
        "primary_case": case["name"],
        "source_spec_sha256": case["source_spec_sha256"],
        "camera": cam_raw,
        "camera_sha256": case["camera_sha256"],
        "support_camber": 0.35,
        "primary_geometry": "same frozen teaching arch spec at 48x6 full-material/monochrome and 96x12 full-material; no new camera, camber, art, or support",
        "panel_svg_png": panel_records,
        "diagnostic_board": {"svg": board_path.name, "png": board_png.name,
                              "svg_sha256": _sha(board_path), "png_sha256": _sha(board_png)},
        "primary_roi": {"name": case["name"], **ROI_MAP[case["name"]],
                        "mask_background_bgr": [239, 245, 244],
                        "mask_channel_tolerance": 8,
                        "coverage_masks": counts,
                        "coverage_mask_differences": coverage_differences},
        "source_triangle_uv_normal_provenance": rois,
        "case_plan_sha256": _sha(PLAN),
        "support_module_sha256": _sha(SCRIPTS / "ribbon_surface.py"),
        "builder_sha256": _sha(Path(__file__).resolve().with_name("build.py")),
        "draw_py_sha256": _sha(SCRIPTS / "draw.py"),
        "diagnostic_script_sha256": _sha(diag_py),
        "chromium": browser_identity,
        "framing": {"panel_px": [WIDTH, HEIGHT], "shared_fit": [scale, ox, oy],
                    "fit_support": "legacy flat plus camber .35 at the frozen 48x6 selected sampling"},
    }
    json_path = EVIDENCE / "roi-source-provenance.json"
    json_path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"board": str(board_path), "png": str(board_png),
                      "json": str(json_path),
                      "roi_side_counts": {row["case"]: row["face_side_counts"] for row in rois},
                      "roi_transition_counts": {row["case"]: row["transition_count"] for row in rois},
                      "coverage": coverage_differences}, indent=2))


def main() -> None:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    primary = next(item for item in plan["cases"]
                   if item["name"] == "untwisted-teaching-arch-front-control")
    _render_diagnostic(plan, primary, plan["cameras"])


if __name__ == "__main__":
    main()
