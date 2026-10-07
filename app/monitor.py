"""Workflow functions for monitoring CSV data quality."""

from pathlib import Path

from app.csv_processor import load_csv
from app.quality_checks import QualityMetrics, calculate_quality_metrics


def analyze_csv(file_path: str | Path) -> QualityMetrics:
    """Load a CSV file and calculate its data-quality metrics.

    Args:
        file_path: Path to the CSV file to analyze.

    Returns:
        The calculated quality metrics for the CSV data.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If the CSV file is empty or cannot be parsed.
    """
    dataframe = load_csv(file_path)
    return calculate_quality_metrics(dataframe)