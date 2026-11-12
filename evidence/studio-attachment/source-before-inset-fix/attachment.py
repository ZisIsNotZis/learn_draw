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
    if node['kind']=='shape':
        from .shape import SIDES,phase
        rows=data.boundary
        half=node.get('stroke',.008)*node.get('length',.32)*min(canvas)/2
        for side in SIDES:
            i=min(range(len(rows)),key=lambda i:abs((rows[i][0]-phase(side,.5)+2)%4-2))
            p=rows[i][1];a=rows[(i-1)%len(rows)][1];b=rows[(i+1)%len(rows)][1]
            dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
            normal=(dy/length,-dx/length)
            result[side]=dict(point=(p[0]+half*normal[0],p[1]+half*normal[1]),normal=normal)
    return result


def mount_scale(node,canvas):
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
            own=anchors(node,canvas);target=anchors(parent,canvas)
            self_name=relation.get('self','center');target_name=relation.get('target','center')
            if self_name not in own: raise ValueError(sid+': unavailable self anchor '+self_name+'; choose '+', '.join(own))
            if target_name not in target: raise ValueError(parent['id']+': unavailable target anchor '+target_name+'; choose '+', '.join(target))
            source=own[self_name]['point'];destination=target[target_name]['point']
            inset=relation.get('inset',0);normal=target[target_name]['normal']
            if inset and normal is None: raise ValueError('inset requires a target surface anchor with an outward normal')
            normal=normal or (0,0);offset=relation.get('offset',[0,0]);unit=min(canvas)
            center=placement_center(node,canvas)
            shift=[destination[k]-source[k]-normal[k]*inset*mount_scale(parent,canvas)+offset[k]*unit for k in (0,1)]
            node['at']=dict(anchor='center',offset=[(center[0]+shift[0])/canvas[0]-.5,(center[1]+shift[1])/canvas[1]-.5])
        done[sid]=node;active.pop();return node
    return dict(scene,nodes=[resolve(n['id']) for n in scene['nodes']])


def anchor_view(node,canvas):
    from .geometry import path
    points=component_outline(node,canvas)
    return dict(paths=[dict(d=path(points),transform='')],bounds=bounds(points),controls=[],
                locks={name:value['point'] for name,value in anchors(node,canvas).items()})
