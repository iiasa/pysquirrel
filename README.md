# pysquirrel

pysquirrel is a Python package designed to fetch NUTS administrative
divisions.

The current NUTS version is valid from 1 January 2024.

From the [Eurostat
website](https://ec.europa.eu/eurostat/web/nuts/overview):

The [NUTS
classification](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Glossary:Nomenclature_of_territorial_units_for_statistics_(NUTS))
(Nomenclature of territorial units for statistics) "is a geographical nomenclature subdividing the economic territory of the European Union (EU) into regions at three different levels (NUTS 1, 2 and 3 respectively, moving from larger to smaller territorial units). Above NUTS 1, there is the 'national' level of the Member States."

"NUTS is used for:

- collecting, developing and harmonising European regional statistics
- carrying out socio-economic analyses of the regions
- framing of EU regional policies"

## Usage

pysquirrel allows searching the list of all territorial units by specifying the 
parameters and the values to search as shown below:

```python
>>> import pysquirrel

>>> pysquirrel.nuts.get(country_code="AT")  # gets all regions in Austria

>>> pysquirrel.nuts.get(code="PT191")  # gets the PT191 region

>>> pysquirrel.nuts.get(label="Drenthe")  # gets the Drenthe region

>>> pysquirrel.nuts.get(level=3)  # gets all NUTS3 regions

>>> pysquirrel.nuts.get(parent_code="DE2")  # gets all regions whose parent region is DE2
```

## Eurostat copyright notice

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