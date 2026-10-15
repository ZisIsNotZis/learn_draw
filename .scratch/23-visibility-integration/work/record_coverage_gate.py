"""Persist finite source-triangle coverage and source-policy counts for the current kernel."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts.tests.test_vector_visibility import ring_and_occluder  # noqa: E402
from scripts.tests.test_vector_visibility_oracle import (  # noqa: E402
    NEAR_POLICY_BAND,
    _fragment_union,
    _grid_bounds,
    _source_depth_masks,
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    rows = []
    for yaw in (0, 55):
        original = ring_and_occluder(yaw)
        faces = [([(x - 200, y - 150, z) for x, y, z in tri], color, name)
                 for tri, color, name in original]
        for n, phase in ((256, .5), (512, .5), (1024, .25), (1024, .75)):
            xs, ys = _grid_bounds(faces, n, phase)
            source = _source_depth_masks(faces, xs, ys)
            strict, fragment_boundary, fragments = _fragment_union(faces, xs, ys)
            usable = ~source["policy"] & ~fragment_boundary
            false_positive = strict & ~source["visible"] & usable
            false_negative = ~strict & source["visible"] & usable
            rows.append({
                "yaw": yaw, "n": n, "phase": phase,
                "near_policy_band": NEAR_POLICY_BAND,
                "samples": n * n,
                "source_strip_layers_ge2": int((source["strip_hits"] >= 2).sum()),
                "source_body_layers_ge2": int((source["body_hits"] >= 2).sum()),
                "source_policy_exclusions_overlapping_categories": {
                    "source_edges": int(source["source_edge"].sum()),
                    "exact_depth_ties": int(source["exact_tie"].sum()),
                    "cross_component_near_ties": int(source["cross_near"].sum()),
                    "strip_same_component_top_near_ties": int(source["strip_self_near"].sum()),
                    "body_same_component_top_near_ties": int(source["body_self_near"].sum()),
                    "unique_union": int(source["policy"].sum()),
                },
                "fragment_boundary_exclusions": int(fragment_boundary.sum()),
                "unambiguous_samples": int(usable.sum()),
                "source_visible_samples": int(source["visible"].sum()),
                "candidate_strict_interior_samples": int(strict.sum()),
                "false_positive_samples": int(false_positive.sum()),
                "false_negative_samples": int(false_negative.sum()),
                "fragment_count": len(fragments),
            })
    test_path = ROOT / "scripts/tests/test_vector_visibility_oracle.py"
    kernel_path = ROOT / "scripts/vector_visibility.py"
    result = {
        "scope": "finite test grids only; comparisons exclude source-policy band and fragment boundaries",
        "source_hashes": {
            "current_kernel": sha(kernel_path),
            "coverage_test": sha(test_path),
            "historical_pre_integration_kernel": "6cea919d0c83b1c4ebb9b3ec3379854c910e2758610b449c036c25c9ce8e1ada",
            "reviewed_v3_candidate": "5f289fed2ffe3d35740e0d3927b0a2ed168883d8785f4786746e6610e3112da7",
        },
        "by_grid": rows,
        "acceptance_boundary": "0 FP/FN on listed unambiguous samples is not continuous or full-policy proof",
    }
    output = ROOT / ".scratch/23-visibility-integration/evidence/oracle/coverage-gate-current.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
