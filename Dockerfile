# Use official Python image
FROM python:3.12-slim

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies without creating a virtual environment (better for containers)
RUN uv pip install --system -r pyproject.toml

# Copy the application code
COPY app/ ./app/
COPY frontend/ ./frontend/

# Expose the port (Cloud Run sets PORT env var)
EXPOSE 8080

# Run the application (Cloud Run will inject PORT)
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
