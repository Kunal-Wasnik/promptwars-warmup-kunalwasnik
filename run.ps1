$env:PYTHONPATH = "."
$env:UV_PROJECT_ENVIRONMENT = ".venv_new"
uv run uvicorn app.main:app --reload --port 8000
