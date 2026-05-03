import pytest
import fakeredis
from typing import AsyncGenerator
from uuid import uuid4

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from httpx import ASGITransport, AsyncClient

from src.infra.redis import get_redis
from src.infra.sql.session import get_db
from src.infra.sql.base import Base
from src.services.websocket import WebSocketManager
from src.main import app as fastapi_app

from src.services.auth import authenticate
from src.infra.sql.models.user import User
from src.services.password import PasswordService


from unittest.mock import AsyncMock
from src.infra.taskiq import broker
from src.services.stt import STTService, get_stt_service
from src.services.llm import LLMService, get_llm_service
from src.services.s3 import S3Service, get_s3_service
from src.crud.lecture import LectureCRUD, get_lecture_crud

@pytest.fixture(autouse=True)
def clear_broker_deps():
    """Очищает переопределения зависимостей брокера перед каждым тестом."""
    broker.dependency_overrides = {}
    yield
    broker.dependency_overrides = {}

@pytest.fixture
def mock_stt_service():
    service = AsyncMock(spec=STTService)
    broker.dependency_overrides[get_stt_service] = lambda: service
    return service

@pytest.fixture
def mock_llm_service():
    service = AsyncMock(spec=LLMService)
    broker.dependency_overrides[get_llm_service] = lambda: service
    return service

@pytest.fixture
def mock_s3_service():
    service = AsyncMock(spec=S3Service)
    broker.dependency_overrides[get_s3_service] = lambda: service
    return service

@pytest.fixture
def mock_lecture_crud():
    crud = AsyncMock(spec=LectureCRUD)
    broker.dependency_overrides[get_lecture_crud] = lambda: crud
    return crud


@pytest.fixture
async def sample_user(db_session: AsyncSession) -> User:
    user = User(
        id = uuid4(),
        username = "test_user",
        password_hash = PasswordService.hash_password("password")
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
def authorize_override():
    """
    Позволяет быстро подменить авторизованного пользователя.\n
    Использование в тесте:\n
    def test_api(client, authorize_override, some_user):\n
        authorize_override(some_user)\n
        client.get(...)
    """
    def _override(user: User | None):
        fastapi_app.dependency_overrides[authenticate] = lambda: user
    
    yield _override
    # Очистка произойдет в setup_dependencies

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Создает чистую БД в памяти для каждого теста."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    session_factory = async_sessionmaker(
        bind=engine, 
        expire_on_commit=False,
        class_=AsyncSession
    )
    
    async with session_factory() as session:
        yield session
    
    await engine.dispose()

@pytest.fixture
def fake_redis() -> fakeredis.FakeAsyncRedis:
    return fakeredis.FakeAsyncRedis(decode_responses=True)

@pytest.fixture(autouse=True)
async def setup_dependencies(
    db_session: AsyncSession, 
    fake_redis: fakeredis.FakeAsyncRedis
) -> AsyncGenerator[None, None]:
    """
    Единая точка подмены зависимостей для FastAPI.
    autouse=True гарантирует, что каждый тест получит мокнутые БД и Redis.
    """
    fastapi_app.dependency_overrides[get_db] = lambda: db_session
    fastapi_app.dependency_overrides[get_redis] = lambda: fake_redis

    broker.dependency_overrides[get_db] = lambda: db_session
    broker.dependency_overrides[get_redis] = lambda: fake_redis
    
    yield
    
    fastapi_app.dependency_overrides.clear()

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Асинхронный клиент для тестирования роутов."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def ws_manager() -> WebSocketManager:
    return WebSocketManager()