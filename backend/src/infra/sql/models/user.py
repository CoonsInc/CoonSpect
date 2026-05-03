from __future__ import annotations
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.infra.sql.base import Base

if TYPE_CHECKING:
    from src.infra.sql.models.lecture import Lecture

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(String, unique=True)
    password_hash: Mapped[str] = mapped_column(String)

    # Используем встроенный list вместо typing.List
    lectures: Mapped[list[Lecture]] = relationship(
        "Lecture", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )