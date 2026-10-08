"""Streamlit dashboard for the Data Quality Monitor API."""

import os
from typing import Any

import pandas as pd
import requests
import streamlit as st

API_BASE_URL = os.getenv("DATA_QUALITY_API_URL", "http://127.0.0.1:8000")
REQUEST_TIMEOUT_SECONDS = 30
STATUS_ORDER = ["PASS", "WARNING", "FAIL"]


def get_error_message(error: requests.RequestException) -> str:
    """Convert an API exception into a message that helps the user recover."""
    if isinstance(error, requests.ConnectionError):
        return "The API is unavailable. Start FastAPI at http://127.0.0.1:8000."
    if isinstance(error, requests.Timeout):
        return "The API took too long to respond. Try again in a moment."

    response = error.response
    if response is not None:
        try:
            return str(response.json().get("detail", "The API rejected the request."))
        except ValueError:
            return "The API returned an unexpected error response."
    return "Unable to reach the API."


@st.cache_data(ttl=15, show_spinner=False)
def get_historical_results(
    limit: int,
    quality_status: str | None,
    dataset_name: str,
) -> list[dict[str, Any]]:
    """Retrieve persisted quality results from the FastAPI backend."""
    parameters: dict[str, str | int] = {"limit": limit}
    if quality_status:
        parameters["quality_status"] = quality_status
    if dataset_name:
        parameters["dataset_name"] = dataset_name

    response = requests.get(
        f"{API_BASE_URL}/results",
        params=parameters,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def process_uploaded_csv(
    uploaded_file: st.runtime.uploaded_file_manager.UploadedFile,
) -> dict[str, Any]:
    """Send an uploaded CSV to the FastAPI backend and return its metrics."""
    response = requests.post(
        f"{API_BASE_URL}/process",
        files={
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                uploaded_file.type or "text/csv",
            )
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def render_quality_status(status: str) -> None:
    """Render the completeness status with color and a textual explanation."""
    if status == "PASS":
        st.success("PASS - Null percentage is below 5%.")
    elif status == "WARNING":
        st.warning("WARNING - Null percentage is between 5% and 20%.")
    else:
        st.error("FAIL - Null percentage is above 20%.")


def render_latest_run() -> None:
    """Render the latest successfully processed dataset from session state."""
    latest_run = st.session_state.get("latest_run")
    if latest_run is None:
        return

    metrics = latest_run["metrics"]
    st.subheader("Latest Run")
    status_column, summary_column = st.columns([1, 3])
    with status_column:
        st.metric("Completeness Status", metrics["quality_status"])
        render_quality_status(metrics["quality_status"])
    with summary_column:
        st.caption(f"Dataset: {latest_run['dataset_name']}")
        metric_columns = st.columns(5)
        metric_columns[0].metric("Rows", f"{metrics['row_count']:,}")
        metric_columns[1].metric("Columns", f"{metrics['column_count']:,}")
        metric_columns[2].metric("Nulls", f"{metrics['null_count']:,}")
        metric_columns[3].metric("Duplicates", f"{metrics['duplicate_count']:,}")
        metric_columns[4].metric("Null Percentage", f"{metrics['null_percentage']:.2f}%")


def render_historical_results(results: list[dict[str, Any]]) -> None:
    """Render result summaries, charts, and a table for historical runs."""
    if not results:
        st.info("No datasets have been processed yet. Upload a CSV to create the first result.")
        return

    dataframe = pd.DataFrame(results)
    dataframe["created_at"] = pd.to_datetime(dataframe["created_at"])
    dataframe = dataframe.sort_values("created_at")

    status_counts = dataframe["quality_status"].value_counts().reindex(
        STATUS_ORDER,
        fill_value=0,
    )
    summary_columns = st.columns(4)
    summary_columns[0].metric("Runs", len(dataframe))
    summary_columns[1].metric("Pass", int(status_counts["PASS"]))
    summary_columns[2].metric("Warning", int(status_counts["WARNING"]))
    summary_columns[3].metric("Fail", int(status_counts["FAIL"]))

    chart_column, trend_column = st.columns(2)
    with chart_column:
        st.caption("Status Distribution")
        st.bar_chart(status_counts)
    with trend_column:
        st.caption("Null Percentage Over Time")
        st.line_chart(dataframe.set_index("created_at")[["null_percentage"]])

    display_dataframe = dataframe.sort_values("created_at", ascending=False)
    display_dataframe["created_at"] = display_dataframe["created_at"].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    st.dataframe(display_dataframe, use_container_width=True, hide_index=True)


def main() -> None:
    """Render the Data Quality Monitor dashboard."""
    st.set_page_config(page_title="Data Quality Monitor", layout="wide")
    st.title("Data Quality Monitor")
    st.caption("Upload CSV datasets, review completeness status, and monitor quality over time.")

    with st.sidebar:
        st.header("Historical Results")
        status_filter = st.selectbox("Status", ["All", *STATUS_ORDER])
        dataset_filter = st.text_input("Dataset name contains")
        result_limit = st.selectbox("Recent runs", [25, 50, 100, 250], index=2)
        if st.button("Refresh historical data"):
            get_historical_results.clear()

    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    if st.button(
        "Process uploaded CSV",
        type="primary",
        disabled=uploaded_file is None,
    ):
        try:
            with st.spinner("Processing CSV and storing quality results..."):
                metrics = process_uploaded_csv(uploaded_file)
            st.session_state["latest_run"] = {
                "dataset_name": uploaded_file.name,
                "metrics": metrics,
            }
            get_historical_results.clear()
            st.rerun()
        except requests.RequestException as error:
            st.error(f"Unable to process the CSV: {get_error_message(error)}")

    render_latest_run()

    st.subheader("Historical Results")
    try:
        with st.spinner("Loading historical results..."):
            results = get_historical_results(
                result_limit,
                None if status_filter == "All" else status_filter,
                dataset_filter,
            )
        render_historical_results(results)
    except requests.RequestException as error:
        st.error(f"Unable to retrieve historical results: {get_error_message(error)}")


if __name__ == "__main__":
    main()