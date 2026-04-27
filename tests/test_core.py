"""Tests for region models and AllRegions database."""

import pytest

from pysquirrel.core import Level, NUTSRegion, SRRegion, AllRegions
from pydantic import ValidationError

AT1 = NUTSRegion(country_code="AT", code="AT1", label="Ostösterreich", level=1)
AT12 = NUTSRegion(country_code="AT", code="AT12", label="Niederösterreich", level=2)
AT127 = NUTSRegion(
    country_code="AT", code="AT127", label="Wiener Umland/Südteil", level=3
)
PT1 = NUTSRegion(country_code="PT", code="PT1", label="Continente", level=1)
PT1C = NUTSRegion(country_code="PT", code="PT1C", label="Alentejo", level=2)
PT1C1 = NUTSRegion(country_code="PT", code="PT1C1", label="Alentejo Litoral", level=3)
IS0 = SRRegion(country_code="IS", code="IS0", label="Ísland", level=1)

MOCK_DATA = [AT1, AT12, AT127, PT1, PT1C, PT1C1, IS0]


@pytest.fixture
def mock_db(monkeypatch):
    """AllRegions instance loaded with MOCK_DATA instead of real data files."""

    def _mock_load(self):
        self.data = MOCK_DATA

    monkeypatch.setattr(AllRegions, "_load", _mock_load)
    db = AllRegions()
    return db


def test_region_creation():
    """Test region fields are stored and exposed correctly."""
    assert AT127.country_code == "AT"
    assert AT127.code == "AT127"
    assert AT127.label == "Wiener Umland/Südteil"
    assert AT127.level == Level.LEVEL_3


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "country_code": "at",
            "code": "AT127",
            "label": "Wiener Umland/Südteil",
            "level": 3,
        },
        {
            "country_code": "AT",
            "code": "A127",
            "label": "Wiener Umland/Südteil",
            "level": 3,
        },
    ],
)
def test_invalid_region(kwargs):
    """Test invalid country or region codes raise a ValidationError."""
    with pytest.raises(ValidationError):
        NUTSRegion(**kwargs)


@pytest.mark.parametrize(
    "kwargs",
    [
        # code does not start with country_code
        {"country_code": "AT", "code": "DE1", "label": "Mismatch", "level": 1},
        # code length inconsistent with level (level 2 needs 4 chars, got 5)
        {"country_code": "AT", "code": "AT127", "label": "Mismatch", "level": 2},
    ],
)
def test_code_consistency(kwargs):
    """Test that mismatches between code, country_code, and level raise ValidationError."""
    with pytest.raises(ValidationError):
        NUTSRegion(**kwargs)


def test_is_extra_regio():
    """Test `is_extra_regio` is True for Z-suffix codes and False for normal codes."""
    extra = NUTSRegion(
        country_code="BE", code="BEZ", label="Extra-Regio NUTS 1", level=1
    )
    assert extra.is_extra_regio is True
    assert AT1.is_extra_regio is False


@pytest.fixture(scope="module")
def real_db():
    return AllRegions()


@pytest.mark.parametrize("level,expected", [(1, 135), (2, 367), (3, 1662)])
def test_counts_exclude_extra_regio(real_db, level, expected):
    """Test region counts per level exclude Extra-Regio entries by default."""
    assert len(real_db.get(level=level)) == expected


@pytest.mark.parametrize("level,expected", [(1, 174), (2, 406), (3, 1700)])
def test_counts_include_extra_regio(real_db, level, expected):
    """Test region counts per level include Extra-Regio entries when requested."""
    assert len(real_db.get(level=level, include_extra_regio=True)) == expected


def test_uk_import(real_db):
    """Test UK NUTS regions from the supplementary file are imported correctly."""
    assert len(real_db.get(country_code="UK")) == 232


def test_mock_data_loaded(mock_db):
    """Test the mock fixture loads exactly the expected number of regions."""
    assert len(mock_db.data) == len(MOCK_DATA)


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({"country_code": "AT"}, {AT1, AT12, AT127}),
        ({"country_code": "PT"}, {PT1, PT1C, PT1C1}),
        ({"country_code": "IS"}, {IS0}),
        ({"level": 2}, {AT12, PT1C}),
        ({"country_code": "AT", "level": 1}, {AT1}),
        ({"country_code": "PT", "level": 3}, {PT1C1}),
    ],
)
def test_query(mock_db, kwargs, expected):
    """Test get() filters correctly by country_code and/or level."""
    assert set(mock_db.get(**kwargs)) == expected


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({"iso3": "AUT"}, {AT1, AT12, AT127}),
        ({"iso3": ["AUT", "PRT"]}, {AT1, AT12, AT127, PT1, PT1C, PT1C1}),
        ({"iso3": "PT"}, {PT1, PT1C, PT1C1}),  # ISO2 accepted in iso3 param
    ],
)
def test_iso3_lookup(mock_db, kwargs, expected):
    """Test get() resolves ISO3 (and ISO2 passed as iso3) to the correct regions."""
    assert set(mock_db.get(**kwargs)) == expected


def test_get_no_args_raises(mock_db):
    """Test get() raises ValueError when called with no arguments."""
    with pytest.raises(ValueError, match="no keyword argument"):
        mock_db.get()


@pytest.mark.parametrize(
    "iso3, exc_match",
    [
        ("XYZ", "unknown ISO3 code"),
        ("TOOLONG", "invalid ISO code"),
        (123, "ISO3 codes must be strings"),
    ],
)
def test_iso3_invalid_raises(mock_db, iso3, exc_match):
    """Test get() raises ValueError for unrecognised or malformed iso3 values."""
    with pytest.raises(ValueError, match=exc_match):
        mock_db.get(iso3=iso3)
