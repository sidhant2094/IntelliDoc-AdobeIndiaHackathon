# Stage 1: Build stage
FROM python:3.10-alpine as builder

# Install build dependencies
RUN apk add --no-cache \
    build-base \
    gcc \
    python3-dev \
    musl-dev \
    tesseract-ocr-dev \
    leptonica-dev \
    g++ \
    make \
    cmake

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime image
FROM python:3.10-alpine

# Install only runtime dependencies
RUN apk add --no-cache \
    tesseract-ocr \
    leptonica \
    libstdc++

WORKDIR /app

# Copy Python from builder
COPY --from=builder /root/.local /root/.local

# Ensure scripts in .local are usable
ENV PATH="/root/.local/bin:${PATH}"

# Copy only necessary files
COPY extractor2.py .

# Create default directories
RUN mkdir -p /app/inputs /app/outputs

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Default command
CMD ["python", "extractor2.py"]