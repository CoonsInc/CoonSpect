from sqlalchemy import Column, ForeignKey, String, DateTime, func, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from ..base import Base

class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    audio_url = Column(String, nullable=False)    # s3 url или локальный путь
    text_url = Column(String, nullable=True)      # путь к .md/.txt
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(String, default="pending")   # pending
    task_id = Column(String, nullable=True)

    user = relationship("User", backref="lectures")
