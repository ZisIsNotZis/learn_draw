"""Visible named mounts resolved from current vector geometry, never stored screen cuts."""
import copy
import math

from .components import component_data,component_outline,support
from .geometry import bounds,lock_rows,resolve_root


def anchors(node,canvas):
    if 'attachment' in node:
        raise ValueError('resolve the scene before reading attached anchors')
    if node['kind']=='hair-lock':
        rows=lock_rows(node,canvas)
        return {name:dict(point=p,normal=None) for name,p in [('center',rows[len(rows)//2].spine),('root',rows[0].spine),('tip',rows[-1].spine)]}
    data=component_data(node,canvas)
    result={'center':dict(point=data.center,normal=None)}
    result.update(getattr(data,'mounts',{}))
    if node['kind']=='stroke':
        result={name:dict(point=p,normal=None) for name,p in [('center',data.rows[len(data.rows)//2].spine),('root',data.rows[0].spine),('tip',data.rows[-1].spine)]}
    if node['kind']=='shape':
        from .shape import SIDES
        result.update({side:_shape_anchor(node,canvas,side,.5) for side in SIDES})
    return result


def _shape_anchor(node,canvas,side,at):
    from .shape import SIDES
    if side not in SIDES or not math.isfinite(at) or not 0<=at<=1:
        raise ValueError('shape mount position is side@fraction, with fraction 0..1')
    from .shape import local_t
    data=component_data(node,canvas);rows=data.boundary
    half=node.get('stroke',.008)*node.get('length',.32)*min(canvas)/2
    def sample(i):
        p=rows[i][1];a=rows[(i-1)%len(rows)][1];b=rows[(i+1)%len(rows)][1]
        dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
        if length<1e-12: raise ValueError('mount has no stable tangent; revise this contour before attaching')
        return p,(dy/length,-dx/length)
    stations=sorted((local_t(q,side),i) for i,(q,p) in enumerate(rows) if 0<=local_t(q,side)<=1)
    lo,hi=next(((a,b) for a,b in zip(stations,stations[1:]) if a[0]<=at<=b[0]),(stations[-2],stations[-1]))
    alpha=(at-lo[0])/(hi[0]-lo[0]);p0,n0=sample(lo[1]);p1,n1=sample(hi[1])
    if alpha==0: point,normal=p0,n0
    elif alpha==1: point,normal=p1,n1
    else:
        point=tuple(x+(y-x)*alpha for x,y in zip(p0,p1))
        normal=tuple(x+(y-x)*alpha for x,y in zip(n0,n1));size=math.hypot(*normal)
        if size<1e-12: raise ValueError('mount has no stable interpolated normal')
        normal=tuple(v/size for v in normal)
    return dict(point=(point[0]+half*normal[0],point[1]+half*normal[1]),normal=normal)



def get_anchor(node,canvas,name):
    available=anchors(node,canvas)
    if name in available: return available[name]
    if node['kind']=='shape' and isinstance(name,str) and '@' in name:
        side,value=name.split('@',1)
        try: at=float(value)
        except ValueError: raise ValueError('mount position requires a fraction 0..1') from None
        return _shape_anchor(node,canvas,side,at)
    raise ValueError(node['id']+': unavailable mount '+str(name)+'; choose '+', '.join(available))


def mount_scale(node,canvas):
    if node['kind']=='head':
        return node.get('length',.55)*min(canvas)*min(1,node.get('width',.79))
    if node['kind']=='stroke':
        from .stroke import DEFAULT_THICKNESS
        return node.get('thickness',DEFAULT_THICKNESS)*min(canvas)
    if node['kind']=='shape':
        from .shape import span
        return span(node,canvas)
    return support(node,canvas)[1]


def placement_center(node,canvas):
    return resolve_root(node,canvas) if node['kind']=='hair-lock' else component_data(node,canvas).center


def resolve_scene(scene):
    """Keep relations in authored data; bake only an ephemeral compiler copy."""
    if not any('attachment' in n for n in scene['nodes']): return scene
    canvas=scene.get('canvas',[640,640]);by_id={n['id']:n for n in scene['nodes']}
    done={};active=[]
    def resolve(sid):
        if sid in done: return done[sid]
        if sid not in by_id: raise ValueError('unknown attachment target: '+str(sid))
        if sid in active: raise ValueError('attachment cycle: '+' -> '.join(active+[sid]))
        active.append(sid)
        node=copy.deepcopy(by_id[sid])
        relation=node.pop('attachment',None)
        if relation is not None:
            parent=resolve(relation['to'])
            self_name=relation.get('self','center');target_name=relation.get('target','center')
            own=get_anchor(node,canvas,self_name);target=get_anchor(parent,canvas,target_name)
            source=own['point'];destination=target['point']
            inset=relation.get('inset',0);normal=target['normal']
            if inset and normal is None: raise ValueError('inset requires a target surface anchor with an outward normal')
            normal=normal or (0,0);offset=relation.get('offset',[0,0]);unit=min(canvas)
            center=placement_center(node,canvas)
            shift=[destination[k]-source[k]-normal[k]*inset*mount_scale(parent,canvas)+offset[k]*unit for k in (0,1)]
            node['at']=dict(anchor='center',offset=[(center[0]+shift[0])/canvas[0]-.5,(center[1]+shift[1])/canvas[1]-.5])
        done[sid]=node;active.pop();return node
    return dict(scene,nodes=[resolve(n['id']) for n in scene['nodes']])


def anchor_view(node,canvas,name=None):
    from .geometry import path
    points=component_outline(node,canvas)
    selected={name:get_anchor(node,canvas,name)} if name is not None else anchors(node,canvas)
    box=bounds(points);focus=None
    if name is not None:
        focus=selected[name]['point'];pad=max(min(box[2]-box[0],box[3]-box[1])*.12,16)
        box=[focus[0]-pad,focus[1]-pad,focus[0]+pad,focus[1]+pad]
    return dict(paths=[dict(d=path(points),transform='')],bounds=box,controls=[],focus=focus,
                locks={name:value['point'] for name,value in selected.items()})
