import jwt
from uuid import UUID
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from typing import Any

from src.app.config import settings
from src.app.db.redis import redis_sync as redis

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(uuid: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "uuid": uuid.int,
        "exp": int(expire.timestamp()),
        "type": "access"
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(uuid: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "uuid": uuid.int,
        "exp": int(expire.timestamp()),
        "type": "refresh"
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

def validate_token(token: str) -> dict[str, Any]:
    if redis.exists(f"blacklist:{token}"):
        raise Exception("Token has been revoked")
    
    try:
        payload = decode_token(token)
    except Exception as e:
        print(e)
        raise Exception("Can't decode token")

    if payload.get("type") != "access" and payload.get("type") != "refresh":
        raise Exception("Invalid token type")
    
    elif payload.get("exp") == None:
        raise Exception("Invalid token type")
    
    elif payload.get("exp") - datetime.now(timezone.utc).timestamp() < 0:
        raise Exception("Token expired")
    
    elif payload.get("uuid") == None:
        raise Exception("Invalid token payload")
    
    try:
        payload["uuid"] = UUID(int = payload["uuid"])
    except Exception as e:
        print(e)
        raise Exception("Invalid token payload")
    
    return payload
