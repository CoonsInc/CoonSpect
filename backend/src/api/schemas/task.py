from pydantic import BaseModel

class TaskInit(BaseModel):
    task_id: str
    upload_url: str
