"""Unit conversion: the only place values change unit."""

from decimal import ROUND_HALF_UP, Decimal

_CM_PER_UNIT = {
    "mm": Decimal("0.1"),
    "cm": Decimal(1),
    "in": Decimal("2.54"),
}


class UnknownUnitError(ValueError):
    """Raised when a unit is not one of the supported length units."""

    def __init__(self, unit: str):
        super().__init__(f"unknown unit {unit!r}; expected one of {sorted(_CM_PER_UNIT)}")
        self.unit = unit


def to_cm(value: float, unit: str) -> float:
    """Convert a length to cm, rounded half-up to 0.1."""
    try:
        factor = _CM_PER_UNIT[unit]
    except KeyError:
        raise UnknownUnitError(unit) from None
    cm = Decimal(str(value)) * factor
    return float(cm.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
