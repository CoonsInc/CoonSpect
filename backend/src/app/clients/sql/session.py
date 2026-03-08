from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.app.config import POSTGRES_URL

engine = create_engine(POSTGRES_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# зависимость для получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
