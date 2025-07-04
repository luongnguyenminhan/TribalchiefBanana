# Multi-stage build với Debian slim 
FROM python:3.11-slim AS builder

# Copy uv binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install system dependencies cần thiết
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Cấu hình uv environment variables
ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_CACHE_DIR=/opt/uv-cache

# Set working directory
WORKDIR /app

# Copy requirements và cài đặt dependencies trước (cho Docker layer cache)
COPY requirements.txt .

# Install dependencies với cache mount (CPU-only PyTorch)
RUN --mount=type=cache,target=/opt/uv-cache \
    uv pip install --system torch>=2.0.0 --index-url https://download.pytorch.org/whl/cpu && \
    uv pip install --system transformers>=4.28 fastapi>=0.95.1 uvicorn[standard]>=0.20.0 pydantic>=1.10.0 requests>=2.28.0

# Copy application code
COPY . .

# Production stage với Debian slim
FROM python:3.11-slim AS production

# Install runtime dependencies  
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy uv binary
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Tạo non-root user (Debian syntax)
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -m appuser

# Set working directory
WORKDIR /app

# Copy installed packages từ builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Create cache directory for runtime model download
RUN mkdir -p /home/appuser/.cache/huggingface && \
    chown -R appuser:appgroup /home/appuser/.cache

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

