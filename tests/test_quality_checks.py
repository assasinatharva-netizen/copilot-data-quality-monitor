import pandas as pd
import pytest

from app.quality_checks import calculate_quality_metrics, calculate_quality_status


def test_calculate_quality_metrics_for_normal_dataframe() -> None:
    dataframe = pd.DataFrame({"name": ["Ada", "Linus"], "score": [10, 20]})

    metrics = calculate_quality_metrics(dataframe)

    assert metrics == {
        "row_count": 2,
        "column_count": 2,
        "null_count": 0,
        "duplicate_count": 0,
        "null_percentage": 0.0,
        "quality_status": "PASS",
    }


def test_calculate_quality_metrics_counts_null_values() -> None:
    dataframe = pd.DataFrame({"name": ["Ada", None], "score": [None, 20]})

    metrics = calculate_quality_metrics(dataframe)

    assert metrics["null_count"] == 2
    assert metrics["null_percentage"] == 50.0
    assert metrics["quality_status"] == "FAIL"


def test_calculate_quality_metrics_counts_duplicate_rows() -> None:
    dataframe = pd.DataFrame({"name": ["Ada", "Ada", "Linus"], "score": [10, 10, 20]})

    metrics = calculate_quality_metrics(dataframe)

    assert metrics["duplicate_count"] == 1


def test_calculate_quality_metrics_handles_empty_dataframe() -> None:
    dataframe = pd.DataFrame(columns=["name", "score"])

    metrics = calculate_quality_metrics(dataframe)

    assert metrics == {
        "row_count": 0,
        "column_count": 2,
        "null_count": 0,
        "duplicate_count": 0,
        "null_percentage": 0.0,
        "quality_status": "PASS",
    }


@pytest.mark.parametrize(
    ("null_percentage", "expected_status"),
    [(0.0, "PASS"), (5.0, "WARNING"), (20.0, "WARNING"), (20.1, "FAIL")],
)
def test_calculate_quality_status(
    null_percentage: float,
    expected_status: str,
) -> None:
    assert calculate_quality_status(null_percentage) == expected_status


def test_calculate_quality_metrics_returns_warning_status() -> None:
    dataframe = pd.DataFrame(
        {"first": [None, 1, 2, 3, 4], "second": [1, 2, 3, 4, 5]}
    )

    metrics = calculate_quality_metrics(dataframe)

    assert metrics["null_percentage"] == 10.0
    assert metrics["quality_status"] == "WARNING"