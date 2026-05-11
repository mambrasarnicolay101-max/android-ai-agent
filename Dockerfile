# NOIR SOVEREIGN v14.0 COMMANDER — VPS Docker Core
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies directly to avoid requirement mismatches
RUN pip install --no-cache-dir \
    requests fastapi uvicorn python-dotenv websockets chromadb \
    numpy pandas Pillow opencv-python-headless scikit-image \
    playwright youtube-transcript-api beautifulsoup4 \
    pycryptodome paramiko scp httpx docker gunicorn

# Setup Playwright Browsers
RUN playwright install --with-deps chromium

# Install CPU-only AI libraries to save disk space
RUN pip install --no-cache-dir \
    torch torchvision --extra-index-url https://download.pytorch.org/whl/cpu \
    sentence-transformers faiss-cpu accelerate

# Copy source code
COPY . .

# Default command (overridden by docker-compose)
CMD ["python", "noir-vps/brain.py"]
