#!/usr/bin/env python3
"""Draw a teacher-only annotated pointer map over the registered A crop.

This does not segment, trace, or supply renderer geometry. Lines between anchors denote
proposed semantic adjacency only; they are deliberately dashed and not fitted boundaries.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).parent
CROP = ROOT / "source-crop-registered.png"
CSV = ROOT / "landmarks.csv"
OUT = ROOT / "teacher-topology-overlay.png"
EXPECTED_CROP_SHA256 = "52e01f5e75e5d98fcd9a0a4ac63be91ed09b8a18ca0f62e7e0348a021b2dd87d"
SCALE = 2

COLORS = {
    "neck/collar": (40, 120, 240),
    "bodice/sleeve": (20, 165, 100),
    "bow": (225, 40, 125),
    "unknown/low": (240, 150, 20),
}


def dashed(draw: ImageDraw.ImageDraw, a: tuple[int, int], b: tuple[int, int],
           color: tuple[int, int, int], dash: int = 10, gap: int = 7) -> None:
    """Draw schematic dashed adjacency pointers in enlarged display coordinates."""
    import math
    x1, y1 = a
    x2, y2 = b
    length = math.hypot(x2 - x1, y2 - y1)
    if not length:
        return
    ux, uy = (x2 - x1) / length, (y2 - y1) / length
    pos = 0.0
    while pos < length:
        end = min(pos + dash, length)
        draw.line((x1 + ux * pos, y1 + uy * pos,
                   x1 + ux * end, y1 + uy * end), fill=color, width=2)
        pos += dash + gap


def main() -> None:
    digest = hashlib.sha256(CROP.read_bytes()).hexdigest()
    if digest != EXPECTED_CROP_SHA256:
        raise SystemExit(f"registered crop hash mismatch: {digest}")
    crop = Image.open(CROP).convert("RGB")
    if crop.size != (400, 480):
        raise SystemExit(f"expected 400x480 crop, got {crop.size}")

    rows = list(csv.DictReader(CSV.open(newline="", encoding="utf-8")))
    by_id = {row["id"]: row for row in rows}
    canvas = Image.new("RGB", (400 * SCALE + 600, 480 * SCALE), "#f6f5f1")
    enlarged = crop.resize((400 * SCALE, 480 * SCALE), Image.Resampling.LANCZOS)
    canvas.paste(enlarged, (0, 0))
    draw = ImageDraw.Draw(canvas, "RGBA")

    def pt(key: str) -> tuple[int, int]:
        row = by_id[key]
        return int(row["crop_x"]) * SCALE, int(row["crop_y"]) * SCALE

    # Dashed lines are topology/adjacency hypotheses, not object outlines.
    for left, right, family in [
        ("CL1", "CL2", "neck/collar"), ("CR1", "CR2", "neck/collar"),
        ("BD2", "SC1", "unknown/low"),
        ("SC3", "CU1", "bodice/sleeve"), ("BK1", "BL1", "bow"),
        ("BK1", "BR1", "bow"), ("BK1", "TL1", "bow"),
        ("BK1", "TD1", "bow"),
    ]:
        dashed(draw, pt(left), pt(right), COLORS[family])

    font = ImageFont.load_default()
    for row in rows:
        x, y = int(row["crop_x"]) * SCALE, int(row["crop_y"]) * SCALE
        ident = row["id"]
        if ident.startswith(("N", "CL", "CR")):
            color = COLORS["neck/collar"]
        elif ident.startswith(("BK", "BL", "BR", "T")):
            color = COLORS["bow"]
        elif ident.startswith(("BD", "SC", "CU")):
            color = COLORS["bodice/sleeve"]
        else:
            color = COLORS["unknown/low"]
        r = 7
        marker_x = max(r + 1, x)  # keep the x=0 crop-edge landmark visibly on-canvas
        draw.ellipse((marker_x-r, y-r, marker_x+r, y+r), fill=(*color, 255), outline=(255, 255, 255, 255), width=2)
        label_dx, label_dy = {"N2": (10, -23), "CL2": (26, 5), "TL1": (13, -22)}.get(ident, (8, -11))
        label_x, label_y = marker_x + label_dx, y + label_dy
        label_box = (label_x, label_y, label_x + 35, label_y + 14)
        draw.rounded_rectangle(label_box, radius=3, fill=(255, 255, 255, 230), outline=(*color, 255), width=1)
        draw.text((label_x + 2, label_y + 1), ident, fill=(20, 20, 20, 255), font=font)

    # Legend stays outside the crop so source pixels remain visible and unmodified.
    left = 400 * SCALE + 22
    draw.text((left, 22), "A teacher semantics — review against crop", fill=(20, 20, 20, 255), font=font)
    lines = [
        "Exact source crop shown at 2x for annotation only.",
        "IDs point to landmarks.csv; coordinates are crop pixels.",
        "Dashed links = adjacency hypothesis, NOT contour/seam.",
        "No segmentation, RGB mask, tracing or renderer geometry.",
        "Unknowns: pink/blue overlap near x=44; right cuff is clipped.",
        "Hair/bow/foreground occlusion is not a garment seam.",
        "Confidence concerns the point observation, not full edge.",
        "",
        "Color key:",
        "Blue: neck / collar observations",
        "Green: bodice / sleeve / cuff observations",
        "Pink: knot / loops / tails",
        "Orange: low-confidence connection",
        "",
        "Region locators (not masks):",
        "neck skin/opening: N1, N2, CL*, CR*",
        "bodice: BD1-BD4",
        "continuous sleeve: SC1-SC3 -> cuff CU1",
        "bow: knot BK1; loops BL1/BR1; tails TL1/TD1",
        "Points locate evidence; no region boundary is asserted.",
        "",
        "Registration: source = (500 + crop_x, 320 + crop_y)",
        "Input crop SHA256:",
        EXPECTED_CROP_SHA256,
    ]
    y = 56
    for line in lines:
        draw.text((left, y), line, fill=(25, 25, 25, 255), font=font)
        y += 24
    canvas.save(OUT, format="PNG", optimize=False)
    print(f"overlay={OUT} size={canvas.size} input_sha256={digest} output_sha256={hashlib.sha256(OUT.read_bytes()).hexdigest()}")


if __name__ == "__main__":
    main()
