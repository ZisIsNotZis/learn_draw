#!/usr/bin/env python3
"""Compare frozen scoped-repair-v1 waist evidence with v3 final region coverage."""
from __future__ import annotations
import hashlib, importlib.util, json, math, sys
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[5]
BASE=ROOT/".scratch/35-r1-articulated-study/evidence/A-cloth-construction-v2/scoped-repair-v1"
NEW=ROOT/".scratch/35-r1-articulated-study/evidence/A-cloth-construction-v3"

def load_builder(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module

def polygons(path):
    import re
    tokens=re.findall(r"[MLZ]|[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?",path)
    result=[];part=[];command=None;i=0
    while i<len(tokens):
        if tokens[i] in {"M","L","Z"}:
            command=tokens[i];i+=1
            if command=="Z":
                if part:result.append(part);part=[]
                continue
        assert command in {"M","L"}
        part.append((float(tokens[i]),480-float(tokens[i+1])));i+=2
    return result

def inside(point,poly):
    x,y=point;hit=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:hit=not hit
    return hit

def area(points):
    xy=[(p.u,p.v) for p in points]
    return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(xy,xy[1:]+xy[:1]))/2

def polygon_area(poly):
    return abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))/2)

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def inspect(builder,output_png):
    from scripts.articulated_construction import component_faces
    from scripts.vector_visibility import visible_regions
    parts,_,params=builder.build_scene();by={p.component.name:p for p in parts}
    upper=by["A-bodice-upper"];band=by["A-derived-waist-band"]
    left=upper.geometry.named_stations["waist_left"];right=upper.geometry.named_stations["waist_right"]
    dx,dy=right[0]-left[0],right[1]-left[1];n=math.hypot(dx,dy)
    probe=((left[0]+right[0])/2+2*dy/n,(left[1]+right[1])/2-2*dx/n)
    expected_point=builder.P(right)
    endpoint_present=any(math.dist((p.u,p.v),(expected_point.u,expected_point.v))<1e-8 for p in upper.component.outline)
    faces=component_faces(tuple(p.component for p in parts),builder.CAMERA)
    body_paths=[d for d,color,owner in visible_regions(faces) if owner==upper.component.name and color==upper.component.fill]
    region_polygons=[poly for d in body_paths for poly in polygons(d)]
    region_covers=any(inside(probe,poly) for poly in region_polygons)
    joins=((upper.geometry.named_stations["waist_left"],upper.geometry.named_stations["waist_right"],band.geometry.named_stations["upper_left"],band.geometry.named_stations["upper_right"]),
           (band.geometry.named_stations["lower_left"],band.geometry.named_stations["lower_right"],by["A-bodice-continuation"].geometry.named_stations["upper_left"],by["A-bodice-continuation"].geometry.named_stations["upper_right"]))
    max_join_error=0.0
    for a,b,c,d in joins:
        for i in range(101):
            t=i/100
            p0=tuple(a[k]*(1-t)+b[k]*t for k in range(2));p1=tuple(c[k]*(1-t)+d[k]*t for k in range(2))
            max_join_error=max(max_join_error,math.dist(p0,p1))
    image=Image.open(output_png).convert("RGB");pixel_xy=(round(probe[0]),round(probe[1]));pixel=image.getpixel(pixel_xy)
    band_pixels=image.getpixel(pixel_xy)
    return {
        "builderSha256":digest(Path(builder.__file__)),"pngSha256":digest(output_png),
        "outlineIncludesNamedSharedRightEndpoint":endpoint_present,"bodyUpperSignedOutlineArea":round(area(upper.component.outline),6),
        "bodyUpperWinding":"positive" if area(upper.component.outline)>0 else "negative",
        "bandSignedOutlineArea":round(area(band.component.outline),6),"waistBandWinding":"positive" if area(band.component.outline)>0 else "negative",
        "bodyUpperCompoundVisibleArea":round(sum(polygon_area(poly) for poly in region_polygons),6),
        "maxTwoSharedJoinErrorAt101Samples":max_join_error,"bodyUpperFill":upper.component.fill,
        "waistBandFill":band.component.fill,"backgroundFill":"#78a49b","sameSupport":upper.component.support.support_id==band.component.support.support_id,
        "probeCropXY":[round(probe[0],4),round(probe[1],4)],"probePixelXY":list(pixel_xy),
        "visibleRegionsHasBodyUpperPath":bool(body_paths),"compoundBodyPathCoversProbe":region_covers,
        "renderedPixelRGB":list(pixel),"visiblePointRGBExpectedForBody":[232,231,220],
        "renderedPixelIsBackgroundRGB":pixel==(120,164,155),
        "waistBoundarySamples":101,
    }

if __name__=="__main__":
    old=load_builder(BASE/"source/build_a.py","waist_old_builder")
    new=load_builder(NEW/"source/build_a.py","waist_v3_builder")
    old_out=inspect(old,BASE/"artwork-a.png");new_out=inspect(new,NEW/"artwork-a.png")
    print(json.dumps({"frozenScopedRepairV1":old_out,"candidateV3":new_out},indent=2,sort_keys=True))
