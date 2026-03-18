from sqlalchemy import Column, ForeignKey, DateTime, func, Text, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from src.app.infra.sql.base import Base

class Lecture(Base):
    __tablename__ = "lectures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    lecturer = Column(String(127), nullable=False, default="Неизвестно")
    name = Column(String(127), nullable=False)
    audio_url = Column(String, nullable=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    
    user = relationship("User", backref="lectures")
