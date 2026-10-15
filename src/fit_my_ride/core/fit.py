"""Fit judgment: one evaluator per Core Parameter, `unknown` when none is registered."""

from collections.abc import Callable
from enum import Enum

from fit_my_ride.core.schema import RiderInput, Tier, parameter


class Unknown(Enum):
    """No evaluator exists for the parameter; never excludes, never gets a colour."""

    UNKNOWN = "unknown"


UNKNOWN = Unknown.UNKNOWN

# (rider, value in the parameter's unit) -> signed deviation from the ideal range:
# 0 in range, negative too short, positive too long.
Evaluator = Callable[[RiderInput, float], float]


class EvaluatorRegistry:
    """One evaluator slot per Core Parameter; slots are independent of each other."""

    def __init__(self) -> None:
        self._evaluators: dict[str, Evaluator] = {}

    def register(self, code: str, evaluator: Evaluator) -> None:
        """Set (or replace) the evaluator for one Core Parameter."""
        self._core(code)
        self._evaluators[code] = evaluator

    def evaluate(self, code: str, rider: RiderInput, value: float) -> float | Unknown:
        """Signed deviation from the ideal range, or `UNKNOWN` without an evaluator."""
        self._core(code)
        evaluator = self._evaluators.get(code)
        if evaluator is None:
            return UNKNOWN
        return evaluator(rider, value)

    @staticmethod
    def _core(code: str) -> None:
        if parameter(code).tier is not Tier.CORE:
            raise ValueError(f"{code} is not a Core Parameter; only Core Parameters are evaluated")
