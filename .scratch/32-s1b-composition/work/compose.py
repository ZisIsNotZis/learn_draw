#!/usr/bin/env python3
"""Render the existing coarse seated-figure hypothesis and one semantic pose variation."""
import argparse
import importlib.util
import math
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("figure_scaffold", SCRIPTS / "figure_scaffold.py")
figure = importlib.util.module_from_spec(spec)
spec.loader.exec_module(figure)


def pose_scene(arm_angle):
    """Rotate the right arm and attached hand together about their shoulder support."""
    pivot = (1.26, 0.18, 0.70)
    c, s = math.cos(arm_angle), math.sin(arm_angle)
    for triangle, color, name in figure.scene():
        if arm_angle and name in {"arm-right", "hand"}:
            transformed = []
            for x, y, z in triangle:
                dx, dy = x - pivot[0], y - pivot[1]
                transformed.append((pivot[0] + c * dx - s * dy,
                                    pivot[1] + s * dx + c * dy, z))
            triangle = tuple(transformed)
        yield triangle, color, name


def render_view(yaw, offset, arm_angle):
    faces = []
    for triangle, color, name in pose_scene(arm_angle):
        projected = [figure.project(point, yaw, offset) for point in triangle]
        if name == "hair-sheet":
            a, b, c = projected
            orient = ((b[0] - a[0]) * (c[1] - a[1])
                      - (b[1] - a[1]) * (c[0] - a[0]))
            color = "#3974ab" if orient < 0 else "#83cbbd"
        faces.append((projected, color, name))
    polygons = []
    for fragment, color, name in figure.visible_fragments(faces):
        points = " ".join(f"{x:.5f},{y:.5f}" for x, y, _ in fragment)
        polygons.append(f'<polygon points="{points}" fill="{color}" stroke="{color}" '
                        f'stroke-width="0.22" data-component="{escape(name)}"/>')
    return "\n".join(polygons)


def document(arm_angle, label):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2048 1024">'
            '<rect width="2048" height="1024" fill="#c7dade"/>'
            '<g font-family="sans-serif" font-size="24" fill="#243c53">'
            '<text x="70" y="42">0° camera</text><text x="1090" y="42">43° camera</text>'
            f'<text x="70" y="985">{escape(label)}</text></g>'
            + render_view(0, 510, arm_angle) + render_view(43, 1530, arm_angle)
            + '</svg>')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "two-view.svg").write_text(
        document(0, "Coarse seated hypothesis; pose and route unvalidated"), encoding="utf-8")
    (args.out_dir / "pose-variation.svg").write_text(
        document(math.radians(-38), "Same components; right arm + hand rotated 38° at shoulder"),
        encoding="utf-8")
    print(args.out_dir / "two-view.svg")
    print(args.out_dir / "pose-variation.svg")


if __name__ == "__main__":
    main()
