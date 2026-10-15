#!/usr/bin/env python3
"""Measure actual selected/fine mesh section chords from triangle/UV intersections."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
TESTS = SCRIPTS / "tests"
if str(TESTS) not in sys.path:
    sys.path.insert(0, str(TESTS))

from ribbon_family import RibbonSpec
from ribbon_surface import build_surface, surface_points
from test_ribbon_surface import mesh_section_chord_length, mesh_section_points

PLAN = Path(__file__).resolve().with_name("cases.json")
OUT = Path(__file__).resolve().parents[1] / "evidence" / "mesh-chord-width.json"
BOUND = 0.002
U_SAMPLES = (0.0, 0.19, 0.49, 0.5, 0.51, 0.81, 1.0)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    unique = []
    seen = set()
    for item in plan["cases"]:
        name = item["ribbon"]["name"]
        if name not in seen:
            seen.add(name)
            camera_rows = [{"name": row["camera"]["name"],
                            "sha256": row["camera_sha256"]}
                           for row in plan["cases"]
                           if row["source_spec_sha256"] == item["source_spec_sha256"]]
            unique.append((item["name"], item["source_spec_sha256"],
                           item["ribbon"], camera_rows))
    measurements = []
    for case_name, source_hash, raw, camera_rows in unique:
        spec = RibbonSpec.from_mapping(raw)
        meshes = {}
        for u_count, v_count in ((48, 6), (96, 12)):
            meshes[("flat", u_count, v_count)] = build_surface(spec, 0.0, u_count, v_count)
            meshes[("curved", u_count, v_count)] = build_surface(spec, 0.35, u_count, v_count)
        for u in U_SAMPLES:
            flat48 = meshes[("flat", 48, 6)]
            curved48 = meshes[("curved", 48, 6)]
            flat_width = mesh_section_chord_length(flat48, u)
            curved_width = mesh_section_chord_length(curved48, u)
            requested = spec.width * (1.0 + (spec.tip_ratio - 1.0) * u)
            flat_points = mesh_section_points(flat48, u)
            curved_points = mesh_section_points(curved48, u)
            dense_points = surface_points(
                spec, curved48, u, (-1.0 + 2.0 * i / 512 for i in range(513)))
            dense_arc = sum(math.dist(a, b) for a, b in zip(dense_points, dense_points[1:]))
            signed = flat_width - curved_width
            fine_flat = mesh_section_chord_length(meshes[("flat", 96, 12)], u)
            fine_curve = mesh_section_chord_length(meshes[("curved", 96, 12)], u)
            fine_signed = fine_flat - fine_curve
            measurements.append({
                "source_case": case_name,
                "same_frozen_camera_rows": camera_rows,
                "source_spec_sha256": source_hash,
                "u": u,
                "continuous_requested_width": requested,
                "48x6": {
                    "legacy_finite_width": flat_width,
                    "curved_mesh_chord_width": curved_width,
                    "signed_deficit_legacy_minus_curved": signed,
                    "absolute_difference": abs(signed),
                    "mesh_chord_vs_512v_curve_arc": curved_width - dense_arc,
                    "flat_section_vertex_count": len(flat_points),
                    "curved_section_vertex_count": len(curved_points),
                    "within_0.002_world_units": abs(signed) <= BOUND,
                },
                "96x12_same_camber": {
                    "legacy_finite_width": fine_flat,
                    "curved_mesh_chord_width": fine_curve,
                    "signed_deficit_legacy_minus_curved": fine_signed,
                    "absolute_difference": abs(fine_signed),
                    "within_0.002_world_units": abs(fine_signed) <= BOUND,
                },
            })
    failures = [row for row in measurements
                if not row["48x6"]["within_0.002_world_units"]]
    fine_failures = [row for row in measurements
                     if not row["96x12_same_camber"]["within_0.002_world_units"]]
    result = {
        "purpose": "actual triangle/UV cross-section chord width; diagnostic, not a changed candidate",
        "camera_scope": "world-space chord width is camera-independent; each unique frozen spec is tested once and its recorded front/oblique rows share that mesh",
        "method": "intersect every generated SupportTriangle UV edge with fixed-u, interpolate its actual 3D edge point, deduplicate shared points by v, sort, sum consecutive 3D chords",
        "case_plan_sha256": sha(PLAN),
        "support_module_sha256": sha(SCRIPTS / "ribbon_surface.py"),
        "test_helper_sha256": sha(TESTS / "test_ribbon_surface.py"),
        "selected_bound_world_units": BOUND,
        "sampling": {"selected": [48, 6], "fine_same_camber": [96, 12]},
        "sampled_u": list(U_SAMPLES),
        "selected48x6_within_bound": not failures,
        "selected_failures": [{"case": row["source_case"], "u": row["u"],
                               "signed_deficit": row["48x6"]["signed_deficit_legacy_minus_curved"],
                               "absolute_difference": row["48x6"]["absolute_difference"]}
                              for row in failures],
        "fine96x12_within_bound": not fine_failures,
        "fine_failures": [{"case": row["source_case"], "u": row["u"],
                            "signed_deficit": row["96x12_same_camber"]["signed_deficit_legacy_minus_curved"],
                            "absolute_difference": row["96x12_same_camber"]["absolute_difference"]}
                           for row in fine_failures],
        "measurements": measurements,
        "interpretation": "The fixed 48x6 raster mesh does not meet the declared 0.002 chord-width bound at every u. Values and failing samples are retained; camber, cases, cameras, algorithm, and candidates were not changed.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(OUT), "selected_pass": result["selected48x6_within_bound"],
                      "selected_failures": result["selected_failures"],
                      "fine_pass": result["fine96x12_within_bound"],
                      "fine_failures": result["fine_failures"]}, indent=2))


if __name__ == "__main__":
    main()
