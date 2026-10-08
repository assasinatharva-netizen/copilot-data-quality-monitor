"""Quality metrics for tabular data."""

from typing import Literal, TypedDict

import pandas as pd

QualityStatus = Literal["PASS", "WARNING", "FAIL"]


class QualityMetrics(TypedDict):
    """Metrics calculated for a pandas DataFrame."""

    row_count: int
    column_count: int
    null_count: int
    duplicate_count: int
    null_percentage: float
    quality_status: QualityStatus


def calculate_quality_status(null_percentage: float) -> QualityStatus:
    """Return a quality status based on the percentage of null values."""
    if null_percentage < 5:
        return "PASS"
    if null_percentage <= 20:
        return "WARNING"
    return "FAIL"


def calculate_quality_metrics(df: pd.DataFrame) -> QualityMetrics:
    """Calculate basic data-quality metrics for a DataFrame.

    The null percentage is the percentage of cells in the DataFrame that are
    null. Empty DataFrames return a null percentage of ``0.0``.
    """
    row_count, column_count = df.shape
    null_count = int(df.isna().sum().sum())
    duplicate_count = int(df.duplicated().sum())
    total_cells = row_count * column_count
    null_percentage = (null_count / total_cells * 100) if total_cells else 0.0
    quality_status = calculate_quality_status(null_percentage)
    return {
        "row_count": row_count,
        "column_count": column_count,
        "null_count": null_count,
        "duplicate_count": duplicate_count,
        "null_percentage": null_percentage,
        "quality_status": quality_status,
    }