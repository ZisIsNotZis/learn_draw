"""The hand's construction claims, each measured on the emitted geometry.

Six claims, and where each one comes from:

  * the scene is one palm, four fingers and a thumb, and every closed patch is wound outwards;
  * the digits are merged at their roots and separated at their distal halves, as fractions of a
    digit's own width - the merge is stated here, not hidden;
  * every digit tapers toward its tip;
  * every digit's tip rests on the dish's **underside**, one digit-radius plus one clearance
    below it, and nothing of the hand penetrates it; the surface is re-derived here from the
    mesh (`dish.derived_rings` -> `contact.underside_ring`) rather than read from the producer,
    and the hand follows the dish when the underside's own size constants change;
  * the dish has a rim with thickness, an inner wall and an underside;
  * no stroke in the drawing is a drawn-on line: every stroke is either a computed contour or a
    computed fold, and the digits carry no folds at all.
"""
from __future__ import annotations

import os
import sys
import unittest

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import util  # noqa: E402

import dish  # noqa: E402
import geo  # noqa: E402
import scene  # noqa: E402

FINGERS = ("index", "middle", "ring", "little")


class TestParts(unittest.TestCase):
    def test_one_palm_four_fingers_and_a_thumb(self):
        parts, _rings = util.parts()
        self.assertEqual(sorted(parts), sorted(("palm", "dish") + util.DIGITS))
        print(f"  parts: {', '.join(sorted(parts))}")

    def test_every_closed_patch_is_wound_outwards(self):
        """A patch wound inside-out would be drawn from behind; half its faces must face us."""
        parts, _rings = util.parts()
        for name, patch in parts.items():
            frac = patch.front_fraction()
            print(f"  {name:8s} front-facing {frac:.2f}")
            self.assertGreater(frac, 0.30, f"{name} has too few front-facing quads")
            self.assertLess(frac, 0.70, f"{name} has too many: it is probably wound inside out")


class TestDigitsTaper(unittest.TestCase):
    def test_every_digit_tapers_toward_its_tip(self):
        parts, _rings = util.parts()
        for name in util.DIGITS:
            patch = parts[name]
            base = util.width_at(patch, int(0.15 * (patch.ni - 1)))
            tip = util.width_at(patch, int(0.90 * (patch.ni - 1)))
            print(f"  {name:8s} width {base:5.1f} -> {tip:5.1f}  ratio {tip / base:.2f}")
            self.assertLessEqual(tip, 0.75 * base, f"{name} does not taper")


class TestSeparation(unittest.TestCase):
    """The contract's separation report: at the roots, and at the distal halves."""

    ROOT_T = 0.15
    DISTAL_T = 0.60
    ROOT_LIMIT = 0.10      # at or below this fraction of a digit's width the digits are merged
    DISTAL_FLOOR = 0.30    # at or above this they read as separate digits

    def _ratios(self, parts, t):
        out = {}
        for a, b in zip(FINGERS, FINGERS[1:]):
            pa, pb = parts[a], parts[b]
            ia = int(round(t * (pa.ni - 1)))
            ib = int(round(t * (pb.ni - 1)))
            width = 0.5 * (util.width_at(pa, ia) + util.width_at(pb, ib))
            out[(a, b)] = (util.station_gap(pa, ia, pb, ib), width)
        return out

    def test_the_roots_are_merged(self):
        parts, _rings = util.parts()
        for pair, (gap, width) in self._ratios(parts, self.ROOT_T).items():
            print(f"  roots {pair[0]:6s}-{pair[1]:6s} gap {gap:5.1f} / width {width:5.1f}"
                  f" = {gap / width:.2f}")
            self.assertLessEqual(gap / width, self.ROOT_LIMIT,
                                 f"{pair} reads as two separate roots at the knuckles")

    def test_the_distal_halves_are_separated(self):
        parts, _rings = util.parts()
        for pair, (gap, width) in self._ratios(parts, self.DISTAL_T).items():
            print(f"  distal {pair[0]:6s}-{pair[1]:6s} gap {gap:5.1f} / width {width:5.1f}"
                  f" = {gap / width:.2f}")
            self.assertGreaterEqual(gap / width, self.DISTAL_FLOOR,
                                    f"{pair} reads as one mass at the distal half")

    def test_the_separation_check_bites(self):
        """Mutation: put two fingers over the same rim station and the distal floor must fail."""
        saved = scene.FINGERS
        try:
            mutated = list(saved)
            name, root_off, _station, reach, radii = mutated[1]
            mutated[1] = (name, root_off, saved[0][2] + 1.0, reach, radii)   # sit on the index
            scene.FINGERS = tuple(mutated)
            parts, _rings = util.parts()
            ratios = self._ratios(parts, self.DISTAL_T)
        finally:
            scene.FINGERS = saved
        worst = min(ratios[(a, b)][0] / ratios[(a, b)][1] for (a, b) in ratios
                    if a == "middle" or b == "middle")
        print(f"  mutation (middle over the index): tightest ratio {worst:.2f}, "
              f"floor {self.DISTAL_FLOOR}")
        self.assertLess(worst, self.DISTAL_FLOOR,
                        "the separation check did not notice two fingers on one station")


class TestContact(unittest.TestCase):
    """Contact is a distance from the dish's own underside, re-derived here, not a claim.

    Re-targeted per resolution R1 of wave 14: the hand is under the plate by the owner's
    direction, so the rim band's top plane is no longer a contact surface and the law is
    measured against the surface the construction actually touches - the dish's own underside
    ring.  The law is unchanged: a digit's pad rests on the contact surface, does not penetrate
    it, and a digit that lifts off is caught.
    """

    def _band(self):
        parts, _rings = util.parts()
        return util.rim_band(parts["dish"]), parts

    def test_the_band_is_a_rim_with_two_edges(self):
        band, parts = self._band()
        lo, hi = band["radii"]
        axis = dish.build(**scene.DISH_POSE)
        up = geo.rot_x(scene.DISH_POSE["tilt_deg"]) @ np.array([0.0, 0.0, 1.0])
        tilt = float(np.degrees(np.arccos(min(1.0, abs(float(band["normal"] @ up))))))
        print(f"  rim band radii {lo:.1f} .. {hi:.1f} px (thickness {hi - lo:.1f}), "
              f"rows {band['rows']}, band normal {tilt:.1f} deg off the dish's axis")
        self.assertGreater(hi - lo, 20.0, "the rim has no measurable thickness")
        self.assertGreater(lo, 100.0, "the rim's inner edge is not a rim, it is the axis")
        self.assertLess(tilt, 6.0, "the rim's band is not flat: it has no thickness to read")
        self.assertEqual(len(axis.v), len(parts["dish"].v))

    def test_every_digit_rests_on_the_underside_and_none_penetrates_it(self):
        _band, parts = self._band()
        _all, rings = util.parts()
        clearance = scene.FINGER_GEOMETRY["clearance"]
        for name in util.DIGITS:
            heights = util.underside_heights(parts[name], rings, util.reach_of(name),
                                            util.station_of(name))
            print(f"  {name:8s} tip {heights.min():6.2f} .. {heights.max():6.2f} px "
                  f"below the dish's underside")
            self.assertGreater(heights.min(), -1.0, f"{name} penetrates the plate's underside")
            self.assertLess(heights.min(), clearance + 4.0,
                            f"{name} hovers {heights.min():.1f} px below the underside instead "
                            f"of resting on it")

    def test_a_digit_that_lifts_off_the_underside_is_caught(self):
        """Mutation: a hand that hovers 20 px clear of the dish must fail the contact check."""
        _band, parts = self._band()
        saved = scene.FINGER_GEOMETRY
        try:
            scene.FINGER_GEOMETRY = dict(saved, clearance=saved["clearance"] + 20.0)
            lifted, rings_after = util.parts()
            heights = util.underside_heights(lifted["index"], rings_after,
                                             util.reach_of("index"), util.station_of("index"))
        finally:
            scene.FINGER_GEOMETRY = saved
        print(f"  mutation (clearance + 20 px): lowest {heights.min():.2f} px")
        self.assertGreater(heights.min(), scene.FINGER_GEOMETRY["clearance"] + 2.0,
                           "the contact check did not notice the hand leaving the dish")

    def test_the_hand_follows_the_dish(self):
        """Change the underside's own drivers and the hand must move with it, not stay put.

        Two measurements, and neither is the old revision's: the rebuilt hand rests on the
        moved surface (the fingerprint of a derived pose), and a hand *held* at the old pose
        no longer does (the fingerprint of a typed one).  The perturbation has to move the
        surface rather than degrade it: an underside whose normals have vanished measures 0.0
        for every vertex, so `util.underside_surface` raises instead of reporting contact.
        """
        parts_before, rings_before = util.parts()
        before = util.underside_heights(parts_before["index"], rings_before,
                                        util.reach_of("index"), util.station_of("index"))
        saved = (dish.FOOT_RADIUS, dish.AXIS_UNDER_Z)
        try:
            dish.FOOT_RADIUS = saved[0] + 60.0
            dish.AXIS_UNDER_Z = saved[1] + 30.0
            parts_after, rings_after = util.parts()
            tip_before = parts_before["index"].v[-1].mean(axis=0)
            tip_after = parts_after["index"].v[-1].mean(axis=0)
            after = util.underside_heights(parts_after["index"], rings_after,
                                           util.reach_of("index"), util.station_of("index"))
            held = util.underside_heights(parts_before["index"], rings_after,
                                          util.reach_of("index"), util.station_of("index"))
        finally:
            dish.FOOT_RADIUS, dish.AXIS_UNDER_Z = saved
        clearance = scene.FINGER_GEOMETRY["clearance"]
        moved = float(np.linalg.norm(tip_after - tip_before))
        print(f"  dish foot +60 px / underside axis +30 px: the fingertip moved {moved:.1f} px; "
              f"rebuilt hand {after.min():.2f} px from the new underside (was {before.min():.2f}), "
              f"hand held at the old pose {held.min():.2f} px")
        self.assertGreater(moved, 20.0, "the fingertip did not follow the dish: it is authored")
        self.assertGreater(after.min(), -1.0, "the rebuilt hand penetrates the moved underside")
        self.assertLess(after.min(), clearance + 4.0,
                        "after the dish changed the finger stopped resting on it")
        self.assertGreater(held.min(), clearance + 4.0,
                           "a hand held at the old pose still looks like contact: the height "
                           "does not depend on where the dish is")

    def test_the_palm_cap_meets_the_underside(self):
        """The palm's nearest vertex sits one clearance below the underside it is said to meet.

        The claim the README makes - the palm's distal end meets the dish's underside - was
        unmeasured, and a probe put the palm's mass 28 px below the surface it was said to
        touch.  The construction now solves its distal station against the surface, and this
        measures the result with the test's own sampler.
        """
        parts, rings = util.parts()
        heights = util.vertex_heights(parts["palm"], rings)
        clearance = scene.PALM["clearance"]
        print(f"  palm nearest vertex {heights.min():.2f} px from the underside "
              f"(clearance {clearance:.1f})")
        self.assertGreater(heights.min(), -1.0, "the palm penetrates the plate's underside")
        self.assertLess(heights.min(), clearance + 4.0,
                        f"the palm stops {heights.min():.1f} px below the underside it claims "
                        "to meet")


def contact_negative_control_lines():
    """The contact half of the negative-control record: the real build, and the lift mutation.

    Computed from the same two measurements the contact tests make, so the record and the tests
    cannot state different numbers.
    """
    parts, rings = util.parts()
    real = util.underside_heights(parts["index"], rings, util.reach_of("index"),
                                  util.station_of("index"))
    saved = scene.FINGER_GEOMETRY
    try:
        scene.FINGER_GEOMETRY = dict(saved, clearance=saved["clearance"] + 20.0)
        lifted, rings_after = util.parts()
        mut = util.underside_heights(lifted["index"], rings_after, util.reach_of("index"),
                                     util.station_of("index"))
    finally:
        scene.FINGER_GEOMETRY = saved
    base, bound = saved["clearance"], saved["clearance"] + 4.0
    caught = bool(mut.min() >= bound)
    return [
        "contact negative control (R1 re-target): the lift mutation must still fail the contact check",
        "test        : TestContact::test_a_digit_that_lifts_off_the_underside_is_caught",
        f'mutation    : scene.FINGER_GEOMETRY["clearance"] {base:g} -> {base + 20.0:g} px, '
        "everything else held fixed",
        f"real build  : index tip {real.min():.2f} .. {real.max():.2f} px below the dish's "
        "underside (rests)",
        f"mutation    : mutation (clearance + 20 px): lowest {mut.min():.2f} px",
        f"assertion   : heights.min() < clearance + 4.0 = {bound:.1f} px  ->  {mut.min():.2f} is "
        f"{'not ' if caught else ''}less than {bound:.1f}: it {'fails' if caught else 'passes'}",
        ("PASS: the contact check notices a hand that leaves the dish by 20 px" if caught else
         "FAIL: the contact check did not notice the hand leaving the dish"),
    ]


class TestDishStructure(unittest.TestCase):
    def test_a_rim_an_inner_wall_and_an_underside(self):
        parts, rings = util.parts()
        patch = parts["dish"]
        band = util.rim_band(patch)
        inner_row = band["rows"][-1]
        bowl_floor = inner_row + int(np.argmin(patch.v[0, inner_row:, 2]))
        under_row = int(np.argmin(patch.v[0, :band["rows"][0], 2]))
        print(f"  interior rows {inner_row} .. {patch.nj - 1} (bowl floor at row {bowl_floor}, "
              f"{(patch.v[0, inner_row, 2] - patch.v[0, bowl_floor, 2]):.0f} px below the rim), "
              f"underside lowest ring row {under_row}")
        self.assertGreater(patch.nj - 1, inner_row + 3, "there is no inner wall to speak of")
        self.assertLess(patch.v[0, bowl_floor, 2], patch.v[0, inner_row, 2] - 30.0,
                        "the interior is flat: the dish has no inner wall")
        self.assertTrue(0 <= under_row < band["rows"][0],
                        "the underside is not below the rim")


class TestNoDrawnForm(unittest.TestCase):
    """The drawing has two kinds of ink: a computed contour and a computed fold.  No third."""

    def test_strokes_come_from_the_mesh_and_from_nowhere_else(self):
        import build
        seen = []
        saved_sil = geo.Patch.silhouette
        saved_crease = geo.Patch.creases

        def rec_sil(self):
            out = saved_sil(self)
            seen.extend(("silhouette", self.name) for _ in out)
            return out

        def rec_crease(self):
            out = saved_crease(self)
            seen.extend(("crease", self.name) for _ in out)
            return out

        try:
            geo.Patch.silhouette = rec_sil
            geo.Patch.creases = rec_crease
            res = build.resolve()
        finally:
            geo.Patch.silhouette = saved_sil
            geo.Patch.creases = saved_crease
        emitted = [(c["kind"], c["part"]) for c in res["curves"]]
        print(f"  {len(emitted)} emitted ink curves; every one came from the mesh: "
              f"{sorted(set(k for k, _ in emitted))}")
        stray = set(emitted) - set(seen)
        self.assertEqual(stray, set(), "the drawing inks a curve the mesh did not produce")
        self.assertLessEqual(len(emitted), len(seen))
        self.assertEqual({k for k, _ in emitted}, {"silhouette", "crease"})

    def test_the_delivered_svg_inks_only_contours_and_folds(self):
        import re
        text = open(os.path.join(util.EVIDENCE, "artwork.svg")).read()
        classes = set(re.findall(r'<polyline class="([a-z]+)"', text))
        print(f"  stroke classes in the delivered svg: {sorted(classes)}")
        self.assertEqual(classes - {"silhouette", "crease"}, set(),
                         "the drawing inks something that is neither a contour nor a fold")
        self.assertNotIn("url(#", text, "a gradient stands in for shading the mesh computes")


if __name__ == "__main__":
    unittest.main(verbosity=2)
