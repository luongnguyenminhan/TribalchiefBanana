# Multi-stage build với Alpine Linux
FROM python:3.11-alpine AS builder

# Copy uv binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install system dependencies cần thiết cho Alpine
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev \
    git \
    && rm -rf /var/cache/apk/*

# Cấu hình uv environment variables
ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_CACHE_DIR=/opt/uv-cache

# Set working directory
WORKDIR /app

# Copy requirements và cài đặt dependencies trước (cho Docker layer cache)
COPY requirements.txt .

# Install dependencies với cache mount
RUN --mount=type=cache,target=/opt/uv-cache \
    uv pip install --system -r requirements.txt

# Copy model download script và download model
COPY download_model.py .
RUN --mount=type=cache,target=/opt/uv-cache \
    --mount=type=cache,target=/root/.cache/huggingface \
    python download_model.py

# Copy application code
COPY . .

# Production stage với Alpine slim
FROM python:3.11-alpine AS production

# Install runtime dependencies
RUN apk add --no-cache \
    libffi \
    && rm -rf /var/cache/apk/*

# Copy uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Tạo non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup

# Set working directory
WORKDIR /app

# Copy installed packages từ builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy HuggingFace model cache
COPY --from=builder --chown=appuser:appgroup /root/.cache/huggingface /home/appuser/.cache/huggingface

# Copy application code
COPY --chown=appuser:appgroup . .

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    TRANSFORMERS_CACHE=/home/appuser/.cache/huggingface \
    HF_HOME=/home/appuser/.cache/huggingface \
    UV_SYSTEM_PYTHON=1

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "main.py"]

