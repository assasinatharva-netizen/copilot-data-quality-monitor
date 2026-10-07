"""SQLite persistence for data-quality monitoring results."""

import sqlite3
from pathlib import Path
from typing import TypedDict

from app.quality_checks import QualityMetrics

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
    created_at: str


def initialize_database(database_path: str | Path = DATABASE_PATH) -> None:
    """Create the quality-results database table when it does not exist."""
    with sqlite3.connect(database_path) as connection:
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
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def insert_quality_result(
    dataset_name: str,
    metrics: QualityMetrics,
    database_path: str | Path = DATABASE_PATH,
) -> int:
    """Store quality metrics for a dataset and return the new result ID."""
    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO quality_results (
                dataset_name,
                row_count,
                column_count,
                null_count,
                duplicate_count,
                null_percentage
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                dataset_name,
                metrics["row_count"],
                metrics["column_count"],
                metrics["null_count"],
                metrics["duplicate_count"],
                metrics["null_percentage"],
            ),
        )
        return int(cursor.lastrowid)


def get_quality_results(
    database_path: str | Path = DATABASE_PATH,
) -> list[QualityResult]:
    """Retrieve all stored quality results in insertion order."""
    initialize_database(database_path)

    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT
                id,
                dataset_name,
                row_count,
                column_count,
                null_count,
                duplicate_count,
                null_percentage,
                created_at
            FROM quality_results
            ORDER BY id
            """
        ).fetchall()

    return [dict(row) for row in rows]