# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy dependency file
COPY pyproject.toml README.md ./

# Install the project and dependencies using standard pip for maximum compatibility
RUN pip install .

# Copy the application code and frontend
COPY app/ ./app/
COPY frontend/ ./frontend/

# Run the application (Cloud Run will inject PORT)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
