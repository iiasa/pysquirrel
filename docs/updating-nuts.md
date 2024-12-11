# Updating the NUTS source file

EUROSTAT occasionally updates the current NUTS classification spreadsheet. These updates might be minor and not encompass changing region names or codes, but knowing they take place, it is important to ensure the package accesses the most up-to-date version of the data.

To this end, a weekly GitHub action compares pysquirrel's copy of the file and the version hosted in the EUROSTAT website with a hash check. The workflow fails if hashes differ.

In such a case, using a local installation of pysquirrel, and with the newest version of the spreadsheet downloaded:

```python
from pysquirrel.core import nuts_to_yaml

nuts_to_yaml("path/to/latest_nuts.xlsx", "path/to/output")
```

The function will parse the XLSX file and output the two corresponding YAML files (for NUTS regions and Statistical Regions). YAML files allow for easy tracking of changes in GitHub commits.