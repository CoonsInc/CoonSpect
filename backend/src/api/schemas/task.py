from pydantic import BaseModel


class ExampleTaskInit(BaseModel):
    task_id: str


class TaskInit(BaseModel):
    task_id: str
    upload_url: str


class TaskStartRequest(BaseModel):
    filename: str


class ExampleTaskDescription(BaseModel):
    filename: str
    title: str
    description: str