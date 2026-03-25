import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from httpx import ASGITransport, AsyncClient
from typing import AsyncGenerator
from src.services.auth import create_auth_cookie
from src.infra.sql.models.user import User
from uuid import uuid4
from fakeredis import FakeAsyncRedis

from src.services.websocket import WebSocketManager
from src.main import app as fastapi_app
from src.infra.sql.base import Base

@pytest.fixture
async def auth_client(client: AsyncClient, db_session: AsyncSession) -> AsyncClient:
    """
    Клиент с уже установленными куками авторизации.
    Создает реального юзера в БД и логинит его.
    """
    # 1. Создаем юзера в тестовой БД
    user = User(
        id=uuid4(), 
        username=f"integration_user_{uuid4().hex[:6]}", 
        password_hash="fake_hash"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # 2. Генерируем куки (используем твою реальную функцию из src.services.auth)
    # create_auth_cookie обычно ожидает объект Response для установки кук,
    # но httpx.AsyncClient хранит куки в ac.cookies.
    
    # Имитируем ответ для захвата кук
    from fastapi import Response
    mock_response = Response()
    create_auth_cookie(user.id, mock_response)
    
    # Переносим куки из mock_response в наш клиент
    for cookie in mock_response.headers.getlist("set-cookie"):
        # Парсим строку 'key=value; Path=/; ...'
        name_value = cookie.split(";")[0]
        name, value = name_value.split("=", 1)
        client.cookies.set(name, value)

    return client

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """
    Асинхронный клиент для тестирования FastAPI.
    Использует новый синтаксис ASGITransport (httpx 0.27+).
    """
    # Создаем транспорт для связи с нашим приложением
    transport = ASGITransport(app=fastapi_app)
    
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # После завершения теста гарантированно чистим оверрайды
    fastapi_app.dependency_overrides.clear()

@pytest.fixture
async def db_session():
    """Создает чистую БД в памяти для каждого теста."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    SessionFactory = async_sessionmaker(
        bind=engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    async with SessionFactory() as session:
        yield session
        
    await engine.dispose()

@pytest.fixture(autouse=True)
async def mock_get_db(db_session):
    """
    Подменяет асинхронный генератор get_db.
    Используем асинхронный хелпер, чтобы имитировать yield в FastAPI.
    """
    async def _mock_get_db():
        yield db_session

    with patch("src.infra.sql.session.get_db", side_effect=_mock_get_db):
        yield

@pytest.fixture
def mock_settings():
    with patch("src.services.token.settings") as mock:
        mock.JWT_SECRET_KEY = "your-super-secret-key-change-in-prod"
        mock.JWT_ALGORITHM = "HS256"
        mock.JWT_ACCESS_EXPIRE_MINUTES = 15
        mock.JWT_REFRESH_EXPIRE_DAYS = 7
        yield mock

@pytest.fixture
def mock_redis(mock_settings):
    with patch("src.services.token.redis", new_callable=AsyncMock) as mock:
        yield mock

@pytest.fixture
async def mock_redis_global():
    with patch("src.services.token.redis", new=FakeAsyncRedis()) as mocked:
        yield mocked

@pytest.fixture
def ws_manager():
    return WebSocketManager()
