# ==============================================================================
# Dockerfile for SMMS Analytical Backend & Deep Learning Model Runner
# Python 3.12 + PyTorch + FastAPI
# ==============================================================================

FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/ai_models/src:/app/backend/app:${PYTHONPATH}"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch (CPU version for lightweight, universal container deployment)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Copy requirements
COPY backend/requirements.txt /app/backend/requirements.txt
COPY ai_models/requirements.txt /app/ai_models/requirements.txt

# Install application dependencies
RUN pip install --no-cache-dir -r /app/backend/requirements.txt && \
    pip install --no-cache-dir numpy pandas scipy scikit-learn joblib matplotlib seaborn pillow requests

# Copy application source code
COPY ai_models /app/ai_models
COPY backend /app/backend

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/docs || exit 1

# Start Uvicorn ASGI server
CMD ["python", "-m", "uvicorn", "main:app", "--app-dir", "backend/app", "--host", "0.0.0.0", "--port", "8000"]
