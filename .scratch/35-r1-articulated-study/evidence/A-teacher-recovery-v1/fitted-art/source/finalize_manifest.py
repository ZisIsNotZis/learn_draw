"""Hash and freeze the isolated A garment-family candidate; preserve B by reference only."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from PIL import Image, ImageChops

FIT = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[6]
TEACHER = REPO / ".scratch/35-r1-articulated-study/evidence/A-teacher-recovery-v1/teacher-only"
PREVIOUS = REPO / ".scratch/35-r1-articulated-study/evidence/goal-recovery-r1-v2-completion"
OUT = FIT / "manifest.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hash_map(base: Path, entries: dict[str, str]) -> dict[str, str]:
    result = {}
    for name, expected in entries.items():
        actual = digest(base / name)
        if actual != expected:
            raise ValueError(f"preserved input changed: {name}")
        result[name] = actual
    return result


def main() -> None:
    params = json.loads((FIT / "source/semantic-parameters.json").read_text(encoding="utf-8"))
    sys.path.insert(0, str(REPO))
    builder_spec = importlib.util.spec_from_file_location("finalize_a_builder", FIT / "source/build_a.py")
    if builder_spec is None or builder_spec.loader is None:
        raise RuntimeError("cannot load the reference-absent A builder")
    builder = importlib.util.module_from_spec(builder_spec)
    sys.modules[builder_spec.name] = builder
    builder_spec.loader.exec_module(builder)
    parts, outlines, _camera = builder.make_components(params)
    teacher_provenance = json.loads((TEACHER / "provenance.json").read_text(encoding="utf-8"))
    prior = json.loads((PREVIOUS / "manifest.json").read_text(encoding="utf-8"))
    with Image.open(REPO / "image.jpg") as reference, Image.open(TEACHER / "source-crop-registered.png") as crop:
        assert reference.size == (1024, 1024) and crop.size == (400, 480)
        assert ImageChops.difference(reference.crop((500, 320, 900, 800)).convert("RGB"), crop.convert("RGB")).getbbox() is None
    assert digest(REPO / "image.jpg") == teacher_provenance["source_sha256"]
    assert digest(TEACHER / "source-crop-registered.png") == teacher_provenance["crop_sha256"] == params["teacher"]["crop_sha256"]

    source_names = (
        "source/build_a.py", "source/semantic-parameters.json", "source/teacher-fit-bridge.md",
        "source/finalize_manifest.py", "tests/test_garment_family.py",
    )
    output_names = (
        "artwork-a.svg", "artwork-a.png", "report.txt", "candidate-status.md",
        "repro-first-build.sha256", "repro-second-build.sha256",
    )
    review_names = tuple(f"check-a/{name}" for name in (
        "side-by-side.png", "draft-fullres.png", "draft.png", "region-1.png", "region-2.png", "region-3.png", "report.txt",
    ))
    source_hashes = {name: digest(FIT / name) for name in source_names}
    source_set = "\n".join(f"{name} {source_hashes[name]}" for name in sorted(source_hashes)) + "\n"
    source_set_hash = hashlib.sha256(source_set.encode("utf-8")).hexdigest()
    report_lines = (FIT / "report.txt").read_text(encoding="utf-8").splitlines()
    listed_images = [line for line in report_lines if line.startswith(".scratch/")]
    if not listed_images or any(not (REPO / image_path).is_file() for image_path in listed_images):
        raise ValueError("image-only review report contains missing image paths")
    output_hashes = {name: digest(FIT / name) for name in output_names}
    review_hashes = {name: digest(FIT / name) for name in review_names}
    teacher_hashes = {name: digest(TEACHER / name) for name in (
        "source-crop-registered.png", "teacher-topology-overlay.png", "landmarks.csv", "topology-map.md", "provenance.json", "make_teacher_overlay.py",
    )}
    prior_hashes = {
        "manifest_sha256": digest(PREVIOUS / "manifest.json"),
        "source_set_sha256": prior["source_set_sha256"],
        "source_sha256": hash_map(PREVIOUS, prior["source_sha256"]),
        "rendered_sha256": hash_map(PREVIOUS, prior["rendered_sha256"]),
        "teacher_evidence_sha256": hash_map(PREVIOUS, prior["teacher_evidence_sha256"]),
        "review_bundle_sha256": hash_map(PREVIOUS, prior["review_bundle_sha256"]),
        "status": "The frozen B v2-completion candidate remains candidate evidence; no B artwork/formal gate PASS is implied.",
        "handling": "Hashes are references only; no B artifact was copied, rebuilt, visually opened, or edited. File bytes were read only to verify their declared hashes.",
    }
    with Image.open(FIT / "artwork-a.png") as image, Image.open(FIT / "check-a/draft-fullres.png") as checked:
        assert image.size == checked.size == (400, 480)
        assert ImageChops.difference(image.convert("RGBA"), checked.convert("RGBA")).getbbox() is None
    first = (FIT / "repro-first-build.sha256").read_bytes()
    second = (FIT / "repro-second-build.sha256").read_bytes()
    if first != second:
        raise ValueError("reference-absent repeated SVG/PNG build hashes differ")
    result = {
        "artifact": "A-only semantic garment-family fitted candidate",
        "status": "emitted candidate; fresh visual/art review and all R1/user gates remain open",
        "task_ticket": ".scratch/35-r1-articulated-study/issues/38-a-garment-family-fit.md",
        "source_set_sha256": source_set_hash,
        "source_sha256": source_hashes,
        "rendered_sha256": output_hashes,
        "review_bundle_sha256": review_hashes,
        "teacher_input_reference_sha256": teacher_hashes,
        "frozen_prior_candidate_reference": prior_hashes,
        "teacher_semantic_gate": {
            "verdict": "PASS for teacher-only visible part/topology observations only",
            "review": "/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/2a74e8cc-0211-4631-b097-057ed526f1d4/r1/a-teacher-semantics-review.md",
            "not_acceptance": ["fitted shape", "art/readability", "transfer", "R1", "user approval"],
        },
        "reference_boundary": {
            "geometry_runtime_inputs": ["source/semantic-parameters.json"],
            "runtime_reference_or_teacher_file_access": False,
            "teacher_crop_use": "draw-check comparison only, outside authored geometry/build/render input",
            "registered_crop_sha256": teacher_provenance["crop_sha256"],
            "source_sha256": teacher_provenance["source_sha256"],
            "registration_rechecked": True,
        },
        "construction": {
            "semantic_parts": len(parts),
            "generated_part_names": [part.name for part in parts],
            "generated_outline_vertices": sum(len(outline) for outline in outlines.values()),
            "shape_anchor_limit": 4,
            "backend": "SupportFrame.local_to_world -> camera projection -> component_faces / visible_regions and visible_segment_spans; scripts/draw render",
            "support_mapping": "real orthographic world support planes with finite depth offsets and gradients; not painter metadata",
            "manual_visibility_cuts": False,
        },
        "reproducibility": {
            "command": "python3 -B source/build_a.py --out artwork-a.svg; scripts/draw render artwork-a.svg -o artwork-a.png",
            "reference_absent": True,
            "repeat_svg_sha256_png_sha256_byte_identical": True,
            "image_pixels_match_draw_check_draft_fullres": True,
        },
        "commands_and_results": [
            {"command": "python3 -B -m pytest -p no:cacheprovider -q <fitted-art>/tests/test_garment_family.py", "result": "passed", "summary": "8 passed in 1.24s; world-space shared contact lines checked"},
            {"command": "python3 -m py_compile <fitted-art>/source/build_a.py <fitted-art>/tests/test_garment_family.py", "result": "passed"},
            {"command": "python3 -B <fitted-art>/source/build_a.py --out <fitted-art>/artwork-a.svg && scripts/draw render <fitted-art>/artwork-a.svg -o <fitted-art>/artwork-a.png", "result": "passed", "summary": "13 parts; 375 generated vertices; SVG plus 400x480 PNG"},
            {"command": "scripts/draw check <fitted-art>/artwork-a.svg --ref <teacher-only>/source-crop-registered.png --outdir <fitted-art>/check-a", "result": "passed", "summary": "A comparison bundle and image list; metrics are alarm-only and not a fit target"},
            {"command": "python3 -B reference/crop, A draw-check pixel, and previous v2 manifest hash verification", "result": "passed", "summary": "source/crop registration exact; A/check pixel identity; 33 previous manifest entries verified"},
            {"command": "reference-absent second generator/render plus sha256sum diff", "result": "passed", "summary": "SVG and PNG hash files byte-identical across builds"},
        ],
        "review_image_list": "report.txt",
        "review_image_paths_exist": True,
        "independent_art_review": "NOT RUN by this worker; Main owns fresh image-only review routing",
        "open_gates": [
            "A fitted-shape correspondence and visual/art/readability review",
            "Main/user acceptance; this candidate is not presented or accepted",
            "full R1 construction/attachment/nonintersection/depth gates beyond these local tests",
            "sealed heldout compatibility/release and later reference-free drawing",
            "integrated reproduction/independent reviews and user feedback",
        ],
        "no_stage_or_commit": True,
        "preexisting_index_note": "The repository already had staged .gitmodules and two vendor gitlinks at task start; preserved without adding or removing any index entries.",
    }
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT}; source_set_sha256={source_set_hash}; previous source/SVG/PNG and evidence hashes verified")


if __name__ == "__main__":
    main()
