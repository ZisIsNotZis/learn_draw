#!/usr/bin/env python3
"""Build source-registered, annotation-only A teacher evidence; never runtime geometry."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "image.jpg"
OLD_REGISTERED = ROOT / ".scratch/35-r1-articulated-study/evidence/A-teacher-recovery-v1/teacher-only/source-crop-registered.png"
BOUNDS = (500, 320, 900, 800)
SOURCE_SHA = "322ad77c0cfd28fa040c625c55c592a54b3052ac4bea61fc31d967d8acff81fb"
CROP_SHA = "52e01f5e75e5d98fcd9a0a4ac63be91ed09b8a18ca0f62e7e0348a021b2dd87d"

# New coordinates are independent observations, not moved/relabelled legacy points.
POINTS = [
    ("NS2", "visible neck-skin field", "neck-skin", 218, 82, "interior", "Pink neck field visibly occupies the throat between lower face/hair and collar; local blue curl is not the point. Full skin boundary remains occluded." , "new observation; not legacy N1"),
    ("NO2", "visible lower neckline termination neighborhood", "neck-opening", 201, 123, "boundary-neighborhood", "At the visible pink-to-collar/dark-trim convergence; exact shared-boundary pixel and anatomy are uncertain.", "new observation; does not inherit N2 exact-point role"),
    ("CLI2", "left pale collar field", "left-collar", 174, 105, "interior", "Visible pale leaf surface, separately sampled away from the old CL1 background/edge neighborhood; outer attachment/endpoint not established.", "new observation; not legacy CL1/CL2"),
    ("CRI2", "right pale collar field", "right-collar", 250, 103, "interior", "Visible broad right pale-blue collar surface. No forced symmetry or internal leaf seam inferred.", "new observation; supports field only"),
    ("BOL2", "exposed left bodice silhouette neighborhood", "bodice", 102, 194, "boundary-neighborhood", "Visible pale garment meets teal field along exposed left torso contour, above the bow-tail crossing; continuation is hidden by bow/foreground below.", "new observation; not legacy BD1"),
    ("BPI2", "exposed left bodice cloth field", "bodice", 116, 177, "interior", "Pale cloth patch lies inside the visible garment to the right of the exposed outer contour; local dark strokes are not asserted as seams.", "new observation"),
    ("BPI3", "central lower bodice cloth field", "bodice", 244, 319, "interior", "Pale torso cloth is visible between bow/foreground forms and the sleeve; thin line is not identified as a seam.", "new observation; complements supported BD3 only as a local field"),
    ("BHE2", "visible lower bodice edge neighborhood", "bodice-lower-edge", 204, 402, "boundary-neighborhood", "A dark/color transition is visible at this internal-crop lower garment edge; do not extrapolate a complete hem or any crop-cut continuation.", "new observation; not legacy BD4"),
    ("SPI2", "right sleeve pale field", "right-sleeve", 346, 190, "interior", "Continuous pale sleeve surface is visible here; point does not divide cap from tube or establish an armhole seam.", "new observation; not legacy SC1"),
    ("SBO2", "sleeve outer/foreground adjacency neighborhood", "right-sleeve", 376, 220, "adjacency-neighborhood", "Sleeve edge approaches dark hair/teal background in this neighborhood; the point is not an exact sleeve-cap boundary and hair identity/occlusion is separated from cloth.", "new observation; conservative adjacency only"),
    ("LTI2", "leftward pink tail interior", "bow-left-tail", 104, 222, "interior", "Pink ribbon strip is visibly continuous at this station; continuation stops being identifiable at the pink/blue overlap toward crop x=44.", "new observation"),
    ("LTA2", "left-tail / blue-band contact neighborhood", "bow-left-tail-contact", 44, 209, "adjacency-neighborhood", "Visible pink/blue contact or overlap only. Pink endpoint/continuation and blue-band identity remain UNKNOWN; crop boundary is not a hem/tip.", "legacy TL1 coordinate, strictly narrowed from tail-tip-like role"),
    ("DTI2", "downward pink ribbon interior", "bow-down-tail", 157, 246, "interior", "Visible pink strip continues downward from knot through this interior station; the lower path approaches occluding foreground/dark forms.", "new observation"),
    ("DTO2", "down-tail terminal/occlusion neighborhood", "bow-down-tail", 158, 278, "unknown", "Pink ribbon's lower edge meets/overlaps dark/foreground forms. Exact terminal type and location UNKNOWN; no point-tip assertion.", "new uncertainty marker; not legacy TD1"),
    # Supported legacy observations carried only at their confirmed, limited roles.
    ("SEED-BD3", "right bodice pale patch", "bodice", 281, 245, "interior", "Supported legacy seed: pale torso cloth patch only; nearby thin mark may be fold, not seam.", "legacy BD3, restricted to field"),
    ("SEED-SC2", "continuous sleeve pale field", "right-sleeve", 360, 203, "interior", "Supported legacy seed: sleeve field only, not a cap/tube split.", "legacy SC2, restricted to field"),
    ("SEED-SC3", "sleeve-to-cuff approach neighborhood", "right-sleeve-cuff", 335, 278, "adjacency-neighborhood", "Supported legacy seed: approach to cuff only; no exact cuff edge or seam inferred.", "legacy SC3, neighborhood only"),
    ("SEED-CU1", "dark cuff band", "cuff", 373, 309, "interior", "Supported legacy seed: visible band field; full ring/far side/right continuation are unknown.", "legacy CU1, band interior only"),
    ("SEED-BK1", "bow gather neighborhood", "bow-knot", 171, 169, "adjacency-neighborhood", "Supported legacy seed: pink gathered/overlap neighborhood, not hidden wrap construction.", "legacy BK1, gather only"),
    ("SEED-BL1", "left bow loop field", "bow-left-loop", 139, 171, "interior", "Supported legacy seed: visible pink lobe interior; does not set exact outer boundary.", "legacy BL1, field only"),
    ("SEED-BR1", "right bow loop field", "bow-right-loop", 230, 183, "interior", "Supported legacy seed: visible pink lobe interior; no precise width ratio from one point.", "legacy BR1, field only"),
    ("LFE2", "left loop free-edge neighborhood", "bow-left-loop", 120, 177, "boundary-neighborhood", "Visible outer pink lobe edge is locally adjacent to pale bodice; exact edge/stroke center is not claimed.", "new observation; outer free edge only"),
    ("RFE2", "right loop free-edge neighborhood", "bow-right-loop", 268, 183, "boundary-neighborhood", "Visible outer pink lobe edge is locally adjacent to pale bodice; overlap near knot and lower fold remain distinct.", "new observation; outer free edge only"),
    ("TBE2", "left tail lower-band edge neighborhood", "bow-left-tail", 86, 231, "boundary-neighborhood", "Visible lower edge of the pink strip at this interior-crop station; tail remains a band here, contact/continuation at LTA2 is unknown.", "new observation; not an endpoint"),
]

REGIONS = [
    {"id":"neck-collar-opening", "xyxy":[150,30,330,155], "reading":"context window for visible pink neck field, two unequal pale collar fields, dark trim and lower opening; not a segmentation mask"},
    {"id":"bodice-left-and-lower", "xyxy":[60,125,310,430], "reading":"context window for exposed left garment silhouette, bodice interior and visible lower edge; interruptions/foreground remain explicit"},
    {"id":"sleeve-and-cuff", "xyxy":[290,105,400,350], "reading":"context window for continuous pale sleeve field, partial silhouette and dark cuff; no invented cap seam or complete cuff"},
    {"id":"bow-and-tails", "xyxy":[0,130,285,305], "reading":"context window for knot, unequal visible loops, left pink/blue contact, down-tail and terminal occlusion; no forced endpoints"},
]

# Open manual teacher pointers over clearly visible intervals only. They are NOT fitted contours.
TRACES = [
    {"id":"bodice-left-visible-interval", "part":"bodice", "crop_xy":[[123,140],[113,169],[96,202],[87,222],[95,239]], "status":"approximate visible outer-edge neighborhood; bow/overlap terminates observation; not a complete silhouette"},
    {"id":"bodice-lower-visible-interval", "part":"bodice-lower-edge", "crop_xy":[[145,397],[174,405],[205,406],[236,401],[250,396]], "status":"approximate visible lower dark/color edge interval; not a crop-cut hem or inferred complete hem"},
    {"id":"left-loop-outer-free-edge", "part":"left bow loop", "crop_xy":[[128,145],[122,157],[120,177],[124,194],[137,205]], "status":"approximate short visible outer lobe edge only; stops before gathered overlap, not a closed loop contour"},
    {"id":"right-loop-outer-free-edge", "part":"right bow loop", "crop_xy":[[265,166],[270,180],[268,194],[258,213],[243,228]], "status":"approximate visible outer lobe edge only; overlap and lower continuation are not completed"},
    {"id":"leftward-tail-centerline-visible", "part":"pink left tail", "crop_xy":[[167,197],[143,209],[116,220],[88,226],[63,216],[45,209]], "status":"approximate pink interior direction ending at contact neighborhood; stops at pink/blue ambiguity, not a tail endpoint claim"},
    {"id":"down-tail-centerline-visible", "part":"pink down tail", "crop_xy":[[169,195],[174,218],[166,240],[157,259],[158,274]], "status":"approximate center direction only; terminates at UNKNOWN overlap neighborhood, not a point tip"},
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rgb(image: Image.Image, x: int, y: int) -> list[int]:
    return list(image.getpixel((x, y)))


def font(size: int = 13):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def main() -> None:
    src_hash = sha(SOURCE)
    assert src_hash == SOURCE_SHA, f"unexpected source hash: {src_hash}"
    source = Image.open(SOURCE).convert("RGB")
    assert source.size == (1024, 1024)
    crop = source.crop(BOUNDS)
    assert crop.size == (400, 480)
    assert sha(OLD_REGISTERED) == CROP_SHA
    old_crop = Image.open(OLD_REGISTERED).convert("RGB")
    assert crop.tobytes() == old_crop.tobytes(), "new registered crop differs from preserved crop"
    assert hashlib.sha256(crop.tobytes()).hexdigest() == hashlib.sha256(old_crop.tobytes()).hexdigest()

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "raw-patches").mkdir(exist_ok=True)
    (OUT / "raw-regions").mkdir(exist_ok=True)
    crop.save(OUT / "pristine-fullcrop.png")

    point_json = []
    csv_rows = []
    for pid, label, part, x, y, kind, trigger, lineage in POINTS:
        assert 0 <= x < 400 and 0 <= y < 480
        source_xy = [500 + x, 320 + y]
        assert rgb(source, source_xy[0], source_xy[1]) == rgb(crop, x, y), f"mapping mismatch for {pid}"
        # Unresampled 11x11 raw source neighborhood (edge-clipped only if needed).
        box = (max(0, x - 5), max(0, y - 5), min(400, x + 6), min(480, y + 6))
        patch = crop.crop(box)
        patch_path = OUT / "raw-patches" / f"{pid}.png"
        patch.save(patch_path)
        offsets = {"N":(0,-3),"NE":(3,-3),"E":(3,0),"SE":(3,3),"S":(0,3),"SW":(-3,3),"W":(-3,0),"NW":(-3,-3)}
        neighbors = {}
        for direction,(dx,dy) in offsets.items():
            nx, ny = x + dx, y + dy
            neighbors[direction] = {"crop_xy":[nx,ny], "source_xy":[500+nx,320+ny], "rgb":rgb(crop,nx,ny)}
        record = {
            "id":pid, "label":label, "part":part, "crop_xy":[x,y], "source_xy":source_xy,
            "type":kind, "visual_trigger_and_limit":trigger, "lineage":lineage,
            "point_rgb":rgb(crop,x,y), "neighbor_samples_3px":neighbors,
            "raw_patch":"raw-patches/"+patch_path.name, "raw_patch_sha256":sha(patch_path),
            "patch_crop_xyxy":list(box),
            "interpretation_rule":"RGB/neighborhood values verify the sampled source pixels only; semantic label comes from visible spatial context and requires fresh review."
        }
        point_json.append(record)
        csv_rows.append({"id":pid,"label":label,"part":part,"type":kind,"crop_x":x,"crop_y":y,"source_x":source_xy[0],"source_y":source_xy[1],"rgb_hex":"#%02x%02x%02x"%tuple(record["point_rgb"]),"raw_patch":record["raw_patch"],"raw_patch_sha256":record["raw_patch_sha256"],"visual_trigger_and_limit":trigger,"lineage":lineage})

    with (OUT / "landmarks.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0]))
        writer.writeheader(); writer.writerows(csv_rows)
    (OUT / "landmarks-and-neighbors.json").write_text(json.dumps(point_json, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")

    region_records = []
    for region in REGIONS:
        x0,y0,x1,y1 = region["xyxy"]
        assert 0 <= x0 < x1 <= 400 and 0 <= y0 < y1 <= 480
        patch = crop.crop((x0,y0,x1,y1))
        path = OUT / "raw-regions" / f"{region['id']}.png"
        patch.save(path)
        region_records.append({**region,"source_xyxy":[500+x0,320+y0,500+x1,320+y1],"raw_patch":f"raw-regions/{path.name}","sha256":sha(path),"pixels":(x1-x0)*(y1-y0),"resampling":"none; raw crop pixels"})
    (OUT / "regions.json").write_text(json.dumps(region_records, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")

    (OUT / "manual-traces.json").write_text(json.dumps(TRACES, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    scale = 2
    crop_display = crop.resize((800,960), Image.Resampling.NEAREST).convert("RGB")
    canvas = Image.new("RGB", (1200, 960), (250, 250, 247))
    canvas.paste(crop_display, (0, 0))
    draw = ImageDraw.Draw(canvas)
    colors = {"interior":(35,120,210),"boundary-neighborhood":(242,140,20),"adjacency-neighborhood":(20,155,105),"unknown":(180,35,55)}
    # Draw open, hand-entered approximate pointers only; never close as a segmentation.
    for trace in TRACES:
        pts = [(int(x*scale),int(y*scale)) for x,y in trace["crop_xy"]]
        for a,b in zip(pts,pts[1:]):
            dx,dy=b[0]-a[0],b[1]-a[1]; length=max(1,int((dx*dx+dy*dy)**0.5))
            for t in range(0,length,10):
                if (t//10)%2==0:
                    t2=min(length,t+5); draw.line((a[0]+dx*t/length,a[1]+dy*t/length,a[0]+dx*t2/length,a[1]+dy*t2/length),fill=(245,210,35),width=2)
    for pid,label,part,x,y,kind,trigger,lineage in POINTS:
        X,Y=x*scale,y*scale; c=colors[kind]
        draw.ellipse((X-5,Y-5,X+5,Y+5),outline=c,width=3)
        draw.text((X+7,Y-13),pid,fill=(0,0,0),font=font(),stroke_width=2,stroke_fill=(255,255,255))
    # Region boxes are view windows only, not semantic masks.
    for r in REGIONS:
        x0,y0,x1,y1=r["xyxy"]
        draw.rectangle((x0*scale,y0*scale,x1*scale,y1*scale),outline=(220,50,190),width=1)
    # A separate legend keeps all crop labels visible without modifying the pristine/source pixels.
    panel_x = 820
    draw.text((panel_x, 18), "A teacher reconstruction v2", fill=(20,20,20), font=font(17))
    draw.text((panel_x, 52), "2x crop at left; marks are teacher pointers, not masks.", fill=(30,30,30), font=font(12))
    y = 88
    for kind, color in colors.items():
        draw.ellipse((panel_x, y+2, panel_x+12, y+14), outline=color, width=3)
        draw.text((panel_x+20, y), kind, fill=(20,20,20), font=font(12)); y += 24
    y += 12
    draw.text((panel_x, y), "Magenta boxes = raw context windows", fill=(20,20,20), font=font(12)); y += 25
    for region in REGIONS:
        x0,y0,x1,y1=region["xyxy"]
        draw.text((panel_x, y), f"{region['id']}: ({x0},{y0})–({x1},{y1})", fill=(20,20,20), font=font(11)); y += 20
    y += 18
    draw.text((panel_x, y), "Yellow dashed traces: open, approximate", fill=(20,20,20), font=font(11)); y += 18
    draw.text((panel_x, y), "visible intervals only; not runtime geometry.", fill=(20,20,20), font=font(11)); y += 28
    draw.text((panel_x, y), "Point RGB/neighbor samples verify lookup,", fill=(20,20,20), font=font(11)); y += 18
    draw.text((panel_x, y), "not semantic identity. UNKNOWN stays unknown.", fill=(20,20,20), font=font(11))
    canvas.save(OUT / "teacher-overlay.png")

    checks = {
        "source":str(SOURCE.relative_to(ROOT)),"source_sha256":src_hash,"source_dimensions":[1024,1024],
        "crop_source_xyxy_exclusive":list(BOUNDS),"crop_dimensions":[400,480],
        "registered_crop_sha256":sha(OUT/"pristine-fullcrop.png"),
        "crop_pixel_bytes_sha256":hashlib.sha256(crop.tobytes()).hexdigest(),
        "registered_png_sha256":sha(OUT/"pristine-fullcrop.png"),
        "old_registered_crop_sha256":sha(OLD_REGISTERED),"old_new_all_pixels_identical":crop.tobytes()==old_crop.tobytes(),
        "crop_to_source":"source=(500+crop_x,320+crop_y)","point_count":len(point_json),"region_count":len(region_records),
        "analysis_only":"No pixel segmentation, RGB thresholding, fitted geometry, engine input, image generation, or artwork was produced. Region rectangles are context patches; manual lines are open approximate teacher pointers.",
        "point_checks":point_json,"regions":region_records,
        "files":{}
    }
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "provenance.json":
            checks["files"][str(path.relative_to(OUT))]=sha(path)
    (OUT/"provenance.json").write_text(json.dumps(checks,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"PASS source={src_hash} crop=400x480 exact=true points={len(point_json)} regions={len(region_records)}")

if __name__ == "__main__":
    main()
