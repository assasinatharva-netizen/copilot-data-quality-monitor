"""Quality metrics for tabular data."""

from typing import TypedDict

import pandas as pd


class QualityMetrics(TypedDict):
    """Metrics calculated for a pandas DataFrame."""

    row_count: int
    column_count: int
    null_count: int
    duplicate_count: int
    null_percentage: float


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
    return {
        "row_count": row_count,
        "column_count": column_count,
        "null_count": null_count,
        "duplicate_count": duplicate_count,
        "null_percentage": null_percentage,
    }