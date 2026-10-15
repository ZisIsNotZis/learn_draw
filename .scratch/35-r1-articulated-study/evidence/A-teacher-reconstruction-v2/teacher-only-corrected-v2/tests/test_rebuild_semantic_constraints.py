import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "rebuild_teacher_evidence.py"
spec = importlib.util.spec_from_file_location("teacher_rebuilder", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_point_set_coordinates_and_withdrawals_are_fixed():
    assert len(module.POINTS) == 24
    lti = next(row for row in module.POINTS if row[0] == "LTI2")
    assert lti[3:6] == (104, 222, "unknown")
    assert "WITHDRAWN" in lti[1] and "No pink interior" in lti[6]
    trace = next(row for row in module.TRACES if row["id"] == "leftward-tail-centerline-visible")
    assert "WITHDRAWN" in trace["status"] and "not source-backed" in trace["status"]
    assert [116, 220] in trace["crop_xy"]


def test_output_guard_allows_only_current_package():
    assert module.validate_output_path(module.DEFAULT_OUT) == module.DEFAULT_OUT.resolve()


def test_output_guard_rejects_historical_and_arbitrary_paths(tmp_path):
    historical = module.ROOT / ".scratch/35-r1-articulated-study/evidence/A-teacher-reconstruction-v2"
    for candidate in (
        historical / "teacher-only",
        historical / "teacher-only" / "raw-patches" / "LTI2.png",
        historical / "teacher-only-corrected",
        tmp_path / "validation-output",
    ):
        try:
            module.validate_output_path(candidate)
        except ValueError:
            pass
        else:
            raise AssertionError(f"accepted forbidden output path: {candidate}")


def test_output_guard_resolves_symlink_alias_to_history(tmp_path):
    historical = module.ROOT / ".scratch/35-r1-articulated-study/evidence/A-teacher-reconstruction-v2/teacher-only"
    alias = tmp_path / "historical-alias"
    alias.symlink_to(historical, target_is_directory=True)
    try:
        module.validate_output_path(alias)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted symlink to historical package")


def test_limited_unknown_roles_remain_explicit():
    tbe = next(row for row in module.POINTS if row[0] == "TBE2")
    dto = next(row for row in module.POINTS if row[0] == "DTO2")
    assert tbe[3:6] == (86, 231, "boundary-neighborhood")
    assert "not an endpoint" not in tbe[6] and "continuation at LTA2 is unknown" in tbe[6]
    assert dto[5] == "unknown"
    assert "UNKNOWN" in dto[6]
