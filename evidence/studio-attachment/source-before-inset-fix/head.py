"""The accepted flat frontal head preset, compiled from editable semantic controls.

Host-relative recipes reuse the existing face/eye families. Same-material front
hair is fused; its child gestures remain editable. No image is opened.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
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
from scripts.studio.geometry import bounds, lock_rows, mix, outline, resolve_root
from scripts.studio.render import tone_region


def build_spec(eye_scale=1, jaw=.42, canvas=(640,640), center=None, length=.55, width=.79,
               expression='gentle',gaze=0):
    # Head framing is a composition choice. All face parts derive from this host.
    ink, skin = "#493b40", "#f1d1b9"
    center = center or (canvas[0]*.5,canvas[1]*.44)
    spec=dict(frame=dict(w=canvas[0], h=canvas[1]), layers=["paper", "neck", "ears", "face", "features"], vars={
        "head_h": min(canvas)*length, "head_w": f"head_h*{width}"}, draw=[
        {"rect": "paper", "full": True, "fill": "#f5eee4", "z": "paper", "desc": "warm quiet paper field"},
        {"face": "head", "at": list(center), "rx": "head_w*.5", "ry": "head_h*.5",
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
         "gaze": 2*gaze, "iris-top-fill": "#68483f", "iris-bot-fill": "#b78767", "lash-fill": ink,
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
    if expression not in ('gentle','neutral','smile','curious'):
        raise ValueError('expression: gentle/neutral/smile/curious')
    if expression!='gentle':
        parts={n.get('stroke'):n for n in spec['draw'] if 'stroke' in n}
        eyes={n.get('eye'):n for n in spec['draw'] if 'eye' in n}
        if expression=='smile':
            eyes['eye-left'].update({'lower-lid':.4})
        elif expression=='curious':
            eyes['eye-left'].update({'upper-lid':1.4,'lower-lid':1.2})
            eyes['eye-right'].update({'upper-lid':.96,'lower-lid':.96})
        mouth={
            'neutral':((-.065,.70),(0,.70),(.065,.70)),
            'smile':((-.105,.655),(0,.76),(.105,.655)),
            'curious':((-.055,.70),(0,.71),(.065,.675)),
        }[expression]
        parts['mouth']['spine']=[[f'head.cx+head.w*{x}',f'head.cy+head.ry*{y}'] for x,y in mouth]
        parts['mouth']['desc']='a '+expression+' closed-mouth gesture derived from the face ruler'
        brows={
            'neutral':((-.075,-.08,-.075),(-.075,-.08,-.075)),
            'smile':((-.095,-.145,-.095),(-.095,-.145,-.095)),
            'curious':((-.13,-.22,-.15),(-.055,-.085,-.06)),
        }[expression]
        for side,xs,ys in zip(('left','right'),((-.38,-.24,-.12),(.12,.24,.38)),brows):
            parts['brow-'+side]['spine']=[[f'head.cx+head.w*{x}',f'head.cy+head.ry*{y}'] for x,y in zip(xs,ys)]
            parts['brow-'+side]['desc']='the '+side+' brow in a '+expression+' expression'
    return spec


def add_bob(nodes, anchors, layers, side_part=False, canvas=(640,640), hair_edits=None):
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
                    at=dict(anchor="upper_center", offset=[root[0] / canvas[0] - .5, root[1] / canvas[1] - .12]),
                    length=ry * 1.34 / min(canvas), width=.20, angle=sign * 8, sweep=sign * .025,
                    width_side=side)
        if hair_edits and hair_edits.get(side):
            node['edits'] = hair_edits[side]
        lock_specs.append(node)
        rows = lock_rows(node, canvas)
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


def compile_recipe(eye_scale=1, jaw=.42, hair="side-part", canvas=(640,640), center=None,
                   length=.55, width=.79, hair_edits=None, palette=None,expression='gentle',gaze=0):
    spec = build_spec(eye_scale, jaw, canvas, center, length, width,expression,gaze)
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
    locks = add_bob(nodes, anchors, spec['layers'], hair == 'side-part', canvas, hair_edits) if hair != 'none' else []
    if palette:
        def darken(value, amount):
            return '#' + ''.join(f'{round(int(value[i:i+2],16)*amount):02x}' for i in (1,3,5))
        replacements = {}
        if 'hair' in palette:
            replacements.update({'#517f9b':palette['hair'], '#426781':palette.get('shade',darken(palette['hair'],.82)),
                                 '#36566f':darken(palette['hair'],.65), '#3e647e':darken(palette['hair'],.78),
                                 '#263c50':palette.get('ink',darken(palette['hair'],.50))})
        if 'skin' in palette:
            replacements.update({'#f1d1b9':palette['skin'],'#b17a68':darken(palette['skin'],.65)})
        if 'iris' in palette:
            replacements.update({'#b78767':palette['iris'],'#68483f':darken(palette['iris'],.62)})
        if 'ink' in palette:
            replacements.update({'#493b40':palette['ink'],'#263c50':palette['ink']})
        if 'shade' in palette:
            replacements['#426781']=palette['shade']
        for part in nodes:
            for key in ('fill','stroke','ink'):
                if part.get(key) in replacements:
                    part[key]=replacements[part[key]]
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
    return dict(root=root, nodes=nodes, spec=spec, anchors=anchors, locks=locks, envelope=envelope)


def generate(directory, eye_scale=1, jaw=.42, hair="none", svg_only=False):
    """Reproduce the original probe and its diagnostic inputs."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    data=compile_recipe(eye_scale,jaw,hair)
    root,spec,anchors,locks=[data[k] for k in ('root','spec','anchors','locks')]
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


def _sample_path(d):
    """Sample only the M/L/Q/C/Z vocabulary emitted by this recipe."""
    import re
    words=re.findall(r'[MLQCZ]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?',d)
    i=0; p=(0.,0.); start=p; points=[]
    while i<len(words):
        command=words[i];i+=1
        count={'M':2,'L':2,'Q':4,'C':6,'Z':0}.get(command)
        if count is None:
            raise ValueError('unsupported compiled head path command')
        values=list(map(float,words[i:i+count]));i+=count
        if command=='M':
            p=tuple(values);start=p;points.append(p)
        elif command=='L':
            p=tuple(values);points.append(p)
        elif command in ('Q','C'):
            controls=[p]+list(zip(values[::2],values[1::2]))
            steps=max(2,min(32,math.ceil(sum(math.dist(a,b) for a,b in zip(controls,controls[1:]))/8)))
            for j in range(1,steps+1):
                t=j/steps
                if command=='Q':
                    a,b,c=controls
                    points.append(tuple((1-t)**2*a[k]+2*(1-t)*t*b[k]+t*t*c[k] for k in (0,1)))
                else:
                    a,b,c,e=controls
                    points.append(tuple((1-t)**3*a[k]+3*(1-t)**2*t*b[k]+3*(1-t)*t*t*c[k]+t**3*e[k] for k in (0,1)))
            p=controls[-1]
        else:
            p=start
    if len(points)>1 and math.dist(points[0],points[-1])<1e-8:
        points.pop()
    return points


def rotate_point(point, center, angle):
    a=math.radians(-angle);dx=point[0]-center[0];dy=point[1]-center[1]
    return (center[0]+dx*math.cos(a)-dy*math.sin(a),center[1]+dx*math.sin(a)+dy*math.cos(a))


@dataclass(frozen=True)
class HeadData:
    svg: str
    outline: tuple
    features: dict
    locks: dict
    center: tuple
    angle: float


def head_data(node, canvas):
    return _head_data(json.dumps(node,sort_keys=True),tuple(canvas))


@lru_cache(maxsize=32)
def _head_data(encoded, canvas):
    node=json.loads(encoded)
    placement=node.get('at',{'anchor':'center','offset':[0,-.06]})
    placement={'anchor':'center'}|placement
    center=resolve_root({'at':placement},canvas)
    angle=node.get('angle',0)
    data=compile_recipe(node.get('eye_scale',1),node.get('jaw',.42),node.get('hair','side-part'),
                        canvas,center,node.get('length',.55),node.get('width',.79),
                        node.get('hair_edits'),node.get('palette'),node.get('expression','gentle'),node.get('gaze',0))
    root=data['root']
    by_id={el.get('id'):el for el in root if el.get('id')}
    from shapely import Polygon, union_all
    from shapely.affinity import rotate
    opaque=[]
    for sid in ('head-contour','bob-back','hair-front-union'):
        if sid in by_id:
            opaque.append(Polygon(_sample_path(by_id[sid].get('d'))))
    for part in data['nodes']:
        if part.get('ellipse','').startswith('ear-'):
            cx,cy=part['at']
            opaque.append(Polygon([(cx+part['rx']*math.cos(i*math.tau/48),cy+part['ry']*math.sin(i*math.tau/48)) for i in range(48)]))
    # Include outer contour ink in this flat component's opaque support footprint.
    footprint=union_all(opaque).buffer(2,quad_segs=2).simplify(.04,preserve_topology=True)
    if footprint.geom_type!='Polygon' or footprint.interiors or not footprint.is_valid:
        raise ValueError('head silhouette must remain one valid connected region')
    if angle:
        footprint=rotate(footprint,-angle,origin=center)
    outer=tuple(footprint.exterior.coords)[:-1]
    transform=f'rotate({-angle} {center[0]} {center[1]})' if angle else ''
    features={}
    controls={'eyes':['eye_scale','iris_color','gaze'], 'face':['jaw','skin_color'], 'hair':['hair','hair_color'],
              'expression':['expression'],
              'object':['intent','expression','gaze','eye_scale','jaw','hair','length','width','angle','depth','depth_slope','hair_color','skin_color','iris_color','ink_color']}
    eye_marks=['eye-left-sclera','eye-right-sclera','eye-left-lash','eye-right-lash']
    for name,ids in (('eyes',eye_marks),('face',['head-contour']),('hair',['hair-front-union']),
                     ('expression',['brow-left','brow-right','mouth']+eye_marks)):
        paths=[];pts=[]
        for sid in ids:
            if sid in by_id:
                d=by_id[sid].get('d')
                paths.append(dict(d=d,transform=transform))
                pts.extend(rotate_point(p,center,angle) for p in _sample_path(d))
        if pts:
            features[name]=dict(paths=paths,bounds=bounds(pts),controls=controls[name])
    features['object']=dict(paths=[dict(d=path(outer),transform='')],bounds=bounds(outer),controls=controls['object'])
    locks={}
    for lock in data['locks']:
        side=lock['id'].split('-')[-1]
        locks[side]=dict(node=lock,rows=lock_rows(lock,canvas))
    # A nested component never paints its paper over neighboring scene objects.
    paper=by_id.get('paper')
    if paper is not None:
        root.remove(paper)
    prefix=node['id']+'--'
    for el in root.iter():
        if el.get('id'):
            el.set('id',prefix+el.get('id'))
        for attr,value in list(el.attrib.items()):
            if 'url(#' in value:
                el.set(attr,value.replace('url(#','url(#'+prefix))
    if angle:
        group=ET.Element('{http://www.w3.org/2000/svg}g',transform=transform)
        for el in list(root):
            root.remove(el);group.append(el)
        root.append(group)
    return HeadData(ET.tostring(root,encoding='unicode'),outer,features,locks,center,angle)
