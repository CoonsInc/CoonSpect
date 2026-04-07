from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-prod"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_DAYS: int = 30

    # Extensions
    ALLOWED_AUDIO_EXTENSIONS: set[str] = {".wav", ".mp3", ".m4a", ".flac", ".aac", ".ogg", ".wma", ".aiff"}
    ALLOWED_VIDEO_EXTENSIONS: set[str] = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm", ".mpeg", ".mpg"}

    # Mode
    BACKEND_MODE: str = "test"  # "test" or "prod"

    # S3
    S3_HOST: str = "localhost"
    S3_PORT: int = 9000
    S3_ACCESS_KEY: str = "admin"
    S3_SECRET_KEY: str = "password"
    S3_RAW_LECTURES_BUCKET: str = "lectures"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Postgres
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5433
    POSTGRES_USER: str = "user"
    POSTGRES_PASSWORD: str = "pwd1234"
    POSTGRES_DB: str = "coonspect"

    # Services
    STT_SERVICE_HOST: str = "localhost"
    STT_SERVICE_PORT: int = 8001
    LLM_SERVICE_HOST : str = "localhost"
    LLM_SERVICE_PORT : int = 8003

    # Pydantic config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def S3_URL(self) -> str:
        return f"http://{self.S3_HOST}:{self.S3_PORT}"
    
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    @property
    def POSTGRES_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def STT_SERVICE_URL(self) -> str:
        return f"http://{self.STT_SERVICE_HOST}:{self.STT_SERVICE_PORT}"
    
    @property
    def LLM_SERVICE_URL(self) -> str:
        return f"http://{self.LLM_SERVICE_HOST}:{self.LLM_SERVICE_PORT}"
    
    @property
    def ALLOWED_EXTENSIONS(self) -> set[str]:
        return self.ALLOWED_AUDIO_EXTENSIONS.union(self.ALLOWED_VIDEO_EXTENSIONS)

settings = Settings()
