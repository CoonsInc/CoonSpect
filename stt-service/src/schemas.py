from pydantic import BaseModel

class RequestTranscribeSTT(BaseModel):
    bucket: str = ""
    filename: str = ""
