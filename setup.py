from setuptools import setup
from pathlib import Path

setup(
    name="pysquirrel",
    version="0.1.0",
    description="A Python library for fetching NUTS administrative divisions.",
    author="IIASA",
    url="https://github.com/iiasa/pySquirrel",
    license="MIT License",
    include_package_data=True,
    package_data={"": ["data/*"]},
    )