import sqlite3
from contextlib import closing

import pytest

from app.database import (
    get_quality_results,
    initialize_database,
    insert_quality_result,
)
from app.quality_checks import QualityMetrics, QualityStatus


@pytest.fixture
def database_path(tmp_path):
    """Provide an isolated SQLite database path for each test."""
    return tmp_path / "quality_monitor.db"


def build_metrics(quality_status: QualityStatus) -> QualityMetrics:
    """Build minimal quality metrics for a persisted test result."""
    return {
        "row_count": 1,
        "column_count": 1,
        "null_count": 0,
        "duplicate_count": 0,
        "null_percentage": 0.0,
        "quality_status": quality_status,
    }


def test_initialize_database_creates_quality_results_table(tmp_path) -> None:
    database_path = tmp_path / "quality_monitor.db"

    initialize_database(database_path)

    with closing(sqlite3.connect(database_path)) as connection:
        table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
            ("quality_results",),
        ).fetchone()

    assert table == ("quality_results",)


def test_insert_and_retrieve_quality_results(tmp_path) -> None:
    database_path = tmp_path / "quality_monitor.db"
    metrics = {
        "row_count": 3,
        "column_count": 2,
        "null_count": 1,
        "duplicate_count": 1,
        "null_percentage": 16.666666666666664,
        "quality_status": "WARNING",
    }

    result_id = insert_quality_result("quality_data.csv", metrics, database_path)

    results = get_quality_results(database_path)

    assert result_id == 1
    assert results[0]["id"] == result_id
    assert results[0]["dataset_name"] == "quality_data.csv"
    assert results[0]["row_count"] == 3
    assert results[0]["column_count"] == 2
    assert results[0]["null_count"] == 1
    assert results[0]["duplicate_count"] == 1
    assert results[0]["null_percentage"] == 16.666666666666664
    assert results[0]["quality_status"] == "WARNING"
    assert results[0]["created_at"]


def test_initialize_database_migrates_existing_results_table(tmp_path) -> None:
    database_path = tmp_path / "quality_monitor.db"
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute(
                """
                CREATE TABLE quality_results (
                    id INTEGER PRIMARY KEY,
                    dataset_name TEXT NOT NULL,
                    row_count INTEGER NOT NULL,
                    column_count INTEGER NOT NULL,
                    null_count INTEGER NOT NULL,
                    duplicate_count INTEGER NOT NULL,
                    null_percentage REAL NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                INSERT INTO quality_results VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (1, "legacy.csv", 3, 2, 1, 1, 16.67, "2026-10-07 00:00:00"),
            )

    initialize_database(database_path)

    result = get_quality_results(database_path)[0]
    assert result["quality_status"] == "WARNING"


def test_get_quality_results_filters_by_quality_status(database_path) -> None:
    insert_quality_result("passed.csv", build_metrics("PASS"), database_path)
    insert_quality_result("warning.csv", build_metrics("WARNING"), database_path)
    insert_quality_result("failed.csv", build_metrics("FAIL"), database_path)

    results = get_quality_results(database_path, quality_status="WARNING")

    assert [result["dataset_name"] for result in results] == ["warning.csv"]


def test_get_quality_results_filters_by_dataset_name(database_path) -> None:
    insert_quality_result("sales_january.csv", build_metrics("PASS"), database_path)
    insert_quality_result("sales_february.csv", build_metrics("PASS"), database_path)
    insert_quality_result("inventory.csv", build_metrics("PASS"), database_path)

    results = get_quality_results(database_path, dataset_name="sales")

    assert [result["dataset_name"] for result in results] == [
        "sales_february.csv",
        "sales_january.csv",
    ]


def test_get_quality_results_returns_newest_results_first(database_path) -> None:
    insert_quality_result("first.csv", build_metrics("PASS"), database_path)
    insert_quality_result("second.csv", build_metrics("PASS"), database_path)
    insert_quality_result("third.csv", build_metrics("PASS"), database_path)

    results = get_quality_results(database_path)

    assert [result["dataset_name"] for result in results] == [
        "third.csv",
        "second.csv",
        "first.csv",
    ]


def test_get_quality_results_limits_returned_results(database_path) -> None:
    insert_quality_result("first.csv", build_metrics("PASS"), database_path)
    insert_quality_result("second.csv", build_metrics("PASS"), database_path)
    insert_quality_result("third.csv", build_metrics("PASS"), database_path)

    results = get_quality_results(database_path, limit=2)

    assert [result["dataset_name"] for result in results] == [
        "third.csv",
        "second.csv",
    ]