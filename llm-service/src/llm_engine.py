import ollama
import os
import json
from typing import Dict, Any, List
from qdrant_client import QdrantClient
from langchain_text_splitters import RecursiveCharacterTextSplitter

class LLMEngine:
    def __init__(self):
        self.client = ollama.AsyncClient(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
        self.qdrant = QdrantClient(host="qdrant", port=6333)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=5000,
            chunk_overlap=500
        )

    async def summarize(self, text: str, model: str = "qwen2.5:3b") -> Dict[str, Any]:
        chunks = self.text_splitter.split_text(text)
        all_extracted_facts = []
        used_sources = set()

        for i, chunk in enumerate(chunks):
            context = await self._get_reranked_context(chunk)
            if context:
                used_sources.update([c['meta'] for c in context])

            facts = await self._extract_facts(chunk, context, model)
            all_extracted_facts.append(facts)

        final_summary = await self._build_final_summary(all_extracted_facts, model)

        return {
            "summary": final_summary,
            "success": True,
            "sources": list(used_sources)
        }

    async def _extract_facts(self, chunk: str, context: List[Dict], model: str) -> str:
        """Извлекает только суть без 'воды' и вступлений"""
        context_str = "\n".join([c['text'] for c in context])
        prompt = f"""
        ИЗВЛЕКИ ТЕХНИЧЕСКИЕ ФАКТЫ.
        Контекст из книг: {context_str}
        Текст лекции: {chunk}

        ЗАДАЧА:
        Выпиши только ключевые тезисы, определения и алгоритмы. 
        НЕ ПИШИ вступлений. НЕ ПИШИ 'В этом отрывке...'. 
        Только список фактов.
        Если данные из книг дополняют лекцию — включи их в тезис в скобках.
        """
        res = await self.client.generate(
            model=model, 
            prompt=prompt,
            options={
                "num_ctx": 8192 
            }
        )
        return res['response']

    async def _build_final_summary(self, facts: List[str], model: str) -> str:
        """Один раз превращает гору фактов в красивый Markdown"""
        full_facts = "\n---\n".join(facts)
        prompt = f"""
        ТЫ - ЭКСПЕРТ-РЕЦЕНЗЕНТ.
        Перед тобой набор сырых фактов из лекции:
        {full_facts}

        ЗАДАЧА:
        Составь из этого ОДИН цельный технический конспект.
        Используй заголовки ##, разделы 'Ключевые понятия', 'Детальный разбор', 'Итог'.
        Удали повторы. Сделай текст логичным и бесшовным.
        Выходной язык: Русский.
        """
        res = await self.client.generate(
            model=model, 
            prompt=prompt,
            options={
                "num_ctx": 8192 
            }
        )
        return res['response']

    async def _get_reranked_context(self, chunk: str) -> List[Dict]:
        """Умный поиск: ищем и фильтруем мусор"""
        try:
            emb = await self.client.embeddings(model="nomic-embed-text", prompt=chunk[:1000])
            search = self.qdrant.query_points(
                collection_name="coon_knowledge_base",
                query=emb["embedding"],
                limit=5
            )
            
            valid_points = []
            for hit in search.points:
                if hit.score > 0.85: 
                    valid_points.append({
                        "text": hit.payload.get("page_content", ""),
                        "meta": f"{hit.payload['metadata'].get('book_title')} (стр. {hit.payload['metadata'].get('page')})"
                    })
            return valid_points
        except:
            return []