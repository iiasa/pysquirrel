pySquirrel
==========

pySquirrel is a Python package designed to fetch NUTS administrative
divisions.

The current NUTS version is valid from 1 January 2024.

From the `Eurostat
website <https://ec.europa.eu/eurostat/web/nuts/overview>`__:

“The `NUTS
classification <https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Glossary:Nomenclature_of_territorial_units_for_statistics_(NUTS)>`__
(Nomenclature of territorial units for statistics) is a hierarchical
system for dividing up the economic territory of the EU for the purpose
of: 
- the collection, development and harmonisation of European regional statistics 
- socio-economic analyses of the regions 
    - NUTS 1: major socio-economic regions 
    - NUTS 2: basic regions for the application of regional policies 
    - NUTS 3: small regions for specific diagnoses
- framing of EU regional policies 
- regions eligible for support from cohesion policy have been defined at NUTS 2 level
- the cohesion report has so far mainly been prepared at NUTS 2 level”


.. code:: python

    >>> import pysquirrel
    >>> pysquirrel.nuts.get()


Eurostat copyright notice
-------------------------

Please note that pyNUTS is not developed, maintained or affiliated with
Eurostat. The `Eurostat copyright notice applies
<https://ec.europa.eu/eurostat/web/main/help/copyright-notice>`__.

The Eurostat editorial content is licensed under the
`Creative Commons Attribution 4.0 International licence
<https://creativecommons.org/licenses/by/4.0/>__`. Reuse of
statistical metadata such as the NUTS classification is authorised with due
citation of the source.

 European Commission, Eurostat, Statistical regions in the European Union and 
 partner countries – NUTS and statistical regions 2021 – 2022 edition, 
 Publications Office of the European Union, 2022, 
 `<https://data.europa.eu/doi/10.2785/321792>__`