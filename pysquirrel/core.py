from dataclasses import fields
from enum import IntEnum
from pathlib import Path
from pydantic import field_validator, model_validator, ValidationInfo

import openpyxl
import pooch
from pydantic.dataclasses import dataclass

# Base path for package code
BASE_PATH = Path(__file__).absolute().parent
BASE_URL = "https://ec.europa.eu/eurostat/documents/345175/629341/"
FILENAME = "NUTS2021-NUTS2024.xlsx"
FILE_URL = BASE_URL + FILENAME
MIN_DATA_ROW = 2
MAX_DATA_COL = 4


# utility function
def flatten(l):
    for i in l:
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

    search_index: dict = {}
    data: list[NUTSRegion | SRRegion] = []

    def __init__(self) -> None:
        self._load()
        self._set_index()

    def _load(self) -> None:
        """
        Reads data from NUTS spreadsheet into Database and builds search index.
        """
        nuts2024_hash = (
            "3df559906175180d58a2a283985fb632b799b4cbe034e92515295064a9f2c01e"
        )
        pooch.retrieve(
            FILE_URL, known_hash=nuts2024_hash, fname=FILENAME, path=BASE_PATH
        )
        spreadsheet = openpyxl.load_workbook(
            BASE_PATH / FILENAME, read_only=True, data_only=True
        )
        sheet_class = {"NUTS2024": NUTSRegion, "Statistical Regions": SRRegion}

        for sheet_name, cls in sheet_class.items():
            sheet = spreadsheet[sheet_name]
            for row in sheet.iter_rows(min_row=MIN_DATA_ROW, max_col=MAX_DATA_COL):
                if all(cell.value for cell in row):
                    region = {
                        field.name: cell.value
                        for (field, cell) in zip(fields(cls), row)
                    }
                    self.data.append(cls(**region))

    def _set_index(self) -> None:
        """
        Builds search index to be used to retrieve regions.
        """
        for region in self.data:
            for field in fields(region):
                key = self.search_index.setdefault(field.name, {})
                value = getattr(region, field.name)
                if field.name == "code":
                    key[value] = region
                else:
                    if value in key:
                        key[value].append(region)
                    else:
                        key[value] = [region]

    def _search(
        self,
        param: str,
        value: str | int,
    ) -> list[NUTSRegion | SRRegion]:
        """
        Searches database index for one value of a parameter
        and returns a set of all matching result(s).

        :param param: field to be searched
        :param value: value(s) to be searched in the field

        """
        results = set(
            flatten(
                [
                    self.search_index[param][key]
                    for key in self.search_index[param]
                    if key == value
                ]
            )
        )

        return results

    def get(self, **params) -> list[NUTSRegion | SRRegion, None]:
        """
        Searches NUTS 2024 classification database. Supports multiple fields/values
        search.

        :param **params: key-value pair, with key being a `Region` field to search,
        and the value to search
        """
        results = []
        if not params:
            raise ValueError("no keyword argument(s) passed.")
        else:
            for param, value in params.items():
                if isinstance(value, (int, str)):
                    if param in [field.name for field in fields(Region)]:
                        results.append(self._search(param, value))
                else:
                    raise TypeError("only one value per keyword argument allowed.")
            return list(set.intersection(*results))
