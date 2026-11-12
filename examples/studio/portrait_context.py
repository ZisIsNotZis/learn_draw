"""Use the editable lock in the existing portrait without modifying its package.

The old long right curtain supplies a semantic root placement. The lock's shape
comes from the studio generator. This is a context experiment, not acceptance of
the old portrait, a new head primitive, or an inferred spatial attachment system.
"""
from __future__ import annotations

import argparse
import importlib.util
import hashlib
import math
import shutil
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.studio.geometry import lock_rows, mix, outline
from scripts.studio.model import engine_fingerprint, read, write
from scripts.studio.render import rasterize, tone_region


def build(base, directory, reuse_before=None):
    package = Path(base).resolve()
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location("portrait_source", package / "source/__init__.py",
                                                submodule_search_locations=[str(package / "source")])
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    from portrait_source.full import figure, assemble_full
    scene = figure.build()
    source_hashes = {str(p.relative_to(package)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in sorted((package / "source").rglob("*.py"))}
    if reuse_before:
        previous = Path(reuse_before)
        binding = read(previous / "binding.json")
        if binding.get("engine") != engine_fingerprint() or binding.get("base_source_sha256") != source_hashes:
            raise ValueError("before-image source/engine binding changed; rebuild it")
        for name in ("before.svg", "before.png"):
            shutil.copyfile(previous / name, directory / name)
    else:
        before, _ = assemble_full.render_svg(scene)
        (directory / "before.svg").write_text(before, encoding="utf-8")
        rasterize(directory / "before.svg", directory / "before.png")
    originals = dict(scene["parts"])
    name = "A-hair-fall-right"
    # Root at the crown under the hat, rather than the old visible silhouette tip.
    # A visible contour extremum is not necessarily the physical attachment.
    face_top = figure.LAYOUT["face_ring"][4]
    eye_center = figure.lerp2(figure.LAYOUT["eye_left"], figure.LAYOUT["eye_right"], .5)
    root = figure.lerp2(face_top, eye_center, .35)
    tip = figure.LAYOUT["fall_right_poly"][4]
    delta = (tip[0] - root[0], tip[1] - root[1])
    length = math.hypot(*delta)
    node = dict(id="temple-lock", kind="hair-lock", intent="a temple-rooted long lock, swelling over the shoulder and tapering below",
                at=dict(anchor="upper_right", offset=[root[0] / 1024 - .75, root[1] / 1024 - .12]),
                length=length / 1024, width=.10, width_side="right",
                angle=math.degrees(math.atan2(delta[0], delta[1])), sweep=.045)
    rows = lock_rows(node, [1024, 1024])
    points = lambda pts: tuple(figure.full(*p) for p in pts)
    # A visible contour extremum was not an attachment, and a sloping depth
    # plane crossed THROUGH the hat, producing a horizontal exposure boundary.
    # Place the root inside its host; keep this support behind face/fringe and
    # in front of shoulder cloth. Their geometry decides exposure at the edges.
    z_base = min(scene['parts']['A-face'].frame.z0,
                 scene['parts']['A-hair-bangs'].frame.z0) - .01
    grad = (0, 0)
    node['depth'] = z_base
    side_lines = [("hair_edge", points([r.left for r in rows]), "the lock's inner flowing contour"),
                  ("hair_edge", points([r.right for r in rows]), "the lock's outer flowing contour")]
    scene["parts"][name] = figure.planar(name, node["intent"], z_base, points(outline(rows)), rows=side_lines,
                                          fill=figure.HAIR_SHADE, grad=grad, authored=(("temple_root", root),))
    scene["parts"][name + "-shade"] = figure.planar(
        name + "-shade", "the same lock turning inward, derived from its edited cross sections", z_base + .001,
        points(tone_region(rows, 0, 1, .77, 1)), fill=figure.HAIR_DEEP, grad=grad)
    light_name = name + "-light"
    scene["parts"][light_name] = figure.planar(
        light_name, "a short sheen following the lock without making a full-length hard stripe", z_base + .002,
        points(tone_region(rows, .20, .76, .23, .38)), fill=figure.HAIR_LIT, grad=grad)
    marks = [m for m in scene["sheet_marks"] if m[1] != name]
    for k, (share, start, end) in enumerate(((.52, .09, .88), (.73, .27, .96))):
        pts = points([mix(r.left, r.right, share) for r in rows if start <= r.t <= end])
        world = tuple((p.u, p.v, z_base + grad[1] * p.v + .005) for p in pts)
        marks.append((f"{name}-strand-{k}", name, "fold_edge", world, figure.HAIR_INK))
    scene["sheet_marks"] = tuple(marks)
    preserved = [sid for sid, part in originals.items() if sid not in (name, name + "-shade")]
    assert all(scene["parts"][sid] is originals[sid] for sid in preserved)
    after, _ = assemble_full.render_svg(scene)
    (directory / "artwork.svg").write_text(after, encoding="utf-8")
    rasterize(directory / "artwork.svg", directory / "artwork.png")
    write(directory / "lock.json", node)
    write(directory / "binding.json", dict(base_package=str(package), engine=engine_fingerprint(),
                                            adapter_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                                            base_source_sha256=source_hashes,
                                            reused_before=str(reuse_before) if reuse_before else None,
                                            changed_parts=[name, name + "-shade"], added_parts=[light_name],
                                            unchanged_part_count=len(preserved),
                                            scope="right fall context experiment; no whole-artwork PASS"))
    from PIL import Image, ImageDraw
    images = [Image.open(directory / f).convert("RGB") for f in ("before.png", "artwork.png")]
    board = Image.new("RGB", (2048, 1060), "#f5eee4")
    draw = ImageDraw.Draw(board)
    for i, (im, label) in enumerate(zip(images, ("BEFORE", "STUDIO LOCK — CONTEXT STUDY"))):
        board.paste(im, (i * 1024, 36))
        draw.text((i * 1024 + 20, 10), label, fill="#263c50")
    board.save(directory / "comparison.png")
    return directory


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="existing A-full-figure-waist-r1 package")
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--reuse-before", help="reuse a baseline only when its source and engine hashes match")
    args = parser.parse_args()
    print(build(args.base, args.outdir, args.reuse_before))
