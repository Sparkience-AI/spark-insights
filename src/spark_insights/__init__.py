"""Deterministic Spark Insights analysis core."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("spark-insights")
except PackageNotFoundError:
    __version__ = "uninstalled"

from .pipeline import run_analysis

__all__ = ["run_analysis"]
