# Use a minimal and secure Python base image
FROM python:3.11-slim AS base

# Set environment variables to optimize Python behavior
ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set the working directory
WORKDIR /src/app

# Install system dependencies (pin versions and avoid extra packages)
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc=12.2.0-14 \
    libpq-dev=15.2-1 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies from `requirements.txt`
COPY requirements.txt .
# hadolint ignore=DL3013
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY . .

# Define the default command (modify as needed)
CMD ["python", "-m", "src.app"]
