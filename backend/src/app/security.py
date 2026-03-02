import jwt
from uuid import UUID
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from typing import Any
from enum import Enum

from src.app.config import settings
from src.app.db.redis import redis_sync as redis

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

class Token:
    class TokenType(str, Enum):
        ACCESS = "access"
        REFRESH = "refresh"

    def __init__(self, uuid: UUID, expire: datetime, token_type: TokenType):
        self.uuid = uuid
        self.expire = expire
        self.token_type = token_type

    def encode(self) -> str:
        payload = {
            "uuid": str(self.uuid),
            "exp": int(self.expire.timestamp()),
            "type": self.token_type.value
        }
        return jwt.encode(payload, settings.secret_key, algorithms=[settings.algorithm])
    
    @classmethod
    def from_type(cls, uuid: UUID, token_type: TokenType) -> "Token":
        expire = datetime.now(timezone.utc)
        match token_type:
            case cls.TokenType.ACCESS:
                expire += timedelta(minutes=settings.access_token_expire_minutes)
            case cls.TokenType.REFRESH:
                expire += timedelta(days=settings.refresh_token_expire_days)
        cls(uuid, expire, token_type)

    @classmethod
    def decode(cls, encoded_token: str) -> "Token":
        payload = cls._validate_token(encoded_token)
        return cls(
            uuid = payload["uuid"],
            expire = datetime.fromtimestamp(payload["expire"]),
            token_type = Token.TokenType(payload["type"])
        )

    @staticmethod
    def _validate_token(encoded_token: str) -> dict[str, Any]:
        if redis.exists(f"blacklist:{encoded_token}"):
            raise Exception("Token has been revoked")
        
        try:
            payload = jwt.decode(encoded_token, settings.secret_key, algorithms=[settings.algorithm])
        except Exception as e:
            print(e)
            raise Exception("Can't decode token")
        
        try:
            Token.TokenType(payload.get("type"))
        except ValueError:
            raise Exception("Invalid token type")
        
        if payload.get("exp") == None:
            raise Exception("Invalid token type")
        
        elif payload.get("exp") - int(datetime.now(timezone.utc).timestamp()) < 0:
            raise Exception("Token expired")
        
        elif payload.get("uuid") == None:
            raise Exception("Invalid token payload")
        
        try:
            payload["uuid"] = UUID(int = payload["uuid"])
        except Exception as e:
            print(e)
            raise Exception("Invalid token uuid")
        
        return payload