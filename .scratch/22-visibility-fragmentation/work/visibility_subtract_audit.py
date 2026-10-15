"""Small deterministic EPS interpolation/source-subset audit for line_clip/subtract_convex."""
import hashlib
import importlib.util
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORK = Path(__file__).resolve().parent
OUT = Path(__file__).resolve().parents[1] / "evidence" / "oracle" / "subtract-eps-witness-v2.json"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def area(poly):
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(poly, poly[1:] + poly[:1])) / 2)


def barycentric(triangle, point):
    (x0, y0, _), (x1, y1, _), (x2, y2, _) = triangle
    det = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
    wb = ((point[0] - x0) * (y2 - y0) - (point[1] - y0) * (x2 - x0)) / det
    wc = ((x1 - x0) * (point[1] - y0) - (y1 - y0) * (point[0] - x0)) / det
    return 1 - wb - wc, wb, wc


def segment_parameter(point, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    denom = dx * dx + dy * dy
    t = ((point[0] - a[0]) * dx + (point[1] - a[1]) * dy) / denom
    distance = math.hypot(point[0] - a[0] - t * dx, point[1] - a[1] - t * dy)
    return t, distance


def line_witness(module, scale, keep_positive, reverse):
    if keep_positive:
        inside_x, outside_x = -.5 / scale, -1.5 / scale
    else:
        inside_x, outside_x = .5 / scale, 1.5 / scale
    source = [(inside_x, 0, 0), (outside_x, 1, 0), (inside_x, 2, 0)]
    if reverse:
        source.reverse()
    fn = lambda point: scale * module.EPS * point[0]
    result = module.line_clip(source, fn, keep_positive)
    source_vertices = []
    for point in result:
        vertex = {"point": point, "barycentric": barycentric(source, point),
                  "finite": all(math.isfinite(float(value)) for value in point)}
        if not any(math.dist(point, q) <= 1e-14 for q in source):
            segment_results = [segment_parameter(point, a, b)
                               for a, b in zip(source, source[1:] + source[:1])]
            nearest_t, nearest_distance = min(segment_results, key=lambda pair: pair[1])
            vertex["nearest_source_edge_t"] = nearest_t
            vertex["distance_to_source_edge"] = nearest_distance
        source_vertices.append(vertex)
    return {"scale": scale, "keep_positive": keep_positive, "reversed_input_winding": reverse,
            "vertices": source_vertices}


def exact_convex_intersection(subject, clipper):
    """Exact-sign Sutherland-Hodgman area used only to audit returned piece overlaps."""
    output = list(subject)
    orientation = 1 if sum(a[0] * b[1] - b[0] * a[1]
                           for a, b in zip(clipper, clipper[1:] + clipper[:1])) > 0 else -1
    for a, b in zip(clipper, clipper[1:] + clipper[:1]):
        if not output:
            return []
        def signed(p):
            return orientation * ((b[0] - a[0]) * (p[1] - a[1])
                                  - (b[1] - a[1]) * (p[0] - a[0]))
        next_output = []
        for first, second in zip(output, output[1:] + output[:1]):
            f_first, f_second = signed(first), signed(second)
            first_inside, second_inside = f_first >= 0, f_second >= 0
            if first_inside != second_inside:
                t = f_first / (f_first - f_second)
                next_output.append(tuple(first[k] + t * (second[k] - first[k])
                                         for k in range(3)))
            if second_inside:
                next_output.append(second)
        output = next_output
    return output


def subtract_summary(module, source, cutter):
    fragments = module.subtract_convex(source, cutter)
    source_area = area(source)
    fragment_areas = [area(poly) for poly in fragments]
    min_bary = min(min(barycentric(source, point)) for poly in fragments for point in poly)
    overlap = []
    for i, first in enumerate(fragments):
        for j in range(i + 1, len(fragments)):
            intersection = exact_convex_intersection(first, fragments[j])
            intersection_area = area(intersection) if len(intersection) >= 3 else 0
            if intersection_area > 1e-24:
                overlap.append({"fragment_indices": [i, j], "intersection_area": intersection_area,
                                "intersection_vertices": intersection})
    return {"fragment_count": len(fragments), "fragment_areas": fragment_areas,
            "source_area": source_area, "sum_fragment_area": sum(fragment_areas),
            "sum_to_source_area_ratio": sum(fragment_areas) / source_area,
            "minimum_source_barycentric_weight_over_vertices": min_bary,
            "nonfinite_vertices": sum(not math.isfinite(float(value))
                                       for poly in fragments for point in poly for value in point),
            "pairwise_positive_area_overlaps": overlap,
            "output_polygons": fragments,
            "zero_area_outputs": sum(value == 0 for value in fragment_areas),
            "serialization_move_count_after_zero_area_filter": module._compound_path(fragments).count("M ")}


def main():
    canonical_path = ROOT / "scripts/vector_visibility.py"
    v1_path = WORK / "vector_visibility_candidate_v1.py"
    v2_path = WORK / "vector_visibility_candidate.py"
    modules = {"canonical": load("subtract_canonical", canonical_path),
               "candidate_v1": load("subtract_v1", v1_path),
               "candidate_v2": load("subtract_v2", v2_path)}
    # This is the independent geometry review's fn=EPS*x witness.
    witness = [(-.8, 0, 0), (-1.2, 1, 0), (-.8, 2, 0)]
    line_results = {}
    for name, module in modules.items():
        line_results[name] = module.line_clip(witness, lambda p: module.EPS * p[0], True)
    # A thin but nondegenerate subject and short cutter edge produce edge-function values around EPS.
    subject = [(0, .0005, 0), (.001, .0015, 0), (0, .0006, 0)]
    cutter = [(0, 0, 1), (.0001, 0, 1), (.00005, .01, 1)]
    result = {"scope": "bounded kernel geometry witness; not a production acceptance",
              "source_hashes": {"canonical": sha(canonical_path), "candidate_v1": sha(v1_path),
                                "candidate_v2": sha(v2_path)},
              "line_clip_eps_times_x": {name: line_results[name] for name in modules},
              "line_clip_sign_scale_winding_cases": {
                  name: [line_witness(module, scale, sign, reverse)
                         for scale in (.5, 1.0, 2.0)
                         for sign in (True, False) for reverse in (False, True)]
                  for name, module in modules.items()},
              "subtract_convex_eps_edge_witness": {
                  "subject": subject, "cutter": cutter,
                  "signed_edge_function_at_subject_vertices": [
                      (cutter[1][0] - cutter[0][0]) * (p[1] - cutter[0][1])
                      - (cutter[1][1] - cutter[0][1]) * (p[0] - cutter[0][0])
                      for p in subject],
                  "by_resolver": {name: subtract_summary(module, subject, cutter)
                                  for name, module in modules.items()},
                  "interpretation": "inspect source-subset, sum-versus-union and pairwise overlaps separately; no overlap merge/tolerance mechanism added"}}
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"wrote {OUT.relative_to(ROOT)} sha256={sha(OUT)}")


if __name__ == "__main__":
    main()
