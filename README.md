# pysquirrel - NUTS administrative region utility

[![license](https://img.shields.io/badge/License-MIT-blue)](https://github.com/iiasa/pysquirrel/blob/main/LICENSE)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pytest](https://img.shields.io/github/actions/workflow/status/iiasa/pysquirrel/pytest.yml?logo=GitHub&label=pytest)](https://github.com/iiasa/pysquirrel/actions/workflows/pytest.yml)

Copyright 2024 IIASA Scenario Services team

This repository is licensed under the [MIT License](LICENSE).

## Overview

**pysquirrel** is a Python package designed to work with NUTS administrative divisions.

The current NUTS version is valid from 1 January 2024.

## Background

From the [Eurostat website](https://ec.europa.eu/eurostat/web/nuts/overview)

The [NUTS
classification](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Glossary:Nomenclature_of_territorial_units_for_statistics_(NUTS))
(Nomenclature of territorial units for statistics) is a geographical nomenclature subdividing the economic territory of the European Union (EU) into regions at three different levels (NUTS 1, 2 and 3 respectively, moving from larger to smaller territorial units). Above NUTS 1, there is the 'national' level of the Member States.

NUTS is used for:

- collecting, developing and harmonising European regional statistics
- carrying out socio-economic analyses of the regions
- framing of EU regional policies

## Usage

**pysquirrel** allows searching the list of all territorial units by specifying the 
parameters and the values to search as shown below:

```python
>>> import pysquirrel

>>> pysquirrel.nuts.get(country_code="AT")  # gets all regions in Austria

>>> pysquirrel.nuts.get(level=3)  # gets all NUTS3 regions

>>> pysquirrel.nuts.get(country_code="AT", level=3)  # gets all NUTS3 regions in Austria
```

Each Region object consists of five attributes:
- a NUTS code (e.g.: AT127)
- a country code
- a label (the full region name)
- a NUTS level (1, 2 or 3)
- a parent code (corresponding to the NUTS parent region)

## Eurostat copyright notice on NUTS region data file

This package imports the NUTS spreadsheet from the Eurostat website.

Please note that pysquirrel is not developed, maintained or affiliated
with Eurostat. The [Eurostat copyright notice
applies](https://ec.europa.eu/eurostat/web/main/help/copyright-notice).

The Eurostat editorial content is licensed under the [Creative Commons
Attribution 4.0 International licence](https://creativecommons.org/licenses/by/4.0/). Reuse
of statistical metadata such as the NUTS classification is authorised
with due citation of the source.

> European Commission, Eurostat, Statistical regions in the European
> Union and partner countries -- NUTS and statistical regions 2021 --
> 2022 edition, Publications Office of the European Union, 2022,
> https://data.europa.eu/doi/10.2785/321792

## Acknowledgement

This package is developed and maintained by the *Scenario Services & Scientific Software*
research theme at the IIASA Energy, Climate, and Enviroment program.
Visit https://software.ece.iiasa.ac.at for more information.
