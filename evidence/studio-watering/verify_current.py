"""Rebuild actual current authored artwork and inspect physical/action relations without metrics."""
import hashlib,math,sys
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from shapely import Polygon,Point
from scripts.studio.model import read,write,fingerprint,engine_fingerprint,node_by_id
from scripts.studio.attachment import resolve_scene,get_anchor
from scripts.studio.components import component_data,component_outline
from scripts.studio.render import drawing,rasterize
s=read('evidence/studio-watering/working.json');resolved=resolve_scene(s);canvas=s['canvas'];out=Path('evidence/studio-watering/verification')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=out/'current.svg';svg=drawing(s);assert svg==drawing(s);p.write_text(svg,encoding='utf-8');rasterize(p,out/'current.png');rasterize(p,out/'repeat.png')
assert sha(out/'current.png')==sha(out/'repeat.png')==sha('evidence/studio-watering/27-softer-knuckles/artwork.png')
water=component_data(node_by_id(resolved,'water'),canvas);soil=Polygon(component_outline(node_by_id(resolved,'soil'),canvas));end=water.rows[-1].spine
handle=component_data(node_by_id(resolved,'can-handle'),canvas);can=Polygon(component_outline(node_by_id(resolved,'can-body'),canvas));hand=Polygon(component_outline(node_by_id(resolved,'carrying-hand'),canvas))
assert soil.covers(Point(*end)),'water endpoint misses actual soil plane'
assert water.rows[-1].spine[1]>water.rows[0].spine[1],'stream must end lower than outlet'
end_joins=[Point(*row.spine).buffer(__import__('math').dist(row.left,row.right)/2).intersection(can).area for row in (handle.rows[0],handle.rows[-1])]
assert all(a>0 for a in end_joins),'both handle ends must meet reservoir paint'
assert node_by_id(s,'carrying-hand')['depth']<node_by_id(s,'can-handle')['depth']<node_by_id(s,'grip-thumb')['depth']
assert hand.intersects(Polygon(handle.outline)),'grip must meet handle'
write(out/'current.json',dict(engine=engine_fingerprint(),scene=fingerprint(s),nodes=len(s['nodes']),repeat_svg_equal=True,repeat_png_equal=True,png_sha256=sha(out/'current.png'),water_end=end,water_endpoint_inside_projected_soil=True,stream_ends_lower_than_outlet=True,grip_handle_overlap_area=hand.intersection(Polygon(handle.outline)).area,handle_can_overlap_area=can.intersection(Polygon(handle.outline)).area,handle_end_cap_overlap_areas=end_joins,palm_handle_thumb_depth_order=True,scope='static projected connection/landing checks; not fluid simulation, load-bearing proof or image acceptance'))
print('current picture repeats; projected hand/handle/can joins overlap and water endpoint is inside soil, below outlet')
