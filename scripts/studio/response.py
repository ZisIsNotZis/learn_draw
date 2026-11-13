"""Focused CLI results; full scene inspection data stays in the ready bundle."""
from pathlib import Path
from .model import node_by_id,select
from .attachment import resolve_scene,get_anchor


def response(report,scene,directory,selection=None,candidate=None,configure=None,full=False):
    if full:return report
    d=Path(directory).resolve()
    files={name:str(d/file) for name,file in [('report','report.json'),('scene','scene.json'),('artwork_svg','artwork.svg')]}
    result=dict(format='learn-draw/studio-response-1',status=report['status'],revision=report['revision'],
                engine=report['engine'],renderer=report['renderer'],images=report['images'],files=files,
                object_count=len(scene['nodes']))
    if selection:
        files['selection']=str(d/'selection.json');result['selection']=selection
        sid=selection['object'];info=report['nodes'].get(sid)
        if info is None:
            result['selected']=dict(id=sid,removed=True)
        else:
            node=node_by_id(scene,sid)
            result['selected']=dict(authored=node,bounds=info['bounds'],
                available_features=list(info.get('features',{})),available_anchors=list(info['anchors']),
                attached_children=info['attached_children'])
            if 'dimensions_canvas' in info:result['selected']['dimensions_canvas']=info['dimensions_canvas']
            if selection.get('feature')=='anchors' or selection.get('interaction')=='stroke-terminal':
                placed=node_by_id(resolve_scene(scene),sid);canvas=scene.get('canvas',[640,640])
                names=([selection['anchor']] if selection.get('anchor') else
                       [selection['feature']] if selection.get('interaction')=='stroke-terminal' else info['anchors'])
                result['selected']['anchors']={name:get_anchor(placed,canvas,name) for name in names}
            if configure:
                try:
                    config=select(scene,sid,feature=configure)
                except ValueError:
                    result['configure']=dict(feature=configure,available=False,controls=[])
                else:
                    result['configure']=dict(feature=configure,available=True,controls=config.get('controls',[]),units=config.get('units'))
    if candidate:
        files['candidate']=str(d/'candidate.json');result['operation']=candidate['operation']
    return result
