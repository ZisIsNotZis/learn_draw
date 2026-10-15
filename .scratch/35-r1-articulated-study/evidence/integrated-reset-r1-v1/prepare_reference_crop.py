"""Validate frozen reference provenance and materialize only the registered comparison crop."""
from __future__ import annotations

import hashlib
from io import BytesIO
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
SOURCE_HASH = "322ad77c0cfd28fa040c625c55c592a54b3052ac4bea61fc31d967d8acff81fb"
CROP_HASH = "52e01f5e75e5d98fcd9a0a4ac63be91ed09b8a18ca0f62e7e0348a021b2dd87d"
BOUNDS = (500, 320, 900, 800)


def prepare_crop() -> Path:
    source = REPO / "image.jpg"
    data = source.read_bytes()
    if hashlib.sha256(data).hexdigest() != SOURCE_HASH:
        raise ValueError("frozen target source hash does not match task-freeze provenance")
    image = Image.open(source).convert("RGB")
    if image.size != (1024, 1024):
        raise ValueError("frozen source dimensions changed")
    crop = image.crop(BOUNDS)
    encoded = BytesIO()
    crop.save(encoded, format="PNG")
    png = encoded.getvalue()
    if crop.size != (400, 480) or hashlib.sha256(png).hexdigest() != CROP_HASH:
        raise ValueError("registered crop digest differs from task-freeze provenance")
    target = ROOT / "reference-crop.png"
    target.write_bytes(png)
    return target


if __name__ == "__main__":
    print(prepare_crop())
