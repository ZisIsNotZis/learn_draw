#!/usr/bin/env python3
"""Compile the frozen ribbon matrix once, checkpoint panels, then export four comparison boards.

This exercise driver reuses ribbon_drawing.render_panel without changing visibility, line, motif,
geometry, cases, or sampling. It is intentionally specific to exercise 20's frozen output matrix.
"""
from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import sys
import tempfile
import time
import xml.etree.ElementTree as ET

import cv2
import numpy as np
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import ribbon_drawing as drawing

SVG_NS = "http://www.w3.org/2000/svg"
NS = {"svg": SVG_NS}
WIDTH, MARGIN, GAP = 1380, 18, 8
PANEL_WIDTH = (WIDTH - 2 * MARGIN - 2 * GAP) // 3
PANEL_HEIGHT = 255
RULES = ("control", "A", "B")


def _safe(value: str) -> str:
    import re
    return re.sub(r"[^A-Za-z0-9_-]", "-", value)


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _json_hash(value) -> str:
    return _hash_text(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False))


def _progress(path: Path, data: dict) -> None:
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(data, sort_keys=True, allow_nan=False) + "\n")
        stream.flush()


def _panel_prefix(row: int, name: str, column: int) -> str:
    return f"case-{row}-{_safe(name)}-col-{column}"


def _cache_key(item: dict, rule: str, renderer_hash: str) -> str:
    return _json_hash({"case": item["name"], "source_spec_sha256": item["source_spec_sha256"],
                       "effective_spec_sha256": _json_hash(dataclasses.asdict(item["spec"])),
                       "camera": dataclasses.asdict(item["camera"]),
                       "card_bounds": item["card_bounds"], "sampling": item["sampling"],
                       "rule": rule, "renderer_sha256": renderer_hash,
                       "view_size": [PANEL_WIDTH, PANEL_HEIGHT]})


def _cached_panel(cache_dir: Path, row: int, item: dict, rule: str,
                  renderer_hash: str) -> tuple[Path, dict] | None:
    prefix = _panel_prefix(row, item["name"], RULES.index(rule))
    svg_path = cache_dir / f"{prefix}.svg"
    metadata_path = cache_dir / f"{prefix}.json"
    if not svg_path.is_file() or not metadata_path.is_file():
        return None
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("cache_key") != _cache_key(item, rule, renderer_hash):
        return None
    if metadata.get("svg_sha256") != drawing._sha256(svg_path):
        return None
    return svg_path, metadata


def compile_panels(cases: list[dict], cache_dir: Path, progress_path: Path,
                   renderer_hash: str) -> tuple[dict[tuple[int, str], tuple[Path, dict]], list[dict]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache = {}
    failures = []
    total = len(cases) * len(RULES)
    count = 0
    for row, item in enumerate(cases):
        for column, rule in enumerate(RULES):
            count += 1
            prefix = _panel_prefix(row, item["name"], column)
            found = _cached_panel(cache_dir, row, item, rule, renderer_hash)
            if found is not None:
                svg_path, metadata = found
                cache[(row, rule)] = found
                event = {"event": "reused", "number": count, "total": total,
                         "name": item["name"], "rule": rule, "svg": str(svg_path),
                         "svg_sha256": metadata["svg_sha256"]}
                _progress(progress_path, event)
                print(f"[{count}/{total}] reused {item['name']} {rule}", flush=True)
                continue
            start = time.monotonic()
            print(f"[{count}/{total}] render start {item['name']} {rule}", flush=True)
            try:
                svg, coverage = drawing.render_panel(
                    item["spec"], item["camera"], rule, PANEL_WIDTH, PANEL_HEIGHT, prefix,
                    False, item["card_bounds"], item["sampling"], False)
                svg_path = cache_dir / f"{prefix}.svg"
                metadata_path = cache_dir / f"{prefix}.json"
                svg_path.write_text(svg, encoding="utf-8")
                metadata = {"cache_key": _cache_key(item, rule, renderer_hash),
                            "case": item["name"], "rule": rule,
                            "source": item["source"],
                            "source_spec_sha256": item["source_spec_sha256"],
                            "camera": dataclasses.asdict(item["camera"]),
                            "sampling": item["sampling"], "coverage": coverage,
                            "svg_sha256": drawing._sha256(svg_path),
                            "svg_bytes": svg_path.stat().st_size}
                metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n",
                                         encoding="utf-8")
                cache[(row, rule)] = (svg_path, metadata)
                elapsed = time.monotonic() - start
                event = {"event": "compiled", "number": count, "total": total,
                         "name": item["name"], "rule": rule, "seconds": round(elapsed, 3),
                         "svg": str(svg_path), "svg_sha256": metadata["svg_sha256"],
                         "svg_bytes": metadata["svg_bytes"]}
                _progress(progress_path, event)
                print(f"[{count}/{total}] render done {item['name']} {rule} "
                      f"{elapsed:.2f}s, {metadata['svg_bytes']} bytes", flush=True)
            except Exception as exc:  # keep all later independent frozen panels runnable
                elapsed = time.monotonic() - start
                failure = {"case": item["name"], "rule": rule,
                           "error_type": type(exc).__name__, "error": str(exc),
                           "seconds": round(elapsed, 3)}
                failures.append(failure)
                _progress(progress_path, {"event": "failed", "number": count, "total": total,
                                          **failure})
                print(f"[{count}/{total}] render FAILED {item['name']} {rule}: "
                      f"{type(exc).__name__}: {exc}", flush=True)
    return cache, failures


def _panel_parts(svg: str) -> tuple[str, list[str]]:
    """Serialize the paper rect and semantic ink as unprefixed inline SVG elements."""
    ET.register_namespace("", SVG_NS)
    root = ET.fromstring(svg)
    ground = root.find('./svg:rect[@id]', NS)
    if ground is None:
        raise ValueError("cached panel has no named ground rectangle")
    lines = root.findall('.//svg:path[@data-intent]', NS)
    serialized = [ET.tostring(ground, encoding="unicode")]
    serialized.extend(ET.tostring(node, encoding="unicode") for node in lines)
    if any("<ns0:" in part for part in serialized):
        raise ValueError("inline SVG child serializer emitted an unsupported namespace prefix")
    return serialized[0], serialized[1:]


def _line_records(svg: str) -> tuple[tuple[tuple[str, str], ...], ...]:
    root = ET.fromstring(svg)
    return tuple(tuple(sorted(element.attrib.items()))
                 for element in root.findall('.//svg:path[@data-intent]', NS))


def verify_line_only_equivalence(cases: list[dict], cache: dict,
                                 progress_path: Path, renderer_hash: str) -> dict:
    """Compare a cached colour panel's named ink with direct `line_only=True` compilation.

    The chosen frozen support-card case verifies that extracted paths retain external depth clipping.
    This is a bounded duplicate compile, not another case/rule hypothesis.
    """
    row = next(index for index, item in enumerate(cases)
               if item["name"] == "external-support-card-front")
    item = cases[row]
    rule = "B"
    svg_path, metadata = cache[(row, rule)]
    prefix = _panel_prefix(row, item["name"], RULES.index(rule))
    direct_svg, _ = drawing.render_panel(item["spec"], item["camera"], rule,
                                         PANEL_WIDTH, PANEL_HEIGHT, prefix, False,
                                         item["card_bounds"], item["sampling"], True)
    cached_svg = svg_path.read_text(encoding="utf-8")
    if _line_records(cached_svg) != _line_records(direct_svg):
        raise AssertionError("cached ink extraction differs from direct line_only=True output")
    cached_ground, cached_lines = _panel_parts(cached_svg)
    direct_ground, direct_lines = _panel_parts(direct_svg)
    if cached_ground != direct_ground or cached_lines != direct_lines:
        raise AssertionError("line-only background/path XML differs from direct output")
    exported_svg = _standalone_line_only(cached_svg, PANEL_WIDTH, PANEL_HEIGHT)
    raster = _raster_equivalence(direct_svg, exported_svg, PANEL_WIDTH, PANEL_HEIGHT)
    result = {"case": item["name"], "rule": rule, "support_card": True,
              "sampling": item["sampling"], "line_path_count": len(cached_lines),
              "cached_svg_sha256": metadata["svg_sha256"],
              "direct_line_only_svg_sha256": _hash_text(direct_svg),
              "raster_equivalence": raster,
              "equivalent": True, "meaning": "no fill-derived depth mask is discarded: each"
              " finite-width ink polygon was already clipped against all depth-nearer triangles"}
    _progress(progress_path, {"event": "line_only_equivalence", **result})
    print(f"line-only equivalence passed: {len(cached_lines)} paths, frozen external card", flush=True)
    return result


def _line_only_inner(svg: str) -> str:
    ground, lines = _panel_parts(svg)
    return ground + "\n" + "\n".join(lines)


def _standalone_line_only(svg: str, width: int, height: int) -> str:
    """Make a browser-ready standalone panel containing only cached, clipped ink paths."""
    body = _line_only_inner(svg)
    result = f'<svg xmlns="{SVG_NS}" viewBox="0 0 {width} {height}">{body}</svg>'
    if "<ns0:" in result:
        raise ValueError("line-only board contains a prefixed SVG tag")
    return result


def _raster_equivalence(direct_svg: str, exported_svg: str, width: int, height: int) -> dict:
    """Require browser pixels from cached extraction to equal direct renderer line-only output."""
    from draw import render
    with tempfile.TemporaryDirectory(prefix="ribbon-line-only-equivalence-") as temp_dir:
        direct_src = Path(temp_dir) / "direct.svg"
        export_src = Path(temp_dir) / "export.svg"
        direct_png = Path(temp_dir) / "direct.png"
        export_png = Path(temp_dir) / "export.png"
        direct_src.write_text(direct_svg, encoding="utf-8")
        export_src.write_text(exported_svg, encoding="utf-8")
        render(str(direct_src), str(direct_png), size=(width, height))
        render(str(export_src), str(export_png), size=(width, height))
        direct_pixels = cv2.imread(str(direct_png), cv2.IMREAD_COLOR)
        export_pixels = cv2.imread(str(export_png), cv2.IMREAD_COLOR)
    if direct_pixels is None or export_pixels is None:
        raise AssertionError("Chromium did not produce both direct/export PNGs")
    if direct_pixels.shape != export_pixels.shape:
        raise AssertionError(f"line-only raster size changed: {direct_pixels.shape} != {export_pixels.shape}")
    paper = np.array((246, 250, 251), dtype=np.uint8)
    nonbackground = int(np.count_nonzero(np.any(
        np.abs(direct_pixels.astype(np.int16) - paper) > 8, axis=2)))
    if nonbackground == 0:
        raise AssertionError("direct line-only reference rendered only the paper background")
    mismatches = int(np.count_nonzero(np.any(direct_pixels != export_pixels, axis=2)))
    if mismatches:
        raise AssertionError(f"direct/export line-only rasters differ at {mismatches} pixels")
    return {"width": width, "height": height, "nonbackground_pixels": nonbackground,
            "mismatched_pixels": mismatches}


def assemble_board(cases: list[dict], cache: dict, labels: bool,
                   line_only: bool, out_path: Path, case_plan_hash: str,
                   equivalence: dict) -> dict:
    columns = 3
    heading = 38 if labels else 12
    height = heading + MARGIN + len(cases) * PANEL_HEIGHT + (len(cases) - 1) * GAP + MARGIN
    parts = [f'<svg xmlns="{SVG_NS}" viewBox="0 0 {WIDTH} {height}">',
             '<!-- Frozen 8-case comparison; unchanged support/camera across three columns. -->',
             f'<rect id="board-ground" width="{WIDTH}" height="{height}" fill="#e9eeea"/>']
    if labels:
        title = "Ribbon drawing rule · control / complete semantic perimeter / perimeter + local motif"
        parts.append(f'<text x="{MARGIN}" y="23" font-family="sans-serif" font-size="15" '
                     f'font-weight="600" fill="#263b4b">{escape(title)}</text>')
        if line_only:
            caption = ("Line-only: finite-width semantic perimeter paths clipped by projected opaque depth; "
                       "no artwork fills shown")
            parts.append(f'<text x="{MARGIN}" y="34" font-family="sans-serif" font-size="8" '
                         f'fill="#526a60">{escape(caption)}</text>')
    headings = ("control", "rule A · perimeter ink", "rule B · ink + local motif")
    for column, text in enumerate(headings):
        if labels:
            x = MARGIN + column * (PANEL_WIDTH + GAP)
            parts.append(f'<text x="{x + 7}" y="{heading - 6}" font-family="sans-serif" '
                         f'font-size="9" fill="#42596a">{escape(text)}</text>')
    panel_manifest = []
    for row, item in enumerate(cases):
        y = heading + MARGIN + row * (PANEL_HEIGHT + GAP)
        for column, rule in enumerate(RULES):
            svg_path, metadata = cache[(row, rule)]
            panel_svg = svg_path.read_text(encoding="utf-8")
            if line_only:
                body = _line_only_inner(panel_svg)
            else:
                body = panel_svg[panel_svg.index(">") + 1:panel_svg.rfind("</svg>")]
            prefix = _panel_prefix(row, item["name"], column)
            x = MARGIN + column * (PANEL_WIDTH + GAP)
            parts.append(f'<g id="{prefix}-group" transform="translate({x} {y})">{body}</g>')
            panel_manifest.append({"name": item["name"], "rule": rule,
                                   "camera": dataclasses.asdict(item["camera"]),
                                   "source": item["source"],
                                   "source_spec_sha256": item["source_spec_sha256"],
                                   "cache_svg_sha256": metadata["svg_sha256"],
                                   "coverage": metadata["coverage"]})
        if labels:
            text = f"{item['name']} · {item['camera'].name} · {item['sampling']} intervals"
            parts.append(f'<text x="{MARGIN + 6}" y="{y + 13}" font-family="sans-serif" '
                         f'font-size="9" fill="#263b4b">{escape(text)}</text>')
    parts.append('</svg>')
    svg = "\n".join(parts)
    if "<ns0:" in svg:
        raise ValueError("board contains namespace-prefixed SVG children that do not survive HTML parsing")
    ET.fromstring(svg)  # reject malformed board XML before committing output files
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(svg, encoding="utf-8")
    manifest = {"case_plan_sha256": case_plan_hash,
                "renderer_sha256": drawing._sha256(SCRIPTS / "ribbon_drawing.py"),
                "line_only": line_only, "labelled": labels,
                "line_only_equivalence": equivalence if line_only else None,
                "panels": panel_manifest, "svg_sha256": drawing._sha256(out_path),
                "svg_bytes": out_path.stat().st_size}
    manifest_path = out_path.with_name(out_path.stem + "-manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
    print(f"board wrote {out_path} ({manifest['svg_bytes']} bytes)", flush=True)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-plan", type=Path,
                        default=ROOT / ".scratch/20-ribbon-drawing-rule/work/cases.json")
    parser.add_argument("--out-dir", type=Path,
                        default=ROOT / ".scratch/20-ribbon-drawing-rule/evidence")
    parser.add_argument("--progress", type=Path,
                        default=ROOT / ".scratch/20-ribbon-drawing-rule/work/build-progress.jsonl")
    args = parser.parse_args()
    cases, plan = drawing.load_case_plan(args.case_plan)
    renderer_hash = drawing._sha256(SCRIPTS / "ribbon_drawing.py")
    args.progress.parent.mkdir(parents=True, exist_ok=True)
    run = datetime.now(timezone.utc).isoformat()
    _progress(args.progress, {"event": "run_started", "utc": run,
                              "case_plan_sha256": drawing._sha256(args.case_plan),
                              "renderer_sha256": renderer_hash,
                              "panel_count": len(cases) * len(RULES),
                              "view_size": [PANEL_WIDTH, PANEL_HEIGHT]})
    cache, failures = compile_panels(cases, args.out_dir / "cache", args.progress, renderer_hash)
    expected = len(cases) * len(RULES)
    if failures or len(cache) != expected:
        _progress(args.progress, {"event": "build_incomplete", "cached": len(cache),
                                  "expected": expected, "failures": failures})
        raise SystemExit(f"board export skipped: {len(cache)}/{expected} panels cached; "
                         f"{len(failures)} individual failures recorded")
    equivalence = verify_line_only_equivalence(cases, cache, args.progress, renderer_hash)
    case_plan_hash = drawing._sha256(args.case_plan)
    jobs = (("comparison-labelled", True, False),
            ("comparison-unlabelled", False, False),
            ("line-only-labelled", True, True),
            ("line-only-unlabelled", False, True))
    for stem, labels, line_only in jobs:
        assemble_board(cases, cache, labels, line_only,
                       args.out_dir / f"{stem}.svg", case_plan_hash, equivalence)
    _progress(args.progress, {"event": "build_complete", "cached": len(cache),
                              "expected": expected, "boards": [job[0] for job in jobs]})
    print(f"complete: {expected} panels compiled once; four cached boards assembled", flush=True)


if __name__ == "__main__":
    main()
