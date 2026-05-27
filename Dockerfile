FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy project files
COPY pyproject.toml pyproject.toml

# Install dependencies (no root, no dev)
RUN poetry config virtualenvs.in-project true && \
    poetry install --no-root --no-directory

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["poetry", "run", "python", "main.py"]
