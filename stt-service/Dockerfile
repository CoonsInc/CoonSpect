# FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04 #нету cudnn
# FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-devel #36gb
#о да оно работает
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04 

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64:/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    ffmpeg \
    libsndfile1 \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python3 -c "import whisperx; whisperx.load_model('turbo', device='cpu', compute_type='int8')"

COPY transcription/ /transcription
WORKDIR /transcription

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
