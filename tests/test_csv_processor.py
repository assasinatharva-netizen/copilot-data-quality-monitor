import pandas as pd
import pytest

from app.csv_processor import load_csv


def test_load_csv_returns_dataframe(tmp_path) -> None:
    csv_file = tmp_path / "people.csv"
    csv_file.write_text("name,score\nAda,10\nLinus,20\n", encoding="utf-8")

    dataframe = load_csv(csv_file)

    expected = pd.DataFrame({"name": ["Ada", "Linus"], "score": [10, 20]})
    pd.testing.assert_frame_equal(dataframe, expected)


def test_load_csv_raises_file_not_found_for_missing_file(tmp_path) -> None:
    missing_file = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError, match="CSV file not found"):
        load_csv(missing_file)


def test_load_csv_raises_value_error_for_invalid_csv(tmp_path) -> None:
    csv_file = tmp_path / "invalid.csv"
    csv_file.write_text('name,score\n"Ada,10\n', encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid CSV file"):
        load_csv(csv_file)


def test_load_csv_raises_value_error_for_empty_csv(tmp_path) -> None:
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="CSV file is empty"):
        load_csv(csv_file)