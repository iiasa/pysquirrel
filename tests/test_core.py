import pytest

from pysquirrel.core import Level, NUTSRegion, AllRegions
from pydantic import ValidationError

MOCK_DATA = [
    NUTSRegion(country_code="AT", code="AT1", label="Ostösterreich", level=1),
    NUTSRegion(country_code="AT", code="AT12", label="Niederösterreich", level=2),
    NUTSRegion(country_code="AT", code="AT127", label="Wiener Umland/Südteil", level=3),
    NUTSRegion(country_code="PT", code="PT1", label="Continente", level=1),
    NUTSRegion(country_code="PT", code="PT1C", label="Alentejo", level=2),
    NUTSRegion(country_code="PT", code="PT1C1", label="Alentejo Litoral", level=3),
]


def test_region_creation():
    region = MOCK_DATA[2]
    assert region.country_code == "AT"
    assert region.code == "AT127"
    assert region.label == "Wiener Umland/Südteil"
    assert region.level == Level.LEVEL_3


def test_invalid_country_code():
    with pytest.raises(ValidationError):
        NUTSRegion(
            country_code="at", code="AT127", label="Wiener Umland/Südteil", level=3
        )


def test_invalid_region_code():
    with pytest.raises(ValidationError):
        NUTSRegion(
            country_code="AT", code="A127", label="Wiener Umland/Südteil", level=3
        )


def mock_load(self):
    """Mocked _load method that loads a sample dataset."""
    self.data = MOCK_DATA


def test_all_regions(monkeypatch):
    # Create an instance of AllRegions
    all_regions = AllRegions()

    # Test full data import
    assert len(all_regions.get(level=1)) == 160
    assert len(all_regions.get(level=2)) == 361
    assert len(all_regions.get(level=3)) == 1521

    # Test data fields
    lux = [
        nuts
        for nuts in all_regions.get(country_code="LU", level=1)
        if "Z" not in nuts.code  # exclude Extra-Regio NUTS 1
    ]
    assert len(lux) == 1
    assert lux[0].label == "Luxembourg" and lux[0].code == "LU0"

    # Replace the _load method with the mock method
    monkeypatch.setattr(AllRegions, "_load", mock_load)

    # Call _load to apply the mock
    all_regions._load()

    # Check if the data is loaded correctly
    assert len(all_regions.data) == 6

    # Test query logic with mock data
    assert set(all_regions.get(country_code="AT")) == set(MOCK_DATA[:3])
    assert set(all_regions.get(country_code="PT")) == set(MOCK_DATA[3:])
    assert set(all_regions.get(level=2)) == set([MOCK_DATA[1], MOCK_DATA[4]])
    assert set(all_regions.get(country_code="AT", level=1)) == set([MOCK_DATA[0]])
    assert set(all_regions.get(country_code="PT", level=3)) == set([MOCK_DATA[-1]])
    assert set(all_regions.get(country_code=["AT", "PT"])) == set(MOCK_DATA)
