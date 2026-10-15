from __future__ import annotations
import importlib.util, math, re, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
SOURCE=Path(__file__).resolve().parents[1]/"source"
SMOOTH=ROOT/".scratch/35-r1-articulated-study/evidence/vendor-smooth-spatial"
for path in (ROOT,SMOOTH):
    if str(path) not in sys.path: sys.path.insert(0,str(path))
spec=importlib.util.spec_from_file_location("scoped_cloth_build",SOURCE/"build_a.py")
build=importlib.util.module_from_spec(spec);sys.modules[spec.name]=build;spec.loader.exec_module(build)

def test_waist_shared_sections_match_at_full_sampled_edges():
    parts,_,_=build.build_scene(); by={p.component.name:p for p in parts}
    joins=((by["A-bodice-upper"].geometry.named_stations["waist_left"],by["A-bodice-upper"].geometry.named_stations["waist_right"],by["A-derived-waist-band"].geometry.named_stations["upper_left"],by["A-derived-waist-band"].geometry.named_stations["upper_right"]),
           (by["A-derived-waist-band"].geometry.named_stations["lower_left"],by["A-derived-waist-band"].geometry.named_stations["lower_right"],by["A-bodice-continuation"].geometry.named_stations["upper_left"],by["A-bodice-continuation"].geometry.named_stations["upper_right"]))
    for a0,a1,b0,b1 in joins:
        for i in range(101):
            t=i/100
            a=tuple(a0[k]*(1-t)+a1[k]*t for k in range(2));b=tuple(b0[k]*(1-t)+b1[k]*t for k in range(2))
            assert math.dist(a,b)<1e-10

def test_cuff_plane_matches_sleeve_depth_across_entire_contact_tangent():
    parts,_,_=build.build_scene(); by={p.component.name:p for p in parts}
    sleeve=by["A-continuous-puff-sleeve"]; cuff=by["A-transverse-cuff-band"]
    axis=sleeve.geometry.named_stations["axis"]
    tangent=(-axis[1],-axis[0])
    g1=(sleeve.component.support.u_axis[2],sleeve.component.support.v_axis[2])
    g2=(cuff.component.support.u_axis[2],cuff.component.support.v_axis[2])
    assert abs((g1[0]-g2[0])*tangent[0]+(g1[1]-g2[1])*tangent[1])<1e-12
    a=sleeve.geometry.named_stations["cuff_left"];b=sleeve.geometry.named_stations["cuff_right"]
    for i in range(101):
        t=i/100;xy=tuple(a[k]*(1-t)+b[k]*t for k in range(2));point=build.P(xy)
        assert abs(sleeve.component.support.local_to_world(point)[2]-cuff.component.support.local_to_world(point)[2])<1e-10


def _path_polygons(data):
    tokens=re.findall(r"[MLZ]|[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?",data)
    polygons=[];points=[];command=None;i=0
    while i<len(tokens):
        if tokens[i] in {"M","L","Z"}:
            command=tokens[i];i+=1
            if command=="Z":
                if points:polygons.append(points);points=[]
                continue
        else:
            assert command in {"M","L"}
        assert i+1<len(tokens)
        points.append((float(tokens[i]),build.HEIGHT-float(tokens[i+1])));i+=2
    assert not points
    return polygons


def _point_in_polygon(point,polygon):
    x,y=point;inside=False
    for a,b in zip(polygon,polygon[1:]+polygon[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:inside=not inside
    return inside


def test_generated_collar_trim_is_curved_actual_outer_boundary():
    parts,_,_=build.build_scene();by={p.component.name:p for p in parts}
    collar=by["A-collar-left"].geometry
    trim=next(e.points for e in collar.edges if e.type=="trim")
    outer=collar.outline
    assert len(trim)>=10
    assert all(any(math.dist(point,vertex)<1e-8 for vertex in outer) for point in trim)
    a,b=trim[0],trim[-1]
    chord=math.dist(a,b)
    deviation=max(abs((b[0]-a[0])*(a[1]-p[1])-(a[0]-p[0])*(b[1]-a[1]))/chord for p in trim)
    assert deviation>=3.0
    left_root=by["A-collar-left"].geometry.named_stations["R"]
    right_root=by["A-collar-right"].geometry.named_stations["R"]
    assert abs(left_root[1]-right_root[1])>=8
    assert by["A-collar-left"].geometry.named_stations["Q"]==by["A-collar-right"].geometry.named_stations["Q"]


def test_final_waist_compound_fill_and_png_cover_generated_shared_seam():
    from PIL import Image
    from scripts.articulated_construction import component_faces
    from scripts.vector_visibility import visible_regions
    parts,_,_=build.build_scene();by={p.component.name:p for p in parts}
    upper=by["A-bodice-upper"];band=by["A-derived-waist-band"]
    right=upper.geometry.named_stations["waist_right"]
    assert any(math.dist((v.u,v.v),(build.P(right).u,build.P(right).v))<1e-8 for v in upper.component.outline)
    assert right==band.geometry.named_stations["upper_right"]
    left=upper.geometry.named_stations["waist_left"]
    dx,dy=right[0]-left[0],right[1]-left[1];length=math.hypot(dx,dy)
    # A point 2 px into the shirt-side of the generated terminal section.
    probe=((left[0]+right[0])/2+2*dy/length,(left[1]+right[1])/2-2*dx/length)
    faces=component_faces(tuple(p.component for p in parts),build.CAMERA)
    body_paths=[data for data,color,owner in visible_regions(faces) if owner=="A-bodice-upper" and color==upper.component.fill]
    assert body_paths
    assert any(_point_in_polygon(probe,poly) for path in body_paths for poly in _path_polygons(path))
    image=Image.open(Path(__file__).resolve().parents[1]/"artwork-a.png").convert("RGB")
    pixel=image.getpixel((round(probe[0]),round(probe[1])))
    assert pixel==tuple(bytes.fromhex(upper.component.fill.lstrip("#")))
