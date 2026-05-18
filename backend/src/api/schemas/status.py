from enum import StrEnum

from pydantic import BaseModel


class StatusType(StrEnum):
    SUCCESS = "success"
    ERROR = "error"


class Status(BaseModel):
    status: StatusType
    msg: str | None = None

    @classmethod
    def success(cls, msg: str | None = None) -> "Status":
        return cls(status=StatusType.SUCCESS, msg=msg)

    @classmethod
    def error(cls, msg: str | None = None) -> "Status":
        return cls(status=StatusType.ERROR, msg=msg)
