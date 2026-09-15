#!/usr/bin/env python3
"""draw.py — toolkit for learning to draw via programmatic art (SVG/CSS).

Subcommands: render | compare | diff | ref | log | measure | check | baseline
Renderer: chrome-headless-shell (playwright cache) — renders SVG and HTML/CSS alike.
The ratchet: `baseline` records the best artifact so far; `check` reports the delta against it,
so a drawing that regresses is visible as a regression instead of being called progress.
"""
import argparse, hashlib, json, os, re, subprocess, sys, datetime
import numpy as np
import cv2

CHROME = os.path.expanduser(
    "~/.cache/ms-playwright/chromium_headless_shell-1234/"
    "chrome-headless-shell-linux64/chrome-headless-shell")

# The recorded best artifact — the floor every new render is measured against (see roadmap M-gates).
BASELINE_DIR = ".scratch/00-tooling/baseline"
BASELINE_PNG = os.path.join(BASELINE_DIR, "best.png")
BASELINE_JSON = os.path.join(BASELINE_DIR, "best.json")


class ToolError(SystemExit):
    """A tool-level failure, reported in words rather than as a traceback."""


def num(value: object, what: str = "value") -> float:
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ToolError(f"draw: {what} is not a number: {value!r}") from exc


def whole(value: object, what: str = "value") -> int:
    try:
        return int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ToolError(f"draw: {what} is not an integer: {value!r}") from exc


def read_text(path: str) -> str:
    try:
        return open(path).read()
    except OSError as exc:
        raise ToolError(f"draw: cannot read {path}: {exc}") from exc


def write_text(path: str, text: str) -> None:
    try:
        with open(path, "w") as fh:
            fh.write(text)
    except OSError as exc:
        raise ToolError(f"draw: cannot write {path}: {exc}") from exc


def append_text(path: str, text: str) -> None:
    try:
        with open(path, "a") as fh:
            fh.write(text)
    except OSError as exc:
        raise ToolError(f"draw: cannot append to {path}: {exc}") from exc


def remove_file(path: str) -> None:
    try:
        os.remove(path)
    except OSError as exc:
        raise ToolError(f"draw: cannot remove {path}: {exc}") from exc


def ensure_dir(path: str) -> None:
    try:
        os.makedirs(path, exist_ok=True)
    except OSError as exc:
        raise ToolError(f"draw: cannot create {path}: {exc}") from exc


def size_arg(text: str | None) -> tuple[int, int] | None:
    """Parse a WxH argument, or None when absent."""
    if not text:
        return None
    parts = text.split("x")
    if len(parts) != 2:
        raise ToolError(f"draw: --size must be WxH, got {text!r}")
    return (whole(parts[0], "--size width"), whole(parts[1], "--size height"))


def render(src: str, out: str, size: tuple[int, int] | None = None) -> tuple[int, int]:
    """Rasterize .svg or .html to PNG via headless chromium."""
    src = os.path.abspath(src)
    out = os.path.abspath(out)
    if not os.path.exists(CHROME):
        sys.exit(f"renderer not found: {CHROME}")
    tmp: str | None = None
    if src.endswith(".svg"):
        svg = read_text(src)
        if size is None:
            m = re.search(r'viewBox="([\d.\- ,]+)"', svg)
            if m and len(m.group(1).split()) == 4:
                size = (whole(num(m.group(1).split()[2])), whole(num(m.group(1).split()[3])))
            else:
                m = re.search(r'<svg[^>]*\bwidth="([\d.]+)"[^>]*\bheight="([\d.]+)"', svg)
                if not m:
                    sys.exit("cannot infer SVG size; pass --size WxH")
                size = (whole(num(m.group(1))), whole(num(m.group(2))))
        html = f'<html><body style="margin:0;overflow:hidden">{svg}</body></html>'
        tmp = out + ".wrap.html"
        write_text(tmp, html)
        target = tmp
    else:
        target = src
    if size is None:
        raise ToolError("draw: cannot infer a size for this source; pass --size WxH")
    subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox",
                    f"--screenshot={out}", f"--window-size={size[0]},{size[1]}",
                    "file://" + target], check=True, capture_output=True, timeout=60)
    if tmp is not None:
        remove_file(tmp)
    return size


def imwrite(path: str, img: np.ndarray):
    ensure_dir(os.path.dirname(os.path.abspath(path)))
    cv2.imwrite(path, img)


def imread(path: str, size: tuple[int, int] | None = None) -> np.ndarray:
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        sys.exit(f"cannot read image: {path}")
    if size is not None and (img.shape[1], img.shape[0]) != size:
        img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
    return img


def edge_map(img: np.ndarray) -> np.ndarray:
    """Binary edge map via auto-canny on blurred grayscale."""
    g = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (3, 3), 0)
    v = np.median(g)
    lo, hi = whole(max(0, 0.66 * v)), whole(min(255, 1.33 * v))
    return cv2.Canny(g, lo, hi)


def hint_boxes(mask: np.ndarray, n: int, min_area: int = 60):
    """Top-n connected components of mask as (x, y, w, h, area), largest first."""
    num, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    cands = [tuple(s) for s in stats[1:] if s[4] >= min_area]
    cands.sort(key=lambda s: -s[4])
    return cands[:n]


def draw_boxes(img: np.ndarray, boxes, color=(0, 215, 255)):
    for i, (x, y, w, h, _) in enumerate(boxes, 1):
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
        cv2.putText(img, str(i), (x + 3, y + 22), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(img, str(i), (x + 3, y + 22), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, color, 2, cv2.LINE_AA)
    return img


def label(img: np.ndarray, text: str):
    h, w = img.shape[:2]
    bar = np.full((28, w, 3), 30, np.uint8)
    cv2.putText(bar, text, (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (255, 255, 255), 1, cv2.LINE_AA)
    return np.vstack([bar, img])


def side_by_side(a: np.ndarray, b: np.ndarray, la: str, lb: str) -> np.ndarray:
    a, b = label(a, la), label(b, lb)
    sep = np.zeros((a.shape[0], 4, 3), np.uint8)
    return np.hstack([a, sep, b])


def subject_mask(ref: np.ndarray, bg_tol: int = 45) -> np.ndarray:
    """Boolean mask of the reference's non-background content.

    Background = median colour of the 12px border band, which is what "the flat backdrop" means for
    a reference like this one. Everything that departs from it is content the drawing owes us:
    the figure, the field shapes, the ribbon sweep.
    """
    return np.linalg.norm(ref.astype(np.int16) - ref_background(ref), axis=2) > bg_tol


def ref_background(ref: np.ndarray) -> np.ndarray:
    """The reference's backdrop colour: median of the 12px border band."""
    b = 12
    band = np.concatenate([ref[:b].reshape(-1, 3), ref[-b:].reshape(-1, 3),
                           ref[:, :b].reshape(-1, 3), ref[:, -b:].reshape(-1, 3)])
    return np.median(band, axis=0)


def drawn_mask(ref: np.ndarray, draft: np.ndarray, bg_tol: int = 45) -> np.ndarray:
    """Where the draft actually painted something (it departs from the reference's backdrop)."""
    return np.linalg.norm(draft.astype(np.int16) - ref_background(ref), axis=2) > bg_tol


def subject_coverage(ref: np.ndarray, draft: np.ndarray, match_tol: int = 60) -> float:
    """Fraction of the reference's content the draft actually accounts for.

    The omission alarm. `color_dist` cannot answer "how much did you leave out?" because it mixes
    wrong pixels with absent ones, so a bust and a badly-coloured full figure score alike — which is
    exactly how a fragment gets committed as a "final image". This number answers the omission
    question directly. Alarm and regression floor only, never an optimisation target (invariant 4).
    """
    subj = subject_mask(ref)
    if not subj.any():
        return 0.0
    d = np.linalg.norm(ref.astype(np.int16) - draft.astype(np.int16), axis=2)
    return num((d[subj] <= match_tol).mean())


def metrics(ref: np.ndarray, draft: np.ndarray) -> dict:
    """edge-F1 (tolerant) + mean color distance + subject coverage. Signal only, never a target."""
    re_, de = edge_map(ref) > 0, edge_map(draft) > 0
    k = np.ones((5, 5), np.uint8)
    rd, dd = cv2.dilate(re_.astype(np.uint8), k) > 0, cv2.dilate(de.astype(np.uint8), k) > 0
    p = (de & rd).sum() / max(de.sum(), 1)   # draft edges covered by ref
    r = (re_ & dd).sum() / max(re_.sum(), 1) # ref edges covered by draft
    f1 = 2 * p * r / max(p + r, 1e-9)
    cd = np.linalg.norm(ref.astype(np.int16) - draft.astype(np.int16), axis=2).mean()
    return {"precision": round(num(p), 3), "recall": round(num(r), 3),
            "edge_f1": round(num(f1), 3), "color_dist": round(num(cd), 1),
            "coverage": round(subject_coverage(ref, draft), 3)}


# ---------------------------------------------------------------- subcommands

def cmd_compare(a):
    size = render(a.src, a.out) if a.src.endswith((".svg", ".html")) else None
    draft = imread(a.src, size) if not a.src.endswith((".svg", ".html")) else imread(a.out)
    ref = imread(a.ref, (draft.shape[1], draft.shape[0]))
    la, lb = "REF", "DRAFT"
    if a.region:
        x, y, w, h = a.region
        ref, draft = ref[y:y + h, x:x + w], draft[y:y + h, x:x + w]
        la += f" region=({x},{y},{w},{h})"
    if a.zoom != 1:
        it = cv2.INTER_NEAREST if a.zoom > 1 else cv2.INTER_AREA
        ref = cv2.resize(ref, None, fx=a.zoom, fy=a.zoom, interpolation=it)
        draft = cv2.resize(draft, None, fx=a.zoom, fy=a.zoom, interpolation=it)
    out = side_by_side(ref, draft, la, lb)
    imwrite(a.out, out)
    print(a.out, f"{out.shape[1]}x{out.shape[0]}")


def cmd_diff(a):
    size = render(a.src, a.out) if a.src.endswith((".svg", ".html")) else None
    draft = imread(a.src, size) if not a.src.endswith((".svg", ".html")) else imread(a.out)
    ref = imread(a.ref, (draft.shape[1], draft.shape[0]))
    m = metrics(ref, draft)
    print("metrics:", m)
    if a.mode == "line":
        re_, de = edge_map(ref) > 0, edge_map(draft) > 0
        dd = cv2.dilate(de.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        rd = cv2.dilate(re_.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
        ov = np.full((*re_.shape, 3), 25, np.uint8)          # dark bg
        ov[re_ & ~dd] = (255, 255, 0)                        # cyan: ref-only (missed)
        ov[de & ~rd] = (255, 0, 255)                         # magenta: mine-only (invented)
        ov[re_ & de] = (255, 255, 255)                       # white: match
        boxes = hint_boxes((re_ & ~dd).astype(np.uint8), a.hints)
        ov = draw_boxes(ov, boxes)
        print(f"hints: {[b[:4] for b in boxes]}")
    else:
        d = np.linalg.norm(ref.astype(np.int16) - draft.astype(np.int16), axis=2)
        dn = (np.clip(d, 0, 128) / 128 * 255).astype(np.uint8)
        ov = cv2.applyColorMap(cv2.GaussianBlur(dn, (0, 0), 2), cv2.COLORMAP_TURBO)
        boxes = hint_boxes((dn > 100).astype(np.uint8), a.hints, min_area=400)
        ov = draw_boxes(ov, boxes)
        print(f"hints: {[b[:4] for b in boxes]}")
    imwrite(a.out, side_by_side(ref, ov, "REF", f"DIFF-{a.mode}"))
    print(a.out)


def worst_cells(dist: np.ndarray, n: int, cell: int = 64, sep: int = 2):
    """Top-n worst cells of a distance map, kept spatially apart.

    Connected components are useless here: when a draft differs globally the threshold mask
    merges into one canvas-sized blob, which is not a "worst region". Ranking a coarse grid
    always yields n localized, comparable areas.
    """
    gh, gw = dist.shape[0] // cell, dist.shape[1] // cell
    if gh < 1 or gw < 1:
        return []
    grid = dist[:gh * cell, :gw * cell].reshape(gh, cell, gw, cell).mean(axis=(1, 3))
    picked: list[tuple[int, int]] = []
    for flat in np.argsort(-grid.ravel()):
        gy, gx = divmod(whole(flat), gw)
        if all(max(abs(gy - py), abs(gx - px)) >= sep for py, px in picked):
            picked.append((gy, gx))
        if len(picked) >= n:
            break
    return [(gx * cell, gy * cell, cell, cell, num(grid[gy, gx])) for gy, gx in picked]


def _fit(img: np.ndarray, max_w: int) -> np.ndarray:
    """Downscale so width <= max_w, preserving aspect (no upscaling)."""
    if img.shape[1] <= max_w:
        return img
    scale = max_w / img.shape[1]
    return cv2.resize(img, (max_w, max(1, round(img.shape[0] * scale))), interpolation=cv2.INTER_AREA)


def _check_dir(art: str) -> str:
    """Evidence dir for a drawing: <exercise>/evidence/check for .scratch arts, else <dir>/check."""
    ap_ = os.path.abspath(art)
    parts = ap_.split(os.sep)
    if ".scratch" in parts:
        i = parts.index(".scratch")
        if i + 1 < len(parts):
            return os.path.join(os.sep.join(parts[:i + 1]), parts[i + 1], "evidence", "check")
    return os.path.join(os.path.dirname(ap_) or ".", "check")


def _rasterize(art: str, outdir: str, ref: str | None, resolver_override: str | None = None):
    """Turn a drawing (svg/html/png/jpg/scene.yaml/relational spec) into a draft PNG.

    Returns (dst, meta) where meta holds the resolver path (if any) and its captured stdout,
    so the caller can put the resolver's diagnostics and anchors into the review bundle.
    """
    ext = os.path.splitext(art)[1].lower()
    if ext in (".png", ".jpg", ".jpeg", ".webp"):
        return art, {"resolver": None, "stdout": ""}
    here = os.path.dirname(os.path.abspath(__file__))
    if ext in (".svg", ".html"):
        dst = os.path.join(outdir, "draft.png")
        render(art, dst)
        return dst, {"resolver": None, "stdout": ""}
    if ext in (".yaml", ".yml"):
        import yaml
        try:
            spec = yaml.safe_load(read_text(art))
        except yaml.YAMLError as exc:
            sys.exit(f"cannot read {art}: {exc}")
        dst = os.path.join(outdir, "draft.png")
        if isinstance(spec, dict) and {"frame", "draw"} <= set(spec):
            resolver = resolver_override or _find_relate(art)
            if resolver is None:
                sys.exit(f"{art} is a relational spec but no relate.py was found; "
                         "pass --resolver PATH or run the resolver yourself")
            run = subprocess.run([sys.executable, resolver, art, "-o", dst, "--anchors"],
                                 capture_output=True, text=True, timeout=120)
            if run.returncode != 0:
                sys.exit(f"resolver failed ({resolver}):\n{run.stderr}")
            return dst, {"resolver": resolver, "stdout": run.stdout}
        else:
            cmd = [sys.executable, os.path.join(here, "scene_render.py"), art, "-o", dst]
            if ref:
                cmd += ["--ref", ref]
            run = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if run.returncode != 0:
                sys.exit(f"scene render failed:\n{run.stderr}")
            return dst, {"resolver": "scene_render.py", "stdout": run.stdout}
    sys.exit(f"draw check: unsupported drawing type {ext or art!r}")


def _find_relate(art: str) -> str | None:
    """Locate the relational resolver: beside the spec, or the canonical one in scripts/.

    Deterministic on purpose (the old last-hit-wins silently depended on directory names):
    a resolver beside the spec wins; otherwise the canonical scripts/relate.py if it exists;
    otherwise error. Forks outside scripts/ are never picked implicitly.
    """
    beside = os.path.join(os.path.dirname(os.path.abspath(art)), "relate.py")
    if os.path.exists(beside):
        return beside
    canonical = os.path.join(os.path.dirname(os.path.abspath(__file__)), "relate.py")
    if os.path.exists(canonical):
        return canonical
    return None


def cmd_check(a):
    """Emit the visual feedback bundle: images + numbers, and never a verdict."""
    outdir = a.outdir or _check_dir(a.art)
    ensure_dir(outdir)
    draft_path, meta = _rasterize(a.art, outdir, a.ref, a.resolver)
    draft = imread(draft_path)
    written: list[tuple[str, str]] = []
    lines: list[str] = []
    if meta["resolver"]:
        lines.append(f"resolver: {meta['resolver']}")

    if a.ref:
        ref = imread(a.ref, (draft.shape[1], draft.shape[0]))
        m = metrics(ref, draft)
        p = os.path.join(outdir, "side-by-side.png")
        imwrite(p, side_by_side(_fit(ref, a.pane), _fit(draft, a.pane), "REF", "DRAFT"))
        written.append((p, "whole frame, ref beside draft"))
        lines.append(f"metrics (breakage alarm only, never a target): {m}")

        # The whole-frame pane downscales to <=pane px and destroys exactly the detail a reviewer
        # must judge (glints, lash taper, marks, hat tilt). Always ship the 1:1 draft too.
        fp = os.path.join(outdir, "draft-fullres.png")
        imwrite(fp, draft)
        written.append((fp, "DRAFT at full resolution (1:1, no downscale)"))

        best = load_baseline()
        if best and best.get("metrics"):
            lines.append(f"vs recorded best: {delta(best['metrics'], m)}"
                         f"   [best recorded {best.get('recorded', '?')}: {best.get('source', '?')}]")

        dist = np.linalg.norm(ref.astype(np.int16) - draft.astype(np.int16), axis=2)
        # Raw worst-distance always picks the largest MISSING mass; the small detail the drawing did
        # produce (the face) then never gets a crop, and the reviewer judges it from a <=600px pane
        # (07's finding). So: keep the biggest-error crops, and force one crop to be the worst error
        # *where the draft actually drew something* — the place a reviewer must look closely.
        boxes = [(x, y, w, h, b, "worst-region") for x, y, w, h, b in worst_cells(dist, a.regions - 1)]
        detail = worst_cells(dist * drawn_mask(ref, draft), a.regions)
        for x, y, w, h, b in detail:
            if all(max(abs(x - px), abs(y - py)) >= 64 for px, py, _, _, _, _ in boxes):
                boxes.append((x, y, w, h, b, "worst-on-drawn"))
                break
        for i, (x, y, w, h, badness, kind) in enumerate(boxes, 1):
            side = whole(max(96, min(256, max(w, h) * 2)))
            cx, cy = x + w // 2, y + h // 2
            x0 = max(0, min(ref.shape[1] - side, cx - side // 2))
            y0 = max(0, min(ref.shape[0] - side, cy - side // 2))
            zoom = max(1.0, min(a.zoom_max, a.pane / side))
            crop = lambda im: _fit(cv2.resize(im[y0:y0 + side, x0:x0 + side], None,  # noqa: E731
                                              fx=zoom, fy=zoom, interpolation=cv2.INTER_NEAREST), a.pane)
            rp = os.path.join(outdir, f"region-{i}.png")
            imwrite(rp, side_by_side(crop(ref), crop(draft),
                                     f"REF x{zoom:.1f}", f"DRAFT x{zoom:.1f}"))
            written.append((rp, f"{kind} #{i} at ({x},{y},{w},{h}) "
                                f"mean-dist {badness:.0f}, {zoom:.1f}x"))
    else:
        p = os.path.join(outdir, "draft.png")
        if os.path.abspath(p) != os.path.abspath(draft_path):
            imwrite(p, _fit(draft, a.pane))
        written.append((p, "the drawing"))
        lines.append("no --ref given: nothing to compare against (reference-free stage)")

    report = os.path.join(outdir, "report.txt")
    lines_out = [
        f"art:    {a.art}",
        f"bundle: {outdir}",
        "",
        "images (feed these, and nothing else):",
    ]
    lines_out += [f"  {path}  -- {what}" for path, what in written]
    lines_out += [""] + lines
    if meta.get("stdout", "").strip():
        lines_out += ["", "resolver output (anchors + diagnostics — part of the evidence):",
                      "```", meta["stdout"].rstrip(), "```"]
    lines_out += [
        "",
        "reviewer protocol - do not skip:",
        "  Give ONLY the images above to a FRESH-context reviewer with no other context.",
        "  Ask the open question: 'what is wrong here?'",
        "  Never leak your intent, your history, or a suspected verdict.",
        "  Verify every claim against a measurement before acting on it (P7).",
        "",
        "This bundle carries no verdict by design - judging is the reviewer's job, not the tool's.",
    ]
    write_text(report, "\n".join(lines_out) + "\n")

    print(f"bundle: {outdir}")
    for path, what in written:
        print(f"  {what:52s} {path}")
    print(f"  {'report + reviewer protocol':52s} {report}")


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_baseline() -> dict | None:
    """The recorded best artifact's metadata, or None when nothing has been recorded yet."""
    if not os.path.exists(BASELINE_JSON):
        return None
    try:
        with open(BASELINE_JSON) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def delta(before: dict, after: dict) -> str:
    """before -> after per metric, so a regression reads as a regression."""
    parts = []
    for key in ("edge_f1", "coverage", "precision", "recall", "color_dist"):
        if key in before and key in after:
            parts.append(f"{key} {before[key]} -> {after[key]} ({after[key] - before[key]:+.3f})")
    return " | ".join(parts)


def cmd_baseline(a):
    """Record ART as the project's best artifact — the floor every later render is measured against."""
    if not os.path.exists(a.art):
        raise ToolError(f"baseline: no such artifact: {a.art}")
    draft = imread(a.art)
    entry = {
        "recorded": datetime.date.today().isoformat(),
        "source": os.path.abspath(a.art),
        "artifact": os.path.abspath(BASELINE_PNG),
        "sha256": _sha256(a.art),
        "note": a.note,
    }
    if a.ref:
        ref = imread(a.ref, (draft.shape[1], draft.shape[0]))
        entry["ref"] = os.path.abspath(a.ref)
        entry["metrics"] = metrics(ref, draft)
    ensure_dir(BASELINE_DIR)
    imwrite(BASELINE_PNG, draft)
    write_text(BASELINE_JSON, json.dumps(entry, indent=2) + "\n")
    print(f"recorded best: {BASELINE_PNG}")
    print(f"  from      : {a.art}")
    if entry.get("metrics"):
        print(f"  metrics   : {entry['metrics']}")
    print(f"  provenance: {BASELINE_JSON}")


def xdog(img: np.ndarray, sigma=1.0, k=1.6, p=25, eps=0.005, phi=10) -> np.ndarray:
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float64) / 255.0
    g1 = cv2.GaussianBlur(g, (0, 0), sigma)
    g2 = cv2.GaussianBlur(g, (0, 0), sigma * k)
    d = (1 + p) * g1 - p * g2
    d /= max(d.max(), 1e-9)
    u = np.where(d >= eps, 1.0, 1.0 + np.tanh(phi * (d - eps)))
    return (u * 255).astype(np.uint8)


def cmd_ref(a):
    img = imread(a.image)
    if a.kind == "lineart":
        out = 255 - xdog(img, **a.params)  # black lines on white
        if a.color:  # keep faint color underlay for orientation
            out = cv2.addWeighted(img, 0.25, cv2.cvtColor(out, cv2.COLOR_GRAY2BGR), 0.75, 0)
    else:  # palette
        Z = img.reshape(-1, 3).astype(np.float32)
        Z = Z[np.random.choice(len(Z), min(20000, len(Z)), replace=False)]
        crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
        _, labels, centers = cv2.kmeans(Z, a.k, None, crit, 3, cv2.KMEANS_PP_CENTERS)  # type: ignore[arg-type]
        counts = np.bincount(labels.flatten(), minlength=a.k)
        order = np.argsort(-counts)
        sw, hexes = [], []
        for i in order:
            c = centers[i].astype(int)
            hexes.append("#%02x%02x%02x" % (c[2], c[1], c[0]))
            row = np.full((60, 60, 3), c, np.uint8)
            cv2.putText(row, hexes[-1][1:], (3, 52), cv2.FONT_HERSHEY_SIMPLEX,
                        0.38, (255, 255, 255) if sum(c) < 360 else (0, 0, 0), 1, cv2.LINE_AA)
            sw.append(row)
        cols = 8
        rows = [np.hstack(sw[i:i + cols] + [np.full((60, 60, 3), 255, np.uint8)] * (cols - len(sw[i:i + cols])))
                for i in range(0, len(sw), cols)]
        out = np.vstack(rows)
        print(" ".join(hexes))
    imwrite(a.out, out)
    print(a.out)


def cmd_log(a):
    path = os.path.join(a.exdir, "log.md")
    row = f"| {a.iter} |"
    if a.src and a.ref:
        size = render(a.src, "/tmp/_log.png") if a.src.endswith((".svg", ".html")) else None
        draft = imread(a.src, size) if not a.src.endswith((".svg", ".html")) else imread("/tmp/_log.png")
        ref = imread(a.ref, (draft.shape[1], draft.shape[0]))
        m = metrics(ref, draft)
        row += f" {m['edge_f1']} | {m['color_dist']} |"
    else:
        row += " - | - |"
    line = f"{row} {a.note} |\n"
    if not os.path.exists(path):
        write_text(path, "# iteration log\n\n| iter | edge-F1 | color-dist | note |\n|---|---|---|---|\n")
    append_text(path, line)
    print("logged:", line.strip())


def cmd_measure(a):
    img = imread(a.image)
    if a.hough:
        g = cv2.GaussianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), (5, 5), 1)
        minR, maxR = (a.rmin, a.rmax) if a.rmin else (14, 130)
        circ = cv2.HoughCircles(g, cv2.HOUGH_GRADIENT, 1.2, 40,
                                param1=120, param2=30, minRadius=minR, maxRadius=maxR)
        if circ is not None:
            for c in circ[0][:10]:
                print("circle: x=%.0f y=%.0f r=%.0f" % tuple(c))
        return
    if a.point:
        x, y = a.point
        print("#%02x%02x%02x" % tuple(img[y, x][::-1])); return
    if a.scan:  # "row:y:x0:x1" or "col:x:y0:y1" - print color transitions
        kind, v, lo, hi = a.scan.split(":"); v, lo, hi = whole(v), whole(lo), whole(hi)
        line = img[v, lo:hi] if kind == "row" else img[lo:hi, v]
        prev = None
        for i, p in enumerate(line):
            hexc = "#%02x%02x%02x" % tuple(p[::-1])
            key = hexc[:4]
            if key != prev:
                pos = lo + i
                print(("x" if kind == "row" else "y") + str(pos), hexc)
                prev = key
        return
    print("nothing to do: use --hough, --point x,y or --scan row:y:x0:x1")


def smooth_path(pts, closed=True):
    """Points [(x,y)...] -> smooth SVG path (quadratic through midpoints)."""
    pts = [tuple(map(float, p)) for p in pts]
    if closed and pts[0] != pts[-1]:
        pts = pts + [pts[0]]
    d = f"M {pts[0][0]:.0f} {pts[0][1]:.0f} "
    for i in range(1, len(pts) - 1):
        mx = (pts[i][0] + pts[i + 1][0]) / 2
        my = (pts[i][1] + pts[i + 1][1]) / 2
        d += f"Q {pts[i][0]:.0f} {pts[i][1]:.0f} {mx:.0f} {my:.0f} "
    d += "Z" if closed else f"L {pts[-1][0]:.0f} {pts[-1][1]:.0f}"
    return d


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("render"); p.add_argument("src"); p.add_argument("-o", "--out", default="/tmp/_render.png"); p.add_argument("--size")
    p.set_defaults(fn=lambda a: print(a.out, render(a.src, a.out, size_arg(a.size))))

    p = sub.add_parser("compare"); p.add_argument("ref"); p.add_argument("src")
    p.add_argument("--region"); p.add_argument("--zoom", type=float, default=1)
    p.add_argument("-o", "--out", default="/tmp/_compare.png")
    p.set_defaults(fn=lambda a: setattr(a, "region", [whole(v) for v in a.region.split(",")] if a.region else None) or cmd_compare(a))

    p = sub.add_parser("diff"); p.add_argument("ref"); p.add_argument("src")
    p.add_argument("--mode", choices=["line", "color"], default="line")
    p.add_argument("--hints", type=int, default=5)
    p.add_argument("-o", "--out", default="/tmp/_diff.png")
    p.set_defaults(fn=cmd_diff)

    p = sub.add_parser("ref"); p.add_argument("image"); p.add_argument("kind", choices=["lineart", "palette"])
    p.add_argument("--k", type=int, default=12); p.add_argument("--color", action="store_true")
    p.add_argument("-o", "--out", default="/tmp/_ref.png")
    p.set_defaults(fn=lambda a: setattr(a, "params", {}) or cmd_ref(a))

    p = sub.add_parser("check"); p.add_argument("art", help="svg/html/png or a spec .yaml to render")
    p.add_argument("--ref", default=None, help="reference image; omit for the reference-free stage")
    p.add_argument("--outdir", default=None, help="default: <exercise>/evidence/check")
    p.add_argument("--resolver", default=None, help="explicit relate.py path; default: beside the spec, then scripts/relate.py")
    p.add_argument("--regions", type=int, default=3, help="worst regions to crop (default 3)")
    p.add_argument("--pane", type=int, default=256, help="max px per pane (default 256)")
    p.add_argument("--zoom-max", type=float, default=3.0, dest="zoom_max")
    p.set_defaults(fn=cmd_check)

    p = sub.add_parser("log"); p.add_argument("exdir"); p.add_argument("--iter", type=int)
    p.add_argument("--ref"); p.add_argument("--src"); p.add_argument("--note", default="")
    p.set_defaults(fn=cmd_log)

    p = sub.add_parser("baseline", help="record ART as the project's best artifact (ratchet floor)")
    p.add_argument("art"); p.add_argument("--ref", default=None); p.add_argument("--note", default="")
    p.set_defaults(fn=cmd_baseline)

    p = sub.add_parser("measure"); p.add_argument("image")
    p.add_argument("--hough", action="store_true"); p.add_argument("--rmin", type=int); p.add_argument("--rmax", type=int)
    p.add_argument("--point"); p.add_argument("--scan")
    p.set_defaults(fn=lambda a: setattr(a, "point", [whole(v) for v in a.point.split(",")] if a.point else None) or cmd_measure(a))

    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()

