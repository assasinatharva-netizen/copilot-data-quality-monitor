"""End-to-end workflow for processing CSV dataset quality."""

from pathlib import Path

from app.csv_processor import load_csv
from app.database import DATABASE_PATH, insert_quality_result
from app.quality_checks import QualityMetrics, calculate_quality_metrics


def process_dataset(
    file_path: str | Path,
    database_path: str | Path = DATABASE_PATH,
) -> QualityMetrics:
    """Load a CSV dataset, calculate its metrics, and store the result.

    Args:
        file_path: Path to the CSV file to process.
        database_path: Path to the SQLite database that stores the result.

    Returns:
        The calculated quality metrics for the dataset.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If the CSV file is empty or cannot be parsed.
    """
    path = Path(file_path)
    dataframe = load_csv(path)
    metrics = calculate_quality_metrics(dataframe)
    insert_quality_result(path.name, metrics, database_path)
    return metrics