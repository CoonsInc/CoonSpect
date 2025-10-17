from sqlalchemy import Column, ForeignKey, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from ..base import Base

# аудиофайл лекции
class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    audio_url = Column(String, nullable=False)  # ссылка на S3 или локальный путь
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="lectures")
    transcription = relationship("Transcription", back_populates="lecture", uselist=False)
    summary = relationship("Summary", back_populates="lecture", uselist=False)
