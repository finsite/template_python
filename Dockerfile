# ---- Base image for building dependencies ----
    FROM python:3.11-slim AS builder

    WORKDIR /src/app
    
    # Install system dependencies
    RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        && rm -rf /var/lib/apt/lists/*
    
    # Install dependencies
    COPY pyproject.toml poetry.lock requirements.txt requirements-dev.txt ./
    RUN pip install --no-cache-dir --upgrade pip \
        && pip install --no-cache-dir -r requirements.txt
    
    # ---- Final runtime image ----
    FROM python:3.11-slim AS runtime
    
    WORKDIR /src/app
    
    # Copy installed dependencies from builder stage
    COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
    
    # Copy application code
    COPY . .
    
    # Define entrypoint
    CMD ["python", "-m", "src.app"]
    