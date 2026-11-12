"""The authoring inventory: every hand-typed coordinate pair in the part library.

A hand-typed coordinate pair is a two-number literal written in a part module: a tuple
literal such as `CHEST_XY = (231.0, 137.0)`, a `crop(x, y)` / `Point(x, y)` call with
two number literals, or a tuple literal inside a spec dict such as `root=(174.0, 92.0)`.
`scan()` finds them in the source text by AST, so the table below is checked against the
code and never against its own arithmetic: `audit()` compares the multiset of pairs in
each module with the multiset this file declares, and reports both an unaccounted pair
and a declared pair that no longer exists.

A pair is a *landmark* when it positions a part's shape.  Landmarks are what the
authoring budget counts (`tests/test_authoring_inventory.py` requires each part's
declared `authored` list to equal its landmarks exactly).  Everything else — a depth
gradient, a direction, a depth band, a fold fraction, a frame origin — is listed with
the reason it positions nothing.

Defect B3 of the v6 closeout: `bodice.py` hand-typed three stations but declared two
(`C0`/`CHEST_XY` was missing from `authored_input_xy`), so `A-bodice-upper.authored`
said 2 while the code had 3.  Run `python3 source/authored.py` for the per-part table.
"""
from __future__ import annotations

import ast
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PARTS_DIR = HERE / "parts"


def _number(node):
    """A numeric literal, including a signed one (`-0.0006` is a unary minus)."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
            and not isinstance(node.value, bool):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        value = _number(node.operand)
        if value is None:
            return None
        return -value if isinstance(node.op, ast.USub) else value
    return None


def scan(module: str) -> list[tuple]:
    """Every two-number literal pair in one part module, as (line, (x, y))."""
    tree = ast.parse((PARTS_DIR / f"{module}.py").read_text(encoding="utf-8"))
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Tuple) and len(node.elts) == 2:
            values = [_number(element) for element in node.elts]
            if all(value is not None for value in values):
                found.append((node.lineno, tuple(values)))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id in ("crop", "Point") and len(node.args) == 2:
            values = [_number(argument) for argument in node.args]
            if all(value is not None for value in values):
                found.append((node.lineno, tuple(values)))
    return found


# Landmarks: part -> ((name, (x, y)), ...).  The values are the module constants, so a
# station has one home; a value that changes here changes there.
LANDMARKS = {
    "bodice": {
        "A-bodice-upper": (("C0", (231.0, 137.0)), ("Cw", (174.0, 365.0)),
                           ("Eleft", (330.0, 175.0))),
    },
    "bow": {
        "A-bow-ribbon": (("knot", (185.0, 163.0)), ("left_lobe_tip", (122.0, 175.0)),
                         ("right_lobe_tip", (262.0, 186.0)), ("left_tail_exit", (20.0, 216.0))),
    },
    "collar": {
        "A-collar-left": (("R", (174.0, 92.0)), ("E", (137.0, 159.0)),
                          ("S", (168.0, 128.0))),
        "A-collar-right": (("R", (230.0, 78.0)), ("E", (279.0, 150.0)),
                           ("S", (255.0, 139.0))),
    },
    "hair": {
        "A-hair-sheet": (("left_tip", (126.0, 356.0)), ("left_bulge", (84.0, 188.0)),
                         ("crown", (206.0, -22.0)), ("right_shoulder", (322.0, 210.0)),
                         ("right_tip", (286.0, 492.0))),
    },
    "head": {
        "A-head-face": (("chin", (212.0, 122.0)), ("jaw_left", (198.0, 101.0)),
                        ("jaw_right", (241.0, 97.0))),
    },
    "sleeve": {
        "A-right-sleeve": (("C", (362.0, 300.0)),),
        "A-left-sleeve": (("C", (81.0, 271.0)),),
    },
}

# A pair one relation owns rather than one part: the two collar leaves are solved on the
# shared opening station, so neither leaf carries it as its own landmark.
SHARED = {
    "collar": ((("open", (214.0, 158.0)), ("A-collar-left", "A-collar-right")),),
}

# Everything else that looks like a hand-typed pair, grouped by why it is not a station.
NOT_LANDMARKS = {
    "bodice": (
        ("the body support's depth gradient FRAME_GRAD (a depth slope, not a station)",
         ((0.0, -0.0006),)),
        ("the body width field's chest and waist half widths (scalars, not stations)",
         ((125.0, 70.0),)),
        ("anchor tangent directions (local seam directions)", ((0.0, -1.0), (0.0, 1.0))),
    ),
    "bow": (
        ("the down tail's direction (a unit vector in crop pixels, y down)", ((-0.22, 0.976),)),
        ("the first ribbon piece's depth band (z at its two ends)", ((0.6, 0.6),)),
        ("a zero control-point offset in the knot bridge (no displacement)",
         ((0.0, 0.0),)),
        ("the knot anchor's tangent direction", ((1.0, 0.0),)),
    ),
    "collar": (
        ("the left leaf's depth gradient", ((-0.0004, 0.0002),)),
        ("the right leaf's depth gradient", ((0.0001, 0.0003),)),
        ("an anchor tangent (the leaf's local +u, defined as R -> Q)", ((1.0, 0.0),)),
    ),
    "families": (
        ("gather-fold fractions along the body width field (parameters, not stations)",
         ((0.32, 0.62),)),
    ),
    "frames": (
        ("the default depth gradient of a flat plane support", ((0.0, 0.0),)),
    ),
    "head": (
        ("the head frame's origin (a coordinate origin, not a shape station)",
         ((216.0, 60.0),)),
        ("the head frame's depth gradient", ((0.0, 0.0),)),
    ),
    "skin": (
        ("the neck frame's depth gradient", ((0.0, 0.0),)),
    ),
    "sleeve": (
        ("the right sleeve's depth gradient", ((-0.0003, -0.0004),)),
        ("the left sleeve's depth gradient", ((0.0001, -0.0003),)),
        ("a local origin and the anchor tangent directions (0,0)/(0,+-1)",
         ((0.0, 0.0), (0.0, 0.0), (0.0, 1.0), (0.0, 1.0), (0.0, -1.0), (0.0, 1.0),
          (0.0, -1.0))),
    ),
}

MODULES = tuple(sorted(set(LANDMARKS) | set(NOT_LANDMARKS) | {"skin"}))


def declared(module: str) -> Counter:
    """The multiset of pairs this inventory attributes to one module."""
    pairs = Counter()
    for entries in LANDMARKS.get(module, {}).values():
        pairs.update(value for _name, value in entries)
    for (_name, value), _parts in SHARED.get(module, ()):
        pairs.update([value])
    for _reason, values in NOT_LANDMARKS.get(module, ()):
        pairs.update(values)
    return pairs


def audit() -> list[str]:
    """Disagreements between the source text and this inventory, one line each."""
    problems = []
    for module in MODULES:
        in_source = Counter(pair for _line, pair in scan(module))
        stated = declared(module)
        for pair, count in sorted((in_source - stated).items()):
            lines = [line for line, found in scan(module) if found == pair]
            problems.append(f"{module}.py:{lines} has {count} unaccounted pair(s) {pair}")
        for pair, count in sorted((stated - in_source).items()):
            problems.append(f"{module}: {count} declared pair(s) {pair} are not in the source")
    return problems


def landmarks(module: str, part: str):
    return LANDMARKS.get(module, {}).get(part, ())


def shared_for(part: str):
    out = []
    for (name, value), parts in (entry for entries in SHARED.values() for entry in entries):
        if part in parts:
            out.append((name, value))
    return tuple(out)


def table():
    """Per-part: landmarks, shared stations, and the declared count to compare with."""
    rows = []
    for module, parts in sorted(LANDMARKS.items()):
        for part, entries in sorted(parts.items()):
            shared = shared_for(part)
            rows.append(dict(module=module, part=part, own=len(entries),
                             shared=len(shared), landmarks=entries,
                             shared_names=tuple(name for name, _value in shared)))
    for module in MODULES:
        if module in LANDMARKS:
            continue
        rows.append(dict(module=module, part="-", own=0, shared=0, landmarks=(),
                         shared_names=()))
    return rows


def main() -> int:
    problems = audit()
    print(f"{'part':26s} {'module':9s} {'own':>3s} {'shared':>6s}  landmarks")
    for row in table():
        names = ", ".join(name for name, _value in row["landmarks"])
        print(f"{row['part']:26s} {row['module']:9s} {row['own']:3d} {row['shared']:6d}  {names}")
    for line in problems:
        print(f"UNACCOUNTED {line}", file=sys.stderr)
    print(f"modules scanned {len(MODULES)}, pairs declared "
          f"{sum(sum(declared(m).values()) for m in MODULES)}, problems {len(problems)}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
