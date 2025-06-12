# --- STAGE 1: Builder ---
# Base image
FROM python:3.12-slim as builder

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
        libgdk-pixbuf2.0-dev && \
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
        libgdk-pixbuf2.0-0 \
        netcat-openbsd \
        curl && \ 
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

# Create logs directory and set permissions
RUN mkdir -p /app/logs && \
    touch /app/logs/clothing_store.log &&  \
    chmod -R 777 /app/logs/clothing_store.log 

#NOTE: Had to do this cos i don't want compose in imahge but need entrypoint.sh and don't wanna mess up the main dir with files
RUN mv /app/compose/dev/entrypoint.sh /entrypoint.sh && \
    rm -rf /app/compose

# Make scripts executable
RUN chmod +x /entrypoint.sh wait-for-it.sh
    
# Set the entrypoint
ENTRYPOINT ["/entrypoint.sh"]