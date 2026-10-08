# Data Quality Monitor

A Python application for monitoring the quality of CSV data.

The application will eventually calculate these metrics for a CSV file:

- Row count
- Null count
- Duplicate count
- Null percentage

The application provides a FastAPI backend, a Streamlit dashboard, and SQLite
persistence for processed CSV results.

## Project Structure

- `app/`: CSV processing, quality checks, workflows, persistence, and API code.
- `dashboard.py`: Streamlit user interface that communicates with the API.
- `tests/`: Automated tests for the application code.
- `requirements.txt`: Python dependencies for the project.

## Getting Started

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run the Application

Start the FastAPI backend in one terminal:

```powershell
uvicorn app.api:app --reload
```

Start the Streamlit dashboard in another terminal:

```powershell
streamlit run dashboard.py
```

Open the dashboard at `http://localhost:8501`. The FastAPI interactive
documentation is available at `http://127.0.0.1:8000/docs`.