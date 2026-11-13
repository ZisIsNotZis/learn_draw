"""Compile editable parts through existing depth visibility; emit inspection bundles."""
from __future__ import annotations

import html
import hashlib
import json
from functools import lru_cache
from pathlib import Path

from scripts.articulated_construction import Point, triangulate_polygon
from scripts.vector_visibility import visible_regions

from .geometry import xml_comment,bounds, lock_rows, mix, outline, resolve_root, path
from .model import canonical, engine_fingerprint, fingerprint, node_by_id, select, exposed_controls, validate, write
from .components import component_data, support, component_outline as node_outline, depth_bounds
from .attachment import resolve_scene,anchors,get_anchor,anchor_view,endpoint_relations,dependencies,anchor_direction


PALETTE = dict(fill="#517f9b", shade="#426781", light="#729eaf", ink="#2e475a")


def selection_paths(scene,selection):
    """Alignment always comes from compiled geometry, including parent transforms."""
    scene=resolve_scene(scene)
    node=node_by_id(scene,selection['object'])
    canvas=scene.get('canvas',[640,640])
    rotate=lambda p:p
    if selection.get('feature')=='anchors':
        view=anchor_view(node,canvas,selection.get('anchor'))
        return view['paths'],view['focus'],view['locks']
    if node['kind']!='hair-lock':
        data=component_data(node,canvas)
        if selection['kind']=='feature':
            if node['kind']=='stroke' and selection.get('interaction')=='spine-push':
                from .stroke import spine_selection
                feature=spine_selection(node,canvas,selection['at'],selection['radius'])
                return feature['paths'],feature['focus'],feature['locks']
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
    scene=resolve_scene(scene)
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

    A linear depth field reaches extrema at polygon vertices. Overlapping depth
    intervals can still commute when the actual painted projections are disjoint.
    Every potentially overlapping pair is checked, including nonadjacent ranges;
    unresolved crossings retain triangle visibility. No surface is moved.
    """
    scene=resolve_scene(scene)
    canvas=scene.get('canvas',[640,640]);intervals=[]
    for node in scene['nodes']:
        low,high=depth_bounds(node,canvas)
        intervals.append((low,high,node))
    intervals.sort(key=lambda item:item[0])
    from shapely import Polygon
    projections={}
    def projected(node):
        if node['id'] not in projections:
            projections[node['id']]=Polygon(node_outline(node,canvas))
        return projections[node['id']]
    for i,(low,high,node) in enumerate(intervals):
        for other_low,_other_high,other in intervals[i+1:]:
            if high<other_low-1e-7:
                break
            if not projected(node).disjoint(projected(other)):
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


def direction_guide(info,name,scale=1,color='#287c7e',prefix='mount-direction'):
    """An outward join arrow is inspection ink, never an artwork mark."""
    direction=anchor_direction(info)
    if direction is None:return []
    x,y=info['point'];dx,dy=direction;ex,ey=x+dx*24*scale,y+dy*24*scale
    left=(ex-dx*6*scale-dy*3*scale,ey-dy*6*scale+dx*3*scale)
    right=(ex-dx*6*scale+dy*3*scale,ey-dy*6*scale-dx*3*scale)
    d=f'M {x} {y} L {ex} {ey} M {ex} {ey} L {left[0]} {left[1]} L {right[0]} {right[1]} Z'
    return [xml_comment(prefix+'-'+name+': outward direction at the actual inspected mount'),
            f'<path id="{prefix}-{name}-halo" d="{d}" fill="none" stroke="#fffaf0" stroke-width="{4.4*scale}" stroke-linejoin="round"/>',
            f'<path id="{prefix}-{name}" d="{d}" fill="{color}" stroke="{color}" stroke-width="{1.4*scale}" stroke-linejoin="round"/>']


def mount_labels(node,canvas,names=None,scale=1):
    """Screen-sized callouts with minimum rails keep tiny-part guides apart."""
    actual=bounds(node_outline(node,canvas));cx=(actual[0]+actual[2])/2;cy=(actual[1]+actual[3])/2
    half_w=max((actual[2]-actual[0])/2,70*scale);half_h=max((actual[3]-actual[1])/2,45*scale)
    box=[cx-half_w,cy-half_h,cx+half_w,cy+half_h]
    buckets={name:[] for name in ('left','right','top','bottom')}
    chosen={name:get_anchor(node,canvas,name) for name in names} if names is not None else anchors(node,canvas)
    out=[]
    for name,info in chosen.items():
        x,y=info['point'];direction=anchor_direction(info)
        dx,dy=direction if direction else (x-cx,y-cy)
        side=('right' if dx>=0 else 'left') if abs(dx)>=abs(dy) else ('bottom' if dy>=0 else 'top')
        extent=24*scale if side in ('left','right') else (max(36,len(name)*7)+12)*scale
        buckets[side].append((y if side in ('left','right') else x,name,(x,y),extent))
        out.extend(direction_guide(info,name,scale))
    for side,items in buckets.items():
        items.sort();positions=[]
        for i,(desired,_name,_p,extent) in enumerate(items):
            gap=(extent+items[i-1][3])/2 if i else 0
            positions.append(max(desired,positions[-1]+gap) if positions else desired)
        shift=sum(p-i[0] for p,i in zip(positions,items))/len(positions) if positions else 0
        for along,(_desired,name,p,_extent) in zip(positions,items):
            along-=shift
            x,y,align=(box[0]-14*scale,along+4*scale,'end') if side=='left' else ((box[2]+14*scale,along+4*scale,'start') if side=='right' else ((along,box[1]-14*scale,'middle') if side=='top' else (along,box[3]+25*scale,'middle')))
            out.append(xml_comment(f'mount-callout-{name}: connect this name to its actual geometric mount'))
            out.append(f'<path id="mount-callout-{name}" d="M {p[0]} {p[1]} L {x} {y-4*scale}" fill="none" stroke="#506655" stroke-width="{.8*scale}"/>')
            out.append(f'<text x="{x}" y="{y}" text-anchor="{align}" font-family="sans-serif" font-size="{13*scale}" fill="#304f44" stroke="#fffaf0" stroke-width="{3*scale}" paint-order="stroke">{html.escape(name)}</text>')
    return out


def removal_guides(scene,previous,removal):
    """Deletion outlines describe old paint; detached children are current retained paint."""
    if previous is None: raise ValueError('removal alignment requires its previous scene')
    old=resolve_scene(previous);current=resolve_scene(scene);canvas=scene.get('canvas',[640,640]);out=[]
    for name,ids,source,color,dash in [('remove',removal['removed'],old,'#ba4261','6 4'),
                                      ('keep',removal['detached_children'],current,'#3983b9','')]:
        for sid in ids:
            poly=node_outline(node_by_id(source,sid),canvas);box=bounds(poly);cx=(box[0]+box[2])/2;cy=(box[1]+box[3])/2
            label=html.escape(name+': '+sid)
            out.extend([xml_comment(f'{name}-{sid}: '+('previous paint will be removed' if name=='remove' else 'retained child released at its current placement')),
                        f'<path id="{name}-{sid}" d="{path(poly)}" fill="none" stroke="{color}" stroke-width="2.5" stroke-dasharray="{dash}"/>',
                        f'<text x="{cx}" y="{cy}" text-anchor="middle" font-family="sans-serif" font-size="14" fill="{color}" stroke="#fffaf0" stroke-width="3" paint-order="stroke">{label}</text>'])
    return out


def drawing(scene, selection=None, previous=None, viewbox=None):
    validate(scene)
    authored=scene;scene=resolve_scene(scene)
    width, height = scene.get("canvas", [640, 640])
    vb = viewbox or [0, 0, width, height]
    guide_scale=max(vb[2]/width,vb[3]/height)
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
            out += [xml_comment(f'{sid}: {node["intent"]}'),
                    f'<g id="{sid}"{clip}>',component_data(node,[width,height]).svg,'</g>']
            continue
        colors = lock_palette(node)
        rows = lock_rows(node, [width, height])
        poly = outline(rows)
        out += [xml_comment(f'{sid}: {node["intent"]}'),
                f'<g id="{sid}" clip-path="url(#visible-{sid})">',
                f'<path id="{sid}-silhouette" d="{path(poly)}" fill="{colors["fill"]}"/>',
                xml_comment(f'{sid}-shade: cel shadow following the edited inner side'),
                f'<path id="{sid}-shade" d="{path(tone_region(rows, 0, 1, .77, 1))}" fill="{colors["shade"]}"/>',
                xml_comment(f'{sid}-light: broad restrained sheen following the lock gesture'),
                f'<path id="{sid}-light" d="{path(tone_region(rows, .20, .76, .23, .38))}" fill="{colors["light"]}"/>',
                xml_comment(f'{sid}-contour: two flowing sides; the root joins the host without a sealed ink cap'),
                f'<path id="{sid}-contour" d="{path([r.left for r in rows], False)} {path([r.right for r in rows], False)}" fill="none" stroke="{colors["ink"]}" stroke-width="3.0" stroke-linejoin="round"/>']
        for k, (share, start, end) in enumerate(((.52, .09, .88), (.73, .27, .96))):
            points = [mix(r.left, r.right, share) for r in rows if start <= r.t <= end]
            out += [xml_comment(f'{sid}-strand-{k}: a sparse directional strand following the edited mass'),
                    f'<path id="{sid}-strand-{k}" d="{path(points, False)}" fill="none" stroke="{colors["ink"]}" opacity=".55" stroke-width=".9"/>']
        out.append('</g>')
    if selection:
        if selection.get("engine") != engine_fingerprint():
            raise ValueError("stale selection: implementation changed; inspect again")
        if selection.get('removal'):
            out.extend(removal_guides(scene,previous,selection['removal']))
        else:
            paths,focus,locks=selection_paths(scene,selection)
            if previous and not selection.get('insertion'):
                old_paths,_,_=selection_paths(previous,selection)
                for i,guide in enumerate(old_paths):
                    out.append(f'<path id="edit-before-{i}" d="{guide["d"]}" transform="{guide["transform"]}" fill="none" stroke="#ba6884" stroke-width="{2*guide_scale}" stroke-dasharray="{5*guide_scale} {4*guide_scale}"/>')
            for i,guide in enumerate(paths):
                ident='selected-edge' if i==0 else f'selected-edge-{i}'
                out.append(f'<path id="{ident}" d="{guide["d"]}" transform="{guide["transform"]}" fill="none" stroke="#e27d39" stroke-width="{3*guide_scale}"/>')
            if focus:
                x,y=focus
                out.append(f'<circle id="edit-focus" cx="{x}" cy="{y}" r="{5*guide_scale}" fill="#fffaf0" stroke="#bc5128" stroke-width="{2*guide_scale}"/>')
            for name,p in locks.items():
                out.append(f'<circle id="locked-{name}" cx="{p[0]}" cy="{p[1]}" r="{4*guide_scale}" fill="#fffaf0" stroke="#506655" stroke-width="{2*guide_scale}"/>')
            for end,relation in endpoint_relations(node_by_id(authored,selection['object'])).items():
                p=get_anchor(node_by_id(scene,selection['object']),[width,height],end)['point']
                out.append(f'<circle id="pinned-{end}" cx="{p[0]}" cy="{p[1]}" r="{8*guide_scale}" fill="none" stroke="#3983b9" stroke-width="{2*guide_scale}"/>')
            if selection.get('feature')=='anchors':
                out.extend(mount_labels(node_by_id(scene,selection['object']),[width,height],locks,guide_scale))
            elif selection.get('interaction')=='stroke-terminal':
                out.extend(mount_labels(node_by_id(scene,selection['object']),[width,height],[selection['feature']],guide_scale))
            if selection.get('attachment_target'):
                target=selection['attachment_target']
                target_mount=get_anchor(node_by_id(scene,target['object']),[width,height],target['anchor'])
                point=target_mount['point']
                out.extend(direction_guide(target_mount,target['anchor'],guide_scale,'#3983b9','target-direction'))
                label=html.escape(target['object']+'.'+target['anchor'])
                box=bounds(node_outline(node_by_id(scene,selection['object']),[width,height]))
                lx,ly=box[2]+20*guide_scale,max(box[3]+50*guide_scale,point[1]+45*guide_scale)
                out.append(f'<circle id="mount-target" cx="{point[0]}" cy="{point[1]}" r="{7*guide_scale}" fill="none" stroke="#3983b9" stroke-width="{3*guide_scale}"/>')
                out.append('<!-- mount-target-callout: identify the inspected target mount -->')
                out.append(f'<path id="mount-target-callout" d="M {point[0]} {point[1]} L {lx} {ly-4*guide_scale}" fill="none" stroke="#3983b9" stroke-width="{guide_scale}"/>')
                out.append(f'<text x="{lx}" y="{ly}" font-family="sans-serif" font-size="{13*guide_scale}" fill="#286d9e" stroke="#fffaf0" stroke-width="{3*guide_scale}" paint-order="stroke">{label}</text>')
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
    compiled=resolve_scene(scene)
    views = {"artwork": drawing(scene)}
    if selection:
        # Crop around the object, not a guessed image location. Square pixel crop
        # is rendered to the same output dimensions, providing real magnification.
        box = (selection['object_bounds'] if selection.get('removal') else
               bounds(node_outline(node_by_id(compiled,selection['object']),scene.get('canvas',[640,640]))))
        x0, y0, x1, y1 = box
        pad = max(x1 - x0, y1 - y0) * .1
        span = max(x1 - x0, y1 - y0) + 2 * pad
        vb = [(x0 + x1 - span) / 2, (y0 + y1 - span) / 2, span, span]
        views["alignment"] = drawing(scene, selection, previous)
        views["object-closeup"] = drawing(scene, selection, previous, vb)
        # An operation-scale crop shows the selected edge and before/after guides.
        current_view=(selection if selection.get('removal') else
                      select(scene,selection['object'],selection.get('side','left'),selection.get('at',.55),selection.get('radius',.30),selection.get('feature'),selection.get('anchor')))
        b = current_view["bounds"]
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
    for n in compiled['nodes']:
        raw=node_by_id(scene,n['id'])
        info=dict(kind=n['kind'],intent=n['intent'],bounds=bounds(node_outline(n,scene.get('canvas',[640,640]))))
        if n['kind']!='hair-lock':
            data=component_data(n,scene.get('canvas',[640,640]))
            info['features']={k:dict(bounds=v['bounds'],controls=exposed_controls(raw,v['controls'])) for k,v in data.features.items()}
            if n['kind']=='head': info['local_locks']=[side+'-lock' for side in data.locks]
            if getattr(data,'dimensions',None):
                info['dimensions_pixels']=data.dimensions
                info['dimensions_canvas']={k:v/min(scene.get('canvas',[640,640])) for k,v in data.dimensions.items()}
        info['anchors']=anchors(n,scene.get('canvas',[640,640]))
        info['attached_children']=[child['id'] for child in scene['nodes'] if n['id'] in dependencies(child)]
        if 'endpoints' in raw:
            info['endpoints']=raw['endpoints']
            if len(raw['endpoints'])==2: info['derived_chord']=dict(length=n['length'],angle=n['angle'])
        authored=node_by_id(scene,n['id'])
        if 'attachment' in authored: info['attachment']=authored['attachment']
        node_info[n['id']]=info
    report = dict(revision=revision, engine=engine_fingerprint(), status='ready',renderer=backend, images=images,
                  image_sha256={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in images},nodes=node_info,
                  scope="editable gesture strokes and colour masses, flat cartoon heads, front-view open hands, compact illustrative grips with an owned handle segment, planar locks and scenic recipes; no full 3D head/hand rig or whole-artwork acceptance claim",
                  removal=selection.get('removal') if selection else None,
                  insertion=selection.get('insertion') if selection else None,
                  direction_fit=selection.get('direction_fit') if selection else None,
                  alignment_legend={'red dashed':'removed previous paint; removal only','blue':'pinned stroke endpoints / inspected target; removal: retained affected children','orange':'selected current boundary','pink dashed':'previous boundary',
                                    'teal arrows':'outward join direction where defined; center mounts can be directionless','green rings':'named mount points or protected endpoints/knuckle','white target':'local edge/spine, terminal, digit-tip or exact-mount focus'},
                  move_units='object: shorter canvas dimension; local edge: nominal lock width; shape contour: nominal shorter extent; stroke spine: thickness; stroke terminal: shorter canvas; digit tip: nominal digit span')
    write(directory / "report.json", report)
    (directory / "report.txt").write_text("\n".join(images) + "\n", encoding="utf-8")
    return report
