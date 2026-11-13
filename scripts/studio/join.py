"""One visible proposal inspects both semantic mounts before committing a connection."""
from .model import validate,select,node_by_id,attachment_preview,fingerprint
from .attachment import resolve_scene,get_anchor,anchor_direction,ORIENTABLE_PORTS
from .placement import placement_preview


def endpoint(value):
    if not isinstance(value,str):raise ValueError('join endpoint requires OBJECT.MOUNT')
    sid,separator,name=value.partition('.')
    if not separator or not sid or not name:raise ValueError('join endpoint requires OBJECT.MOUNT')
    return sid,name


def join_preview(scene,source,target,*,mode='auto',inset=0,pending=None,reason):
    validate(scene)
    if mode not in ('auto','point','opposed'):raise ValueError('join mode: auto/point/opposed')
    sid,own=endpoint(source);tid,dest=endpoint(target)
    before=pending['scene'] if pending is not None else scene
    if pending is not None:
        if pending.get('operation',{}).get('object')!=sid:raise ValueError('join source must be the pending component')
        if tid==sid:raise ValueError('pending component cannot join to itself')
    placed=resolve_scene(before);canvas=scene.get('canvas',[640,640])
    node=node_by_id(placed,sid);parent=node_by_id(placed,tid)
    a=get_anchor(node,canvas,own);b=get_anchor(parent,canvas,dest)
    supported=own in ORIENTABLE_PORTS.get(node['kind'],())
    directional=supported and anchor_direction(a) is not None and anchor_direction(b) is not None
    orient='opposed' if mode=='opposed' or (mode=='auto' and directional) else None
    if pending is None:
        candidate=attachment_preview(scene,select(scene,sid,feature='anchors',anchor=own),select(scene,tid,feature='anchors',anchor=dest),own,dest,inset,reason,orient)
        candidate['operation']['action']='join'
    else:
        candidate=placement_preview(scene,prior=pending,target=select(scene,tid,feature='anchors',anchor=dest),self_anchor=own,target_anchor=dest,inset=inset,orient=orient,reason=reason)
        # Placement normally exposes every mount. This comparison needs the exact
        # requested port, including its operation-scale crop and source arrow.
        view=select(candidate['scene'],sid,feature='anchors',anchor=own)
        candidate['selection'].update(view,base=fingerprint(scene))
    join=dict(source=dict(object=sid,anchor=own),target=dict(object=tid,anchor=dest),
              requested_mode=mode,mode='opposed' if orient else 'point',before_revision=fingerprint(before),pending=pending is not None)
    candidate['selection']['join']=join;candidate['operation']['join']=join
    return candidate
