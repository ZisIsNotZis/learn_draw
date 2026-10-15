#!/usr/bin/env python3
"""Compile the frozen ex28 local-UV stripe comparison; no authoring knobs are exposed."""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SCRATCH = ROOT / ".scratch/28-local-art-identity"
WORK = SCRATCH / "work"
EVIDENCE = SCRATCH / "evidence"
PANELS = EVIDENCE / "panels"
SPEC_PATH = ROOT / ".scratch/27-return-bend/work/specs.json"
CASE_SOURCE = ROOT / ".scratch/27-return-bend/work/cases.json"
KERNEL_PATH = ROOT / "scripts/vector_visibility.py"
RETURN_SOURCE = ROOT / "scripts/ribbon_return.py"
OLD_BUILD_PATH = ROOT / ".scratch/27-return-bend/work/build.py"
COMPLETION_PATH = ROOT / ".scratch/27-return-bend/evidence/proof/geometry-gate-completion.json"
CONTROL_CASE_PATH = ROOT / ".scratch/19-ribbon-family/work/cases.json"
REPLAY_CASE_PATH = ROOT / ".scratch/24-clean-support-replay/work/cases-current.json"

PINNED_INPUTS = {
    "scripts/ribbon_return.py": "618d701c3a26eb1f97d6b6cfd210ffe41eba3fe25032eb216d3c2ead398d2607",
    "scripts/vector_visibility.py": "fa4c31acf8ffc622352d1feb192e4adddc7931be9cdfc046fda70b1f4d23d3fa",
    ".scratch/27-return-bend/work/specs.json": "c5f874f3bc4d15a30eeffdff1676d1bf7b26a8144f46b034bfe69f120fd60603",
    ".scratch/27-return-bend/work/cases.json": "95fa2bad3da49f092879d7cbfdd5871f7d7c6ff7a389ee1b55611b31f900cbbc",
    ".scratch/27-return-bend/work/build.py": "088541e6b481d4b9a086c11daa0ce3a264f4206b40bf0453c14cec36849216c8",
    ".scratch/19-ribbon-family/work/cases.json": "bd2732b806de26cc2d8a261be68e8f30e21e1f8f8bd5301556d85241a8bc5800",
    ".scratch/24-clean-support-replay/work/cases-current.json": "793ca4c206e44d3801cb5a1c82783a5fecbffb9d16e5c1539999445ba20b6034",
    ".scratch/27-return-bend/evidence/proof/geometry-gate-completion.json": "5c1306b6c0fe37dc8aa22892ea013899ad46689eaa83a4b3750c452f59056ab9",
    "scripts/tests/test_ribbon_return.py": "cc933869b3c75a5458493151cc44972cde972c8a0ef90df35e19c93fc6a2cb67",
    "scripts/tests/test_vector_visibility.py": "dfdaf991b63b918f9b0f7ad592e7e6d1d53300c259838e2db31ea65542edeb92",
    "scripts/tests/test_vector_visibility_oracle.py": "91ccb65c7aaf19cc51554982094d7523280f2cc0df78c089a920a6b9c5363f8c",
}
PROTECTED_ARTIFACTS = {
    ".scratch/27-return-bend/evidence/boards/comparison-labelled.png": "542fbe0cae127bc76a0eb049b803b7a8a338a02449514484b7ba157b3c202fb9",
    ".scratch/27-return-bend/evidence/boards/comparison-labelled.svg": "7f372fd1a86e8a810725381234212e4e979eea98677babe43c3491859c6ce16e",
    ".scratch/27-return-bend/evidence/boards/comparison-unlabelled.png": "765bea857a9d816a78fc8257cf1734ba2cd6fa22bbb024dbc2434ef94d0b8f5f",
    ".scratch/27-return-bend/evidence/boards/comparison-unlabelled.svg": "da1f4059f9c75a9c6b8053f52111836e7691079c90e6a9e45aafa91f16c7012e",
    ".scratch/27-return-bend/evidence/boards/diagnostics/comparison-labelled-margin-failure.png": "4e295e27c2c02c8865b2db618655157e9350f1eade982967fb4d0975a5e8ba47",
    ".scratch/27-return-bend/evidence/boards/diagnostics/comparison-labelled-margin-failure.svg": "2996568cc8b0104ebfe03f50ea98ecb510ebd63b6529df05e4558f6ef78cc904",
    ".scratch/27-return-bend/evidence/diagnostics/dminus-resolution-v2.json": "1d27022bfd3999d5ee2fac3ecc188229422232a596f8aa9c124f15376ebe492f",
    ".scratch/27-return-bend/evidence/diagnostics/dminus-resolution.json": "9f88f39c6ebbdd77ef3368bdd0256768c23293ea1db4af2062f19dc5539c14bf",
    ".scratch/27-return-bend/evidence/panels/panel-a191.png": "50955be0671ea11ab3c26741fb07478054a6f2ae2541f910f92675ea8be15d8c",
    ".scratch/27-return-bend/evidence/panels/panel-a191.svg": "77973ae08b953d6b550f640f0bfa3e5b0118023801e0f27921e9fe3b31543839",
    ".scratch/27-return-bend/evidence/panels/panel-b704.png": "6caf318ca5f1f53dfcb75ed0a4b079bc3c57e904cb77ebc399ef81b43bcac201",
    ".scratch/27-return-bend/evidence/panels/panel-b704.svg": "2d405e28a375b7ea9a9bc3dcb04722ee04098fe055007c6c9508c4d67b56c7a3",
    ".scratch/27-return-bend/evidence/panels/panel-c628.png": "8a69c8fdea7ab734a6aff7f06713006f389d22caf2b902238e1ca1341e9034a8",
    ".scratch/27-return-bend/evidence/panels/panel-c628.svg": "ab51192d9d6c2f4b74e4d659674d1f814254c82c5c63be3346b8c0408edb4746",
    ".scratch/27-return-bend/evidence/panels/panel-d315.png": "92c0012752709212281b5ba653caa7fa088e473e9038e12d6548932f06fa1e46",
    ".scratch/27-return-bend/evidence/panels/panel-d315.svg": "ce034e16c836c35249875feaa8ca84525e02f0b0a0443c8bbb3ed488584d66be",
    ".scratch/27-return-bend/evidence/panels/panel-e943.png": "50955be0671ea11ab3c26741fb07478054a6f2ae2541f910f92675ea8be15d8c",
    ".scratch/27-return-bend/evidence/panels/panel-e943.svg": "77973ae08b953d6b550f640f0bfa3e5b0118023801e0f27921e9fe3b31543839",
    ".scratch/27-return-bend/evidence/panels/panel-f837.png": "0c7f8c9978b23fccada5dbaf98866ac449573d70bb15732b299400052da1f67f",
    ".scratch/27-return-bend/evidence/panels/panel-f837.svg": "d6fe60d9359b73fcd4063aebd4f7cd3f3b05f0fb4fa0795e66fbfbd90f36dd9a",
    ".scratch/27-return-bend/evidence/panels/panel-g292.png": "5e32da2c8625055555e1448558d5f0fc14802affd2b5f6fc1a2d5655004c8db7",
    ".scratch/27-return-bend/evidence/panels/panel-g292.svg": "3b73a3707c9a8745ebfddce175b1dad87f193e1dc9677370a55d620ab2154622",
    ".scratch/27-return-bend/evidence/panels/panel-h156.png": "9b95b9bad928845d7b54faa7c6fba8e4695ce1dee28bf6517b474a110e184cc4",
    ".scratch/27-return-bend/evidence/panels/panel-h156.svg": "5f1b2bcf961d773a78bc4702c179b1896dee1674ef961392cf5e6e268b78e61f",
    ".scratch/27-return-bend/evidence/panels/panel-j601.png": "562cfe60684acc6ec2b3e2864cc26956201c63f05207b6aac866a9fdaf89c602",
    ".scratch/27-return-bend/evidence/panels/panel-j601.svg": "6dde0df748f60a335c1b7ad6dce713075249b8494f8e10a6da4644338ad07a07",
    ".scratch/27-return-bend/evidence/panels/panel-k482.png": "5de37fa82beb107f9fcbff4a7465f7264c7cbe164a426fe53456012e9b792c88",
    ".scratch/27-return-bend/evidence/panels/panel-k482.svg": "181080db4946e829becd510bd90183c1da8a1a9a301ad05eebe226cb31eb7b7b",
    ".scratch/27-return-bend/evidence/proof/geometry-gate-board-crop-build.json": "ecf027d2c29c1e0e8119171be775b8d1edef74c16a6804a40ef1f18321c292ad",
    ".scratch/27-return-bend/evidence/proof/geometry-gate-corrected.json": "83ccee28c349623c779329989be955946bfc25ca7c4f8decb6f3164522f13bae",
    ".scratch/27-return-bend/evidence/proof/geometry-gate-render-build.json": "ecf027d2c29c1e0e8119171be775b8d1edef74c16a6804a40ef1f18321c292ad",
    ".scratch/27-return-bend/evidence/proof/geometry-gate.json": "a0e4379fb33fab095d1d6e3d6d2178b9c94d1e41068b758ebce0ede045a0f878",
    ".scratch/27-return-bend/evidence/diagnostics/dminus-resolution-v2.json": "1d27022bfd3999d5ee2fac3ecc188229422232a596f8aa9c124f15376ebe492f",
    ".scratch/27-return-bend/evidence/diagnostics/dminus-resolution.json": "9f88f39c6ebbdd77ef3368bdd0256768c23293ea1db4af2062f19dc5539c14bf",
    "scripts/tests/test_ribbon_return.py": "cc933869b3c75a5458493151cc44972cde972c8a0ef90df35e19c93fc6a2cb67",
    "scripts/tests/test_vector_visibility.py": "dfdaf991b63b918f9b0f7ad592e7e6d1d53300c259838e2db31ea65542edeb92",
    "scripts/tests/test_vector_visibility_oracle.py": "91ccb65c7aaf19cc51554982094d7523280f2cc0df78c089a920a6b9c5363f8c",
    ".scratch/28-local-art-identity/design.md": "565fef4f1e1d816de8fd0f581ed51d071051247620b834eb389ed87e551c8d69",
}
EXTERNAL_PINS = {
    "/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/e8b12fe9-8413-4a76-8959-5c9ff67642ea/s1a/identity-design-final-recheck.md":
        "063cad1ed8e350c0d8a58b4f7bf059efd2be2adf22c1d17ac259c75d4b7f4ad3",
}

CASE_CONFIG = {
    "primary-dplus": {"alpha": math.pi, "camera": "D-plus-10deg", "card": False},
    "variation-2pi3-dplus": {"alpha": 2 * math.pi / 3, "camera": "D-plus-10deg", "card": False},
    "negative-dminus": {"alpha": math.pi, "camera": "D-minus-symmetric", "card": False},
    "card-dplus": {"alpha": math.pi, "camera": "D-plus-10deg", "card": True},
}
CASE_ORDER = tuple(CASE_CONFIG)


class CaseId(str, Enum):
    PRIMARY_DPLUS = "primary-dplus"
    VARIATION_2PI3_DPLUS = "variation-2pi3-dplus"
    NEGATIVE_DMINUS = "negative-dminus"
    CARD_DPLUS = "card-dplus"


class ArtPolicy(str, Enum):
    SIDE_DEPENDENT = "SIDE_DEPENDENT"
    SHARED_FIXED_LOCAL = "SHARED_FIXED_LOCAL"


@dataclass(frozen=True)
class CaseArtifact:
    case_id: CaseId
    policy: ArtPolicy
    svg_path: Path
    png_path: Path
    svg_sha256: str
    png_sha256: str
    support_sha256: str
    camera_sha256: str
    submitted_inputs: int
    pixel_margins: tuple[int, int, int, int]


@dataclass(frozen=True)
class SceneTriangle:
    """A projected kernel input with provenance from support, local UV art, or the card."""

    points: tuple[tuple[float, float, float], ...]
    pigment: str
    provenance: str
    local_uv: tuple[tuple[float, float], ...] | None = None
    source_face_index: int | None = None


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def verify_pinned_inputs() -> dict[str, str]:
    actual: dict[str, str] = {}
    for relative, expected in {**PINNED_INPUTS, **PROTECTED_ARTIFACTS}.items():
        path = ROOT / relative
        if not path.is_file():
            raise RuntimeError(f"missing pinned input: {relative}")
        found = sha256_file(path)
        if found != expected:
            raise RuntimeError(f"pinned input hash mismatch: {relative} ({found})")
        actual[relative] = found
    for path_text, expected in EXTERNAL_PINS.items():
        path = Path(path_text)
        if not path.is_file():
            raise RuntimeError(f"missing pinned authorization source: {path}")
        found = sha256_file(path)
        if found != expected:
            raise RuntimeError(f"authorization source hash mismatch: {path} ({found})")
        actual[f"external:{path}"] = found
    return actual


def cases_document() -> dict[str, Any]:
    return {
        "schema": "local-art-identity-cases/v1",
        "frozen_before_images": True,
        "source_bindings": dict(PINNED_INPUTS),
        "sampling": {"u_intervals": 16, "v_intervals": 2, "support_faces": 64,
                     "maximum_submitted_inputs": 256},
        "fixed_art": {"base_front": "#e68aa4", "base_back": "#7188bd",
                      "side_dependent_front_stripe": "#472639",
                      "side_dependent_back_stripe": "#fff1b8",
                      "shared_stripe": "#472639", "u": [0.0, 1.0],
                      "v": [-0.18, 0.18], "material_width_world": 0.36},
        "cases": [
            {"case_id": case_id, "alpha_radians": CASE_CONFIG[case_id]["alpha"],
             "camera": CASE_CONFIG[case_id]["camera"], "card": CASE_CONFIG[case_id]["card"]}
            for case_id in CASE_ORDER
        ],
    }


def _load_render_dependencies():
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    import ribbon_return
    import vector_visibility
    import draw
    return ribbon_return, vector_visibility, draw


def _verify_frozen_cases() -> dict[str, Any]:
    plan_path = EVIDENCE / "provenance/cases.json"
    if not plan_path.is_file():
        raise RuntimeError("frozen ex28 case plan missing; run build --phase freeze before compilation")
    actual = json.loads(plan_path.read_text(encoding="utf-8"))
    if actual != cases_document():
        raise RuntimeError("frozen ex28 case plan differs from its source-defined contract")
    verify_pinned_inputs()
    return actual


def _case_name(case_id: CaseId) -> str:
    if type(case_id) is not CaseId:
        raise TypeError("case_id must be one of the four pinned CaseId enum members")
    if case_id.value not in CASE_CONFIG:
        raise ValueError("unknown frozen case")
    return case_id.value


def _policy(policy: ArtPolicy) -> ArtPolicy:
    if type(policy) is not ArtPolicy:
        raise TypeError("policy must be SIDE_DEPENDENT or SHARED_FIXED_LOCAL")
    return policy


def _spec_and_camera(case_id: CaseId):
    rr, _visibility, _draw = _load_render_dependencies()
    specs = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    base = specs["return_support"]
    config = CASE_CONFIG[case_id.value]
    spec = rr.ReturnSpec(base["name"], tuple(base["root"]), tuple(base["root_tangent"]),
                         tuple(base["bend_normal"]), base["length"], base["width"],
                         base["tip_ratio"], config["alpha"])
    camera_data = specs["camera_bases"][config["camera"]]
    camera = rr.OrthographicCamera(config["camera"], tuple(camera_data["screen_right"]),
                                   tuple(camera_data["screen_up"]), tuple(camera_data["toward_viewer"]))
    return rr, spec, camera


def _facing_side(face, camera) -> str:
    rr, _visibility, _draw = _load_render_dependencies()
    normal = rr._cross(rr._sub(face.points[1], face.points[0]),
                       rr._sub(face.points[2], face.points[0]))
    return "front" if rr._dot(normal, camera.toward_viewer) > 0.0 else "back"


def _panel_projector(mesh, camera, with_card: bool):
    """Use the pinned full-frame panel transform; marks still originate only in source UV."""
    rr, _visibility, _draw = _load_render_dependencies()
    world = [point for face in mesh.faces for point in face.points]
    if with_card:
        world.extend(point for triangle in rr.card_triangles(mesh.spec) for point in triangle)
    projected = [rr.project_point(point, camera) for point in world]
    low_x, high_x = min(point[0] for point in projected), max(point[0] for point in projected)
    low_y, high_y = min(point[1] for point in projected), max(point[1] for point in projected)
    center_x, center_y = (low_x + high_x) / 2.0, (low_y + high_y) / 2.0
    scale = min(90.0, 380.0 / max(high_x - low_x, 1e-12),
                280.0 / max(high_y - low_y, 1e-12))
    offset_x, offset_y = 210.0 - scale * center_x, 160.0 + scale * center_y

    def project(point):
        x, y, depth = rr.project_point(point, camera)
        return (offset_x + scale * x, offset_y - scale * y, depth)

    projected_center = [offset_x + scale * center_x, offset_y - scale * center_y]
    if any(abs(value - expected) > 1e-10 for value, expected in zip(projected_center, (210.0, 160.0))):
        raise RuntimeError("frozen full-frame projection is not centered")
    return project, {"scale_px_per_world_unit": scale, "center_px": projected_center,
                     "geometry_center": [center_x, center_y],
                     "geometry_bounds": [low_x, low_y, high_x, high_y],
                     "offset_px": [offset_x, offset_y]}


def _local_stripe_triangles(mesh, camera, policy: ArtPolicy, project=None) -> list[SceneTriangle]:
    """Clip existing per-face UV coordinates; shared pigment selection is view-independent."""
    rr, _visibility, _draw = _load_render_dependencies()
    project = project or (lambda point: rr.project_point(point, camera))
    result: list[SceneTriangle] = []
    for face in mesh.faces:
        polygon = [(face.points[index], face.uv[index]) for index in range(3)]
        polygon = rr._clip_uv_v(polygon, -0.18, True)
        polygon = rr._clip_uv_v(polygon, 0.18, False)
        if policy is ArtPolicy.SHARED_FIXED_LOCAL:
            pigment = "#472639"
        else:
            pigment = "#472639" if _facing_side(face, camera) == "front" else "#fff1b8"
        for triangle in rr._fan_uv(polygon):
            projected = tuple(project(vertex[0]) for vertex in triangle)
            local_uv = tuple(vertex[1] for vertex in triangle)
            result.append(SceneTriangle(projected, pigment, "local-uv-stripe", local_uv,
                                        face.source_index))
    return result


def scene_triangles(case_id: CaseId, policy: ArtPolicy) -> tuple[SceneTriangle, ...]:
    """Create exactly the original support-plus-local-art order, changing stripe pigment only."""
    case_name, selected = _case_name(case_id), _policy(policy)
    _verify_frozen_cases()
    rr, spec, camera = _spec_and_camera(CaseId(case_name))
    mesh = rr.build_return_mesh(spec, 16, 2)
    project, _frame = _panel_projector(mesh, camera, CASE_CONFIG[case_name]["card"])
    stripes = _local_stripe_triangles(mesh, camera, selected, project)
    body: list[SceneTriangle] = []
    for face in mesh.faces:
        side = _facing_side(face, camera)
        pigment = "#e68aa4" if side == "front" else "#7188bd"
        points = tuple(project(point) for point in face.points)
        body.append(SceneTriangle(points, pigment, f"support-body:{side}", face.uv,
                                  face.source_index))
    scene = stripes + body
    if CASE_CONFIG[case_name]["card"]:
        for triangle in rr.card_triangles(spec):
            projected = tuple(project(point) for point in triangle)
            scene.append(SceneTriangle(projected, "#526a60", "root-attached-card", None,
                                       len(mesh.faces) + len(scene) - len(stripes) - len(body)))
    expected = 162 if CASE_CONFIG[case_name]["card"] else 160
    if len(scene) != expected or len(scene) > 256:
        raise RuntimeError(f"actual submitted input total violates the frozen 160/162 cap: {len(scene)}")
    return tuple(scene)


def _scene_kernel_entries(scene: tuple[SceneTriangle, ...]):
    return [(triangle.points, triangle.pigment, triangle.provenance) for triangle in scene]


def _hash_structure(value: Any) -> str:
    return sha256_bytes(canonical_json(value))


def _support_and_camera_hash(case_id: CaseId) -> tuple[str, str]:
    rr, spec, camera = _spec_and_camera(case_id)
    mesh = rr.build_return_mesh(spec, 16, 2)
    support = [{"source_index": face.source_index, "u_cell": face.u_cell, "v_cell": face.v_cell,
                "points": face.points, "uv": face.uv} for face in mesh.faces]
    camera_record = {"name": camera.name, "right": camera.right, "up": camera.up,
                     "toward_viewer": camera.toward_viewer}
    return _hash_structure({"spec": spec.__dict__, "faces": support}), _hash_structure(camera_record)


def svg_for_case(case_id: CaseId, policy: ArtPolicy) -> tuple[str, tuple[SceneTriangle, ...]]:
    case_name, selected = _case_name(case_id), _policy(policy)
    scene = scene_triangles(CaseId(case_name), selected)
    _rr, visibility, _draw = _load_render_dependencies()
    visible = visibility.visible_regions(_scene_kernel_entries(scene))
    paths = [f'<!-- {component}: depth-visible local artwork fill; tessellation is not ink -->'
             f'<path id="identity-{index}" d="{path}" fill="{pigment}" fill-rule="nonzero"/>'
             for index, (path, pigment, component) in enumerate(visible)]
    if not paths:
        raise RuntimeError("depth kernel produced a blank ex28 panel")
    markup = (f'<svg xmlns="http://www.w3.org/2000/svg" width="420" height="320" '
              'viewBox="0 0 420 320"><!-- Frozen ex28 full-frame local-art panel. -->'
              '<rect id="panel-background" width="100%" height="100%" fill="#edf1ef"/>'
              '<g id="return-support-and-local-art">' + "".join(paths) + "</g></svg>")
    return markup, scene


def _audit_png(path: Path, expected_size: tuple[int, int]) -> dict[str, Any]:
    _rr, _visibility, draw = _load_render_dependencies()
    image = draw.imread(str(path))
    if (image.shape[1], image.shape[0]) != expected_size:
        raise RuntimeError(f"wrong raster dimensions at {path}")
    if len(set(map(tuple, image.reshape(-1, image.shape[2])))) <= 1:
        raise RuntimeError(f"blank raster at {path}")
    # Geometry-to-frame centering is independently audited by the builder; this checks safe margins.
    background = image[0, 0]
    foreground = (image != background).any(axis=2)
    ys, xs = foreground.nonzero()
    margins = [int(xs.min()), int(ys.min()), int(expected_size[0] - 1 - xs.max()),
               int(expected_size[1] - 1 - ys.max())]
    if min(margins) < 4:
        raise RuntimeError(f"panel art violates the 4px full-frame safety margin: {margins}")
    return {"width": expected_size[0], "height": expected_size[1], "nonblank": True,
            "pixel_margins": margins}


def _expected_path(case_name: str, policy: ArtPolicy) -> Path:
    return PANELS / f"{case_name}--{policy.value}.svg"


def _validate_output(case_id: CaseId, policy: ArtPolicy, output_path: Path) -> tuple[Path, Path]:
    case_name, selected = _case_name(case_id), _policy(policy)
    if not isinstance(output_path, Path):
        raise TypeError("output_path must be a pathlib.Path")
    relative = Path(".scratch/28-local-art-identity/evidence/panels") / f"{case_name}--{selected.value}.svg"
    absolute = ROOT / relative
    if output_path not in (relative, absolute):
        raise ValueError(f"output_path must be exactly {relative.as_posix()}")
    if output_path.is_symlink():
        raise ValueError("symlink output paths are rejected")
    expected_directory = ROOT / relative.parent
    if any(path.is_symlink() for path in (ROOT / ".scratch", SCRATCH, EVIDENCE, PANELS)):
        raise ValueError("symlink directory paths are rejected for final outputs")
    if (not PANELS.is_dir() or PANELS.resolve() != expected_directory.resolve()
            or not PANELS.resolve().is_relative_to(ROOT.resolve())):
        raise ValueError("evidence/panels must exist under the exact isolated project output directory")
    svg_path = absolute
    png_path = absolute.with_suffix(".png")
    if svg_path.exists() or png_path.exists() or svg_path.is_symlink() or png_path.is_symlink():
        raise FileExistsError("refusing to overwrite an existing final panel or paired raster")
    return svg_path, png_path


def compile_case(case_id: CaseId, policy: ArtPolicy, output_path: Path) -> CaseArtifact:
    """Compile one pinned case/policy directly to its evidence SVG/PNG pair."""
    name, selected = _case_name(case_id), _policy(policy)
    svg_path, png_path = _validate_output(case_id, selected, output_path)
    _verify_frozen_cases()
    proof_path = EVIDENCE / "provenance/technical-proof.json"
    if not proof_path.is_file():
        raise RuntimeError("technical proof must pass before panel compilation")
    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    if (proof.get("status") != "passed"
            or proof.get("compiler_sha256") != sha256_file(Path(__file__))
            or proof.get("builder_sha256") != sha256_file(WORK / "build.py")):
        raise RuntimeError("technical proof is stale or not passed for this compiler/builder revision")
    svg, scene = svg_for_case(case_id, selected)
    if len(scene) != (162 if CASE_CONFIG[name]["card"] else 160):
        raise RuntimeError("scene count changed after the pre-image technical proof")
    _rr, _visibility, draw = _load_render_dependencies()
    cache = WORK / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="panel-", dir=cache) as temporary:
        temp_svg = Path(temporary) / "panel.svg"
        temp_png = Path(temporary) / "panel.png"
        temp_svg.write_text(svg, encoding="utf-8")
        draw.render(str(temp_svg), str(temp_png), (420, 320))
        raster_audit = _audit_png(temp_png, (420, 320))
        if not temp_png.is_file():
            raise RuntimeError("browser renderer did not create the panel raster")
        svg_bytes, png_bytes = svg.encode("utf-8"), temp_png.read_bytes()
    # Exclusive creation prevents accidental relabeling or cache promotion over prior evidence.
    with svg_path.open("xb") as output:
        output.write(svg_bytes)
    try:
        with png_path.open("xb") as output:
            output.write(png_bytes)
    except BaseException:
        svg_path.unlink(missing_ok=True)
        raise
    support_sha, camera_sha = _support_and_camera_hash(case_id)
    return CaseArtifact(case_id, selected, svg_path, png_path, sha256_bytes(svg_bytes),
                        sha256_bytes(png_bytes), support_sha, camera_sha, len(scene),
                        tuple(raster_audit["pixel_margins"]))


def input_geometry_record(scene: tuple[SceneTriangle, ...]) -> list[dict[str, Any]]:
    return [{"points": triangle.points, "provenance": triangle.provenance,
             "local_uv": triangle.local_uv, "source_face_index": triangle.source_face_index}
            for triangle in scene]


def validate_scene_pair(case_id: CaseId) -> dict[str, Any]:
    side = scene_triangles(case_id, ArtPolicy.SIDE_DEPENDENT)
    shared = scene_triangles(case_id, ArtPolicy.SHARED_FIXED_LOCAL)
    side_geometry = input_geometry_record(side)
    shared_geometry = input_geometry_record(shared)
    if side_geometry != shared_geometry:
        raise RuntimeError(f"one-variable geometry invariant failed for {case_id.value}")
    stripe_indices = [i for i, triangle in enumerate(side) if triangle.provenance == "local-uv-stripe"]
    body_indices = [i for i, triangle in enumerate(side) if triangle.provenance.startswith("support-body:")]
    card_indices = [i for i, triangle in enumerate(side) if triangle.provenance == "root-attached-card"]
    if len(stripe_indices) != 96 or len(body_indices) != 64:
        raise RuntimeError(f"local mask/input triangles differ from frozen design for {case_id.value}")
    if len(card_indices) != (2 if CASE_CONFIG[case_id.value]["card"] else 0):
        raise RuntimeError("opaque card source-face count changed")
    changed = [i for i, (a, b) in enumerate(zip(side, shared)) if a.pigment != b.pigment]
    if changed != [i for i in stripe_indices if side[i].pigment != "#472639"]:
        # Side-dependent back stripes change; front stripes already reuse the fixed pigment.
        raise RuntimeError("a pigment outside the predeclared local stripe assignment changed")
    if any(shared[index].pigment != "#472639" for index in stripe_indices):
        raise RuntimeError("shared policy does not use the fixed local stripe pigment")
    stripe_uv = [uv for index in stripe_indices for uv in (shared[index].local_uv or ())]
    if (not stripe_uv or min(point[0] for point in stripe_uv) != 0.0
            or max(point[0] for point in stripe_uv) != 1.0
            or min(point[1] for point in stripe_uv) != -0.18
            or max(point[1] for point in stripe_uv) != 0.18):
        raise RuntimeError("stripe provenance is not the complete fixed local UV mask")
    for scene in (side, shared):
        entries = _scene_kernel_entries(scene)
        if len(entries) > 256:
            raise RuntimeError("actual submitted kernel input count exceeds 256")
    # Kernel polygons and projected depth fragments are equal after pigment is excluded.
    _rr, visibility, _draw = _load_render_dependencies()
    fragments = []
    for scene in (side, shared):
        rows = []
        for polygon, _pigment, component in visibility.visible_fragments(_scene_kernel_entries(scene)):
            rows.append({"polygon": [[float(f"{coord:.12g}") for coord in point]
                                      for point in polygon], "provenance": component})
        fragments.append(rows)
    if fragments[0] != fragments[1]:
        raise RuntimeError(f"depth fragment geometry changed with pigment for {case_id.value}")
    rr, spec, camera = _spec_and_camera(case_id)
    mesh = rr.build_return_mesh(spec, 16, 2)
    _project, frame = _panel_projector(mesh, camera, CASE_CONFIG[case_id.value]["card"])
    return {"case_id": case_id.value, "submitted_inputs": len(side),
            "frame_center_px": frame["center_px"], "frame_scale_px_per_world_unit": frame["scale_px_per_world_unit"],
            "support_triangles": 64, "local_uv_stripe_triangles": len(stripe_indices),
            "card_triangles": len(card_indices), "changed_pigment_indices": changed,
            "input_geometry_identical": True, "source_order_uv_camera_depth_identical": True,
            "visible_depth_fragments_identical_excluding_pigment": True,
            "fragment_sha256": _hash_structure(fragments[0]),
            "support_sha256": _support_and_camera_hash(case_id)[0],
            "camera_sha256": _support_and_camera_hash(case_id)[1]}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--svg-sha", choices=CASE_ORDER)
    parser.add_argument("--policy", choices=[p.value for p in ArtPolicy])
    args = parser.parse_args()
    if not args.svg_sha or not args.policy:
        parser.error("--svg-sha and --policy are required")
    text, _scene = svg_for_case(CaseId(args.svg_sha), ArtPolicy(args.policy))
    print(sha256_bytes(text.encode("utf-8")))
