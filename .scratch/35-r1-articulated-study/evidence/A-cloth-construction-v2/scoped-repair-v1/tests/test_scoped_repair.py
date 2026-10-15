from __future__ import annotations
import importlib.util, math, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[6]
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
