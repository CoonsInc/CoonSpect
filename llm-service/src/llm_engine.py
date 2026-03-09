import ollama
import os
from typing import Dict, Any
from langchain_text_splitters import RecursiveCharacterTextSplitter

class LLMEngine:
    def __init__(self):
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.client = ollama.AsyncClient(host=host)
        self.prompt_tmp = self.load_prompt()
        
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
            
            for i, chunk in enumerate(chunks):
                progress_info = f"ЧАСТЬ {i+1} ИЗ {len(chunks)}."
                
                context_instruction = ""
                if context_summary:
                    context_instruction = (
                        f"\nКРАТКОЕ СОДЕРЖАНИЕ ПРЕДЫДУЩИХ ЧАСТЕЙ (используй для понимания общего контекста, "
                        f"но НЕ повторяй в текущем конспекте):\n{context_summary}\n\nПродолжай конспектировать."
                    )
                
                prompt = f"{self.prompt_tmp}\n{context_instruction}\n{progress_info}\nТЕКСТ ЛЕКЦИИ:\n{chunk}"
                
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
                "chunks_processed": len(chunks)
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
