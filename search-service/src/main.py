from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import traceback
import os
import uuid

app = FastAPI()


model = SentenceTransformer('intfloat/multilingual-e5-small')
qdrant = QdrantClient(host=os.getenv("QDRANT_HOST", "localhost"), port=6333)

COLLECTION_NAME = "audio_transcripts"

# Создаем коллекцию, если её нет
if not qdrant.collection_exists(COLLECTION_NAME):
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

class Segment(BaseModel):
    start: float
    end: float
    text: str

class IndexRequest(BaseModel):
    audio_id: str
    segments: List[Segment]

@app.post("/index")
async def index_audio(data: IndexRequest):
    """Принимает сегменты от WhisperX и сохраняет их в векторную базу"""
    points = []
    for i, seg in enumerate(data.segments):
        # Префикс 'passage: ' нужен для модели E5
        vector = model.encode(f"passage: {seg.text}").tolist()
        
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "audio_id": data.audio_id,
                "start": seg.start,
                "end": seg.end,
                "text": seg.text
            }
        ))
    
    qdrant.upsert(collection_name=COLLECTION_NAME, points=points)
    return {"status": "success", "indexed_segments": len(points)}

# ... остальной код ...

@app.get("/search")
async def search(audio_id: str, query: str, limit: int = 5):
    try:
        # 1. Проверяем, не отвалилась ли модель при старте
        if model is None:
            raise ValueError("Модель SentenceTransformer не загружена! Проверьте функцию lifespan.")
            
        # 2. Векторизуем запрос
        query_vector = model.encode(f"query: {query}").tolist()
        
        # 3. Строгий синтаксис фильтрации Qdrant (чтобы избежать ошибок валидации)
        qdrant_filter = Filter(
            must=[
                FieldCondition(
                    key="audio_id", 
                    match=MatchValue(value=audio_id)
                )
            ]
        )
        
        # 4. Поиск в БД (Новый синтаксис Qdrant 1.17.0+)
        search_response = qdrant.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,           # ВАЖНО: раньше было query_vector=..., теперь просто query=...
            query_filter=qdrant_filter,
            limit=limit
        )
        
        results = [
            {
                "score": res.score,
                "start": res.payload["start"],
                "end": res.payload["end"],
                "text": res.payload["text"]
            } for res in search_response.points
        ]
        return {"results": results}

    except Exception as e:
        # Захватываем полный стек ошибки
        error_trace = traceback.format_exc()
        
        # Печатаем в консоль принудительно
        print("!!! КРИТИЧЕСКАЯ ОШИБКА В ПОИСКЕ !!!")
        print(error_trace)
        
        # Возвращаем ошибку прямо в Postman!
        raise HTTPException(status_code=500, detail={
            "error": str(e),
            "traceback": error_trace.splitlines()
        })