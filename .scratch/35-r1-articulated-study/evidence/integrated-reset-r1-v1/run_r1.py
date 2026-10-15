"""Reference-absent deterministic reproduction entry point for the frozen A/B scene inputs."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from r1_scene import build_a_study, build_b_study, build_svg


def write_svgs(output_directory):
    """Write both authored scenes; input is an output path only and never includes a reference."""
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    paths = {}
    for filename, scene_builder in (
        ("A-observed-garment.svg", build_a_study),
        ("B-original-action.svg", build_b_study),
    ):
        destination = output / filename
        destination.write_text(build_svg(scene_builder()), encoding="utf-8")
        paths[filename] = destination
    return paths


if __name__ == "__main__":
    destination = Path(sys.argv[1]) if len(sys.argv) == 2 else ROOT / "rendered"
    for name, path in write_svgs(destination).items():
        print(f"{name}: {path}")
