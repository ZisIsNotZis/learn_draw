#!/usr/bin/env python3
"""Build entry point: write artwork-a.svg from the part library.

Reference discipline: this program never reads image.jpg or the crop.  The crop
seeded the design numbers while they were authored; the engine sees geometry only.
Run from the repository root:

    python3 .scratch/35-r1-articulated-study/evidence/A-cloth-v6-closeout/source/build_a.py \
        --out .scratch/35-r1-articulated-study/evidence/A-cloth-v6-closeout/artwork-a.svg
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
for path in (str(ROOT), str(HERE.parent)):
    if path not in sys.path:
        sys.path.insert(0, path)

from source import assemble  # noqa: E402
from source import seam_contract  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Build artwork-a.svg; no reference inputs")
    parser.add_argument("--out", required=True, help="output SVG path")
    parser.add_argument("--report", help="optional build report JSON path")
    args = parser.parse_args()

    scene = assemble.build()
    findings = seam_contract.check(scene["parts"])
    failures = seam_contract.failures(findings)
    inventory = seam_contract.unaccounted_anchors(scene["parts"])
    svg, info = assemble.render_svg(scene)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")

    report = dict(
        svg=str(out),
        parts=sorted(scene["parts"]),
        faces=info["faces"],
        visible_fill_regions=info["regions"],
        marks=info["marks"],
        mark_paths=info["mark_paths"],
        seams_total=len(findings),
        seams_failed=len(failures),
        seam_findings=findings,
        anchors_declared=inventory["declared"],
        anchors_joint_endpoints=inventory["joint_endpoints"],
        anchors_non_joints=inventory["non_joints"],
        anchors_unaccounted=inventory["unaccounted"],
        anchors_inventory_errors=inventory["non_joint_without_reason"]
                                + inventory["inventory_names_a_missing_anchor"],
    )
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("parts", "faces", "visible_fill_regions",
                                             "seams_total", "seams_failed", "anchors_declared",
                                             "anchors_joint_endpoints", "anchors_non_joints")},
                     sort_keys=True))
    failed = False
    if failures:
        for finding in failures:
            print(f"SEAM FAILED {finding['name']}: {finding['detail']}", file=sys.stderr)
        failed = True
    for name in report["anchors_unaccounted"]:
        print(f"ANCHOR UNACCOUNTED {name}: no joint reads it and NON_JOINTS gives no reason",
              file=sys.stderr)
        failed = True
    for name in report["anchors_inventory_errors"]:
        print(f"ANCHOR INVENTORY ERROR {name}", file=sys.stderr)
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
