from dataclasses import fields
from enum import IntEnum
from pathlib import Path
from pydantic import field_validator, model_validator, ValidationInfo

import os
import yaml
from pydantic.dataclasses import dataclass

# Base path for package code
BASE_PATH = Path(__file__).absolute().parent
DATA_PATH = BASE_PATH / "data"
MIN_DATA_ROW = 2
MAX_DATA_COL = 4


# utility function
def flatten(lst):
    for i in lst:
        if isinstance(i, list):
            yield from flatten(i)
        else:
            yield i


class Level(IntEnum):
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3


@dataclass(frozen=True)
class Region:
    """Territorial region base class."""

    country_code: str
    code: str
    label: str
    level: Level

    @property
    def parent_code(self) -> str | None:
        return self.code[:-1] if self.level > 1 else None

    @field_validator("country_code")
    @classmethod
    def check_country_code(cls, v: str):
        """
        Checks if country code follow standard format of two capital letters.
        """
        if v.isalpha() and v.isupper():
            return v
        else:
            raise ValueError()

    @field_validator("code")
    @classmethod
    def check_code(cls, v: str):
        """
        Checks if region code follows standard format of a two capital letters
        country code followed by an alphanumeric code, between one to three elements.
        Placeholder region are marked with 'Z' in place of digits.
        """
        if v[:2].isalpha() and v[:2].isupper() and v[2:].isalnum():
            return v
        else:
            raise ValueError()

    @field_validator("parent_code")
    @classmethod
    def check_parent_code(cls, v: str, info: ValidationInfo):
        if v is None and info.data["level"] == 1:
            return v
        elif v[:2].isalpha() and v[:2].isupper() and v[2:].isalnum():
            return v
        elif v is None and info.data["level"] == 1:
            return v
        else:
            raise ValueError()

    @model_validator(mode="after")
    def check_code_consistency(self):
        """Checks if code, country code, and level are all in conformity."""
        if (
            self.code.startswith(self.country_code)
            and len(self.code) == len(self.country_code) + self.level
        ):
            return self


class NUTSRegion(Region):
    """NUTS-specific implementation of the Region base class."""

    pass


class SRRegion(Region):
    """SR-specific implementation of the Region base class."""

    pass


class AllRegions:
    """Database that contains list of all territorial region."""

    data: list[NUTSRegion | SRRegion] = []

    def __init__(self) -> None:
        self._load()

    def _load(self) -> None:
        """
        Reads data from NUTS data files into Database and builds search index.
        """
        region_class = {"NUTS": NUTSRegion, "SR": SRRegion}

        for data_file in os.listdir(DATA_PATH):
            for region_type, cls in region_class.items():
                if data_file.startswith(region_type):
                    with open(DATA_PATH / data_file, "r", encoding="utf8") as f:
                        data = yaml.safe_load(f)
                    for region in data:
                        region = {
                            field.name: value
                            for (field, value) in zip(fields(cls), region.values())
                        }
                        self.data.append(cls(**region))

    def _search(
        self,
        param: str,
        value: str | int,
    ) -> set[NUTSRegion | SRRegion]:
        """
        Searches database for one value of a region field
        and returns a set of all matching result(s).

        :param param: field to be searched
        :param value: value(s) to be searched in the field
        """
        return set(i for i in self.data if getattr(i, param) == value)

    def get(
        self, *, country_code: str | list[str] = None, level: int | list[int] = None
    ) -> list[NUTSRegion | SRRegion, None]:
        """
        Searches NUTS 2024 classification database by country code(s) and/or
        NUTS level.
        Returns all regions for the listed countries and levels.

        :param country_code: country code(s) to search
        :param level: NUTS level(s) to search
        """
        results = []
        if not (country_code or level):
            raise ValueError("no keyword argument(s) passed.")
        for param, values in {"country_code": country_code, "level": level}.items():
            if isinstance(values, (int, str)):
                values = [values]
            if values:
                results.append(
                    set.union(*(self._search(param, value) for value in values))
                )
        return list(set.intersection(*results))
