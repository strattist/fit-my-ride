"""Canonical schema: the one definition of geometry parameters and record shapes."""

import re
import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum


class Tier(StrEnum):
    CORE = "core"
    OPTIONAL = "optional"


class UnknownParameterError(KeyError):
    """Raised when a parameter code or name is not in the canonical schema."""


class InvalidNameError(ValueError):
    """Raised when a vendor or model name yields no usable slug."""


@dataclass(frozen=True)
class Parameter:
    code: str
    name: str
    unit: str
    tier: Tier


# Canonical order; the full name is the meaning, the code a compact key.
PARAMETERS: tuple[Parameter, ...] = (
    Parameter("ST", "Seat Tube Length", "cm", Tier.OPTIONAL),
    Parameter("HT", "Head Tube Length", "cm", Tier.OPTIONAL),
    Parameter("TT", "Top Tube Length", "cm", Tier.OPTIONAL),
    Parameter("HTA", "Head Tube Angle", "deg", Tier.CORE),
    Parameter("STA", "Seat Tube Angle", "deg", Tier.CORE),
    Parameter("CS", "Chainstay Length", "cm", Tier.OPTIONAL),
    Parameter("FL", "Fork Length", "cm", Tier.OPTIONAL),
    Parameter("FR", "Fork Rake", "cm", Tier.OPTIONAL),
    Parameter("BB", "Bottom Bracket Drop", "cm", Tier.CORE),
    Parameter("S", "Stack", "cm", Tier.CORE),
    Parameter("R", "Reach", "cm", Tier.CORE),
    Parameter("E", "Wheel Base", "cm", Tier.OPTIONAL),
)

CORE_PARAMETERS: tuple[Parameter, ...] = tuple(p for p in PARAMETERS if p.tier is Tier.CORE)
OPTIONAL_PARAMETERS: tuple[Parameter, ...] = tuple(p for p in PARAMETERS if p.tier is Tier.OPTIONAL)

_BY_CODE = {p.code: p for p in PARAMETERS}
_BY_NAME = {p.name: p for p in PARAMETERS}


def parameter(code: str) -> Parameter:
    """Resolve a short code to its parameter; unknown code raises KeyError."""
    try:
        return _BY_CODE[code]
    except KeyError:
        raise UnknownParameterError(code) from None


def parameter_by_name(name: str) -> Parameter:
    """Resolve a full name to its parameter; unknown name raises KeyError."""
    try:
        return _BY_NAME[name]
    except KeyError:
        raise UnknownParameterError(name) from None


# Letters NFKD cannot decompose; without this they would be dropped and names collide.
_TRANSLITERATION = str.maketrans(
    {
        "ß": "ss",
        "ø": "o",
        "Ø": "O",
        "æ": "ae",
        "Æ": "AE",
        "œ": "oe",
        "Œ": "OE",
        "ł": "l",
        "Ł": "L",
        "đ": "d",
        "Đ": "D",
        "þ": "th",
        "Þ": "TH",
    }
)


def slugify(text: str) -> str:
    """Lowercase ASCII slug with single underscores; an empty result raises ValueError."""
    folded = unicodedata.normalize("NFKD", text.translate(_TRANSLITERATION))
    ascii_text = "".join(c for c in folded if not unicodedata.combining(c))
    slug = re.sub(r"[^a-z0-9]+", "_", ascii_text.lower()).strip("_")
    if not slug:
        raise InvalidNameError(f"cannot derive a slug from {text!r}")
    return slug


def bike_id(vendor: str, model: str, year: int | None = None) -> str:
    """`<vendor_slug>:<model_slug>[:<model_year>]`, identical for identical input."""
    parts = [slugify(vendor), slugify(model)]
    if year is not None:
        parts.append(str(year))
    return ":".join(parts)


NOT_REPORTED = "not reported"


@dataclass(frozen=True)
class ParameterValue:
    """A measured value, or `None` plus the reason it is missing; never zero as a stand-in."""

    value: float | None
    reason: str | None = None

    def __post_init__(self):
        if self.value is None and not (self.reason and self.reason.strip()):
            raise ValueError("a missing value needs a reason")
        if self.value is not None and self.reason is not None:
            raise ValueError("a reason is only valid for a missing value")


def complete_geometry(partial: Mapping[str, ParameterValue]) -> dict[str, ParameterValue]:
    """All 12 parameters in canonical order; absent ones are null plus a reason."""
    for code in partial:
        parameter(code)
    return {p.code: partial.get(p.code, ParameterValue(None, NOT_REPORTED)) for p in PARAMETERS}


class Style(StrEnum):
    """Usage Taxonomy: the fixed riding-style set, also the rider's style input.

    The string values are the wire format (URL parameter, approved files); renaming one
    breaks existing links and data.
    """

    ROAD = "road"
    GRAVEL = "gravel"
    MTB = "mtb"
    CITY_COMMUTE = "city_commute"
    TOURING = "touring"
    E_BIKE = "e_bike"


class InvalidRiderInputError(ValueError):
    """Raised when a rider input is outside its accepted range or set."""


HEIGHT_RANGE_CM = (120, 230)
INSEAM_RANGE_CM = (50, 120)


@dataclass(frozen=True)
class RiderInput:
    """The rider's three inputs; invalid values raise with the accepted range named.

    `style` may be given as a `Style` or its string value; it is stored as a `Style`.
    """

    height_cm: float
    inseam_cm: float
    style: Style

    def __post_init__(self):
        for label, value, (low, high) in (
            ("height_cm", self.height_cm, HEIGHT_RANGE_CM),
            ("inseam_cm", self.inseam_cm, INSEAM_RANGE_CM),
        ):
            if isinstance(value, bool) or not isinstance(value, int | float):
                raise InvalidRiderInputError(f"{label} must be a number, got {value!r}")
            if not low <= value <= high:
                raise InvalidRiderInputError(
                    f"{label} must be between {low} and {high}, got {value}"
                )
        try:
            object.__setattr__(self, "style", Style(self.style))
        except ValueError:
            accepted = ", ".join(s.value for s in Style)
            raise InvalidRiderInputError(
                f"style must be one of {accepted}, got {self.style!r}"
            ) from None
