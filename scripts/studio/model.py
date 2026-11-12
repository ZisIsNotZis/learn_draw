"""Strict small scene schema, observable selections and optimistic edit transactions."""
from __future__ import annotations

import copy
import hashlib
import json
import math
from functools import lru_cache
from pathlib import Path

from .geometry import bounds, geometry_issues, lock_rows, outline, resolve_root


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def fingerprint(scene):
    return hashlib.sha256(canonical(scene).encode()).hexdigest()


@lru_cache(maxsize=1)
def engine_fingerprint():
    """An unchanged scene can render differently after a primitive implementation edit."""
    directory = Path(__file__).parent
    sources = {str(p.relative_to(directory.parent)): p.read_text(encoding="utf-8")
               for p in sorted(directory.glob("*.py"))}
    for name in ("vector_visibility.py", "articulated_construction.py", "renderer.py", "relate.py", "scene_render.py"):
        sources[name] = (directory.parent / name).read_text(encoding="utf-8")
    return hashlib.sha256(canonical(sources).encode()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write(path, value):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    # Replace, never partially overwrite a working scene.
    temp = p.with_suffix(p.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    temp.replace(p)


def number(value, label, low, high):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label}: expected a finite number")
    if not low <= value <= high:
        raise ValueError(f"{label}: must be between {low} and {high}")


def keys(value, allowed, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label}: expected an object")
    unknown = set(value) - set(allowed)
    if unknown:
        raise ValueError(f"{label}: unknown fields {sorted(unknown)}")


def validate_edits(edits):
    if not isinstance(edits,list):
        raise ValueError('edits: expected a list')
    for edit in edits:
        keys(edit, ("side", "at", "radius", "dx", "dy", "reason"), "edit")
        if edit.get("side") not in ("left", "right"):
            raise ValueError("edit.side: left or right")
        number(edit.get("at"), "edit.at", .01, .99)
        number(edit.get("radius"), "edit.radius", .025, .49)
        if edit["at"]-edit["radius"]<=0 or edit["at"]+edit["radius"]>=1:
            raise ValueError("edit influence must stay inside root/tip locks")
        for axis in ('dx','dy'):
            number(edit.get(axis),'edit.'+axis,-2,2)
        if not isinstance(edit.get('reason'),str) or not edit['reason'].strip():
            raise ValueError('edit: state a drawing reason')


def validate_placement(node):
    if 'attachment' in node:
        if 'at' in node: raise ValueError('use attachment or free at placement, not both')
        if node.get('kind') in ('sky','hills'): raise ValueError('canvas-wide backgrounds cannot be attached children')
        relation=node['attachment']
        keys(relation,('to','target','self','inset','offset'),'attachment')
        for name,default in [('to',None),('target','center'),('self','center')]:
            value=relation.get(name,default)
            if not isinstance(value,str) or not value.strip(): raise ValueError('attachment.'+name+' requires a name')
        number(relation.get('inset',0),'attachment.inset',-2,2)
        offset=relation.get('offset',[0,0])
        if not isinstance(offset,list) or len(offset)!=2: raise ValueError('attachment.offset requires two values')
        for value in offset: number(value,'attachment.offset',-2,2)
    at=node.get('at',{})
    keys(at,('anchor','offset'),'at')
    if at.get('anchor','center') not in ('upper_center','center','upper_left','upper_right'):
        raise ValueError('unknown canvas anchor')
    offset=at.get('offset',[0,0])
    if not isinstance(offset,list) or len(offset)!=2:
        raise ValueError('offset: needs two canvas-relative values')
    for n in offset:
        number(n,'offset',-2,2)


def validate_head(node, canvas):
    keys(node,('id','kind','intent','attachment','at','length','width','angle','depth','depth_slope',
               'eye_scale','jaw','hair','hair_edits','palette','expression','gaze'),'head')
    for name,default,low,high in (('length',.55,.1,1.2),('width',.79,.5,1.1),('angle',0,-180,180),
                                ('depth',0,-100,100),('depth_slope',0,-10,10),
                                ('eye_scale',1,.6,1.4),('jaw',.42,.1,.7),('gaze',0,-1,1)):
        number(node.get(name,default),'head.'+name,low,high)
    if node.get('hair','side-part') not in ('none','bob','side-part'):
        raise ValueError('head.hair: none/bob/side-part')
    if node.get('expression','gentle') not in ('gentle','neutral','smile','curious'):
        raise ValueError('head.expression: gentle/neutral/smile/curious')
    validate_placement(node)
    palette=node.get('palette',{})
    keys(palette,('hair','skin','iris','shade','ink'),'head.palette')
    for value in palette.values():
        color(value)
    edits=node.get('hair_edits',{})
    keys(edits,('left','right'),'head.hair_edits')
    for values in edits.values():
        validate_edits(values)
    from .head import head_data
    data=head_data(node,canvas)
    for child in data.locks.values():
        problems=geometry_issues(child['rows'])
        if problems:
            raise ValueError('head lock: '+'; '.join(problems))


def validate_scenery(node,canvas):
    kind=node['kind']
    fields={'sky':('style','stars','seed'), 'hills':('horizon','relief','seed','trees','tree_scale','tree_side'),
            'moon':('at','length','angle','fullness'), 'sun':('at','length','angle','rays')}
    palette_keys={'sky':('top','bottom','stars'),'hills':('far','middle','near'),
                  'moon':('fill',),'sun':('fill','rays')}
    keys(node,('id','kind','intent','attachment','depth','depth_slope','palette')+fields[kind],kind)
    for name,default,lo,hi in [('depth',0,-100,100),('depth_slope',0,-10,10)]:
        number(node.get(name,default),kind+'.'+name,lo,hi)
    if 'attachment' in node and kind in ('sky','hills'): validate_placement(node)
    if kind in ('moon','sun'):
        validate_placement(node)
        number(node.get('length',.22),'length',.03,1.2)
        number(node.get('angle',0),'angle',-180,180)
    if kind=='moon': number(node.get('fullness',.42),'fullness',.08,1)
    if kind=='hills':
        number(node.get('horizon',.64),'horizon',.3,.75)
        number(node.get('relief',.11),'relief',.02,.12)
        number(node.get('tree_scale',.18),'tree_scale',.06,.35)
        if node.get('tree_side','left') not in ('left','right'): raise ValueError('tree_side: left/right')
    for key,default,lo,hi in [('seed',4,0,100000),('stars',28,0,120),('rays',12,0,32),('trees',0,0,5)]:
        if key in fields[kind]:
            value=node.get(key,default)
            number(value,key,lo,hi)
            if value!=int(value): raise ValueError(key+': expected a whole number')
    if kind=='sun' and 0<node.get('rays',12)<3:
        raise ValueError('rays: use 0 or at least 3')
    if kind=='sky' and node.get('style','dusk') not in ('dusk','day'):
        raise ValueError('sky.style: dusk/day')
    keys(node.get('palette',{}),palette_keys[kind],kind+'.palette')
    for value in node.get('palette',{}).values(): color(value)
    from .scenery import scenery_data
    from shapely import Polygon
    if not Polygon(scenery_data(node,canvas).outline).is_valid:
        raise ValueError(kind+': invalid silhouette')


def validate_hand(node,canvas):
    from .hand import DIGITS,DEFAULT_LENGTH,hand_data
    keys(node,('id','kind','intent','attachment','at','length','width','angle','depth','depth_slope','handedness','spread','digits','palette'),'hand')
    for name,default,lo,hi in [('length',DEFAULT_LENGTH,.1,1.2),('width',1,.75,1.3),('angle',0,-180,180),
                               ('depth',0,-100,100),('depth_slope',0,-10,10),('spread',1,.25,1.6)]:
        number(node.get(name,default),'hand.'+name,lo,hi)
    if node.get('handedness','right') not in ('right','left'):
        raise ValueError('hand.handedness: right/left')
    validate_placement(node)
    adjustments=node.get('digits',{})
    keys(adjustments,DIGITS,'hand.digits')
    for name,control in adjustments.items():
        keys(control,('length','lean'),'hand.digits.'+name)
        number(control.get('length',1),name+'.length',.7,1.25)
        number(control.get('lean',0),name+'.lean',-12,12)
    keys(node.get('palette',{}),('skin','ink','crease'),'hand.palette')
    for value in node.get('palette',{}).values(): color(value)
    hand_data(node,canvas)


def validate_shape(node,canvas):
    from .shape import SIDES,DEFAULT_LENGTH,shape_data
    keys(node,('id','kind','intent','attachment','at','length','width','angle','depth','depth_slope','profile','rounding','taper','stroke','palette','edits'),'shape')
    for name,default,lo,hi in [('length',DEFAULT_LENGTH,.005,1.6),('width',.8,.001,6),('angle',0,-180,180),
                              ('depth',0,-100,100),('depth_slope',0,-10,10),('rounding',.65,0,1),
                              ('taper',0,-.98,.98),('stroke',.008,0,.1)]:
        number(node.get(name,default),'shape.'+name,lo,hi)
    if node.get('profile','block') not in ('block','oval'): raise ValueError('shape.profile: block/oval')
    validate_placement(node)
    keys(node.get('palette',{}),('fill','ink'),'shape.palette')
    for value in node.get('palette',{}).values(): color(value)
    edits=node.get('edits',[])
    if not isinstance(edits,list): raise ValueError('shape.edits must be a list')
    for edit in edits:
        keys(edit,('side','at','radius','dx','dy','reason'),'shape.edit')
        if edit.get('side') not in SIDES: raise ValueError('shape.edit.side: top/right/bottom/left')
        # Reuse the lock's bounded influence and reason validation, not its side enum.
        validate_edits([dict(edit,side='left')])
    shape_data(node,canvas)


def validate(scene):
    keys(scene, ("format", "canvas", "background", "nodes"), "scene")
    if scene.get("format") != "learn-draw/studio-1":
        raise ValueError("scene: unsupported format")
    canvas = scene.get("canvas", [640, 640])
    if not isinstance(canvas, list) or len(canvas) != 2:
        raise ValueError("canvas: needs width and height")
    for n in canvas:
        number(n, "canvas", 64, 4096)
    color(scene.get("background", "#f5eee4"))
    if not isinstance(scene.get("nodes"), list) or not 1 <= len(scene["nodes"]) <= 24:
        raise ValueError("scene: needs 1–24 nodes")
    ids = set()
    for node in scene["nodes"]:
        if not isinstance(node,dict):
            raise ValueError('node: expected an object')
        sid = node.get("id", "")
        if not isinstance(sid, str) or not sid or not sid.replace("-", "").replace("_", "").isalnum() or sid in ids:
            raise ValueError("node: ID must be unique and contain letters, digits, - or _")
        ids.add(sid)
        if not isinstance(node.get("intent"), str) or not node["intent"].strip():
            raise ValueError(f"{sid}: intent is required")
        if node.get('kind')=='head':
            validate_head(node,canvas)
            continue
        if node.get('kind')=='shape':
            validate_shape(node,canvas)
            continue
        if node.get('kind')=='hand':
            validate_hand(node,canvas)
            continue
        from .scenery import KINDS
        if node.get('kind') in KINDS:
            validate_scenery(node,canvas)
            continue
        if node.get("kind") != "hair-lock":
            raise ValueError(f"{sid}: supported kinds are shape/head/hand/hair-lock/sky/hills/moon/sun")
        keys(node, ("id", "kind", "intent", "attachment", "at", "length", "width", "width_side", "angle", "sweep", "depth",
                    "depth_slope", "palette", "edits"), "node")
        if node.get("width_side", "both") not in ("both", "left", "right"):
            raise ValueError(f"{sid}.width_side: both/left/right")
        for name, default, low, high in (("length", .68, .1, 1.2), ("width", .19, .03, .65),
                                       ("angle", -8, -180, 180), ("sweep", .16, -.45, .45),
                                       ("depth", 0, -100, 100), ("depth_slope", 0, -10, 10)):
            number(node.get(name, default), f"{sid}.{name}", low, high)
        validate_placement(node)
        palette = node.get("palette", {})
        keys(palette, ("fill", "shade", "light", "ink"), f"{sid}.palette")
        for c in palette.values():
            color(c)
        validate_edits(node.get('edits',[]))
        problems = geometry_issues(lock_rows(node, canvas))
        if problems:
            raise ValueError(f"{sid}: " + "; ".join(problems))
    from .attachment import resolve_scene
    resolve_scene(scene)
    return scene


def color(value):
    if not isinstance(value, str) or len(value) != 7 or value[0] != "#":
        raise ValueError("colour: expected #rrggbb")
    try:
        int(value[1:], 16)
    except ValueError:
        raise ValueError("colour: expected #rrggbb") from None


def node_by_id(scene, sid):
    for node in scene["nodes"]:
        if node["id"] == sid:
            return node
    raise ValueError(f"unknown object {sid!r}")


def select(scene, sid=None, side="left", at=.55, radius=.30, feature=None):
    validate(scene)
    if sid is None:
        if len(scene['nodes'])!=1:
            raise ValueError('select an object: '+', '.join(n['id'] for n in scene['nodes']))
        sid=scene['nodes'][0]['id']
    selection = dict(base=fingerprint(scene), engine=engine_fingerprint(), object=sid)
    from .attachment import resolve_scene,anchor_view
    node = node_by_id(resolve_scene(scene), sid)
    canvas=scene.get('canvas',[640,640])
    rotate=lambda p:p
    if feature=='anchors':
        f=anchor_view(node,canvas)
        selection.update(kind='feature',feature='anchors',bounds=f['bounds'],object_bounds=f['bounds'],controls=[],
                         locks=f['locks'],units='named geometry mounts; attachment pins one point and keeps the child angle in screen space')
        return selection
    if node['kind']!='hair-lock':
        from .components import component_data
        data=component_data(node,canvas)
        feature=feature or 'object'
        if node['kind']=='shape' and feature in ('top','right','bottom','left'):
            from .shape import edge_selection
            validate_edits([dict(side='left',at=at,radius=radius,dx=0,dy=0,reason='selection')])
            f=edge_selection(node,canvas,feature,at,radius)
            selection.update(kind='feature',feature=feature,interaction='contour-push',side=feature,at=at,radius=radius,
                             bounds=f['bounds'],object_bounds=bounds(data.outline),focus=f['focus'],locks=f['locks'],
                             controls=data.features[feature]['controls'],
                             units='screen-direction push in nominal shorter shape extent; clockwise arc: top left-to-right, right top-to-bottom, bottom right-to-left, left bottom-to-top')
            return selection
        if feature in data.features:
            f=data.features[feature]
            selection.update(kind='feature',feature=feature,bounds=f['bounds'],object_bounds=bounds(data.outline),
                             controls=f['controls'],units=f.get('units',('semantic values; object move amount is a fraction of the shorter canvas dimension'
                             if feature=='object' else 'semantic parameter values; inspect the actual selected feature')))
            for key in ('interaction','locks','focus','nominal_span'):
                if key in f: selection[key]=f[key]
            return selection
        if node['kind']!='head' or feature not in ('left-lock','right-lock') or feature.split('-')[0] not in data.locks:
            raise ValueError('unavailable '+node['kind']+' feature: '+str(feature))
        child=feature.split('-')[0]
        from .head import rotate_point
        lock=data.locks[child]
        rows=lock['rows']
        rotate=lambda p:rotate_point(p,data.center,data.angle)
        selection.update(feature=feature,child=child)
        object_bounds=bounds(data.outline)
        root=resolve_root(lock['node'],canvas)
    else:
        if feature not in (None,'object'):
            raise ValueError('hair-lock exposes its left/right edge, not '+str(feature))
        rows=lock_rows(node,canvas)
        object_bounds=bounds(outline(rows))
        root=resolve_root(node,canvas)
        if feature=='object':
            selection.update(kind='feature',feature='object',bounds=object_bounds,object_bounds=object_bounds,
                             controls=['intent','length','width','sweep','angle','width_side','depth','depth_slope',
                                       'fill_color','shade_color','light_color','ink_color'],
                             units='semantic values; object move amount is a fraction of the shorter canvas dimension')
            return selection
    validate_edits([dict(side=side,at=at,radius=radius,dx=0,dy=0,reason='selection')])
    region = [rotate(getattr(r, side)) for r in rows if abs(r.t - at) <= radius]
    selection.update(kind='local',side=side,at=at,radius=radius,bounds=bounds(region),object_bounds=object_bounds,
                     locks={"root":rotate(root),"tip":rotate(rows[-1].left)},
                     units="push amount = fraction of this object's nominal full width; directions are screen directions")
    return selection


def current_selection(scene, selection):
    validate(scene)
    if selection["base"] != fingerprint(scene):
        raise ValueError("stale selection: inspect the current scene again")
    if selection.get("engine") != engine_fingerprint():
        raise ValueError("stale selection: primitive implementation changed; inspect again")


def preview(scene, selection, direction, amount, reason):
    current_selection(scene,selection)
    object_move=selection.get('kind')=='feature' and selection.get('feature')=='object'
    digit_move=selection.get('kind')=='feature' and selection.get('interaction')=='digit-tip'
    contour_move=selection.get('kind')=='feature' and selection.get('interaction')=='contour-push'
    if selection.get('kind','local')!='local' and not object_move and not digit_move and not contour_move:
        raise ValueError('use a semantic parameter, or select a lock edge, shape contour or digit tip for a local move')
    if direction not in ("left", "right", "up", "down"):
        raise ValueError("direction: left/right/up/down")
    number(amount, "amount", 0, 2)
    if not isinstance(reason,str) or not reason.strip():
        raise ValueError('state a drawing reason')
    dx, dy = {"left": (-amount, 0), "right": (amount, 0), "up": (0, -amount), "down": (0, amount)}[direction]
    candidate = copy.deepcopy(scene)
    node = node_by_id(candidate, selection["object"])
    if object_move:
        canvas=scene.get('canvas',[640,640])
        if node['kind'] in ('sky','hills'):
            raise ValueError('canvas-wide backgrounds use horizon/relief controls; select a movable object')
        default={'head':{'anchor':'center','offset':[0,-.06]},'hand':{'anchor':'center'},'shape':{'anchor':'center'},
                 'moon':{'anchor':'upper_right','offset':[0,.10]},
                 'sun':{'anchor':'upper_right','offset':[0,.10]}}.get(node['kind'],{})
        if 'attachment' in node:
            relation=node['attachment'];offset=relation.get('offset',[0,0])
            relation['offset']=[offset[0]+dx,offset[1]+dy]
            validate(candidate)
            return dict(base=fingerprint(scene),engine=engine_fingerprint(),result=fingerprint(candidate),scene=candidate,
                        selection=selection,operation=dict(object=selection['object'],feature='object',direction=direction,
                        amount=amount,units='screen offset from attached target, shorter canvas dimension',reason=reason))
        placement=node.setdefault('at',copy.deepcopy(default))
        offset=placement.get('offset',[0,0])
        placement['offset']=[offset[0]+dx*min(canvas)/canvas[0],offset[1]+dy*min(canvas)/canvas[1]]
        validate(candidate)
        return dict(base=fingerprint(scene),engine=engine_fingerprint(),result=fingerprint(candidate),scene=candidate,
                    selection=selection,operation=dict(object=selection['object'],feature='object',
                    direction=direction,amount=amount,units='shorter canvas dimension',reason=reason))
    if contour_move:
        from .shape import SAMPLES
        if node.get('attachment',{}).get('self')==selection.get('feature') and abs(selection['at']-.5)<=selection['radius']+4/SAMPLES:
            raise ValueError('this contour interval contains the attached anchor; edit outside the pin or detach first')
        if node['kind']!='shape': raise ValueError('contour push requires a shape')
        edit={k:selection[k] for k in ('side','at','radius')}
        a=math.radians(node.get('angle',0))
        edit.update(dx=dx*math.cos(a)-dy*math.sin(a),dy=dx*math.sin(a)+dy*math.cos(a),reason=reason)
        node.setdefault('edits',[]).append(edit)
        validate(candidate)
        return dict(base=fingerprint(scene),engine=engine_fingerprint(),result=fingerprint(candidate),scene=candidate,
                    selection=selection,operation=dict(edit,object=selection['object'],units='nominal shorter shape extent'))
    if digit_move:
        if node['kind']!='hand': raise ValueError('digit-tip movement requires a hand')
        from .hand import move_tip
        from .attachment import resolve_scene
        resolved=node_by_id(resolve_scene(scene),selection['object'])
        changed,derived=move_tip(resolved,scene.get('canvas',[640,640]),selection['feature'],direction,amount)
        node['digits']=changed['digits']
        validate(candidate)
        return dict(base=fingerprint(scene),engine=engine_fingerprint(),result=fingerprint(candidate),scene=candidate,
                    selection=selection,operation=dict(object=selection['object'],feature=selection['feature'],
                    direction=direction,amount=amount,units='nominal digit span',derived=derived,reason=reason))
    edit = {k: selection[k] for k in ("side", "at", "radius")}
    edit.update(dx=dx, dy=dy, reason=reason)
    if node['kind']=='head':
        a=math.radians(node.get('angle',0))
        edit['dx'],edit['dy']=dx*math.cos(a)-dy*math.sin(a),dx*math.sin(a)+dy*math.cos(a)
        node.setdefault('hair_edits',{}).setdefault(selection['child'],[]).append(edit)
    else:
        node.setdefault("edits", []).append(edit)
    validate(candidate)
    return dict(base=fingerprint(scene), engine=engine_fingerprint(), result=fingerprint(candidate), scene=candidate,
                selection=selection, operation=dict(edit,object=selection['object'],feature=selection.get('feature',selection['side'])))


def attachment_preview(scene,selection,target_selection,self_anchor,target_anchor,inset,reason):
    current_selection(scene,selection)
    current_selection(scene,target_selection)
    if selection.get('feature')!='anchors' or target_selection.get('feature')!='anchors':
        raise ValueError('inspect anchors on both objects before attaching')
    if not isinstance(reason,str) or not reason.strip(): raise ValueError('state a drawing reason')
    candidate=copy.deepcopy(scene)
    node=node_by_id(candidate,selection['object'])
    node.pop('at',None)
    node['attachment']=dict(to=target_selection['object'],self=self_anchor,target=target_anchor,inset=inset)
    validate(candidate)
    view=dict(selection,attachment_target=dict(object=target_selection['object'],anchor=target_anchor))
    return dict(base=fingerprint(scene),engine=engine_fingerprint(),result=fingerprint(candidate),scene=candidate,
                selection=view,operation=dict(action='attach',object=selection['object'],attachment=node['attachment'],reason=reason))


def detach_preview(scene,selection,reason):
    current_selection(scene,selection)
    if selection.get('feature')!='anchors': raise ValueError('inspect anchors before detaching')
    if not isinstance(reason,str) or not reason.strip(): raise ValueError('state a drawing reason')
    from .attachment import resolve_scene
    candidate=copy.deepcopy(scene);node=node_by_id(candidate,selection['object'])
    if 'attachment' not in node: raise ValueError('this object has no attachment to detach')
    placed=node_by_id(resolve_scene(scene),selection['object'])
    node.pop('attachment');node['at']=copy.deepcopy(placed['at'])
    validate(candidate)
    return dict(base=fingerprint(scene),engine=engine_fingerprint(),result=fingerprint(candidate),scene=candidate,
                selection=selection,operation=dict(action='detach',object=selection['object'],reason=reason))


def _set_parameter(node,selection,parameter,value):
    """Assign one exposed semantic value; validate the complete proposed state later."""
    if selection.get('kind')!='feature' or parameter not in selection.get('controls',[]):
        raise ValueError('parameter is not exposed by the selected feature; inspect the relevant feature first')
    aliases={'hair_color':'hair','skin_color':'skin','iris_color':'iris','ink_color':'ink',
             'fill_color':'fill','shade_color':'shade','light_color':'light',
             'top_color':'top','bottom_color':'bottom','stars_color':'stars','far_color':'far',
             'middle_color':'middle','near_color':'near','rays_color':'rays','crease_color':'crease'}
    if parameter in aliases:
        color(value)
        node.setdefault('palette',{})[aliases[parameter]]=value
    elif node['kind']=='hand' and parameter in ('finger_length','finger_lean'):
        from .hand import DIGITS
        if selection['feature'] not in DIGITS: raise ValueError('select a named digit')
        if isinstance(value,str):
            try: value=float(value)
            except ValueError: raise ValueError('finger control requires a numeric value') from None
        node.setdefault('digits',{}).setdefault(selection['feature'],{})['length' if parameter=='finger_length' else 'lean']=value
    else:
        if parameter not in ('intent','expression','hair','width_side','style','tree_side','handedness','profile') and isinstance(value,str):
            try:
                value=float(value)
            except ValueError:
                raise ValueError('parameter requires a numeric value') from None
        node[parameter]=value
    return value


def parameters_preview(scene,selection,changes,reason):
    """One coherent parameter proposal, one validation, one eventual undo entry."""
    current_selection(scene,selection)
    if not isinstance(reason,str) or not reason.strip():
        raise ValueError('state a drawing reason')
    if not isinstance(changes,dict) or not changes:
        raise ValueError('provide a nonempty object of semantic parameter changes')
    candidate=copy.deepcopy(scene)
    node=node_by_id(candidate,selection['object'])
    applied={}
    for parameter,value in changes.items():
        applied[parameter]=_set_parameter(node,selection,parameter,copy.deepcopy(value))
    validate(candidate)
    return dict(base=fingerprint(scene),engine=engine_fingerprint(),result=fingerprint(candidate),scene=candidate,
                selection=selection,operation=dict(object=selection['object'],feature=selection['feature'],parameters=applied,reason=reason))


def parameter_preview(scene,selection,parameter,value,reason):
    candidate=parameters_preview(scene,selection,{parameter:value},reason)
    applied=candidate['operation'].pop('parameters')
    candidate['operation'].update(parameter=parameter,value=applied[parameter])
    return candidate


def accept(path, candidate):
    if candidate.get('status') not in (None,'ready'):
        raise ValueError('preview has not completed; no working scene change was made')
    scene = validate(read(path))
    if candidate["base"] != fingerprint(scene):
        raise ValueError("stale preview: working scene has changed; preview again")
    if candidate.get("engine") != engine_fingerprint():
        raise ValueError("stale preview: primitive implementation changed; preview again")
    validate(candidate["scene"])
    if candidate["result"] != fingerprint(candidate["scene"]):
        raise ValueError("candidate hash mismatch")
    p = Path(path)
    history = p.parent / (p.stem + ".history")
    write(history / (fingerprint(scene) + ".json"), scene)
    journal_path = history / "journal.json"
    journal = read(journal_path) if journal_path.exists() else []
    journal.append({k: candidate[k] for k in ("base", "result", "operation")})
    write(journal_path, journal)
    write(p, candidate["scene"])
    return candidate["result"]


def undo(path):
    p = Path(path)
    scene = validate(read(p))
    history = p.parent / (p.stem + ".history")
    journal_path = history / "journal.json"
    journal = read(journal_path) if journal_path.exists() else []
    if not journal:
        raise ValueError("no accepted edit to undo")
    item = journal[-1]
    if item["result"] != fingerprint(scene):
        raise ValueError("scene changed outside edit history; refusing unsafe undo")
    previous = validate(read(history / (item["base"] + ".json")))
    if fingerprint(previous) != item["base"]:
        raise ValueError("history hash mismatch")
    write(p, previous)
    write(journal_path, journal[:-1])
    return fingerprint(previous)
