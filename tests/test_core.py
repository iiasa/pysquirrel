import pytest

from pysquirrel.core import Level, NUTSRegion, AllRegions
from pydantic import ValidationError

SAMPLE_DATA = [
    NUTSRegion(country_code="AT", code="AT1", label="Ostösterreich", level=1),
    NUTSRegion(country_code="AT", code="AT12", label="Niederösterreich", level=2),
    NUTSRegion(country_code="AT", code="AT127", label="Wiener Umland/Südteil", level=3),
    NUTSRegion(country_code="PT", code="PT1", label="Continente", level=1),
    NUTSRegion(country_code="PT", code="PT1C", label="Alentejo", level=2),
    NUTSRegion(country_code="PT", code="PT1C1", label="Alentejo Litoral", level=3),
]


class TestRegionClass:
    def test_region_creation(self):
        region = SAMPLE_DATA[2]
        assert region.country_code == "AT"
        assert region.code == "AT127"
        assert region.label == "Wiener Umland/Südteil"
        assert region.level == Level.LEVEL_3

    def test_invalid_country_code(self):
        with pytest.raises(ValidationError):
            NUTSRegion(
                country_code="at", code="AT127", label="Wiener Umland/Südteil", level=3
            )

    def test_invalid_region_code(self):
        with pytest.raises(ValidationError):
            NUTSRegion(
                country_code="AT", code="A127", label="Wiener Umland/Südteil", level=3
            )


def mock_load(self):
    """Mocked _load method that loads a sample dataset."""
    self.data = SAMPLE_DATA


def test_all_regions(monkeypatch):
    # Create an instance of AllRegions
    all_regions = AllRegions()

    # Replace the _load method with the mock method
    monkeypatch.setattr(AllRegions, "_load", mock_load)

    # Call _load to apply the mock
    all_regions._load()

    # Check if the data is loaded correctly
    assert len(all_regions.data) == 6

    # Check if returned data sets are equivalent (get() processing might change order of results)
    assert set(all_regions.get(country_code="AT")) == set(SAMPLE_DATA[:3])
    assert set(all_regions.get(country_code="PT")) == set(SAMPLE_DATA[3:])
    assert set(all_regions.get(level=2)) == set([SAMPLE_DATA[1], SAMPLE_DATA[4]])
    assert set(all_regions.get(country_code="AT", level=1)) == set([SAMPLE_DATA[0]])
    assert set(all_regions.get(country_code="PT", level=3)) == set([SAMPLE_DATA[-1]])
    assert set(all_regions.get(country_code=["AT", "PT"])) == set(SAMPLE_DATA)
