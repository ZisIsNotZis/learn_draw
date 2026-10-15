#!/usr/bin/env python3
"""Build one fixed-weight S1a apparent-contour/control comparison from Exercise24 evidence."""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / ".scratch/25-apparent-contour/work"
EVIDENCE = ROOT / ".scratch/25-apparent-contour/evidence"
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(WORK))

import apparent_contour as contour
from draw import render
from PIL import Image

BOARD_WIDTH = 1000
ROW_HEIGHT = 360
ROW_TOP = 20
PANEL_X = (20, 500)
PANEL_Y_OFFSET = 36
PANEL_WIDTH = 480
PANEL_HEIGHT = 320
BACKGROUND = (244, 245, 239)


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_progress(path: Path, event: str, **values) -> None:
    record = {"event": event, "elapsed_seconds": round(time.monotonic() - STARTED, 3), **values}
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")
        stream.flush()


def _extract_svg_body(svg: str):
    match = re.fullmatch(r'<svg xmlns="http://www.w3.org/2000/svg" viewBox="([^"]+)">(.*)</svg>',
                         svg, flags=re.DOTALL)
    if not match:
        raise ValueError("cached control panel has an unexpected SVG namespace/viewBox")
    return match.group(1), match.group(2)


def _namespace_ids(body: str, prefix: str) -> str:
    return re.sub(r'\bid="([^"]+)"', lambda match: f'id="{prefix}-{match.group(1)}"', body)


def _embed_panel(svg: str, x: int, y: int, prefix: str) -> str:
    view_box, body = _extract_svg_body(svg)
    body = _namespace_ids(body, prefix)
    return (f'<svg x="{x}" y="{y}" width="{PANEL_WIDTH}" height="{PANEL_HEIGHT}" '
            f'viewBox="{view_box}" preserveAspectRatio="xMidYMid meet">{body}</svg>')


def _label(text: str, x: int, y: int, anchor: str = "start") -> str:
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" '
            f'font-family="sans-serif" font-size="13" fill="#253746">{escape(text)}</text>')


def comparison_board(rows, labelled: bool) -> str:
    chunks = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {BOARD_WIDTH} '
              f'{ROW_TOP + ROW_HEIGHT * len(rows)}">'
              f'<rect id="board-ground" width="{BOARD_WIDTH}" '
              f'height="{ROW_TOP + ROW_HEIGHT * len(rows)}" fill="#f4f5ef"/>']
    for index, row in enumerate(rows):
        top = ROW_TOP + index * ROW_HEIGHT
        panel_y = top + PANEL_Y_OFFSET
        if labelled:
            chunks.append(_label(row["name"], PANEL_X[0], top + 20))
            chunks.append(_label("Control", PANEL_X[0] + PANEL_WIDTH / 2, top + 20, "middle"))
            chunks.append(_label("Apparent contour", PANEL_X[1] + PANEL_WIDTH / 2, top + 20, "middle"))
        chunks.append(_embed_panel(row["control_svg"], PANEL_X[0], panel_y,
                                   f"r{index}-control"))
        chunks.append(_embed_panel(row["candidate_svg"], PANEL_X[1], panel_y,
                                   f"r{index}-candidate"))
    chunks.append("</svg>")
    return "".join(chunks)


def validate_board(svg_path: Path) -> None:
    root = ET.parse(svg_path).getroot()
    ids = [element.attrib["id"] for element in root.iter() if "id" in element.attrib]
    if len(ids) != len(set(ids)):
        raise ValueError(f"comparison SVG contains duplicate ids: {svg_path}")
    nested = [element for element in root.iter()
              if element.tag.endswith("svg") and element is not root]
    if len(nested) != 10 or any(element.attrib.get("viewBox") != "0 0 480 320" for element in nested):
        raise ValueError("board must contain ten correctly namespaced frozen-size panels")
    if root.attrib.get("viewBox") != f"0 0 {BOARD_WIDTH} {ROW_TOP + ROW_HEIGHT * 5}":
        raise ValueError("comparison viewport is not the frozen five-row layout")


def validate_png(path: Path) -> None:
    image = Image.open(path).convert("RGB")
    expected_size = (BOARD_WIDTH, ROW_TOP + ROW_HEIGHT * 5)
    if image.size != expected_size:
        raise ValueError(f"incorrect rendered viewport {image.size}, expected {expected_size}")
    pixels = image.load()
    for row in range(5):
        for column, x in enumerate(PANEL_X):
            x0, y0 = x, ROW_TOP + row * ROW_HEIGHT + PANEL_Y_OFFSET
            visible = []
            for py in range(y0, y0 + PANEL_HEIGHT):
                for px in range(x0, x0 + PANEL_WIDTH):
                    if pixels[px, py] != BACKGROUND:
                        visible.append((px - x0, py - y0))
            if len(visible) < 500:
                raise ValueError(f"panel row {row} column {column} is blank or clipped")
            bounds = (min(point[0] for point in visible), min(point[1] for point in visible),
                      max(point[0] for point in visible), max(point[1] for point in visible))
            if (bounds[0] < 1 or bounds[1] < 1 or bounds[2] >= PANEL_WIDTH - 1
                    or bounds[3] >= PANEL_HEIGHT - 1):
                raise ValueError(f"panel artwork escapes its actual viewport: row {row}: {bounds}")
            center_x = (bounds[0] + bounds[2]) / 2
            center_y = (bounds[1] + bounds[3]) / 2
            if abs(center_x - PANEL_WIDTH / 2) > PANEL_WIDTH * 0.2:
                raise ValueError(f"panel artwork is not horizontally centered: row {row}: {bounds}")


def panel_crop_variance(labelled_path: Path, unlabelled_path: Path) -> list[dict]:
    """Measure and preserve any raster differences caused solely by board labels."""
    import numpy as np
    labelled = np.asarray(Image.open(labelled_path).convert("RGB"))
    unlabelled = np.asarray(Image.open(unlabelled_path).convert("RGB"))
    if labelled.shape != unlabelled.shape:
        raise ValueError("labelled and unlabelled viewports differ")
    changes = []
    for row in range(5):
        top = ROW_TOP + row * ROW_HEIGHT + PANEL_Y_OFFSET
        for column, x in enumerate(PANEL_X):
            crop_a = labelled[top:top + PANEL_HEIGHT, x:x + PANEL_WIDTH]
            crop_b = unlabelled[top:top + PANEL_HEIGHT, x:x + PANEL_WIDTH]
            changed = np.any(crop_a != crop_b, axis=2)
            if changed.any():
                ys, xs = np.where(changed)
                changes.append({"row": row, "column": column,
                                "changed_pixels": int(changed.sum()),
                                "bbox_panel_xy": [int(xs.min()), int(ys.min()),
                                                  int(xs.max()), int(ys.max())]})
    return changes


def _support_hash(mesh) -> str:
    payload = [{"uv": face.uv, "points": face.points, "source_triangle": face.source_triangle}
               for face in mesh.triangles]
    return hashlib.sha256(json.dumps(payload, separators=(",", ":"),
                                      sort_keys=True).encode()).hexdigest()


def main() -> None:
    global STARTED
    STARTED = time.monotonic()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "panels").mkdir(parents=True, exist_ok=True)
    (EVIDENCE / "provenance").mkdir(parents=True, exist_ok=True)
    progress = WORK / "build-progress.jsonl"
    progress.write_text("", encoding="utf-8")
    config, cases = contour.load_cases()
    append_progress(progress, "pins-verified", pins=contour.verify_pins())

    built_rows = []
    proof_rows = []
    primary_visible = {}
    for index, case in enumerate(cases):
        started = time.monotonic()
        flat, curved, fit, candidates, spans, patches = contour.build_case(
            case["spec"], case["camera"])
        source_panel = ROOT / case["control_panel"]
        source_svg = source_panel.read_text(encoding="utf-8")
        view_box, _body = _extract_svg_body(source_svg)
        if view_box != "0 0 480 320":
            raise ValueError(f"cached panel has wrong viewport: {case['name']} {view_box}")
        if f"camber=0.35; u=96; v=12" not in source_svg:
            raise ValueError(f"cached control has mismatched support: {case['name']}")
        if (case["condition"] == "primary-existing-spec"
                and (not candidates or not spans or not patches)):
            outcome = {"status": "hypothesis_unsupported", "case": case["name"],
                       "reason": "no valid depth-visible apparent turn contour remains on the actual support"}
            write_json(EVIDENCE / "outcome.json", outcome)
            append_progress(progress, "hypothesis-unsupported", **outcome)
            raise SystemExit("hypothesis unsupported; no candidate image produced for this row")
        if (case["condition"] == "negative-control-and-root-width-check"
                and (candidates or spans or patches)):
            raise ValueError("untwisted arch negative control unexpectedly acquired an internal contour cue")

        candidate_group = contour.serialize_group(patches, f"case-{index:02d}-{case['name']}")
        candidate_svg = contour.overlay_group(source_svg, candidate_group) if candidate_group else source_svg
        control_path = EVIDENCE / "panels" / f"case-{index:02d}-{case['name']}-control.svg"
        candidate_path = EVIDENCE / "panels" / f"case-{index:02d}-{case['name']}-apparent-contour.svg"
        control_path.write_text(source_svg, encoding="utf-8")
        candidate_path.write_text(candidate_svg, encoding="utf-8")
        fill_without_cue = (contour.remove_group(candidate_svg, candidate_group)
                            if candidate_group else candidate_svg)
        if fill_without_cue != source_svg:
            raise ValueError(f"candidate changed cached fill/support visibility bytes: {case['name']}")

        support_hash = _support_hash(curved)
        panel_proof = {
            "name": case["name"], "condition": case["condition"],
            "spec_sha256": case["source_spec_sha256"], "camera_sha256": case["camera_sha256"],
            "camera": {"name": case["camera"].name, "yaw": case["camera"].yaw,
                       "pitch": case["camera"].pitch},
            "support_geometry_sha256": support_hash,
            "support_triangles": len(curved.triangles),
            "support": {"camber": 0.35, "u_intervals": 96, "v_intervals": 12},
            "cached_control_panel": case["control_panel"],
            "control_panel_sha256": file_sha(source_panel),
            "candidate_panel_sha256": hashlib.sha256(candidate_svg.encode()).hexdigest(),
            "fill_visibility_unchanged": hashlib.sha256(fill_without_cue.encode()).hexdigest()
            == file_sha(source_panel),
            "fill_visibility_sha256": hashlib.sha256(fill_without_cue.encode()).hexdigest(),
            "camera_dependent_candidates": len(candidates),
            "depth_visible_centerline_spans": len(spans), "finite_ink_patches": len(patches),
            "candidate_edges": [contour.jsonable_candidate(item) for item in candidates],
            "visible_spans": [contour.jsonable_span(item) for item in spans],
            "cue_weight_px": contour.INK_WIDTH_PX,
        }
        proof_rows.append(panel_proof)
        primary_visible[case["name"]] = bool(candidates and spans and patches)
        built_rows.append({"name": case["name"], "control_svg": source_svg,
                           "candidate_svg": candidate_svg})
        row_geometry_path = EVIDENCE / "provenance" / f"case-{index:02d}-selection.json"
        write_json(row_geometry_path, panel_proof)
        append_progress(progress, "row-measured-and-saved", row=index, name=case["name"],
                        candidates=len(candidates), visible_spans=len(spans),
                        ink_patches=len(patches), support_geometry_sha256=support_hash,
                        panel= str(candidate_path.relative_to(ROOT)),
                        panel_sha256=file_sha(candidate_path),
                        elapsed_row_seconds=round(time.monotonic() - started, 3))

    if not all(primary_visible.get(row["name"], False) for row in cases[:2]):
        raise ValueError("positive half-turn views do not both have a valid visible cue")
    if any(not proof["fill_visibility_unchanged"] for proof in proof_rows):
        raise ValueError("support fill visibility changed in the overlay")

    labelled_svg = comparison_board(built_rows, True)
    unlabelled_svg = comparison_board(built_rows, False)
    labelled_svg_path = EVIDENCE / "comparison-labelled.svg"
    unlabelled_svg_path = EVIDENCE / "comparison-unlabelled.svg"
    labelled_svg_path.write_text(labelled_svg, encoding="utf-8")
    unlabelled_svg_path.write_text(unlabelled_svg, encoding="utf-8")
    validate_board(labelled_svg_path)
    validate_board(unlabelled_svg_path)
    labelled_png_path = EVIDENCE / "comparison-labelled.png"
    unlabelled_png_path = EVIDENCE / "comparison-unlabelled.png"
    render(str(labelled_svg_path), str(labelled_png_path), size=(BOARD_WIDTH, ROW_TOP + ROW_HEIGHT * 5))
    render(str(unlabelled_svg_path), str(unlabelled_png_path), size=(BOARD_WIDTH, ROW_TOP + ROW_HEIGHT * 5))
    validate_png(labelled_png_path)
    validate_png(unlabelled_png_path)
    label_only_panel_variance = panel_crop_variance(labelled_png_path, unlabelled_png_path)

    repeat_dir = EVIDENCE / "determinism"
    repeat_dir.mkdir(parents=True, exist_ok=True)
    repeat_png = repeat_dir / "comparison-unlabelled-repeat.png"
    render(str(unlabelled_svg_path), str(repeat_png), size=(BOARD_WIDTH, ROW_TOP + ROW_HEIGHT * 5))
    if file_sha(repeat_png) != file_sha(unlabelled_png_path):
        raise ValueError("unlabelled comparison PNG is not deterministic")

    cases_path = WORK / "cases.json"
    ledger = {
        "status": "built_pending_independent_blind_review",
        "hypothesis": config["hypothesis"],
        "authority": "continuing user go; bounded Exercise25 study only",
        "inputs": {"cases": str(cases_path.relative_to(ROOT)), "cases_sha256": file_sha(cases_path),
                   "source_plan": str(contour.PLAN_PATH.relative_to(ROOT)),
                   "source_plan_sha256": file_sha(contour.PLAN_PATH),
                   "pins": contour.verify_pins()},
        "rule": {"facing_sign_transition": "actual adjacent face normals have strict opposite camera-facing signs",
                 "projected_role": "both facets lie on the same side of their shared projected edge; positive-area overlap",
                 "occluding_role": "adjacent depth planes separate by more than existing 1e-5 + EPS tie band",
                 "visibility": "candidate intervals checked against every actual support triangle; finite ink clipped to actual depth-visible owner-face regions",
                 "weight_color": contour.INK_COLOR, "weight_px": contour.INK_WIDTH_PX,
                 "geometry": "untouched curved .35 support at 96x12; no cue changes support geometry/fill"},
        "rows": proof_rows,
        "comparison": {"labelled_svg": str(labelled_svg_path.relative_to(ROOT)),
                       "labelled_svg_sha256": file_sha(labelled_svg_path),
                       "labelled_png": str(labelled_png_path.relative_to(ROOT)),
                       "labelled_png_sha256": file_sha(labelled_png_path),
                       "unlabelled_svg": str(unlabelled_svg_path.relative_to(ROOT)),
                       "unlabelled_svg_sha256": file_sha(unlabelled_svg_path),
                       "unlabelled_png": str(unlabelled_png_path.relative_to(ROOT)),
                       "unlabelled_png_sha256": file_sha(unlabelled_png_path),
                       "unlabelled_png_repeat": str(repeat_png.relative_to(ROOT)),
                       "unlabelled_png_repeat_sha256": file_sha(repeat_png),
                       "repeat_byte_identical": file_sha(repeat_png) == file_sha(unlabelled_png_path),
                       "label_only_panel_variance": label_only_panel_variance,
                       "viewport": [BOARD_WIDTH, ROW_TOP + ROW_HEIGHT * 5],
                       "panel_namespaces_unique": True,
                       "all_panels_nonblank_centered_in_viewport": True},
        "reference_free_checks": "to be appended after exact scripts/draw check report image lists are captured",
        "full_build_elapsed_seconds": round(time.monotonic() - STARTED, 3),
    }
    write_json(EVIDENCE / "provenance" / "build-ledger.json", ledger)
    append_progress(progress, "boards-rasterized-and-validated", labelled_png_sha256=file_sha(labelled_png_path),
                    unlabelled_png_sha256=file_sha(unlabelled_png_path), repeat_equal=True,
                    label_only_panel_variance=label_only_panel_variance,
                    elapsed_seconds=ledger["full_build_elapsed_seconds"])
    print(json.dumps({"status": ledger["status"], "rows": [
        {"name": row["name"], "candidate_edges": row["camera_dependent_candidates"],
         "visible_spans": row["depth_visible_centerline_spans"],
         "ink_patches": row["finite_ink_patches"],
         "fill_visibility_unchanged": row["fill_visibility_unchanged"]} for row in proof_rows],
        "labelled_png": str(labelled_png_path.relative_to(ROOT)),
        "unlabelled_png": str(unlabelled_png_path.relative_to(ROOT)),
        "repeat_equal": True,
    }, indent=2))


if __name__ == "__main__":
    main()
