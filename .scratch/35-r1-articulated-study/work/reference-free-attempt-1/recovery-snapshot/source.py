"""Original authored vector illustration; all coordinates are semantic local art."""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

from scripts.articulated_construction import (
    Camera, Component, LimbParameters, Point, SupportFrame, component_faces,
    construct_limb, triangulate_polygon, visible_scene_regions,
)
from scripts.articulated_line_visibility import visible_segment_spans

HERE = Path(__file__).resolve().parent
CAMERA = Camera()


@dataclass(frozen=True)
class Stroke:
    name: str
    intent: str
    owner: str
    points: tuple[Point, ...]
    color: str = "#273c46"
    width: float = 0.018
    closed: bool = False


def smooth_quad(corners: tuple[Point, Point, Point, Point], steps: int = 8) -> tuple[Point, ...]:
    """Centripetal-style Catmull sample from four semantic corners, not a dense point list."""
    out = []
    for i, p1 in enumerate(corners):
        p0, p2, p3 = corners[(i - 1) % 4], corners[(i + 1) % 4], corners[(i + 2) % 4]
        for j in range(steps):
            t = j / steps
            t2, t3 = t * t, t * t * t
            vals = []
            for a, b, c, d in ((p0.u, p1.u, p2.u, p3.u), (p0.v, p1.v, p2.v, p3.v)):
                vals.append(0.5 * ((2*b) + (-a+c)*t + (2*a-5*b+4*c-d)*t2 + (-a+3*b-3*c+d)*t3))
            out.append(Point(*vals))
    return tuple(out)


def ellipse(rx: float, ry: float, count: int = 48, angle: float = 0.0) -> tuple[Point, ...]:
    """A named oval family; radii and rotation generate the complete closed boundary."""
    ca, sa = math.cos(angle), math.sin(angle)
    return tuple(Point(rx*math.cos(2*math.pi*i/count)*ca - ry*math.sin(2*math.pi*i/count)*sa,
                      rx*math.cos(2*math.pi*i/count)*sa + ry*math.sin(2*math.pi*i/count)*ca)
                 for i in range(count))


def bezier(a: Point, b: Point, c: Point, d: Point, count: int = 24) -> tuple[Point, ...]:
    """Sample a four-anchor semantic curve for the breeze and soft tapered marks."""
    result = []
    for i in range(count + 1):
        t = i / count
        q = 1 - t
        result.append(Point(q**3*a.u + 3*q*q*t*b.u + 3*q*t*t*c.u + t**3*d.u,
                            q**3*a.v + 3*q*q*t*b.v + 3*q*t*t*c.v + t**3*d.v))
    return tuple(result)


def tube_from_curve(spine: tuple[Point, ...], start_width: float, end_width: float) -> tuple[Point, ...]:
    """Generate a closed, smoothly tapered local shape from a semantic centerline."""
    left, right = [], []
    last = len(spine) - 1
    for i, p in enumerate(spine):
        tangent = spine[min(i+1, last)] - spine[max(i-1, 0)]
        mag = math.hypot(tangent.u, tangent.v)
        if mag <= 1e-10:
            raise ValueError("curve contains a degenerate tangent")
        width_t = i / last
        ease = width_t * width_t * (3 - 2 * width_t)
        width = start_width + (end_width - start_width) * ease
        normal = Point(-tangent.v / mag, tangent.u / mag)
        left.append(p + normal.scale(width))
        right.append(p - normal.scale(width))
    return tuple(left + list(reversed(right)))


def support(name: str, origin: tuple[float, float, float]) -> SupportFrame:
    return SupportFrame(f"{name}-surface", f"{name}-depth", origin=origin)


def component(name: str, intent: str, origin: tuple[float, float, float], outline: tuple[Point, ...], fill: str,
              anchors: tuple[tuple[str, Point], ...] = (),
              attachments: tuple[tuple[str, str, str], ...] = ()) -> Component:
    return Component(name, intent, support(name, origin), outline, fill, attachments, anchors)


def shifted(points: tuple[Point, ...], origin: Point) -> tuple[Point, ...]:
    return tuple(p - origin for p in points)


def limb_components(name: str, intent: str, start: Point, end: Point,
                    upper_length: float, fore_length: float, branch: int,
                    support_z: float, fill: str, end_z: float):
    depth_slope = (end_z-support_z)/(end.v-start.v) if abs(end.v-start.v)>1e-9 else 0.0
    frame = SupportFrame(f"{name}-surface",f"{name}-depth",(start.u,start.v,support_z),
                         (1.0,0.0,0.0),(0.0,1.0,depth_slope))
    result = construct_limb(LimbParameters(
        shoulder=Point(0.0, 0.0), upper_length=upper_length, fore_length=fore_length,
        hand_target=end-start, elbow_branch=branch,
        upper_width_shoulder=0.115, upper_width_elbow=0.09,
        fore_width_elbow=0.082, fore_width_wrist=0.056, support=frame,
    ))
    upper = Component(f"{name}_upper", f"{intent}: shoulder-to-elbow sleeve", frame,
                      result.upper_arm.outline, fill,
                      anchors=(("shoulder", Point(0, 0)), ("elbow", result.elbow)))
    elbow_world = frame.local_to_world(result.elbow)
    fore_frame = SupportFrame(f"{name}-forearm-surface",f"{name}-forearm-depth",elbow_world,
                              (1.0,0.0,0.0),(0.0,1.0,depth_slope))
    fore = Component(f"{name}_forearm", f"{intent}: elbow-to-wrist sleeve", fore_frame,
                     shifted(result.forearm.outline, result.elbow), fill,
                     anchors=(("elbow", Point(0, 0)), ("wrist", end-start-result.elbow)),
                     attachments=((f"{name}_upper", "elbow", "elbow"),))
    return upper, fore, result.elbow


def build_scene() -> tuple[tuple[Component, ...], tuple[Stroke, ...], dict]:
    parts: list[Component] = []
    strokes: list[Stroke] = []

    # A quiet, warm paper field and a generated sun-disc establish the portrait's stage.
    parts.append(component("paper", "unbroken warm background field", (0, 0, -3.0),
                           (Point(-2.08,-2.55), Point(2.08,-2.55), Point(2.08,2.75), Point(-2.08,2.75)), "#f5f0e5"))
    parts.append(component("sun_disc", "soft circular accent behind the figure", (-0.1,0.15,-2.0),
                           ellipse(1.02,1.42,64), "#e4eee5"))
    parts.append(component("ground_shadow", "small grounding shadow below the shoes", (-0.12,-1.79,-0.8),
                           ellipse(0.77,0.105,48), "#d6d9cf"))

    # Two curved trouser legs grow from the jacket hem; four anchors author each spine.
    left_hip, left_ankle = Point(-0.47,-0.48), Point(-0.57,-1.73)
    left_spine = bezier(left_hip, Point(-0.54,-0.86), Point(-0.46,-1.28), left_ankle)
    left_frame = support("left-trouser", (left_hip.u,left_hip.v,0.05))
    left_leg = Component("left_trouser", "tapered cloth from hip to planted ankle", left_frame,
                         shifted(tube_from_curve(left_spine,0.215,0.12),left_hip), "#47757a")
    parts.append(left_leg)
    right_hip, right_ankle = Point(-0.02,-0.48), Point(0.39,-1.69)
    right_spine = bezier(right_hip, Point(0.08,-0.85), Point(0.43,-1.21), right_ankle)
    right_frame = support("right-trouser", (right_hip.u,right_hip.v,0.06))
    right_leg = Component("right_trouser", "slightly bent cloth leg balancing the stance", right_frame,
                          shifted(tube_from_curve(right_spine,0.21,0.12),right_hip), "#47757a")
    parts.append(right_leg)
    parts.append(component("left_shoe", "rounded dark left shoe", (-0.66,-1.76,0.16),
                           smooth_quad((Point(-0.10,-0.12),Point(0.16,-0.10),Point(0.21,0.02),Point(-0.07,0.08))), "#324751"))
    parts.append(component("right_shoe", "rounded dark right shoe", (0.32,-1.73,0.16),
                           smooth_quad((Point(-0.10,-0.12),Point(0.19,-0.10),Point(0.22,0.01),Point(-0.08,0.07))), "#324751"))

    # Four semantic corner anchors generate a gentle jacket silhouette.
    torso_origin = Point(-0.22,0.08)
    torso_support = support("jacket", (torso_origin.u,torso_origin.v,0.12))
    jacket_shape = smooth_quad((Point(-0.48,-0.55), Point(0.53,-0.53), Point(0.42,0.55), Point(-0.39,0.63)))
    jacket = Component("jacket", "short tailored outer layer with a readable waist and shoulders",
                       torso_support, jacket_shape, "#6e9a91",
                       anchors=(("left_shoulder",Point(-0.36,0.37)),("right_shoulder",Point(0.35,0.44)),
                                ("hem",Point(0,-0.53))))
    parts.append(jacket)
    # Neck and face are separate local ovals; their support depths establish the overlap.
    parts.append(component("neck", "visible neck joining head and jacket", (-0.25,0.72,0.16),
                           ellipse(0.15,0.28), "#dfad8d"))
    head_center = Point(-0.27,1.23)
    parts.append(component("hair_back", "dark hair mass behind the face", (head_center.u,head_center.v,0.18),
                           ellipse(0.43,0.52,56), "#334550"))
    parts.append(component("face", "warm oval face framed by hair", (head_center.u,head_center.v,0.22),
                           ellipse(0.325,0.42,56,angle=-0.06), "#edc4a0"))
    # The cap is a generated upper arc with four authored lower fringe notches.
    cap_points = [Point(0.40*math.cos(math.pi*i/32),0.48*math.sin(math.pi*i/32)+0.015) for i in range(33)]
    cap_points.extend(bezier(Point(-0.40,0.015),Point(-0.27,-0.20),Point(0.18,-0.20),Point(0.40,0.015),24)[1:-1])
    parts.append(component("hair_cap", "swept fringe and upper hair silhouette", (head_center.u,head_center.v+0.03,0.28),
                           tuple(cap_points), "#334550"))

    # Raised arm comes from a two-link IK construction; both segments share a true elbow anchor.
    raised_shoulder, wrist = Point(0.13,0.52), Point(0.70,1.70)
    upper, forearm, elbow = limb_components("raised_arm", "raised arm reaching toward the hat",
                                            raised_shoulder,wrist,0.88,0.83,1,0.12,"#6e9a91",0.72)
    upper = Component(upper.name,upper.intent,upper.support,upper.outline,upper.fill,
                      attachments=(("jacket","shoulder","right_shoulder"),),anchors=upper.anchors)
    parts.extend((upper,forearm))

    # The other arm rests low, separating the raised gesture from the body's edge.
    low_shoulder, low_wrist = Point(-0.58,0.45), Point(-0.82,-0.18)
    low_upper, low_forearm, low_elbow = limb_components("resting_arm", "lower resting sleeve along the jacket side",
                                                        low_shoulder,low_wrist,0.49,0.57,-1,0.12,"#6e9a91",0.30)
    low_upper = Component(low_upper.name,low_upper.intent,low_upper.support,low_upper.outline,low_upper.fill,
                          attachments=(("jacket","shoulder","left_shoulder"),),anchors=low_upper.anchors)
    parts.extend((low_upper,low_forearm))
    parts.append(component("resting_hand", "small relaxed hand at the lowered wrist", (low_wrist.u,low_wrist.v,0.30),
                           ellipse(0.105,0.14,32), "#dfad8d",
                           anchors=(("wrist",Point(0,0)),),
                           attachments=(("resting_arm_forearm","wrist","wrist"),)))

    # Hat support and palm support share the same authored contact world point.
    hat_origin = Point(0.79,1.99)
    hat_frame = support("hat", (hat_origin.u,hat_origin.v,0.72))
    brim = Component("hat_brim", "tilted oval brim with an exposed touch point", hat_frame,
                     ellipse(0.76,0.115,64,angle=0.11), "#d99a52",
                     anchors=(("touch",Point(0.15,-0.065)),("crown_seat",Point(0,0.05))))
    crown = Component("hat_crown", "small slanted crown rising from the brim", hat_frame,
                      smooth_quad((Point(-0.37,0.02),Point(0.35,0.12),Point(0.24,0.62),Point(-0.20,0.57))), "#c47c43",
                      anchors=(("base",Point(0,0.05)),), attachments=(("hat_brim","base","crown_seat"),))
    parts.extend((brim,crown))
    contact = Point(0.15,-0.065)
    hand_frame = support("steadying_hand", (wrist.u,wrist.v,0.72))
    fingertip = Point(0.24,0.225)
    hand_spine = bezier(Point(0,0),Point(0.13,0.03),Point(0.22,0.14),fingertip,16)
    palm_shape = tube_from_curve(hand_spine,0.092,0.052)
    hand = Component("steadying_hand", "palm and curved fingertips meet the brim at one contact anchor",
                     hand_frame,palm_shape,"#edc4a0",
                     anchors=(("wrist",Point(0,0)),("hat_touch",fingertip)),
                     attachments=(("raised_arm_forearm","wrist","wrist"),("hat_brim","hat_touch","touch")))
    parts.append(hand)

    # Wind is authored as two slender, generated curved bands, not as an occlusion cut.
    for name, anchors, width in (
        ("breeze_high",(Point(-1.65,2.25),Point(-1.10,2.63),Point(-0.42,2.45),Point(0.08,2.55)),0.025),
        ("breeze_low",(Point(-1.72,1.78),Point(-1.20,2.03),Point(-0.82,1.83),Point(-0.51,1.91)),0.018),
    ):
        spine = bezier(*anchors)
        base = anchors[0]
        frame = support(name,(base.u,base.v,-0.55))
        band = Component(name, "flowing wind mark indicating a gust across the pose", frame,
                         shifted(tube_from_curve(spine,width,width*0.35),base), "#a8c8c2")
        parts.append(band)

    # Explicit contour intentions: only these authored semantic boundaries receive ink.
    outline_specs = (
        ("jacket", "jacket silhouette seam", 0.022),
        ("face", "face contour", 0.017),
        ("hair_cap", "fringe edge", 0.023),
        ("hat_brim", "hat brim edge", 0.019),
        ("hat_crown", "crown edge", 0.019),
    )
    by_name = {p.name:p for p in parts}
    for owner, intent, width in outline_specs:
        shape = by_name[owner]
        strokes.append(Stroke(f"{owner}_contour",intent,owner,shape.outline,"#344650",width,True))

    # Face features and garment seams are named authored lines on their owning supports.
    strokes.extend((
        Stroke("eye_left", "small attentive eye", "face", (Point(-0.17,0.045),Point(-0.105,0.04)), width=0.018),
        Stroke("eye_right", "small attentive eye", "face", (Point(0.045,0.055),Point(0.11,0.05)), width=0.018),
        Stroke("nose_mark", "quiet nose contour", "face", (Point(0.00,0.01),Point(-0.025,-0.075)), width=0.012),
        Stroke("smile_mark", "calm closed smile", "face", (Point(-0.065,-0.15),Point(0.01,-0.17),Point(0.075,-0.145)), width=0.012),
        Stroke("jacket_lapel", "overlapping lapel seam", "jacket", (Point(-0.19,0.46),Point(0.00,0.13),Point(0.20,0.48)), width=0.018),
        Stroke("jacket_center", "short center opening seam", "jacket", (Point(0.00,0.13),Point(0.03,-0.43)), width=0.012),
    ))

    # Supports are distinct names and real affine mappings; contact values are checked below.
    metadata = {
        "canvas": {"width":600,"height":760,"world_to_canvas":"translate(300 450) scale(140 -140)"},
        "camera": "orthographic default X-right/Y-up/Z-toward-viewer",
        "contact": {"component_a":"steadying_hand","anchor_a":"hat_touch",
                    "component_b":"hat_brim","anchor_b":"touch"},
        "ik": {"raised_elbow": [elbow.u+raised_shoulder.u, elbow.v+raised_shoulder.v],
               "resting_elbow": [low_elbow.u+low_shoulder.u,low_elbow.v+low_shoulder.v]},
    }
    return tuple(parts),tuple(strokes),metadata


def point_world(part: Component, p: Point) -> tuple[float,float,float]:
    return part.support.local_to_world(p)


def validate_scene(parts: tuple[Component,...], strokes: tuple[Stroke,...], metadata: dict) -> None:
    names = [p.name for p in parts]
    if len(names) != len(set(names)):
        raise ValueError("component names must be unique")
    by_name = {p.name:p for p in parts}
    for part in parts:
        if not part.name or not part.intent or not part.support.support_id or not part.support.depth_ref:
            raise ValueError("every component requires semantic identity and support")
        if len(part.outline) < 3 or not all(math.isfinite(v) for p in part.outline for v in (p.u,p.v)):
            raise ValueError(f"invalid authored outline: {part.name}")
        try:
            triangulate_polygon(part.outline)
        except ValueError as exc:
            raise ValueError(f"invalid polygon for {part.name}: {exc}") from exc
        for target, own_anchor, target_anchor in part.attachments:
            if target not in by_name:
                raise ValueError(f"unknown attachment target on {part.name}")
            if own_anchor not in dict(part.anchors) or target_anchor not in dict(by_name[target].anchors):
                raise ValueError(f"unresolved named attachment on {part.name}")
    for stroke in strokes:
        if not stroke.name or not stroke.intent or stroke.owner not in by_name or len(stroke.points)<2:
            raise ValueError(f"invalid semantic art line: {stroke.name}")
    faces = component_faces(parts,CAMERA)
    if not faces:
        raise ValueError("scene must reach the support-mapped visibility engine")
    # Distinct support origins and varying actual projected depths prove local art reaches world/camera.
    if len({p.support.support_id for p in parts}) < 3:
        raise ValueError("scene must bind artwork to multiple named support frames")
    projected = [CAMERA.project(p.support.local_to_world(p.outline[0])) for p in parts]
    if len({round(p[2],6) for p in projected}) < 3:
        raise ValueError("scene requires actual support-derived depth variation")
    for part in parts:
        for target, own_anchor, target_anchor in part.attachments:
            q0 = point_world(part,dict(part.anchors)[own_anchor])
            q1 = point_world(by_name[target],dict(by_name[target].anchors)[target_anchor])
            if math.dist(q0,q1) > 1e-8:
                raise ValueError(f"attachment world points do not coincide: {part.name} -> {target}")
    hand, brim = by_name["steadying_hand"],by_name["hat_brim"]
    p0 = point_world(hand,dict(hand.anchors)["hat_touch"])
    p1 = point_world(brim,dict(brim.anchors)["touch"])
    if math.dist(p0,p1)>1e-8:
        raise ValueError("declared hand-to-brim contact must coincide in world space")
    # Every non-paper authored contour must fit the final SVG viewBox after its world mapping.
    for part in parts:
        if part.name == "paper":
            continue
        for local in part.outline:
            x,y,_depth = CAMERA.project(part.support.local_to_world(local))
            screen_x,screen_y = 300 + 140*x, 450 - 140*y
            if not (0 <= screen_x <= 600 and 0 <= screen_y <= 760):
                raise ValueError(f"authored contour leaves the canvas: {part.name}")
    for poly, _color, _name in visible_scene_regions(parts,CAMERA):
        if not poly:
            raise ValueError("visibility engine returned an empty path")


def svg_text(parts: tuple[Component,...], strokes: tuple[Stroke,...], metadata: dict) -> str:
    faces = component_faces(parts,CAMERA)
    regions = visible_scene_regions(parts,CAMERA)
    contents = []
    for path_data,color,owner in regions:
        contents.append(f'<path data-part="{owner}" d="{path_data}" fill="{color}"/>')
    by_name = {p.name:p for p in parts}
    for stroke in strokes:
        owner = by_name[stroke.owner]
        points = stroke.points
        edges = list(zip(points,points[1:]))
        if stroke.closed:
            edges.append((points[-1],points[0]))
        for a,b in edges:
            q0 = CAMERA.project(owner.support.local_to_world(a))
            q1 = CAMERA.project(owner.support.local_to_world(b))
            for lo,hi in visible_segment_spans(q0,q1,faces,stroke.owner):
                x0,y0 = q0[0]+(q1[0]-q0[0])*lo, q0[1]+(q1[1]-q0[1])*lo
                x1,y1 = q0[0]+(q1[0]-q0[0])*hi, q0[1]+(q1[1]-q0[1])*hi
                contents.append(f'<path data-line="{stroke.name}" d="M {x0:.6f} {y0:.6f} L {x1:.6f} {y1:.6f}" fill="none" stroke="{stroke.color}" stroke-width="{stroke.width:.4f}" stroke-linecap="round"/>')
    return "\n".join((
        '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="760" viewBox="0 0 600 760">',
        '<title>Original programmatic illustration</title>',
        '<g transform="translate(300 450) scale(140 -140)">',
        *contents,
        '</g>',
        '</svg>',
        '',
    ))


def build() -> tuple[tuple[Component,...],tuple[Stroke,...],dict]:
    parts,strokes,metadata = build_scene()
    validate_scene(parts,strokes,metadata)
    return parts,strokes,metadata


def main() -> None:
    parts,strokes,metadata = build()
    out = HERE / "artwork.svg"
    out.write_text(svg_text(parts,strokes,metadata),encoding="utf-8")
    manifest = {
        "status":"created",
        "source":"source.py",
        "svg":"artwork.svg",
        "png":"artwork.png",
        "components":[{"name":p.name,"intent":p.intent,"support":p.support.support_id,
                       "depth_ref":p.support.depth_ref,"origin":p.support.origin,
                       "anchors":[[n,[q.u,q.v]] for n,q in p.anchors],"attachments":p.attachments}
                      for p in parts],
        "semantic_lines":[{"name":s.name,"intent":s.intent,"owner":s.owner} for s in strokes],
        "construction":metadata,
    }
    (HERE/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")


if __name__ == "__main__":
    main()
