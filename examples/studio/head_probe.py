"""A clean head context: reuse legacy face/eye construction before expanding studio.

This probe is deliberately outside the production node catalog. A visually weak
macro is not promoted just because it has a high-level name. Fractions below are
stylized drawing choices, not measurements of image.jpg. No image is opened.
"""
from __future__ import annotations

import argparse
import hashlib
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT))

import cv2
import numpy as np
import relate
from scripts.studio.model import write
from scripts.studio.render import rasterize, path
from scripts.studio.geometry import lock_rows, mix, outline
from scripts.studio.render import tone_region


def build_spec(eye_scale=1, jaw=.42):
    # Head framing is a composition choice. All face parts derive from this host.
    ink, skin = "#493b40", "#f1d1b9"
    return dict(frame=dict(w=640, h=640), layers=["paper", "neck", "ears", "face", "features"], vars={
        "head_h": "frame.h*.55", "head_w": "head_h*.79"}, draw=[
        {"rect": "paper", "full": True, "fill": "#f5eee4", "z": "paper", "desc": "warm quiet paper field"},
        {"face": "head", "at": ["frame.w*.5", "frame.h*.44"], "rx": "head_w*.5", "ry": "head_h*.5",
         "cheek": .78, "jaw": jaw, "chin-w": .12, "fill": skin, "z": "face", "desc": "one stylized skull and tapered jaw"},
        {"blob": "neck", "spine": [["head.cx", "head.cy+head.ry*.76"], ["head.cx", "head.bottom+head.h*.20"]],
         "w": "head.w*.26", "fill": "#dfb39c", "z": "neck", "desc": "neck continuous behind the jaw"},
        {"ellipse": "ear-left", "at": ["head.cx-head.rx*.96", "head.cy+head.ry*.13"],
         "rx": "head.w*.065", "ry": "head.h*.09", "fill": skin, "stroke": ink, "sw": 2,
         "z": "ears", "desc": "left ear partly covered by the face"},
        {"ellipse": "ear-right", "at": ["head.cx+head.rx*.96", "head.cy+head.ry*.13"],
         "rx": "head.w*.065", "ry": "head.h*.09", "fill": skin, "stroke": ink, "sw": 2,
         "z": "ears", "desc": "right ear partly covered by the face"},
        {"eye": "eye-left", "host": "head", "at": ["head.cx-head.w*.235", "head.cy+head.ry*.12"],
         "w": f"head.w*{.275*eye_scale}", "h": f"head.w*{.17*eye_scale}", "tilt": -3,
         "gaze": 0, "iris-top-fill": "#68483f", "iris-bot-fill": "#b78767", "lash-fill": ink,
         "iris-w": .24, "iris-h": .46,
         "line-w": .035, "glints": 1, "z": "features", "desc": "layered almond left eye"},
        {"eye": "eye-right", "host": "head", "mirror-of": "eye-left", "z": "features", "desc": "matching right eye"},
        {"stroke": "brow-left", "spine": [["head.cx-head.w*.38", "head.cy-head.ry*.06"],
                                                  ["head.cx-head.w*.24", "head.cy-head.ry*.10"],
                                                  ["head.cx-head.w*.12", "head.cy-head.ry*.07"]],
         "w": 3, "ink": ink, "z": "features", "desc": "soft left eyebrow following brow ridge"},
        {"stroke": "brow-right", "spine": [["head.cx+head.w*.12", "head.cy-head.ry*.07"],
                                                   ["head.cx+head.w*.24", "head.cy-head.ry*.10"],
                                                   ["head.cx+head.w*.38", "head.cy-head.ry*.06"]],
         "w": 3, "ink": ink, "z": "features", "desc": "soft right eyebrow"},
        {"stroke": "nose", "spine": [["head.cx", "head.cy+head.ry*.27"],
                                            ["head.cx-head.w*.025", "head.cy+head.ry*.46"],
                                            ["head.cx+head.w*.023", "head.cy+head.ry*.48"]],
         "w": 2.2, "ink": "#b17a68", "z": "features", "desc": "small nose plane turn and underside"},
        {"stroke": "mouth", "spine": [["head.cx-head.w*.065", "head.cy+head.ry*.69"],
                                             ["head.cx", "head.cy+head.ry*.715"],
                                             ["head.cx+head.w*.065", "head.cy+head.ry*.69"]],
         "w": 2.3, "ink": "#a4635e", "z": "features", "desc": "short relaxed closed smile"},
    ])


def add_bob(nodes, anchors, layers, side_part=False):
    """One cap organizes the roots; short subordinate locks emerge below it."""
    cx, cy, rx, ry = [anchors['head.' + k] for k in ('cx', 'cy', 'rx', 'ry')]
    layers[:] = ["paper", "hair-back", "neck", "ears", "face", "features", "hair-front", "cap"]
    # A bob ends as a haircut behind the jaw; it does not wrap under the chin.
    crown_y, cut_y = cy - ry * .22, cy + ry * .84
    anchors['hair.back-cut-y'] = cut_y
    rear = [(cx + rx * 1.18 * math.cos(math.pi + math.pi * i / 48),
             crown_y + ry * 1.08 * math.sin(math.pi + math.pi * i / 48)) for i in range(49)]
    rear += [(cx + rx * 1.18, cut_y), (cx - rx * 1.18, cut_y)]
    nodes.append(dict(blob="bob-back", poly=rear, fill="#426781", stroke="#263c50", sw=2.4, z="hair-back",
                      desc="one rear bob volume, with a cut behind the jaw rather than a band under the chin"))
    lock_specs = []
    members = []
    for side, sign in (("left", -1), ("right", 1)):
        root = (cx + sign * rx * .91, cy - ry * .32)
        node = dict(id="bob-" + side, kind="hair-lock", intent="a short temple lock emerging under the shared cap",
                    at=dict(anchor="upper_center", offset=[root[0] / 640 - .5, root[1] / 640 - .12]),
                    length=ry * 1.34 / 640, width=.20, angle=sign * 8, sweep=sign * .025,
                    width_side=side)
        lock_specs.append(node)
        rows = lock_rows(node, [640, 640])
        members.append(outline(rows))
        nodes.append(dict(blob=node['id'] + '-turn', poly=tone_region(rows, .12, .94, .7, 1),
                          fill="#426781", z="hair-front", desc="the lock's soft inward turn"))
        nodes.append(dict(stroke=node['id'] + '-strand', spine=[mix(r.left, r.right, .53) for r in rows if .15 < r.t < .9],
                          w=.8, ink="#36566f", z="hair-front", desc="one subordinate strand follows the short lock"))
    base_y = cy - ry * .18
    top = [(cx + rx * 1.14 * math.cos(math.pi + math.pi * i / 48),
            base_y + ry * 1.12 * math.sin(math.pi + math.pi * i / 48)) for i in range(49)]
    top[0], top[-1] = (cx-rx*1.14, base_y), (cx+rx*1.14, base_y)
    # Rounded asymmetric clump rhythm, generated across the same cap's underside.
    if side_part:
        # Four semantic stations define a side part and a long swept fringe.
        stations = [(-.98, -.08), (-.22, -.65), (.36, -.08), (1.10, -.08)]
        controls = [(-.70, -.20), (.08, -.18), (.85, -.02)]
        fringe = []
        for (a, b), c in zip(zip(stations, stations[1:]), controls):
            a, b, c = [(cx + u * rx, cy + v * ry) for u, v in (a, b, c)]
            fringe += [((1-t)**2*a[0] + 2*(1-t)*t*c[0] + t*t*b[0],
                        (1-t)**2*a[1] + 2*(1-t)*t*c[1] + t*t*b[1]) for t in (i/20 for i in range(21))]
        lower = list(reversed(fringe))
    else:
        lower = []
        for i in range(49):
            t = i / 48
            x = cx + rx * 1.14 * (1 - 2 * t)
            scallop = math.sin(math.pi * t) * (7 + 11 * math.sin(3 * math.pi * t + .3) ** 2)
            lower.append((x, base_y + scallop))
    members.append(top + lower)
    from shapely import Polygon, union_all, is_valid_reason
    pieces = [Polygon(p) for p in members]
    invalid = [(i,is_valid_reason(p)) for i,p in enumerate(pieces) if not p.is_valid]
    if invalid:
        raise ValueError('invalid authored hair member; refuse silent topology repair: '+str(invalid))
    fused = union_all(pieces)
    if fused.geom_type != 'Polygon' or fused.interiors:
        raise ValueError('front hair must be one connected region without accidental holes')
    contour = list(fused.exterior.coords)[:-1]
    # Fill goes before the derived tone regions; only the merged exterior is inked.
    front_start = next(i for i,n in enumerate(nodes) if n['z'] == 'hair-front')
    nodes.insert(front_start, dict(blob='hair-front-union', poly=contour, fill='#517f9b',
                                  stroke='#263c50', sw=2, z='hair-front',
                                  art_curve=True,
                                  desc='one fused cap/temple-lock contour; internal construction joins are not ink'))
    if side_part:
        part=(cx-rx*.22,cy-ry*.65)
        crown=(cx-rx*.22,base_y-ry*1.08)
        control=(cx-rx*.43,base_y-ry*.66)
        line=[((1-t)**2*part[0]+2*(1-t)*t*control[0]+t*t*crown[0],
               (1-t)**2*part[1]+2*(1-t)*t*control[1]+t*t*crown[1]) for t in (i/32 for i in range(33))]
        nodes.append(dict(stroke='hair-parting',spine=line,w=1.4,ink='#36566f',z='cap',
                          desc='one parting line actually joins the exposed fringe division to the crown direction'))
    # Strand fields stay subordinate to the unified mass. The new parting contour
    # is sufficient at this stage; decorative lines do not stand in for a hairstyle.
    for k, controls in enumerate(() if side_part else (
            ((-.30, -.88), (-.15, -.33), (.60, .04)),
            ((-.50, -.65), (-.50, -.25), (-.10, .08)))):
        a, b, c = [(cx + u * rx, base_y + v * ry) for u, v in controls]
        curve = [((1-t)**2*a[0] + 2*(1-t)*t*b[0] + t*t*c[0],
                  (1-t)**2*a[1] + 2*(1-t)*t*b[1] + t*t*c[1]) for t in (i/36 for i in range(37))]
        nodes.append(dict(stroke=f'bob-flow-{k}', spine=curve, w=1.5, ink='#3e647e', z='cap',
                          desc='a restrained comb-direction line from parting toward fringe, not a support edge'))
    return lock_specs


def generate(directory, eye_scale=1, jaw=.42, hair="none", svg_only=False):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    spec = build_spec(eye_scale, jaw)
    nodes, anchors, _notes, _layers = relate.resolve(spec)
    # A head-only preset ends at its silhouette. A neck without shoulders made
    # the first probe resemble a mannequin on a capsule pedestal.
    nodes = [n for n in nodes if n.get('blob') != 'neck']
    # The face family emits overlapping skull and jaw fill pieces. Their internal
    # construction seam is not an art line. A computed convex envelope supplies
    # one contour, appropriate to this frontal stylized head only.
    skull = next(n for n in nodes if n.get("ellipse") == "head-cranium")
    jaw_node = next(n for n in nodes if n.get("blob") == "head-jaw")
    cx, cy = skull["at"]
    points = [(cx + skull["rx"] * math.cos(i * math.tau / 96),
               cy + skull["ry"] * math.sin(i * math.tau / 96)) for i in range(96)] + jaw_node["poly"]
    envelope = cv2.convexHull(np.array(points, dtype=np.float32)).reshape(-1, 2).tolist()
    nodes = [n for n in nodes if n.get("ellipse") != "head-cranium" and n.get("blob") != "head-jaw"]
    nodes.append({"blob": "head-contour", "poly": envelope, "fill": "#f1d1b9", "stroke": "#493b40", "sw": 2.4, "art_curve": True,
                  "z": "face", "desc": "one computed outer skull/jaw envelope without an interior construction seam"})
    locks = add_bob(nodes, anchors, spec['layers'], hair == 'side-part') if hair != 'none' else []
    svg = relate.emit_svg(nodes, spec["layers"], spec["frame"])
    # The older emitter preserves intent comments but omits element IDs. Add
    # semantic names at this boundary without rebuilding its drawing algorithms.
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
    root = ET.fromstring(svg, parser=parser)
    ordered = [n for n in nodes if n.get("full")]
    ordered += sorted([n for n in nodes if not n.get("full")], key=lambda n: spec["layers"].index(n["z"]))
    elements = [el for el in root if el.tag is not ET.Comment]
    assert len(elements) == len(ordered)
    for el, node in zip(elements, ordered):
        kind = next(k for k in ("rect", "ellipse", "blob", "stroke") if k in node)
        el.set("id", node[kind])
        # Curve design is explicit: face/front hair are drawn smoothly; the rear
        # haircut preserves its computed corners. No projection edge is auto-ink.
        if kind == 'blob' and 'poly' in node and not node.get('art_curve'):
            el.set('d', path(node['poly']))
        elif kind == 'stroke' and len(node['spine']) > 4:
            el.set('d', path(node['spine'], False))
    # Old eye parts were free ellipses: catchlights escaped the almond aperture.
    # Containment belongs to the primitive, not to per-picture corrections.
    namespace = '{http://www.w3.org/2000/svg}'
    defs = ET.SubElement(root, namespace + 'defs')
    by_id = {el.get('id'): el for el in elements}
    for side in ('left', 'right'):
        sid = 'eye-' + side
        clip = ET.SubElement(defs, namespace + 'clipPath', id=sid + '-aperture', clipPathUnits='userSpaceOnUse')
        ET.SubElement(clip, namespace + 'path', d=by_id[sid + '-sclera'].get('d'))
        for suffix in ('iris-lo', 'iris-hi', 'pupil', 'glint1', 'glint2', 'refl'):
            if sid + '-' + suffix in by_id:
                by_id[sid + '-' + suffix].set('clip-path', 'url(#' + sid + '-aperture)')
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    svg = ET.tostring(root, encoding="unicode")
    (directory / "artwork.svg").write_text(svg, encoding="utf-8")
    write(directory / "inputs.json", dict(kind="head-probe", eye_scale=eye_scale, jaw=jaw, hair=hair))
    write(directory / "hair-locks.json", locks)
    write(directory / "spec.json", spec)
    write(directory / "anchors.json", anchors)
    binding = dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   scope="frontal head macro probe; no 3D or default-quality pass", status="svg-only")
    write(directory / "binding.json", binding)
    if not svg_only:
        binding['renderer'] = rasterize(directory / "artwork.svg", directory / "artwork.png")
        binding['png_sha256'] = hashlib.sha256((directory / "artwork.png").read_bytes()).hexdigest()
        binding['status'] = 'rendered-unreviewed'
        write(directory / "binding.json", binding)
    return directory


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--eye-scale", type=float, default=1)
    parser.add_argument("--jaw", type=float, default=.42)
    parser.add_argument("--hair", choices=('none', 'bob', 'side-part'), default='none')
    parser.add_argument("--svg-only", action='store_true')
    args = parser.parse_args()
    print(generate(args.outdir, args.eye_scale, args.jaw, args.hair, args.svg_only))
