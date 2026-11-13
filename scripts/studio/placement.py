"""Observe and revise one pending component before inserting it into the working scene."""
import copy
from .model import (validate,fingerprint,engine_fingerprint,node_by_id,select,current_selection,
                    _set_parameter,preview,attachment_preview)
from .attachment import resolve_scene
from .components import depth_bounds


def placement_preview(scene,node=None,*,prior=None,changes=None,feature='object',at=None,offset=None,
                      direction=None,amount=.05,target=None,self_anchor=None,target_anchor=None,inset=0,reason):
    validate(scene)
    if not isinstance(reason,str) or not reason.strip():raise ValueError('state a drawing reason')
    if (node is None)==(prior is None):raise ValueError('choose a new preset or revise one pending placement')
    base=fingerprint(scene);engine=engine_fingerprint()
    if prior is not None:
        if prior.get('status')!='ready':raise ValueError('placement preview has not completed')
        if prior.get('base')!=base or prior.get('engine')!=engine:raise ValueError('stale placement; preview against the current scene and implementation')
        if prior.get('operation',{}).get('action')!='place':raise ValueError('revise requires a pending placement candidate')
        staged=copy.deepcopy(prior['scene']);validate(staged)
        if prior.get('result')!=fingerprint(staged):raise ValueError('placement candidate hash mismatch')
        sid=prior['operation']['object']
        # A pending placement may add exactly one node. Never smuggle earlier scene edits
        # into an insertion or replace a working object with the same semantic name.
        remainder=copy.deepcopy(staged);remainder['nodes']=[n for n in staged['nodes'] if n['id']!=sid]
        if fingerprint(remainder)!=base or len(staged['nodes'])!=len(scene['nodes'])+1:
            raise ValueError('placement must preserve every existing object and scene setting')
        if at is not None or offset is not None:raise ValueError('revise placement with a screen move; initial --at/--offset only')
    else:
        if target is not None:raise ValueError('preview the new shape and mounts first; then revise with --attach')
        staged=copy.deepcopy(scene);node=copy.deepcopy(node);sid=node['id']
        if node['kind'] not in ('sky','hills'):
            canvas=scene.get('canvas',[640,640])
            node['depth']=max((depth_bounds(n,canvas)[1] for n in resolve_scene(scene)['nodes']),default=0)+1
        if at is not None or offset is not None:
            # Preserve each preset's default origin when only offset is requested.
            if 'at' not in node:
                default={'head':{'anchor':'center','offset':[0,-.06]},'hand':{'anchor':'center'},'grip':{'anchor':'center'},
                         'shape':{'anchor':'center'},'stroke':{'anchor':'center','offset':[0,-.2]},
                         'moon':{'anchor':'upper_right','offset':[0,.10]},'sun':{'anchor':'upper_right','offset':[0,.10]}}
                node['at']=copy.deepcopy(default.get(node['kind'],{'anchor':'upper_center'}))
            if at is not None:node['at']=dict(anchor=at)
            if offset is not None:node['at']['offset']=list(offset)
        staged['nodes'].append(node);validate(staged)
    node=node_by_id(staged,sid)
    if changes:
        view=select(staged,sid,feature=feature)
        for name,value in changes.items():_set_parameter(node,view,name,copy.deepcopy(value))
        validate(staged)
    if direction is not None:
        staged=preview(staged,select(staged,sid,feature='object'),direction,amount,reason)['scene']
    attachment_target=None
    if target is not None:
        current_selection(scene,target)
        # Target was inspected on the unchanged working scene; rebind only its revision
        # after verifying the pending scene preserves all of that target's input.
        target=copy.deepcopy(target);target['base']=fingerprint(staged)
        source=select(staged,sid,feature='anchors')
        result=attachment_preview(staged,source,target,self_anchor,target_anchor,inset,reason)
        staged=result['scene'];attachment_target=result['selection']['attachment_target']
    elif self_anchor is not None or target_anchor is not None or inset!=0:
        raise ValueError('mount flags require --attach')
    validate(staged)
    view=select(staged,sid,feature='anchors')
    view.update(base=base,insertion=dict(object=sid))
    if attachment_target:view['attachment_target']=attachment_target
    return dict(base=base,engine=engine,result=fingerprint(staged),scene=staged,selection=view,
                operation=dict(action='place',object=sid,kind=node_by_id(staged,sid)['kind'],reason=reason,
                               revised_from=prior['result'] if prior else None))
