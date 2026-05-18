from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
import jwt.types
from fastapi import Depends
from redis.asyncio import Redis

from src.api.schemas.token import Token, TokenType
from src.infra.redis import get_redis
from src.settings import settings


class TokenException(Exception):
    pass


class TokenExpiredException(TokenException):
    pass


class TokenService:
    def __init__(self, redis: Redis):
        self.redis = redis

    def create_token(self, user_uuid: UUID, token_type: TokenType) -> Token:
        expire = datetime.now(UTC)
        if token_type == TokenType.ACCESS:
            expire += timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES)
        else:
            expire += timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)

        return Token(uuid=user_uuid, expire=expire, token_type=token_type)

    async def add_to_blacklist(self, token_obj: Token) -> None:
        now = datetime.now(UTC)
        if token_obj.expire < now:
            return

        ttl = max(int((token_obj.expire - now).total_seconds()), 1)
        # Для ключа в редисе используем закодированную строку
        await self.redis.setex(f"token:blacklist:{token_obj.encode()}", ttl, "true")

    async def decode_and_validate(self, encoded_token: str) -> Token:
        # 1. Проверка в блеклисте через внедренный redis
        if await self.redis.exists(f"token:blacklist:{encoded_token}"):
            raise TokenException("Token has been revoked")

        # 2. Декодирование
        try:
            payload = jwt.decode(
                encoded_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options=jwt.types.Options(verify_exp=True),
            )
            return Token(
                uuid=UUID(payload["uuid"]),
                expire=datetime.fromtimestamp(payload["exp"], tz=UTC),
                token_type=TokenType(payload["type"]),
            )
        except jwt.ExpiredSignatureError as e:
            raise TokenExpiredException("Token expired") from e
        except (jwt.InvalidTokenError, KeyError, ValueError) as e:
            raise TokenException("Invalid token") from e


def get_token_service(redis: Redis = Depends(get_redis)) -> TokenService:
    return TokenService(redis)
