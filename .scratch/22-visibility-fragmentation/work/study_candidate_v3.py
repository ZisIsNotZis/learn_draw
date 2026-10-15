"""Scratch-only geometric and Chromium study for positive-area triangle overlap."""
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
EVIDENCE = Path(__file__).resolve().parents[1] / "evidence"
FINE = EVIDENCE / "fine"
FINE.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(SCRIPTS))
from draw import render  # noqa: E402
from ribbon_family import Camera, RibbonSpec, project  # noqa: E402
import ribbon_surface as surface  # noqa: E402


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def polygon_area(poly):
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(poly, poly[1:] + poly[:1])) / 2)


def svg_for(path, color, width=320, height=256):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">'
            f'<rect width="{width}" height="{height}" fill="#14212b"/>'
            f'<path d="{path}" fill="{color}" fill-rule="nonzero"/></svg>')


def area_stats(polygons):
    areas = [polygon_area(poly) for poly in polygons]
    positive = [area for area in areas if area > 0]
    zero_examples = [{"vertices": poly} for poly, area in zip(polygons, areas) if area == 0][:4]
    tiny_examples = [{"area": area, "vertices": poly}
                     for poly, area in sorted(zip(polygons, areas), key=lambda row: row[1])
                     if area > 0][:4]
    return {"fragment_count": len(polygons), "zero_area_fragments": len(areas) - len(positive),
            "positive_area_fragments": len(positive),
            "min_positive_area": min(positive) if positive else None,
            "sum_area": sum(areas),
            "area_le_1e-10": sum(0 < area <= 1e-10 for area in areas),
            "area_le_1e-7": sum(0 < area <= 1e-7 for area in areas),
            "zero_area_geometry_examples": zero_examples,
            "smallest_positive_geometry_examples": tiny_examples}


def generated_grid(nx, ny):
    """Fractional-coordinate surface generated from a regular grid, never a hand contour."""
    faces = []
    x0, y0, dx, dy = 31.25, 27.375, 31.125, 31.125
    for j in range(ny):
        for i in range(nx):
            xa, xb = x0 + i * dx, x0 + (i + 1) * dx
            ya, yb = y0 + j * dy, y0 + (j + 1) * dy
            a, b, c, d = (xa, ya, 1), (xb, ya, 1), (xb, yb, 1), (xa, yb, 1)
            triangles = ((a, b, c), (a, c, d)) if (i + j) % 2 == 0 else ((a, b, d), (b, c, d))
            faces.extend((list(triangle), "#45c982", "computed-sheet") for triangle in triangles)
    return faces


def mesh_raster_study(canonical, candidate):
    faces = generated_grid(4, 3)
    raw_polygons = [triangle for triangle, _color, _name in faces]
    canonical_polygons = [poly for poly, _color, _name in canonical.visible_fragments(faces)]
    candidate_polygons = [poly for poly, _color, _name in candidate.visible_fragments(faces)]
    outputs = {}
    images = {}
    for name, module, polygons in (
            ("source", canonical, raw_polygons),
            ("canonical", canonical, canonical_polygons),
            ("candidate", candidate, candidate_polygons)):
        path_data = module._compound_path(polygons)
        svg = svg_for(path_data, "#45c982")
        svg_path = FINE / f"minimal-4x3-{name}-v3.svg"
        png_path = svg_path.with_suffix(".png")
        svg_path.write_text(svg, encoding="utf-8")
        render(str(svg_path), str(png_path), size=(320, 256))
        images[name] = np.asarray(Image.open(png_path).convert("RGB"))
        outputs[name] = {"svg": str(svg_path.relative_to(ROOT)),
                         "png": str(png_path.relative_to(ROOT)),
                         "svg_sha256": sha256(svg_path), "png_sha256": sha256(png_path),
                         "path_move_count": path_data.count("M "),
                         "path_bytes": len(path_data.encode("utf-8")),
                         "polygons": area_stats(polygons)}
    source, current, patched = (images[name] for name in ("source", "canonical", "candidate"))
    canonical_diff = np.argwhere(np.any(source != current, axis=2))
    candidate_diff = np.argwhere(np.any(source != patched, axis=2))
    changed = []
    for y, x in canonical_diff:
        changed.append({"x": int(x), "y": int(y), "source_rgb": source[y, x].tolist(),
                        "canonical_rgb": current[y, x].tolist(),
                        "inside_generated_mesh_bounds": bool(31.25 < x + .5 < 31.25 + 4 * 31.125
                                                              and 27.375 < y + .5 < 27.375 + 3 * 31.125)})

    # Independently list touching triangle pairs that pass the canonical bbox gate.
    touching_pairs = []
    for i, (a, _color, _name) in enumerate(faces):
        for j in range(i + 1, len(faces)):
            b = faces[j][0]
            if canonical.overlaps(canonical.bbox(a), canonical.bbox(b)) \
                    and not candidate.positive_area_overlap(a, b):
                touching_pairs.append({"face_indices": [i, j], "face_a": a, "face_b": b,
                                       "bbox_a": canonical.bbox(a), "bbox_b": canonical.bbox(b)})
    return {"geometry": {"kind": "generated regular planar mesh", "nx": 4, "ny": 3,
                         "face_count": len(faces), "rectangle": [31.25, 27.375, 155.75, 120.75],
                         "coordinates_are_computed": True},
            "source_canonical_candidate": outputs,
            "raster": {"source_vs_canonical_differing_pixels": len(canonical_diff),
                       "source_vs_candidate_differing_pixels": len(candidate_diff),
                       "canonical_differences": changed,
                       "candidate_matches_source_byte_pixels": not len(candidate_diff)},
            "bbox_overlap_without_positive_area_count": len(touching_pairs),
            "bbox_overlap_without_positive_area_examples": touching_pairs[:8]}


def point_segment_distance(point, edge):
    x, y = point
    ax, ay = edge[0]
    bx, by = edge[1]
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - (ax + t * dx), y - (ay + t * dy))


def build_arch_probe(canonical, candidate):
    plan_path = ROOT / ".scratch/21-ribbon-cross-section/work/cases-fine.json"
    plan = json.loads(plan_path.read_text())
    case = next(c for c in plan["cases"] if c["ribbon"]["name"] == "teaching-arch")
    spec, camera = RibbonSpec.from_mapping(case["ribbon"]), Camera(**case["camera"])
    flat = surface.build_surface(spec, 0, 96, 12)
    curved = surface.build_surface(spec, .35, 96, 12)
    width, height = 480, 320
    scale, ox, oy = surface._projected_fit((flat, curved), camera, width, height)
    depth = np.full((height, width), -np.inf)
    u = np.full((height, width), np.nan)
    v = np.full((height, width), np.nan)
    projected = []
    edge_uses = {}
    for triangle in curved.triangles:
        points = [project(point, camera) for point in triangle.points]
        projected_triangle = [(ox + scale * point[0], oy - scale * point[1], point[2])
                              for point in points]
        projected.append((projected_triangle, spec.front, spec.name))
        for edge_index in range(3):
            a_xy = tuple(projected_triangle[edge_index][:2])
            b_xy = tuple(projected_triangle[(edge_index + 1) % 3][:2])
            edge_key = tuple(sorted((a_xy, b_xy)))
            edge_uses[edge_key] = edge_uses.get(edge_key, 0) + 1
        p = np.asarray(projected_triangle, dtype=float)
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
        uv = np.asarray(triangle.uv)
        depth[top:bottom, left:right][nearer] = z[nearer]
        u[top:bottom, left:right][nearer] = (wa * uv[0, 0] + wb * uv[1, 0] + wc * uv[2, 0])[nearer]
        v[top:bottom, left:right][nearer] = (wa * uv[0, 1] + wb * uv[1, 1] + wc * uv[2, 1])[nearer]
    safe = (np.isfinite(depth) & (u > .1) & (u < .9) & (np.abs(v) < .75)
            & (np.abs(v) > .3))
    background = np.asarray([244, 245, 239], dtype=np.int16)
    expected = np.asarray([int(spec.front[i:i + 2], 16) for i in (1, 3, 5)], dtype=np.int16)
    checks, polygon_stats, raster_arrays = {}, {}, {}
    for name, module in (("source", canonical), ("canonical", canonical), ("candidate", candidate)):
        if name == "source":
            polygons = [triangle for triangle, _color, _component in projected]
            path_data = module._compound_path(polygons)
        else:
            polygons = [poly for poly, _color, _component in module.visible_fragments(projected)]
            path_data = module._compound_path(polygons)
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">'
               f'<rect width="{width}" height="{height}" fill="#f4f5ef"/>'
               f'<path d="{path_data}" fill="{spec.front}" fill-rule="nonzero"/></svg>')
        svg_path, png_path = FINE / f"arch-{name}-v3.svg", FINE / f"arch-{name}-v3.png"
        svg_path.write_text(svg, encoding="utf-8")
        render(str(svg_path), str(png_path), size=(width, height))
        pixels = np.asarray(Image.open(png_path).convert("RGB"), dtype=np.int16)
        raster_arrays[name] = pixels
        deviation = np.max(np.abs(pixels - expected), axis=2)
        checks[name] = {"svg": str(svg_path.relative_to(ROOT)), "png": str(png_path.relative_to(ROOT)),
                        "svg_sha256": sha256(svg_path), "png_sha256": sha256(png_path),
                        "nonmatching_base_pixels_in_safe_mask": int((safe & (deviation > 12)).sum()),
                        "background_like_interior_pixels": int((safe & (np.max(np.abs(pixels - background), axis=2) <= 3)).sum()),
                        "fragment_path_moves": path_data.count("M "),
                        "path_bytes": len(path_data.encode("utf-8"))}
        polygon_stats[name] = area_stats(polygons)
    internal_edges = [edge for edge, uses in edge_uses.items() if uses > 1]
    canonical_bad = np.argwhere(safe & (np.max(np.abs(raster_arrays["canonical"] - expected), axis=2) > 12))
    edge_proximity = []
    for y, x in canonical_bad:
        pixel_center = (float(x) + .5, float(y) + .5)
        nearest = min(internal_edges, key=lambda edge: point_segment_distance(pixel_center, edge))
        edge_proximity.append({"x": int(x), "y": int(y), "pixel_center": pixel_center,
                               "nearest_internal_mesh_edge": nearest,
                               "distance_px": point_segment_distance(pixel_center, nearest)})
    repeat_path = FINE / "arch-candidate-v3.svg"
    repeat_png = FINE / "arch-candidate-v3-repeat.png"
    render(str(repeat_path), str(repeat_png), size=(width, height))
    checks["candidate"]["repeat_png_sha256"] = sha256(repeat_png)
    checks["candidate"]["repeat_png_byte_deterministic"] = (
        checks["candidate"]["repeat_png_sha256"] == checks["candidate"]["png_sha256"])
    return {"scope": "fixed parent fine96x12 teaching-arch geometry; same camera, fit, camber,"
                      " pixel-centre depth sample and safe-mask bounds; no visual/art verdict",
            "plan_sha256": sha256(plan_path), "image_sha256": sha256(
                ROOT / ".scratch/21-ribbon-cross-section/evidence/fine/panels/"
                "case-04-untwisted-teaching-arch-front-control-camber-035.png"),
            "fine_geometry": {"face_count": len(projected), "safe_pixels": int(safe.sum()),
                              "camber": .35, "u_segments": 96, "v_segments": 12},
            "source_current_candidate": checks, "fragment_areas": polygon_stats,
            "internal_mesh_edge_diagnostic": {"unique_internal_edges": len(internal_edges),
                                              "current_bad_pixels_near_mesh_edges": edge_proximity[:12],
                                              "all_current_bad_pixels_accounted_for": len(edge_proximity) == checks["canonical"]["nonmatching_base_pixels_in_safe_mask"]}}


def main():
    canonical_path = SCRIPTS / "vector_visibility.py"
    candidate_path = Path(__file__).with_name("vector_visibility_candidate.py")
    candidate_v1_path = Path(__file__).with_name("vector_visibility_candidate_v1.py")
    candidate_v2_path = Path(__file__).with_name("vector_visibility_candidate_v2.py")
    canonical_hash_before = sha256(canonical_path)
    if canonical_hash_before != "6cea919d0c83b1c4ebb9b3ec3379854c910e2758610b449c036c25c9ce8e1ada":
        raise RuntimeError("historical canonical visibility source hash is not the known input")
    canonical = load_module("study_canonical_visibility", canonical_path)
    candidate = load_module("study_candidate_visibility", candidate_path)
    result = {"scope": "candidate evaluation only; canonical implementation and historical evidence are read-only",
              "sources": {"canonical_path": str(canonical_path.relative_to(ROOT)),
                          "canonical_sha256_before": canonical_hash_before,
                          "candidate_path": str(candidate_path.relative_to(ROOT)),
                          "candidate_v1_sha256": sha256(candidate_v1_path),
                          "candidate_v2_sha256": sha256(candidate_v2_path),
                          "candidate_v3_sha256": sha256(candidate_path),
                          "plan_path": ".scratch/21-ribbon-cross-section/work/cases-fine.json"},
              "minimal_generated_mesh": mesh_raster_study(canonical, candidate),
              "fine_parent_reproduction": build_arch_probe(canonical, candidate)}
    canonical_hash_after = sha256(canonical_path)
    result["sources"]["canonical_sha256_after"] = canonical_hash_after
    result["sources"]["canonical_hash_unchanged"] = canonical_hash_before == canonical_hash_after
    out = FINE / "study-v3.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not result["sources"]["canonical_hash_unchanged"]:
        raise RuntimeError("canonical source changed during scratch-only study")


if __name__ == "__main__":
    main()
