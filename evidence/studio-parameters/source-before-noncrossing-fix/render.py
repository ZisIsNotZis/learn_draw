"""Compile editable parts through existing depth visibility; emit inspection bundles."""
from __future__ import annotations

import html
import hashlib
import json
from functools import lru_cache
from pathlib import Path

from scripts.articulated_construction import Point, triangulate_polygon
from scripts.vector_visibility import visible_regions

from .geometry import bounds, lock_rows, mix, outline, resolve_root, path
from .model import canonical, engine_fingerprint, fingerprint, node_by_id, validate, write
from .components import component_data, support, component_outline as node_outline, depth_bounds


PALETTE = dict(fill="#517f9b", shade="#426781", light="#729eaf", ink="#2e475a")


def selection_paths(scene,selection):
    """Alignment always comes from compiled geometry, including parent transforms."""
    node=node_by_id(scene,selection['object'])
    canvas=scene.get('canvas',[640,640])
    rotate=lambda p:p
    if node['kind']!='hair-lock':
        data=component_data(node,canvas)
        if selection['kind']=='feature':
            if node['kind']=='shape' and selection.get('interaction')=='contour-push':
                from .shape import edge_selection
                feature=edge_selection(node,canvas,selection['feature'],selection['at'],selection['radius'])
            else:
                feature=data.features.get(selection['feature'])
            return (feature['paths'],feature.get('focus'),feature.get('locks',{})) if feature else ([],None,{})
        from .head import rotate_point
        child=data.locks[selection['child']]
        rows=child['rows'];root=resolve_root(child['node'],canvas)
        rotate=lambda p:rotate_point(p,data.center,data.angle)
    else:
        rows=lock_rows(node,canvas);root=resolve_root(node,canvas)
        if selection.get('kind')=='feature':
            return [dict(d=path(outline(rows)),transform='')],None,{}
    points=[rotate(getattr(r,selection['side'])) for r in rows if abs(r.t-selection['at'])<=selection['radius']]
    target=min(rows,key=lambda r:abs(r.t-selection['at']))
    return [dict(d=path(points,False),transform='')],rotate(getattr(target,selection['side'])),{
        'root':rotate(root),'tip':rotate(rows[-1].left)}


def lock_palette(node):
    palette=node.get('palette',{})
    colors=dict(PALETTE)
    if 'fill' in palette:
        rgb=[int(palette['fill'][i:i+2],16) for i in (1,3,5)]
        def shade(factor,white=0):
            return '#'+''.join(f'{round(v*factor+255*white):02x}' for v in rgb)
        colors.update(fill=palette['fill'],shade=shade(.81),light=shade(.72,.28),ink=shade(.50))
    return colors|palette


def faces_for(scene):
    faces = []
    canvas = scene.get("canvas", [640, 640])
    for node in scene["nodes"]:
        poly = node_outline(node,canvas)
        root_y,scale,depth=support(node,canvas)
        for triangle in triangulate_polygon(tuple(Point(*p) for p in poly)):
            tri = tuple((p.u, p.v, depth + node.get("depth_slope", 0) * (p.v - root_y) / scale) for p in triangle)
            faces.append((tri, PALETTE["fill"], node["id"]))
    return faces


def global_depth_order(scene):
    """A conservative planar fast path, proved from depths rather than author order.

    A linear depth field reaches extrema at polygon vertices. Disjoint depth
    intervals admit one exact back-to-front order; crossing intervals use the
    existing triangle visibility engine. This is not a curved/wrapping shortcut.
    """
    canvas=scene.get('canvas',[640,640]);intervals=[]
    for node in scene['nodes']:
        low,high=depth_bounds(node,canvas)
        intervals.append((low,high,node))
    intervals.sort(key=lambda item:item[0])
    if any(a[1]>=b[0]-1e-7 for a,b in zip(intervals,intervals[1:])):
        return None
    return [entry[2] for entry in intervals]


@lru_cache(maxsize=16)
def _scene_regions(encoded):
    return tuple(visible_regions(faces_for(json.loads(encoded))))


def tone_region(rows, start, end, a, b):
    selected = [r for r in rows if start <= r.t <= end]
    # Both ends of the highlight taper inside the lock, not square-ended stripes.
    left, right = [], []
    import math
    for r in selected:
        t = (r.t - start) / (end - start)
        envelope = max(0, math.sin(math.pi * t)) ** .6
        middle, half = (a + b) / 2, (b - a) / 2 * envelope
        left.append(mix(r.left, r.right, middle - half))
        right.append(mix(r.left, r.right, middle + half))
    return left + list(reversed(right))


def drawing(scene, selection=None, previous=None, viewbox=None):
    validate(scene)
    width, height = scene.get("canvas", [640, 640])
    vb = viewbox or [0, 0, width, height]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{" ".join(map(str, vb))}">',
           '<title>Drawing studio</title>',
           '<desc>Authored gesture and local edits; visibility from support depth. Selection aids are separate from artwork.</desc>']
    if viewbox is not None:
        out += ['<!-- inspection-workspace: neutral opaque margin outside the document canvas -->',
                f'<rect id="inspection-workspace" x="{vb[0]}" y="{vb[1]}" width="{vb[2]}" height="{vb[3]}" fill="#dedbd5"/>']
    out.append(f'<rect id="paper" x="0" y="0" width="{width}" height="{height}" fill="{scene.get("background", "#f5eee4")}"/>')
    ordered=global_depth_order(scene)
    regions=() if ordered is not None else _scene_regions(canonical(scene))
    for node in ordered if ordered is not None else scene['nodes']:
        sid = node["id"]
        needs_clip=ordered is None or node['kind']=='hair-lock'
        if needs_clip:
            visible=path(node_outline(node,[width,height])) if ordered is not None else " ".join(p for p, _color, name in regions if name == sid)
            out.append(f'<defs><clipPath id="visible-{sid}" clipPathUnits="userSpaceOnUse"><path d="{visible}"/></clipPath></defs>')
        if node['kind']!='hair-lock':
            clip=f' clip-path="url(#visible-{sid})"' if needs_clip else ''
            out += [f'<!-- {sid}: {html.escape(node["intent"])} -->',
                    f'<g id="{sid}"{clip}>',component_data(node,[width,height]).svg,'</g>']
            continue
        colors = lock_palette(node)
        rows = lock_rows(node, [width, height])
        poly = outline(rows)
        out += [f'<!-- {sid}: {html.escape(node["intent"])} -->',
                f'<g id="{sid}" clip-path="url(#visible-{sid})">',
                f'<path id="{sid}-silhouette" d="{path(poly)}" fill="{colors["fill"]}"/>',
                f'<!-- {sid}-shade: cel shadow following the edited inner side -->',
                f'<path id="{sid}-shade" d="{path(tone_region(rows, 0, 1, .77, 1))}" fill="{colors["shade"]}"/>',
                f'<!-- {sid}-light: broad restrained sheen following the lock gesture -->',
                f'<path id="{sid}-light" d="{path(tone_region(rows, .20, .76, .23, .38))}" fill="{colors["light"]}"/>',
                f'<!-- {sid}-contour: two flowing sides; the root joins the host without a sealed ink cap -->',
                f'<path id="{sid}-contour" d="{path([r.left for r in rows], False)} {path([r.right for r in rows], False)}" fill="none" stroke="{colors["ink"]}" stroke-width="3.0" stroke-linejoin="round"/>']
        for k, (share, start, end) in enumerate(((.52, .09, .88), (.73, .27, .96))):
            points = [mix(r.left, r.right, share) for r in rows if start <= r.t <= end]
            out += [f'<!-- {sid}-strand-{k}: a sparse directional strand following the edited mass -->',
                    f'<path id="{sid}-strand-{k}" d="{path(points, False)}" fill="none" stroke="{colors["ink"]}" opacity=".55" stroke-width=".9"/>']
        out.append('</g>')
    if selection:
        if selection.get("engine") != engine_fingerprint():
            raise ValueError("stale selection: implementation changed; inspect again")
        paths,focus,locks=selection_paths(scene,selection)
        if previous:
            old_paths,_,_=selection_paths(previous,selection)
            for i,guide in enumerate(old_paths):
                out.append(f'<path id="edit-before-{i}" d="{guide["d"]}" transform="{guide["transform"]}" fill="none" stroke="#ba6884" stroke-width="2" stroke-dasharray="5 4"/>')
        for i,guide in enumerate(paths):
            ident='selected-edge' if i==0 else f'selected-edge-{i}'
            out.append(f'<path id="{ident}" d="{guide["d"]}" transform="{guide["transform"]}" fill="none" stroke="#e27d39" stroke-width="3"/>')
        if focus:
            x,y=focus
            out.append(f'<circle id="edit-focus" cx="{x}" cy="{y}" r="5" fill="#fffaf0" stroke="#bc5128" stroke-width="2"/>')
        for name,p in locks.items():
            out.append(f'<circle id="locked-{name}" cx="{p[0]}" cy="{p[1]}" r="4" fill="#fffaf0" stroke="#506655" stroke-width="2"/>')
    return "\n".join(out + ['</svg>'])


def rasterize(svg, target):
    """Native CPU SVG first; Cairo or isolated CPU browser are fallbacks."""
    try:
        import resvg_py
    except ImportError:
        pass
    else:
        Path(target).write_bytes(resvg_py.svg_to_bytes(svg_path=str(Path(svg).resolve())))
        return f"resvg-py-{resvg_py.__version__}-cpu"
    try:
        import cairosvg
        cairosvg.svg2png(url=str(Path(svg).resolve()), write_to=str(target))
        return "cairosvg-cpu"
    except (ImportError, OSError):
        pass
    import xml.etree.ElementTree as ET
    from scripts.renderer import screenshot
    root = ET.parse(svg).getroot()
    size = (int(float(root.attrib["width"])), int(float(root.attrib["height"])))
    screenshot(svg, target, size)
    return "chromium-disable-gpu"


def bundle(scene, directory, selection=None, previous=None, png=True):
    """Scene, inspection and image list are bound to one exact canonical revision."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    validate(scene)
    write(directory / "scene.json", scene)
    revision = fingerprint(scene)
    if selection:
        if previous is None and selection["base"] != revision:
            raise ValueError("stale selection: cannot draw alignment against another revision")
        if previous is not None and selection["base"] != fingerprint(previous):
            raise ValueError("preview alignment base mismatch")
        write(directory / "selection.json", selection)
    write(directory/'report.json',dict(revision=revision,engine=engine_fingerprint(),status='rendering',images=[]))
    (directory/'report.txt').write_text('',encoding='utf-8')
    views = {"artwork": drawing(scene)}
    if selection:
        # Crop around the object, not a guessed image location. Square pixel crop
        # is rendered to the same output dimensions, providing real magnification.
        box = bounds(node_outline(node_by_id(scene,selection['object']),scene.get('canvas',[640,640])))
        x0, y0, x1, y1 = box
        pad = max(x1 - x0, y1 - y0) * .1
        span = max(x1 - x0, y1 - y0) + 2 * pad
        vb = [(x0 + x1 - span) / 2, (y0 + y1 - span) / 2, span, span]
        views["alignment"] = drawing(scene, selection, previous)
        views["object-closeup"] = drawing(scene, selection, previous, vb)
        # An operation-scale crop shows the selected edge and before/after guides.
        b = selection["bounds"]
        span = max(b[2] - b[0], b[3] - b[1], 40) * 1.8
        views["edit-closeup"] = drawing(scene, selection, previous,
                                       [(b[0] + b[2] - span) / 2, (b[1] + b[3] - span) / 2, span, span])
    backend = None
    images = []
    for name, svg in views.items():
        f = directory / (name + ".svg")
        f.write_text(svg, encoding="utf-8")
        if png:
            backend = rasterize(f, directory / (name + ".png"))
            images.append(str((directory / (name + ".png")).resolve()))
    node_info={}
    for n in scene['nodes']:
        info=dict(kind=n['kind'],intent=n['intent'],bounds=bounds(node_outline(n,scene.get('canvas',[640,640]))))
        if n['kind']!='hair-lock':
            data=component_data(n,scene.get('canvas',[640,640]))
            info['features']={k:dict(bounds=v['bounds'],controls=v['controls']) for k,v in data.features.items()}
            if n['kind']=='head': info['local_locks']=[side+'-lock' for side in data.locks]
        node_info[n['id']]=info
    report = dict(revision=revision, engine=engine_fingerprint(), status='ready',renderer=backend, images=images,
                  image_sha256={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in images},nodes=node_info,
                  scope="editable colour masses, flat cartoon heads, front-view open hands, planar locks and scenic recipes; no full 3D head/hand rig or whole-artwork acceptance claim",
                  alignment_legend={'orange':'selected current boundary','pink dashed':'previous boundary',
                                    'green rings':'protected endpoints or knuckle','white target':'local edge focus or digit-tip handle'},
                  move_units='object: shorter canvas dimension; local edge: nominal lock width; shape contour: nominal shorter extent; digit tip: nominal digit span')
    write(directory / "report.json", report)
    (directory / "report.txt").write_text("\n".join(images) + "\n", encoding="utf-8")
    return report
