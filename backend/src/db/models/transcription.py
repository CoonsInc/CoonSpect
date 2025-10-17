from sqlalchemy import Column, ForeignKey, Text, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from ..base import Base

# результат стт сервиса
class Transcription(Base):
    __tablename__ = "transcriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lecture_id = Column(UUID(as_uuid=True), ForeignKey("lectures.id"), nullable=False, unique=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    lecture = relationship("Lecture", back_populates="transcription")
