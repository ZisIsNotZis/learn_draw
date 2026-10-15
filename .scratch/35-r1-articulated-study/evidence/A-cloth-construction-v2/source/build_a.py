#!/usr/bin/env python3
"""Build the crop-local A garment study from low-dimensional family parameters only."""
from __future__ import annotations
import argparse, html, importlib.util, json, math, sys
from dataclasses import dataclass
from pathlib import Path

ROOT=Path(__file__).resolve().parents[5]
SMOOTH=ROOT/".scratch/35-r1-articulated-study/evidence/vendor-smooth-spatial"
if str(SMOOTH) not in sys.path: sys.path.insert(0,str(SMOOTH))
PARAMS=Path(__file__).with_name("semantic-parameters.json")
RULES=Path(__file__).with_name("family-rules.py")
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
_spec=importlib.util.spec_from_file_location("a_cloth_family_rules",RULES)
fam=importlib.util.module_from_spec(_spec);sys.modules[_spec.name]=fam;_spec.loader.exec_module(fam)
from scripts.articulated_construction import Point,Component,SupportFrame,Camera,component_faces,triangulate_polygon
from scripts.articulated_line_visibility import visible_segment_spans,transform_compound_path
from scripts.vector_visibility import visible_regions
from smooth_spatial import validate_closed_contour

WIDTH,HEIGHT=400,480
CAMERA=Camera()
@dataclass(frozen=True)
class Part:
    component: Component
    geometry: object
    family: str
    authored_count: int

@dataclass(frozen=True)
class Mark:
    name:str; intent:str; owner:str; points:tuple[Point,...]; color:str; width:float

def P(xy): return Point(float(xy[0]),HEIGHT-float(xy[1]))
def XY(p): return (p.u,HEIGHT-p.v)
def center(a,b): return ((a[0]+b[0])/2,(a[1]+b[1])/2)
def dot2(a,b): return a[0]*b[0]+a[1]*b[1]
def add2(a,b): return (a[0]+b[0],a[1]+b[1])
def sub2(a,b): return (a[0]-b[0],a[1]-b[1])
def mul2(a,s): return (a[0]*s,a[1]*s)
def unit2(a):
    d=math.hypot(*a)
    if d<=1e-10: raise ValueError("degenerate scene relation")
    return (a[0]/d,a[1]/d)

def support(name, data, align_xy=None, align_depth=None):
    du,dv=float(data["du"]),float(data["dv"])
    if align_xy is None: z0=float(data["z"])
    else:
        if align_depth is None: raise ValueError("aligned support needs parent depth")
        q=P(align_xy);z0=float(align_depth)-du*q.u-dv*q.v
    return SupportFrame(name,f"{name}-depth",(0.,0.,z0),(1.,0.,du),(0.,1.,dv))

def depth_at(s,p): return s.local_to_world(P(p))[2]
def to_outline(geom): return tuple(P(q) for q in geom.outline)
def to_edges(geom): return tuple(tuple(P(q) for q in e.points) for e in geom.edges)
def attachment(target,own,target_anchor): return (target,own,target_anchor)

def part(name,intent,geom,support_frame,fill,anchors=(),attachments=()):
    outline=to_outline(geom)
    validate_closed_contour(outline)
    triangulate_polygon(outline)
    inputs=tuple((k,tuple(v)) for k,v in geom.authored_inputs)
    if len(inputs)>4: raise ValueError(f"{name}: generator consumed >4 authored coordinate inputs")
    component=Component(name,intent,support_frame,outline,fill,tuple(attachments),
                        tuple((n,P(xy)) for n,xy in anchors))
    return Part(component,geom,geom.family,len(inputs))

def _opening_root(p,key): return tuple(p["parts"]["opening"]["stations_xy"][key])

def build_scene():
    p=json.loads(PARAMS.read_text(encoding="utf-8"));d=p["parts"];supports=p["supports"]
    out=[];body_s=support("A-bodice-support",supports["bodice"])
    opening=dict(d["opening"]["stations_xy"])
    opening["left_root"]=d["collar_left"]["authored_xy"]["R"]
    opening["right_root"]=d["collar_right"]["authored_xy"]["R"]

    # The opening is one semantic relation; both leaves and skin inherit exactly this Q.
    for key,name in (("collar_left","A-collar-left"),("collar_right","A-collar-right")):
        source=d[key];q=dict(source);q["authored_xy"]={**source["authored_xy"],"Q":opening["Q"]}
        q["authored_input_xy"]={k:source["authored_xy"][k] for k in ("R","E","S")}
        g=fam._wedge(q,name)
        s=support(name+"-support",supports[key])
        out.append(part(name,"opening-derived asymmetric fold-wedge collar leaf",g,s,q["palette"]))
    skin_spec=dict(d["neck_skin"]);skin_spec["authored_xy"]={"R_left":opening["left_root"],"Q":opening["Q"],"R_right":opening["right_root"],"upper_continuation":skin_spec["authored_xy"]["upper_continuation"]}
    skin_spec["authored_input_xy"]=d["neck_skin"]["authored_xy"]
    skin_g=fam.neck_skin(skin_spec,opening)
    skin_s=support("A-neck-skin-support",supports["skin"])
    out.append(part("A-visible-neck-skin","visible neck field continuing above the opening; no round cap",skin_g,skin_s,d["neck_skin"]["palette"]))

    body_spec=dict(d["bodice"]);body_spec["authored_xy"]={**body_spec["authored_xy"],"Q":opening["Q"]}
    body_spec["authored_input_xy"]={k:d["bodice"]["authored_xy"][k] for k in ("C0","Cw","Eleft")}
    upper_g=fam.bodice_upper(body_spec,opening)
    shoulder=upper_g.named_stations["upper_right"]
    out.append(part("A-bodice-upper","tilted chest cloth field, shared opening and upper width profile",upper_g,body_s,body_spec["palette"],
                    anchors=(("waist_center",upper_g.named_stations["waist_center"]),("shoulder",shoulder))))
    band_g=fam.waist_band(body_spec)
    band_center=band_g.named_stations["lower_center"]
    out.append(part("A-derived-waist-band","narrow band derived from the bodice waist cross-section",band_g,body_s,"#d9d8ce",
                    anchors=(("upper_center",band_g.named_stations["upper_center"]),("lower_center",band_center)),
                    attachments=(attachment("A-bodice-upper","upper_center","waist_center"),)))
    cont_g=fam.bodice_continuation(body_spec)
    cont_upper=cont_g.named_stations["upper_center"]
    out.append(part("A-bodice-continuation","same bodice cloth continues below the crop without an in-frame hem",cont_g,body_s,body_spec["palette"],
                    anchors=(("waist_center",cont_upper),),attachments=(attachment("A-derived-waist-band","waist_center","lower_center"),)))

    sleeve_spec=dict(d["sleeve"])
    # Shoulder is inherited from the bodice's generated right upper section, not re-authored.
    sleeve_spec["authored_xy"]={"C":sleeve_spec["authored_xy"]["C"]}
    sleeve_spec["shoulder_radius"]=d["sleeve"]["shoulder_radius"]
    sleeve_local=dict(d["sleeve"]);S=shoulder;sleeve_local["authored_xy"]={"S":S,"C":d["sleeve"]["authored_xy"]["C"]}
    sleeve_local["authored_input_xy"]={"C":d["sleeve"]["authored_xy"]["C"]}
    sleeve_g=fam.sleeve_family(sleeve_local)
    sleeve_support=support("A-continuous-sleeve-support",supports["sleeve"],S,depth_at(body_s,S))
    out.append(part("A-continuous-puff-sleeve","single fullness envelope from shoulder cap to shared cuff section",sleeve_g,sleeve_support,d["sleeve"]["palette"],
                    anchors=(("shoulder",S),("cuff_seat",sleeve_g.named_stations["C"])),
                    attachments=(attachment("A-bodice-upper","shoulder","shoulder"),)))
    cuff_g=fam.cuff_family({"band_depth":d["cuff"]["band_depth"],"band_ease":d["cuff"]["band_ease"],"cuff_radius":d["sleeve"]["cuff_radius"]},sleeve_g)
    cuff_center=cuff_g.named_stations["C"]
    cuff_support=support("A-transverse-cuff-support",supports["cuff"],cuff_center,depth_at(sleeve_support,cuff_center))
    out.append(part("A-transverse-cuff-band","short cuff band sharing the sleeve terminal section",cuff_g,cuff_support,d["cuff"]["palette"],
                    anchors=(("sleeve_seat",cuff_center),),attachments=(attachment("A-continuous-puff-sleeve","sleeve_seat","cuff_seat"),)))

    bow=d["bow"];G=tuple(bow["G"]);bow_s=support("A-bow-support",supports["bow"])
    knot_g=fam.gather_patch(G,bow)
    root=add2(G,tuple(d["tail_down"]["root_offset"]))
    out.append(part("A-bow-gather","short folded wrap gathering the independent bow loops and tail root",knot_g,bow_s,bow["palette"],
                    anchors=(("gather",G),("tail_root",root))))
    for key,name in (("loop_left","A-bow-left-loop"),("loop_right","A-bow-right-loop")):
        q=dict(d[key]);E=q["authored_xy"]["E"];q["authored_xy"]={"G":G,"E":E};q["authored_input_xy"]={"E":E}
        loop=fam.folded_loop(q,name)
        out.append(part(name,"gathered cloth loop with broad free edge and return fold",loop,bow_s,q["palette"],
                        anchors=(("gather",G),),attachments=(attachment("A-bow-gather","gather","gather"),)))
    down_g=fam.tension_tail(d["tail_down"],G)
    tail_support=support("A-down-tail-support",supports["pink_tail"],down_g.named_stations["P0"],depth_at(bow_s,down_g.named_stations["P0"]))
    out.append(part("A-down-tail-continuation","cubic tension band continues below crop; no terminal-tip claim",down_g,tail_support,d["tail_down"]["palette"],
                    anchors=(("root",down_g.named_stations["P0"]),),attachments=(attachment("A-bow-gather","root","tail_root"),)))
    left_g=fam.local_pink_band(d["tail_left_local"])
    left_support=support("A-left-local-pink-band-support",supports["pink_tail"])
    out.append(part("A-left-local-pink-band","local artist-hypothesis band near contact; no recovered centerline or blue attachment",left_g,left_support,d["tail_left_local"]["palette"]))
    blue_g=fam.anonymous_blue_band(d["anonymous_blue_band"])
    blue_support=support("A-anonymous-blue-band-support",supports["blue_band"])
    out.append(part("A-anonymous-blue-band","identity-unknown crop-exiting band, independent of pink cloth",blue_g,blue_support,d["anonymous_blue_band"]["palette"]))
    for key,name in (("hair_neck_curlband","A-neck-curlband"),("hair_right_shoulder_sheet","A-right-shoulder-hair-sheet")):
        hair_g=fam.hair_curlband(d[key]) if key=="hair_neck_curlband" else fam.hair_shoulder_sheet(d[key])
        hair_support=support(name+"-support",supports["hair"])
        out.append(part(name,"minimal visible-context hair sheet; hidden endpoints unknown",hair_g,hair_support,d[key]["palette"]))

    marks=[]
    trim_colors={"A-collar-left":p["parts"]["collar_left"]["trim"],"A-collar-right":p["parts"]["collar_right"]["trim"]}
    for item in out:
        for edge in item.geometry.edges:
            if edge.type=="closure": continue
            if edge.type=="contact" and edge.owner not in trim_colors: continue
            width=float(p["art_lines"]["trim_width"] if edge.type=="contact" else p["art_lines"]["fold_width"] if edge.type=="fold_edge" else p["art_lines"]["silhouette_width"])
            color=trim_colors[edge.owner] if edge.type=="contact" and edge.owner in trim_colors else p["art_lines"]["ink"]
            marks.append(Mark(f"{item.component.name}-{edge.type}-{len(marks)}",edge.intent,item.component.name,
                              tuple(P(q) for q in edge.points),color,width))
    for name,xy in p["art_lines"]["mark_coordinates_xy"].items():
        owner="A-bodice-upper" if name.startswith("bodice") else "A-continuous-puff-sleeve"
        marks.append(Mark("A-"+name,"short semantic fold follows cloth flow toward the gathered waist",owner,tuple(P(q) for q in xy),"#b9b8aa",1.6))
    return tuple(out),tuple(marks),p

def _world(s,point): return CAMERA.project(s.local_to_world(point))
def _segments_svg(mark,owner,faces):
    result=[];world=tuple(_world(owner.support,p) for p in mark.points)
    for i,(a,b) in enumerate(zip(world,world[1:])):
        for j,(lo,hi) in enumerate(visible_segment_spans(a,b,faces,owner.name)):
            p0=tuple(a[k]+(b[k]-a[k])*lo for k in range(3));p1=tuple(a[k]+(b[k]-a[k])*hi for k in range(3))
            result.append(f'<path id="{html.escape(mark.name)}-{i}-{j}" d="M {p0[0]:.6f},{HEIGHT-p0[1]:.6f} L {p1[0]:.6f},{HEIGHT-p1[1]:.6f}" fill="none" stroke="{mark.color}" stroke-width="{mark.width:.3f}" stroke-linecap="round" stroke-linejoin="round"/>')
    return result

def render_svg():
    built,marks,params=build_scene();components=tuple(x.component for x in built);by_name={x.name:x for x in components}
    faces=component_faces(components,CAMERA);regions=tuple(visible_regions(faces))
    output=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
            '<title>A garment construction study — observed shoulder and upper-torso clothing only</title>',
            '<desc>Low-dimensional cloth families with explicit artist hypotheses. It is not a recovered full portrait or 3D truth.</desc>',
            '<!-- A-local-composition-field: flat contextual background, not a generated image -->',
            '<rect id="A-local-composition-field" x="0" y="0" width="400" height="480" fill="#78a49b"/>']
    for path,color,name in regions:
        d=transform_compound_path(path,lambda x,y:(x,HEIGHT-y))
        owner=by_name[name]
        output.append(f'<!-- {html.escape(owner.name)}: {html.escape(owner.intent)} -->')
        output.append(f'<path id="fill-{html.escape(name)}" data-part="{html.escape(name)}" d="{d}" fill="{color}" fill-rule="nonzero"/>')
    selected={m.name:m for m in marks}
    for mark in marks:
        output.append(f'<!-- {html.escape(mark.name)}: {html.escape(mark.intent)}; owner={html.escape(mark.owner)}; edge is depth-clipped -->')
        output.extend(_segments_svg(mark,by_name[mark.owner],faces))
    metadata={"parts":[{"name":x.component.name,"intent":x.component.intent,"family":x.family,
                        "actual_authored_coordinate_inputs":x.authored_count,
                        "generated_outline_vertices":len(x.component.outline),
                        "support_id":x.component.support.support_id,"depth_ref":x.component.support.depth_ref,
                        "attachments":list(x.component.attachments),
                        "named_stations":{k:([list(v) if isinstance(v,tuple) and v and isinstance(v[0],tuple) else list(v)] if isinstance(v,tuple) else v) for k,v in x.geometry.named_stations.items()}}
                       for x in built],
              "edges":sum(len(x.geometry.edges) for x in built),"semantic_lines":len(marks),
              "projected_faces":len(faces),"visible_fill_regions":len(regions),"parameters":params}
    output.append('</svg>')
    return "\n".join(output)+"\n",metadata

def main():
    parser=argparse.ArgumentParser(description="Build A garment study from local semantic parameters; no reference inputs")
    parser.add_argument("--out",required=True)
    args=parser.parse_args();svg,meta=render_svg();out=Path(args.out).resolve();out.parent.mkdir(parents=True,exist_ok=True);out.write_text(svg,encoding="utf-8")
    print(json.dumps({"svg":str(out),"parts":len(meta["parts"]),"faces":meta["projected_faces"],"visible_fill_regions":meta["visible_fill_regions"],"vertices":sum(x["generated_outline_vertices"] for x in meta["parts"]),"max_authored_inputs":max(x["actual_authored_coordinate_inputs"] for x in meta["parts"])},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
