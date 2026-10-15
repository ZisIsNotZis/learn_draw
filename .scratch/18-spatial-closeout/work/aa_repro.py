#!/usr/bin/env python3
"""Controlled adjacent-face SVG raster probe; --grouped is post-fix behavior."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from vector_visibility import visible_fragments


def faces(nx=8, ny=6):
    out = []
    for j in range(ny):
        for i in range(nx):
            x0, x1 = 31.25 + i * 31.125, 31.25 + (i + 1) * 31.125
            y0, y1 = 27.375 + j * 31.125, 27.375 + (j + 1) * 31.125
            # A flat support surface with alternating diagonal tessellation.
            a, b, c, d = (x0, y0, 1), (x1, y0, 1), (x1, y1, 1), (x0, y1, 1)
            tris = ((a, b, c), (a, c, d)) if (i + j) % 2 == 0 else ((a, b, d), (b, c, d))
            out.extend((list(tri), '#45c982', 'planar-sheet') for tri in tris)
    return out


def svg(grouped):
    source = faces()
    background = '<rect width="320" height="256" fill="#14212b"/>'
    if not grouped:
        shapes = []
        for poly, color, _name in visible_fragments(source):
            points = ' '.join(f'{x:.12g},{y:.12g}' for x, y, _z in poly)
            shapes.append(f'<polygon points="{points}" fill="{color}"/>')
    else:
        from vector_visibility import visible_regions
        shapes = []
        for data, color, _name in visible_regions(source):
            shapes.append(f'<path d="{data}" fill="{color}"/>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 256">'
            + background + ''.join(shapes) + '</svg>')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--grouped', action='store_true')
    parser.add_argument('-o', '--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg(args.grouped), encoding='utf-8')
    print(args.output)
