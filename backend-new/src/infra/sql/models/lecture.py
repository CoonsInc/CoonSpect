from __future__ import annotations
from typing import TYPE_CHECKING
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Text, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infra.sql.base import Base

if TYPE_CHECKING:
    from src.infra.sql.models.user import User

class Lecture(Base):
    __tablename__ = "lectures"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    
    lecturer: Mapped[str] = mapped_column(String(127), server_default="Неизвестно")
    name: Mapped[str] = mapped_column(String(127))
    # Используем str | None вместо Optional[str] (PEP 604)
    audio_url: Mapped[str | None] = mapped_column(String, nullable=True)
    text: Mapped[str] = mapped_column(Text)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    
    user: Mapped[User] = relationship("User", back_populates="lectures")