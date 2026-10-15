"""Teacher-only registered crop and coarse semantic ROI map; never imported by renderer."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "image.jpg"
SOURCE_SHA = "322ad77c0cfd28fa040c625c55c592a54b3052ac4bea61fc31d967d8acff81fb"
BOUNDS = (500, 320, 900, 800)
FOCUS = (74, 65, 384, 418)  # registered crop-local bounds, collar through lower bodice and sleeve cuff
REGIONS = {
    "bodice-and-shoulder": ((82, 112, 331, 405), "central light garment panel; neckline to curved hem"),
    "right-sleeve-cap": ((267, 106, 352, 286), "puffed right sleeve attached to shoulder panel"),
    "right-cuff": ((326, 278, 399, 331), "dark band at the sleeve opening"),
    "visible-neck-skin": ((196, 38, 276, 130), "small source-visible skin region inside the collar opening"),
    "layered-collar": ((122, 61, 311, 143), "cool pale folded collar under the neck"),
    "bow-and-tails": ((39, 133, 273, 286), "pink paired loops, central gather and descending cloth tails"),
}
COLORS = [(235, 190, 125), (242, 132, 183), (64, 60, 67), (112, 202, 235), (250, 145, 125), (215, 120, 130)]


def main():
    raw = SOURCE.read_bytes()
    actual_sha = hashlib.sha256(raw).hexdigest()
    if actual_sha != SOURCE_SHA:
        raise ValueError(f"teacher source digest changed: {actual_sha}")
    image = Image.open(SOURCE).convert("RGB")
    if image.size != (1024, 1024):
        raise ValueError(f"teacher source dimensions changed: {image.size}")
    crop = image.crop(BOUNDS)
    crop_path = OUT / "teacher-crop-registered.png"
    crop.save(crop_path)
    focus_path = OUT / "teacher-crop-focus.png"
    crop.crop(FOCUS).save(focus_path)
    grid = crop.copy()
    draw = ImageDraw.Draw(grid)
    for x in range(0, crop.width, 20):
        draw.line((x, 0, x, crop.height), fill=(90, 100, 110), width=1)
        if x % 40 == 0: draw.text((x + 2, 2), str(x), fill=(20, 25, 35), stroke_width=1, stroke_fill=(245,245,245))
    for y in range(0, crop.height, 20):
        draw.line((0, y, crop.width, y), fill=(90, 100, 110), width=1)
        if y % 40 == 0: draw.text((2, y + 2), str(y), fill=(20, 25, 35), stroke_width=1, stroke_fill=(245,245,245))
    grid_path = OUT / "teacher-grid.png"
    grid.save(grid_path)
    annotated = crop.copy()
    draw = ImageDraw.Draw(annotated)
    details = {}
    array = np.asarray(crop).astype(np.uint8)
    for index, (name, (roi, purpose)) in enumerate(REGIONS.items()):
        x0,y0,x1,y1 = roi
        color = COLORS[index]
        draw.rectangle(roi, outline=color, width=2)
        draw.text((x0 + 2, max(0,y0 - 12)), name, fill=color, stroke_width=2, stroke_fill=(15,20,25))
        tile = array[y0:y1,x0:x1].reshape(-1,3)
        colors, counts = np.unique(tile, axis=0, return_counts=True)
        top = counts.argsort()[-5:][::-1]
        details[name] = {
            "purpose": purpose,
            "rough_observation_roi_crop_xyxy": list(roi),
            "same_region_roi_source_xyxy": [x0+BOUNDS[0],y0+BOUNDS[1],x1+BOUNDS[0],y1+BOUNDS[1]],
            "roi_dimensions": [x1-x0,y1-y0],
            "most_frequent_exact_jpeg_rgb_samples": [
                {"rgb": colors[i].astype(int).tolist(), "pixels": int(counts[i])} for i in top
            ],
            "interpretation_limit": "rough teacher viewing window only; not an object mask, contour, or renderer input",
        }
    annotated_path = OUT / "teacher-region-windows.png"
    annotated.save(annotated_path)
    result = {
        "role": "teacher-only source and coarse semantic region observations; not renderer input",
        "source": "image.jpg", "source_sha256": actual_sha, "source_dimensions": list(image.size),
        "registered_crop_source_xyxy": list(BOUNDS), "crop_dimensions": list(crop.size),
        "focus_crop_xyxy_within_registered_crop": list(FOCUS),
        "mapping": "crop (x,y) maps to source (500+x,320+y); no resize/stretch",
        "coordinate_scope": "Only feature ROI windows and handwritten compact semantic anchors are extracted from the teacher; no dense source contour is sent to runtime.",
        "regions": details,
        "evidence_files": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in (crop_path, focus_path, grid_path, annotated_path)},
        "runtime_boundary": "scene/reproduction imports neither this script nor any image output; source image stays closed during scene construction and render",
    }
    (OUT / "teacher-observations.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({name: {"roi": value["rough_observation_roi_crop_xyxy"], "purpose": value["purpose"]}
                      for name,value in details.items()}, indent=2))

if __name__ == "__main__":
    main()
