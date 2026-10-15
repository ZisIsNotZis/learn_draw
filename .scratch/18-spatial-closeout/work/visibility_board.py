#!/usr/bin/env python3
"""Small deterministic opaque-visibility diagnostics; reference image is never read."""
import argparse
import math
from pathlib import Path
import sys
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from vector_visibility import visible_regions

BG = '#17232d'
TEXT = '#e6edf1'
GREEN = '#45c982'
ROSE = '#e16e87'
BLUE = '#3974ab'
PALE = '#f0adbd'


def grid_rect(x0, y0, x1, y1, nx, ny, component, color, flip=False):
    faces = []
    for j in range(ny):
        for i in range(nx):
            xa, xb = x0 + (x1 - x0) * i / nx, x0 + (x1 - x0) * (i + 1) / nx
            ya, yb = y0 + (y1 - y0) * j / ny, y0 + (y1 - y0) * (j + 1) / ny
            a, b, c, d = (xa, ya, 0), (xb, ya, 0), (xb, yb, 0), (xa, yb, 0)
            alternate = flip and (i + j) % 2 == 1
            triangles = ((a, b, d), (b, c, d)) if alternate else ((a, b, c), (a, c, d))
            faces.extend((list(tri), color, component) for tri in triangles)
    return faces


def card(title, faces, width=480, height=320, label_lines=(), id_prefix='case'):
    parts = [f'<rect width="{width}" height="{height}" fill="{BG}"/>',
             f'<text x="18" y="28" fill="{TEXT}" font-size="17">{escape(title)}</text>']
    for i, (data, color, component) in enumerate(visible_regions(faces)):
        ident = ''.join(ch if ch.isalnum() or ch in '-_' else '-' for ch in component)
        parts.append(f'<!-- depth-visible fill for semantic component {escape(component)} -->')
        parts.append(f'<path id="{id_prefix}-{ident}-fill-{i}" d="{data}" fill="{color}" '
                     'fill-rule="nonzero"/>')
    for i, (text, x, y) in enumerate(label_lines):
        parts.append(f'<!-- diagnostic note {i + 1} -->')
        parts.append(f'<text x="{x}" y="{y}" fill="{TEXT}" font-size="13">'
                     f'{escape(text)}</text>')
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d">%s</svg>' % (
        width, height, ''.join(parts))


def retessellation_case():
    faces = grid_rect(32, 70, 224, 276, 1, 1, 'coarse-sheet', GREEN)
    faces += grid_rect(256, 70, 448, 276, 8, 6, 'fine-sheet', GREEN, flip=True)
    return card('Adjacent faces / alternate subdivision', faces, label_lines=(
        ('2 triangles', 80, 298), ('96 triangles', 320, 298)),
        id_prefix='retessellation')


def partial_occlusion_case():
    back = [([(42, 68, 0), (438, 68, 0), (438, 272, 0)], GREEN, 'far-sheet'),
            ([(42, 68, 0), (438, 272, 0), (42, 272, 0)], GREEN, 'far-sheet')]
    front = [([(160, 92, 1), (326, 146, 1), (206, 252, 1)], ROSE, 'near-occluder')]
    return card('Partial occlusion / real silhouette and background edges', back + front,
                id_prefix='partial-occlusion')


def depth_flip_case():
    # Both source faces have the exact same projected triangle; only depth differs.
    flat = ([(60, 72, 0), (420, 72, 0), (60, 276, 0)], ROSE, 'flat-surface')
    slope = ([(60, 72, -1), (420, 72, 1), (60, 276, -1)], BLUE, 'depth-flipping-strip')
    result_cards = []
    for order, prefix, title in (
            ([flat, slope], 'depth-flat-first', 'Visible result / flat first'),
            ([slope, flat], 'depth-slope-first', 'Visible result / slope first')):
        faces = []
        for tri, color, name in order:
            points = [((x - 60) * .42 + 26, (y - 72) * .68 + 74, z)
                      for x, y, z in tri]
            faces.append((points, color, name))
        rendered = card(title, faces, width=210, height=270,
                        label_lines=(('depth winner changes at center', 12, 255),),
                        id_prefix=prefix)
        body = rendered.split('>', 1)[1].rsplit('</svg>', 1)[0]
        result_cards.append(f'<svg x="{210 + 220 * len(result_cards)}" y="40" '
                            f'width="210" height="270" viewBox="0 0 210 270">{body}</svg>')

    source_outline = 'M 28 78 L 176 78 L 28 222 Z'
    parts = [
        f'<rect width="640" height="320" fill="{BG}"/>',
        '<text x="18" y="28" fill="#e6edf1" font-size="17">Depth flip / source overlap and visible result</text>',
        '<text x="12" y="51" fill="#e6edf1" font-size="12">INPUT DIAGNOSTIC ONLY</text>',
        '<text x="12" y="67" fill="#e6edf1" font-size="12">same x/y outline</text>',
        '<!-- flat source outline and translucent fill, z=0 across the face -->',
        f'<path id="depth-source-flat" d="{source_outline}" fill="{ROSE}" fill-opacity="0.38" '
        f'stroke="{ROSE}" stroke-width="2"/>',
        '<!-- sloped source has the exact same projected triangle, depth -1 to +1 -->',
        f'<path id="depth-source-slope" d="{source_outline}" fill="{BLUE}" fill-opacity="0.38" '
        f'stroke="{BLUE}" stroke-width="2" stroke-dasharray="7 4"/>',
        '<!-- equality boundary at the source footprint midpoint; this is diagnostic annotation -->',
        '<path id="depth-source-equality" d="M 102 78 L 102 148" fill="none" '
        'stroke="#f4f1d0" stroke-width="1.5" stroke-dasharray="3 3"/>',
        f'<text x="12" y="246" fill="{ROSE}" font-size="12">flat z = 0</text>',
        f'<text x="12" y="263" fill="{BLUE}" font-size="12">sloped z: −1 → +1</text>',
        '<text x="12" y="285" fill="#e6edf1" font-size="11">diagnostic overlay, not output</text>',
        *result_cards,
    ]
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 320">%s</svg>' % ''.join(parts)


def tie_and_self_case():
    tie_a = ([(24, 88, 0), (145, 88, 0), (24, 244, 0)], GREEN, 'first-coplanar-face')
    tie_b = ([(24, 88, 0), (145, 88, 0), (24, 244, 0)], BLUE, 'second-coplanar-face')
    tangent_left = ([(174, 88, 0), (246, 88, 0), (174, 244, 0)], GREEN, 'tangent-left')
    tangent_right = ([(246, 88, 0), (246, 244, 0), (174, 244, 0)], BLUE, 'tangent-right')
    self_near = ([(294, 88, 1), (450, 88, 1), (294, 244, 1)], ROSE, 'one-self-overlap')
    self_far = ([(294, 88, 0), (450, 88, 0), (294, 244, 0)], BLUE, 'one-self-overlap')
    return card('Coplanar tie / edge tangency / same-component self-occlusion',
                [tie_a, tie_b, tangent_left, tangent_right, self_far, self_near],
                label_lines=(('tie: first wins', 20, 286),
                             ('edge touch: both', 169, 286),
                             ('depth: near wins', 319, 286)),
                id_prefix='tie-self')


def strip_faces(yaw, pitch, scale=105):
    yaw_angle, pitch_angle = math.radians(yaw), math.radians(pitch)
    yaw_cos, yaw_sin = math.cos(yaw_angle), math.sin(yaw_angle)
    pitch_cos, pitch_sin = math.cos(pitch_angle), math.sin(pitch_angle)

    def project(point):
        x, y, z = point
        horizontal = x * yaw_cos + z * yaw_sin
        depth = z * yaw_cos - x * yaw_sin
        screen_vertical = y * pitch_cos - depth * pitch_sin
        camera_depth = depth * pitch_cos + y * pitch_sin
        return (280 + scale * horizontal, 170 - scale * screen_vertical, camera_depth)

    n = 24
    faces = []
    def point(step, v):
        t = 2 * math.pi * step / n
        return (math.cos(t) + v * .12 * math.cos(t),
                .12 * math.sin(2 * t), math.sin(t) + v * .12 * math.sin(t))
    for i in range(n):
        for lo, hi, color in ((-1, -.3, ROSE), (-.3, .3, PALE), (.3, 1, ROSE)):
            a, b, c, d = point(i, lo), point(i + 1, lo), point(i + 1, hi), point(i, hi)
            faces.extend(([project(p) for p in tri], color, 'one-uncut-striped-strip')
                         for tri in ((a, b, c), (a, c, d)))
    body = [((-0.7, -.5, .55), (.7, -.5, .55), (.7, .5, .55)),
            ((-.7, -.5, .55), (.7, .5, .55), (-.7, .5, .55))]
    faces.extend(([project(p) for p in tri], GREEN, 'body-occluder') for tri in body)
    return faces


def two_view_case():
    parts = ['<rect width="1120" height="320" fill="%s"/>' % BG]
    views = (
        (0, 0, '0° yaw / 0° pitch — front, edge-on',
         'Rose strip z=+1 is in front of green body z=.55; z=−1 is behind.'),
        (55, 35, '55° yaw / 35° pitch — width view',
         'Green body hides far arc; pitch shows rose strip width, same geometry.'),
    )
    for index, (yaw, pitch, title, caption) in enumerate(views):
        rendered = card(title, strip_faces(yaw, pitch), width=560, height=320,
                        label_lines=((caption, 12, 302),),
                        id_prefix=f'strip-yaw-{yaw}-pitch-{pitch}')
        body = rendered.split('>', 1)[1].rsplit('</svg>', 1)[0]
        ox = index * 560
        parts.append(f'<svg x="{ox}" y="0" width="560" height="320" viewBox="0 0 560 320">'
                     f'{body}</svg>')
    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1120 320">%s</svg>' % ''.join(parts)


CASES = {
    'retessellation': retessellation_case,
    'partial-occlusion': partial_occlusion_case,
    'depth-flip-order': depth_flip_case,
    'tie-self-occlusion': tie_and_self_case,
    'two-view-strip': two_view_case,
}


def ensure_unique_ids(svg):
    root = ET.fromstring(svg)
    ids = [element.attrib['id'] for element in root.iter() if 'id' in element.attrib]
    duplicates = sorted({identifier for identifier in ids if ids.count(identifier) > 1})
    if duplicates:
        raise ValueError(f'diagnostic board contains duplicate SVG ids: {duplicates}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-o', '--output', type=Path, required=True)
    parser.add_argument('--cases-dir', type=Path, required=True)
    args = parser.parse_args()
    args.cases_dir.mkdir(parents=True, exist_ok=True)
    results = {}
    for name, make in CASES.items():
        path = args.cases_dir / f'{name}.svg'
        path.write_text(make(), encoding='utf-8')
        results[name] = path
    cells = []
    placements = ((0, 0, 480, 320), (480, 0, 480, 320), (960, 0, 640, 320),
                  (0, 320, 480, 320), (480, 320, 1120, 320))
    for (name, path), (x, y, width, height) in zip(results.items(), placements):
        cells.append(f'<svg x="{x}" y="{y}" width="{width}" height="{height}" '
                     f'viewBox="0 0 {width} {height}">{path.read_text(encoding="utf-8").split(">", 1)[1].rsplit("</svg>", 1)[0]}</svg>')
    board = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 640">'
             '<rect width="1600" height="640" fill="#101820"/>' + ''.join(cells) + '</svg>')
    ensure_unique_ids(board)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(board, encoding='utf-8')
    print(f'board={args.output}')
    for name, path in results.items():
        print(f'case={path}')


if __name__ == '__main__':
    main()
