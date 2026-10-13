import pytest

from fit_my_ride.core.schema import PARAMETERS, ParameterValue, complete_geometry


def test_present_value_has_no_reason():
    v = ParameterValue(54.2)
    assert v.value == 54.2
    assert v.reason is None


def test_missing_value_is_null_plus_reason():
    v = ParameterValue(None, "not in vendor table")
    assert v.value is None
    assert v.reason == "not in vendor table"


def test_missing_value_without_reason_raises():
    with pytest.raises(ValueError):
        ParameterValue(None)
    with pytest.raises(ValueError):
        ParameterValue(None, "  ")


def test_partial_geometry_is_completed_with_null_and_reason():
    geometry = complete_geometry({"S": ParameterValue(55.0), "R": ParameterValue(38.5)})
    assert list(geometry) == [p.code for p in PARAMETERS]
    assert geometry["S"].value == 55.0
    assert geometry["BB"].value is None
    assert geometry["BB"].reason == "not reported"
    assert all(v.value is None or v.reason is None for v in geometry.values())


def test_unknown_code_raises():
    with pytest.raises(KeyError):
        complete_geometry({"XX": ParameterValue(1.0)})


def test_present_value_with_reason_raises():
    with pytest.raises(ValueError):
        ParameterValue(54.2, "oops")
