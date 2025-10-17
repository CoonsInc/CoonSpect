from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
import uuid
from ..base import Base

# учетная запись
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    profile = Column(String, nullable=True)
    settings = Column(String, nullable=True)  # JSON позже можно сделать
