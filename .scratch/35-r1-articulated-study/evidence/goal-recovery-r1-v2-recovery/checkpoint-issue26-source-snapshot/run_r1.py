"""Reference-absent entry point for one semantic scene at a time."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]
if str(REPO) not in sys.path: sys.path.insert(0,str(REPO))
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from r1_scene import build_a_study,build_b_study,build_svg

CASES=("A","baseline","variant","control")


def build_case_svg(case: str) -> str:
    """Only frozen semantic inputs enter rendering; case is not a reference path."""
    if case=="A":
        study=build_a_study()
    elif case in {"baseline","variant","control"}:
        study,_evidence=build_b_study(case)
    else:
        raise ValueError(f"case must be one of {CASES}")
    return build_svg(study)


def write_case(case: str, output_directory: Path | None=None) -> Path:
    output_directory=Path(output_directory) if output_directory else ROOT/"rendered"
    output_directory.mkdir(parents=True,exist_ok=True)
    filename={"A":"A-observed-garment.svg","baseline":"B-baseline-support.svg",
              "variant":"B-variant-support.svg","control":"B-near-miss-control.svg"}[case]
    destination=output_directory/filename
    destination.write_text(build_case_svg(case),encoding="utf-8")
    print(f"{case}: {destination}")
    return destination


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case",choices=CASES)
    parser.add_argument("--outdir",type=Path,default=ROOT/"rendered")
    args=parser.parse_args()
    write_case(args.case,args.outdir)
