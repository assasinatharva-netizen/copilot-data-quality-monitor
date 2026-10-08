from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.api import app, get_database_path


@pytest.fixture
def client(tmp_path) -> Generator[TestClient]:
    database_path = tmp_path / "quality_monitor.db"
    app.dependency_overrides[get_database_path] = lambda: database_path

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_health_check_returns_running_status(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_results_returns_no_results_for_new_database(client: TestClient) -> None:
    response = client.get("/results")

    assert response.status_code == 200
    assert response.json() == []


def test_process_csv_returns_metrics_and_stores_result(client: TestClient) -> None:
    response = client.post(
        "/process",
        files={
            "file": (
                "quality_data.csv",
                b"name,score\nAda,10\nAda,10\nLinus,\n",
                "text/csv",
            )
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "row_count": 3,
        "column_count": 2,
        "null_count": 1,
        "duplicate_count": 1,
        "null_percentage": 16.666666666666664,
        "quality_status": "WARNING",
    }

    results_response = client.get("/results")
    assert results_response.json()[0]["dataset_name"] == "quality_data.csv"
    assert results_response.json()[0]["quality_status"] == "WARNING"


def test_get_results_filters_by_status_and_limits_results(client: TestClient) -> None:
    client.post(
        "/process",
        files={"file": ("pass.csv", b"name\nAda\n", "text/csv")},
    )
    client.post(
        "/process",
        files={"file": ("fail.csv", b"name,score\n,\n", "text/csv")},
    )

    response = client.get("/results", params={"quality_status": "FAIL", "limit": 1})

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 2,
            "dataset_name": "fail.csv",
            "row_count": 1,
            "column_count": 2,
            "null_count": 2,
            "duplicate_count": 0,
            "null_percentage": 100.0,
            "quality_status": "FAIL",
            "created_at": response.json()[0]["created_at"],
        }
    ]


def test_process_csv_rejects_empty_csv(client: TestClient) -> None:
    response = client.post(
        "/process",
        files={"file": ("empty.csv", b"", "text/csv")},
    )

    assert response.status_code == 400
    assert response.json()["detail"].startswith("CSV file is empty:")


def test_process_csv_requires_a_file(client: TestClient) -> None:
    response = client.post("/process")

    assert response.status_code == 422


def test_process_csv_rejects_non_csv_upload(client: TestClient) -> None:
    response = client.post(
        "/process",
        files={"file": ("quality_data.txt", b"data", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "The uploaded file must be a CSV."