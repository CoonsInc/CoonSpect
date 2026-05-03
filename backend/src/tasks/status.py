from enum import StrEnum

class TaskStatus(StrEnum):
    STARTING = "starting"
    UPLOADING = "uploading"
    STT = "stt"
    RAG = "rag"
    LLM = "llm"
    SAVING = "saving"
    FINISH = "finish"
    ERROR = "error"

    @property
    def is_final(self) -> bool:
        return self in (TaskStatus.FINISH, TaskStatus.ERROR)
