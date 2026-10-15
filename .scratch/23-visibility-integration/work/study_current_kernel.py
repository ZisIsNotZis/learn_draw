"""Render a fresh, hash-bound current-kernel diagnostic from frozen exercise21 geometry."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
PLAN_PATH = Path(__file__).resolve().with_name("cases-fine-current.json")
EVIDENCE = Path(__file__).resolve().parents[1] / "evidence" / "fine-current"
EVIDENCE.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(SCRIPTS))
import draw  # noqa: E402
from draw import render  # noqa: E402
from ribbon_family import Camera, RibbonSpec, project  # noqa: E402
import ribbon_surface as surface  # noqa: E402
import vector_visibility as visibility  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _module_sha(module) -> str:
    return sha256(Path(module.__file__).resolve())


def _load_case(plan: dict) -> tuple[RibbonSpec, Camera]:
    source_plan = ROOT / plan["derived_from"]["path"]
    if sha256(source_plan) != plan["derived_from"]["sha256"]:
        raise RuntimeError("historical exercise21 fine plan changed; refusing derived render")
    original = json.loads(source_plan.read_text(encoding="utf-8"))
    case = next(row for row in original["cases"]
                if row["name"] == plan["derived_from"]["case_name"])
    expected = plan["frozen_geometry"]
    if (case["ribbon"] != expected["ribbon"]
            or case["camera"] != expected["camera"]
            or expected["support_camber"] != .35
            or expected["sampling"] != {"u_intervals": 96, "v_intervals": 12}):
        raise RuntimeError("derived geometry, camera, camber, or sampling differs from frozen inputs")
    return RibbonSpec.from_mapping(case["ribbon"]), Camera(**case["camera"])


def _svg(path_data: str, fill: str, width: int, height: int, background: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">'
            f'<rect width="{width}" height="{height}" fill="{background}"/>'
            f'<path d="{path_data}" fill="{fill}" fill-rule="nonzero"/></svg>')


def _render_pair(name: str, source_path: str, current_path: str, fill: str,
                 size: tuple[int, int], background: str) -> dict:
    width, height = size
    output = {}
    for label, path_data in (("source", source_path), ("current", current_path)):
        svg_path = EVIDENCE / f"{name}-{label}.svg"
        png_path = svg_path.with_suffix(".png")
        svg_path.write_text(_svg(path_data, fill, width, height, background), encoding="utf-8")
        render(str(svg_path), str(png_path), size=size)
        output[label] = {"svg": str(svg_path.relative_to(ROOT)),
                         "png": str(png_path.relative_to(ROOT)),
                         "svg_sha256": sha256(svg_path), "png_sha256": sha256(png_path)}
    source = np.asarray(Image.open(ROOT / output["source"]["png"]).convert("RGB"))
    current = np.asarray(Image.open(ROOT / output["current"]["png"]).convert("RGB"))
    difference = np.any(source != current, axis=2)
    output["source_vs_current_differing_pixels"] = int(difference.sum())
    repeat = EVIDENCE / f"{name}-current-repeat.png"
    render(str(EVIDENCE / f"{name}-current.svg"), str(repeat), size=size)
    output["current_repeat"] = {"png": str(repeat.relative_to(ROOT)),
                                "png_sha256": sha256(repeat),
                                "byte_identical": sha256(repeat) == output["current"]["png_sha256"]}
    return output


def _fine_arch(plan: dict, spec: RibbonSpec, camera: Camera) -> dict:
    frozen = plan["frozen_geometry"]
    flat = surface.build_surface(spec, 0.0, 96, 12)
    curved = surface.build_surface(spec, frozen["support_camber"], 96, 12)
    width, height = plan["rendering"]["view_size"]
    scale, ox, oy = surface._projected_fit((flat, curved), camera, width, height)
    faces, uv_faces = [], []
    for triangle in curved.triangles:
        points = [project(point, camera) for point in triangle.points]
        projected = [(ox + scale * x, oy - scale * y, z) for x, y, z in points]
        faces.append((projected, spec.front, spec.name))
        uv_faces.append((projected, np.asarray(triangle.uv, dtype=float)))

    depth = np.full((height, width), -np.inf)
    u = np.full((height, width), np.nan)
    v = np.full((height, width), np.nan)
    for triangle, uv in uv_faces:
        p = np.asarray(triangle, dtype=float)
        a, b, c = p
        matrix = np.column_stack((b[:2] - a[:2], c[:2] - a[:2]))
        if abs(np.linalg.det(matrix)) < 1e-10:
            continue
        left, right = max(0, int(np.floor(p[:, 0].min()))), min(width, int(np.ceil(p[:, 0].max())))
        top, bottom = max(0, int(np.floor(p[:, 1].min()))), min(height, int(np.ceil(p[:, 1].max())))
        yy, xx = np.mgrid[top:bottom, left:right]
        if not xx.size:
            continue
        weights = np.linalg.inv(matrix) @ np.stack((xx.ravel() + .5 - a[0], yy.ravel() + .5 - a[1]))
        wb, wc = weights.reshape(2, *xx.shape)
        wa = 1 - wb - wc
        z = wa * a[2] + wb * b[2] + wc * c[2]
        nearer = ((wa >= -1e-9) & (wb >= -1e-9) & (wc >= -1e-9)
                  & (z > depth[top:bottom, left:right]))
        depth[top:bottom, left:right][nearer] = z[nearer]
        u[top:bottom, left:right][nearer] = (wa * uv[0, 0] + wb * uv[1, 0] + wc * uv[2, 0])[nearer]
        v[top:bottom, left:right][nearer] = (wa * uv[0, 1] + wb * uv[1, 1] + wc * uv[2, 1])[nearer]

    safe = (np.isfinite(depth) & (u > .1) & (u < .9) & (np.abs(v) < .75)
            & (np.abs(v) > .3))
    expected = np.asarray([int(spec.front[i:i + 2], 16) for i in (1, 3, 5)], dtype=np.int16)
    rendered = _render_pair("arch", visibility._compound_path([tri for tri, _, _ in faces]),
                            visibility._compound_path([poly for poly, _, _ in
                                                       visibility.visible_fragments(faces)]),
                            spec.front, (width, height), "#f4f5ef")
    pixels = np.asarray(Image.open(ROOT / rendered["current"]["png"]).convert("RGB"), dtype=np.int16)
    background = np.asarray([244, 245, 239], dtype=np.int16)
    deviation = np.max(np.abs(pixels - expected), axis=2)
    background_distance = np.max(np.abs(pixels - background), axis=2)
    rendered["safe_interior"] = {"pixel_count": int(safe.sum()),
                                 "nonmatching_base_pixels_gt12": int((safe & (deviation > 12)).sum()),
                                 "background_like_pixels_within3": int((safe & (background_distance <= 3)).sum())}
    rendered["geometry"] = {"source_plan_case": plan["derived_from"]["case_name"],
                             "ribbon_sha256": plan["frozen_geometry"]["source_spec_sha256"],
                             "camera": camera.__dict__, "camber": .35,
                             "u_intervals": 96, "v_intervals": 12,
                             "triangles": len(faces), "fit_scale": scale,
                             "fit_origin": [ox, oy]}
    return rendered


def _planar_mesh_control() -> dict:
    faces = []
    x0, y0, dx, dy = 31.25, 27.375, 31.125, 31.125
    for j in range(3):
        for i in range(4):
            xa, xb = x0 + i * dx, x0 + (i + 1) * dx
            ya, yb = y0 + j * dy, y0 + (j + 1) * dy
            a, b, c, d = (xa, ya, 1), (xb, ya, 1), (xb, yb, 1), (xa, yb, 1)
            triangles = ((a, b, c), (a, c, d)) if (i + j) % 2 == 0 else ((a, b, d), (b, c, d))
            faces.extend((list(triangle), "#45c982", "generated-sheet") for triangle in triangles)
    raw = visibility._compound_path([tri for tri, _, _ in faces])
    current = visibility._compound_path([poly for poly, _, _ in visibility.visible_fragments(faces)])
    result = _render_pair("mesh-4x3", raw, current, "#45c982", (320, 256), "#14212b")
    result["geometry"] = {"kind": "computed regular planar grid", "nx": 4, "ny": 3,
                           "face_count": len(faces), "rectangle": [x0, y0, x0 + 4 * dx, y0 + 3 * dy]}
    return result


def main() -> None:
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    resolver_path = ROOT / plan["producer"]["path"]
    if sha256(resolver_path) != plan["producer"]["sha256"]:
        raise RuntimeError("current resolver no longer matches derived plan")
    spec, camera = _load_case(plan)
    browser = Path(draw.CHROME).resolve()
    version_result = subprocess.run([str(browser), "--version"], capture_output=True,
                                    text=True, timeout=5, check=True)
    chromium_version = (version_result.stdout or version_result.stderr).strip()
    result = {"purpose": plan["purpose"],
              "plan": {"path": str(PLAN_PATH.relative_to(ROOT)), "sha256": sha256(PLAN_PATH),
                       "source_plan_sha256": plan["derived_from"]["sha256"]},
              "producer": {"path": plan["producer"]["path"],
                           "sha256_before": sha256(resolver_path),
                           "study_script_sha256": sha256(Path(__file__).resolve()),
                           "draw_py_sha256": sha256(SCRIPTS / "draw.py"),
                           "chromium": {"path": str(browser), "version": chromium_version}},
              "fine_arch_source_vs_current": _fine_arch(plan, spec, camera),
              "computed_mesh_source_vs_current": _planar_mesh_control()}
    result["producer"]["sha256_after"] = sha256(resolver_path)
    result["producer"]["unchanged_during_run"] = (
        result["producer"]["sha256_before"] == result["producer"]["sha256_after"])
    output = EVIDENCE / "current-kernel-study.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["producer"]["unchanged_during_run"]:
        raise RuntimeError("current source changed during rendering")


if __name__ == "__main__":
    main()
