import os
from pydantic_settings import BaseSettings

# Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_URL = os.getenv('REDIS_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}')

# Database
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'pwd1234')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'coonspect')
POSTGRES_URL = os.getenv('POSTGRES_URL', f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}')

# STT Service
STT_SERVICE_URL = os.getenv('STT_SERVICE_URL', "http://stt-service:8000")
LLM_SERVICE_URL = os.getenv('STT_SERVICE_URL', "http://llm-service:8000")

class Settings(BaseSettings):
    secret_key: str = "your-super-secret-key-change-in-prod"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

settings = Settings()
