from sqlalchemy.orm import Session
from uuid import UUID
from src.app.infra.sql.models.user import User
from src.app.services.security import hash_password

def get_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def get_by_id(db: Session, user_id: UUID) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def create(db: Session, username: str, password_raw: str) -> User:
    user = User(
        username=username,
        password_hash=hash_password(password_raw)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
