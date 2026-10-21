# B-hand-study-v2-rimwrap — one digit crosses the near rim (crossing floor MET, suite 28/28, ART VERDICT PENDING)

A copy of `../B-hand-study-v1-r1/` (which stays untouched, and which the archived verdict is
bound to by hash) carrying the one bounded experiment cut in
[`../../work/r1a-method-hypothesis.md`](../../work/r1a-method-hypothesis.md) § 4 and authorised
by root's `inbox/2026-10-21-rimwrap-contract.md`: **the joint's order, not the object's
precision, is what the four image verdicts were failing at.**

## The result

- The wrapped digit (**the ring finger**, station 288°) passes *above* the dish's rim band and
  its pad lands on the **pressed surface past the rim's inner corner**, so its fill lies inside
  the dish's projected outline while the other four digits and the palm stay behind the plate.
  The joint therefore has **mixed order**: one piece in front, the rest behind.
- **`cross_px` 3527 against a floor of 2175** — 1.62 % of the dish's projected outline
  (217 540 px), on the delivered 1:1 PNG, measured against the dish's outline **from its own
  geometry**, not its visible outline. **`contour_breaks` 0** of 6 rear-contour points inside
  the crossing: the dish's rim contour terminates on the digit, and the digit's contour runs
  unbroken. Both numbers are line 1 of `check/report.txt`.
- **Suite 28/28 green**, of which the audit's own negative control is
  `tests/test_joint_audit.py::test_the_audit_zeroes_on_the_r1_route`: put the same digit back on
  v1-r1's underside route (same station, same radii, only the contact surface changed) and
  `cross_px` falls below the floor. A green number therefore counts the crossing and not merely
  some pixels. Rebuild is byte-identical; the manifest verifies; the delivered PNG is a fresh
  render of the delivered SVG through `scripts/draw render`.

## What changed, and what did not

| | |
| --- | --- |
| `dish.derived_rings` | adds the **bowl** rings (two rows between the rim's inner corner and the floor): the surface a digit presses has to be derived the same way the underside is. No tessellation change. |
| `contact.pressed_ring` | the pressed surface as a blend of the mesh's own rings: 0→1 across the rim's top band (outer→inner corner), past 1 onto the bowl's interior. |
| `contact.wrap_finger` | the front piece: root → a knot above the band → the pad's two knots on the pressed surface, each one tip radius plus the stated clearance off it, with v1-r1's `PAD_RUN` knot so the last cross-section is framed by the pad. |
| `scene.WRAP` | the pose of the one changed digit (`name="ring"`, `land=(0.80, 1.20)`, `over=0.12`). Dish, palette, framing, palm and the other four digits are unchanged. |
| `source/joint_audit.py` | the two pixel measurements, on the delivered PNG, with no image library in `source/` (polygon raster by ray crossing, so the drawing source stays drawing). |
| `tests/` | `test_joint_audit.py` (the criterion + its control); the underside contact test now exempts the wrapped digit and a new test measures it against the surface it presses. Nothing was weakened: every digit still has a contact test, and the mutation that lifts the hand 20 px still fails. |

## What is not claimed

No art verdict. Whether flesh over the rim **reads as holding the dish** is a fresh
image-only reviewer's question, and the picture goes to one; R1a's exit stays the person's
judgement of a picture. The four remaining v1-r1 findings (blockers on the well's tessellation
and the digit silhouette) are untouched, by scope.

## Reproduce

```
python source/build.py                     # -> artwork.svg
scripts/draw check artwork.svg --outdir $PWD/check
python source/joint_audit.py $PWD/check/draft-fullres.png artwork.svg --report   # line 1
python -m unittest discover -s tests -q    # 28 tests
```
