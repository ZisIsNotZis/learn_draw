#!/usr/bin/env python3
"""Build entry point: write the full figure's SVG from the parts library.

Reference discipline: this program never reads the reference image or any crop.  The reference
seeded the landmarks while they were authored; after that it is closed, and the build
proves it by running with the image absent.

Run from the repository root:

    .venv/bin/python .scratch/35-r1-articulated-study/evidence/A-full-figure-v1/source/build_full.py \
        --out .scratch/35-r1-articulated-study/evidence/A-full-figure-v1/artwork.svg
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

from source.full import assemble_full, figure  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the full figure; no reference inputs")
    parser.add_argument("--out", required=True, help="output SVG path")
    parser.add_argument("--report", help="optional build report JSON path")
    args = parser.parse_args()

    scene = figure.build()
    svg, info = assemble_full.render_svg(scene)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(svg, encoding="utf-8")

    missing = sorted(part for part in figure.declared_parts() if part not in scene["parts"])
    undeclared = sorted(set(scene["parts"]) - figure.declared_parts())
    report = dict(svg=str(out), parts=sorted(scene["parts"]), faces=info["faces"],
                  visible_fill_regions=info["regions"], marks=info["marks"],
                  mark_paths=info["mark_paths"], objects=len(figure.OBJECTS),
                  missing_objects=missing, undeclared_parts=undeclared)
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("parts", "faces", "visible_fill_regions",
                                             "objects", "missing_objects",
                                             "undeclared_parts")}, sort_keys=True))
    if missing:
        print(f"MISSING OBJECTS {missing}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
