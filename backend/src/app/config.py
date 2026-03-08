import os
from pydantic_settings import BaseSettings

# test or prod
BACKEND_MODE = os.getenv('BACKEND_MODE', 'test')

# S3
S3_HOST = os.getenv('S3_HOST', 'localhost')
S3_PORT = int(os.getenv('S3_PORT', '9000'))
S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY', 'admin')
S3_SECRET_KEY = os.getenv('S3_SECRET_KEY', 'password')
S3_RAW_LECTURES_BUCKET = os.getenv('S3_RAW_LECTURES_BUCKET', 'lectures')
S3_URL = os.getenv('S3_URL', f'http://{S3_HOST}:{S3_PORT}')

# Redis
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_URL = os.getenv('REDIS_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}')

# Postgres
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
