"""Where the hand and the dish interleave, the rear edge is BROKEN by depth - and the check bites.

The claim is not "the nearer thing is painted last".  Strokes are emitted in a separate pass
from the fills, so the only reason a rear edge is missing is that the depth test removed it.
This audit therefore works on geometry:

  * take every ink curve the drawing carries, from two *different* parts (a digit and the dish,
    or one digit and another);
  * find where two of them cross in 2D;
  * require the two surfaces to be at least `MIN_SEP` apart in depth there - a crossing with no
    depth separation is not an occlusion, it is a coincidence;
  * require the rear curve's stroke to be *absent* at that station in the delivered SVG.

The mutation is the build's `--no-depth-break`, which emits every stroke whole.  The same audit
run against it must fail, and `negative_control()` records both counts.
"""
from __future__ import annotations

import os
import re
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import util  # noqa: E402

import build  # noqa: E402

SVG = os.path.join(util.EVIDENCE, "artwork.svg")
RECORD = os.path.join(HERE, "negative-control-output.txt")
INK = re.compile(r'<polyline class="(\w+)" data-part="(\w+)" data-id="(\w+)" '
                 r'data-s0="([\d.]+)" data-s1="([\d.]+)"')
MIN_SEP = 6.0          # px of depth: below this a crossing is not an occlusion
STEP = 3               # px of stroke sampled per segment; finer than any digit is wide
MIN_CROSSINGS = 6
BROKEN_MARGIN = 0.004  # of a curve's own length: a stroke ending nearer than this was broken


def emitted_runs(path=SVG):
    """{(part, id): [(s0, s1), ...]} straight out of the delivered SVG."""
    out = {}
    for _kind, part, ident, s0, s1 in INK.findall(open(path).read()):
        out.setdefault((part, ident), []).append((float(s0), float(s1)))
    return out


def _segments(curve):
    """Subsample one ink curve into (a, b, s_mid) segments in screen space with depth."""
    pts = curve["pts"]
    n = len(pts)
    if n < 2:
        return []
    idx = list(range(0, n - 1, STEP)) + [n - 1]
    segs = []
    for i, j in zip(idx, idx[1:]):
        if j <= i:
            continue
        segs.append((pts[i], pts[j], i / (n - 1), j / (n - 1)))
    return segs


def _cross_pairs(segs_a, segs_b):
    """All (i, j) where segment i of A crosses segment j of B, plus the crossing parameters."""
    if not segs_a or not segs_b:
        return []
    A = np.array([[s[0][:2], s[1][:2]] for s in segs_a])       # (na, 2 pts, 2)
    B = np.array([[s[0][:2], s[1][:2]] for s in segs_b])
    p, r = A[:, 0, :][:, None, :], (A[:, 1, :] - A[:, 0, :])[:, None, :]
    q, s = B[:, 0, :][None, :, :], (B[:, 1, :] - B[:, 0, :])[None, :, :]
    den = r[..., 0] * s[..., 1] - r[..., 1] * s[..., 0]
    qp = q - p
    ok = np.abs(den) > 1e-12
    with np.errstate(invalid="ignore", divide="ignore"):
        t = (qp[..., 0] * s[..., 1] - qp[..., 1] * s[..., 0]) / den
        u = (qp[..., 0] * r[..., 1] - qp[..., 1] * r[..., 0]) / den
    hit = ok & (t >= 0.0) & (t <= 1.0) & (u >= 0.0) & (u <= 1.0)
    return [(int(i), int(j), float(t[i, j]), float(u[i, j]))
            for i, j in zip(*np.nonzero(hit))]


def _depth(seg, w):
    a, b, _s0, _s1 = seg
    return float(a[2] * (1.0 - w) + b[2] * w)


def _station(seg, w):
    _a, _b, s0, s1 = seg
    return float(s0 * (1.0 - w) + s1 * w)


def audit(path=SVG, res=None):
    """Returns (occlusions audited, failures, contacts, crossings) for one emitted drawing.

    A crossing whose two surfaces are less than `MIN_SEP` apart in depth is not an occlusion:
    it is a *contact*, the place where two digits merge or a fingertip meets the rim, and no
    edge is expected to disappear there.  Those are counted and reported, never ignored - the
    roots' merge is a stated fact of this hand, not a hidden one.
    """
    res = res or build.resolve()
    runs = emitted_runs(path)
    curves = res["curves"]
    failures, contacts, total, occlusions = [], [], 0, 0
    for i, first in enumerate(curves):
        for second in curves[i + 1:]:
            if first["part"] == second["part"]:
                continue
            segs_a, segs_b = _segments(first), _segments(second)
            for ia, ib, t, u in _cross_pairs(segs_a, segs_b):
                total += 1
                za = _depth(segs_a[ia], t)
                zb = _depth(segs_b[ib], u)
                sa = _station(segs_a[ia], t)
                sb = _station(segs_b[ib], u)
                here = (f"{first['part']}.{first['id']} x {second['part']}.{second['id']} "
                        f"at ({segs_a[ia][0][0]:.0f},{segs_a[ia][0][1]:.0f})")
                if abs(za - zb) < MIN_SEP:
                    contacts.append(f"{abs(za - zb):.1f} px: {here}")
                    continue
                occlusions += 1
                rear, rear_s = ((first, sa) if za > zb else (second, sb))
                spans = runs.get((rear["part"], rear["id"]), [])
                drawn = any(a + BROKEN_MARGIN <= rear_s <= b - BROKEN_MARGIN for a, b in spans)
                if drawn:
                    failures.append(f"rear edge drawn through, {here} (rear {rear['part']}, "
                                    f"s={rear_s:.3f})")
    return occlusions, failures, contacts, total


class TestOcclusionIsBrokenByDepth(unittest.TestCase):
    def test_the_hand_and_the_dish_do_cross_in_the_drawing(self):
        occlusions, _fail, contacts, total = audit()
        print(f"  {total} 2D crossings between ink curves of different parts: "
              f"{occlusions} with a depth gap, {len(contacts)} contacts")
        self.assertGreaterEqual(occlusions, MIN_CROSSINGS,
                                "too few occlusions: the depth-break test would test nothing")

    def test_every_occlusion_has_a_broken_rear_edge(self):
        occlusions, failures, contacts, total = audit()
        for f in failures:
            print("  FAIL " + f)
        print(f"  {occlusions} occlusions, {len(failures)} failures; "
              f"contacts (no depth gap, no break expected): {len(contacts)}")
        self.assertEqual(failures, [])


def negative_control_text():
    """The whole record, both controls, computed from the build on disk - never hand-written."""
    healthy_total, healthy_bad, healthy_contacts, _t = audit()
    res = build.resolve(break_depth=False)
    mutated = os.path.join(HERE, "_negative-control.svg")
    with open(mutated, "w") as fh:
        fh.write(build.svg(res))
    try:
        m_total, m_bad, m_contacts, _mt = audit(mutated, res=res)
    finally:
        os.remove(mutated)
    lines = [
        "occlusion-break negative control (P37): the mechanism must be visible as a failure",
        f"real build : {healthy_total} occlusions, {len(healthy_bad)} failures, "
        f"{len(healthy_contacts)} contacts",
        f"mutation   : --no-depth-break, {m_total} occlusions, {len(m_bad)} failures, "
        f"{len(m_contacts)} contacts",
    ]
    if healthy_bad:
        lines.append("  real-build failures: " + "; ".join(healthy_bad[:6]))
    if m_bad:
        lines.append("  mutation failures (expected, this is the point):")
        lines += ["    " + f for f in m_bad[:8]]
    lines.append("PASS: the depth break is what makes the test pass"
                 if not healthy_bad and m_bad else
                 "FAIL: the mutation did not fail the audit")
    import test_hand_construction  # noqa: E402  (same directory; needs source/ on sys.path)
    return "\n".join(lines + [""] + test_hand_construction.contact_negative_control_lines()) + "\n"


def negative_control():
    """Regenerate the whole record - both controls - from the build on disk.

    It maintains the file: every section it owns is recomputed and rewritten, so the record
    cannot lose half of itself when the producer runs.  It never appends and never keeps an
    old section, and `TestNegativeControlRecord` fails when the committed file and a fresh
    computation disagree, so the record cannot go stale under a green suite either.
    """
    text = negative_control_text()
    open(RECORD, "w").write(text)
    return "FAIL:" not in text


class TestNegativeControlRecord(unittest.TestCase):
    def test_the_committed_record_is_this_revision(self):
        """The committed evidence states this build's numbers, or the suite is red."""
        committed = open(RECORD).read()
        fresh = negative_control_text()
        print(f"  negative-control record: {len(committed.splitlines())} lines committed, "
              f"{'identical' if committed == fresh else 'DIFFERS from this build'}")
        self.assertEqual(committed, fresh,
                         "tests/negative-control-output.txt does not state what this build "
                         "does; regenerate it with: PYTHONPATH=... python -c \"import sys; "
                         "sys.path[:0]=['tests','source','.']; import test_occlusion_break as t; "
                         "t.negative_control()\"")


if __name__ == "__main__":
    unittest.main(verbosity=2)
