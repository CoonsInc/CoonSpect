from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infra.db.base import Base

if TYPE_CHECKING:
    from src.infra.db.models.user import User


class Lecture(Base):
    __tablename__ = "lectures"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )

    lecturer: Mapped[str] = mapped_column(String(127), default="Неизвестно")
    name: Mapped[str] = mapped_column(String(127))
    audio_url: Mapped[str | None] = mapped_column(String)
    text: Mapped[str] = mapped_column(Text)
    public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship("User", back_populates="lectures")
