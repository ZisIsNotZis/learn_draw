"""Fit one observed stroke terminal direction while preserving both endpoints."""
import copy,math
from .model import current_selection,validate,fingerprint,engine_fingerprint,node_by_id
from .attachment import resolve_scene,get_anchor,anchor_direction,endpoint_relations
from .stroke import stroke_data


def aim_preview(scene,selection,target_selection,target_anchor,reason):
    current_selection(scene,selection);current_selection(scene,target_selection)
    if not isinstance(reason,str) or not reason.strip():raise ValueError('state a drawing reason')
    end=selection.get('feature');source=node_by_id(scene,selection['object'])
    if source.get('attachment',{}).get('orient'):raise ValueError('this join direction is already attached; detach before a one-shot aim')
    if source['kind']!='stroke' or end not in ('root','tip'):
        raise ValueError('aim uses an inspected stroke root or tip')
    if target_selection.get('feature')!='anchors':raise ValueError('inspect the target anchors before aiming')
    name=target_anchor or target_selection.get('anchor') or 'center'
    if (target_selection.get('anchor') is not None and name!=target_selection['anchor']) or ('@' in name and name!=target_selection.get('anchor')):
        raise ValueError('inspect this exact target anchor before aiming: '+name)
    relation=endpoint_relations(source).get(end)
    target_authored=node_by_id(scene,target_selection['object'])
    reverse=endpoint_relations(target_authored).get(name)
    if reverse is None and target_authored.get('attachment',{}).get('self','center')==name:
        reverse=target_authored.get('attachment')
    forward=bool(relation and relation['to']==target_selection['object'] and relation.get('target','center')==name)
    backward=bool(reverse and reverse['to']==source['id'] and reverse.get('target','center')==end)
    if not (forward or backward):
        raise ValueError('connect this terminal to the inspected target first; aim uses the existing join in either graph direction')
    canvas=scene.get('canvas',[640,640]);placed=resolve_scene(scene)
    target=node_by_id(placed,target_selection['object']);outward=anchor_direction(get_anchor(target,canvas,name))
    if outward is None:raise ValueError('target mount has no defined direction; inspect a surface edge, wrist or stroke terminal')
    data=stroke_data(node_by_id(placed,source['id']),canvas)
    a,b=data.rows[0].spine,data.rows[-1].spine;length=math.dist(a,b)
    chord=((b[0]-a[0])/length,(b[1]-a[1])/length);side=(chord[1],-chord[0])
    # Opposed outward directions make centerlines continue through the join.
    desired=outward if end=='root' else tuple(-v for v in outward)
    forward=sum(x*y for x,y in zip(desired,chord));across=sum(x*y for x,y in zip(desired,side))
    if forward<=1e-10:raise ValueError('direction cannot fit while keeping endpoints; reposition a target or choose another gesture')
    bend=across/(4*forward)*(1 if end=='root' else -1)
    if not -1<=bend<=1:raise ValueError('direction exceeds the supported bend; reposition a target or choose another gesture')
    candidate=copy.deepcopy(scene);node_by_id(candidate,source['id'])['bend']=bend;validate(candidate)
    new_scene=resolve_scene(candidate)
    new=stroke_data(node_by_id(new_scene,source['id']),canvas)
    new_outward=anchor_direction(get_anchor(node_by_id(new_scene,target_selection['object']),canvas,name))
    if any(math.dist(x,y)>1e-7 for x,y in ((a,new.rows[0].spine),(b,new.rows[-1].spine))):
        raise ValueError('direction fit would move a protected endpoint')
    tangent=new.tangents[0 if end=='root' else -1]
    actual=tuple(-v for v in tangent) if end=='root' else tangent
    if sum(x*y for x,y in zip(actual,new_outward))>-1+1e-9:raise ValueError('direction fit could not satisfy the observed join')
    target_info=dict(object=target_selection['object'],anchor=name)
    view=dict(selection,attachment_target=target_info,direction_fit=dict(endpoint=end,mode='opposed-outward',bend=bend))
    return dict(base=fingerprint(scene),engine=engine_fingerprint(),result=fingerprint(candidate),scene=candidate,
                selection=view,operation=dict(action='aim',object=source['id'],endpoint=end,target=target_info,bend=bend,reason=reason))
