"""Core data models and region database for pysquirrel."""

from dataclasses import fields
from enum import IntEnum
from pathlib import Path
from pydantic import field_validator, model_validator, ValidationInfo

import os
import yaml
from openpyxl import load_workbook
from pydantic.dataclasses import dataclass

# Base path for package code
BASE_PATH = Path(__file__).absolute().parent
DATA_PATH = BASE_PATH / "data"
COL_NAME_ROW = 1
MIN_DATA_ROW = 2
MAX_DATA_COL = 4


# Minimal ISO mappings (ISO 3166-1 alpha-2 -> alpha-3)
ISO2_TO_ISO3 = {
    "AT": "AUT",
    "BE": "BEL",
    "BG": "BGR",
    "HR": "HRV",
    "CY": "CYP",
    "CZ": "CZE",
    "DK": "DNK",
    "EE": "EST",
    "FI": "FIN",
    "FR": "FRA",
    "DE": "DEU",
    "GR": "GRC",
    "EL": "GRC",
    "HU": "HUN",
    "IE": "IRL",
    "IS": "ISL",
    "IT": "ITA",
    "LI": "LIE",
    "LV": "LVA",
    "LT": "LTU",
    "LU": "LUX",
    "MT": "MLT",
    "NL": "NLD",
    "NO": "NOR",
    "PL": "POL",
    "PT": "PRT",
    "RO": "ROU",
    "SK": "SVK",
    "SI": "SVN",
    "ES": "ESP",
    "SE": "SWE",
    "GB": "GBR",
    "CH": "CHE",
    "TR": "TUR",
    "RS": "SRB",
    "ME": "MNE",
    "AL": "ALB",
    "MK": "MKD",
    "UA": "UKR",
    "UK": "GBR",
}

# Reverse mapping for quick lookups from ISO3 -> ISO2
ISO3_TO_ISO2 = {v: k for k, v in ISO2_TO_ISO3.items()}


# Utility functions
def flatten(lst):
    for i in lst:
        if isinstance(i, list):
            yield from flatten(i)
        else:
            yield i


def nuts_to_yaml(file_path: str, output_dir: str):
    """Converts a NUTS .xlsx source file to YAML files."""

    workbook = load_workbook(file_path, read_only=True, data_only=True)

    for sheet, file in {
        "NUTS2024": "NUTS2021-2024.yaml",
        "Statistical Regions": "SR2021-2024.yaml",
    }.items():
        regions = []
        worksheet = workbook[sheet]
        cols = [cell.value for cell in worksheet[1]]
        for row in worksheet.iter_rows(min_row=MIN_DATA_ROW, max_col=MAX_DATA_COL):
            if all(cell.value for cell in row):
                regions.append({col: cell.value for (col, cell) in zip(cols, row)})

        with open(Path(output_dir) / file, "w") as f:
            yaml.dump(regions, f, allow_unicode=True)


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

    @property
    def is_extra_regio(self) -> bool:
        return all(c == "Z" for c in self.code[len(self.country_code) :])

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
        else:
            raise ValueError(
                f"code '{self.code}' is inconsistent with country_code "
                f"'{self.country_code}' and level {self.level}."
            )


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
                if data_file.startswith(region_type) and data_file.endswith("yaml"):
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
        self,
        *,
        country_code: str | list[str] = None,
        iso3: str | list[str] = None,
        level: int | list[int] = None,
        include_extra_regio: bool = False,
    ) -> list[NUTSRegion | SRRegion, None]:
        """
        Searches NUTS 2024 classification database by country code(s), ISO3 code, or
        NUTS level.
        Returns all regions for the listed countries and levels.

        :param country_code: country code(s) to search
        :param iso3: ISO3 code(s) to search
        :param level: NUTS level(s) to search
        :param include_extra_regio: if True, include Extra-Regio NUTS regions
            (codes where all characters after the country code are 'Z',
            e.g. BEZ, BEZZ, BEZZZ). Defaults to False.
        """
        results: list[Region] = []
        if not (country_code or level or iso3):
            raise ValueError("no keyword argument(s) passed.")

        # If iso3 is provided, convert to country_code(s) (ISO2) using
        # the built-in mapping. Accept both single string and list.
        if iso3:
            iso3_codes = iso3 if isinstance(iso3, (list, tuple)) else [iso3]
            iso2_codes: list[str] = []
            for v in iso3_codes:
                if not isinstance(v, str):
                    raise ValueError("ISO3 codes must be strings")
                v_up = v.upper()
                # Accept both 3-letter ISO3 and 2-letter ISO2 passed accidentally.
                if len(v_up) == 3:
                    if v_up in ISO3_TO_ISO2:
                        iso2_codes.append(ISO3_TO_ISO2[v_up])
                    else:
                        raise ValueError(f"unknown ISO3 code: {v}")
                elif len(v_up) == 2:
                    iso2_codes.append(v_up)
                else:
                    raise ValueError(f"invalid ISO code: {v}")

            # Merge converted ISO2 values into country_code argument
            if country_code:
                # normalize existing country_code into list
                if isinstance(country_code, (str, int)):
                    country_code = [country_code]
                country_code = list(set(country_code) | set(iso2_codes))
            else:
                country_code = iso2_codes
        for param, values in {"country_code": country_code, "level": level}.items():
            if isinstance(values, (int, str)):
                values = [values]
            if values:
                results.append(
                    set.union(*(self._search(param, value) for value in values))
                )
        matched = (
            {r for r in set.intersection(*results) if not r.is_extra_regio}
            if not include_extra_regio
            else set.intersection(*results)
        )
        return list(matched)
