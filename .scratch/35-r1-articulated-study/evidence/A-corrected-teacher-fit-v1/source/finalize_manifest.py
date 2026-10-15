#!/usr/bin/env python3
"""Hash the exclusive fit artifact tree without accessing any teacher/target input."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.json"
SIDECAR = ROOT / "manifest.sha256"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    files = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path in (MANIFEST, SIDECAR):
            continue
        if "__pycache__" in path.parts:
            raise SystemExit(f"unexpected cache in evidence tree: {path.relative_to(ROOT)}")
        data = path.read_bytes()
        files.append({"path": path.relative_to(ROOT).as_posix(),
                      "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)})
    artifact = {
        "artifact": "A-only corrected-teacher clothing study candidate; writer-complete, not art/R1 accepted",
        "ticket": ".scratch/35-r1-articulated-study/issues/45-a-corrected-teacher-fit-v1.md",
        "teacher_source": {
            "package": ".scratch/35-r1-articulated-study/evidence/A-teacher-reconstruction-v2/teacher-only-corrected-v2/",
            "source_image_sha256": "322ad77c0cfd28fa040c625c55c592a54b3052ac4bea61fc31d967d8acff81fb",
            "registered_crop_sha256": "52e01f5e75e5d98fcd9a0a4ac63be91ed09b8a18ca0f62e7e0348a021b2dd87d",
            "crop_source_xyxy_exclusive": [500, 320, 900, 800],
            "frozen_teacher_file_sha256": {
                "provenance.json": "18e086f8e21ab040cfe63653a9fee7f2646cb8d87ce32385e522358bcff085c8",
                "fit-correction.md": "8ad0e882362b00a7c0678138f9d332ab5cdd0f6bf1ce3007c2de1a1a61975b7f",
                "family-fitting-interface.md": "133668c8e1688e075c0bc8969feb7ea9f191bfac5faa5935e10d380f546a24d6",
                "topology-map.md": "026fd6bf97b6154e8fad69267c4aa6f28d501bea667787e2bd6418029eef2662",
                "landmarks.csv": "5cb2dc0efccdde89333321bb8987f0ec92dfb02df9cd5d048c72e896b0905d80",
                "manual-traces.json": "4e4e21b3def2fece29fbe2925dbf6732a8b1566d4ec0a7eab9ac86f31f9b9e41",
                "pristine-fullcrop.png": "52e01f5e75e5d98fcd9a0a4ac63be91ed09b8a18ca0f62e7e0348a021b2dd87d"
            },
            "current_semantic_review": "/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/25d155f0-05d4-41ea-8e72-d0c1929292cd/r1/teacher-v2-independent-semantic-review.md",
            "teacher_output_guard_review": "/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/3b2bad58-e1ed-44cd-bd21-f1aba0b6b4ce/r1/teacher-output-guard-review.md",
            "fit_observation_boundary": "teacher-measurements/observation-boundary.json",
            "one_time_sparse_trace_measurements": "teacher-measurements/station-measurements.json"
        },
        "scope": "registered 400x480 shoulder/upper-torso clothing only; neck skin context, separate unequal collars, tilted bodice, continuous puff sleeve/tube to dark cuff, gathered unequal loops and bounded tail/neighbor context",
        "evidence_classes": ["source_observation", "artist_parameterization", "generated_structural_hypothesis"],
        "runtime_input_isolation": {
            "builder_arguments": ["--out SVG_PATH"],
            "parameter_input": "source/semantic-parameters.json only",
            "not_opened_by_builder": ["image.jpg", "crop/patch/region pixels", "manual traces", "landmark files", "teacher manifest", "B candidate", "sealed heldout"],
            "reference_is_used_only_by": "scripts/draw check external comparison after source/output freeze"
        },
        "renderer": {
            "backend": "existing SupportFrame/Camera/component_faces/visible_regions/visible_segment_spans/compound path APIs plus smooth_spatial closed-contour guard",
            "component_count": 12,
            "generated_outline_vertices": 944,
            "projected_faces": 920,
            "author_anchor_limit": "maximum 4 coordinates per semantic component/mark; tests verify",
            "manual_visibility_cuts": False,
            "backend_or_physics_modified": False
        },
        "actual_outputs": {
            "svg": "artwork-a.svg",
            "png": "artwork-a.png",
            "draw_check": "check-a/",
            "exact_reviewer_image_list": "check-a/report.txt",
            "reference_absent_repeat": ["reproduction/rebuilt.svg", "reproduction/rebuilt.png"]
        },
        "checks": {
            "focused_test_command": "timeout 115s python3 -B -m pytest -p no:cacheprovider -q .scratch/35-r1-articulated-study/evidence/A-corrected-teacher-fit-v1/tests/test_a_garment_family.py",
            "focused_tests": "6 passed, 12 subtests passed",
            "reference_absent_repeat_svg_and_png": "byte-identical to artwork-a.svg/artwork-a.png",
            "draw_check_metric_role": "alarm only; never used as a parameter target",
            "draw_check_image_review": "not yet performed; writer did not open/judge any generated image"
        },
        "gates": {
            "teacher_semantics": "independent limited-scope PASS supplied before this fit",
            "teacher_output_chain": "independent final-chain PASS supplied before this fit",
            "fit_writer_emission": "complete candidate artifacts emitted and deterministic reproduction checked",
            "A_visual_art_review": "OPEN; Main owns fresh image-only review",
            "construction_attachment_depth_review": "OPEN for independent R1 acceptance",
            "heldout_compatibility_drawing": "OPEN, separate owner; sealed heldout not read",
            "B_and_R1_integration": "OPEN; B not read/copied/rerendered",
            "user_acceptance": "OPEN; no art or R1 PASS"
        },
        "files_excluding_manifest_and_sidecar": files
    }
    MANIFEST.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    SIDECAR.write_text(f"{sha256(MANIFEST)}  manifest.json\n", encoding="ascii")
    print(f"manifest={MANIFEST.relative_to(ROOT)} files={len(files)} sha256={sha256(MANIFEST)}")


if __name__ == "__main__":
    main()
