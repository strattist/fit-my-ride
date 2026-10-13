import pytest

from fit_my_ride.core.schema import (
    CORE_PARAMETERS,
    OPTIONAL_PARAMETERS,
    PARAMETERS,
    Tier,
    parameter,
    parameter_by_name,
)


def test_five_core_and_seven_optional_parameters():
    assert len(PARAMETERS) == 12
    assert [p.code for p in CORE_PARAMETERS] == ["HTA", "STA", "BB", "S", "R"]
    assert len(OPTIONAL_PARAMETERS) == 7
    assert all(p.tier is Tier.CORE for p in CORE_PARAMETERS)
    assert all(p.tier is Tier.OPTIONAL for p in OPTIONAL_PARAMETERS)


def test_canonical_order():
    assert [p.code for p in PARAMETERS] == ("ST HT TT HTA STA CS FL FR BB S R E".split())


def test_units():
    core = {p.code: p.unit for p in CORE_PARAMETERS}
    assert core == {"HTA": "deg", "STA": "deg", "BB": "cm", "S": "cm", "R": "cm"}
    assert all(p.unit == "cm" for p in OPTIONAL_PARAMETERS)


def test_code_to_name():
    hta = parameter("HTA")
    assert hta.name == "Head Tube Angle"
    assert hta.unit == "deg"


def test_name_to_code():
    assert parameter_by_name("Bottom Bracket Drop").code == "BB"
    assert parameter_by_name("Bottom Bracket Drop") is parameter("BB")


def test_unknown_code_and_name_raise():
    with pytest.raises(KeyError):
        parameter("XX")
    with pytest.raises(KeyError):
        parameter_by_name("Nonsense")


def test_unknown_lookups_raise_typed_error():
    from fit_my_ride.core.schema import UnknownParameterError

    with pytest.raises(UnknownParameterError, match="XX"):
        parameter("XX")
    with pytest.raises(UnknownParameterError, match="Nonsense"):
        parameter_by_name("Nonsense")
