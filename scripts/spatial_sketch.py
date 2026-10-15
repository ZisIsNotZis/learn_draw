#!/usr/bin/env python3
"""Spatial scaffold: one uncut 2D ribbon on a curved 3D support.

Two SVG views from identical surfaces. Projected triangles are geometrically
clipped by depth, with no visibility annotations or reference raster.
"""
import argparse
import math
from pathlib import Path
from xml.sax.saxutils import escape

from vector_visibility import visible_regions


def project(p, yaw, ox, oy, scale):
    x, y, z = p
    a = math.radians(yaw)
    depth = z * math.cos(a) - x * math.sin(a)
    horizontal = x * math.cos(a) + z * math.sin(a)
    return ox + horizontal * scale, oy - y * scale, depth


def body():
    # A coarse torso/lap volume. No visibility flags or pre-cut ribbon pieces.
    nu, nv = 24, 12
    def point(i, j):
        longitude = 2 * math.pi * i / nu
        latitude = -math.pi / 2 + math.pi * j / nv
        c = math.cos(latitude)
        return (0.94 * c * math.cos(longitude),
                1.28 * math.sin(latitude),
                0.57 * c * math.sin(longitude))
    for i in range(nu):
        for j in range(nv):
            p, q, r, s = point(i, j), point(i + 1, j), point(i + 1, j + 1), point(i, j + 1)
            yield (p, q, r), '#d8e5da', 'body'
            yield (p, r, s), '#d8e5da', 'body'


def ribbon():
    # The 2D stripe occupies u in [0,1] along ONE strip, v across its width.
    # u is never split into manually marked near/far or visible/hidden intervals.
    nu = 64
    def point(i, v):
        t = 2 * math.pi * i / nu
        x = 1.30 * math.cos(t)
        y = -0.28 + 0.24 * math.sin(2 * t)
        z = 0.91 * math.sin(t)
        return (x, y + v * 0.12 * math.cos(t), z + v * 0.12 * math.sin(t))
    for i in range(nu):
        for va, vb, color in [(-1, -0.36, '#d47591'),
                              (-0.36, 0.36, '#f5b6c3'),
                              (0.36, 1, '#d47591')]:
            p, q, r, s = point(i, va), point(i + 1, va), point(i + 1, vb), point(i, vb)
            yield (p, q, r), color, 'ribbon'
            yield (p, r, s), color, 'ribbon'


def view(yaw, ox, id_prefix=None):
    faces = [([project(p, yaw, ox, 295, 167) for p in tri], color, name)
             for tri, color, name in [*body(), *ribbon()]]
    if id_prefix is None:
        id_prefix = f'camera-{yaw}-{ox}'
    out = [f'<text x="{ox - 250}" y="34" font-size="19" fill="#20304a">'
           f'{escape(str(yaw))}° camera — same uncut surfaces</text>']
    for index, (path, color, name) in enumerate(visible_regions(faces)):
        out.append(f'<!-- {escape(name)}: depth-visible region of this component fill -->')
        out.append(f'<path id="{escape(id_prefix)}-{escape(name)}-fill-{index}" d="{path}" '
                   f'fill="{color}" fill-rule="nonzero" data-component="{escape(name)}"/>')
    return '\n'.join(out)


def svg_document():
    """Build the complete two-camera document with disjoint SVG ID scopes."""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630">'
            '<rect width="1200" height="630" fill="#c5d9df"/>'
            + view(0, 290, 'camera-0') + view(55, 900, 'camera-55')
            + '<text x="28" y="610" font-size="15" fill="#20304a">'
              'One 2D striped component on a curved 3D ring; torso hides it by depth. '
              'Depth-clipped SVG polygons; the 2D ribbon is never cut by its author.'
              '</text></svg>')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-o', '--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg_document(), encoding='utf-8')
    print(args.output)


if __name__ == '__main__':
    main()
