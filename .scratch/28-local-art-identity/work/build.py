#!/usr/bin/env python3
"""Freeze, audit, render, anonymize, and pin the bounded ex28 local-art comparison."""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
import os
import random
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
SCRATCH = ROOT / ".scratch/28-local-art-identity"
WORK = SCRATCH / "work"
EVIDENCE = SCRATCH / "evidence"
PANELS = EVIDENCE / "panels"
BOARDS = EVIDENCE / "boards"
PRIVATE = EVIDENCE / "private"
PROVENANCE = EVIDENCE / "provenance"
REVIEW = EVIDENCE / "review"
CACHE = WORK / "cache"
sys.path.insert(0, str(WORK))
sys.path.insert(0, str(ROOT / "scripts"))

import compile_case as cc
import vision_control
import build_review_payload as payloads

POLICIES = (cc.ArtPolicy.SIDE_DEPENDENT, cc.ArtPolicy.SHARED_FIXED_LOCAL)
SOURCE_FILES = (
    "work/compile_case.py", "work/build.py", "work/vision_control.py",
    "work/build_review_payload.py", "work/tests/test_compile_case.py",
    "work/tests/test_review_payload.py",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _new(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as output:
        output.write(data)


def _json_new(path: Path, value: Any) -> None:
    _new(path, (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode())


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _progress(event: str, **details) -> None:
    PROVENANCE.mkdir(parents=True, exist_ok=True)
    record = {"event": event, "utc": _utc(), **details}
    with (PROVENANCE / "build-progress.jsonl").open("a", encoding="utf-8") as output:
        output.write(json.dumps(record, sort_keys=True) + "\n")


def _mkdirs() -> None:
    for path in (PANELS, BOARDS, PRIVATE, PROVENANCE, REVIEW / "precheck", CACHE):
        path.mkdir(parents=True, exist_ok=True)


def prebuild_pins() -> dict[str, Any]:
    pins = cc.verify_pinned_inputs()
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True, timeout=10, check=True).stdout.strip()
    staged = subprocess.run(["git", "diff", "--cached", "--binary"], cwd=ROOT,
                            capture_output=True, timeout=10, check=True).stdout
    staged_sha = hashlib.sha256(staged).hexdigest()
    if head != "24693d4b764755165509fc206695ebca03ee44fe":
        raise RuntimeError(f"unexpected starting HEAD: {head}")
    if staged_sha != "d36b0b11e5833b1ba841b29af202dc157482b064eb9bb0c432684e74f6eae4a4":
        raise RuntimeError("inherited staged state changed; stopping without touching it")
    record = {"schema": "local-art-identity-prebuild-pins/v1", "head": head,
              "inherited_staged_patch_sha256": staged_sha,
              "verified_input_count": len(pins), "verified_inputs": pins,
              "no_index_or_protected_input_changes": True}
    path = PROVENANCE / "prebuild-pins.json"
    if path.exists():
        if json.loads(path.read_text(encoding="utf-8")) != record:
            raise RuntimeError("existing prebuild pin record is stale; refusing to relabel it")
    else:
        _json_new(path, record)
    _progress("prebuild-inputs-verified", record_sha256=digest(path), count=len(pins))
    print(json.dumps({"prebuild_pins_sha256": digest(path), "verified_inputs": len(pins)}, sort_keys=True))
    return record


def _frozen_mapping() -> dict[str, Any]:
    rng = random.Random(2801)
    rows = list(cc.CASE_ORDER)
    rng.shuffle(rows)
    shared_columns = [0, 0, 1, 1]
    rng.shuffle(shared_columns)
    placements = []
    for row_index, (case_name, shared_column) in enumerate(zip(rows, shared_columns)):
        cells = [
            {"column": shared_column, "policy": cc.ArtPolicy.SHARED_FIXED_LOCAL.value},
            {"column": 1 - shared_column, "policy": cc.ArtPolicy.SIDE_DEPENDENT.value},
        ]
        cells.sort(key=lambda cell: cell["column"])
        for cell in cells:
            placements.append({"row": row_index, "column": cell["column"],
                               "case_id": case_name, "policy": cell["policy"]})
    return {"schema": "local-art-identity-private-mapping/v1", "seed": 2801,
            "rows": rows, "placements": placements,
            "column_policy_counts": {
                str(column): {policy.value: sum(item["column"] == column
                                                and item["policy"] == policy.value
                                                for item in placements)
                              for policy in POLICIES}
                for column in (0, 1)},
            "mapping_is_evaluator_private": True}


def freeze() -> dict[str, str]:
    _mkdirs()
    cc.verify_pinned_inputs()
    cases_path = PROVENANCE / "cases.json"
    mapping_path = PRIVATE / "mapping.json"
    cases = cc.cases_document()
    mapping = _frozen_mapping()
    if cases_path.exists() or mapping_path.exists():
        if not cases_path.is_file() or not mapping_path.is_file():
            raise RuntimeError("frozen case/mapping pair is incomplete; refusing relabel")
        if (json.loads(cases_path.read_text(encoding="utf-8")) != cases
                or json.loads(mapping_path.read_text(encoding="utf-8")) != mapping):
            raise RuntimeError("frozen cases/mapping differ from their source contract")
        result = {"cases_sha256": digest(cases_path),
                  "private_mapping_sha256": digest(mapping_path)}
        _progress("frozen-plan-reverified", **result)
        print(json.dumps(result, sort_keys=True))
        return result
    if list(PANELS.glob("*")) or list(BOARDS.glob("*")):
        raise RuntimeError("cases and private mapping must freeze before any images exist")
    if any(mapping["column_policy_counts"][str(column)][policy.value] != 2
           for column in (0, 1) for policy in POLICIES):
        raise RuntimeError("private board mapping is not balanced across columns")
    if set(mapping["rows"]) != set(cc.CASE_ORDER) or len(mapping["placements"]) != 8:
        raise RuntimeError("private mapping does not cover exactly four cases and eight panels")
    _json_new(cases_path, cases)
    _json_new(mapping_path, mapping)
    result = {"cases_sha256": digest(cases_path), "private_mapping_sha256": digest(mapping_path)}
    _progress("frozen-before-images", **result)
    print(json.dumps(result, sort_keys=True))
    return result


def _load_old_build():
    work_path = str(ROOT / ".scratch/27-return-bend/work")
    if work_path not in sys.path:
        sys.path.insert(0, work_path)
    name = "ex27_pinned_build_for_oracle"
    spec = importlib.util.spec_from_file_location(name, cc.OLD_BUILD_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the pinned independent geometry/oracle implementation")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _full_scene_oracle(scene, case_id: cc.CaseId, camera, frame: dict[str, Any], old_build):
    scale = frame["scale_px_per_world_unit"]
    offset_x, offset_y = frame["offset_px"]
    projected_faces, signs, categories, source_faces = [], {}, {}, {}
    for index, item in enumerate(scene):
        raw_triangle = tuple(((point[0] - offset_x) / scale,
                              (offset_y - point[1]) / scale, point[2])
                             for point in item.points)
        projected_faces.append((raw_triangle, item.pigment, index))
        categories[index] = "card" if item.provenance == "root-attached-card" else "ribbon"
        if item.provenance.startswith("support-body:"):
            source_faces[item.source_face_index] = (1 if item.provenance.endswith(":front") else -1)
    roots = set()
    for index, item in enumerate(scene):
        if item.provenance == "root-attached-card":
            triangle = projected_faces[index][0]
            area = ((triangle[1][0] - triangle[0][0]) * (triangle[2][1] - triangle[0][1])
                    - (triangle[1][1] - triangle[0][1]) * (triangle[2][0] - triangle[0][0]))
            signs[index] = 1 if area > 1e-12 else (-1 if area < -1e-12 else 0)
            continue
        source_index = item.source_face_index
        if source_index not in source_faces:
            raise RuntimeError("local art does not identify its source support face")
        signs[index] = source_faces[source_index]
        if source_index < 64 and source_index // 4 == 0:
            roots.add(index)
    result = old_build.independent_oracle(projected_faces, signs, roots, categories)
    return result


def _actual_geometry(case_id: cc.CaseId, old_build, completion: dict) -> dict[str, Any]:
    rr, spec, camera = cc._spec_and_camera(case_id)
    mesh = rr.build_return_mesh(spec, 16, 2)
    faces, signs, roots, normals = old_build.projected_support(mesh, camera)
    unoccluded_areas, unoccluded_root_area, _base_fragment_count = old_build.clipped_area(
        faces, signs, roots)
    case_name = case_id.value
    if cc.CASE_CONFIG[case_name]["card"]:
        for index, triangle in enumerate(rr.card_triangles(spec)):
            source_id = len(mesh.faces) + index
            faces.append(([rr.project_point(point, camera) for point in triangle], "card", source_id))
            signs[source_id] = 0
    areas, root_area, fragment_count = old_build.clipped_area(faces, signs, roots)
    oracle = old_build.independent_oracle(faces, signs, roots)
    if case_name == "primary-dplus":
        previous = completion["cases"]["D-plus-10deg"]
        previous_area_key, previous_root_key = "depth_clipped_area_by_facing_sign", "root_row_clipped_area"
        previous_oracle_key = "independent_actual_depth_oracle"
    elif case_name == "variation-2pi3-dplus":
        previous = completion["variation_and_straight"]["two-thirds-return"]
        previous_area_key, previous_root_key = "area_by_facing_sign", "root_area"
        previous_oracle_key = "oracle"
    else:
        previous = completion["cases"]["D-minus-symmetric"]
        previous_area_key, previous_root_key = "depth_clipped_area_by_facing_sign", "root_row_clipped_area"
        previous_oracle_key = "independent_actual_depth_oracle"
    has_card = cc.CASE_CONFIG[case_name]["card"]
    if has_card:
        positive_reference = completion["cases"]["D-plus-10deg"]
        if (unoccluded_areas != positive_reference["depth_clipped_area_by_facing_sign"]
                or unoccluded_root_area != positive_reference["root_row_clipped_area"]):
            raise RuntimeError("card case changed its underlying fixed return support geometry")
        if len(oracle["tag_winners"]) != 0:
            raise RuntimeError("support-only actual-depth oracle included card face labels unexpectedly")
    elif areas != previous[previous_area_key] or root_area != previous[previous_root_key]:
        raise RuntimeError(f"actual clipped support areas changed for {case_name}")
    if oracle != previous[previous_oracle_key] and not has_card:
        raise RuntimeError(f"independent max-depth oracle changed for {case_name}")
    total = 162 if has_card else 160
    if len(mesh.faces) != 64 or len(normals) != 64:
        raise RuntimeError("frozen 16x2 support triangles or normals changed")
    return {"support_faces": len(mesh.faces), "area_by_facing_sign": areas,
            "root_area": root_area, "unoccluded_support_area_by_facing_sign": unoccluded_areas,
            "unoccluded_support_root_area": unoccluded_root_area,
            "visible_fragment_count": fragment_count,
            "independent_actual_depth_oracle": oracle, "submitted_inputs": total,
            "support_sha256": cc._support_and_camera_hash(case_id)[0],
            "camera_sha256": cc._support_and_camera_hash(case_id)[1]}


def _card_oracle(old_build, completion) -> dict[str, Any]:
    case_id = cc.CaseId.CARD_DPLUS
    rr, spec, camera = cc._spec_and_camera(case_id)
    mesh = rr.build_return_mesh(spec, 16, 2)
    tagged, signs, roots, _normals = old_build.projected_support(mesh, camera)
    categories = {face.source_index: "ribbon" for face in mesh.faces}
    for index, triangle in enumerate(rr.card_triangles(spec)):
        source_id = len(mesh.faces) + index
        tagged.append(([rr.project_point(point, camera) for point in triangle], "card", source_id))
        signs[source_id] = -1
        categories[source_id] = "card"
    oracle = old_build.independent_oracle(tagged, signs, roots, categories)
    fixed = completion["card"]
    if oracle != fixed["independent_card_depth_oracle"]:
        raise RuntimeError("actual card depth winners/occlusion differ from the frozen proof")
    if len(tagged) != 66 or not oracle["tag_winners"].get("card", 0):
        raise RuntimeError("fixed opaque card input/winner proof failed")
    return {"submitted_inputs": 162, "actual_card_triangles": 2,
            "independent_card_depth_oracle": oracle, "card_wins_depth": True,
            "card_overlaps_ribbon": oracle["card_overlap_samples"] > 0}


def audit() -> dict[str, Any]:
    started = time.monotonic()
    cc._verify_frozen_cases()
    mapping_path = PRIVATE / "mapping.json"
    if not mapping_path.is_file():
        raise RuntimeError("private row/column mapping must freeze before technical audit")
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    if mapping != _frozen_mapping():
        raise RuntimeError("private board mapping differs from frozen before-image plan")
    old_build = _load_old_build()
    completion = json.loads(cc.COMPLETION_PATH.read_text(encoding="utf-8"))
    if completion.get("status") != "passed":
        raise RuntimeError("pinned Exercise27 technical completion proof is not passed")
    case_rows = {}
    for case_id in cc.CaseId:
        pair = cc.validate_scene_pair(case_id)
        _rr, _spec, camera = cc._spec_and_camera(case_id)
        mesh = _rr.build_return_mesh(_spec, 16, 2)
        _project, frame = cc._panel_projector(mesh, camera, cc.CASE_CONFIG[case_id.value]["card"])
        policy_oracles = {
            policy.value: _full_scene_oracle(cc.scene_triangles(case_id, policy), case_id,
                                             camera, frame, old_build)
            for policy in POLICIES
        }
        if policy_oracles[POLICIES[0].value] != policy_oracles[POLICIES[1].value]:
            raise RuntimeError(f"full-scene actual-depth winners changed by stripe pigment for {case_id.value}")
        pair["full_scene_actual_depth_oracle_by_policy"] = policy_oracles
        pair["full_scene_actual_depth_winners_policy_invariant"] = True
        geometry = _actual_geometry(case_id, old_build, completion)
        if pair["support_sha256"] != geometry["support_sha256"] or pair["camera_sha256"] != geometry["camera_sha256"]:
            raise RuntimeError("policy comparison changed frozen support/camera hash")
        if pair["submitted_inputs"] != geometry["submitted_inputs"]:
            raise RuntimeError("actual support/art/card total differs from the proof")
        case_rows[case_id.value] = {**geometry, "one_variable_art_audit": pair}
    card = _card_oracle(old_build, completion)
    dminus = case_rows["negative-dminus"]["independent_actual_depth_oracle"]
    residual = case_rows["negative-dminus"]["area_by_facing_sign"]["-1"]
    if dminus["winners_by_facing_sign"]["-1"] != 0:
        raise RuntimeError("D-minus hidden side has an actual-depth oracle winner")
    if residual != completion["cases"]["D-minus-symmetric"]["depth_clipped_area_by_facing_sign"]["-1"]:
        raise RuntimeError("D-minus raw kernel residual changed from its pinned proof")
    if residual > 1e-6:
        raise RuntimeError("D-minus hidden-side residual exceeds the recorded kernel tolerance")
    if max(row["submitted_inputs"] for row in case_rows.values()) > 256:
        raise RuntimeError("actual submitted scene exceeded the 256-face kernel cap")
    compiler_sha = digest(Path(cc.__file__))
    builder_sha = digest(Path(__file__))
    proof_sources = {name: digest(SCRATCH / name) for name in SOURCE_FILES}
    renderer_identities = _renderer_identity()
    report = {
        "schema": "local-art-identity-technical-proof/v1", "status": "passed",
        "scope": "finite source/kernel/artifact invariants only; no perception or art acceptance",
        "pinned_inputs": cc.verify_pinned_inputs(),
        "compiler_sha256": compiler_sha, "builder_sha256": builder_sha,
        "source_hashes": proof_sources, "renderer_identities": renderer_identities,
        "cases": case_rows, "card": card,
        "Dminus": {"hidden_side_oracle_winners": 0,
                   "raw_kernel_hidden_area_residual": residual,
                   "residual_within_pinned_kernel_tolerance": True},
        "requirements": {"all_four_cases": True, "both_policies": True,
                         "fixed_16x2_support": True, "actual_inputs_160_or_162": True,
                         "maximum_actual_inputs": 256, "geometry_camera_frame_order_uv_unchanged": True,
                         "depth_fragments_and_areas_policy_invariant": True,
                         "card_winners_preserved": True, "shared_stripe_side_lookup": False,
                         "screen_space_art": False, "per_view_art_rewrite": False,
                         "depth_override": False, "mutable_configuration": False},
        "measured_seconds": round(time.monotonic() - started, 6),
    }
    path = PROVENANCE / "technical-proof.json"
    _json_new(path, report)
    _progress("technical-proof-passed", proof_sha256=digest(path), elapsed_seconds=report["measured_seconds"])
    print(json.dumps({"technical_proof_sha256": digest(path), "seconds": report["measured_seconds"]}, sort_keys=True))
    return report


def _policy_for(case_name: str, policy_name: str) -> cc.ArtPolicy:
    case_id = cc.CaseId(case_name)
    policy = cc.ArtPolicy(policy_name)
    return policy


def compile_all() -> list[dict[str, Any]]:
    proof_path = PROVENANCE / "technical-proof.json"
    if not proof_path.is_file() or json.loads(proof_path.read_text())["status"] != "passed":
        raise RuntimeError("all panel builds depend on a passed technical proof")
    start = time.monotonic()
    artifacts = []
    for case_name in cc.CASE_ORDER:
        for policy in POLICIES:
            case_id = cc.CaseId(case_name)
            output = PANELS / f"{case_name}--{policy.value}.svg"
            artifact = cc.compile_case(case_id, policy, output)
            row = {"case_id": case_name, "policy": policy.value,
                   "svg": str(artifact.svg_path.relative_to(ROOT)),
                   "svg_sha256": artifact.svg_sha256,
                   "png": str(artifact.png_path.relative_to(ROOT)),
                   "png_sha256": artifact.png_sha256,
                   "support_sha256": artifact.support_sha256,
                   "camera_sha256": artifact.camera_sha256,
                   "submitted_inputs": artifact.submitted_inputs,
                   "pixel_margins": artifact.pixel_margins}
            artifacts.append(row)
            _progress("panel-saved", **row)
            print(json.dumps(row, sort_keys=True), flush=True)
    raster_audit = {"schema": "local-art-identity-panel-raster-audit/v1",
                    "panels": [{"case_id": item["case_id"], "policy": item["policy"],
                                "path": item["png"], "sha256": item["png_sha256"],
                                "dimensions": [420, 320], "pixel_margins": item["pixel_margins"],
                                "nonblank": True} for item in artifacts]}
    if len(raster_audit["panels"]) != 8 or any(min(item["pixel_margins"]) < 4
                                                for item in raster_audit["panels"]):
        raise RuntimeError("full eight-panel namespace/frame/margin audit failed")
    _json_new(PROVENANCE / "panel-raster-audit.json", raster_audit)
    _progress("compile-complete", panels=len(artifacts), raster_audit_sha256=digest(
        PROVENANCE / "panel-raster-audit.json"), elapsed_seconds=round(time.monotonic() - start, 6))
    return artifacts


def _renderer_identity() -> dict[str, Any]:
    import draw
    chrome = Path(draw.CHROME)
    if not chrome.is_file():
        raise RuntimeError("approved chrome-headless-shell renderer is unavailable")
    version = subprocess.run([str(chrome), "--version"], capture_output=True, text=True,
                             timeout=10, check=True).stdout.strip()
    python_path = Path(sys.executable).resolve()
    return {"draw.py_sha256": digest(ROOT / "scripts/draw.py"),
            "draw_wrapper_sha256": digest(ROOT / "scripts/draw"),
            "chrome_headless_shell_path": str(chrome), "chrome_sha256": digest(chrome),
            "chrome_version": version, "python_path": str(python_path),
            "python_sha256": digest(python_path), "python_version": sys.version.split()[0],
            "kernel_sha256": digest(cc.KERNEL_PATH)}


def _panel_paths() -> list[Path]:
    result = []
    for name in cc.CASE_ORDER:
        for policy in POLICIES:
            stem = f"{name}--{policy.value}"
            for suffix in ("svg", "png"):
                path = PANELS / f"{stem}.{suffix}"
                if not path.is_file():
                    raise RuntimeError(f"missing final panel output: {path}")
                result.append(path)
    return result


def _determinism_worker(output_json: Path) -> None:
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import draw
    CACHE.mkdir(parents=True, exist_ok=True)
    generated = {}
    with tempfile.TemporaryDirectory(prefix="determinism-", dir=CACHE) as temporary:
        temp_root = Path(temporary)
        for case_name in cc.CASE_ORDER:
            for policy in POLICIES:
                stem = f"{case_name}--{policy.value}"
                svg_text, _scene = cc.svg_for_case(cc.CaseId(case_name), policy)
                temp_svg = temp_root / f"{stem}.svg"
                temp_png = temp_root / f"{stem}.png"
                temp_svg.write_text(svg_text, encoding="utf-8")
                draw.render(str(temp_svg), str(temp_png), (420, 320))
                generated[f"panel:{stem}:svg"] = hashlib.sha256(svg_text.encode()).hexdigest()
                generated[f"panel:{stem}:png"] = digest(temp_png)
        board_svg = _board_svg(json.loads((PRIVATE / "mapping.json").read_text()))
        board_svg_path = temp_root / "comparison-unlabelled.svg"
        board_png_path = temp_root / "comparison-unlabelled.png"
        board_svg_path.write_text(board_svg, encoding="utf-8")
        draw.render(str(board_svg_path), str(board_png_path), (900, 1380))
        generated["board:svg"] = hashlib.sha256(board_svg.encode()).hexdigest()
        generated["board:png"] = digest(board_png_path)
        control_svg = vision_control.control_svg()
        vision_control.validate_control_svg(control_svg)
        control_svg_path = temp_root / "control.svg"
        control_png_path = temp_root / "control.png"
        control_svg_path.write_text(control_svg, encoding="utf-8")
        draw.render(str(control_svg_path), str(control_png_path), (480, 320))
        generated["control:svg"] = hashlib.sha256(control_svg.encode()).hexdigest()
        generated["control:png"] = digest(control_png_path)
    _new(output_json, (json.dumps(generated, sort_keys=True, indent=2) + "\n").encode())


def render_determinism() -> dict[str, Any]:
    manifest_path = PROVENANCE / "manifest.json"
    # Panel manifest is written after compile, but board/control follow in separate phases.
    current = {str(path.relative_to(ROOT)): digest(path) for path in _panel_paths()}
    expected_sources = {str(path.relative_to(ROOT)): digest(path) for path in _panel_paths() if path.suffix == ".svg"}
    output_path = CACHE / "determinism-child.json"
    output_path.unlink(missing_ok=True)
    command = [sys.executable, str(Path(__file__).resolve()), "--determinism-worker",
               str(output_path)]
    child_process = subprocess.run(command, cwd=ROOT, check=False, timeout=170,
                                   capture_output=True, text=True)
    if child_process.returncode != 0:
        raise RuntimeError("separate-process deterministic render failed: "
                           + child_process.stderr[-3000:])
    regenerated = json.loads(output_path.read_text(encoding="utf-8"))
    output_path.unlink()
    for path_string, png_path in ((path, path[:-4] + ".png") for path in expected_sources):
        stem = Path(path_string).stem
        if regenerated[f"panel:{stem}:svg"] != current[path_string]:
            raise RuntimeError(f"panel SVG changed across processes: {stem}")
        if regenerated[f"panel:{stem}:png"] != current[png_path]:
            raise RuntimeError(f"panel PNG render is not deterministic across processes: {stem}")
    # Board and control are compared in their owning phase after they have final paths.
    return {"panel_count": 8, "all_panel_svgs_regenerated_in_child": True,
            "all_panel_pngs_rerendered_in_child": True,
            "child_hashes_sha256": cc.sha256_bytes(canonical(regenerated)),
            "board_control_child_hashes": {key: value for key, value in regenerated.items()
                                           if key.startswith("board:") or key.startswith("control:")}}


def render_phase() -> dict[str, Any]:
    result = render_determinism()
    path = PROVENANCE / "panel-determinism.json"
    _json_new(path, result)
    _progress("panel-determinism-passed", proof_sha256=digest(path))
    print(json.dumps(result, sort_keys=True))
    return result


def _board_svg(mapping: dict[str, Any]) -> str:
    placements = mapping.get("placements")
    if not isinstance(placements, list) or len(placements) != 8:
        raise RuntimeError("board mapping must contain exactly eight frozen placements")
    slots = {(item["row"], item["column"]): item for item in placements}
    if len(slots) != 8 or set(slots) != {(r, c) for r in range(4) for c in range(2)}:
        raise RuntimeError("board mapping has missing or duplicate row/column placements")
    images = []
    for row in range(4):
        for column in range(2):
            item = slots[(row, column)]
            case_id = cc.CaseId(item["case_id"])
            policy = cc.ArtPolicy(item["policy"])
            path = PANELS / f"{case_id.value}--{policy.value}.png"
            if not path.is_file():
                raise RuntimeError("board source panel is missing")
            content = base64.b64encode(path.read_bytes()).decode("ascii")
            x, y = 20 + column * 440, 20 + row * 340
            images.append(f'<image x="{x}" y="{y}" width="420" height="320" '
                          f'href="data:image/png;base64,{content}"/>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="900" height="1380" '
            'viewBox="0 0 900 1380"><rect width="100%" height="100%" fill="#edf1ef"/>'
            + "".join(images) + "</svg>")


def _audit_board(board_path: Path, mapping: dict[str, Any]) -> dict[str, Any]:
    import draw
    image = draw.imread(str(board_path))
    if image.shape[:2] != (1380, 900):
        raise RuntimeError("unlabelled board dimensions differ from frozen two-column full frame")
    cells = []
    for item in mapping["placements"]:
        row, column = item["row"], item["column"]
        x, y = 20 + column * 440, 20 + row * 340
        crop = image[y:y + 320, x:x + 420]
        panel = draw.imread(str(PANELS / f"{item['case_id']}--{item['policy']}.png"))
        if crop.shape != panel.shape or not (crop == panel).all():
            raise RuntimeError("board crop does not exactly match its frozen source panel")
        if len(set(map(tuple, crop.reshape(-1, crop.shape[2])))) <= 1:
            raise RuntimeError("board cell is blank")
        cells.append({"row": row, "column": column, "source_panel_sha256": digest(
            PANELS / f"{item['case_id']}--{item['policy']}.png"), "pixel_match": True})
    backgrounds = [image[0, 0], image[-1, 0], image[0, -1], image[-1, -1]]
    if not all((pixel == backgrounds[0]).all() for pixel in backgrounds):
        raise RuntimeError("board outer frame/background is inconsistent")
    gray = backgrounds[0]
    if not (image[:20, :, :] == gray).all() or not (image[-20:, :, :] == gray).all():
        raise RuntimeError("board vertical full-frame margins are not 20px")
    if not (image[:, :20, :] == gray).all() or not (image[:, -20:, :] == gray).all():
        raise RuntimeError("board horizontal full-frame margins are not 20px")
    if any("policy" not in item for item in mapping["placements"]):
        raise RuntimeError("private source mapping incomplete")
    if any(mapping["column_policy_counts"][str(column)][policy.value] != 2
           for column in (0, 1) for policy in POLICIES):
        raise RuntimeError("unlabelled comparison board leaks a fixed policy column")
    return {"width": 900, "height": 1380, "rows": 4, "columns": 2,
            "outer_margin_px": 20, "cell_gap_px": 20, "nonblank_cells": 8,
            "panel_pixels_match_frozen_mapping": True, "balanced_policy_columns": True,
            "labels_or_text": False, "cells": cells}


def board_phase() -> dict[str, Any]:
    mapping = json.loads((PRIVATE / "mapping.json").read_text(encoding="utf-8"))
    mapping_before = digest(PRIVATE / "mapping.json")
    svg = _board_svg(mapping)
    root = ET.fromstring(svg)
    if root.attrib.get("viewBox") != "0 0 900 1380" or len(list(root)) != 9:
        raise RuntimeError("board SVG namespace/frame/panel count is invalid")
    if any(element.tag.rsplit("}", 1)[-1] not in ("rect", "image") for element in root):
        raise RuntimeError("board contains an unexpected label/text or non-panel element")
    out = BOARDS / "comparison-unlabelled.png"
    if out.exists() or out.is_symlink():
        raise FileExistsError("refusing to overwrite the frozen unlabelled board")
    import draw
    CACHE.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="board-", dir=CACHE) as temporary:
        temp_svg, temp_png = Path(temporary) / "board.svg", Path(temporary) / "board.png"
        temp_svg.write_text(svg, encoding="utf-8")
        draw.render(str(temp_svg), str(temp_png), (900, 1380))
        if temp_png.stat().st_size <= 0:
            raise RuntimeError("browser rendered an empty unlabelled board")
        child = json.loads((PROVENANCE / "panel-determinism.json").read_text())
        if child["board_control_child_hashes"]["board:svg"] != hashlib.sha256(svg.encode()).hexdigest():
            raise RuntimeError("anonymous board SVG differs from its separate-process build")
        if child["board_control_child_hashes"]["board:png"] != digest(temp_png):
            raise RuntimeError("anonymous board PNG differs from separate-process rerender")
        _new(out, temp_png.read_bytes())
    if digest(PRIVATE / "mapping.json") != mapping_before:
        raise RuntimeError("private row/column mapping changed after board generation")
    report = _audit_board(out, mapping)
    report.update({"board_sha256": digest(out), "private_mapping_sha256": mapping_before,
                   "board_svg_source_sha256": hashlib.sha256(svg.encode()).hexdigest()})
    audit_path = PROVENANCE / "board-audit.json"
    _json_new(audit_path, report)
    _progress("unlabelled-board-saved", board_sha256=digest(out), audit_sha256=digest(audit_path))
    print(json.dumps({"board_sha256": digest(out), "board_audit_sha256": digest(audit_path)}, sort_keys=True))
    return report


def control_phase() -> dict[str, Any]:
    source_svg = vision_control.control_svg()
    vision_control.validate_control_svg(source_svg)
    control_svg_path = PRIVATE / "precheck-control.svg"
    key_path = PRIVATE / "precheck-answer-key.json"
    image_path = REVIEW / "precheck/control-01.png"
    if any(path.exists() or path.is_symlink() for path in (control_svg_path, key_path, image_path)):
        raise FileExistsError("refusing to overwrite frozen control evidence")
    import draw
    CACHE.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="control-", dir=CACHE) as temporary:
        temp_svg, temp_png = Path(temporary) / "control.svg", Path(temporary) / "control.png"
        temp_svg.write_text(source_svg, encoding="utf-8")
        draw.render(str(temp_svg), str(temp_png), (480, 320))
        child = json.loads((PROVENANCE / "panel-determinism.json").read_text())
        if child["board_control_child_hashes"]["control:svg"] != hashlib.sha256(source_svg.encode()).hexdigest():
            raise RuntimeError("control SVG differs from its separate-process source build")
        if child["board_control_child_hashes"]["control:png"] != digest(temp_png):
            raise RuntimeError("control PNG differs from separate-process rerender")
        _new(control_svg_path, source_svg.encode("utf-8"))
        _new(image_path, temp_png.read_bytes())
    _json_new(key_path, vision_control.control_answer_key())
    image = draw.imread(str(image_path))
    if image.shape[:2] != (320, 480) or len(set(map(tuple, image.reshape(-1, 3)))) < 5:
        raise RuntimeError("control raster dimensions/nonblank audit failed")
    background = image[0, 0]
    foreground = (image != background).any(axis=2)
    ys, xs = foreground.nonzero()
    margins = [int(xs.min()), int(ys.min()), int(image.shape[1] - 1 - xs.max()),
               int(image.shape[0] - 1 - ys.max())]
    audit = {"schema": "local-art-identity-control-integrity/v1", "dimensions": [480, 320],
             "nonblank": True, "no_embedded_text": True,
             "content_pixel_bounds": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
             "pixel_margins": margins, "svg_namespace": "http://www.w3.org/2000/svg",
             "source_sha256": digest(Path(vision_control.__file__)),
             "svg_sha256": digest(control_svg_path), "png_sha256": digest(image_path)}
    _json_new(PRIVATE / "precheck-control-audit.json", audit)
    return {"control_svg_sha256": digest(control_svg_path), "control_png_sha256": digest(image_path),
            "answer_key_sha256": digest(key_path),
            "control_audit_sha256": digest(PRIVATE / "precheck-control-audit.json"),
            "vision_control_source_sha256": digest(Path(vision_control.__file__)),
            "provider_receipt": "not-run; no reviewer dispatch authorized"}


def _validate_payload_output() -> dict[str, str]:
    hashes = payloads.write_payloads()
    review_json = json.loads((REVIEW / "payload.json").read_text(encoding="utf-8"))
    capability_json = json.loads((REVIEW / "precheck-payload.json").read_text(encoding="utf-8"))
    if review_json != payloads.formal_payload() or capability_json != payloads.capability_payload():
        raise RuntimeError("formal or capability payload differs from the exact approved schema")
    if (REVIEW / "report.txt").read_text(encoding="utf-8") != payloads.report_text(review_json):
        raise RuntimeError("formal report is not exactly one unlabelled board path and neutral prompt")
    report = (REVIEW / "report.txt").read_text(encoding="utf-8")
    expected_lines = [review_json["images"][0], "", review_json["prompt"]]
    if report.splitlines() != expected_lines or len(review_json["images"]) != 1:
        raise RuntimeError("formal review packet is not exactly one image path, blank line, and neutral prompt")
    return hashes


def _all_artifacts() -> dict[str, str]:
    paths = _panel_paths()
    paths.extend([PROVENANCE / "prebuild-pins.json", PROVENANCE / "panel-raster-audit.json",
                  BOARDS / "comparison-unlabelled.png",
                  PRIVATE / "precheck-control.svg", PRIVATE / "precheck-control-audit.json",
                  REVIEW / "precheck/control-01.png", PRIVATE / "precheck-answer-key.json",
                  PROVENANCE / "cases.json", PRIVATE / "mapping.json",
                  PROVENANCE / "technical-proof.json", PROVENANCE / "panel-determinism.json",
                  PROVENANCE / "board-audit.json", REVIEW / "precheck-payload.json",
                  REVIEW / "precheck-payload.sha256", REVIEW / "payload.json",
                  REVIEW / "report.txt", REVIEW / "payload.sha256"])
    return {str(path.relative_to(ROOT)): digest(path) for path in paths if path.is_file()}


def manifest_phase(payload_hashes: dict[str, str] | None = None) -> dict[str, Any]:
    cc._verify_frozen_cases()
    identities = _renderer_identity()
    source_hashes = {name: digest(SCRATCH / name) for name in SOURCE_FILES
                     if (SCRATCH / name).is_file()}
    if len(source_hashes) != len(SOURCE_FILES):
        raise RuntimeError("manifest must bind every compiler, builder and test source")
    if payload_hashes is None:
        payload_hashes = {"capability_payload_sha256": payloads.payload_hash(payloads.capability_payload()),
                          "formal_payload_sha256": payloads.payload_hash(payloads.formal_payload())}
    body = {
        "schema": "local-art-identity-provenance/v1",
        "disposition": "technical artifacts built; sight precheck and formal review not dispatched",
        "source_hashes": source_hashes, "pinned_input_hashes": cc.verify_pinned_inputs(),
        "prebuild_pins_sha256": digest(PROVENANCE / "prebuild-pins.json"),
        "renderer_identities": identities,
        "frozen_cases_sha256": digest(PROVENANCE / "cases.json"),
        "private_mapping_sha256": digest(PRIVATE / "mapping.json"),
        "technical_proof_sha256": digest(PROVENANCE / "technical-proof.json"),
        "panel_determinism_sha256": digest(PROVENANCE / "panel-determinism.json"),
        "board_audit_sha256": digest(PROVENANCE / "board-audit.json"),
        "precheck_control": {"source_sha256": digest(Path(vision_control.__file__)),
                             "svg_sha256": digest(PRIVATE / "precheck-control.svg"),
                             "png_sha256": digest(REVIEW / "precheck/control-01.png"),
                             "private_answer_key_sha256": digest(PRIVATE / "precheck-answer-key.json"),
                             "control_audit_sha256": digest(PRIVATE / "precheck-control-audit.json"),
                             "payload_sha256": payload_hashes["capability_payload_sha256"],
                             "provider_receipt": "not-run; no reviewer dispatch authorized"},
        "formal_review": {"payload_schema": "local-art-identity-review/v1",
                          "payload_sha256": payload_hashes["formal_payload_sha256"],
                          "report_sha256": payload_hashes["formal_report_sha256"],
                          "response": "not-dispatched; no response exists"},
        "artifacts": _all_artifacts(),
        "acceptance_state": {"technical_integrity": "built; pending independent technical review",
                             "sight_capability": "not-dispatched; no receipt or score",
                             "formal_perception": "not-dispatched; S1a remains open"},
    }
    path = PROVENANCE / "manifest.json"
    _new(path, (json.dumps(body, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode())
    return body


def payload_phase() -> dict[str, Any]:
    if not (BOARDS / "comparison-unlabelled.png").is_file():
        raise RuntimeError("unlabelled comparison board must exist before payload freeze")
    control = control_phase()
    hashes = _validate_payload_output()
    manifest = manifest_phase(hashes)
    _progress("payloads-pinned-no-dispatch", manifest_sha256=digest(PROVENANCE / "manifest.json"),
              formal_payload_sha256=hashes["formal_payload_sha256"],
              capability_payload_sha256=hashes["capability_payload_sha256"])
    result = {**control, **hashes, "manifest_sha256": digest(PROVENANCE / "manifest.json")}
    print(json.dumps(result, sort_keys=True))
    return result


def selftest() -> dict[str, Any]:
    manifest_path = PROVENANCE / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    final = {name: digest(SCRATCH / name) for name in SOURCE_FILES}
    if manifest["source_hashes"] != final:
        raise RuntimeError("manifest source hash does not bind the final post-export source revision")
    if manifest["artifacts"] != _all_artifacts():
        raise RuntimeError("manifest artifact hashes differ from final evidence files")
    cc.verify_pinned_inputs()
    if json.loads((PROVENANCE / "technical-proof.json").read_text())["compiler_sha256"] != final["work/compile_case.py"]:
        raise RuntimeError("technical proof does not bind the final compiler source")
    if json.loads((PROVENANCE / "technical-proof.json").read_text())["builder_sha256"] != final["work/build.py"]:
        raise RuntimeError("technical proof does not bind the final builder source")
    for payload_path in (REVIEW / "payload.json", REVIEW / "precheck-payload.json"):
        payload = json.loads(payload_path.read_text())
        if set(payload) != {"schema", "images", "prompt"} or len(payload["images"]) != 1:
            raise RuntimeError("review payload contains extra routing or answer fields")
    result = {"status": "passed", "final_source_hashes": final,
              "manifest_sha256": digest(manifest_path), "artifacts_bound": len(manifest["artifacts"]),
              "no_reviewer_dispatch": True, "no_artistic_pass_claim": True}
    _progress("final-source-selftest-passed", manifest_sha256=result["manifest_sha256"])
    print(json.dumps(result, sort_keys=True))
    return result


def run(phase: str) -> None:
    start = time.monotonic()
    print(json.dumps({"phase": phase, "event": "started", "utc": _utc()}), flush=True)
    if phase == "freeze":
        freeze()
    elif phase == "pins":
        prebuild_pins()
    elif phase == "audit":
        audit()
    elif phase == "compile":
        compile_all()
    elif phase == "render":
        render_phase()
    elif phase == "board":
        board_phase()
    elif phase == "payload":
        payload_phase()
    elif phase == "selftest":
        selftest()
    elif phase == "all":
        freeze()
        prebuild_pins()
        audit()
        compile_all()
        render_phase()
        board_phase()
        payload_phase()
        selftest()
    else:
        raise ValueError(f"unknown phase: {phase}")
    elapsed = time.monotonic() - start
    if elapsed > (900 if phase == "all" else 180):
        raise RuntimeError(f"foreground phase exceeded its bounded runtime: {elapsed:.2f}s")
    print(json.dumps({"phase": phase, "event": "complete", "elapsed_seconds": round(elapsed, 6)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("freeze", "pins", "audit", "compile", "render", "board", "payload", "selftest", "all"))
    parser.add_argument("--determinism-worker", type=Path)
    args = parser.parse_args()
    if args.determinism_worker:
        _determinism_worker(args.determinism_worker)
    elif args.phase:
        run(args.phase)
    else:
        parser.error("--phase required")
