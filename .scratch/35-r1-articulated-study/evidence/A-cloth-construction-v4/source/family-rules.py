"""Low-dimensional crop-local cloth families; not a raster trace or renderer backend."""
from __future__ import annotations
from dataclasses import dataclass
import math

EDGE_TYPES = {"silhouette", "free_edge", "fold_edge", "contact", "trim", "closure"}

@dataclass(frozen=True)
class Edge:
    type: str
    points: tuple[tuple[float, float], ...]
    owner: str
    intent: str

@dataclass(frozen=True)
class FamilyGeometry:
    outline: tuple[tuple[float, float], ...]
    named_stations: dict[str, tuple[float, float]]
    edges: tuple[Edge, ...]
    authored_inputs: tuple[tuple[str, tuple[float, float]], ...]
    family: str


def _add(a,b): return (a[0]+b[0],a[1]+b[1])
def _sub(a,b): return (a[0]-b[0],a[1]-b[1])
def _mul(a,s): return (a[0]*s,a[1]*s)
def dot(a,b): return a[0]*b[0]+a[1]*b[1]
def _len(a): return math.hypot(a[0],a[1])
def _unit(a):
    d=_len(a)
    if d<=1e-10: raise ValueError("degenerate family direction")
    return (a[0]/d,a[1]/d)
def _normal(a):
    u=_unit(a)
    return (-u[1],u[0])
def _lerp(a,b,t): return ((1-t)*a[0]+t*b[0],(1-t)*a[1]+t*b[1])
def _smooth(t): return 3*t*t-2*t*t*t
def _beta(t,a,b):
    x=t**a*(1-t)**b
    peak=(a/(a+b))**a*(b/(a+b))**b
    return x/peak

def _bezier(a,b,c,d,steps=16):
    out=[]
    for i in range(steps+1):
        t=i/steps;s=1-t
        out.append((s**3*a[0]+3*s*s*t*b[0]+3*s*t*t*c[0]+t**3*d[0],
                    s**3*a[1]+3*s*s*t*b[1]+3*s*t*t*c[1]+t**3*d[1]))
    return tuple(out)

def _catmull_open(points, steps=12):
    """Open cubic interpolation with handles bounded by local station spacing."""
    pts=tuple(points); out=[]
    for i,(a,b) in enumerate(zip(pts,pts[1:])):
        prev=pts[max(0,i-1)]; nxt=pts[min(len(pts)-1,i+2)]
        chord=_len(_sub(b,a)); limit=.25*min(chord,_len(_sub(a,prev)) if i else chord,
                                               _len(_sub(nxt,b)) if i+2<len(pts) else chord)
        ta=_mul(_unit(_sub(b,prev)),min(limit,.24*chord))
        tb=_mul(_unit(_sub(nxt,a)),min(limit,.24*chord))
        seg=_bezier(a,_add(a,ta),_sub(b,tb),b,steps)
        out.extend(seg if i==0 else seg[1:])
    return tuple(out)

def _clean_closed(points):
    pts=[]
    for p in points:
        if not pts or _len(_sub(p,pts[-1]))>1e-8: pts.append(tuple(map(float,p)))
    if len(pts)>1 and _len(_sub(pts[0],pts[-1]))<1e-8: pts.pop()
    if len(pts)<3: raise ValueError("family must emit a closed contour")
    return tuple(pts)

def _edge(kind,points,owner,intent):
    if kind not in EDGE_TYPES: raise ValueError(f"unknown semantic edge type {kind}")
    return Edge(kind,tuple(tuple(map(float,p)) for p in points),owner,intent)

def _input_rows(mapping): return tuple((k,tuple(map(float,v))) for k,v in mapping.items())
def _geometry(outline,stations,edges,inputs,family):
    return FamilyGeometry(_clean_closed(outline),dict(stations),tuple(edges),_input_rows(inputs),family)


def _curve_point(controls, t):
    a,b,c,d=controls;u=1-t
    return tuple(u**3*a[k]+3*u*u*t*b[k]+3*u*t*t*c[k]+t**3*d[k] for k in range(2))


def _curve_derivatives(controls, t):
    a,b,c,d=controls;u=1-t
    first=tuple(3*(u*u*(b[k]-a[k])+2*u*t*(c[k]-b[k])+t*t*(d[k]-c[k])) for k in range(2))
    second=tuple(6*(u*(c[k]-2*b[k]+a[k])+t*(d[k]-2*c[k]+b[k])) for k in range(2))
    return first,second


def _oriented_frame(controls, end_reference, samples=96):
    """Resolve an inner-curve normal from E, then propagate its sign continuously."""
    frames=[]
    for i in range(samples+1):
        t=i/samples;tangent,_=_curve_derivatives(controls,t)
        if _len(tangent)<=1e-10: raise ValueError("collar inner curve has a degenerate tangent")
        frames.append(_normal(tangent))
    reference=_sub(end_reference,controls[-1]);alignment=dot(frames[-1],reference)
    if abs(alignment)<=1e-8: raise ValueError("collar E station cannot resolve outward normal at Q")
    if alignment<0: frames[-1]=_mul(frames[-1],-1)
    for i in range(samples-1,-1,-1):
        if dot(frames[i],frames[i+1])<0: frames[i]=_mul(frames[i],-1)
        if dot(frames[i],frames[i+1])<=1e-8: raise ValueError("collar outward normal field is discontinuous")
    def normal_at(t):
        tangent,_=_curve_derivatives(controls,t);raw=_normal(tangent)
        idx=max(0,min(samples,round(t*samples)))
        return raw if dot(raw,frames[idx])>=0 else _mul(raw,-1)
    return tuple(frames),normal_at


def _normal_derivative(controls, t, normal_at):
    tangent,acceleration=_curve_derivatives(controls,t);speed=_len(tangent)
    if speed<=1e-10: raise ValueError("collar inner curve has a degenerate tangent")
    unit=_mul(tangent,1/speed);along=dot(unit,acceleration)
    unit_derivative=_mul(_sub(acceleration,_mul(unit,along)),1/speed)
    raw=_normal(tangent);n=normal_at(t)
    sign=1.0 if dot(raw,n)>=0 else -1.0
    return _mul(_normal(unit_derivative),sign)


def _field_tangents(xs,ys,last_slope):
    secants=[(ys[i+1]-ys[i])/(xs[i+1]-xs[i]) for i in range(len(xs)-1)]
    slopes=[secants[0]]
    for i in range(1,len(xs)-1):
        left,right=secants[i-1],secants[i]
        if left*right<=0: slopes.append(0.0)
        else:
            h0=xs[i]-xs[i-1];h1=xs[i+1]-xs[i]
            slopes.append((h0+h1)/((h0+2*h1)/(3*left)+(2*h0+h1)/(3*right)))
    slopes.append(last_slope)
    return slopes


def _field_value(xs,ys,slopes,t):
    i=max(0,min(len(xs)-2,next((j-1 for j,x in enumerate(xs[1:],1) if t<=x),len(xs)-2)))
    width=xs[i+1]-xs[i];u=(t-xs[i])/width
    h00=2*u**3-3*u*u+1;h10=u**3-2*u*u+u;h01=-2*u**3+3*u*u;h11=u**3-u*u
    return h00*ys[i]+h10*width*slopes[i]+h01*ys[i+1]+h11*width*slopes[i+1]


def _segments_cross(a,b,c,d,eps=1e-9):
    def orient(p,q,r): return (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
    def on(p,q,r):
        return min(p[0],q[0])-eps<=r[0]<=max(p[0],q[0])+eps and min(p[1],q[1])-eps<=r[1]<=max(p[1],q[1])+eps
    o1,o2,o3,o4=orient(a,b,c),orient(a,b,d),orient(c,d,a),orient(c,d,b)
    if ((o1>eps and o2 < -eps) or (o1 < -eps and o2>eps)) and ((o3>eps and o4 < -eps) or (o3 < -eps and o4>eps)): return True
    return (abs(o1)<=eps and on(a,b,c)) or (abs(o2)<=eps and on(a,b,d)) or (abs(o3)<=eps and on(c,d,a)) or (abs(o4)<=eps and on(c,d,b))


def _assert_simple_offset(outline, widths, minimum):
    if not all(math.isfinite(v) for p in outline for v in p): raise ValueError("collar offset produced non-finite geometry")
    if not all(math.isfinite(w) and w>=minimum for w in widths): raise ValueError("collar offset width violates its positive floor")
    points=tuple(outline);count=len(points)
    for i,(a,b) in enumerate(zip(points,points[1:]+points[:1])):
        for j in range(i+1,count):
            if j==i or j==(i+1)%count or (j+1)%count==i: continue
            if _segments_cross(a,b,points[j],points[(j+1)%count]):
                raise ValueError(f"collar offset self-intersects at sampled edges {i} and {j}")


def _wrap_context(spec):
    a=spec["authored_xy"];R,Q,E,S=(tuple(a[k]) for k in ("R","Q","E","S"))
    axis=_sub(Q,R);base=_normal(axis);bend=float(spec["inner_bend"])
    controls=(R,_add(_lerp(R,Q,.30),_mul(base,bend)),_add(_lerp(R,Q,.72),_mul(base,bend)),Q)
    frames,normal_at=_oriented_frame(controls,E)
    lengths=(_len(_sub(R,S)),_len(_sub(S,E)),_len(_sub(E,Q)))
    total=sum(lengths)
    if min(lengths)<=1e-8: raise ValueError("collar R/S/E/Q stations must be distinct")
    t_s=lengths[0]/total;t_e=(lengths[0]+lengths[1])/total
    def station_width(station,t):
        width=dot(_sub(station,_curve_point(controls,t)),normal_at(t))
        if not math.isfinite(width) or width<=float(spec["width_floor"]):
            raise ValueError("collar E/S station does not define a positive outward width")
        return width
    xs=(0.0,t_s,t_e,1.0)
    ys=(float(spec["root_width"]),station_width(S,t_s),station_width(E,t_e),float(spec["front_width"]))
    if not all(math.isfinite(w) and w>float(spec["width_floor"]) for w in ys):
        raise ValueError("collar width field must remain above its positive floor")
    return {"spec":spec,"R":R,"Q":Q,"E":E,"S":S,"controls":controls,"frames":frames,
            "normal_at":normal_at,"xs":xs,"ys":ys,"width_floor":float(spec["width_floor"])}


def _wrap_strip(context, name, front_normal, front_width, endpoint_slope, sample_count=64):
    spec=context["spec"];controls=context["controls"];normal_at=context["normal_at"]
    xs,ys=context["xs"],context["ys"]
    slopes=_field_tangents(xs,ys,endpoint_slope)
    width_samples=tuple(_field_value(xs,ys,slopes,i/(sample_count*2)) for i in range(sample_count*2+1))
    floor=context["width_floor"]
    if min(width_samples)<floor: raise ValueError(f"{name}: width field falls below its positive floor")
    front=context["Q"];q_prime=_add(front,_mul(front_normal,front_width))
    inner=tuple(_curve_point(controls,i/sample_count) for i in range(sample_count+1))
    outer=[]
    for i in range(sample_count+1):
        t=i/sample_count;center=inner[i];n=normal_at(t);w=_field_value(xs,ys,slopes,t)
        H=_smooth(t)
        # The endpoint correction is expressed in each leaf's resolved outward frame.
        end_normal=normal_at(1.0)
        correction=_sub(_sub(q_prime,front),_mul(end_normal,front_width))
        outer.append(_add(_add(center,_mul(n,w)),_mul(correction,H)))
    outer[-1]=q_prime
    # One generated contour is the shape and the full outer curve is the trim.
    outline=_clean_closed((*inner,q_prime,*reversed(outer[:-1])))
    _assert_simple_offset(outline,width_samples,floor)
    tangent,_=_curve_derivatives(controls,1.0)
    nprime=_normal_derivative(controls,1.0,normal_at)
    endpoint_vector=_add(_add(tangent,_mul(nprime,front_width)),_mul(normal_at(1.0),endpoint_slope))
    trim=tuple(outer)
    edges=(_edge("fold_edge",inner,name,"inner opening boundary preserves shared Q and the negative skin opening"),
           _edge("trim",trim,name,"dark trim is the generated finite-width outer wrap-strip boundary"),
           _edge("closure",(context["R"],outer[0]),name,"computed root bridge closes the finite cloth strip; not an art line"),
           _edge("closure",(front,q_prime),name,"shared positive-width front seam closes the strip; not an art line"))
    stations={"R":context["R"],"Q":front,"Q_prime":q_prime,"E":context["E"],"S":context["S"],
              "front_width":front_width,"front_normal":front_normal,"outer_tangent":endpoint_vector,
              "width_samples":width_samples,"width_stations":tuple(zip(xs,ys)),"inner":inner,"outer":trim,
              "root_width":ys[0],"fold_corner_before":outer[round(.75*sample_count)]}
    return _geometry(outline,stations,edges,spec.get("authored_input_xy",spec["authored_xy"]),"opening-finite-width-wrap-strip")


def wrap_strips(specs, names):
    """Build a coupled pair of finite-width strips sharing an opening front seam."""
    if len(specs)!=2 or len(names)!=2: raise ValueError("collar wrap requires exactly two leaves")
    contexts=tuple(_wrap_context(spec) for spec in specs)
    wf_values=tuple(float(c["spec"]["front_width"]) for c in contexts)
    if not all(math.isfinite(w) and w>max(c["width_floor"] for c in contexts) for w in wf_values):
        raise ValueError("collar front width must be finite and positive")
    if abs(wf_values[0]-wf_values[1])>1e-10: raise ValueError("left/right collar front widths must be one shared value")
    normals=tuple(c["normal_at"](1.0) for c in contexts)
    summed=_add(*normals)
    if _len(summed)<=1e-8: raise ValueError("collar outward normals have a degenerate shared bisector")
    front_normal=_unit(summed);front_width=wf_values[0]
    tangents=tuple(_curve_derivatives(c["controls"],1.0)[0] for c in contexts)
    normal_derivatives=tuple(_normal_derivative(c["controls"],1.0,c["normal_at"]) for c in contexts)
    bases=tuple(_add(tangents[i],_mul(normal_derivatives[i],front_width)) for i in range(2))
    n0,n1=normals;det=n0[0]*n1[1]-n1[0]*n0[1]
    if abs(det)<=1e-8: raise ValueError("collar endpoint normal basis is degenerate; shared sweep cannot be derived")
    rhs=_mul(_add(bases[0],bases[1]),-1)
    slopes=((rhs[0]*n1[1]-n1[0]*rhs[1])/det,(n0[0]*rhs[1]-rhs[0]*n0[1])/det)
    geoms=tuple(_wrap_strip(c,name,front_normal,front_width,slopes[i]) for i,(c,name) in enumerate(zip(contexts,names)))
    if math.dist(geoms[0].named_stations["Q_prime"],geoms[1].named_stations["Q_prime"])>1e-10:
        raise ValueError("paired collar outer edges do not share Q-prime")
    if math.dist(geoms[0].named_stations["outer_tangent"],_mul(geoms[1].named_stations["outer_tangent"],-1))>1e-8:
        raise ValueError("paired collar outer edge sweep is not tangent-continuous at Q-prime")
    return geoms


def neck_skin(spec, opening):
    a=spec["authored_xy"]; Rl,Q,Rr,top=(tuple(a[k]) for k in ("R_left","Q","R_right","upper_continuation"))
    left=_bezier(Rl,_lerp(Rl,Q,.38),_lerp(Rl,Q,.72),Q,16)
    right=_bezier(Q,_lerp(Q,Rr,.25),_lerp(Q,Rr,.74),Rr,16)
    # Skin continues upward beyond the crop; there is no in-frame rounded forehead/neck cap.
    tr=(top[0]+20,top[1]); tl=(top[0]-20,top[1])
    outline=_clean_closed((*left,*right[1:],tr,tl))
    edges=(_edge("contact",(*left,*right[1:]),"A-visible-neck-skin","visible skin follows the shared opening relation"),
           _edge("closure",(Rr,tr,tl,Rl),"A-visible-neck-skin","crop-exiting upper continuation closure, not ink"))
    return _geometry(outline,{"R_left":Rl,"Q":Q,"R_right":Rr,"upper_continuation":top},edges,spec.get("authored_input_xy",a),"opening-skin-continuation")


def body_axis(p,t):
    c0=tuple(p["authored_xy"]["C0"]);cw=tuple(p["authored_xy"]["Cw"])
    return _add(c0,_mul(_sub(cw,c0),t))

def body_frame(p):
    e=_unit(_sub(tuple(p["authored_xy"]["Cw"]),tuple(p["authored_xy"]["C0"])))
    return e,(e[1],-e[0])

def body_widths(p,t):
    right0,rightw=p["right_widths"]
    C0=tuple(p["authored_xy"]["C0"]);Eleft=tuple(p["authored_xy"]["Eleft"]);e,n=body_frame(p)
    length=_len(_sub(tuple(p["authored_xy"]["Cw"]),C0))
    te=min(1,max(0,dot(_sub(Eleft,C0),e)/length))
    H=_smooth(te);beta=_beta(te,1,3)
    leftw=float(p["left_waist_width"])
    L0=(dot(_sub(body_axis(p,te),Eleft),n)-H*leftw-p["left_chest_fullness"]*beta)/max(1-H,1e-8)
    h=_smooth(min(1,max(0,t)))
    L=(1-h)*L0+h*leftw+p["left_chest_fullness"]*_beta(min(1,max(0,t)),1,3)
    R=(1-h)*right0+h*rightw+p["right_chest_fullness"]*_beta(min(1,max(0,t)),2,3)
    if t>1:
        extra=t-1
        L+=p["continuation_flare"]*extra*.72
        R+=p["continuation_flare"]*extra*.48
    return L,R

def body_section(p,t):
    c=body_axis(p,t);_,n=body_frame(p);L,R=body_widths(p,t)
    return _sub(c,_mul(n,L)),_add(c,_mul(n,R))

def _chain_sections(p,t0,t1,count=18,left_side=False,reverse=False):
    ts=[t0+(t1-t0)*i/count for i in range(count+1)]
    pairs=[body_section(p,t) for t in ts]
    side=[lr[0] if left_side else lr[1] for lr in pairs]
    return tuple(reversed(side)) if reverse else tuple(side)

def bodice_upper(spec, opening):
    p=spec;a=p["authored_xy"];Q=tuple(a["Q"])
    left0,right0=body_section(p,0)
    left=_chain_sections(p,0,p["waist_start"],24,left_side=True)
    right=_chain_sections(p,0,p["waist_start"],24,left_side=False)
    # Opening recess Q is shared by collar, skin, and bodice. Eleft seeds only the exposed-side trend.
    # Include the complete generated terminal section. Omitting right[-1] leaves a
    # rendered cloth wedge despite the named shared boundary matching the band.
    outline=_clean_closed((right0,tuple(opening["right_root"]),Q,tuple(opening["left_root"]),left0,*left[1:],*right[::-1]))
    # The last cross-section is an attachment, not a visible hem. Body cloth continues into a derived waist band.
    left_path=tuple(reversed(left))
    right_path=tuple(reversed(right))
    edges=(_edge("silhouette",left_path,"A-bodice-upper","tilted exposed bodice edge"),
           _edge("silhouette",right_path,"A-bodice-upper","covered shoulder-side continuation"),
           _edge("contact",(tuple(opening["left_root"]),Q,tuple(opening["right_root"])) ,"A-bodice-upper","shared opening relation; semantic trim is selected from collar edges"),
           _edge("closure",(left[-1],right[-1]),"A-bodice-upper","waist cross-section shared with the derived band"))
    return _geometry(outline,{"upper_left":left0,"upper_right":right0,"waist_left":left[-1],"waist_right":right[-1],"waist_center":body_axis(p,p["waist_start"])},edges,p.get("authored_input_xy",a),"tilted-bodice-upper-field")

def waist_band(spec):
    p=spec;t0,t1=p["waist_start"],p["waist_end"]
    l0,r0=body_section(p,t0);l1,r1=body_section(p,t1)
    outline=_clean_closed((l0,r0,r1,l1))
    edges=(_edge("fold_edge",(l0,r0),"A-waist-band","shared upper waist gather edge"),
           _edge("fold_edge",(l1,r1),"A-waist-band","lower edge continues into the same body width field"),
           _edge("closure",(r0,r1,l1,l0),"A-waist-band","derived band side closure"))
    inputs={}
    return _geometry(outline,{"upper_left":l0,"upper_right":r0,"upper_center":body_axis(p,t0),"lower_left":l1,"lower_right":r1,"lower_center":body_axis(p,t1)},edges,inputs,"derived-waist-cross-section-band")

def bodice_continuation(spec):
    p=spec;t0=p["waist_end"];t1=p["continuation_end_t"]
    left=_chain_sections(p,t0,t1,30,left_side=True);right=_chain_sections(p,t0,t1,30,left_side=False)
    outline=_clean_closed((*left,*reversed(right)))
    edges=(_edge("silhouette",left,"A-bodice-continuation","same cloth section continues below viewport"),
           _edge("silhouette",tuple(reversed(right)),"A-bodice-continuation","same cloth section continues below viewport"),
           _edge("closure",(left[-1],right[-1]),"A-bodice-continuation","calculation closure lies below crop, not a garment hem"),
           _edge("contact",(left[0],right[0]),"A-bodice-continuation","exact shared waist-band lower section"))
    return _geometry(outline,{"upper_left":left[0],"upper_right":right[0],"upper_center":body_axis(p,t0),"out_of_crop_closure_left":left[-1],"out_of_crop_closure_right":right[-1]},edges,{},"crop-exiting-body-continuation")


def sleeve_frame(S,C):
    e=_unit(_sub(C,S)); n=(-e[1],e[0]);return e,n

def sleeve_radius(p,t):
    H=_smooth(t)
    return (1-H)*p["shoulder_radius"]+H*p["cuff_radius"]+p["fullness"]*_beta(t,1.2,2.2)

def sleeve_center(p,t):
    S,C=(tuple(p["authored_xy"][k]) for k in ("S","C"));e,n=sleeve_frame(S,C)
    return _add(_lerp(S,C,t),_mul(n,p["skew"]*_beta(t,2,2)))

def sleeve_section(p,t):
    e,n=sleeve_frame(tuple(p["authored_xy"]["S"]),tuple(p["authored_xy"]["C"]))
    c=sleeve_center(p,t);r=sleeve_radius(p,t)
    return _sub(c,_mul(n,r)),_add(c,_mul(n,r))

def sleeve_family(spec):
    p=spec;S,C=(tuple(p["authored_xy"][k]) for k in ("S","C"));e,n=sleeve_frame(S,C)
    A,B=sleeve_section(p,0);U,V=sleeve_section(p,1)
    cap=_bezier(A,_sub(A,_mul(e,p["cap_height"])),_sub(B,_mul(e,p["cap_height"])),B,20)
    ts=[i/24 for i in range(25)]
    side_a=[sleeve_section(p,t)[0] for t in ts]
    side_b=[sleeve_section(p,t)[1] for t in ts]
    outline=_clean_closed((*cap,*side_b[1:],*reversed(side_a[:-1])))
    edges=(_edge("silhouette",cap,"A-puff-sleeve","fullness cap generated from shoulder section and action direction"),
           _edge("silhouette",side_b,"A-puff-sleeve","fullness envelope narrows to shared cuff section"),
           _edge("silhouette",tuple(reversed(side_a)),"A-puff-sleeve","continuous sleeve opposite side"),
           _edge("contact",(U,V),"A-puff-sleeve","shared terminal cross-section with transverse cuff"),
           _edge("closure",(B,A),"A-puff-sleeve","generated shoulder-seat closure; not an ink seam"))
    return _geometry(outline,{"S":S,"cap_left":A,"cap_right":B,"C":C,"cuff_left":U,"cuff_right":V,"axis":e},edges,p.get("authored_input_xy",p["authored_xy"]),"puff-cap-fullness-envelope")

def cuff_family(spec,sleeve):
    C=tuple(sleeve.named_stations["C"]);e=tuple(sleeve.named_stations["axis"]);n=(-e[1],e[0])
    r=spec["cuff_radius"]+spec["band_ease"];d=spec["band_depth"]
    u=_sub(C,_mul(n,r));v=_add(C,_mul(n,r));lo_v=_add(_add(C,_mul(e,d)),_mul(n,r+1.5));lo_u=_add(_add(C,_mul(e,d)),_mul(n,-r-1.5))
    outline=_clean_closed((u,v,lo_v,lo_u))
    edges=(_edge("contact",(u,v),"A-transverse-cuff","shares the sleeve terminal section by an eased band"),
           _edge("silhouette",(v,lo_v),"A-transverse-cuff","short transverse cuff side"),
           _edge("silhouette",(lo_v,lo_u),"A-transverse-cuff","lower cuff free edge"),
           _edge("closure",(lo_u,u),"A-transverse-cuff","far cuff closure unknown; no full ring is asserted"))
    return _geometry(outline,{"C":C,"upper_left":u,"upper_right":v,"lower_left":lo_u,"lower_right":lo_v},edges,{},"shared-transverse-short-cuff")


def folded_loop(spec,name):
    a=spec["authored_xy"];G,E=(tuple(a[k]) for k in ("G","E"));axis=_sub(E,G);n=_normal(axis)
    g,W,b,d=(spec[k] for k in ("gather_half_width","free_half_width","bend","return_indentation"))
    def center(t): return _add(_lerp(G,E,t),_mul(n,b*math.sin(math.pi*t)))
    def width(t): return g*(1-t)+W*math.sin(math.pi*t/2)**0.95
    out=[];ret=[]
    for i in range(33):
        t=i/32;c=center(t);w=width(t);indent=d*_beta(t,1,4)*spec["fold_return"]
        out.append(_add(c,_mul(n,w)))
        ret.append(_add(c,_mul(n,-(w-indent))))
    free=(((out[-1][0]+ret[-1][0])/2+n[0]*2.5,(out[-1][1]+ret[-1][1])/2+n[1]*2.5),)
    outline=_clean_closed((*out,*free,*reversed(ret)))
    # A return-fold seam is generated toward gather; it is not a hand-drawn lobe decoration.
    fold=tuple(_lerp(ret[24],G,i/12) for i in range(13))
    edges=(_edge("free_edge",out,name,"gather-to-wide free-edge cloth flow"),
           _edge("free_edge",(out[-1],free[0],ret[-1]),name,"short free edge at the broad station"),
           _edge("fold_edge",tuple(reversed(ret)),name,"return-fold contracts back toward shared gather"),
           _edge("fold_edge",fold,name,"generated fold flow toward gather"),
           _edge("closure",(ret[0],out[0]),name,"gather overlap closure"))
    return _geometry(outline,{"G":G,"E":E,"root_half_width":g,"free_half_width":W,"return_start":ret[24]},edges,spec.get("authored_input_xy",a),"gather-free-edge-return-fold")


def gather_patch(G,spec):
    G=tuple(G);d=spec["gather_depth"];w=spec["gather_half_width"]
    pts=((G[0]-w,G[1]-d/2),(G[0]+w,G[1]-d/2),(G[0]+w*.55,G[1]+d/2),(G[0]-w*.55,G[1]+d/2))
    edges=(_edge("silhouette",pts,"A-bow-gather","short gathered wrap patch, not a rounded knot ball"),
           _edge("closure",(pts[3],pts[0]),"A-bow-gather","hidden gather wrap closure"))
    return _geometry(pts,{"G":G,"root_left":pts[0],"root_right":pts[1]},edges,{"G":G},"gathered-fold-wrap-patch")

def ribbon_outline(centerline,widths):
    left=[];right=[]
    for i,p in enumerate(centerline):
        before=centerline[max(0,i-1)];after=centerline[min(len(centerline)-1,i+1)]
        n=_normal(_sub(after,before));w=widths[i]
        left.append(_add(p,_mul(n,w)));right.append(_add(p,_mul(n,-w)))
    return tuple(left+list(reversed(right))),tuple(left),tuple(right)

def tension_tail(spec,G):
    G=tuple(G);off=tuple(spec["root_offset"]);P0=_add(G,off)
    gd=_unit(tuple(spec["gravity_direction"]));P3=_add(P0,_mul(gd,spec["length"]))
    root=_unit(off);P1=_add(P0,_mul(root,spec["root_tension"]))
    P2=_sub(P3,_mul(gd,spec["destination_return"]))
    line=_bezier(P0,P1,P2,P3,48)
    widths=tuple(spec["half_width"]*(1-.10*i/(len(line)-1)) for i in range(len(line)))
    outline,left,right=ribbon_outline(line,widths)
    edges=(_edge("silhouette",left,"A-down-tail","cubic tension edge from gather root toward crop continuation"),
           _edge("silhouette",tuple(reversed(right)),"A-down-tail","paired tension edge of the same cloth band"),
           _edge("closure",(left[-1],right[-1]),"A-down-tail","calculation closure below crop; terminal remains unknown"),
           _edge("contact",(left[0],right[0]),"A-down-tail","generated gathering attachment at the knot"))
    return _geometry(outline,{"P0":P0,"P1":P1,"P2":P2,"P3":P3,"centerline":line,"root_tangent":_unit(_sub(P1,P0))},edges,{},"cubic-tension-crop-continuation")

def local_pink_band(spec):
    a=spec["authored_xy"];T,L,X=(tuple(a[k]) for k in ("TBE2_local_neighborhood","LTA2_contact_neighborhood","crop_exit"))
    # Both teacher stations retain only their local roles. A low-dimensional artist cubic is not a recovered centerline.
    p1=_add(X,_mul(_unit(_sub(L,X)),_len(_sub(T,X))*.36))
    p2=_sub(T,_mul(_unit(_sub(T,L)),_len(_sub(T,X))*.36))
    combined=_bezier(X,p1,p2,T,48);width=spec["half_width"]
    outline,left,right=ribbon_outline(combined,tuple(width for _ in combined))
    edges=(_edge("silhouette",left,"A-pink-local-band","artist-route local pink band; no source-backed centerline"),
           _edge("silhouette",tuple(reversed(right)),"A-pink-local-band","paired edge of the local artist band"),
           _edge("closure",(left[-1],right[-1]),"A-pink-local-band","crop-exiting closure outside viewport"),
           _edge("closure",(right[0],left[0]),"A-pink-local-band","local generated root closure; not an attachment to blue"))
    return _geometry(outline,{"TBE2_neighborhood":T,"LTA2_neighborhood":L,"crop_exit":X,"centerline":combined},edges,a,"hypothesis-local-band")

def anonymous_blue_band(spec):
    a=spec["authored_xy"];P0,P3=(tuple(a[k]) for k in ("crop_entry","crop_exit"));c1,c2=(tuple(x) for x in spec["cubic_controls_xy"])
    line=_bezier(P0,c1,c2,P3,48);w=spec["half_width"]
    outline,left,right=ribbon_outline(line,tuple(w for _ in line))
    edges=(_edge("free_edge",left,"A-anonymous-blue-band","anonymous crop-exiting band edge; identity and attachment unknown"),
           _edge("free_edge",tuple(reversed(right)),"A-anonymous-blue-band","other edge of the independent crop-exiting band"),
           _edge("closure",(left[-1],right[-1]),"A-anonymous-blue-band","far edge closure lies outside crop"),
           _edge("closure",(right[0],left[0]),"A-anonymous-blue-band","entry closure lies outside crop"))
    inputs={"entry":P0,"exit":P3,"control_1":c1,"control_2":c2}
    return _geometry(outline,{"entry":P0,"exit":P3,"centerline":line},edges,inputs,"anonymous-independent-crop-band")

def _band_from_stations(spec,name):
    centers=tuple(tuple(p) for p in spec["authored_center_xy"]);widths=tuple(spec["half_widths"])
    line=_catmull_open(centers,14)
    # Interpolate the four semantic widths over the generated open curve, not a dense hand table.
    vals=[]
    for i in range(len(line)):
        t=i/(len(line)-1)*(len(widths)-1);j=min(len(widths)-2,int(t));f=t-j
        vals.append((1-f)*widths[j]+f*widths[j+1])
    outline,left,right=ribbon_outline(line,vals)
    edges=(_edge("silhouette",left,name,"narrow locally observed-context sheet edge"),
           _edge("silhouette",tuple(reversed(right)),name,"opposing context-sheet edge"),
           _edge("closure",(left[-1],right[-1]),name,"unknown hidden context closure"),
           _edge("closure",(right[0],left[0]),name,"crop-continuation closure"))
    inputs={f"station_{i}":p for i,p in enumerate(centers)}
    return _geometry(outline,{"centerline":line,"width_profile":widths},edges,inputs,"open-context-sheet-width-profile")

def hair_curlband(spec): return _band_from_stations(spec,"A-neck-curlband")
def hair_shoulder_sheet(spec): return _band_from_stations(spec,"A-right-shoulder-hair-sheet")


def signed_area(poly): return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))/2

def point_in_polygon(p,poly):
    inside=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]: inside=not inside
    return inside
