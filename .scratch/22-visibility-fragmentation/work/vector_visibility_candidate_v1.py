"""Orthographic vector visibility for opaque triangular support surfaces.

Fragments carry projected (x,y,depth); visibility is derived from geometry,
never authored front/back ranges. Slow reference implementation for small scenes.
"""

EPS = 1e-7


def line_clip(poly, fn, keep_positive=True):
    if not poly:
        return []
    out = []
    for a, b in zip(poly, poly[1:] + poly[:1]):
        fa, fb = fn(a), fn(b)
        inside_a = fa >= -EPS if keep_positive else fa <= EPS
        inside_b = fb >= -EPS if keep_positive else fb <= EPS
        if inside_a != inside_b:
            t = fa / (fa - fb)
            out.append(tuple(a[k] + t * (b[k] - a[k]) for k in range(3)))
        if inside_b:
            out.append(b)
    return out


def bbox(poly):
    return (min(p[0] for p in poly), min(p[1] for p in poly),
            max(p[0] for p in poly), max(p[1] for p in poly))


def overlaps(a, b):
    return a[0] < b[2] - EPS and b[0] < a[2] - EPS and a[1] < b[3] - EPS and b[1] < a[3] - EPS


def positive_area_overlap(a, b):
    """Return whether two projected convex polygons overlap with positive area."""
    for polygon in (a, b):
        for first, second in zip(polygon, polygon[1:] + polygon[:1]):
            axis = (second[1] - first[1], first[0] - second[0])
            a_projection = [axis[0] * point[0] + axis[1] * point[1] for point in a]
            b_projection = [axis[0] * point[0] + axis[1] * point[1] for point in b]
            if max(a_projection) <= min(b_projection) or max(b_projection) <= min(a_projection):
                return False
    return True


def depth_plane(tri):
    (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = tri
    det = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
    if abs(det) < EPS:
        return None
    a = ((z1 - z0) * (y2 - y0) - (z2 - z0) * (y1 - y0)) / det
    b = ((x1 - x0) * (z2 - z0) - (x2 - x0) * (z1 - z0)) / det
    return a, b, z0 - a * x0 - b * y0


def subtract_convex(subject, cutter):
    """Subtract convex cutter in screen space, preserving depth on subject."""
    area = sum(a[0] * b[1] - b[0] * a[1]
               for a, b in zip(cutter, cutter[1:] + cutter[:1]))
    if abs(area) < EPS:
        return [subject]
    orientation = 1 if area > 0 else -1
    inside = subject
    outside = []
    for a, b in zip(cutter, cutter[1:] + cutter[:1]):
        def edge(p):
            return orientation * ((b[0] - a[0]) * (p[1] - a[1])
                                  - (b[1] - a[1]) * (p[0] - a[0]))
        piece = line_clip(inside, edge, False)
        if len(piece) >= 3:
            outside.append(piece)
        inside = line_clip(inside, edge, True)
        if len(inside) < 3:
            break
    return outside


def visible_fragments(faces):
    """Yield (visible polygon, color, component) for projected triangular faces.

    Depth increases toward the viewer. Face entries: (triangle, color, component).
    Compare actual depth functions at overlap; no global painter ordering.
    """
    prepared = []
    for tri, color, component in faces:
        plane = depth_plane(tri)
        if plane is not None:
            prepared.append((tri, color, component, plane, bbox(tri)))
    for index, (tri, color, component, plane, box) in enumerate(prepared):
        fragments = [list(tri)]
        for other_index, (other, _, _, other_plane, other_box) in enumerate(prepared):
            if (other_index == index or not overlaps(box, other_box)
                    or not positive_area_overlap(tri, other)):
                continue
            # The portion of the occluder whose depth exceeds this face's plane.
            # A deterministic tie rule avoids duplicate coplanar output.
            da = other_plane[0] - plane[0]
            db = other_plane[1] - plane[1]
            dc = other_plane[2] - plane[2]
            bias = 1e-5 if other_index < index else -1e-5
            cutter = line_clip(list(other),
                               lambda p: da * p[0] + db * p[1] + dc + bias,
                               True)
            if len(cutter) < 3:
                continue
            next_fragments = []
            cut_box = bbox(cutter)
            for frag in fragments:
                if overlaps(bbox(frag), cut_box):
                    next_fragments.extend(subtract_convex(frag, cutter))
                else:
                    next_fragments.append(frag)
            fragments = next_fragments
            if not fragments:
                break
        for frag in fragments:
            yield frag, color, component


def _compound_path(polygons):
    """Serialize filled polygons as consistently wound SVG subpaths.

    Keeping a semantic fill in one path lets the SVG rasterizer cancel shared
    tessellation edges instead of antialiasing each face independently. No
    stroke or geometric expansion is applied, so true outer/occlusion edges
    remain exactly the visibility boundary.
    """
    parts = []
    for polygon in polygons:
        area = sum(a[0] * b[1] - b[0] * a[1]
                   for a, b in zip(polygon, polygon[1:] + polygon[:1]))
        points = polygon if area >= 0 else list(reversed(polygon))
        if len(points) < 3 or area == 0:
            continue
        commands = [f'M {points[0][0]:.12g} {points[0][1]:.12g}']
        commands.extend(f'L {x:.12g} {y:.12g}' for x, y, _depth in points[1:])
        commands.append('Z')
        parts.append(' '.join(commands))
    return ' '.join(parts)


def visible_regions(faces):
    """Yield (SVG path data, color, component) for each semantic fill.

    Visible polygons sharing both component and color are combined into one
    compound path. The subpaths have consistent winding so shared internal
    edges cancel during fill rasterization; visibility geometry is unchanged.
    """
    groups = {}
    for polygon, color, component in visible_fragments(faces):
        groups.setdefault((component, color), []).append(polygon)
    for (component, color), polygons in groups.items():
        path = _compound_path(polygons)
        if path:
            yield path, color, component
