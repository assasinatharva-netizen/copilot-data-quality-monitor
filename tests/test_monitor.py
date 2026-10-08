from app.monitor import analyze_csv


def test_analyze_csv_loads_data_and_calculates_quality_metrics(tmp_path) -> None:
    csv_file = tmp_path / "quality_data.csv"
    csv_file.write_text(
        "name,score\nAda,10\nAda,10\nLinus,\n",
        encoding="utf-8",
    )

    metrics = analyze_csv(csv_file)

    assert metrics == {
        "row_count": 3,
        "column_count": 2,
        "null_count": 1,
        "duplicate_count": 1,
        "null_percentage": 16.666666666666664,
        "quality_status": "WARNING",
    }