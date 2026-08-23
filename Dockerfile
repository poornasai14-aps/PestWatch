# PestWatch — cloud deployment image (CPU-only, self-contained).
FROM python:3.12-slim

WORKDIR /app

# OpenCV (headless) runtime libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 libgomp1 \
 && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch first (avoids pulling ~2GB CUDA), then the rest.
RUN pip install --no-cache-dir torch torchvision \
      --index-url https://download.pytorch.org/whl/cpu
COPY requirements-deploy.txt .
RUN pip install --no-cache-dir -r requirements-deploy.txt

# App code, trained models, and web UI
COPY backend/ backend/
COPY frontend/ frontend/
COPY models/ models/

ENV PYTHONUNBUFFERED=1 \
    HF_HUB_DISABLE_TELEMETRY=1 \
    YOLO_CONFIG_DIR=/tmp/Ultralytics \
    MPLCONFIGDIR=/tmp/mpl \
    PESTWATCH_DB=/tmp/pestwatch/pestwatch.db \
    PESTWATCH_UPLOADS=/tmp/pestwatch/uploads

# Hugging Face Spaces uses 7860; Render/Railway inject $PORT.
EXPOSE 7860
CMD ["sh", "-c", "uvicorn backend.app:app --host 0.0.0.0 --port ${PORT:-7860}"]
