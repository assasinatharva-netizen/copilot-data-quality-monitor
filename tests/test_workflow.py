import pytest

from app.database import get_quality_results
from app.workflow import process_dataset


def test_process_dataset_calculates_and_stores_quality_metrics(tmp_path) -> None:
    csv_file = tmp_path / "quality_data.csv"
    database_path = tmp_path / "quality_monitor.db"
    csv_file.write_text(
        "name,score\nAda,10\nAda,10\nLinus,\n",
        encoding="utf-8",
    )

    metrics = process_dataset(csv_file, database_path)

    assert metrics == {
        "row_count": 3,
        "column_count": 2,
        "null_count": 1,
        "duplicate_count": 1,
        "null_percentage": 16.666666666666664,
        "quality_status": "WARNING",
    }
    results = get_quality_results(database_path)
    assert len(results) == 1
    assert results[0]["dataset_name"] == "quality_data.csv"
    assert results[0]["row_count"] == metrics["row_count"]
    assert results[0]["null_count"] == metrics["null_count"]
    assert results[0]["quality_status"] == "WARNING"


def test_process_dataset_raises_for_empty_csv(tmp_path) -> None:
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="CSV file is empty"):
        process_dataset(csv_file, tmp_path / "quality_monitor.db")


def test_process_dataset_raises_for_missing_csv(tmp_path) -> None:
    missing_file = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError, match="CSV file not found"):
        process_dataset(missing_file, tmp_path / "quality_monitor.db")