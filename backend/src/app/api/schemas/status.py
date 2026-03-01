from enum import Enum
from pydantic import BaseModel
from typing import Optional

class StatusType(str, Enum):
    SUCCESS = "success"
    ERROR = "error"

class Status(BaseModel):
    status: StatusType
    msg: Optional[str] = None
    
    @classmethod
    def success(cls, msg: Optional[str] = None) -> "Status":
        return cls(status=StatusType.SUCCESS, msg=msg)
    
    @classmethod
    def error(cls, msg: Optional[str] = None) -> "Status":
        return cls(status=StatusType.ERROR, msg=msg)
