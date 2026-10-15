"""Stack and Reach rules, with values from docs/fit-rules.md (rider height 175 cm)."""

import pytest

from fit_my_ride.core.fit import UNKNOWN, EvaluatorRegistry
from fit_my_ride.core.fit_rules import register_stack_reach
from fit_my_ride.core.schema import RiderInput, Style


def rider(style=Style.ROAD, height=175, inseam=80):
    return RiderInput(height_cm=height, inseam_cm=inseam, style=style)


@pytest.fixture
def registry():
    reg = EvaluatorRegistry()
    register_stack_reach(reg)
    return reg


# Road, h = 175: stack range 54.75-57.75, reach range 36.625-39.625 (worked example).
@pytest.mark.parametrize(
    ("code", "value", "expected"),
    [
        ("S", 56.0, 0),  # inside
        ("S", 54.75, 0),  # lower edge
        ("S", 57.75, 0),  # upper edge
        ("S", 54.0, -0.75),  # below
        ("S", 59.0, 1.25),  # above
        ("R", 38.0, 0),
        ("R", 36.625, 0),
        ("R", 39.625, 0),
        ("R", 36.0, -0.625),
        ("R", 40.0, 0.375),
    ],
)
def test_road_deviation_from_the_documented_range(registry, code, value, expected):
    assert registry.evaluate(code, rider(), value) == pytest.approx(expected)


# (style, stack offset, reach offset) from the style table in docs/fit-rules.md.
OFFSETS = [
    (Style.ROAD, 0.0, 0.0),
    (Style.GRAVEL, 1.0, -0.5),
    (Style.MTB, 0.5, 1.5),
    (Style.CITY_COMMUTE, 3.0, -2.0),
    (Style.TOURING, 2.0, -1.0),
    (Style.E_BIKE, 3.0, -2.0),
]


@pytest.mark.parametrize(("style", "s_off", "r_off"), OFFSETS)
def test_style_shifts_the_range(registry, style, s_off, r_off):
    r = rider(style)
    # Edges of the road range moved by the style offset.
    assert registry.evaluate("S", r, 54.75 + s_off) == pytest.approx(0)
    assert registry.evaluate("S", r, 57.75 + s_off) == pytest.approx(0)
    assert registry.evaluate("S", r, 54.75 + s_off - 1) == pytest.approx(-1)
    assert registry.evaluate("S", r, 57.75 + s_off + 1) == pytest.approx(1)
    assert registry.evaluate("R", r, 36.625 + r_off) == pytest.approx(0)
    assert registry.evaluate("R", r, 39.625 + r_off) == pytest.approx(0)
    assert registry.evaluate("R", r, 36.625 + r_off - 1) == pytest.approx(-1)
    assert registry.evaluate("R", r, 39.625 + r_off + 1) == pytest.approx(1)


def test_range_follows_height(registry):
    # h = 190: stack centre 0.31*190+2.0 = 60.9; reach centre 0.215*190+0.5 = 41.35.
    r = rider(height=190)
    assert registry.evaluate("S", r, 60.9) == 0
    assert registry.evaluate("S", r, 62.4) == pytest.approx(0)
    assert registry.evaluate("S", r, 63.4) == pytest.approx(1.0)
    assert registry.evaluate("R", r, 41.35) == 0
    assert registry.evaluate("R", r, 39.85) == pytest.approx(0)
    assert registry.evaluate("R", r, 38.85) == pytest.approx(-1.0)


def test_inseam_is_not_used(registry):
    assert registry.evaluate("S", rider(inseam=50), 59.0) == registry.evaluate(
        "S", rider(inseam=120), 59.0
    )


def test_other_core_parameters_stay_unknown(registry):
    for code in ("HTA", "STA", "BB"):
        assert registry.evaluate(code, rider(), 70.0) is UNKNOWN


def test_missing_value_is_unknown(registry):
    assert registry.evaluate("S", rider(), None) is UNKNOWN
