#!/usr/bin/env python3
"""One frozen D-minus diagnostic: compare 16x2 and pinned reviewed 32x4 without images."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
import vector_visibility
from ribbon_return import OrthographicCamera, ReturnSpec, build_return_mesh, project_point

PRECHECK_PATH = ROOT / ".scratch/26-turn-mechanism-design/work/preflight_fixture.py"
PRECHECK_SHA = "205d889d4ef8da4878261552bc600b0fa605d644ec33d463b7e8e7be1ceb2fc1"
KERNEL_SHA = "fa4c31acf8ffc622352d1feb192e4adddc7931be9cdfc046fda70b1f4d23d3fa"
ORACLE_STEP = 0.0125
STRICT_INTERIOR_EPS = 1e-10
DEGENERATE_DENOMINATOR_EPS = 1e-14
DEPTH_ORDER_BAND = 1e-5
C0 = (0.0, 0.0, 0.0)
D_MINUS = OrthographicCamera("negative-D-minus", (1, 0, 0), (0, 0, -1), (0, 1, 0))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def screen_denominator(tri):
    (x0, y0, _), (x1, y1, _), (x2, y2, _) = tri
    return (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)


def barycentric_correct(x, y, tri):
    (x0, y0, _), (x1, y1, _), (x2, y2, _) = tri
    den = screen_denominator(tri)
    if abs(den) <= DEGENERATE_DENOMINATOR_EPS:
        return None
    a = ((y1 - y2) * (x - x2) + (x2 - x1) * (y - y2)) / den
    b = ((y2 - y0) * (x - x2) + (x0 - x2) * (y - y2)) / den
    return a, b, 1.0 - a - b


def barycentric_original_fault(x, y, tri):
    """Exact erroneous builder.py form, retained only to diagnose its raw false-negative gate."""
    (x0, y0, _), (x1, y1, _), (x2, y2, _) = tri
    den = screen_denominator(tri)
    if abs(den) <= DEGENERATE_DENOMINATOR_EPS:
        return None
    a = ((y1 - y2) * (x - x2) + (x2 - x1) * (y - y2)) / den
    b = ((y2 - y0) * (x - x2) + (x0 - x2) * (y - y0)) / den
    return a, b, 1.0 - a - b


def source_face_set(sample_count):
    if sample_count == 32:
        spec = importlib.util.spec_from_file_location("preflight_fixture_readonly", PRECHECK_PATH)
        preflight = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(preflight)
        _d, _r, _u, _stations, faces, metadata, connected = preflight.make_scene(0.0)
        assert connected == len(faces) == 256
        records = []
        for tri, _label, fid in faces:
            m = metadata[fid]
            i, j = m["u_cell"], m["v_cell"]
            u0, u1 = i / 32, (i + 1) / 32
            v0, v1 = -1 + 2 * j / 4, -1 + 2 * (j + 1) / 4
            local_uv = (((u0, v0), (u1, v0), (u1, v1)) if fid % 2 == 0
                        else ((u0, v0), (u1, v1), (u0, v1)))
            records.append({"fid": fid, "cell": [i, j], "tri": tri, "uv": local_uv,
                            "sign": m["sign"], "normal_norm": m["normal_norm"],
                            "facing_dot": m["facing_dot"], "source_label": m["sign"]})
        return records, preflight
    support = ReturnSpec("primary-return", C0, (1, 0, 0), (0, 0, 1), 3.0, 0.36, 1.0,
                         math.pi)
    mesh = build_return_mesh(support, 16, 2)
    records = []
    for face in mesh.faces:
        normal = cross(sub(face.points[1], face.points[0]), sub(face.points[2], face.points[0]))
        facing = dot(normal, D_MINUS.toward_viewer)
        sign = 1 if facing > 1e-12 else (-1 if facing < -1e-12 else 0)
        records.append({"fid": face.source_index, "cell": [face.u_cell, face.v_cell],
                        "tri": [project_point(p, D_MINUS) for p in face.points],
                        "uv": face.uv, "sign": sign, "normal_norm": math.sqrt(dot(normal, normal)),
                        "facing_dot": facing, "source_label": sign})
    return records, None


def classify(samples):
    records, preflight = source_face_set(samples)
    source_map = {row["fid"]: row for row in records}
    source_ids_ok = len(source_map) == len(records) and set(source_map) == set(range(len(records)))
    degenerate = [row["fid"] for row in records
                  if abs(screen_denominator(row["tri"])) <= DEGENERATE_DENOMINATOR_EPS]
    sign_errors = []
    for row in records:
        tri = row["tri"]
        signed_area = ((tri[1][0] - tri[0][0]) * (tri[2][1] - tri[0][1])
                       - (tri[1][1] - tri[0][1]) * (tri[2][0] - tri[0][0]))
        projected_sign = 1 if signed_area > 1e-12 else (-1 if signed_area < -1e-12 else 0)
        if projected_sign != row["source_label"]:
            sign_errors.append({"fid": row["fid"], "label": row["source_label"],
                                "projected_sign": projected_sign})
    valid = [row for row in records if row["fid"] not in degenerate]
    xmin = min(p[0] for row in valid for p in row["tri"])
    ymin = min(p[1] for row in valid for p in row["tri"])
    xmax = max(p[0] for row in valid for p in row["tri"])
    ymax = max(p[1] for row in valid for p in row["tri"])
    nx, ny = math.ceil((xmax - xmin) / ORACLE_STEP), math.ceil((ymax - ymin) / ORACLE_STEP)
    counts = {"sampled_lattice_points": 0, "correct_strict_surface_points": 0,
              "correct_positive_near_winners": 0, "correct_hidden_side_winners": 0,
              "correct_hidden_uncovered_points": 0, "correct_hidden_nearer_overlaps": 0,
              "depth_policy_ties_1e-5": 0, "source_edge_only_points": 0,
              "source_edge_memberships": 0, "buggy_hidden_winners": 0,
              "buggy_only_points_outside_true_mesh": 0,
              "buggy_only_points_on_predeclared_source_edge": 0,
              "buggy_hidden_winners_with_true_near_side_hit": 0,
              "buggy_hidden_winners_with_true_depth_tie": 0}
    witnesses = {"buggy_false_surface_memberships": [], "near_side_depth_witnesses": [],
                 "edge_policy_witnesses": [], "tie_policy_witnesses": []}
    for iy in range(ny):
        y = ymin + (iy + 0.619) * ORACLE_STEP
        for ix in range(nx):
            x = xmin + (ix + 0.371) * ORACLE_STEP
            counts["sampled_lattice_points"] += 1
            correct_hits, edge_hits, buggy_hits = [], [], []
            for row in valid:
                tri = row["tri"]
                bx0, bx1 = min(p[0] for p in tri), max(p[0] for p in tri)
                by0, by1 = min(p[1] for p in tri), max(p[1] for p in tri)
                if x < bx0 or x > bx1 or y < by0 or y > by1:
                    continue
                weights = barycentric_correct(x, y, tri)
                if weights is None:
                    continue
                lower = min(weights)
                depth = sum(weights[k] * tri[k][2] for k in range(3))
                hit = {"fid": row["fid"], "weights": weights, "depth": depth,
                       "sign": row["source_label"], "cell": row["cell"], "uv": row["uv"],
                       "normal_norm": row["normal_norm"], "facing_dot": row["facing_dot"]}
                if lower >= STRICT_INTERIOR_EPS:
                    correct_hits.append(hit)
                elif lower >= -STRICT_INTERIOR_EPS:
                    edge_hits.append(hit)
                wrong = barycentric_original_fault(x, y, tri)
                if wrong is not None and min(wrong) >= STRICT_INTERIOR_EPS:
                    wrong_depth = sum(wrong[k] * tri[k][2] for k in range(3))
                    buggy_hits.append((wrong_depth, row, wrong, weights, depth))
            if edge_hits:
                counts["source_edge_memberships"] += len(edge_hits)
                if not correct_hits:
                    counts["source_edge_only_points"] += 1
                    if len(witnesses["edge_policy_witnesses"]) < 3:
                        witness = edge_hits[0]
                        witnesses["edge_policy_witnesses"].append(
                            {"screen_xy": [x, y], "source_edge_hit": witness})
            if correct_hits:
                counts["correct_strict_surface_points"] += 1
            correct_hidden = [hit for hit in correct_hits if hit["sign"] == -1]
            correct_near = [hit for hit in correct_hits if hit["sign"] == 1]
            if correct_hits:
                correct_winner = max(correct_hits, key=lambda hit: hit["depth"])
                if correct_winner["sign"] == 1:
                    counts["correct_positive_near_winners"] += 1
                if correct_winner["sign"] == -1:
                    counts["correct_hidden_side_winners"] += 1
                    if not correct_near:
                        counts["correct_hidden_uncovered_points"] += 1
                    elif max(hit["depth"] for hit in correct_hidden) - max(
                            hit["depth"] for hit in correct_near) > DEPTH_ORDER_BAND:
                        counts["correct_hidden_nearer_overlaps"] += 1
                        if len(witnesses["near_side_depth_witnesses"]) < 3:
                            witnesses["near_side_depth_witnesses"].append(
                                {"screen_xy": [x, y], "winner": correct_winner,
                                 "nearest_opposite_sign": max(correct_near, key=lambda hit: hit["depth"])})
                if correct_hidden and correct_near and abs(
                        max(hit["depth"] for hit in correct_hidden)
                        - max(hit["depth"] for hit in correct_near)) <= DEPTH_ORDER_BAND:
                    counts["depth_policy_ties_1e-5"] += 1
                    if len(witnesses["tie_policy_witnesses"]) < 3:
                        witnesses["tie_policy_witnesses"].append(
                            {"screen_xy": [x, y], "hidden_hit": max(correct_hidden, key=lambda hit: hit["depth"]),
                             "near_hit": max(correct_near, key=lambda hit: hit["depth"])})
            if buggy_hits:
                wrong_winner = max(buggy_hits, key=lambda row: row[0])
                wrong_row = wrong_winner[1]
                if wrong_row["source_label"] == -1:
                    counts["buggy_hidden_winners"] += 1
                    correct_candidate_signs = {hit["sign"] for hit in correct_hits}
                    if 1 in correct_candidate_signs:
                        counts["buggy_hidden_winners_with_true_near_side_hit"] += 1
                    elif edge_hits and not correct_hits:
                        counts["buggy_only_points_on_predeclared_source_edge"] += 1
                    else:
                        counts["buggy_only_points_outside_true_mesh"] += 1
                    if correct_hidden and correct_near and abs(
                            max(hit["depth"] for hit in correct_hidden)
                            - max(hit["depth"] for hit in correct_near)) <= DEPTH_ORDER_BAND:
                        counts["buggy_hidden_winners_with_true_depth_tie"] += 1
                    if len(witnesses["buggy_false_surface_memberships"]) < 5:
                        witnesses["buggy_false_surface_memberships"].append({
                            "lattice_index_xy": [ix, iy], "screen_xy": [x, y],
                            "faulty_face_id": wrong_row["fid"],
                            "faulty_cell_uv": wrong_row["uv"], "faulty_weights": wrong_winner[2],
                            "correct_weights_for_same_face": wrong_winner[3],
                            "depth_interpolated_with_faulty_weights": wrong_winner[0],
                            "depth_interpolated_with_correct_weights": wrong_winner[4],
                            "correct_surface_hits_with_faulty_membership": [
                                {**hit, "faulty_weights_for_same_face": barycentric_original_fault(
                                    x, y, source_map[hit["fid"]]["tri"]),
                                 "faulty_interior_membership": barycentric_original_fault(
                                     x, y, source_map[hit["fid"]]["tri"]) is not None and
                                     min(barycentric_original_fault(
                                         x, y, source_map[hit["fid"]]["tri"])) >= STRICT_INTERIOR_EPS}
                                for hit in correct_hits[:3]],
                            "source_edge_hits": edge_hits[:3]})
    result = {"samples": samples, "support_face_count": len(records),
              "strict_projection_membership": {"strict_interior_epsilon": STRICT_INTERIOR_EPS,
                                                "degenerate_denominator_epsilon": DEGENERATE_DENOMINATOR_EPS,
                                                "depth_order_deadband": DEPTH_ORDER_BAND,
                                                "lattice_step": ORACLE_STEP,
                                                "lattice_offsets": [0.371, 0.619],
                                                "degenerate_projected_faces": degenerate},
              "source_id_sign_validation": {"ids_unique_and_dense": source_ids_ok,
                                             "facing_sign_mismatches": sign_errors},
              "counts": counts, "witnesses": witnesses}
    if preflight is not None:
        result["reviewed_preflight_oracle_crosscheck"] = preflight.independent_ray_oracle(
            [(row["tri"], "side", row["fid"]) for row in records],
            {row["fid"]: {"sign": row["source_label"], "u_cell": row["cell"][0]}
             for row in records})
    return result


def main():
    if sha(PRECHECK_PATH) != PRECHECK_SHA or sha(SCRIPTS / "vector_visibility.py") != KERNEL_SHA:
        raise RuntimeError("pinned read-only preflight/kernel input changed")
    start = time.monotonic()
    result = {"schema": 1, "purpose": "one fixed D-minus numeric diagnosis; no images or policy changes",
              "pins": {"reviewed_32x4_preflight": PRECHECK_SHA, "kernel": KERNEL_SHA,
                       "geometry_module": sha(SCRIPTS / "ribbon_return.py"),
                       "original_failed_proof": sha(ROOT / ".scratch/27-return-bend/evidence/proof/geometry-gate.json"),
                       "frozen_specs": sha(ROOT / ".scratch/27-return-bend/work/specs.json"),
                       "frozen_cases": sha(ROOT / ".scratch/27-return-bend/work/cases.json")},
              "fixed_fixture": {"C0": C0, "L": 3.0, "w": 0.36, "tip_ratio": 1.0,
                                "alpha_radians": math.pi, "camera": "D-minus-symmetric",
                                "samples_compared_only": ["16x2", "32x4"]},
              "classifier": {"correct_rule": "predeclared preflight barycentric b term uses y-y2; max actual depth wins",
                             "fault_reproduction": "the first gate's scratch builder used y-y0 in barycentric b; reproduced only to classify the original 611 count",
                             "masks_fixed_before_classification": True,
                             "source_edge_and_degenerate_policy": "strict min barycentric >=1e-10; source-edge candidates in [-1e-10,1e-10); abs denominator <=1e-14 is projected-degenerate",
                             "depth_order_policy": "fixed 1e-5 band for tie classification only; no thresholds swept",
                             "sample_lattice": "same design preflight step 0.0125 and offsets x=.371,y=.619"},
              "results": {"16x2": classify(16), "reviewed32x4": classify(32)},
              "elapsed_seconds": time.monotonic() - start}
    out = ROOT / ".scratch/27-return-bend/evidence/diagnostics/dminus-resolution-v2.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": "diagnosis-complete-no-render", "path": str(out.relative_to(ROOT)),
                      "sha256": sha(out), "elapsed_seconds": result["elapsed_seconds"],
                      "counts": {key: value["counts"] for key, value in result["results"].items()}}, indent=2))


if __name__ == "__main__":
    main()
