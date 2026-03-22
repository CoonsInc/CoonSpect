FROM nvidia/cuda:12.6.0-cudnn-runtime-ubuntu22.04 

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LD_LIBRARY_PATH="/usr/local/lib/python3.10/dist-packages/nvidia/cudnn/lib/:$LD_LIBRARY_PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --retries 5 --default-timeout=5000 -r requirements.txt

COPY src/ /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
