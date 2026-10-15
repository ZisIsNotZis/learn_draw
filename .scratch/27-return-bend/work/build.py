#!/usr/bin/env python3
"""Freeze-check, prove, then incrementally render the one authorized return-bend case matrix."""
from __future__ import annotations

import base64
import hashlib
import json
import math
import random
import sys
import tempfile
import time
import xml.sax.saxutils as sax

import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRATCH = ROOT / ".scratch/27-return-bend"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import vector_visibility
from draw import imread, render
from ribbon_family import (BACK_STRIPE_COLOR, FRONT_STRIPE_COLOR, RIBBON_STRIPE_HALF_V,
                           RibbonSpec, _clip_local_v, _fan_local_polygon, build_mesh,
                           mesh_triangles_uv)
from ribbon_return import (CARD_FILL, OrthographicCamera, ReturnSpec, build_return_mesh,
                           card_triangles, panel_svg, project_point, return_art_faces)
from vector_visibility import visible_fragments, visible_regions

SPEC_PATH = SCRATCH / "work/specs.json"
CASE_PATH = SCRATCH / "work/cases.json"
PRE_RESUME_PINS = SCRATCH / "evidence/provenance/pre-resume-pins.json"
PROTECTED_PANEL_PRODUCER_SHA = "d8f90f99641e5400e8ac2febafa7bc42c530c6dca8fd193041e86ff86dc62aaa"
FAILED_LABEL_BOARD_HASHES = {
    "svg": "2996568cc8b0104ebfe03f50ea98ecb510ebd63b6529df05e4558f6ef78cc904",
    "png": "4e295e27c2c02c8865b2db618655157e9350f1eade982967fb4d0975a5e8ba47",
}
KERNEL_PIN = "fa4c31acf8ffc622352d1feb192e4adddc7931be9cdfc046fda70b1f4d23d3fa"
FAMILY_PIN = "015ec14ec90da5768dbcdd9486220d3971c55673f0944971ccb3a8a47662bd3e"
OLD_CASES_PIN = "bd2732b806de26cc2d8a261be68e8f30e21e1f8f8bd5301556d85241a8bc5800"
REPLAY_PIN = "793ca4c206e44d3801cb5a1c82783a5fecbffb9d16e5c1539999445ba20b6034"
ORACLE_STEP = 0.0125


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def write_json(path: Path, data) -> None:
    write_atomic(path, (json.dumps(data, indent=2, sort_keys=True) + "\n").encode())


def frozen_inputs(specs, cases):
    expected = {
        ROOT / "scripts/vector_visibility.py": KERNEL_PIN,
        ROOT / "scripts/ribbon_family.py": FAMILY_PIN,
        ROOT / ".scratch/19-ribbon-family/work/cases.json": OLD_CASES_PIN,
        ROOT / ".scratch/24-clean-support-replay/work/cases-current.json": REPLAY_PIN,
        ROOT / ".scratch/24-clean-support-replay/evidence/panels/case-00-positive-half-twist-front-flat.svg":
            "54e1e474fe36e8dbaec9c7d73318b7832a88ecd8dcc4acc18d81828670379d09",
        ROOT / ".scratch/24-clean-support-replay/evidence/panels/case-04-untwisted-teaching-arch-front-control-flat.svg":
            "15e97acb08885105fafb670a78c8fdd88d999ad83ff0fad913a9af27a1b2d173",
    }
    actual = {str(path.relative_to(ROOT)): digest(path) for path, sha in expected.items()
              if path.exists() and digest(path) == sha}
    if len(actual) != len(expected):
        missing = [str(path) for path, sha in expected.items()
                   if not path.exists() or digest(path) != sha]
        raise RuntimeError(f"protected inputs do not match frozen pins: {missing}")
    if digest(SPEC_PATH) != cases["specs_sha256"]:
        raise RuntimeError("frozen specs SHA does not match cases plan")
    old_source_sha = digest(SCRIPTS / "ribbon_family.py")
    if old_source_sha != FAMILY_PIN or digest(SCRIPTS / "vector_visibility.py") != KERNEL_PIN:
        raise RuntimeError("protected renderer input changed")
    for name, expected_sha in (("twisted-two-sided", "23c2156b82b501f4be5c4a23005f0c3e0eb387a397ff408f17e576f564747618"),
                               ("teaching-arch", "f14e326804cc536214e0ae17993c43cbf5b1784fcb0ad55db2b4310f4b136b88")):
        _camera, ribbon = _old_case(specs, name)
        canonical = json.dumps(ribbon, sort_keys=True, separators=(",", ":")).encode()
        if hashlib.sha256(canonical).hexdigest() != expected_sha:
            raise RuntimeError(f"immutable old case {name} no longer matches its source hash")
    checkpoint = json.loads(PRE_RESUME_PINS.read_text(encoding="utf-8"))
    if checkpoint["cached_panel_origin"]["producer_sha256"] != PROTECTED_PANEL_PRODUCER_SHA:
        raise RuntimeError("cached panels are not bound to the stopped producer hash")
    if checkpoint["cached_panel_origin"]["renderer_kernel_sha256"] != KERNEL_PIN:
        raise RuntimeError("cached panels do not use the pinned renderer kernel")
    for path, expected_sha in (("scripts/ribbon_return.py", "618d701c3a26eb1f97d6b6cfd210ffe41eba3fe25032eb216d3c2ead398d2607"),
                               (".scratch/27-return-bend/work/specs.json", "c5f874f3bc4d15a30eeffdff1676d1bf7b26a8144f46b034bfe69f120fd60603"),
                               (".scratch/27-return-bend/work/cases.json", "95fa2bad3da49f092879d7cbfdd5871f7d7c6ff7a389ee1b55611b31f900cbbc"),
                               (".scratch/27-return-bend/evidence/proof/geometry-gate.json", "a0e4379fb33fab095d1d6e3d6d2178b9c94d1e41068b758ebce0ede045a0f878"),
                               (".scratch/27-return-bend/evidence/proof/geometry-gate-corrected.json", "83ccee28c349623c779329989be955946bfc25ca7c4f8decb6f3164522f13bae"),
                               (".scratch/27-return-bend/evidence/proof/geometry-gate-board-crop-build.json", "ecf027d2c29c1e0e8119171be775b8d1edef74c16a6804a40ef1f18321c292ad"),
                               (".scratch/27-return-bend/evidence/diagnostics/dminus-resolution-v2.json", "1d27022bfd3999d5ee2fac3ecc188229422232a596f8aa9c124f15376ebe492f")):
        if digest(ROOT / path) != expected_sha:
            raise RuntimeError(f"preserved source/proof input changed: {path}")
    expected_tokens = {case[side]["panel_token"] for case in cases["pairs"]
                       for side in ("before", "after")}
    if expected_tokens != set(checkpoint["cached_raw_panels"]):
        raise RuntimeError("cached panel token set differs from the frozen paired plan")
    for token, hashes in checkpoint["cached_raw_panels"].items():
        for suffix, expected_sha in hashes.items():
            path = SCRATCH / "evidence/panels" / f"{token}.{suffix}"
            if not path.is_file() or digest(path) != expected_sha:
                raise RuntimeError(f"checkpoint panel {token}.{suffix} changed; refusing stale reuse")
    progress_lines = [json.loads(line) for line in
                      (SCRATCH / "evidence/build-progress.jsonl").read_text().splitlines() if line]
    first_panel = next(i for i, item in enumerate(progress_lines) if item.get("event") == "panel-saved")
    origin_pin = next(item for item in reversed(progress_lines[:first_panel])
                      if item.get("event") == "pins-verified")
    if origin_pin["producer_sha256"] != PROTECTED_PANEL_PRODUCER_SHA:
        raise RuntimeError("saved panel hashes do not match their original producer pin")
    actual[".scratch/27-return-bend/evidence/provenance/pre-resume-pins.json"] = digest(PRE_RESUME_PINS)
    actual["cached_panel_origin_producer_sha256"] = PROTECTED_PANEL_PRODUCER_SHA
    return actual


def _old_case(specs, name):
    plan = json.loads((ROOT / ".scratch/24-clean-support-replay/work/cases-current.json").read_text())
    found = next(case for case in plan["cases"] if case["source"].get("case_name") == name)
    return found["camera"], found["ribbon"]


def cameras_from_specs(specs):
    result = {}
    for name, data in specs["camera_bases"].items():
        result[name] = OrthographicCamera(name, tuple(data["screen_right"]),
                                          tuple(data["screen_up"]), tuple(data["toward_viewer"]))
        result[name].validate()
    return result


def return_spec(specs, alpha: float, name: str) -> ReturnSpec:
    data = specs["return_support"]
    return ReturnSpec(name, tuple(data["root"]), tuple(data["root_tangent"]),
                      tuple(data["bend_normal"]), data["length"], data["width"],
                      data["tip_ratio"], alpha)


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def poly_area(polygon):
    return abs(sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(polygon, polygon[1:] + polygon[:1]))) / 2


def projected_support(mesh, camera):
    faces, signs, root_ids, normals = [], {}, set(), {}
    for face in mesh.faces:
        normal = cross(sub(face.points[1], face.points[0]), sub(face.points[2], face.points[0]))
        norm = math.sqrt(dot(normal, normal))
        facing = dot(normal, camera.toward_viewer)
        sign = 1 if facing > 1e-12 else (-1 if facing < -1e-12 else 0)
        signs[face.source_index] = sign
        normals[face.source_index] = {"normal_norm": norm, "facing_dot": facing}
        if face.u_cell == 0:
            root_ids.add(face.source_index)
        faces.append(([project_point(point, camera) for point in face.points],
                      f"side:{sign}", face.source_index))
    return faces, signs, root_ids, normals


def barycentric(x, y, tri):
    """Preflight-equivalent barycentrics; each depth uses these exact projected coordinates."""
    (x0, y0, _), (x1, y1, _), (x2, y2, _) = tri
    denominator = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(denominator) <= 1e-14:
        return None
    a = ((y1 - y2) * (x - x2) + (x2 - x1) * (y - y2)) / denominator
    b = ((y2 - y0) * (x - x2) + (x0 - x2) * (y - y2)) / denominator
    return a, b, 1.0 - a - b


def source_visibility_audit(faces, signs):
    source_ids = [fid for _triangle, _color, fid in faces]
    mismatches = []
    for triangle, _color, fid in faces:
        signed_area = ((triangle[1][0] - triangle[0][0]) * (triangle[2][1] - triangle[0][1])
                       - (triangle[1][1] - triangle[0][1]) * (triangle[2][0] - triangle[0][0]))
        projected_sign = 1 if signed_area > 1e-12 else (-1 if signed_area < -1e-12 else 0)
        if signs.get(fid) != projected_sign:
            mismatches.append({"source_index": fid, "normal_sign": signs.get(fid),
                               "projected_winding_sign": projected_sign})
    return {"ids_unique_dense": sorted(source_ids) == list(range(len(source_ids))),
            "facing_sign_mismatches": mismatches}


def independent_oracle(faces, signs, root_ids, categories=None):
    """Independent strict-interior barycentric ray test with maximum actual camera depth."""
    boxes = [(min(p[0] for p in tri), min(p[1] for p in tri),
              max(p[0] for p in tri), max(p[1] for p in tri), fid, tri)
             for tri, _color, fid in faces]
    degenerate = sum(1 for _x0, _y0, _x1, _y1, _fid, tri in boxes
                     if abs((tri[1][1] - tri[2][1]) * (tri[0][0] - tri[2][0])
                            + (tri[2][0] - tri[1][0]) * (tri[0][1] - tri[2][1])) <= 1e-14)
    xmin, ymin = min(b[0] for b in boxes), min(b[1] for b in boxes)
    xmax, ymax = max(b[2] for b in boxes), max(b[3] for b in boxes)
    nx, ny = math.ceil((xmax - xmin) / ORACLE_STEP), math.ceil((ymax - ymin) / ORACLE_STEP)
    winners = {"-1": 0, "0": 0, "1": 0}
    root_winners = mixed = samples = edge_memberships = edge_only = depth_ties = 0
    tag_winners, tag_overlap = {}, 0
    for iy in range(ny):
        y = ymin + (iy + 0.619) * ORACLE_STEP
        for ix in range(nx):
            x = xmin + (ix + 0.371) * ORACLE_STEP
            hits, edge_hits = [], 0
            for x0, y0, x1, y1, fid, tri in boxes:
                if x < x0 or x > x1 or y < y0 or y > y1:
                    continue
                weights = barycentric(x, y, tri)
                if weights is None:
                    continue
                low = min(weights)
                if -1e-10 <= low < 1e-10:
                    edge_hits += 1
                if low < 1e-10:
                    continue
                depth = sum(weights[k] * tri[k][2] for k in range(3))
                hits.append((depth, fid))
            edge_memberships += edge_hits
            if edge_hits and not hits:
                edge_only += 1
            if not hits:
                continue
            samples += 1
            hit_signs = {signs[fid] for _depth, fid in hits}
            depths_by_sign = {sign: max(depth for depth, fid in hits if signs[fid] == sign)
                              for sign in hit_signs}
            depths = [depth for depth, _fid in hits]
            if -1 in hit_signs and 1 in hit_signs:
                if max(depths) - min(depths) > 1e-5:
                    mixed += 1
                if abs(depths_by_sign[-1] - depths_by_sign[1]) <= 1e-5:
                    depth_ties += 1
            if categories is not None:
                kinds = {categories[fid] for _depth, fid in hits}
                if "card" in kinds and "ribbon" in kinds:
                    tag_overlap += 1
            _depth, winner = max(hits, key=lambda item: item[0])
            winners[str(signs[winner])] += 1
            root_winners += winner in root_ids
            if categories is not None:
                tag = categories[winner]
                tag_winners[tag] = tag_winners.get(tag, 0) + 1
    return {"step": ORACLE_STEP, "samples": samples, "winners_by_facing_sign": winners,
            "root_row_winners": root_winners, "opposite_facing_depth_overlap": mixed,
            "depth_policy_tie_samples_1e-5": depth_ties,
            "source_edge_memberships_1e-10": edge_memberships,
            "source_edge_only_points_1e-10": edge_only,
            "projected_degenerate_faces_1e-14": degenerate,
            "card_overlap_samples": tag_overlap, "tag_winners": tag_winners}


def clipped_area(faces, signs, root_ids):
    by_sign = {"-1": 0.0, "0": 0.0, "1": 0.0}
    root_area = 0.0
    fragments = list(visible_fragments(faces))
    for polygon, _color, source in fragments:
        by_sign[str(signs[source])] += poly_area(polygon)
        if source in root_ids:
            root_area += poly_area(polygon)
    return by_sign, root_area, len(fragments)


def sampled_centerline_self_intersection(mesh):
    root, ex, _w = mesh.spec.validate()
    ed = mesh.bend_direction
    centers = [tuple((row[0][axis] + row[-1][axis]) / 2 for axis in range(3))
               for row in mesh.rows]
    uv = [(dot(sub(point, root), ex), dot(sub(point, root), ed)) for point in centers]
    for first in range(len(uv) - 1):
        for second in range(first + 2, len(uv) - 1):
            a, b, c, d = uv[first], uv[first + 1], uv[second], uv[second + 1]
            ab, cd = (b[0] - a[0], b[1] - a[1]), (d[0] - c[0], d[1] - c[1])
            denominator = ab[0] * cd[1] - ab[1] * cd[0]
            if abs(denominator) <= 1e-12:
                continue
            delta = (c[0] - a[0], c[1] - a[1])
            t = (delta[0] * cd[1] - delta[1] * cd[0]) / denominator
            u = (delta[0] * ab[1] - delta[1] * ab[0]) / denominator
            if 1e-9 < t < 1 - 1e-9 and 1e-9 < u < 1 - 1e-9:
                return True
    return False


def support_connectivity(mesh):
    edge_owners = {}
    for face in mesh.faces:
        for a, b in ((face.points[0], face.points[1]), (face.points[1], face.points[2]),
                     (face.points[2], face.points[0])):
            edge_owners.setdefault(tuple(sorted((a, b))), []).append(face.source_index)
    neighbors = {face.source_index: set() for face in mesh.faces}
    for owners in edge_owners.values():
        for owner in owners:
            neighbors[owner].update(owners)
    reached, pending = set(), [0]
    while pending:
        face = pending.pop()
        if face in reached:
            continue
        reached.add(face)
        pending.extend(neighbors[face] - reached)
    return len(reached) == len(mesh.faces)


def geometry_proof(specs, cameras, case_plan):
    start = time.monotonic()
    by_name = {}
    fixed = return_spec(specs, math.pi, "primary-positive-return")
    for camera_name in ("D-plus-10deg", "D-minus-symmetric"):
        camera = cameras[camera_name]
        geometry_start = time.monotonic()
        mesh = build_return_mesh(fixed, 16, 2)
        faces, signs, roots, normals = projected_support(mesh, camera)
        geometry_seconds = time.monotonic() - geometry_start
        kernel_start = time.monotonic()
        areas, root_area, fragment_count = clipped_area(faces, signs, roots)
        kernel_seconds = time.monotonic() - kernel_start
        oracle_start = time.monotonic()
        oracle = independent_oracle(faces, signs, roots)
        oracle_seconds = time.monotonic() - oracle_start
        source_audit = source_visibility_audit(faces, signs)
        submitted_faces = len(return_art_faces(mesh, camera, with_card=False))
        row = {"camera": camera_name, "support_faces": len(faces), "submitted_art_faces_including_support": submitted_faces,
               "source_visibility_audit": source_audit, "connected": support_connectivity(mesh),
               "sampled_centerline_self_intersection": sampled_centerline_self_intersection(mesh),
               "finite_nonzero_normals": all(math.isfinite(n["normal_norm"])
                                               and n["normal_norm"] > 0 for n in normals.values()),
               "kernel_fragments": fragment_count, "depth_clipped_area_by_facing_sign": areas,
               "root_row_clipped_area": root_area, "independent_actual_depth_oracle": oracle,
               "material_width_world": fixed.width,
               "projected_width_world": fixed.width * math.sqrt(1 - dot(camera.toward_viewer,
                                                                           fixed.bend_normal) ** 2),
               "profile_seconds": {"geometry": geometry_seconds, "kernel": kernel_seconds,
                                   "independent_oracle": oracle_seconds}}
        by_name[camera_name] = row
    positive, negative = by_name["D-plus-10deg"], by_name["D-minus-symmetric"]
    positive_ok = (positive["connected"] and positive["finite_nonzero_normals"]
                   and positive["source_visibility_audit"]["ids_unique_dense"]
                   and not positive["source_visibility_audit"]["facing_sign_mismatches"]
                   and positive["depth_clipped_area_by_facing_sign"]["-1"] > 0
                   and positive["depth_clipped_area_by_facing_sign"]["1"] > 0
                   and positive["independent_actual_depth_oracle"]["winners_by_facing_sign"]["-1"] > 0
                   and positive["independent_actual_depth_oracle"]["winners_by_facing_sign"]["1"] > 0
                   and positive["independent_actual_depth_oracle"]["opposite_facing_depth_overlap"] > 0
                   and positive["root_row_clipped_area"] > 0
                   and positive["independent_actual_depth_oracle"]["root_row_winners"] > 0)
    negative_hidden = negative["independent_actual_depth_oracle"]["winners_by_facing_sign"]["-1"] == 0
    negative_ok = (negative_hidden and negative["source_visibility_audit"]["ids_unique_dense"]
                   and not negative["source_visibility_audit"]["facing_sign_mismatches"]
                   and negative["independent_actual_depth_oracle"]["winners_by_facing_sign"]["1"] > 0)
    variation_spec = return_spec(specs, 2 * math.pi / 3, "two-thirds-return")
    straight_spec = return_spec(specs, 0.0, "straight-control")
    other = {}
    for spec in (variation_spec, straight_spec):
        mesh = build_return_mesh(spec, 16, 2)
        for camera_name in ("D-plus-10deg",):
            camera = cameras[camera_name]
            faces, signs, roots, normals = projected_support(mesh, camera)
            areas, root_area, fragments = clipped_area(faces, signs, roots)
            oracle = independent_oracle(faces, signs, roots)
            source_audit = source_visibility_audit(faces, signs)
            art_count = len(return_art_faces(mesh, camera, with_card=False))
            if art_count > 256:
                raise RuntimeError("variation art exceeds the total submitted kernel-face cap")
            other[spec.name] = {"alpha_radians": spec.alpha, "support_faces": len(faces),
                                "sampled_centerline_self_intersection": sampled_centerline_self_intersection(mesh),
                                "submitted_art_faces": art_count, "source_visibility_audit": source_audit,
                                "area_by_facing_sign": areas, "root_area": root_area, "oracle": oracle,
                                "finite_nonzero_normals": all(n["normal_norm"] > 0 for n in normals.values()),
                                "kernel_fragments": fragments}
    card_mesh = build_return_mesh(fixed, 16, 2)
    card_camera = cameras["D-plus-10deg"]
    tagged, tags, roots, _normals = projected_support(card_mesh, card_camera)
    card_sources = card_triangles(fixed)
    card_ids = {}
    for index, triangle in enumerate(card_sources):
        source_id = len(card_mesh.faces) + index
        tags[source_id] = -1
        card_ids[source_id] = "card"
        tagged.append(([project_point(point, card_camera) for point in triangle], "card", source_id))
    for face in card_mesh.faces:
        card_ids[face.source_index] = "ribbon"
    tag_by_id = {fid: card_ids[fid] for _triangle, _color, fid in tagged}
    card_oracle = independent_oracle(tagged, tags, roots, tag_by_id)
    card_art_count = len(return_art_faces(card_mesh, card_camera, with_card=True))
    card_result = {"submitted_art_and_card_faces": card_art_count,
                   "actual_opaque_card_triangles": len(card_sources),
                   "independent_card_depth_oracle": card_oracle,
                   "card_wins_depth": card_oracle["tag_winners"].get("card", 0) > 0,
                   "card_overlaps_ribbon": card_oracle["card_overlap_samples"] > 0}
    other_geometry_ok = all(not case["sampled_centerline_self_intersection"]
                            and case["finite_nonzero_normals"] for case in other.values())
    passed = (positive_ok and negative_ok and other_geometry_ok and card_art_count <= 256
              and card_result["card_wins_depth"] and card_result["card_overlaps_ribbon"])
    return {"schema": 1, "status": "passed" if passed else "stopped-before-images",
            "positive_fixture_gate": positive_ok, "symmetric_negative_gate": negative_ok,
            "cases": by_name, "variation_and_straight": other, "card": card_result,
            "fixed_sampling": {"u_intervals": 16, "v_intervals": 2,
                               "support_faces": 64, "primary_submitted_art_faces": 160,
                               "card_case_total_submitted_faces": card_art_count,
                               "art_face_cap": 256,
                               "strict_interior_epsilon": 1e-10,
                               "projected_degenerate_epsilon": 1e-14,
                               "depth_policy_band": 1e-5},
            "timing": {"all_geometry_gates_seconds": time.monotonic() - start},
            "declared_limits": specs["limits"]}


def _legacy_faces(ribbon_data, camera, add_card):
    spec = RibbonSpec.from_mapping(ribbon_data)
    mesh = build_mesh(spec)
    stripe, body = [], []
    for source_id, local in enumerate(mesh_triangles_uv(mesh)):
        points = tuple(vertex[0] for vertex in local)
        normal = cross(sub(points[1], points[0]), sub(points[2], points[0]))
        side = "front" if dot(normal, camera.toward_viewer) > 0 else "back"
        stripe_color = FRONT_STRIPE_COLOR if side == "front" else BACK_STRIPE_COLOR
        local_polygon = list(local)
        local_polygon = _clip_local_v(local_polygon, -RIBBON_STRIPE_HALF_V, True)
        local_polygon = _clip_local_v(local_polygon, RIBBON_STRIPE_HALF_V, False)
        for tri in _fan_local_polygon(local_polygon):
            stripe.append(([project_point(vertex[0], camera) for vertex in tri], stripe_color,
                           f"legacy-local-stripe:{side}"))
        base_color = spec.front if side == "front" else spec.back
        body.append(([project_point(point, camera) for point in points], base_color,
                     f"legacy-axial-support:{side}"))
    faces = stripe + body
    if add_card:
        fixed = return_spec(json.loads(SPEC_PATH.read_text()), math.pi, "card-root")
        faces.extend(([project_point(point, camera) for point in triangle], CARD_FILL, "root-card-control")
                     for triangle in card_triangles(fixed))
    if len(faces) > 256:
        raise RuntimeError(f"unchanged axial control submits {len(faces)} faces, above cap")
    return spec, mesh, faces


def legacy_panel_svg(ribbon_data, camera, add_card):
    spec, mesh, faces = _legacy_faces(ribbon_data, camera, add_card)
    world = [point for face in mesh_triangles_uv(mesh) for point in face]
    world_points = [point[0] for point in world]
    if add_card:
        fixed = return_spec(json.loads(SPEC_PATH.read_text()), math.pi, "card-root")
        world_points.extend(point for triangle in card_triangles(fixed) for point in triangle)
    projected = [project_point(point, camera) for point in world_points]
    low_x, high_x = min(p[0] for p in projected), max(p[0] for p in projected)
    low_y, high_y = min(p[1] for p in projected), max(p[1] for p in projected)
    width, height = 420, 320
    scale = min(90.0, (width - 40) / max(high_x - low_x, 1e-12),
                (height - 40) / max(high_y - low_y, 1e-12))
    ox, oy = width / 2 - scale * (low_x + high_x) / 2, height / 2 + scale * (low_y + high_y) / 2
    transformed = [([(ox + scale * p[0], oy - scale * p[1], p[2]) for p in triangle], color, name)
                   for triangle, color, name in faces]
    paths = [f'<!-- {sax.escape(name)}: unchanged axial control local art; depth clipped -->'
             f'<path id="legacy-{index}" d="{path}" fill="{color}" fill-rule="nonzero"/>'
             for index, (path, color, name) in enumerate(visible_regions(transformed))]
    if not paths:
        raise RuntimeError("old control rendered as blank")
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="420" height="320" viewBox="0 0 420 320">'
            '<!-- Fixed-camera legacy control panel; unaltered source parameters. -->'
            '<rect id="panel-background" width="100%" height="100%" fill="#edf1ef"/>'
            '<g id="unchanged-legacy-control">' + ''.join(paths) + '</g></svg>')


def build_panels(specs, cases, cameras, progress_path, outdir, input_pins):
    start = time.monotonic()
    old_positive = _old_case(specs, "twisted-two-sided")[1]
    old_straight = _old_case(specs, "teaching-arch")[1]
    panel_sources = {}
    for pair in cases["pairs"]:
        before = pair["before"]
        after = pair["after"]
        camera = cameras[before["camera"]]
        old_data = old_straight if before["control"] == "unchanged untwisted teaching arch" else old_positive
        before_svg = legacy_panel_svg(old_data, camera, bool(before["card"]))
        alpha = after["alpha_radians"]
        spec = return_spec(specs, alpha, after["return_case"])
        mesh = build_return_mesh(spec, cases["sampling"]["u_intervals"],
                                 cases["sampling"]["v_intervals"])
        after_svg = panel_svg(mesh, cameras[after["camera"]], with_card=bool(after["card"]))
        for record, svg in ((before, before_svg), (after, after_svg)):
            token = record["panel_token"]
            svg_path = outdir / "panels" / f"{token}.svg"
            png_path = outdir / "panels" / f"{token}.png"
            svg_bytes = svg.encode()
            if not svg_path.is_file() or not png_path.is_file():
                raise RuntimeError(f"verified checkpoint panel {token} is missing; refusing regeneration")
            if svg_path.read_bytes() != svg_bytes:
                raise RuntimeError(f"frozen panel {token} differs from its source; refusing stale reuse")
            svg_sha = digest(svg_path)
            raster_audit = audit_raster(png_path, 420, 320, 20)
            panel_sources[token] = {"svg": str(svg_path.relative_to(ROOT)), "svg_sha256": svg_sha,
                                    "png": str(png_path.relative_to(ROOT)), "png_sha256": digest(png_path),
                                    "control_or_return": "return" if "return_case" in record else "control",
                                    "pair_id": pair["pair_id"], "cache_reused": True,
                                    "cache_origin_producer_sha256": input_pins["cached_panel_origin_producer_sha256"],
                                    "continuation_producer_sha256": digest(Path(__file__)),
                                    "raster_audit": raster_audit}
            with progress_path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps({"event": "panel-cache-verified", "token": token,
                                         "elapsed_seconds": time.monotonic() - start,
                                         "cache_origin_producer_sha256": input_pins["cached_panel_origin_producer_sha256"],
                                         "svg_sha256": svg_sha, "png_sha256": digest(png_path)},
                                        sort_keys=True) + "\n")
    return panel_sources, time.monotonic() - start


def audit_raster(path: Path, width: int, height: int, minimum_margin: int) -> dict:
    image = imread(str(path))
    if image.shape[:2] != (height, width):
        raise RuntimeError(f"raster frame changed for {path}: {image.shape[:2]}")
    changed = np.any(image != image[0, 0], axis=2)
    ys, xs = np.nonzero(changed)
    if len(xs) < 500:
        raise RuntimeError(f"raster is blank or unexpectedly sparse: {path}")
    bounds = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
    margins = [bounds[0], bounds[1], width - 1 - bounds[2], height - 1 - bounds[3]]
    if min(margins) < minimum_margin:
        raise RuntimeError(f"raster content is cropped or below minimum margin: {path}, {margins}")
    center_delta = [((bounds[0] + bounds[2]) / 2 - width / 2),
                    ((bounds[1] + bounds[3]) / 2 - height / 2)]
    return {"dimensions_px": [width, height], "changed_pixels": int(changed.sum()),
            "nonbackground_bounds_xyxy": bounds, "margins_ltrb_px": margins,
            "center_delta_px": center_delta}


def _embedded_image(path: Path, x: int, y: int) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return (f'<image x="{x}" y="{y}" width="420" height="320" '
            f'href="data:image/png;base64,{encoded}"/>')


def board_svg(cases, panels, labelled: bool) -> str:
    pairs = list(cases["pairs"])
    if labelled:
        order = pairs
        columns = [("before", "Axial / untwisted control — before"),
                   ("after", "Center-route return bend — after")]
    else:
        order = pairs[:]
        random.Random(cases["blind_board"]["unlabelled_panel_order_seed"]).shuffle(order)
        rng = random.Random(cases["blind_board"]["unlabelled_column_swap_seed"])
        columns = [("before", ""), ("after", "")]
        swaps = {pair["pair_id"]: bool(rng.getrandbits(1)) for pair in order}
    row_height = 370 if labelled else 330
    height = 20 + row_height * len(order)
    width = 900
    pieces = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
              f'viewBox="0 0 {width} {height}">',
              '<rect id="board-background" width="100%" height="100%" fill="#ffffff"/>']
    for row, pair in enumerate(order):
        y0 = 20 + row * row_height
        display = [("before", pair["before"]), ("after", pair["after"])]
        if not labelled and swaps[pair["pair_id"]]:
            display.reverse()
        if labelled:
            detail = pair["after"].get("alpha_radians")
            detail_text = (f"{pair['pair_id']} — {pair['after']['return_case']} alpha={detail:g} rad"
                           if detail is not None else pair["pair_id"])
            pieces.append(f'<text x="20" y="{y0 + 15}" font-size="14" fill="#203040">'
                          f'{sax.escape(detail_text)}</text>')
            pieces.append(f'<text x="20" y="{y0 + 33}" font-size="12" fill="#203040">'
                          f'{columns[0][1]}</text>')
            pieces.append(f'<text x="455" y="{y0 + 33}" font-size="12" fill="#203040">'
                          f'{columns[1][1]}</text>')
        ypanel = y0 + (36 if labelled else 0)
        for column, (_side, record) in enumerate(display):
            x = 20 + column * 440
            png = ROOT / panels[record["panel_token"]]["png"]
            pieces.append(_embedded_image(png, x, ypanel))
            if labelled:
                pieces.append(f'<rect x="{x}" y="{ypanel}" width="420" height="320" '
                              'fill="none" stroke="#aab4b2" stroke-width="1"/>')
    pieces.append('</svg>')
    return ''.join(pieces)


def render_boards(cases, panels, outdir):
    board_dir = outdir / "boards"
    board_dir.mkdir(parents=True, exist_ok=True)
    result = {}
    for label, labelled in (("labelled", True), ("unlabelled", False)):
        svg = board_svg(cases, panels, labelled)
        svg_path = board_dir / f"comparison-{label}.svg"
        png_path = board_dir / f"comparison-{label}.png"
        board_svg_changed = False
        if svg_path.exists() and svg_path.read_bytes() != svg.encode():
            failed_svg = board_dir / "diagnostics/comparison-labelled-margin-failure.svg"
            failed_png = board_dir / "diagnostics/comparison-labelled-margin-failure.png"
            if (label != "labelled" or not failed_svg.is_file() or not failed_png.is_file()
                    or digest(svg_path) != FAILED_LABEL_BOARD_HASHES["svg"]
                    or digest(failed_svg) != FAILED_LABEL_BOARD_HASHES["svg"]
                    or digest(png_path) != FAILED_LABEL_BOARD_HASHES["png"]
                    or digest(failed_png) != FAILED_LABEL_BOARD_HASHES["png"]):
                raise RuntimeError(f"frozen {label} board changed outside the recorded margin failure")
            write_atomic(svg_path, svg.encode())
            board_svg_changed = True
        elif not svg_path.exists():
            write_atomic(svg_path, svg.encode())
        if not png_path.exists() or board_svg_changed:
            render(str(svg_path), str(png_path))
        result[label] = {"svg": str(svg_path.relative_to(ROOT)), "svg_sha256": digest(svg_path),
                         "png": str(png_path.relative_to(ROOT)), "png_sha256": digest(png_path),
                         "raster_audit": audit_raster(png_path, 900, 20 +
                             (370 if labelled else 330) * len(cases["pairs"]), 4)}
    return result


def review_report_payload(cases, boards):
    """Route one randomized anonymous board only; raw panels stay outside blind payload."""
    return "\n".join([boards["unlabelled"]["png"], "", cases["blind_board"]["review_question"]]) + "\n"


def verify_raster_determinism(panels, boards, outdir):
    start = time.monotonic()
    candidates = {**{token: item for token, item in panels.items()},
                  **{f"board-{name}": item for name, item in boards.items()}}
    results = {}
    with tempfile.TemporaryDirectory(prefix="return-bend-raster-repeat-") as temp:
        for index, (name, item) in enumerate(sorted(candidates.items())):
            source = ROOT / item["svg"]
            expected_sha = item["png_sha256"]
            first, second = Path(temp) / f"{index}-first.png", Path(temp) / f"{index}-second.png"
            render(str(source), str(first))
            render(str(source), str(second))
            first_sha, second_sha = digest(first), digest(second)
            if first_sha != second_sha or first_sha != expected_sha:
                raise RuntimeError(f"two-process PNG determinism failed for {name}")
            results[name] = {"svg_sha256": digest(source), "stored_png_sha256": expected_sha,
                             "repeat_png_sha256": [first_sha, second_sha], "passed": True}
    record = {"schema": 1, "status": "passed", "renderer": "scripts/draw.py render / chrome-headless-shell",
              "image_count": len(results), "images": results,
              "elapsed_seconds": time.monotonic() - start}
    path = outdir / "provenance/determinism.json"
    write_json(path, record)
    return record, path


def main():
    geometry_only = sys.argv[1:] == ["--geometry-only"]
    if sys.argv[1:] not in ([], ["--geometry-only"]):
        raise SystemExit("usage: build.py [--geometry-only]")
    full_start = time.monotonic()
    specs = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    cases = json.loads(CASE_PATH.read_text(encoding="utf-8"))
    preexisting = frozen_inputs(specs, cases)
    outdir = SCRATCH / "evidence"
    progress_path = outdir / "build-progress.jsonl"
    outdir.mkdir(parents=True, exist_ok=True)
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    with progress_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"event": "pins-verified", "inputs": preexisting,
                                "kernel_import": vector_visibility.__file__,
                                "kernel_sha256": digest(SCRIPTS / "vector_visibility.py"),
                                "producer_sha256": digest(Path(__file__)),
                                "started": time.monotonic()}, sort_keys=True) + "\n")
    cameras = cameras_from_specs(specs)
    proof = geometry_proof(specs, cameras, cases)
    proof_version = ("geometry-gate-corrected.json" if geometry_only
                     else "geometry-gate-completion.json")
    proof_path = outdir / "proof" / proof_version
    write_json(proof_path, proof)
    with progress_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"event": "geometry-gate-complete", "status": proof["status"],
                                "proof_sha256": digest(proof_path), "proof_seconds": proof["timing"]},
                                sort_keys=True) + "\n")
    if proof["status"] != "passed" or geometry_only:
        print(json.dumps({"status": proof["status"], "proof": str(proof_path.relative_to(ROOT)),
                          "sha256": digest(proof_path),
                          "render_skipped": geometry_only or proof["status"] != "passed"}, indent=2))
        return 0 if proof["status"] == "passed" else 2
    panel_start = time.monotonic()
    panels, panel_seconds = build_panels(specs, cases, cameras, progress_path, outdir, preexisting)
    boards = render_boards(cases, panels, outdir)
    determinism, determinism_path = verify_raster_determinism(panels, boards, outdir)
    board_seconds = time.monotonic() - panel_start - panel_seconds
    artifact = {"schema": 1, "status": "generated-pending-independent-review",
                "specs": {"path": str(SPEC_PATH.relative_to(ROOT)), "sha256": digest(SPEC_PATH)},
                "cases": {"path": str(CASE_PATH.relative_to(ROOT)), "sha256": digest(CASE_PATH)},
                "sources": {"scripts/ribbon_return.py": digest(SCRIPTS / "ribbon_return.py"),
                            "scripts/tests/test_ribbon_return.py": digest(SCRIPTS / "tests/test_ribbon_return.py"),
                            "scripts/vector_visibility.py": digest(SCRIPTS / "vector_visibility.py"),
                            "scripts/ribbon_family.py": digest(SCRIPTS / "ribbon_family.py"),
                            str(Path(__file__).relative_to(ROOT)): digest(Path(__file__))},
                "protected_old_inputs_sha256": preexisting,
                "geometry_proof": {"path": str(proof_path.relative_to(ROOT)),
                                   "sha256": digest(proof_path)},
                "panels": panels, "boards": boards,
                "raster_determinism": {"path": str(determinism_path.relative_to(ROOT)),
                                       "sha256": digest(determinism_path),
                                       "image_count": determinism["image_count"]},
                "timing_seconds": {"full_build_including_images": time.monotonic() - full_start,
                                    "panels": panel_seconds, "boards": board_seconds,
                                    "geometry_proof": proof["timing"]["all_geometry_gates_seconds"]},
                "limitations": ["finite 16x2 support and current opaque triangle renderer only",
                                "actual depth oracle is sampled at 0.0125 screen units",
                                "midpoint remains edge-on; no claim of broad-facing at midpoint",
                                "D-minus negative retains nonzero kernel clipping residual",
                                "one preselected angle variation; no search or retuning",
                                "old controls re-rendered from unchanged old specs at frozen camera bases",
                                "no reference input, learner run, visual judgment or milestone acceptance"]}
    manifest_path = outdir / "provenance/build-manifest.json"
    write_json(manifest_path, artifact)
    report = review_report_payload(cases, boards)
    write_atomic(outdir / "report.txt", report.encode())
    with progress_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"event": "build-complete", "manifest_sha256": digest(manifest_path),
                                "full_build_seconds": time.monotonic() - full_start,
                                "report_sha256": digest(outdir / "report.txt")}, sort_keys=True) + "\n")
    print(json.dumps({"status": artifact["status"], "proof": str(proof_path.relative_to(ROOT)),
                      "proof_sha256": digest(proof_path),
                      "manifest": str(manifest_path.relative_to(ROOT)),
                      "manifest_sha256": digest(manifest_path), "report": str((outdir / "report.txt").relative_to(ROOT)),
                      "report_sha256": digest(outdir / "report.txt"),
                      "timing_seconds": artifact["timing_seconds"],
                      "submitted_faces": proof["card"]["submitted_art_and_card_faces"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
