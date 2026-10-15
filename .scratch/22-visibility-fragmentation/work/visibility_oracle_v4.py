"""Independent original-triangle depth oracle and bounded fragment-union audit.

Run from the repository root with .venv/bin/python. Sampling is tiled to each triangle/polygon
bbox; no full-frame-per-face or pixel-score tuning is used.
"""
import ast
import hashlib
import importlib.util
import inspect
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
EDGE_DISTANCE_TOL = 1e-12  # centered screen-coordinate units, fixed before candidate comparisons
POLYGON_AREA_FLOOR = 1e-18


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def resolver_tie_bias(module):
    """Read the signed declaration tie literals from the pinned resolver function source."""
    tree = ast.parse(inspect.getsource(module.visible_fragments))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not any(
                isinstance(target, ast.Name) and target.id == "bias" for target in node.targets):
            continue
        expression = node.value
        branches = ((expression.body, expression.orelse)
                    if isinstance(expression, ast.IfExp) else (expression,))
        values = []
        for branch in branches:
            if isinstance(branch, ast.Constant) and isinstance(branch.value, (float, int)):
                values.append(float(branch.value))
            elif (isinstance(branch, ast.UnaryOp) and isinstance(branch.op, ast.USub)
                  and isinstance(branch.operand, ast.Constant)
                  and isinstance(branch.operand.value, (float, int))):
                values.append(-float(branch.operand.value))
        if values:
            return max(abs(value) for value in values)
    raise ValueError("resolver source has no numeric visible_fragments declaration bias")


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


def original_triangle_oracle(faces, xs, ys, near_policy_band):
    """Barycentric source truth plus source-derived tie, layer, and edge masks."""
    shape = (len(ys), len(xs))
    strip_depth = np.full(shape, -np.inf, dtype=np.float64)
    body_depth = np.full(shape, -np.inf, dtype=np.float64)
    strip_second = np.full(shape, -np.inf, dtype=np.float64)
    body_second = np.full(shape, -np.inf, dtype=np.float64)
    strip_hits = np.zeros(shape, dtype=np.uint16)
    body_hits = np.zeros(shape, dtype=np.uint16)
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
        region = np.s_[iy0:iy1, ix0:ix1]
        xx, yy = np.meshgrid(xs[ix0:ix1], ys[iy0:iy1])
        wb = ((xx - x0) * (y2 - y0) - (yy - y0) * (x2 - x0)) / det
        wc = ((x1 - x0) * (yy - y0) - (y1 - y0) * (xx - x0)) / det
        wa = 1 - wb - wc
        weights = (wa, wb, wc)
        inside = (wa >= -1e-12) & (wb >= -1e-12) & (wc >= -1e-12)
        depth = wa * z0 + wb * z1 + wc * z2
        edge_ambiguous[region] |= inside & (np.minimum.reduce(
            [np.abs(value) for value in weights]) <= EDGE_BARY_EPS)
        if component == "strip":
            hits, top, second = strip_hits[region], strip_depth[region], strip_second[region]
        else:
            hits, top, second = body_hits[region], body_depth[region], body_second[region]
        hits[inside] += 1
        old_top = top.copy()
        new_top = np.maximum(old_top, depth)
        new_second = np.maximum(second, np.minimum(old_top, depth))
        top[inside] = new_top[inside]
        second[inside] = new_second[inside]
    strip_covered = np.isfinite(strip_depth)
    body_covered = np.isfinite(body_depth)
    both_covered = strip_covered & body_covered
    depth_delta = np.zeros(shape, dtype=np.float64)
    depth_delta[both_covered] = strip_depth[both_covered] - body_depth[both_covered]
    exact_depth_tie = both_covered & (np.abs(depth_delta) <= TIE_EPS)
    cross_component_near = both_covered & (np.abs(depth_delta) <= near_policy_band)
    strip_pair_covered = strip_covered & np.isfinite(strip_second)
    body_pair_covered = body_covered & np.isfinite(body_second)
    strip_depth_gap = np.zeros(shape, dtype=np.float64)
    body_depth_gap = np.zeros(shape, dtype=np.float64)
    strip_depth_gap[strip_pair_covered] = (strip_depth[strip_pair_covered]
                                           - strip_second[strip_pair_covered])
    body_depth_gap[body_pair_covered] = (body_depth[body_pair_covered]
                                         - body_second[body_pair_covered])
    strip_self_near = strip_pair_covered & (strip_depth_gap <= near_policy_band)
    body_self_near = body_pair_covered & (body_depth_gap <= near_policy_band)
    source_policy_ambiguous = (edge_ambiguous | exact_depth_tie | cross_component_near
                               | strip_self_near | body_self_near)
    visible = strip_covered & (~body_covered | (strip_depth > body_depth + TIE_EPS))
    return {"visible": visible, "source_policy_ambiguous": source_policy_ambiguous,
            "source_edge_ambiguous": edge_ambiguous,
            "exact_depth_tie_ambiguous": exact_depth_tie,
            "cross_component_near_policy_band": cross_component_near,
            "strip_same_component_top_near_tie": strip_self_near,
            "body_same_component_top_near_tie": body_self_near,
            "strip_hits": strip_hits, "body_hits": body_hits,
            "strip_covered": strip_covered, "degenerate_source_triangles": degenerate}


def point_polygon_membership(poly, xx, yy):
    """Return ray-crossing interior and a fixed Euclidean point-to-segment mask.

    EDGE_DISTANCE_TOL is in the centered screen-coordinate units. Projection is restricted to
    the actual segment endpoints only for this distance test; it is never used for clipping.
    """
    inside = np.zeros(xx.shape, dtype=bool)
    boundary = np.zeros(xx.shape, dtype=bool)
    tol2 = EDGE_DISTANCE_TOL * EDGE_DISTANCE_TOL
    for a, b in zip(poly, poly[1:] + poly[:1]):
        ax, ay, _ = a
        bx, by, _ = b
        dx, dy = bx - ax, by - ay
        length2 = dx * dx + dy * dy
        if length2 == 0:
            continue
        projection = ((xx - ax) * dx + (yy - ay) * dy) / length2
        closest_x = np.where(projection <= 0, ax,
                             np.where(projection >= 1, bx, ax + projection * dx))
        closest_y = np.where(projection <= 0, ay,
                             np.where(projection >= 1, by, ay + projection * dy))
        distance2 = (xx - closest_x) ** 2 + (yy - closest_y) ** 2
        boundary |= distance2 <= tol2
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


def sample_summary(oracle, predicted, fragment_boundary, cell_area, raw_area):
    truth = oracle["visible"]
    source_ambiguous = oracle["source_policy_ambiguous"]
    unambiguous = ~source_ambiguous & ~fragment_boundary
    false_positive = predicted & ~truth & unambiguous
    false_negative = ~predicted & truth & unambiguous
    oracle_count = int(np.count_nonzero(truth & unambiguous))
    predicted_count = int(np.count_nonzero(predicted & unambiguous))
    source_policy_counts = {
        "source_edge": int(np.count_nonzero(oracle["source_edge_ambiguous"])),
        "exact_depth_tie_1e-10": int(np.count_nonzero(oracle["exact_depth_tie_ambiguous"])),
        "cross_component_near_policy_band": int(np.count_nonzero(oracle["cross_component_near_policy_band"])),
        "strip_same_component_top_near_tie": int(np.count_nonzero(oracle["strip_same_component_top_near_tie"])),
        "body_same_component_top_near_tie": int(np.count_nonzero(oracle["body_same_component_top_near_tie"])),
        "unique_source_policy_union": int(np.count_nonzero(source_ambiguous))}
    return {"samples_total": int(truth.size),
            "source_policy_ambiguity_counts_overlapping_categories": source_policy_counts,
            "strip_samples_with_2plus_source_layers": int(np.count_nonzero(oracle["strip_hits"] >= 2)),
            "body_samples_with_2plus_source_layers": int(np.count_nonzero(oracle["body_hits"] >= 2)),
            "maximum_strip_source_layers_at_sample": int(oracle["strip_hits"].max(initial=0)),
            "maximum_body_source_layers_at_sample": int(oracle["body_hits"].max(initial=0)),
            "candidate_fragment_boundary_ambiguous_samples": int(np.count_nonzero(fragment_boundary)),
            "unambiguous_comparison_samples": int(np.count_nonzero(unambiguous)),
            "oracle_visible_unambiguous_samples": oracle_count,
            "oracle_fraction_of_raw_source_area_on_unambiguous_samples": oracle_count * cell_area / raw_area,
            "candidate_strict_interior_unambiguous_samples": predicted_count,
            "candidate_fraction_of_raw_source_area_on_unambiguous_samples": predicted_count * cell_area / raw_area,
            "false_positive_samples_on_unambiguous_domain": int(np.count_nonzero(false_positive)),
            "false_negative_samples_on_unambiguous_domain": int(np.count_nonzero(false_negative)),
            "false_positive_fraction_of_raw_source_area": np.count_nonzero(false_positive) * cell_area / raw_area,
            "false_negative_fraction_of_raw_source_area": np.count_nonzero(false_negative) * cell_area / raw_area}


def run():
    canonical_path = SCRIPTS / "vector_visibility.py"
    v1_path = WORK / "vector_visibility_candidate_v1.py"
    v2_path = WORK / "vector_visibility_candidate_v2.py"
    v3_path = WORK / "vector_visibility_candidate.py"
    modules = {"canonical": load_module("oracle_canonical", canonical_path),
               "candidate_v1": load_module("oracle_v1", v1_path),
               "candidate_v2": load_module("oracle_v2", v2_path),
               "candidate_v3": load_module("oracle_v3", v3_path)}
    resolver_bias = resolver_tie_bias(modules["candidate_v3"])
    near_policy_band = resolver_bias + modules["candidate_v3"].EPS
    result = {"scope": "independent sampled depth/coverage audit of original projected triangles; not a continuous proof",
              "method": {"geometry": "ring_and_occluder(yaw, segments=24) original projected triangle vertices only",
                         "coordinates": "subtract (200,150); source triangles depth-interpolated barycentrically; nearest depth is max z",
                         "sample_domain": "bounding box of original strip triangles; stratified cell centers",
                         "oracle_strip_visible": "max strip depth > max body depth + 1e-10 (or no body) at covered samples",
                         "source_policy_mask": "source-triangle barycentric edge hits <=1e-10; exact depth ties <=1e-10; source-derived cross-component and same-component top-layer near-tie band",
                         "resolver_declaration_tie_bias_from_source": resolver_bias,
                         "near_policy_band_depth_units": near_policy_band,
                         "near_policy_derivation": "absolute V3 visible_fragments bias parsed from hashed source plus unchanged public line_clip EPS; fixed before candidate-error comparison",
                         "boundary_test": "Euclidean distance to projected segment <=1e-12 centered coordinate units; projection endpoints are explicitly bounded; zero-length edges skipped",
                         "comparison": "strict fragment interior versus raw max-depth visibility in both directions; source-policy samples and fragment-boundary samples are counted/excluded explicitly, never accepted by a permissive union",
                         "union": "bbox-tiled point-in-polygon; zero-area/tiny <=1e-18 polygons and zero-length edges skipped",
                         "limits": "finite samples are observations, not rigorous continuous bounds; near-policy samples are not adjudicated under full declaration order; source tags are diagnostic only; raster component grouping is unchanged",
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
            oracle = original_triangle_oracle(centered, xs, ys, near_policy_band)
            grid_row = {"n": n, "phase": phase,
                        "oracle_source_edge_hits": int(np.count_nonzero(oracle["source_edge_ambiguous"])),
                        "oracle_exact_depth_ties": int(np.count_nonzero(oracle["exact_depth_tie_ambiguous"])),
                        "oracle_cross_component_near_policy_samples": int(np.count_nonzero(
                            oracle["cross_component_near_policy_band"])),
                        "oracle_strip_same_component_top_near_ties": int(np.count_nonzero(
                            oracle["strip_same_component_top_near_tie"])),
                        "oracle_body_same_component_top_near_ties": int(np.count_nonzero(
                            oracle["body_same_component_top_near_tie"])),
                        "oracle_source_policy_union_exclusions": int(np.count_nonzero(
                            oracle["source_policy_ambiguous"])),
                        "strip_source_layer_samples_ge2": int(np.count_nonzero(oracle["strip_hits"] >= 2)),
                        "body_source_layer_samples_ge2": int(np.count_nonzero(oracle["body_hits"] >= 2)),
                        "max_strip_source_layers": int(oracle["strip_hits"].max(initial=0)),
                        "max_body_source_layers": int(oracle["body_hits"].max(initial=0)),
                        "multiply_covered_strip_area_fraction_of_raw_sum": float(
                            np.maximum(oracle["strip_hits"].astype(np.int32) - 1, 0).sum()
                            * cell_area / raw_area),
                        "resolvers": {}}
            for name, geometry in geometries.items():
                union, boundary, skipped = fragment_union(geometry["polygons"], xs, ys)
                grid_row["resolvers"][name] = sample_summary(
                    oracle, union, boundary, cell_area, raw_area)
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
    out = OUTDIR / "visibility-oracle-v4.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"wrote {out.relative_to(ROOT)} sha256={sha256(out)}")


if __name__ == "__main__":
    run()
