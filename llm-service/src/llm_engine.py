import ollama
import os
from typing import Dict, Any
from qdrant_client import QdrantClient
from langchain_text_splitters import RecursiveCharacterTextSplitter

class LLMEngine:
    def __init__(self):
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.client = ollama.AsyncClient(host=host)
        self.prompt_tmp = self.load_prompt()
        
        qdrant_host = "qdrant"
        self.qdrant = QdrantClient(host=qdrant_host, port=6333)
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=8000,
            chunk_overlap=400,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def load_prompt(self) -> str:
        try:
            with open("prompt.txt", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "Блляяя, прикинь надо структурированный конспектик зафигачить из этого:"
    
    async def summarize(self, text: str, model: str = "ministral-3:3b") -> Dict[str, Any]:
        """Основной метод для генерации конспекта"""
        if not text.strip():
            return {
                "summary": "", 
                "success": False,
                "error": "The text for llm is empty"
            }
        
        try:
            chunks = self.text_splitter.split_text(text)
            full_summary = []
            context_summary = ""
            used_sources = set()
            
            for i, chunk in enumerate(chunks):
                progress_info = f"ЧАСТЬ {i+1} ИЗ {len(chunks)}."
                
                context_text = ""
                try:
                    if self.qdrant.collection_exists("coon_knowledge_base"):
                        embed_response = await self.client.embeddings(
                            model="nomic-embed-text", 
                            prompt=chunk[:1500]
                        )

                        embedding = embed_response["embedding"]

                        search_response = self.qdrant.query_points(
                            collection_name="coon_knowledge_base",
                            query=embedding,
                            limit=3
                        )

                        context_parts = []
                        score_threshold = 0.91

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
                            
                            rag_chunk = f"--- Источник: {source_info} (score: {hit.score:.2f}) ---\n{chunk_text}"
                            print(rag_chunk)
                            context_parts.append(rag_chunk)

                        if context_parts:
                            context_text = "Дополнительная информация из базы знаний:\n" + "\n\n".join(context_parts) + "\n\n"
                        else:
                            print(f"[RAG] Для части {i+1} релевантных данных не найдено.")
                except Exception as rag_e:
                    print(f"[RAG Warning] Ошибка поиска контекста: {rag_e}")
                
                context_instruction = ""
                if context_summary:
                    context_instruction = (
                        f"\nКРАТКОЕ СОДЕРЖАНИЕ ПРЕДЫДУЩИХ ЧАСТЕЙ (используй для понимания общего контекста, "
                        f"но НЕ повторяй в текущем конспекте):\n{context_summary}\n\nПродолжай конспектировать."
                    )
                
                prompt = f"{self.prompt_tmp}\n{context_instruction}\n{context_text}\n{progress_info}\nТЕКСТ ЛЕКЦИИ:\n{chunk}"
                
                response = await self.client.generate(
                    model=model,
                    prompt=prompt
                )
                chunk_result = response["response"]
                full_summary.append(chunk_result)
                
                if len(chunks) > 1 and i < len(chunks) - 1:
                    context_summary = await self._get_brief_context(chunk_result, model)
                    
            return {
                "summary": "\n\n---\n\n".join(full_summary),
                "success": True,
                "chunks_processed": len(chunks),
            }
            
        except Exception as e:
            return {
                "summary": "",
                "success": False,
                "error": str(e)
            }

    async def _get_brief_context(self, text: str, model: str) -> str:
        """Генерируем выжимку предыдущей закинутой части"""
        try:
            prompt = f"Кратко (в 3-4 предложениях) опиши суть этого фрагмента лекции: {text[:2000]}"
            res = await self.client.generate(model=model, prompt=prompt)
            return res["response"]
        except:
            return ""