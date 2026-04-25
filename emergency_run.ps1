$env:PYTHONPATH = "."
& .\.venv_new\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
