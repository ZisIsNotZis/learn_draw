"""Compare the existing hand's declared direction, ellipse axes and outer contour."""
from pathlib import Path
import json,math,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import relate
from scripts.studio.render import rasterize,path
from shapely import Polygon,union_all

out=Path('evidence/studio-hand/01-existing');out.mkdir(parents=True,exist_ok=False)
pieces=[];records=[]
for index,(fingers,fix,unify) in enumerate([(3,False,False),(4,False,False),(4,True,False),(4,True,True)]):
    spec=dict(frame=dict(w=400,h=440),layers=['paper','hand'],draw=[
        dict(rect='paper',full=True,fill='#f5eee4',z='paper',desc='quiet paper for a hand study'),
        dict(hand='wave',at=[200,240],w=140,h=210,tilt=-90,fingers=fingers,z='hand',desc='request an upward-facing open hand')])
    nodes,anchors,notes,layers=relate.resolve(spec)
    diagnostics=[]
    for node in nodes:
        if 'ellipse' in node:
            ident=node['ellipse'].split('-')[-1]
            intended=-90 if ident=='palm' else -170 if ident=='thumb' else -90+(int(ident.removeprefix('finger'))-1-(fingers-1)/2)*24
            if fix: node['rot']-=90
            diagnostics.append(dict(part=ident,intended_direction=intended,ellipse_major_axis=node['rot']+90,
                 absolute_axis_alignment=abs(math.cos(math.radians(node['rot']+90-intended)))))
    if unify:
        polygons=[]
        for node in nodes:
            if 'ellipse' in node:
                angle=math.radians(node['rot']);cx,cy=node['at'];rx,ry=node['rx'],node['ry']
                polygons.append(Polygon([(cx+rx*math.cos(t)*math.cos(angle)-ry*math.sin(t)*math.sin(angle),
                                          cy+rx*math.cos(t)*math.sin(angle)+ry*math.sin(t)*math.cos(angle)) for t in [i*math.tau/96 for i in range(96)]]))
        shape=union_all(polygons)
        if shape.geom_type!='Polygon': raise ValueError('hand lobes are not connected')
        nodes=[nodes[0],dict(blob='wave-outer',poly=list(shape.exterior.coords)[:-1],fill='#e8d7bd',stroke='#493b40',sw=2.4,
                              z='hand',desc='one computed outer silhouette; lobe intersections are not art lines')]
    svg=relate.emit_svg(nodes,spec['layers'],spec['frame'])
    # These are disjoint teaching panels, not hand-authored visibility cuts.
    pieces.append(f'<g transform="translate({400*index} 0)">{svg}</g>')
    label=f'{fingers} fingers + thumb'+(' / axis corrected' if fix else ' / existing axis')+(' / union' if unify else '')
    pieces.append(f'<text x="{400*index+200}" y="475" font-family="sans-serif" font-size="14" text-anchor="middle" fill="#493b40">{label}</text>')
    records.append(dict(spec=spec,axis_correction=fix,outer_union=unify,diagnostics=diagnostics,nodes=nodes))
svg='<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="500"><rect id="study-paper" width="1600" height="500" fill="#f5eee4"/>'+''.join(pieces)+'</svg>'
(out/'study.svg').write_text(svg,encoding='utf-8');rasterize(out/'study.svg',out/'study.png')
(out/'inputs.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
(out/'source.py').write_bytes(Path(__file__).read_bytes())
print(out/'study.png')
