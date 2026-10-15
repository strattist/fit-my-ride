"""Stack and Reach fit rules, implementing exactly `docs/fit-rules.md`.

Centre of the ideal range is the BikeSize height formula plus a per-style offset; the range
is centre +/- TOLERANCE_CM. Inseam is deliberately not used. Deviations are in cm.
"""

from fit_my_ride.core.fit import Evaluator, EvaluatorRegistry
from fit_my_ride.core.schema import RiderInput, Style

TOLERANCE_CM = 1.5

# (stack offset, reach offset) in cm, from the style table in docs/fit-rules.md.
STYLE_OFFSETS_CM: dict[Style, tuple[float, float]] = {
    Style.ROAD: (0.0, 0.0),
    Style.GRAVEL: (1.0, -0.5),
    Style.MTB: (0.5, 1.5),
    Style.CITY_COMMUTE: (3.0, -2.0),
    Style.TOURING: (2.0, -1.0),
    Style.E_BIKE: (3.0, -2.0),
}


def _distance_to_range(value: float, centre: float) -> float:
    # Rounded so float noise at the range edges cannot turn "on the edge" into a deviation.
    low = round(centre - TOLERANCE_CM, 6)
    high = round(centre + TOLERANCE_CM, 6)
    if value < low:
        return round(value - low, 6)
    if value > high:
        return round(value - high, 6)
    return 0.0


def stack_deviation(rider: RiderInput, value: float) -> float:
    """Signed distance (cm) of a stack value from the rider's ideal range."""
    centre = 0.31 * rider.height_cm + 2.0 + STYLE_OFFSETS_CM[rider.style][0]
    return _distance_to_range(value, centre)


def reach_deviation(rider: RiderInput, value: float) -> float:
    """Signed distance (cm) of a reach value from the rider's ideal range."""
    centre = 0.215 * rider.height_cm + 0.5 + STYLE_OFFSETS_CM[rider.style][1]
    return _distance_to_range(value, centre)


def register_stack_reach(registry: EvaluatorRegistry) -> None:
    """Install the S and R evaluators; the other Core Parameters are untouched."""
    evaluators: dict[str, Evaluator] = {"S": stack_deviation, "R": reach_deviation}
    for code, evaluator in evaluators.items():
        registry.register(code, evaluator)
