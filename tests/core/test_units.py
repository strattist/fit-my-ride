import pytest

from fit_my_ride.core.units import UnknownUnitError, to_cm


@pytest.mark.parametrize(
    ("value", "unit", "expected"),
    [(1234, "mm", 123.4), (28, "in", 71.1), (57.46, "cm", 57.5), (57.45, "cm", 57.5)],
)
def test_converts_to_cm_with_one_decimal(value, unit, expected):
    assert to_cm(value, unit) == expected


def test_unknown_unit_raises_naming_the_unit():
    with pytest.raises(UnknownUnitError, match="furlong"):
        to_cm(5, "furlong")
