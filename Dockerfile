# # Use a minimal and secure Python base image
# FROM python:3.11-slim AS base

# # Set environment variables to optimize Python behavior
# ENV PYTHONUNBUFFERED=1 \
#     PYTHONFAULTHANDLER=1 \
#     PIP_NO_CACHE_DIR=1 \
#     PIP_DISABLE_PIP_VERSION_CHECK=1

# # Set the working directory
# WORKDIR /src/app

# # Install system dependencies (pin versions and avoid extra packages)
# # hadolint ignore=DL3008
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     gcc=12.2.0-14 \
#     libpq-dev=15.2-1 \
#     && rm -rf /var/lib/apt/lists/*

# # Copy and install dependencies from `requirements.txt`
# COPY requirements.txt .
# # hadolint ignore=DL3013
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the application source code
# COPY . .

# # Define the default command (modify as needed)
# CMD ["python", "-m", "src.app"]
# Stage 1: Build dependencies in a separate layer
FROM python:3.11-slim AS builder

# Set environment variables to optimize Python behavior
ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set the working directory
WORKDIR /src/app

# Install system dependencies (Dynamically get latest versions)
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies separately for better Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final runtime image (Minimal and Secure)
FROM python:3.11-slim AS runtime

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /src/app

# Create a non-root user for security
RUN groupadd -r app && useradd --no-log-init -r -g app appuser

# Copy dependencies from the builder stage (avoid reinstalling in final image)
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:app /src/app

# Switch to the non-root user
USER appuser

# Define the default command
CMD ["python", "-m", "src.app"]
