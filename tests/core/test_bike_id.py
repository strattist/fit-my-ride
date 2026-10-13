import pytest

from fit_my_ride.core.schema import bike_id, slugify


def test_id_without_year():
    assert bike_id("KTM", "Strada Elite") == "ktm:strada_elite"


def test_id_with_year():
    assert bike_id("Van Rysel", "RCR Pro", 2025) == "van_rysel:rcr_pro:2025"


def test_same_input_same_id():
    assert bike_id("Van Rysel", "RCR Pro", 2025) == bike_id("Van Rysel", "RCR Pro", 2025)


def test_slug_normalises_accents_and_punctuation():
    assert slugify("  Côte-d'Azur / 2.0 ") == "cote_d_azur_2_0"


@pytest.mark.parametrize("vendor, model", [("", "X"), ("KTM", "  "), ("KTM", "---")])
def test_empty_names_raise(vendor, model):
    with pytest.raises(ValueError):
        bike_id(vendor, model)


def test_empty_names_raise_typed_error():
    from fit_my_ride.core.schema import InvalidNameError

    with pytest.raises(InvalidNameError):
        bike_id("KTM", "---")


@pytest.mark.parametrize(
    ("text", "slug"), [("Straße", "strasse"), ("Øresund", "oresund"), ("Łódź", "lodz")]
)
def test_slug_transliterates_letters_without_decomposition(text, slug):
    assert slugify(text) == slug
