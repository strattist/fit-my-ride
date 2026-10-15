from dataclasses import FrozenInstanceError

import pytest

from fit_my_ride.core.schema import InvalidRiderInputError, RiderInput, Style


def test_valid_rider_input():
    rider = RiderInput(height_cm=178, inseam_cm=82, style=Style.ROAD)
    assert (rider.height_cm, rider.inseam_cm, rider.style) == (178, 82, Style.ROAD)


@pytest.mark.parametrize("height", [119.9, 230.1])
def test_height_outside_range_names_the_range(height):
    with pytest.raises(InvalidRiderInputError, match=r"120.*230"):
        RiderInput(height_cm=height, inseam_cm=82, style=Style.ROAD)


@pytest.mark.parametrize("inseam", [49.9, 120.1])
def test_inseam_outside_range_names_the_range(inseam):
    with pytest.raises(InvalidRiderInputError, match=r"50.*120"):
        RiderInput(height_cm=178, inseam_cm=inseam, style=Style.ROAD)


def test_range_edges_are_accepted():
    RiderInput(height_cm=120, inseam_cm=50, style=Style.GRAVEL)
    RiderInput(height_cm=230, inseam_cm=120, style=Style.GRAVEL)


def test_style_is_the_usage_taxonomy():
    assert [s.value for s in Style] == [
        "road",
        "gravel",
        "mtb",
        "city_commute",
        "touring",
        "e_bike",
    ]


def test_unknown_style_raises_typed_error():
    with pytest.raises(InvalidRiderInputError, match="style"):
        RiderInput(height_cm=178, inseam_cm=82, style="unicycle")


def test_style_accepts_taxonomy_value_string():
    assert RiderInput(178, 82, "gravel").style is Style.GRAVEL


@pytest.mark.parametrize("bad", ["178", None, True])
def test_non_numeric_measurement_raises_typed_error(bad):
    with pytest.raises(InvalidRiderInputError, match="height_cm.*number"):
        RiderInput(height_cm=bad, inseam_cm=82, style=Style.ROAD)
    with pytest.raises(InvalidRiderInputError, match="inseam_cm.*number"):
        RiderInput(height_cm=178, inseam_cm=bad, style=Style.ROAD)


def test_rider_input_is_immutable_and_hashable():
    rider = RiderInput(178, 82, Style.ROAD)
    with pytest.raises(FrozenInstanceError):
        rider.height_cm = 180
    assert hash(rider) == hash(RiderInput(178, 82, "road"))
