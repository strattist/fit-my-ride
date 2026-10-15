import pytest

from fit_my_ride.core.fit import (
    UNKNOWN,
    EvaluatorRegistry,
    InvalidEvaluationError,
    NotCoreParameterError,
)
from fit_my_ride.core.schema import (
    CORE_PARAMETERS,
    ParameterValue,
    RiderInput,
    Style,
    UnknownParameterError,
)

RIDER = RiderInput(height_cm=178, inseam_cm=82, style=Style.ROAD)


def band(low, high):
    """Stand-in evaluator: signed distance to the nearest edge of [low, high]."""

    def evaluate(rider, value):
        if value < low:
            return value - low
        if value > high:
            return value - high
        return 0.0

    return evaluate


@pytest.mark.parametrize("code", [p.code for p in CORE_PARAMETERS])
def test_core_parameter_without_evaluator_is_unknown(code):
    assert EvaluatorRegistry().evaluate(code, RIDER, 50.0) is UNKNOWN


def test_registered_evaluator_returns_signed_deviation():
    registry = EvaluatorRegistry()
    registry.register("S", band(50.0, 56.0))
    assert registry.evaluate("S", RIDER, 53.0) == 0
    assert registry.evaluate("S", RIDER, 48.5) == -1.5
    assert registry.evaluate("S", RIDER, 58.0) == 2.0


def test_evaluator_receives_the_rider():
    registry = EvaluatorRegistry()
    registry.register("S", lambda rider, value: value - rider.height_cm)
    assert registry.evaluate("S", RIDER, 180.0) == 2.0


def test_replacing_one_evaluator_changes_no_other_parameter():
    registry = EvaluatorRegistry()
    registry.register("S", band(50.0, 56.0))
    registry.register("R", band(38.0, 40.0))
    before = {c: registry.evaluate(c, RIDER, 45.0) for c in ("S", "R", "HTA", "STA", "BB")}

    registry.register("S", band(40.0, 44.0))
    after = {c: registry.evaluate(c, RIDER, 45.0) for c in ("S", "R", "HTA", "STA", "BB")}

    assert before["S"] == -5.0
    assert after["S"] == 1.0
    assert {c: v for c, v in after.items() if c != "S"} == {
        c: v for c, v in before.items() if c != "S"
    }


def test_unknown_parameter_code_raises():
    with pytest.raises(UnknownParameterError):
        EvaluatorRegistry().evaluate("XX", RIDER, 1.0)
    with pytest.raises(UnknownParameterError):
        EvaluatorRegistry().register("XX", band(0, 1))


def test_optional_parameter_cannot_have_an_evaluator():
    with pytest.raises(NotCoreParameterError, match="Core"):
        EvaluatorRegistry().register("ST", band(0, 1))
    with pytest.raises(NotCoreParameterError, match="Core"):
        EvaluatorRegistry().evaluate("ST", RIDER, 1.0)


def test_unknown_is_not_a_number():
    assert not isinstance(UNKNOWN, (int, float))


def test_missing_value_is_unknown_even_with_an_evaluator():
    registry = EvaluatorRegistry()
    registry.register("S", band(50.0, 56.0))
    assert registry.evaluate("S", RIDER, None) is UNKNOWN
    assert registry.evaluate("S", RIDER, ParameterValue(None, "not reported")) is UNKNOWN


def test_parameter_value_is_unwrapped():
    registry = EvaluatorRegistry()
    registry.register("S", band(50.0, 56.0))
    assert registry.evaluate("S", RIDER, ParameterValue(58.0)) == 2.0


def test_evaluator_may_return_unknown():
    registry = EvaluatorRegistry()
    registry.register("S", lambda rider, value: UNKNOWN)
    assert registry.evaluate("S", RIDER, 53.0) is UNKNOWN


@pytest.mark.parametrize("bad", [None, float("nan"), float("inf"), "0", True])
def test_evaluator_result_must_be_unknown_or_a_finite_number(bad):
    registry = EvaluatorRegistry()
    registry.register("S", lambda rider, value: bad)
    with pytest.raises(InvalidEvaluationError, match="S"):
        registry.evaluate("S", RIDER, 53.0)


def test_registering_a_non_callable_raises():
    with pytest.raises(TypeError):
        EvaluatorRegistry().register("S", 5)


def test_evaluator_errors_propagate():
    registry = EvaluatorRegistry()

    def broken(rider, value):
        raise ZeroDivisionError

    registry.register("S", broken)
    with pytest.raises(ZeroDivisionError):
        registry.evaluate("S", RIDER, 53.0)
