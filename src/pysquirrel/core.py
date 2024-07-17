"""

"""
import unicodedata

from dataclasses import fields
from pathlib import Path
from pydantic import field_validator, model_validator, ValidationInfo
from typing import Optional

import openpyxl
from pydantic.dataclasses import dataclass

# Base path for package code
BASE_PATH = Path(__file__).absolute().parent
DATA_PATH = BASE_PATH / "data"
MIN_DATA_ROW = 2
MAX_DATA_COL = 4

# utility function
def flatten(l):
    for i in l:
        if isinstance(i, list):
            yield from flatten(i)
        else:
            yield i

@dataclass(frozen=True)
class Region:
    """Territorial unit base class."""
    country_code: str
    code: str
    label: str
    level: int
    parent_code: Optional[str]

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
        Checks if unit code follows standard format of a two capital letters 
        country code followed by an alphanumeric code, between one to three elements.
        Placeholder units are marked with 'Z' in place of digits.
        """
        if v[:2].isalpha() and v[:2].isupper() and v[2:].isalnum():
            return v
        else:
            raise ValueError()

    @field_validator("level")
    @classmethod
    def check_level(cls, v: int):
        """
        Checks if level corresponds to 1, 2 or 3.
        """
        if v in [1, 2, 3]:
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
        if self.code.startswith(self.country_code) and \
            len(self.code) == len(self.country_code) + self.level:
            return self

class NUTSRegion(Region):
    """NUTS-specific implementation of the Region base class."""
    pass

class SRRegion(Region):
    """SR-specific implementation of the Region base class."""
    pass

class AllRegions:
    """Database that contains list of all territorial units."""

    filename = DATA_PATH / "NUTS2021-NUTS2024.xlsx"
    search_index: dict = {}
    data: list[dict] = []

    def __init__(self) -> None:
        self._load()
        self._set_index()

    def _load(self) -> None:
        """
        Reads data from NUTS spreadsheet into Database and builds search index.
        """
        spreadsheet = openpyxl.load_workbook(
            self.filename, read_only=True, data_only=True
        )
        sheet_class = {"NUTS2024": NUTSRegion, "Statistical Regions": SRRegion}

        for sheet_name, cls in sheet_class.items():
            sheet = spreadsheet[sheet_name]
            for row in sheet.iter_rows(min_row=MIN_DATA_ROW, max_col=MAX_DATA_COL):
                if all([cell.value for cell in row]):   
                    unit = {field.name: cell.value for (field, cell) in zip(fields(cls), row)}
                    if unit["level"] > 1:
                        unit.update({"parent_code": unit["code"][:-1]})
                    else:
                        unit.update({"parent_code": None})
                    self.data.append(cls(**unit))

    def _set_index(self) -> None:
        """
        
        """
        for unit in self.data:
            for field in fields(unit):
                key = self.search_index.setdefault(field.name, {})
                value = getattr(unit, field.name)
                if field.name == "code":
                    key[value] = unit
                else:
                    if value in key:
                        key[value].append(unit)
                    else:
                        key[value] = [unit]

    def _search(
            self, param: str, value: str | int,
        ) -> list[NUTSRegion | SRRegion]:
        """
        Searches database index for one value of a parameter
        and returns a set of all matching result(s).

        :param param: field to be searched
        :param value: value(s) to be searched in the field 
        
        """
        results = set(flatten([self.search_index[param][key] 
            for key in self.search_index[param] 
            if key == value]))
        
        return results

    def get(
            self, **params
        ) -> list[NUTSRegion | SRRegion, None, None]:
        """
        Searches NUTS 2024 classification database. Supports multiple fields/values
        search.

        :param **params: key-value pair, with key being a `Region` field to search,
        and the value to search
        """
        results = []
        if not params:
            raise TypeError("no keyword argument(s) passed.")
        else:
            for param, value in params.items():
                if isinstance(value, (int, str)):
                    if param in [field.name for field in fields(Region)]:
                        results.append(self._search(param, value))
                else:
                    raise TypeError("only one value per keyword argument allowed.")
            return list(set.intersection(*results))