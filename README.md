# Data Quality Monitor

A small Python learning project for monitoring the quality of CSV data.

The application will eventually calculate these metrics for a CSV file:

- Row count
- Null count
- Duplicate count
- Null percentage

This first step only establishes the project structure. It does not yet include
CSV-processing logic, a web interface, a database, containers, or AI features.

## Project Structure

- `app/`: Application package. Future CSV quality-monitoring code will live here.
- `tests/`: Tests for the application code.
- `requirements.txt`: Python dependencies for the project. It is intentionally
	empty until the application needs a library.

## Getting Started

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```