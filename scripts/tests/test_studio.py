"""Discriminate useful local edits, unsafe revision changes and real depth order.

These are operation/geometry checks. Visual quality is reviewed on rendered images.
"""
import copy
import tempfile
import unittest
from pathlib import Path

from scripts.studio.__main__ import default_scene
from scripts.studio.geometry import geometry_issues, lock_rows, window
from scripts.studio.model import accept, fingerprint, preview, read, select, undo, validate, write
from scripts.studio.render import drawing, faces_for
from scripts.vector_visibility import visible_fragments


class LocalEditing(unittest.TestCase):
    def setUp(self):
        self.scene = default_scene()
        other = copy.deepcopy(self.scene["nodes"][0])
        other.update(id="protected-lock", at={"anchor": "upper_right"}, sweep=-.4)
        self.scene["nodes"].append(other)
        self.selection = select(self.scene, "cheek-lock", radius=.2)

    def test_push_lands_on_selected_edge_and_preserves_everything_else(self):
        before = lock_rows(self.scene["nodes"][0], self.scene["canvas"])
        candidate = preview(self.scene, self.selection, "right", .18, "tuck the inner edge toward the body of the lock")
        after = lock_rows(candidate["scene"]["nodes"][0], self.scene["canvas"])
        self.assertEqual(self.scene["nodes"][1], candidate["scene"]["nodes"][1])
        self.assertNotEqual(before[22].left, after[22].left)
        self.assertGreater(after[22].left[0], before[22].left[0])
        for a, b in zip(before, after):
            self.assertEqual(a.right, b.right)
            if abs(a.t - .55) >= .2:
                self.assertEqual(a.left, b.left)
        self.assertEqual(before[0], after[0])
        self.assertEqual(before[-1], after[-1])
        self.assertNotIn("edits", self.scene["nodes"][0], "preview must not mutate the live scene")

    def test_reversal_can_recover_the_same_boundary(self):
        a = preview(self.scene, self.selection, "right", .18, "tuck middle")
        selection = select(a["scene"], "cheek-lock", radius=.2)
        b = preview(a["scene"], selection, "left", .18, "the middle was tucked too far")
        old = lock_rows(self.scene["nodes"][0], self.scene["canvas"])
        new = lock_rows(b["scene"]["nodes"][0], self.scene["canvas"])
        for x, y in zip(old, new):
            for p, q in zip(x.left, y.left):
                self.assertAlmostEqual(p, q, places=10)

    def test_invalid_push_is_refused_instead_of_drawing_a_crossed_lock(self):
        with self.assertRaisesRegex(ValueError, "crossed|intersection"):
            preview(self.scene, self.selection, "right", 2, "test deliberately collapsing the width")

    def test_selection_cannot_move_a_locked_terminal(self):
        with self.assertRaisesRegex(ValueError, "root/tip"):
            select(self.scene, "cheek-lock", at=.1, radius=.2)

    def test_stale_selection_is_refused(self):
        self.scene["nodes"][0]["angle"] = 20
        with self.assertRaisesRegex(ValueError, "stale selection"):
            preview(self.scene, self.selection, "left", .1, "change")

    def test_implementation_changes_invalidate_alignment_and_preview(self):
        selection = self.selection | {"engine": "old-implementation"}
        with self.assertRaisesRegex(ValueError, "implementation changed"):
            preview(self.scene, selection, "left", .1, "change")
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "working.json"
            write(p, self.scene)
            candidate = preview(self.scene, self.selection, "right", .1, "tuck middle")
            candidate["engine"] = "old-implementation"
            with self.assertRaisesRegex(ValueError, "implementation changed"):
                accept(p, candidate)

    def test_accept_undo_and_stale_preview(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "working.json"
            write(p, self.scene)
            before_bytes = p.read_bytes()
            a = preview(self.scene, self.selection, "right", .12, "soften the inner arc")
            accept(p, a)
            self.assertEqual(fingerprint(read(p)), a["result"])
            with self.assertRaisesRegex(ValueError, "stale preview"):
                accept(p, a)
            undo(p)
            self.assertEqual(p.read_bytes(), before_bytes)

    def test_external_change_prevents_undo(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "working.json"
            write(p, self.scene)
            a = preview(self.scene, self.selection, "right", .12, "soften inner arc")
            accept(p, a)
            changed = read(p)
            changed["background"] = "#ffffff"
            write(p, changed)
            with self.assertRaisesRegex(ValueError, "outside edit history"):
                undo(p)

    def test_unknown_fields_and_nonfinite_values_are_errors(self):
        for key, val in (("typo_width", .3), ("width", float("nan"))):
            scene = copy.deepcopy(self.scene)
            scene["nodes"][0][key] = val
            with self.assertRaises(ValueError):
                validate(scene)

    def test_presets_have_simple_uncrossed_contours_across_supported_gestures(self):
        for angle in (-150, -30, 0, 70, 180):
            for sweep in (-.25, 0, .25):
                node = copy.deepcopy(self.scene["nodes"][0])
                node.update(angle=angle, sweep=sweep)
                self.assertEqual(geometry_issues(lock_rows(node, self.scene["canvas"])), [])

    def test_one_sided_width_keeps_the_protected_edge_in_place(self):
        node = copy.deepcopy(self.scene["nodes"][0])
        node.update(width_side="right", width=.12)
        node["width"] = .24
        node["sweep"] = .16
        a = lock_rows(node | {"width": .12}, self.scene["canvas"])
        b = lock_rows(node, self.scene["canvas"])
        self.assertEqual([r.left for r in a], [r.left for r in b])
        self.assertNotEqual([r.right for r in a], [r.right for r in b])

    def test_one_sided_root_caps_are_valid_rings(self):
        from shapely import Polygon
        from scripts.studio.geometry import outline
        for side in ('left','right','both'):
            for angle in (-100,-8,8,100):
                node = self.scene['nodes'][0] | dict(width_side=side, angle=angle, width=.20, sweep=.025)
                self.assertTrue(Polygon(outline(lock_rows(node, self.scene['canvas']))).is_valid,
                                (side,angle))

    def test_overlay_and_art_are_distinct(self):
        self.assertNotIn('id="selected-edge"', drawing(self.scene))
        self.assertIn('id="selected-edge"', drawing(self.scene, self.selection))
        self.assertEqual(drawing(self.scene), drawing(copy.deepcopy(self.scene)))


def inside(point, polygon):
    x, y = point
    result = False
    for a, b in zip(polygon, polygon[1:] + polygon[:1]):
        if (a[1] > y) != (b[1] > y) and x < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1]) + a[0]:
            result = not result
    return result


class DepthAuthority(unittest.TestCase):
    def test_crossing_depth_changes_visible_owner_without_author_cuts(self):
        # A rising plane changes front order halfway down two identical footprints.
        # Swapping node declaration order must not change the winner.
        scene = default_scene()
        scene["nodes"][0].update(id="sloping", depth=-.5, depth_slope=1)
        flat = copy.deepcopy(scene["nodes"][0])
        flat.update(id="flat", depth=0, depth_slope=0)
        scene["nodes"].append(flat)
        rows = lock_rows(flat, scene["canvas"])
        for t, expected in ((.25, "flat"), (.75, "sloping")):
            r = min(rows, key=lambda r: abs(r.t - t))
            point = tuple((a + b) / 2 for a, b in zip(r.left, r.right))
            for order in (scene["nodes"], list(reversed(scene["nodes"]))):
                trial = scene | {"nodes": order}
                winners = {name for poly, _color, name in visible_fragments(faces_for(trial)) if inside(point, poly)}
                self.assertEqual(winners, {expected})


if __name__ == "__main__":
    unittest.main()
