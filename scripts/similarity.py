#!/usr/bin/env python3
"""similarity.py — contextual similarity between a draft and the reference (a secondary alarm).

Measures CLIP image-embedding cosine similarity (OpenAI ViT-B-32, 151M params, cached under
~/.cache/clip). This is the *contextual* signal the pixel metrics lack: it compares what the image
depicts, not which pixels coincide. It tracked the project's own history correctly on first use:

    M3b (fitted families)   0.836
    M2 (flat bust)          0.732
    M1 (flat blobs)         0.637
    starry probe (different subject) 0.591
    random noise            0.489
    flat colour             0.484

STATUS: a SECONDARY ALARM, never a gate (roadmap G8 is the rubric). Two reasons, recorded in
docs/drawing/rubric.md Part III: (1) a scalar is a black box in a project whose method is
explainability, and the rubric's per-axis evidence and free-text "one change" field are worth more than
a number; (2) a scalar invites optimisation — a CLIP score measures *semantic neighbourhood*, so a
drawing can drift toward "anime girl with a hat" generally and the number rises while the drawing
becomes less like the target. Use it to catch regressions between rubric rounds, and to record history.

Usage:
    .venv/bin/python scripts/similarity.py <draft> [--ref image.jpg] [--threshold 0.02]
    .venv/bin/python scripts/similarity.py compare <draft> <other.png> ... [--ref image.jpg]

Exit status is 0 always — this is a reading, not a verdict (invariant 4: metrics are alarms).
"""
import argparse
import os
import sys

import cv2
import numpy as np

DEFAULT_MODEL = ("ViT-B-32", "openai")


def _load_model():
    import open_clip, torch
    name, pretrained = DEFAULT_MODEL
    model, _, preprocess = open_clip.create_model_and_transforms(name, pretrained=pretrained)
    model.eval()
    return model, preprocess


def _to_pil(img):
    from PIL import Image
    if img is None:
        raise SystemExit("similarity: cannot read an input image")
    if isinstance(img, str):
        return Image.open(img).convert("RGB")
    if img.ndim == 2:
        return Image.fromarray(img)
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


def embed(model, preprocess, img):
    import torch
    x = preprocess(_to_pil(img)).unsqueeze(0)
    with torch.no_grad():
        e = model.encode_image(x)
    return e / e.norm(dim=-1, keepdim=True)


def cosine(a, b) -> float:
    import torch
    return float(torch.nn.functional.cosine_similarity(a, b))


def main(argv):
    ap = argparse.ArgumentParser(description="contextual similarity (CLIP) — a secondary alarm")
    ap.add_argument("paths", nargs="+", help="draft image(s), or 'compare' followed by images")
    ap.add_argument("--ref", default="image.jpg", help="reference image (default: image.jpg)")
    ap.add_argument("--threshold", type=float, default=0.02,
                    help="alarm: report a regression if the best draft falls this far below the others")
    args = ap.parse_args(argv[1:])

    paths = list(args.paths)
    mode = "single"
    if paths and paths[0] == "compare":
        mode = "compare"; paths = paths[1:]
    if len(paths) < 1:
        raise SystemExit("similarity: need at least one draft image")

    model, pre = _load_model()
    ref = embed(model, pre, D_read(args.ref))
    scores = []
    for p in paths:
        if not os.path.exists(p):
            raise SystemExit(f"similarity: no such image: {p}")
        scores.append((os.path.basename(p), cosine(ref, embed(model, pre, D_read(p)))))
    scores.sort(key=lambda kv: -kv[1])

    if mode == "single":
        for name, s in scores:
            print(f"  contextual similarity to the reference: {s:.4f}   {name}")
    else:
        print("  contextual similarity to the reference (highest first):")
        for name, s in scores:
            print(f"    {s:.4f}   {name}")
    best = scores[0][1]
    if len(scores) > 1 and (scores[0][1] - min(s for _, s in scores[1:])) >= args.threshold:
        print(f"  ALARM: the highest-scoring draft is >= {args.threshold:.2f} above the others — "
              f"check that the intended artifact is the one being rendered.")
    return 0


def D_read(path):
    """Read without pulling draw.py's chrome helpers — this script must work standalone."""
    img = cv2.imread(path)
    return img


if __name__ == "__main__":
    sys.exit(main(sys.argv))
