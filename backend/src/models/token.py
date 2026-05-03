from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from enum import StrEnum
import jwt
from src.settings import settings

class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"

@dataclass
class Token:
    uuid: UUID
    expire: datetime
    token_type: TokenType

    def encode(self) -> str:
        payload = {
            "uuid": str(self.uuid),
            "exp": int(self.expire.timestamp()),
            "type": self.token_type.value
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)