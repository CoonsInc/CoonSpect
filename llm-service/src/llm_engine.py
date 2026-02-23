import ollama
import os
from typing import Dict, Any
from qdrant_client import QdrantClient

class LLMEngine:
    def __init__(self):
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.client = ollama.Client(host=host)
        self.prompt_tmp = self.load_prompt()
        qdrant_host = "qdrant"
        self.qdrant = QdrantClient(host=qdrant_host, port=6333)
    
    def load_prompt(self) -> str:
        try:
            with open("prompt.txt", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "Блляяя, прикинь надо структурированный конспектик зафигачить из этого:"
    
    def summarize(self, text: str, model: str = "ministral-3:3b") -> Dict[str, Any]:
        if not text.strip():
            return {
                "summary": "", 
                "success": False,
                "error": "The text for llm is empty"
            }
        
        try:
            context_text = ""
            used_sources = set()
            
            try:
                if self.qdrant.collection_exists("coon_knowledge_base"):
                    embed_response = self.client.embeddings(
                        model="nomic-embed-text", 
                        prompt=text[:1500] 
                    )

                    embedding = embed_response["embedding"]

                    search_response = self.qdrant.query_points(
                        collection_name="coon_knowledge_base",
                        query=embedding,
                        limit=3
                    )

                    context_parts = []
                    score_threshold = 0.6

                    for hit in search_response.points:
                        if hit.score < score_threshold:
                            print(f"[RAG] Пропущен кусок с низким score: {hit.score:.3f}")
                            continue
                        
                        payload = hit.payload or {}
                        chunk_text = payload.get("page_content", "")
                        meta = payload.get("metadata", {})
                        
                        book_title = meta.get("book_title", "Неизвестный источник")
                        page = meta.get("page", "?")
                        
                        source_info = f"{book_title} (стр. {page})"
                        used_sources.add(source_info)
                        
                        context_parts.append(f"--- Источник: {source_info} (score: {hit.score:.2f}) ---\n{chunk_text}")

                    if context_parts:
                        context_text = "Дополнительная информация из базы знаний:\n" + "\n\n".join(context_parts) + "\n\n"
                    else:
                        print("[RAG] Релевантных данных в базе не найдено.")
            except Exception as rag_e:
                print(f"[RAG Warning] Ошибка поиска контекста: {rag_e}")
            
            print("контекст:\n---\n", context_text, "\n---\n")
            prompt = f"{self.prompt_tmp}\n\n[ЗАПРОС ПОЛЬЗОВАТЕЛЯ]:\n{text}\n\n[НАЙДЕННЫЙ КОНТЕКСТ]:\n{context_text}"
            
            response = self.client.generate(
                model=model,
                prompt=prompt
            )
            return {
                "summary": response["response"],
                "success": True
            }
        except Exception as e:
            return {
                "summary": "",
                "success": False,
                "error": str(e)
            }