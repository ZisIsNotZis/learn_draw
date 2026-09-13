"""Diagnosis experiment — why the hand-authored portrait failed.

Three questions, answered by measurement instead of by more authoring:
  A. Can COMPUTED geometry alone reproduce the reference? (region decomposition)
  B. Does the reference even carry uniform black line art? (ink-pixel extraction)
  C. How do they compare against the 20-iteration hand-authored render?

Run:  .venv/bin/python .scratch/05-portrait-scene/evidence/diagnosis/exp_region_decomposition.py
Outputs (same dir): regionvec.png, lineart.png, 3up-ref-current-computed.png
"""
from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO / "scripts"))

from scene_render import chrome, smooth_path  # noqa: E402

HERE = Path(__file__).resolve().parent
REF = REPO / "image.jpg"
CURRENT = REPO / ".scratch/05-portrait-scene/evidence/current.png"


def load(path: Path) -> np.ndarray:
    img = cv2.imread(str(path))
    if img is None:
        raise SystemExit(f"cannot read {path}")
    return img


def posterize(img: np.ndarray, k: int) -> np.ndarray:
    """k-means palette over all pixels -> per-pixel region index map."""
    h, w = img.shape[:2]
    samples = img.reshape(-1, 3).astype(np.float32)
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.5)
    compactness, labels, centers = cv2.kmeans(samples, k, None, crit, 4, cv2.KMEANS_PP_CENTERS)  # type: ignore[arg-type]
    del compactness
    palettes = np.asarray(centers, dtype=np.uint8)
    np.save(HERE / "_palette.npy", palettes)
    return np.asarray(labels, dtype=np.int32).reshape(h, w)


def region_decomposition(img: np.ndarray, k: int = 14) -> tuple[str, int, int]:
    """posterize -> connected components -> contours -> flat SVG paths."""
    h, w = img.shape[:2]
    lab = posterize(img, k)
    palette = np.load(HERE / "_palette.npy")
    kernel: np.ndarray = np.ones((3, 3), np.uint8)

    paths: list[str] = []
    for idx in range(k):
        mask: np.ndarray = np.where(lab == idx, 255, 0).astype(np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        count, comp, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
        bgr = palette[idx]
        color = f"#{bgr[2]:02x}{bgr[1]:02x}{bgr[0]:02x}"
        for i in range(1, count):
            if stats[i, cv2.CC_STAT_AREA] < 220:
                continue
            one: np.ndarray = np.where(comp == i, 1, 0).astype(np.uint8)
            contours, _ = cv2.findContours(one, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in contours:
                poly = cv2.approxPolyDP(c, 1.6, True).reshape(-1, 2)
                if len(poly) < 3:
                    continue
                d = smooth_path([tuple(map(int, p)) for p in poly], closed=True)
                paths.append(f'<path d="{d}" fill="{color}"/>')
    return svg_doc(paths, w, h), len(paths), 0


def ink_extraction(img: np.ndarray, threshold: int = 95) -> tuple[str, int, int]:
    """Reference's genuinely black pixels, as strokes — answers question B."""
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel: np.ndarray = np.ones((2, 2), np.uint8)
    ink: np.ndarray = np.where(gray < threshold, 255, 0).astype(np.uint8)
    ink = cv2.morphologyEx(ink, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(ink, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    ink_px = len(np.flatnonzero(gray < threshold))
    strokes: list[str] = []
    for c in contours:
        if len(c) < 6:
            continue
        poly = cv2.approxPolyDP(c, 1.4, False).reshape(-1, 2)
        d = smooth_path([tuple(map(int, p)) for p in poly], closed=False)
        strokes.append(
            f'<path d="{d}" fill="none" stroke="#101820" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round"/>'
        )
    return svg_doc(strokes, w, h), len(strokes), ink_px


def svg_doc(body: list[str], w: int, h: int, bg: str = "#ffffff") -> str:
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
            f'<rect width="100%" height="100%" fill="{bg}"/>',
            *body,
            "</svg>",
        ]
    )


def render(svg: str, png: Path, size: tuple[int, int]) -> None:
    tmp = png.with_suffix(".svg")
    tmp.write_text(svg)
    chrome(str(tmp), str(png), size)


def label(img: np.ndarray, text: str) -> np.ndarray:
    out = img.copy()
    cv2.rectangle(out, (0, 0), (out.shape[1], 34), (24, 24, 28), -1)
    cv2.putText(out, text, (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (240, 240, 240), 1, cv2.LINE_AA)
    return out


def main() -> None:
    ref = load(REF)
    h, w = ref.shape[:2]

    vec_svg, n_sym, _ = region_decomposition(ref)
    render(vec_svg, HERE / "regionvec.png", (w, h))

    ink_svg, n_strokes, ink_px = ink_extraction(ref)
    render(ink_svg, HERE / "lineart.png", (w, h))

    tiles = []
    for path, cap in ((REF, "REFERENCE"), (CURRENT, "20 ITERATIONS + CUSTOM DSL"), (HERE / "regionvec.png", "COMPUTED REGION DECOMPOSITION")):
        t = cv2.resize(load(path), (600, 600), interpolation=cv2.INTER_AREA)
        tiles.append(label(t, cap))
    cv2.imwrite(str(HERE / "3up-ref-current-computed.png"), np.hstack(tiles))

    print(f"region decomposition : {n_sym} paths")
    print(f"ink extraction       : {n_strokes} strokes, {ink_px} px below gray {95} "
          f"({100 * ink_px / (w * h):.2f}% of canvas)")


if __name__ == "__main__":
    main()
