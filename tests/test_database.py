import sqlite3

from app.database import (
    get_quality_results,
    initialize_database,
    insert_quality_result,
)


def test_initialize_database_creates_quality_results_table(tmp_path) -> None:
    database_path = tmp_path / "quality_monitor.db"

    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
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
    assert results[0]["created_at"]