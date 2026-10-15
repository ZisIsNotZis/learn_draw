"""Independent original-triangle depth oracle and bounded fragment-union audit.

Run from the repository root with .venv/bin/python. Sampling is tiled to each triangle/polygon
bbox; no full-frame-per-face or pixel-score tuning is used.
"""
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
WORK = Path(__file__).resolve().parent
OUTDIR = Path(__file__).resolve().parents[1] / "evidence" / "oracle"
OUTDIR.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(SCRIPTS))
from tests.test_vector_visibility import ring_and_occluder  # noqa: E402


TIE_EPS = 1e-10
EDGE_BARY_EPS = 1e-10
POLYGON_AREA_FLOOR = 1e-18


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def signed_area(poly):
    return sum(a[0] * b[1] - b[0] * a[1]
               for a, b in zip(poly, poly[1:] + poly[:1])) / 2


def polygon_area(poly):
    return abs(signed_area(poly))


def triangle_barycentric(triangle, x, y):
    (x0, y0, _), (x1, y1, _), (x2, y2, _) = triangle
    det = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
    if det == 0:
        return None
    wb = ((x - x0) * (y2 - y0) - (y - y0) * (x2 - x0)) / det
    wc = ((x1 - x0) * (y - y0) - (y1 - y0) * (x - x0)) / det
    return 1 - wb - wc, wb, wc


def source_subset_stats(polygons, source_triangles, module):
    outside_vertices = 0
    outside_fragments = 0
    max_barycentric_excursion = 0.0
    nonfinite_vertices = 0
    for poly, _color, tag in polygons:
        source_index = tag[1]
        source = source_triangles[source_index]
        fragment_outside = False
        for point in poly:
            if not all(math.isfinite(float(c)) for c in point):
                nonfinite_vertices += 1
                fragment_outside = True
                continue
            bary = triangle_barycentric(source, point[0], point[1])
            if bary is None:
                continue
            excursion = max(0.0, -min(bary))
            max_barycentric_excursion = max(max_barycentric_excursion, excursion)
            if excursion > 1e-10:
                outside_vertices += 1
                fragment_outside = True
        if fragment_outside:
            outside_fragments += 1
    return {"tagged_strip_fragments": len(polygons),
            "source_triangle_vertices_outside_by_more_than_1e-10_barycentric": outside_vertices,
            "source_triangle_fragments_with_outside_or_nonfinite_vertex": outside_fragments,
            "nonfinite_vertices": nonfinite_vertices,
            "max_barycentric_excursion": max_barycentric_excursion,
            "tag_semantics": "geometry-only source-owner tuple; does not change component/color grouping or raster calls"}


def segments_intersect(a, b, c, d, tol=1e-14):
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    o1, o2, o3, o4 = orient(a, b, c), orient(a, b, d), orient(c, d, a), orient(c, d, b)
    return (o1 * o2 < -tol * tol) and (o3 * o4 < -tol * tol)


def polygon_topology(polygons):
    zero_area = 0
    tiny_positive = 0
    nonfinite = 0
    nonconvex = 0
    nonsimple = 0
    skipped_for_union = 0
    for poly, _color, _tag in polygons:
        if not all(math.isfinite(float(c)) for point in poly for c in point):
            nonfinite += 1
            skipped_for_union += 1
            continue
        area2 = signed_area(poly)
        if area2 == 0:
            zero_area += 1
            skipped_for_union += 1
            continue
        if abs(area2) / 2 <= POLYGON_AREA_FLOOR:
            tiny_positive += 1
            skipped_for_union += 1
            continue
        points = [tuple(p[:2]) for p in poly]
        crosses = []
        for a, b, c in zip(points, points[1:] + points[:1], points[2:] + points[:2]):
            cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
            if abs(cross) > 1e-14:
                crosses.append(cross)
        if crosses and any(value * crosses[0] < 0 for value in crosses[1:]):
            nonconvex += 1
        edges = [(points[i], points[(i + 1) % len(points)]) for i in range(len(points))]
        bad = False
        n = len(edges)
        for i, (a, b) in enumerate(edges):
            if a == b:
                continue
            for j in range(i + 1, n):
                if j == i or j == (i + 1) % n or i == (j + 1) % n:
                    continue
                c, d = edges[j]
                if c == d:
                    continue
                if segments_intersect(a, b, c, d):
                    bad = True
                    break
            if bad:
                break
        if bad:
            nonsimple += 1
    return {"zero_area_polygons": zero_area, "positive_area_at_or_below_1e-18": tiny_positive,
            "nonfinite_polygons": nonfinite, "nonconvex_positive_polygons": nonconvex,
            "self_intersecting_positive_polygons": nonsimple,
            "zero_or_tiny_or_nonfinite_excluded_from_union": skipped_for_union}


def grid_axes(bounds, n, phase):
    xmin, ymin, xmax, ymax = bounds
    xs = xmin + (np.arange(n, dtype=np.float64) + phase) * ((xmax - xmin) / n)
    ys = ymin + (np.arange(n, dtype=np.float64) + phase) * ((ymax - ymin) / n)
    return xs, ys, ((xmax - xmin) / n) * ((ymax - ymin) / n)


def bbox_index_range(axis, low, high):
    left = max(0, int(np.searchsorted(axis, low, side="left")))
    right = min(len(axis), int(np.searchsorted(axis, high, side="right")))
    return left, right


def original_triangle_oracle(faces, xs, ys):
    shape = (len(ys), len(xs))
    strip_depth = np.full(shape, -np.inf, dtype=np.float64)
    body_depth = np.full(shape, -np.inf, dtype=np.float64)
    strip_hits = np.zeros(shape, dtype=np.uint16)
    edge_ambiguous = np.zeros(shape, dtype=bool)
    degenerate = 0
    for triangle, _color, component in faces:
        tri = np.asarray(triangle, dtype=np.float64)
        (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = tri
        det = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        if det == 0:
            degenerate += 1
            continue
        ix0, ix1 = bbox_index_range(xs, float(tri[:, 0].min()), float(tri[:, 0].max()))
        iy0, iy1 = bbox_index_range(ys, float(tri[:, 1].min()), float(tri[:, 1].max()))
        if ix0 >= ix1 or iy0 >= iy1:
            continue
        xx, yy = np.meshgrid(xs[ix0:ix1], ys[iy0:iy1])
        wb = ((xx - x0) * (y2 - y0) - (yy - y0) * (x2 - x0)) / det
        wc = ((x1 - x0) * (yy - y0) - (y1 - y0) * (xx - x0)) / det
        wa = 1 - wb - wc
        weights = (wa, wb, wc)
        inside = (wa >= -1e-12) & (wb >= -1e-12) & (wc >= -1e-12)
        if component == "strip":
            tile_hits = strip_hits[iy0:iy1, ix0:ix1]
            tile_hits[inside] += 1
            tile = strip_depth[iy0:iy1, ix0:ix1]
            depth = wa * z0 + wb * z1 + wc * z2
            np.maximum(tile, depth, out=tile, where=inside)
            edge_ambiguous[iy0:iy1, ix0:ix1] |= (inside & (np.minimum.reduce(
                [np.abs(value) for value in weights]) <= EDGE_BARY_EPS))
        else:
            tile = body_depth[iy0:iy1, ix0:ix1]
            depth = wa * z0 + wb * z1 + wc * z2
            np.maximum(tile, depth, out=tile, where=inside)
            edge_ambiguous[iy0:iy1, ix0:ix1] |= (inside & (np.minimum.reduce(
                [np.abs(value) for value in weights]) <= EDGE_BARY_EPS))
    strip_covered = np.isfinite(strip_depth)
    body_covered = np.isfinite(body_depth)
    both_covered = strip_covered & body_covered
    depth_delta = np.zeros(shape, dtype=np.float64)
    depth_delta[both_covered] = strip_depth[both_covered] - body_depth[both_covered]
    tie = both_covered & (np.abs(depth_delta) <= TIE_EPS)
    visible = strip_covered & (~body_covered | (strip_depth > body_depth + TIE_EPS))
    ambiguous = edge_ambiguous | tie
    return {"visible": visible, "ambiguous": ambiguous, "source_edge_ambiguous": edge_ambiguous,
            "depth_tie_ambiguous": tie, "strip_hits": strip_hits,
            "strip_covered": strip_covered, "degenerate_source_triangles": degenerate}


def point_polygon_membership(poly, xx, yy):
    """Return strict ray-crossing interior and sampled-edge ambiguity masks."""
    inside = np.zeros(xx.shape, dtype=bool)
    boundary = np.zeros(xx.shape, dtype=bool)
    for a, b in zip(poly, poly[1:] + poly[:1]):
        ax, ay, _ = a
        bx, by, _ = b
        dx, dy = bx - ax, by - ay
        length2 = dx * dx + dy * dy
        if length2 == 0:
            continue
        length = math.sqrt(length2)
        cross = (xx - ax) * dy - (yy - ay) * dx
        dot = (xx - ax) * dx + (yy - ay) * dy
        on_segment = ((np.abs(cross) <= 1e-12 * max(1.0, length))
                      & (dot >= -1e-12) & (dot <= length2 + 1e-12))
        boundary |= on_segment
        crosses_ray = (ay > yy) != (by > yy)
        if ay != by:
            x_at_y = ax + (yy - ay) * dx / dy
            inside ^= crosses_ray & (xx < x_at_y)
    return inside, boundary


def fragment_union(polygons, xs, ys):
    interior = np.zeros((len(ys), len(xs)), dtype=bool)
    boundary = np.zeros_like(interior)
    skipped = 0
    for poly, _color, _tag in polygons:
        if len(poly) < 3 or not all(math.isfinite(float(c)) for p in poly for c in p):
            skipped += 1
            continue
        if polygon_area(poly) <= POLYGON_AREA_FLOOR:
            skipped += 1
            continue
        points = np.asarray(poly, dtype=np.float64)
        ix0, ix1 = bbox_index_range(xs, float(points[:, 0].min()), float(points[:, 0].max()))
        iy0, iy1 = bbox_index_range(ys, float(points[:, 1].min()), float(points[:, 1].max()))
        if ix0 >= ix1 or iy0 >= iy1:
            continue
        xx, yy = np.meshgrid(xs[ix0:ix1], ys[iy0:iy1])
        is_inside, on_boundary = point_polygon_membership(poly, xx, yy)
        interior[iy0:iy1, ix0:ix1] |= is_inside & ~on_boundary
        boundary[iy0:iy1, ix0:ix1] |= on_boundary
    return interior, boundary, skipped


def resolver_geometry(module, faces):
    tagged = [(triangle, color, (component, index))
              for index, (triangle, color, component) in enumerate(faces)]
    polygons = list(module.visible_fragments(tagged))
    strip_polygons = [item for item in polygons if item[2][0] == "strip"]
    area_sum = sum(polygon_area(poly) for poly, _color, _tag in strip_polygons)
    raw_area = sum(polygon_area(triangle) for triangle, _color, component in faces
                   if component == "strip")
    return {"polygons": strip_polygons,
            "raw_area": raw_area,
            "sum_area": area_sum,
            "sum_fraction": area_sum / raw_area,
            "topology": polygon_topology(strip_polygons),
            "source_subset": source_subset_stats(strip_polygons,
                [triangle for triangle, _color, _component in faces], module)}


def sample_summary(oracle, predicted, possible, usable, cell_area, raw_area):
    truth = oracle["visible"]
    strict = predicted
    inclusive = possible
    false_positive = strict & ~truth & usable
    false_negative = ~strict & truth & usable
    possible_false_positive = inclusive & ~truth & usable
    possible_false_negative = ~inclusive & truth & usable
    oracle_count = int(np.count_nonzero(truth & usable))
    strict_count = int(np.count_nonzero(strict & usable))
    possible_count = int(np.count_nonzero(inclusive & usable))
    return {"samples_total": int(truth.size),
            "source_edge_ambiguous_samples": int(np.count_nonzero(oracle["source_edge_ambiguous"])),
            "depth_tie_ambiguous_samples": int(np.count_nonzero(oracle["depth_tie_ambiguous"])),
            "ambiguous_samples_excluded": int(np.count_nonzero(~usable)),
            "oracle_visible_nonambiguous_samples": oracle_count,
            "oracle_fraction_of_raw_source_area": oracle_count * cell_area / raw_area,
            "candidate_union_strict_interior_samples": strict_count,
            "candidate_union_strict_fraction_of_raw_source_area": strict_count * cell_area / raw_area,
            "candidate_union_possible_samples_including_sampled_boundary": possible_count,
            "candidate_union_possible_fraction_of_raw_source_area": possible_count * cell_area / raw_area,
            "strict_false_positive_samples": int(np.count_nonzero(false_positive)),
            "strict_false_negative_samples": int(np.count_nonzero(false_negative)),
            "strict_false_positive_fraction_of_raw_source_area": np.count_nonzero(false_positive) * cell_area / raw_area,
            "strict_false_negative_fraction_of_raw_source_area": np.count_nonzero(false_negative) * cell_area / raw_area,
            "possible_false_positive_samples": int(np.count_nonzero(possible_false_positive)),
            "possible_false_negative_samples": int(np.count_nonzero(possible_false_negative)),
            "possible_union_contains_all_oracle_visible_nonambiguous_sample_centers": not bool(
                np.any(possible_false_negative))}


def run():
    canonical_path = SCRIPTS / "vector_visibility.py"
    v1_path = WORK / "vector_visibility_candidate_v1.py"
    v2_path = WORK / "vector_visibility_candidate_v2.py"
    v3_path = WORK / "vector_visibility_candidate.py"
    modules = {"canonical": load_module("oracle_canonical", canonical_path),
               "candidate_v1": load_module("oracle_v1", v1_path),
               "candidate_v2": load_module("oracle_v2", v2_path),
               "candidate_v3": load_module("oracle_v3", v3_path)}
    result = {"scope": "independent sampled depth/coverage audit of original projected triangles; not a continuous proof",
              "method": {"geometry": "ring_and_occluder(yaw, segments=24) original projected triangle vertices only",
                         "coordinates": "subtract (200,150); source triangles depth-interpolated barycentrically; nearest depth is max z",
                         "sample_domain": "bounding box of original strip triangles; stratified cell centers",
                         "oracle_strip_visible": "max strip depth > max body depth + 1e-10 (or no body) at covered samples",
                         "ambiguous_samples": "exclude source-triangle hits with min absolute barycentric <=1e-10 and strip/body max-depth ties within 1e-10",
                         "union": "bbox-tiled point-in-polygon; zero-area/tiny <=1e-18 polygons and zero-length edges skipped; strict and sampled-boundary-inclusive results reported separately",
                         "limits": "finite samples are observations, not rigorous continuous bounds; source tags are diagnostic only; raster component grouping is not changed",
                         "phases": [0.5, 0.25, 0.75], "resolutions": [128, 256, 512, 1024]},
              "source_hashes": {"canonical": sha256(canonical_path),
                                "candidate_v1": sha256(v1_path), "candidate_v2": sha256(v2_path),
                                "candidate_v3": sha256(v3_path)},
              "by_yaw": {}}
    for yaw in (0, 55):
        faces = ring_and_occluder(yaw)
        centered = [( [(p[0] - 200, p[1] - 150, p[2]) for p in tri], color, component)
                    for tri, color, component in faces]
        strip_tris = [tri for tri, _color, component in centered if component == "strip"]
        raw_area = sum(polygon_area(tri) for tri in strip_tris)
        bounds = (min(p[0] for tri in strip_tris for p in tri),
                  min(p[1] for tri in strip_tris for p in tri),
                  max(p[0] for tri in strip_tris for p in tri),
                  max(p[1] for tri in strip_tris for p in tri))
        geometries = {name: resolver_geometry(module, centered) for name, module in modules.items()}
        grid_results = []
        configs = [(n, .5) for n in (128, 256, 512, 1024)] + [(1024, .25), (1024, .75)]
        for n, phase in configs:
            xs, ys, cell_area = grid_axes(bounds, n, phase)
            oracle = original_triangle_oracle(centered, xs, ys)
            usable = ~oracle["ambiguous"]
            grid_row = {"n": n, "phase": phase,
                        "oracle_source_edge_hits": int(np.count_nonzero(oracle["source_edge_ambiguous"])),
                        "oracle_depth_ties": int(np.count_nonzero(oracle["depth_tie_ambiguous"])),
                        "multiply_covered_strip_area_fraction_of_raw_sum": float(
                            np.maximum(oracle["strip_hits"].astype(np.int32) - 1, 0).sum()
                            * cell_area / raw_area),
                        "resolvers": {}}
            for name, geometry in geometries.items():
                union, boundary, skipped = fragment_union(geometry["polygons"], xs, ys)
                grid_row["resolvers"][name] = sample_summary(
                    oracle, union, union | boundary, usable, cell_area, raw_area)
                grid_row["resolvers"][name]["polygons_skipped_from_union"] = skipped
            grid_results.append(grid_row)
        result["by_yaw"][str(yaw)] = {
            "original_triangle_count": len(centered),
            "strip_triangle_count": len(strip_tris),
            "strip_bbox_centered": bounds,
            "raw_projected_strip_area_sum": raw_area,
            "resolvers": {name: {"sum_visible_fragment_area": value["sum_area"],
                                  "sum_fraction_of_raw_strip_area": value["sum_fraction"],
                                  "topology": value["topology"],
                                  "source_subset": value["source_subset"]}
                          for name, value in geometries.items()},
            "grid_observations": grid_results}
    out = OUTDIR / "visibility-oracle-v3.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"wrote {out.relative_to(ROOT)} sha256={sha256(out)}")


if __name__ == "__main__":
    run()
