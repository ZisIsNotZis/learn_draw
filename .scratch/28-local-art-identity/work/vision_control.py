#!/usr/bin/env python3
"""Generate the approved text-free vector capability control; no raster or neural generator."""
from __future__ import annotations

import hashlib
from pathlib import Path
from xml.etree import ElementTree

WIDTH, HEIGHT = 480, 320


def control_svg() -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="480" height="320" '
        'viewBox="0 0 480 320">'
        '<rect width="480" height="320" fill="#ffffff"/>'
        '<circle cx="96" cy="80" r="28" fill="#ff0000"/>'
        '<rect x="332" y="52" width="56" height="56" fill="#0000ff"/>'
        '<polygon points="68,212 124,212 96,268" fill="#ffff00"/>'
        '<polygon points="360,212 388,240 360,268 332,240" fill="#00ff00"/>'
        '</svg>'
    )


def validate_control_svg(markup: str) -> None:
    root = ElementTree.fromstring(markup)
    if root.tag != "{http://www.w3.org/2000/svg}svg":
        raise ValueError("control SVG must use the SVG namespace")
    if root.attrib != {"width": "480", "height": "320", "viewBox": "0 0 480 320"}:
        raise ValueError("control frame differs from the frozen 480x320 design")
    tags = [element.tag.rsplit("}", 1)[-1] for element in root]
    if tags != ["rect", "circle", "rect", "polygon", "polygon"]:
        raise ValueError("control must contain only its background and four frozen vector forms")
    if any(element.text or element.tail for element in root.iter()):
        raise ValueError("control must not include text clues")
    expected = control_svg()
    if markup != expected:
        raise ValueError("control geometry/color differs from the approved fixed composition")


def control_answer_key() -> dict:
    return {
        "schema": "local-art-identity-capability-answer/v1",
        "facts": [
            {"shape": "circle", "color": "red", "quadrant": "upper-left"},
            {"shape": "square", "color": "blue", "quadrant": "upper-right"},
            {"shape": "triangle", "color": "yellow", "quadrant": "lower-left"},
            {"shape": "diamond", "color": "green", "quadrant": "lower-right"},
        ],
    }


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


if __name__ == "__main__":
    content = control_svg()
    validate_control_svg(content)
    print(sha256(content.encode("utf-8")))
