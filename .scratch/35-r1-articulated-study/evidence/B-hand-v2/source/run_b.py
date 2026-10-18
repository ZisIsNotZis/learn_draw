"""Reference-absent entry point: build the three B panels and their matched-camera sheet.

Nothing here reads a reference image; each case is a frozen semantic input.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]
for entry in (str(REPO), str(ROOT)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from scene import build_b_study, build_svg, compose_b_studies  # noqa: E402

CASES = ("baseline", "variant", "control")
FILENAMES = {"baseline": "B-baseline-support.svg", "variant": "B-variant-support.svg",
             "control": "B-near-miss-control.svg"}


def panel_svg(case: str) -> str:
    study, _evidence = build_b_study(case)
    return build_svg(study)


def write_case(case: str, output_directory: Path) -> Path:
    if case not in CASES:
        raise ValueError(f"case must be one of {CASES}")
    output_directory.mkdir(parents=True, exist_ok=True)
    destination = output_directory / FILENAMES[case]
    destination.write_text(panel_svg(case), encoding="utf-8")
    print(f"{case}: {destination}")
    return destination


def write_sheet(output_directory: Path) -> Path:
    sources = tuple((output_directory / FILENAMES[case]).read_text(encoding="utf-8") for case in CASES)
    destination = output_directory / "B-original-support.svg"
    destination.write_text(compose_b_studies(sources), encoding="utf-8")
    print(f"sheet: {destination}")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=ROOT.parent / "rendered")
    args = parser.parse_args()
    for case in CASES:
        write_case(case, args.outdir)
    write_sheet(args.outdir)


if __name__ == "__main__":
    main()
