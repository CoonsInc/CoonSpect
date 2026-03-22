from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llm_engine import LLMEngine
import uvicorn

app = FastAPI()
llm = LLMEngine()

class TextRequest(BaseModel):
    text: str

@app.post("/summarize")
async def summarize(request: TextRequest):
    result = await llm.summarize(request.text, "ministral-3:3b")
    
    if not result.get("success"):
        raise HTTPException(
            status_code=500,
            detail={
                "error": result.get("error", "Неизвестная ошибка генерации"),
                "type": "llm_error"
            }
        )
    
    return {
        "status": "success",
        "summary": result["summary"],
    }

@app.get("/health")
async def health():
    return {"status": "ok", "service": "llm"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
