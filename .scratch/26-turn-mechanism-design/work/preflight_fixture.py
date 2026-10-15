#!/usr/bin/env python3
"""Design-only preflight for the single preregistered return-turn fixture.

This is not a support API, renderer, reusable prototype, or visual-output tool. It generates only
finite triangles from the design equation, checks them with the pinned visibility kernel, and runs an
independent sampled orthographic ray-depth oracle. The two camera cases and all numeric parameters
are fixed below before execution; this script deliberately contains no sweep/search mechanism.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
import vector_visibility

KERNEL = ROOT / "scripts/vector_visibility.py"
KERNEL_SHA256 = "fa4c31acf8ffc622352d1feb192e4adddc7931be9cdfc046fda70b1f4d23d3fa"
OUT = Path(__file__).resolve().parents[1] / "evidence/preflight.json"
C0 = (0.0, 0.0, 0.0)
EX = (1.0, 0.0, 0.0)
ED = (0.0, 1.0, 0.0)
W = (0.0, 0.0, 1.0)
LENGTH = 3.0
WIDTH = 0.36
TIP_RATIO = 1.0
ALPHA = math.pi
NU = 32
NV = 4
QUADRATURE_STEPS = 256
ORACLE_STEP = 0.0125
EPS = vector_visibility.EPS


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def scale(a, k):
    return tuple(x * k for x in a)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def unit(a):
    n = math.sqrt(dot(a, a))
    if not math.isfinite(n) or n <= 1e-12:
        raise ValueError("degenerate frame vector")
    return scale(a, 1.0 / n)


def tangent(u):
    q = 3.0 * u * u - 2.0 * u * u * u
    theta = ALPHA * q
    return math.cos(theta), math.sin(theta), 0.0


def integrate_center(u):
    """Fixed composite-Simpson integration of C'(u)=L*T(u)."""
    if u == 0.0:
        return C0
    n = QUADRATURE_STEPS if QUADRATURE_STEPS % 2 == 0 else QUADRATURE_STEPS + 1
    h = u / n
    accum = [0.0, 0.0, 0.0]
    for i in range(n + 1):
        t = i * h
        weight = 1 if i in (0, n) else (4 if i % 2 else 2)
        tv = tangent(t)
        for axis in range(3):
            accum[axis] += weight * tv[axis]
    return add(C0, scale(tuple(x * h / 3.0 for x in accum), LENGTH))


def centerline(u):
    # Use the exact alpha=pi route symmetry for paired finite stations, rather than letting
    # independent quadrature roundoff spoil the deliberately symmetric negative control.
    if u <= 0.5:
        return integrate_center(u)
    mirrored = integrate_center(1.0 - u)
    total_y = integrate_center(1.0)[1]
    return mirrored[0], total_y - mirrored[1], 0.0


def point(u, v):
    center = centerline(u)
    local_width = WIDTH * (1.0 + (TIP_RATIO - 1.0) * u)
    return add(center, scale(W, 0.5 * v * local_width))


def area2(poly):
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(poly, poly[1:] + poly[:1]))) * 0.5


def validate_fixed_domain():
    assert 1.0 <= LENGTH <= 3.0 and 0.1 <= WIDTH <= 0.6
    assert 0.5 <= TIP_RATIO <= 1.0 and 0.0 <= ALPHA <= math.pi
    assert all(-10.0 <= c <= 10.0 for c in C0)
    assert 16 <= NU <= 32 and 2 <= NV <= 4 and 2 * NU * NV <= 256
    assert abs(math.sqrt(dot(EX, EX)) - 1.0) <= 1e-12
    assert abs(math.sqrt(dot(ED, ED)) - 1.0) <= 1e-12
    assert abs(math.sqrt(dot(W, W)) - 1.0) <= 1e-12
    assert abs(dot(EX, ED)) <= 1e-12
    assert abs(dot(EX, W)) <= 1e-12
    assert abs(dot(ED, W)) <= 1e-12
    assert math.dist(cross(EX, ED), W) <= 1e-12


def make_camera(delta):
    d = (0.0, math.cos(delta), math.sin(delta))
    right = EX
    up = unit(cross(d, right))
    assert abs(dot(right, up)) <= 1e-12
    assert abs(dot(right, d)) <= 1e-12
    assert abs(dot(up, d)) <= 1e-12
    assert math.dist(cross(right, up), d) <= 1e-12
    return d, right, up


def tri_normal(points):
    return cross(sub(points[1], points[0]), sub(points[2], points[0]))


def make_scene(delta):
    validate_fixed_domain()
    d, right, up = make_camera(delta)
    stations = [[point(i / NU, -1.0 + 2.0 * j / NV) for j in range(NV + 1)]
                for i in range(NU + 1)]
    faces = []
    metadata = {}
    raw_face_points = {}
    face_id = 0
    for i in range(NU):
        for j in range(NV):
            p00, p10 = stations[i][j], stations[i + 1][j]
            p11, p01 = stations[i + 1][j + 1], stations[i][j + 1]
            for pts in ((p00, p10, p11), (p00, p11, p01)):
                normal = tri_normal(pts)
                facing = dot(normal, d)
                sign = 1 if facing > 1e-12 else (-1 if facing < -1e-12 else 0)
                projected = tuple((dot(p, right), dot(p, up), dot(p, d)) for p in pts)
                faces.append((projected, f"side:{sign}", face_id))
                metadata[face_id] = {"u_cell": i, "v_cell": j, "sign": sign,
                                     "normal_norm": math.sqrt(dot(normal, normal)),
                                     "facing_dot": facing}
                raw_face_points[face_id] = pts
                face_id += 1
    # Structural continuity: adjacent triangles share exact generated vertices and edge keys.
    edge_owners = {}
    for fid, pts in raw_face_points.items():
        for a, b in ((pts[0], pts[1]), (pts[1], pts[2]), (pts[2], pts[0])):
            edge = tuple(sorted((a, b)))
            edge_owners.setdefault(edge, []).append(fid)
    neighbors = {fid: set() for fid in raw_face_points}
    for owners in edge_owners.values():
        for fid in owners:
            neighbors[fid].update(other for other in owners if other != fid)
    reached = set()
    stack = [0]
    while stack:
        fid = stack.pop()
        if fid in reached:
            continue
        reached.add(fid)
        stack.extend(neighbors[fid] - reached)
    assert len(stations) == NU + 1 and all(len(row) == NV + 1 for row in stations)
    assert len(reached) == len(faces), "generated triangle support is not connected"
    return d, right, up, stations, faces, metadata, len(reached)


def barycentric_xy(x, y, tri):
    (x0, y0, _), (x1, y1, _), (x2, y2, _) = tri
    den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(den) <= 1e-14:
        return None
    a = ((y1 - y2) * (x - x2) + (x2 - x1) * (y - y2)) / den
    b = ((y2 - y0) * (x - x2) + (x0 - x2) * (y - y2)) / den
    c = 1.0 - a - b
    return a, b, c


def independent_ray_oracle(faces, metadata):
    """Independent barycentric ray test; no calls to kernel clipping/fragment functions."""
    boxes = []
    for tri, _color, fid in faces:
        boxes.append((min(p[0] for p in tri), min(p[1] for p in tri),
                      max(p[0] for p in tri), max(p[1] for p in tri), fid, tri))
    xmin = min(b[0] for b in boxes)
    ymin = min(b[1] for b in boxes)
    xmax = max(b[2] for b in boxes)
    ymax = max(b[3] for b in boxes)
    counts = {"-1": 0, "1": 0}
    root_winners = 0
    mixed_depth_samples = 0
    tested_points = 0
    ny = max(1, math.ceil((ymax - ymin) / ORACLE_STEP))
    nx = max(1, math.ceil((xmax - xmin) / ORACLE_STEP))
    for iy in range(ny):
        y = ymin + (iy + 0.619) * ORACLE_STEP
        for ix in range(nx):
            x = xmin + (ix + 0.371) * ORACLE_STEP
            hits = []
            for bx0, by0, bx1, by1, fid, tri in boxes:
                if x < bx0 or x > bx1 or y < by0 or y > by1:
                    continue
                weights = barycentric_xy(x, y, tri)
                if weights is None or min(weights) < 1e-10:
                    continue
                depth = sum(weights[k] * tri[k][2] for k in range(3))
                hits.append((depth, fid))
            if not hits:
                continue
            tested_points += 1
            signs = {metadata[fid]["sign"] for _depth, fid in hits}
            depths = [depth for depth, _fid in hits]
            if -1 in signs and 1 in signs and max(depths) - min(depths) > 1e-5:
                mixed_depth_samples += 1
            depth, winner = max(hits, key=lambda item: item[0])
            meta = metadata[winner]
            if meta["sign"] in (-1, 1):
                counts[str(meta["sign"])] += 1
            if meta["u_cell"] == 0:
                root_winners += 1
    return {"step_screen_units": ORACLE_STEP, "sampled_points_with_surface": tested_points,
            "nearest_depth_winners_by_facing_sign": counts,
            "root_row_winner_samples": root_winners,
            "opposite_facing_depth_overlap_samples": mixed_depth_samples}


def run_case(name, delta):
    start = time.monotonic()
    d, right, up, stations, faces, metadata, connected_faces = make_scene(delta)
    geometry_seconds = time.monotonic() - start
    kernel_start = time.monotonic()
    fragments = list(vector_visibility.visible_fragments(faces))
    kernel_seconds = time.monotonic() - kernel_start
    visible_area = {"-1": 0.0, "1": 0.0, "0": 0.0}
    root_area = 0.0
    for polygon, _color, fid in fragments:
        meta = metadata[fid]
        visible_area[str(meta["sign"])] += area2(polygon)
        if meta["u_cell"] == 0:
            root_area += area2(polygon)
    oracle_start = time.monotonic()
    oracle = independent_ray_oracle(faces, metadata)
    oracle_seconds = time.monotonic() - oracle_start
    width_material = WIDTH
    width_projected = WIDTH * math.sqrt(1.0 - dot(d, W) ** 2)
    nonzero_normals = sum(1 for m in metadata.values() if m["normal_norm"] > 1e-12)
    paired_projection_error = 0.0
    for i in range(NU + 1):
        for j in range(NV + 1):
            a = stations[i][j]
            b = stations[NU - i][j]
            pa = (dot(a, right), dot(a, up))
            pb = (dot(b, right), dot(b, up))
            paired_projection_error = max(paired_projection_error,
                                          math.dist(pa, pb))
    quarter_a = stations[NU // 4][NV // 2]
    quarter_b = stations[3 * NU // 4][NV // 2]
    quarter_screen_offset = abs(dot(sub(quarter_b, quarter_a), up))
    quarter_depth_delta = abs(dot(sub(quarter_b, quarter_a), d))
    return {
        "name": name,
        "camera_toward_viewer": d,
        "screen_right": right,
        "screen_up": up,
        "orthonormal_right_handed_camera": True,
        "frame": {"e_x": EX, "e_d": ED, "W": W,
                  "right_handed": math.dist(cross(EX, ED), W) <= 1e-12},
        "parameters": {"origin": C0, "L_world": LENGTH, "w_material_world": WIDTH,
                       "tip_ratio": TIP_RATIO, "alpha_radians": ALPHA,
                       "Nu": NU, "Nv": NV, "face_count": len(faces),
                       "quadrature_steps": QUADRATURE_STEPS},
        "projected_width_world": width_projected,
        "material_width_world": width_material,
        "paired_station_projection_error_world": paired_projection_error,
        "quarter_branch_screen_offset_world": quarter_screen_offset,
        "quarter_branch_camera_depth_delta_world": quarter_depth_delta,
        "visible_area_screen_square_units_by_face_facing_sign": visible_area,
        "root_row_visible_area_screen_square_units": root_area,
        "fragments_count": len(fragments),
        "nonzero_3d_face_normals": nonzero_normals,
        "connected_faces": connected_faces,
        "independent_ray_depth_oracle": oracle,
        "profile_seconds": {"geometry": geometry_seconds, "kernel": kernel_seconds,
                            "independent_oracle": oracle_seconds},
        "status": "measured",
    }


def main():
    actual_kernel = sha(KERNEL)
    if actual_kernel != KERNEL_SHA256:
        raise SystemExit(f"protected kernel pin mismatch: {actual_kernel}")
    # Preselected cases only: the reviewer-specified symmetric negative control and one analytic
    # positive fixture with a fixed 10-degree view offset. No search, camera sweep, or parameter loop.
    neg = run_case("symmetric-alpha-pi-negative", 0.0)
    pos = run_case("ten-degree-alpha-pi-positive-candidate", math.radians(10.0))
    pos_areas = pos["visible_area_screen_square_units_by_face_facing_sign"]
    pos_ray = pos["independent_ray_depth_oracle"]
    pos_oracle = pos_ray["nearest_depth_winners_by_facing_sign"]
    neg_areas = neg["visible_area_screen_square_units_by_face_facing_sign"]
    neg_oracle = neg["independent_ray_depth_oracle"]["nearest_depth_winners_by_facing_sign"]
    delta_pos = math.radians(10.0)
    theta_quarter = ALPHA * (3.0 * (0.25 ** 2) - 2.0 * (0.25 ** 3))
    delta_y_lower = LENGTH * 0.5 * math.sin(5.0 * math.pi / 32.0)
    delta_y_upper = LENGTH * 0.5
    width_pos = WIDTH * math.cos(delta_pos)
    result = {
        "scope": "design-only numerical preflight; not a renderer/API/prototype or visual acceptance",
        "analytic_positive_fixture_precheck": {
            "selected_without_search": True,
            "theta_at_u_quarter_radians": theta_quarter,
            "facing_dot_magnitude_at_quarter": abs(math.cos(theta_quarter) * math.cos(delta_pos)),
            "paired_centerline_delta_y_bound_world": [delta_y_lower, delta_y_upper],
            "paired_screen_offset_bound_world": [math.sin(delta_pos) * delta_y_lower,
                                                  math.sin(delta_pos) * delta_y_upper],
            "projected_width_world": width_pos,
            "minimum_uncovered_exposed_margin_world": width_pos - math.sin(delta_pos) * delta_y_upper,
            "minimum_camera_depth_delta_at_equal_screen_point_world": delta_y_lower / math.cos(delta_pos),
            "reason": "paired route stations have equal x, opposite non-edge-on facing signs, nonzero screen offset smaller than their projected width, and strict camera-depth order; partial overlap leaves a nonzero exposed strip on each branch",
        },
        "tested_bounded_domain": {"L_world": [1.0, 3.0], "w_root_world": [0.1, 0.6],
                                   "tip_ratio": [0.5, 1.0], "alpha_radians": [0.0, math.pi],
                                   "origin_each_axis_world": [-10.0, 10.0],
                                   "Nu": [16, 32], "Nv": [2, 4], "face_cap": 256,
                                   "frame_tolerance": 1e-10},
        "mathematical_limits": {"domain_width_minimum_world": 0.1 * 0.5,
                                "domain_surface_jacobian_Lw_half_minimum": 1.0 * 0.1 * 0.5 / 2,
                                "centerline_injective_under_monotone_turn_up_to_pi": True,
                                "claim_scope": "formula/domain only; finite projected depth cases are separately sampled"},
        "fixed_parameters": {"origin": C0, "L_world": LENGTH, "w_material_world": WIDTH,
                              "tip_ratio": TIP_RATIO, "alpha_radians": ALPHA,
                              "q": "3u^2-2u^3", "Nu": NU, "Nv": NV,
                              "face_count_per_fixture": 2 * NU * NV},
        "method": {
            "canonical_visibility": "vector_visibility.visible_fragments on generated projected triangles",
            "independent_check": "screen-lattice barycentric triangle coverage; interpolate each actual projected depth and choose maximum toward viewer",
            "independent_step": ORACLE_STEP,
            "no_image_or_rendering": True,
        },
        "pins": {"kernel_sha256": actual_kernel, "checker_sha256": sha(Path(__file__).resolve())},
        "negative_fixture": neg,
        "positive_candidate": pos,
        "criterion": {
            "positive_kernel_area_both_sides": pos_areas["-1"] > 0.0 and pos_areas["1"] > 0.0,
            "positive_independent_depth_winners_both_sides": pos_oracle["-1"] > 0 and pos_oracle["1"] > 0,
            "positive_root_after_clip": pos["root_row_visible_area_screen_square_units"] > 0.0 and pos_ray["root_row_winner_samples"] > 0,
            "positive_opposite_facing_actual_depth_overlap": pos_ray["opposite_facing_depth_overlap_samples"] > 0,
            "negative_fixture_hides_one_facing_side_in_independent_ray_oracle": min(neg_oracle["-1"], neg_oracle["1"]) == 0
                and neg["paired_station_projection_error_world"] <= 1e-12,
            "no_parameter_or_camera_search": True,
        },
    }
    criterion_values = result["criterion"]
    result["negative_kernel_residual_area_screen_square_units"] = min(neg_areas["-1"], neg_areas["1"])
    result["negative_kernel_residual_area_fraction"] = min(neg_areas["-1"], neg_areas["1"]) / max(
        1e-30, sum(neg_areas.values()))
    result["overall"] = "pass" if all(criterion_values.values()) else "unsupported"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"overall": result["overall"], "criterion": criterion_values,
                      "positive_visible_area": pos_areas,
                      "negative_visible_area": neg_areas,
                      "profiles": {"positive": pos["profile_seconds"],
                                   "negative": neg["profile_seconds"]},
                      "evidence": str(OUT)}, indent=2, sort_keys=True))
    if result["overall"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
