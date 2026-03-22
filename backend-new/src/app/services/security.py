import bcrypt
import jwt
import jwt.types
from uuid import UUID
from datetime import datetime, timedelta, timezone
from typing import Any
from enum import StrEnum

from src.app.settings import settings
from src.app.infra.redis import redis

def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(pwd_bytes, salt)
    return hash_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

class TokenType(StrEnum):
        ACCESS = "access"
        REFRESH = "refresh"

class Token:
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

        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    async def to_blacklist(self) -> None:
        if self.expire < datetime.now(timezone.utc):
            return
        
        ttl = max((self.expire - datetime.now(timezone.utc)).seconds, 1)
        await redis.setex(f"token:blacklist:{self.encode()}", ttl, "true")
    
    @classmethod
    def from_type(cls, uuid: UUID, token_type: TokenType) -> "Token":
        return cls(uuid, cls._exp_from_type(token_type), token_type)

    @classmethod
    async def decode(cls, encoded_token: str) -> "Token":
        payload = await cls._validate_token(encoded_token)
        return cls(
            uuid = payload["uuid"],
            expire = datetime.fromtimestamp(payload["exp"]),
            token_type = payload["type"]
        )

    @staticmethod
    async def _validate_token(encoded_token: str) -> dict[str, Any]:
        if await redis.exists(f"token:blacklist:{encoded_token}"):
            raise Exception("Token has been revoked")

        try:
            payload = jwt.decode(
                encoded_token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM],
                options = jwt.types.Options(verify_exp = True)
            )
        except jwt.ExpiredSignatureError:
            raise Exception("Token expired")
        except jwt.InvalidTokenError:
            raise Exception("Can't decode token")

        try:
            payload["type"] = TokenType(payload.get("type"))
        except ValueError:
            raise Exception("Invalid token type")

        user_uuid = payload.get("uuid")

        if not user_uuid:
            raise Exception("Invalid token payload: uuid missing")
        
        try:
            payload["uuid"] = UUID(user_uuid)
        except (ValueError, TypeError):
            raise Exception("Invalid token uuid format")

        return payload

    @staticmethod
    def _exp_from_type(token_type: TokenType) -> datetime:
        expire = datetime.now(timezone.utc)
        match token_type:
            case TokenType.ACCESS:
                expire += timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES)
            case TokenType.REFRESH:
                expire += timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
        return expire
