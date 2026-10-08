"""SQLite persistence for data-quality monitoring results."""

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import TypedDict

from app.quality_checks import QualityMetrics, QualityStatus

DATABASE_PATH = Path(__file__).resolve().parent.parent / "quality_monitor.db"


class QualityResult(TypedDict):
    """A persisted data-quality result."""

    id: int
    dataset_name: str
    row_count: int
    column_count: int
    null_count: int
    duplicate_count: int
    null_percentage: float
    quality_status: str
    created_at: str


def initialize_database(database_path: str | Path = DATABASE_PATH) -> None:
    """Create the quality-results database table when it does not exist."""
    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS quality_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_name TEXT NOT NULL,
                    row_count INTEGER NOT NULL,
                    column_count INTEGER NOT NULL,
                    null_count INTEGER NOT NULL,
                    duplicate_count INTEGER NOT NULL,
                    null_percentage REAL NOT NULL,
                    quality_status TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            columns = {
                row[1]
                for row in connection.execute("PRAGMA table_info(quality_results)")
            }
            if "quality_status" not in columns:
                connection.execute(
                    "ALTER TABLE quality_results "
                    "ADD COLUMN quality_status TEXT NOT NULL DEFAULT 'PASS'"
                )
                connection.execute(
                    """
                    UPDATE quality_results
                    SET quality_status = CASE
                        WHEN null_percentage < 5 THEN 'PASS'
                        WHEN null_percentage <= 20 THEN 'WARNING'
                        ELSE 'FAIL'
                    END
                    """
                )


def insert_quality_result(
    dataset_name: str,
    metrics: QualityMetrics,
    database_path: str | Path = DATABASE_PATH,
) -> int:
    """Store quality metrics for a dataset and return the new result ID."""
    initialize_database(database_path)

    with closing(sqlite3.connect(database_path)) as connection:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO quality_results (
                    dataset_name,
                    row_count,
                    column_count,
                    null_count,
                    duplicate_count,
                    null_percentage,
                    quality_status
                )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    dataset_name,
                    metrics["row_count"],
                    metrics["column_count"],
                    metrics["null_count"],
                    metrics["duplicate_count"],
                    metrics["null_percentage"],
                    metrics["quality_status"],
                ),
            )
            return int(cursor.lastrowid)


def get_quality_results(
    database_path: str | Path = DATABASE_PATH,
    limit: int = 100,
    quality_status: QualityStatus | None = None,
    dataset_name: str | None = None,
) -> list[QualityResult]:
    """Retrieve recent quality results, optionally filtered by status or name."""
    initialize_database(database_path)

    conditions: list[str] = []
    values: list[str | int] = []
    if quality_status is not None:
        conditions.append("quality_status = ?")
        values.append(quality_status)
    if dataset_name:
        conditions.append("dataset_name LIKE ?")
        values.append(f"%{dataset_name}%")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    values.append(limit)

    with closing(sqlite3.connect(database_path)) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            f"""
            SELECT
                id,
                dataset_name,
                row_count,
                column_count,
                null_count,
                duplicate_count,
                null_percentage,
                quality_status,
                created_at
            FROM quality_results
            {where_clause}
            ORDER BY id DESC
            LIMIT ?
            """,
            values,
        ).fetchall()

    return [dict(row) for row in rows]