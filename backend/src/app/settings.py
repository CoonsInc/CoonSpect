from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
from typing import Optional

class Settings(BaseSettings):
    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-prod"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    # Extensions
    ALLOWED_AUDIO_EXTENSIONS: set[str] = {'.wav', '.mp3', '.m4a', '.flac', '.aac', '.ogg', '.wma', '.aiff'}
    ALLOWED_VIDEO_EXTENSIONS: set[str] = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.mpeg', '.mpg'}

    # Mode
    BACKEND_MODE: str = 'test'  # 'test' or 'prod'

    # S3
    S3_HOST: str = 'localhost'
    S3_PORT: int = 9000
    S3_ACCESS_KEY: str = 'admin'
    S3_SECRET_KEY: str = 'password'
    S3_RAW_LECTURES_BUCKET: str = 'lectures'

    # Redis
    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379

    # Postgres
    POSTGRES_HOST: str = 'localhost'
    POSTGRES_PORT: str = '5432'
    POSTGRES_USER: str = 'user'
    POSTGRES_PASSWORD: str = 'pwd1234'
    POSTGRES_DB: str = 'coonspect'

    # Services
    STT_SERVICE_URL: str = "http://stt-service:8000"
    LLM_SERVICE_URL : str = "http://llm-service:8000"

    # Pydantic config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    # Computable fields
    @computed_field
    @property
    def S3_URL(self) -> str:
        return f'http://{self.S3_HOST}:{self.S3_PORT}'

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        return f'redis://{self.REDIS_HOST}:{self.REDIS_PORT}'

    @computed_field
    @property
    def POSTGRES_URL(self) -> str:
        return f'postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'

    @computed_field
    @property
    def ALLOWED_EXTENSIONS(self) -> str:
        return self.ALLOWED_AUDIO_EXTENSIONS.union(self.ALLOWED_VIDEO_EXTENSIONS)

settings = Settings()
