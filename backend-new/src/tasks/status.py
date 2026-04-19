from enum import StrEnum

class TaskStatus(StrEnum):
    STARTING = "starting"
    UPLOADING = "uploading"
    STT = "stt"
    RAG = "rag"
    LLM = "llm"
    SAVING = "saving"
    FINISH = "finish"
