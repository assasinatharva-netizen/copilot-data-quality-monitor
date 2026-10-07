import pandas as pd

from app.quality_checks import calculate_quality_metrics


def test_calculate_quality_metrics_for_normal_dataframe() -> None:
    dataframe = pd.DataFrame({"name": ["Ada", "Linus"], "score": [10, 20]})

    metrics = calculate_quality_metrics(dataframe)

    assert metrics == {
        "row_count": 2,
        "column_count": 2,
        "null_count": 0,
        "duplicate_count": 0,
        "null_percentage": 0.0,
    }


def test_calculate_quality_metrics_counts_null_values() -> None:
    dataframe = pd.DataFrame({"name": ["Ada", None], "score": [None, 20]})

    metrics = calculate_quality_metrics(dataframe)

    assert metrics["null_count"] == 2
    assert metrics["null_percentage"] == 50.0


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
    }