from pydantic_settings import BaseSettings
from pydantic import computed_field

class Settings(BaseSettings):
    ALLOWED_AUDIO_EXTENSIONS: set[str] = {'.wav', '.mp3', '.m4a', '.flac', '.aac', '.ogg', '.wma', '.aiff'}
    ALLOWED_VIDEO_EXTENSIONS: set[str] = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.mpeg', '.mpg'}
    S3_HOST: str = 'localhost'
    S3_PORT: int = 9000
    S3_ACCESS_KEY: str = 'admin'
    S3_SECRET_KEY: str = 'password'

    @computed_field
    @property
    def S3_URL(self) -> str:
        return f'http://{self.S3_HOST}:{self.S3_PORT}'
    
    @computed_field
    @property
    def ALLOWED_EXTENSIONS(self) -> str:
        return self.ALLOWED_AUDIO_EXTENSIONS.union(self.ALLOWED_VIDEO_EXTENSIONS)

settings = Settings()