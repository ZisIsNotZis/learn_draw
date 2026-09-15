#!/usr/bin/env python3
"""measure-trace-debt.py — how much of the head is traced (reference-derived) vs invented.

Reads the assembly spec, resolves it (no --ref needed: traced sidecars), reconstructs the exact
paint order `relate.emit_svg` uses, and labels every pixel of the head crop by the TOPMOST shape
that covers it: TRACED (a frozen `region` outline, once the reference raster) or INVENTED (a
`face`/`eye`/`sunhat` family, a relation, or an authored gesture).

Why paint order, not a union: a traced hair-mass paints over the invented face, so a plain union
double-counts area the viewer cannot see. The viewer sees the topmost fill; that is the number M5
must repay. Deterministic, no verdict, no --ref.
"""
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import relate as rl  # noqa: E402

SPEC = ROOT / ".scratch/13-assembly/work/spec.yaml"
# the head region M2's gate owns (matches the bar command)
HX0, HY0, HX1, HY1 = 400, 0, 1020, 420

spec = rl.load_yaml(SPEC)
emit, env, notes, layers = rl.resolve(spec, base_dir=SPEC.parent)
W = int(env["frame.w"])
H = int(env["frame.h"])


def zindex(node):
    z = str(node.get("z", "default"))
    return layers.index(z) if z in layers else len(layers)


# identical to relate.emit_svg: full-canvas rects paint first, then stable layer order
order = [n for n in emit if n.get("full")]
order += sorted((n for n in emit if not n.get("full")), key=zindex)

label = np.zeros((H, W), np.uint8)  # 0 none, 1 invented, 2 traced


def visible(node):
    """Was this node actually painted? fill:none shapes (the sunhat brim/dome, whose surfaces the
    traced regions replace) paint nothing, so counting their area as invented is wrong."""
    if "spine" in node and "ink" in node:
        return True  # a stroke always paints
    fill = node.get("fill")
    if fill in (None, "none"):
        return bool(node.get("stroke"))  # fill:none + stroke still draws an outline
    return True


for node in order:
    if not visible(node):
        continue
    traced = "traced" in node or "region" in node
    val = 2 if traced else 1
    if node.get("full"):
        label[:] = 0  # full backdrop is invented but it is the ground; keep it out of the fraction
        continue
    if "poly" in node:
        pts = np.round(np.array(node["poly"], float)).astype(np.int32)
        cv2.fillPoly(label, [pts], val)
    elif "ellipse" in node:
        cx, cy = node["at"]
        axes = (int(round(node["rx"])), int(round(node["ry"])))
        cv2.ellipse(label, (int(round(cx)), int(round(cy))), axes,
                    float(node.get("rot", 0)), 0, 360, val, -1)
    elif "spine" in node:
        pts = np.round(np.array(node["spine"], float)).astype(np.int32)
        cv2.polylines(label, [pts], False, val, max(1, int(round(node.get("w", 4)))))

crop = label[HY0:HY1, HX0:HX1]
traced_px = int((crop == 2).sum())
invented_px = int((crop == 1).sum())
drawn = traced_px + invented_px
crop_px = crop.size

print("head crop           x[%d,%d) y[%d,%d)  = %d px" % (HX0, HX1, HY0, HY1, crop_px))
print("drawn (non-bg)      %7d px  (%.1f%% of crop)" % (drawn, 100.0 * drawn / crop_px))
print("  traced            %7d px  (%.3f of drawn)" % (traced_px, traced_px / max(drawn, 1)))
print("  invented          %7d px  (%.3f of drawn)" % (invented_px, invented_px / max(drawn, 1)))
print("unpainted/backdrop  %7d px  (%.1f%% of crop)" % (crop_px - drawn, 100.0 * (crop_px - drawn) / crop_px))

# a tighter box around the hat+face only (the gate crop x400..1020 also holds a slice of the
# invented mint field at the left, which inflates the invented share)
TX0, TY0, TX1, TY1 = 440, 0, 1020, 400
crop2 = label[TY0:TY1, TX0:TX1]
t2, i2 = int((crop2 == 2).sum()), int((crop2 == 1).sum())
print("\ntight head box      x[%d,%d) y[%d,%d)  = %d px" % (TX0, TX1, TY0, TY1, crop2.size))
print("  traced            %7d px  (%.3f of drawn)" % (t2, t2 / max(t2 + i2, 1)))
print("  invented          %7d px  (%.3f of drawn)" % (i2, i2 / max(t2 + i2, 1)))

# per traced node, its own covered area within the crop (raw, not occlusion-corrected)
print("\nper traced node (raw covered px in crop):")
for node in emit:
    if "traced" not in node:
        continue
    m = np.zeros((H, W), np.uint8)
    cv2.fillPoly(m, [np.round(np.array(node["poly"], float)).astype(np.int32)], 1)
    print("  %-22s %7d" % (node["traced"], int(m[HY0:HY1, HX0:HX1].sum())))

# the largest INVENTED contributors inside the gate crop: what M5 still has to redraw by hand
print("\ntop invented contributors (raw covered px in crop):")
rows = []
for node in emit:
    if "traced" in node or node.get("full") or not visible(node):
        continue
    m = np.zeros((H, W), np.uint8)
    if "poly" in node:
        cv2.fillPoly(m, [np.round(np.array(node["poly"], float)).astype(np.int32)], 1)
    elif "ellipse" in node:
        cv2.ellipse(m, (int(round(node["at"][0])), int(round(node["at"][1]))),
                    (int(round(node["rx"])), int(round(node["ry"]))),
                    float(node.get("rot", 0)), 0, 360, 1, -1)
    elif "spine" in node:
        cv2.polylines(m, [np.round(np.array(node["spine"], float)).astype(np.int32)],
                      False, 1, max(1, int(round(node.get("w", 4)))))
    n = int(m[HY0:HY1, HX0:HX1].sum())
    if n:
        rows.append((n, rl._sid(node)))
for n, sid in sorted(rows, reverse=True)[:8]:
    print("  %-22s %7d" % (sid, n))
