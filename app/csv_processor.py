"""CSV loading helpers for the data quality monitor."""

from pathlib import Path

import pandas as pd
from pandas.errors import EmptyDataError, ParserError


def load_csv(file_path: str | Path) -> pd.DataFrame:
    """Load a CSV file into a pandas DataFrame.

    Args:
        file_path: Path to the CSV file to load.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If the CSV file is empty or cannot be parsed.
    """
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"CSV file not found: {path}")

    try:
        return pd.read_csv(path)
    except EmptyDataError as error:
        raise ValueError(f"CSV file is empty: {path}") from error
    except ParserError as error:
        raise ValueError(f"Invalid CSV file: {path}") from error