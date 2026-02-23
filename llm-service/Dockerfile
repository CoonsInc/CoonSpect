FROM ollama/ollama:latest

RUN apt-get update && apt-get install -y python3 python3-pip
RUN rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --break-system-packages --no-cache-dir -r requirements.txt

COPY src/ .

ENTRYPOINT []
CMD ["sh", "-c", "ollama serve & sleep 10 && ollama pull ministral-3:3b && ollama pull nomic-embed-text || true && exec uvicorn main:app --host 0.0.0.0 --port 8000"]
