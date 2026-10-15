"""Compose the three already generated B vectors into a matched-camera review sheet."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
REPO=ROOT.parents[3]
if str(REPO) not in sys.path: sys.path.insert(0,str(REPO))
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from r1_scene import compose_b_studies

FILES=("B-baseline-support.svg","B-variant-support.svg","B-near-miss-control.svg")

def main():
    sources=tuple((ROOT/"rendered"/name).read_text(encoding="utf-8") for name in FILES)
    output=ROOT/"rendered"/"B-original-support.svg"
    output.write_text(compose_b_studies(sources),encoding="utf-8")
    print(output)

if __name__=="__main__": main()
