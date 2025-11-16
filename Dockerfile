# --- STAGE 1: Builder ---
# Base image
FROM python:3.12-slim as builder

# Create a virtual environment
RUN python -m venv /opt/venv

# Set the virtual environment as the current location
ENV PATH=/opt/venv/bin:$PATH

# Set the working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1

# Install minimal system dependencies needed to build packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        libpango1.0-dev \
        libcairo2-dev \
        libgdk-pixbuf-2.0-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file to the app dir app/requirements.txt
COPY requirements.txt . 

# Build wheels in a temp dir
RUN pip install --upgrade pip  && \
    pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt


# --- STAGE 2: Final Image ---
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1

# Install only runtime system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libcairo2 \
        libgdk-pixbuf-2.0-0 \
        netcat-openbsd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy wheels from builder stage
COPY --from=builder /wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install dependencies from wheels
RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Copy source code
COPY . . 

# Make scripts executable
RUN chmod +x ./deployment/docker-run && \
    chmod +x ./deployment/celery

CMD ["./deployment/docker-run"]