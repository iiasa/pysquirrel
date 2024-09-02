"""pysquirrel"""

from .core import AllRegions
from importlib.metadata import version

__version__ = version("pysquirrel")

# create database
nuts = AllRegions()
