"""FastAPI endpoints for the data-quality monitor."""

import shutil
import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile

from app.database import DATABASE_PATH, QualityResult, get_quality_results
from app.quality_checks import QualityMetrics, QualityStatus
from app.workflow import process_dataset

app = FastAPI(title="Data Quality Monitor API")


def get_database_path() -> Path:
    """Provide the database path used by API endpoints."""
    return DATABASE_PATH


@app.get("/health")
def health_check() -> dict[str, str]:
    """Report whether the application is running."""
    return {"status": "ok"}


@app.get("/results")
def get_results(
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    quality_status: QualityStatus | None = None,
    dataset_name: str | None = None,
    database_path: Path = Depends(get_database_path),
) -> list[QualityResult]:
    """Return recent persisted results, optionally filtered by status or name."""
    return get_quality_results(
        database_path,
        limit=limit,
        quality_status=quality_status,
        dataset_name=dataset_name,
    )


@app.post("/process")
async def process_csv(
    file: UploadFile = File(...),
    database_path: Path = Depends(get_database_path),
) -> QualityMetrics:
    """Process an uploaded CSV file and store its quality metrics."""
    temporary_path: Path | None = None

    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="A CSV file is required.")

        dataset_name = Path(file.filename).name
        if Path(dataset_name).suffix.lower() != ".csv":
            raise HTTPException(status_code=400, detail="The uploaded file must be a CSV.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temporary_file:
            temporary_path = Path(temporary_file.name)
            shutil.copyfileobj(file.file, temporary_file)

        try:
            return process_dataset(
                temporary_path,
                database_path,
                dataset_name=dataset_name,
            )
        except FileNotFoundError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        await file.close()