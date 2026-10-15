"""Independent pixel-centre/triangle check of one fixed fine-grid arch, not an art verdict."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from ribbon_family import Camera, RibbonSpec, project
import ribbon_surface as surface

plan_path = ROOT / '.scratch/21-ribbon-cross-section/work/cases-fine.json'
plan = json.loads(plan_path.read_text())
case = next(c for c in plan['cases'] if c['ribbon']['name'] == 'teaching-arch')
spec, camera = RibbonSpec.from_mapping(case['ribbon']), Camera(**case['camera'])
flat = surface.build_surface(spec, 0, 96, 12)
curved = surface.build_surface(spec, .35, 96, 12)
w, h = 480, 320
scale, ox, oy = surface._projected_fit((flat, curved), camera, w, h)
z = np.full((h, w), -np.inf)
u = np.full((h, w), np.nan)
v = np.full((h, w), np.nan)
for triangle in curved.triangles:
    p = np.array([project(q, camera) for q in triangle.points])
    p[:, 0] = ox + scale * p[:, 0]
    p[:, 1] = oy - scale * p[:, 1]
    a, b, c = p
    matrix = np.column_stack((b[:2] - a[:2], c[:2] - a[:2]))
    if abs(np.linalg.det(matrix)) < 1e-10:
        continue
    left, right = max(0, int(np.floor(p[:, 0].min()))), min(w, int(np.ceil(p[:, 0].max())))
    top, bottom = max(0, int(np.floor(p[:, 1].min()))), min(h, int(np.ceil(p[:, 1].max())))
    yy, xx = np.mgrid[top:bottom, left:right]
    if not xx.size:
        continue
    weights = np.linalg.inv(matrix) @ np.stack((xx.ravel() + .5 - a[0], yy.ravel() + .5 - a[1]))
    wb, wc = weights.reshape(2, *xx.shape)
    wa = 1 - wb - wc
    depth = wa * a[2] + wb * b[2] + wc * c[2]
    nearer = (wa >= -1e-9) & (wb >= -1e-9) & (wc >= -1e-9) & (depth > z[top:bottom, left:right])
    uv = np.array(triangle.uv)
    z[top:bottom, left:right][nearer] = depth[nearer]
    u[top:bottom, left:right][nearer] = (wa * uv[0, 0] + wb * uv[1, 0] + wc * uv[2, 0])[nearer]
    v[top:bottom, left:right][nearer] = (wa * uv[0, 1] + wb * uv[1, 1] + wc * uv[2, 1])[nearer]
# Stay away from semantic outer boundaries and the stripe, but NOT from internal mesh edges.
safe = np.isfinite(z) & (u > .1) & (u < .9) & (np.abs(v) < .75) & (np.abs(v) > .3)
image_path = ROOT / '.scratch/21-ribbon-cross-section/evidence/fine/panels/case-04-untwisted-teaching-arch-front-control-camber-035.png'
pixels = np.array(Image.open(image_path).convert('RGB')).astype(np.int16)
expected = np.array([int(spec.front[i:i+2], 16) for i in (1, 3, 5)])
deviation = np.max(np.abs(pixels - expected), axis=2)
background = np.array([244, 245, 239])
background_like = np.max(np.abs(pixels - background), axis=2) <= 3
bad = safe & (deviation > 12)
coords = np.argwhere(bad)
result = {'scope': 'fixed untwisted fine arch, base-fill interior away from true boundaries; no image-quality judgment',
          'plan_sha256': hashlib.sha256(plan_path.read_bytes()).hexdigest(),
          'image_sha256': hashlib.sha256(image_path.read_bytes()).hexdigest(),
          'safe_pixels': int(safe.sum()), 'nonmatching_base_pixels': int(bad.sum()),
          'background_like_interior_pixels': int((safe & background_like).sum()),
          'first_nonmatches': [{'x': int(x), 'y': int(y), 'rgb': pixels[y, x].tolist(), 'u': float(u[y, x]), 'v': float(v[y, x])} for y, x in coords[:12]]}
out = ROOT / '.scratch/21-ribbon-cross-section/evidence/fine/parent-raster-probe.json'
out.write_text(json.dumps(result, indent=2) + '\n')
# Separate raw surface coverage from resolver clipping, with exactly the same generated geometry.
from draw import render
from vector_visibility import _compound_path, visible_regions
projected = []
for triangle in curved.triangles:
    points = [project(q, camera) for q in triangle.points]
    projected.append(([(ox + scale * q[0], oy - scale * q[1], q[2]) for q in points], spec.front, spec.name))
conditions = {
    'raw-monochrome': [_compound_path([tri for tri, _, _ in projected])],
    'depth-monochrome': [path for path, _, _ in visible_regions(projected)],
}
checks = {}
for label, paths in conditions.items():
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">'
           f'<rect width="{w}" height="{h}" fill="#f4f5ef"/>'
           + ''.join(f'<path d="{path}" fill="{spec.front}" fill-rule="nonzero"/>' for path in paths)
           + '</svg>')
    destination = out.parent / ('parent-' + label + '.svg')
    destination.write_text(svg)
    raster_path = destination.with_suffix('.png')
    render(str(destination), str(raster_path), size=(w, h))
    raster = np.array(Image.open(raster_path).convert('RGB')).astype(np.int16)
    checks[label] = {'nonmatching_base_pixels': int((safe & (np.max(np.abs(raster - expected), axis=2) > 12)).sum()),
                     'background_like_interior_pixels': int((safe & (np.max(np.abs(raster - background), axis=2) <= 3)).sum()),
                     'svg_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
                     'png_sha256': hashlib.sha256(raster_path.read_bytes()).hexdigest()}
result['source_vs_depth_monochrome'] = checks
out.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
