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
            last_paragraph = ""
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
                        score_threshold = 0.87 

                        for hit in search_response.points:
                            if hit.score < score_threshold:
                                continue
                            
                            payload = hit.payload
                            main_text = payload.get("page_content", "")
                            meta = payload.get("metadata", {})
                            
                            expanded_text = main_text
                            neighbor_ids = []
                            if meta.get("prev_id"): neighbor_ids.append(meta["prev_id"])
                            if meta.get("next_id"): neighbor_ids.append(meta["next_id"])
                            
                            if neighbor_ids:
                                neighbors = self.qdrant.retrieve(
                                    collection_name="coon_knowledge_base",
                                    ids=neighbor_ids
                                )
                                prev_t = next((n.payload["page_content"] for n in neighbors if n.id == meta.get("prev_id")), "")
                                next_t = next((n.payload["page_content"] for n in neighbors if n.id == meta.get("next_id")), "")
                                expanded_text = f"{prev_t}\n{main_text}\n{next_t}".strip()

                            source_info = f"{meta.get('book_title')} (стр. {meta.get('page')})"
                            used_sources.add(source_info)
                            rag_chunk = f"--- Источник: {source_info} (score: {hit.score:.2f}) ---\n{expanded_text}"
                            print(rag_chunk)
                            context_parts.append(rag_chunk)

                        if context_parts:
                            context_text = "Дополнительная информация из книг:\n" + "\n\n".join(context_parts) + "\n\n"
                except Exception as rag_e:
                    print(f"[RAG Warning] Ошибка поиска контекста: {rag_e}")
                
                context_instruction = ""
                if i > 0:
                    context_instruction = (
                        "ВНИМАНИЕ: Это ПРОДОЛЖЕНИЕ лекции.\n"
                        f"О чем шла речь в предыдущих частях (используй для понимания контекста):\n{context_summary}\n\n"
                        f"ТОЧНЫЙ ТЕКСТ, на котором ты закончил предыдущую часть:\n\"{last_paragraph}\"\n\n"
                        "ПРАВИЛО: ПРОДОЛЖАЙ конспект ровно с того места, где остановился. "
                        "НЕ пиши 'Продолжение конспекта'. Сразу выдавай следующий заголовок или абзац!"
                    )
                else:
                    context_instruction = "Это НАЧАЛО лекции. Сделай красивый заглавный заголовок (##) по теме фрагмента и начни конспект."
                
                prompt = f"{self.prompt_tmp}\n{context_instruction}\n{context_text}\n{progress_info}\nТЕКСТ ЛЕКЦИИ:\n{chunk}"
                
                response = await self.client.chat(
                    model=model,
                    messages=[
                        {'role': 'system', 'content': self.prompt_tmp},
                        {'role': 'user', 'content': f"Context: {context_instruction}\n\nLecture part: {chunk}"}
                    ],
                    options={"temperature": 0.2}
                )
                chunk_result = response['message']['content'].strip()
                full_summary.append(chunk_result)
                
                if i < len(chunks) - 1:
                    paragraphs = [p for p in chunk_result.split("\n") if p.strip()]
                    last_paragraph = paragraphs[-1] if paragraphs else ""
                    
                    context_summary = await self._update_brief_context(context_summary, chunk_result, model)
                    
            final_text = "\n\n".join(full_summary)
            
            if len(chunks) > 1 and context_summary:
                final_conclusion = await self._generate_final_conclusion(context_summary, model)
                if final_conclusion:
                    final_text += f"\n\n## 🎓 Итоги и выводы\n{final_conclusion}"
                    
            return {
                "summary": final_text,
                "success": True,
                "chunks_processed": len(chunks),
                "sources": list(used_sources)
            }
            
        except Exception as e:
            return {
                "summary": "",
                "success": False,
                "error": str(e)
            }

    async def _update_brief_context(self, current_summary: str, new_chunk_result: str, model: str) -> str:
        """Динамически обновляет общее понимание хода лекции"""
        try:
            text_to_summarize = new_chunk_result[-2500:] 
            
            prompt = (
                "Опиши в 2-3 предложениях самую суть этого фрагмента конспекта:\n"
                f"{text_to_summarize}\n\n"
            )
            
            if current_summary:
                prompt += (
                    f"Ранее в лекции обсуждалось: {current_summary}\n"
                    "Сложи старое и новое вместе в один связный абзац (максимум 5 предложений), "
                    "чтобы получился краткий пересказ всей лекции до текущего момента."
                )
                
            res = await self.client.generate(model=model, prompt=prompt)
            return res["response"].strip()
        except:
            return current_summary

    async def _generate_final_conclusion(self, full_context: str, model: str) -> str:
        """Генерирует единый красивый вывод в самом конце"""
        try:
            prompt = (
                "На основе этого краткого содержания всей лекции напиши красивый итоговый вывод "
                "и выдели 3-5 главных тезисов (буллитами):\n\n"
                f"{full_context}\n\n"
                "Выведи ТОЛЬКО тезисы и вывод. Без слов 'Вот вывод'."
            )
            res = await self.client.generate(model=model, prompt=prompt)
            return res["response"].strip()
        except:
            return ""