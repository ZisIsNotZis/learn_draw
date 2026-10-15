#!/usr/bin/env python3
"""Verify the frozen 96x12 precision retest on the copied 44-u actual-mesh grid before rendering."""
from __future__ import annotations

import hashlib
import json
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
from ribbon_surface import build_surface
from test_ribbon_surface import mesh_section_chord_length

PLAN = Path(__file__).resolve().with_name("cases-fine.json")
OUT = Path(__file__).resolve().parents[1] / "evidence" / "fine" / "fine-mesh-width.json"
BOUND = 0.002


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    fine = plan["precision_retest"]
    grid = fine["actual_mesh_u_probes"]["values"]
    if len(grid) != fine["actual_mesh_u_probes"]["count"]:
        raise ValueError("precision-retet u-grid count does not match its frozen list")
    if sha(ROOT / fine["parent_independent_summary"]["evidence_copy_path"]) != \
            fine["parent_independent_summary"]["source_sha256"]:
        raise ValueError("copied parent evidence no longer matches its frozen hash")
    unique = {}
    for case in plan["cases"]:
        unique.setdefault(case["ribbon"]["name"], case)
    measurements = []
    for case_name, case in unique.items():
        spec = RibbonSpec.from_mapping(case["ribbon"])
        flat = build_surface(spec, 0.0, 96, 12)
        curved = build_surface(spec, 0.35, 96, 12)
        for u in grid:
            flat_width = mesh_section_chord_length(flat, u)
            curved_width = mesh_section_chord_length(curved, u)
            difference = flat_width - curved_width
            requested = spec.width * (1.0 + (spec.tip_ratio - 1.0) * u)
            measurements.append({
                "case": case_name,
                "source_spec_sha256": case["source_spec_sha256"],
                "u": u,
                "legacy_flat_mesh_chord_width": flat_width,
                "curved_96x12_mesh_chord_width": curved_width,
                "signed_deficit_flat_minus_curved": difference,
                "absolute_difference": abs(difference),
                "requested_continuous_profile_width": requested,
                "within_0.002_world_units": abs(difference) <= BOUND,
            })
    failures = [row for row in measurements if not row["within_0.002_world_units"]]
    by_case = {}
    for case_name in unique:
        rows = [row for row in measurements if row["case"] == case_name]
        by_case[case_name] = {"samples": len(rows),
                              "max_abs_difference": max(row["absolute_difference"] for row in rows),
                              "failures": [{"u": row["u"],
                                            "signed_deficit": row["signed_deficit_flat_minus_curved"]}
                                           for row in rows if not row["within_0.002_world_units"]]}
    result = {
        "status": "fail" if failures else "pass",
        "purpose": "pre-render actual-mesh width gate for the separately frozen same-camber fine retest",
        "precision_retest_plan_sha256": sha(PLAN),
        "original_48x6_plan_sha256": fine["original_case_plan_sha256"],
        "parent_checkpoint_summary_sha256": fine["parent_independent_summary"]["source_sha256"],
        "support_module_sha256": sha(SCRIPTS / "ribbon_surface.py"),
        "test_helper_sha256": sha(TESTS / "test_ribbon_surface.py"),
        "measurement_script_sha256": sha(Path(__file__).resolve()),
        "mesh": {"u_intervals": 96, "v_intervals": 12, "camber": 0.35},
        "declared_bound_world_units": BOUND,
        "probe_design": fine["actual_mesh_u_probes"],
        "unique_geometry_specs": by_case,
        "measurement_count": len(measurements),
        "measurements": measurements,
        "rendering_authorized_by_this_check": not failures,
        "note": "The samples are finite evidence only; no continuous/global width guarantee is implied.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "output": str(OUT),
                      "measurement_count": len(measurements),
                      "unique_geometry_specs": by_case}, indent=2))
    if failures:
        raise SystemExit(f"fine mesh exceeded unchanged {BOUND} world-unit bound at {len(failures)} probes")


if __name__ == "__main__":
    main()
