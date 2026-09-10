#!/usr/bin/env python3
"""Migrate portrait v20.svg -> scene.yaml (object-level nodes). One-shot converter."""
import re
import xml.etree.ElementTree as ET
import yaml

NS = '{http://www.w3.org/2000/svg}'
SRC = '.scratch/05-portrait-scene/work/v20.svg'
OUT = '.scratch/05-portrait-scene/work/scene-migrated.yaml'
OFF = (580.0, 150.0)   # face-group transform: translate + scale(0.5)


def bake(x: float, y: float) -> list[float]:
    return [OFF[0] + x * 0.5, OFF[1] + y * 0.5]


def path_pts(d: str, baked: bool) -> list[list[float]]:
    d = d.replace(',', ' ')
    pts: list[list[float]] = []
    cur = [0.0, 0.0]
    start = [0.0, 0.0]
    for m in re.finditer(r'([MLQCZmlqcz])([^MLQCZmlqcz]*)', d):
        cmd = m.group(1)
        rel = cmd.islower()
        up = cmd.upper()
        vals = [float(v) for v in m.group(2).split()]
        if up == 'Z':
            cur = list(start)
            continue
        n = len(vals)
        if up == 'M' or up == 'L':
            pairs = [(vals[i], vals[i+1]) for i in range(0, n-1, 2)]
        elif up == 'Q':
            pairs = [(vals[i], vals[i+1]) for i in range(2, n-1, 2)]
        elif up == 'C':
            pairs = [(vals[i], vals[i+1]) for i in range(4, n-1, 2)]
        else:
            pairs = [(vals[i], vals[i+1]) for i in range(0, n-1, 2)]
        for px, py in pairs:
            x, y = (cur[0]+px, cur[1]+py) if rel else (px, py)
            if up == 'M' and not rel:
                start = [x, y]
            pts.append(bake(x, y) if baked else [x, y])
            cur = [x, y]
    return pts


def fill_of(el: ET.Element) -> str:
    f = el.get('fill') or '#888888'
    if f.startswith('url(#'):
        return 'grad:' + f.split('#')[1].rstrip(')')
    return f


nodes: list[dict] = [{"layers": ["bg", "ribbon", "skirt", "body", "overlays", "face", "hair", "arms", "hat"]}]

src = open(SRC).read()
root = ET.parse(SRC).getroot()

# gradients -> grad nodes
for lg in re.finditer(r'<linearGradient id="([^"]+)" x1="([^"]+)" y1="([^"]+)" x2="([^"]+)" y2="([^"]+)"(.*?)</linearGradient>', src, re.S):
    name, x1, y1, x2, y2, body = lg.groups()
    stops = re.findall(r'<stop offset="([^"]+)" stop-color="([^"]+)"/>', body)
    nodes.append({"grad": name, "dir": [float(x1), float(y1), float(x2), float(y2)],
                  "stops": [[float(o), c] for o, c in stops]})

# z-map by element id
ZMAP = {
    "bg-sky": "bg",
    "ribbon-body": "ribbon", "ribbon-tail": "ribbon", "ribbon-white": "ribbon", "ribbon-tealband": "ribbon",
    "skirt-underlayer": "skirt", "skirt-light-body": "skirt", "skirt-band-left": "skirt",
    "skirt-hem-solid": "skirt", "skirt-band-bottom": "skirt", "skirt-band-right": "skirt",
    "skirt-folds": "skirt", "skirt-folds2": "skirt", "hem-underlayer": "skirt", "overskirt": "skirt",
    "blouse": "body", "blouse-wrinkles": "body", "jabot": "body", "jabot-stripe": "body",
    "jabot-folds": "body", "sleeve-left": "body", "sleeve-right": "body", "sleeve-gathers": "body",
    "collar-ext": "body", "collar-trim": "body", "bow-tail": "body", "bow-tail-fold": "body",
    "bow-wing-l": "body", "bow-wing-r": "body", "bow-knot": "body",
    "cuff-left": "arms", "arm-left": "arms", "cuff-right": "arms", "arm-right": "arms",
    "hand": "arms", "fingers": "arms",
    "green-behind": "overlays", "green-overlay": "overlays", "pink-overlay": "overlays",
    "yellow-overlay": "overlays", "pink-ring": "overlays", "pink-flower": "overlays",
    "arm-shadow-tint": "overlays",
    "skin": "face", "skin-shadow-cheek": "face", "nose": "face", "mouth": "face",
    "pink-pocket-1": "face", "pink-pocket-2": "face",
    "eyeL-sclera": "face", "eyeL-lid-band": "face", "eyeL-iris": "face", "eyeL-green": "face",
    "eyeL-glint": "face", "eyeL-dot1": "face", "eyeL-dot2": "face", "eyeL-outline": "face",
    "eyeL-lash-top": "face", "eyeL-lower-ticks": "face",
    "eyeR-sclera": "face", "eyeR-lid-band": "face", "eyeR-iris": "face", "eyeR-green": "face",
    "eyeR-glint": "face", "eyeR-dot1": "face", "eyeR-outline": "face", "eyeR-lash-top": "face",
    "eyeR-lash-spikes": "face", "eyeR-lower-ticks": "face",
    "brow-left": "face", "brow-right": "face",
    "hair-top": "hair", "hair-thin-lines": "hair", "hair-eye-strand": "hair", "hair-right": "hair",
    "hair-right-edge": "hair", "hair-curl": "hair", "hair-lines": "hair",
    "bangs-top-filler": "hair", "curtain-filler": "hair", "right-wall-strands": "hair",
    "curtain": "hair", "wing-strand": "hair", "curtain-flow": "hair",
    "brim-underside": "hat", "hat-dome": "hat", "hat-dome-band": "hat", "brim-band": "hat",
    "brim-teal-rim": "hat", "pom-1": "hat", "pom-2": "hat", "brim-edges": "hat",
}

nid_counter = 0
seen_ids: set[str] = set()


def unique(eid: str, tag: str) -> str:
    global nid_counter
    base = eid or f"{tag}-{nid_counter}"
    nid = base
    while nid in seen_ids:
        nid_counter += 1
        nid = f"{base}-{nid_counter}"
    seen_ids.add(nid)
    return nid


def emit(el: ET.Element, baked: bool, group_z: str | None):
    global nid_counter
    tag = el.tag.split('}')[-1]
    eid = el.get('id') or ''
    if tag in ('g', 'desc', 'linearGradient', 'filter', 'defs', 'svg'):
        return
    z = ZMAP.get(eid, group_z or 'body')
    fill = fill_of(el)
    op = el.get('opacity')
    stroke = el.get('stroke')
    sw = el.get('stroke-width')
    filt = el.get('filter') or ''

    if tag in ('ellipse', 'circle'):
        cx_s, cy_s = el.get('cx'), el.get('cy')
        rx_s = el.get('rx') or el.get('r') or '1'
        ry_s = el.get('ry') or el.get('r') or '1'
        if cx_s is None or cy_s is None:
            return
        cx, cy = float(cx_s), float(cy_s)
        rx, ry = float(rx_s), float(ry_s)
        if baked:
            cx, cy = OFF[0] + cx * 0.5, OFF[1] + cy * 0.5
            rx, ry = rx * 0.5, ry * 0.5
        kw: dict = {"at": [round(cx, 1), round(cy, 1)], "rx": round(rx, 1), "ry": round(ry, 1), "fill": fill, "z": z}
        tr = el.get('transform')
        if tr:
            mm = re.search(r'rotate\(([-\d.]+)', tr)
            if mm:
                kw["rot"] = float(mm.group(1))
        if op:
            kw["op"] = float(op)
        if stroke:
            kw["stroke"] = stroke
            kw["sw"] = (float(sw or 3) * 0.5) if baked else float(sw or 3)
        nodes.append({"ellipse": unique(eid, 'ellipse'), **kw})
        nid_counter += 1
        return
    if tag == 'rect':
        nodes.append({"rect": unique(eid or 'bg-sky', 'rect'), "full": True, "fill": fill, "z": "bg"})
        nid_counter += 1
        return
    if tag != 'path':
        return
    d = el.get('d')
    if not d:
        return
    pts = path_pts(d, baked)
    if len(pts) < 2:
        return
    nid_counter += 1
    is_stroke_only = fill in ('none', '')
    if is_stroke_only and stroke:
        kw = {"stroke": unique(eid, 'stroke'), "spine": pts, "ink": stroke, "z": z}
        if sw:
            kw["w"] = (float(sw) * 0.5) if baked else float(sw)
        if op:
            kw["op"] = float(op)
        nodes.append(kw)
        return
    kw = {"blob": unique(eid, 'blob'), "poly": pts, "fill": fill, "z": z}
    if op:
        kw["op"] = float(op)
    if stroke:
        kw["stroke"] = stroke
        kw["sw"] = (float(sw or 3) * 0.5) if baked else float(sw or 3)
    if filt or 'overlay' in eid:
        kw["blur"] = 6
    nodes.append(kw)


for top in root:
    tag = top.tag.split('}')[-1]
    gid = top.get('id') or ''
    if tag == 'g' and gid == 'face-group':
        for el in top.iter():
            emit(el, baked=True, group_z='face')
    elif tag == 'g':
        gz = ZMAP.get(gid, 'body')
        for el in top.iter():
            if el is not top:
                emit(el, baked=False, group_z=gz)
    elif tag == 'path':
        emit(top, baked=False, group_z='body')

yaml_text = yaml.dump(nodes, allow_unicode=True, default_flow_style=None, width=1200, sort_keys=False)
open(OUT, 'w').write(yaml_text)
print("nodes:", len(nodes))
