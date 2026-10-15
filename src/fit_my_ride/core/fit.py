"""Fit judgment: one evaluator per Core Parameter, `unknown` when none is registered."""

import math
from collections.abc import Callable
from enum import Enum

from fit_my_ride.core.schema import ParameterValue, RiderInput, Tier, parameter


class Unknown(Enum):
    """No judgment is possible; never excludes, never gets a colour."""

    UNKNOWN = "unknown"


UNKNOWN = Unknown.UNKNOWN


class NotCoreParameterError(ValueError):
    """Raised when an Optional Parameter is registered or evaluated."""


class InvalidEvaluationError(ValueError):
    """Raised when an evaluator returns neither `UNKNOWN` nor a finite number."""


# (rider, value in the parameter's unit: deg for HTA/STA, cm otherwise) -> signed deviation
# from the ideal range in that same unit (0 in range, negative too short, positive too
# long), or UNKNOWN when the rider/value cannot be judged.
Evaluator = Callable[[RiderInput, float], float | Unknown]


class EvaluatorRegistry:
    """One evaluator slot per Core Parameter; slots are independent of each other.

    Exceptions raised by an evaluator propagate; the registry does not swallow them.
    """

    def __init__(self) -> None:
        self._evaluators: dict[str, Evaluator] = {}

    def register(self, code: str, evaluator: Evaluator) -> None:
        """Set (or replace) the evaluator for one Core Parameter."""
        self._core(code)
        if not callable(evaluator):
            raise TypeError(f"evaluator for {code} must be callable")
        self._evaluators[code] = evaluator

    def evaluate(
        self, code: str, rider: RiderInput, value: float | ParameterValue | None
    ) -> float | Unknown:
        """Signed deviation from the ideal range, or `UNKNOWN`.

        `UNKNOWN` when no evaluator is registered or the value is missing.
        """
        self._core(code)
        if isinstance(value, ParameterValue):
            value = value.value
        evaluator = self._evaluators.get(code)
        if evaluator is None or value is None:
            return UNKNOWN
        result = evaluator(rider, value)
        if result is UNKNOWN:
            return UNKNOWN
        if (
            isinstance(result, bool)
            or not isinstance(result, int | float)
            or not math.isfinite(result)
        ):
            raise InvalidEvaluationError(
                f"evaluator for {code} returned {result!r}; expected UNKNOWN or a finite number"
            )
        return result

    @staticmethod
    def _core(code: str) -> None:
        if parameter(code).tier is not Tier.CORE:
            raise NotCoreParameterError(
                f"{code} is not a Core Parameter; only Core Parameters are evaluated"
            )
