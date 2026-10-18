"""The seam contract: declared cloth-to-cloth joints, checked geometrically.

The defect this milestone fixes was a joint asserted only by name: an attachment
stored three strings, nothing compared the two boundaries, and the rendered cloth
came apart.  Here every declared joint is a pair of named anchors, and the check
compares real geometry:

* a `seam` is a place where two cloth pieces are sewn together, so both anchors
  must (a) lie on their own part's boundary, (b) coincide within `POSITION_EPS`,
  (c) share a tangent direction within `TANGENT_EPS`, and (d) satisfy the declared
  depth relation (two cloth pieces sewn on depth planes that disagree are not one
  surface);
* an `attachment` is a place where one piece is set into another (a sleeve into a
  shoulder), so only the position and the layering are compared — there is no shared
  boundary direction to compare, and claiming one would be the same lie in a
  different form.  An attachment's anchors are *not* boundary-checked; the README and
  this docstring say so, and `NON_JOINTS` below accounts for every anchor that is not
  a joint at all.

`check` returns one finding per joint for every declared joint; a build fails if any
finding is not ok.

What the tangent clause does and does not prove.  Each side's tangent is the direction
that side declares for the seam: the collar leaf's local +u is defined as R -> Q, the
sleeve's cross direction is the terminal section, and the bodice, band and skin
anchors compute `_toward(anchor, anchor)` from two shared stations.  Because both
sides name the same two stations, the clause compares two independent derivations of
one direction in two different frames -- it verifies *declaration consistency*, not a
direction read off the emitted outline.  Deriving the tangent from the sampled outline
instead was measured and rejected: the polygon's local chord at an anchor departs from
the cloth's seam direction by up to 87 degrees at a corner (S8-band-continuation),
because the outline is a sampled contour and not a seam.  The consequence is recorded
in the README: the clause can catch a rotated declared direction (negative control
`test_negative_control_rotated_tangent` in `tests/test_seam_contract.py`) and cannot
catch an outline that rotates while its anchor stays put.

Completeness is checked, not asserted: every anchor a part declares must appear in a
`Joint` here or in `NON_JOINTS` with a stated reason, and every `NON_JOINTS` entry must
name a real declared anchor.  `tests/test_anchor_inventory.py` enforces both directions.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

POSITION_EPS = 1e-6
TANGENT_EPS = 1e-6
BOUNDARY_EPS = 1e-6

SAME_SURFACE = ("same_surface", 2e-3)     # two pieces of one cloth: same depth
CLOTH_LAYER = ("front_is_b", 0.30)        # b is layered over a, within one cloth thickness


@dataclass(frozen=True)
class Joint:
    """One declared joint between two parts.

    kind: "seam" (sewn: boundaries meet and share a direction) or "attachment"
    (one piece set into another: position and layering only).
    depth: how the two supports must relate — see SAME_SURFACE / CLOTH_LAYER.
    """
    name: str
    kind: str
    a: tuple
    b: tuple
    depth: tuple = SAME_SURFACE
    note: str = ""


JOINTS = (
    Joint("S1-collar-front", "seam", ("A-collar-left", "Q_prime"), ("A-collar-right", "Q_prime"),
          note="the two collar leaves share the finite front seam Q..Q'"),
    Joint("S2-collar-left-root", "seam", ("A-bodice-upper", "opening_left_root"), ("A-collar-left", "R"),
          CLOTH_LAYER, "the collar leaf is sewn on the bodice's opening edge"),
    Joint("S3-collar-right-root", "seam", ("A-bodice-upper", "opening_right_root"), ("A-collar-right", "R"),
          CLOTH_LAYER),
    Joint("S4-skin-left-root", "seam", ("A-visible-neck-skin", "R_left"), ("A-collar-left", "R"), CLOTH_LAYER),
    Joint("S5-skin-right-root", "seam", ("A-visible-neck-skin", "R_right"), ("A-collar-right", "R"), CLOTH_LAYER),
    Joint("S6-skin-opening", "seam", ("A-bodice-upper", "Q"), ("A-visible-neck-skin", "Q"), CLOTH_LAYER,
          "the neck field is cut by the same opening station as the bodice"),
    Joint("S7-waist-section", "seam", ("A-bodice-upper", "waist_left"), ("A-derived-waist-band", "upper_left")),
    Joint("S7-waist-section-right", "seam", ("A-bodice-upper", "waist_right"), ("A-derived-waist-band", "upper_right")),
    Joint("S8-band-continuation", "seam", ("A-derived-waist-band", "lower_left"), ("A-bodice-continuation", "upper_left")),
    Joint("S8-band-continuation-right", "seam", ("A-derived-waist-band", "lower_right"), ("A-bodice-continuation", "upper_right")),
    Joint("S9-right-cuff", "seam", ("A-right-sleeve", "terminal_left"), ("A-right-cuff", "contact_left")),
    Joint("S9-right-cuff-right", "seam", ("A-right-sleeve", "terminal_right"), ("A-right-cuff", "contact_right")),
    Joint("S10-left-cuff", "seam", ("A-left-sleeve", "terminal_left"), ("A-left-cuff", "contact_left")),
    Joint("S10-left-cuff-right", "seam", ("A-left-sleeve", "terminal_right"), ("A-left-cuff", "contact_right")),
    Joint("S11-jaw-left", "seam", ("A-head-face", "jaw_left"), ("A-visible-neck-skin", "jaw_left"),
          SAME_SURFACE, "the face field ends on the same jaw relation the neck starts from"),
    Joint("S12-jaw-right", "seam", ("A-head-face", "jaw_right"), ("A-visible-neck-skin", "jaw_right"),
          SAME_SURFACE),
    Joint("A1-right-sleeve-seat", "attachment", ("A-bodice-upper", "shoulder_left"), ("A-right-sleeve", "seat"),
          CLOTH_LAYER, "the sleeve is set into the shoulder; there is no shared boundary direction"),
    Joint("A2-left-sleeve-seat", "attachment", ("A-bodice-upper", "left_seat"), ("A-left-sleeve", "seat"),
          CLOTH_LAYER),
)

# Every declared (part, anchor) pair that is *not* a joint, with the reason it is not.
# `tests/test_anchor_inventory.py` fails in both directions: a part that declares an
# anchor appearing in neither this map nor a Joint, and an entry here that names an
# anchor no part declares.
NON_JOINTS = {
    ("A-head-face", "chin"): "a station on the jaw seam between the two joint anchors; the seam is "
                             "declared at its two ends and the chin is read as the shared relation's "
                             "midpoint, not as a joint",
    ("A-bow-ribbon", "knot"): "the tie's own centre station; the ribbon is one part, so the knot is "
                              "not a joint between two pieces",
}


def _on_boundary(part, plane_point, eps=BOUNDARY_EPS) -> bool:
    points = [part.frame.to_plane(p) for p in part.outline]
    for a, b in zip(points, points[1:] + points[:1]):
        ax, ay = a.u, a.v
        bx, by = b.u, b.v
        dx, dy = bx - ax, by - ay
        length_sq = dx * dx + dy * dy
        if length_sq <= 1e-18:
            continue
        t = max(0.0, min(1.0, ((plane_point.u - ax) * dx + (plane_point.v - ay) * dy) / length_sq))
        px, py = ax + dx * t, ay + dy * t
        if math.hypot(plane_point.u - px, plane_point.v - py) <= eps:
            return True
    return False


def _tangent_error(ta, tb):
    na = math.hypot(*ta)
    nb = math.hypot(*tb)
    if na <= 1e-12 or nb <= 1e-12:
        return math.inf
    return abs(ta[0] * tb[1] - ta[1] * tb[0]) / (na * nb)   # |sin|: parallel or antiparallel both pass


def check(parts, joints=JOINTS):
    """Return findings for every declared joint. A finding is not ok when it fails."""
    findings = []
    for joint in joints:
        problems = []
        missing = [name for name in (joint.a[0], joint.b[0]) if name not in parts]
        if missing:
            findings.append(dict(name=joint.name, kind=joint.kind, ok=False,
                                 detail=f"missing part(s): {', '.join(missing)}"))
            continue
        pa = parts[joint.a[0]]
        pb = parts[joint.b[0]]
        try:
            point_a, depth_a, tangent_a = pa.plane_anchor(joint.a[1])
            point_b, depth_b, tangent_b = pb.plane_anchor(joint.b[1])
        except (KeyError, IndexError) as exc:
            findings.append(dict(name=joint.name, kind=joint.kind, ok=False,
                                 detail=f"undeclared anchor: {exc}"))
            continue
        gap = math.hypot(point_a.u - point_b.u, point_a.v - point_b.v)
        if gap > POSITION_EPS:
            problems.append(f"boundary gap {gap:.6f} > {POSITION_EPS}")
        rule, bound = joint.depth
        drop = depth_b - depth_a
        if rule == "same_surface":
            if abs(drop) > bound:
                problems.append(f"depth gap {abs(drop):.6f} > {bound}")
        elif rule == "front_is_b":
            if not (0.0 <= drop <= bound):
                problems.append(f"{joint.b[0]} is not layered 0..{bound} in front of "
                                f"{joint.a[0]} (gap {drop:.6f})")
        else:
            problems.append(f"unknown depth rule {rule}")
        if joint.kind == "seam":
            if tangent_a is None or tangent_b is None:
                problems.append("seam anchor has no tangent")
            else:
                error = _tangent_error(tangent_a, tangent_b)
                if error > TANGENT_EPS:
                    problems.append(f"tangent mismatch {error:.6f} > {TANGENT_EPS}")
            for part, point, side in ((pa, point_a, joint.a), (pb, point_b, joint.b)):
                if not _on_boundary(part, point):
                    problems.append(f"{side[0]}.{side[1]} is not on that part's boundary")
        findings.append(dict(name=joint.name, kind=joint.kind, ok=not problems,
                             detail="; ".join(problems)))
    return findings


def failures(findings):
    return [f for f in findings if not f["ok"]]


def joint_endpoints(joints=JOINTS):
    """Every (part, anchor) pair a joint reads."""
    return {(joint.a[0], joint.a[1]) for joint in joints} | {(joint.b[0], joint.b[1]) for joint in joints}


def declared_anchors(parts):
    """Every (part, anchor) pair the part library declares."""
    return {(name, key) for name, part in parts.items() for key in part.anchors}


def unaccounted_anchors(parts, joints=JOINTS, non_joints=None):
    """Declared anchors that no joint reads and no reason excuses.

    An anchor that nothing reads is an unchecked claim about a boundary, so the set
    must be empty; `tests/test_anchor_inventory.py` holds it at zero and the build
    fails when it is not.  The called-with inventory is also checked the other way:
    an entry that names an anchor no part declares is reported too.
    """
    if non_joints is None:
        non_joints = NON_JOINTS
    endpoints = joint_endpoints(joints)
    declared = declared_anchors(parts)
    unaccounted = sorted(declared - endpoints - set(non_joints))
    phantom = sorted((set(non_joints) | endpoints) - declared)
    reasons_missing = sorted(key for key, reason in non_joints.items() if not reason.strip())
    return dict(declared=len(declared), joint_endpoints=len(declared & endpoints),
                non_joints=len(declared & set(non_joints)),
                unaccounted=[f"{part}.{anchor}" for part, anchor in unaccounted],
                non_joint_without_reason=[f"{part}.{anchor}" for part, anchor in reasons_missing],
                inventory_names_a_missing_anchor=[f"{part}.{anchor}" for part, anchor in phantom])
