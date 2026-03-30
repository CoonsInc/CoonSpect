from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sys
from loguru import logger

from src.api.routers.auth import router as auth_router
#from src.api.routers.tasks import router as tasks_router
from src.api.routers.user import router as user_router
from src.api.routers.lecture import router as lecture_router
from src.infra.redis import _redis
# from src.infra.s3 import session, setup_s3
from src.services.websocket import _manager
from src.api.schemas.status import Status
from src.infra.taskiq import broker
from src.infra.http_client import _http_client

logger.remove()
logger.add(
    sys.stdout,
    format="({time:HH:mm:ss}) [{name} / {function} {level}] {message}",
    level="INFO",
    enqueue=True
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # await setup_s3()
    await broker.startup()
    
    yield

    await broker.shutdown()
    await _manager.cleanup_all()
    await _http_client.aclose()
    await _redis.close()

app = FastAPI()

app.include_router(auth_router)
#app.include_router(task_router)
app.include_router(user_router)
app.include_router(lecture_router)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        content=Status.error(exc.detail).model_dump(),
        status_code=exc.status_code,
        headers=exc.headers
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Извлекаем детали: 'loc' - это путь к полю (н-р, ['body', 'password'])
    # 'msg' - сама ошибка (н-р, 'String should have at least 6 characters')
    error_details = []
    for error in exc.errors():
        field = error.get("loc")[-1] # Берем имя поля
        message = error.get("msg")
        error_details.append(f"{field}: {message}")
    
    full_message = " | ".join(error_details)
    
    return JSONResponse(
        content=Status.error(f"Validation failed: {full_message}").model_dump(),
        status_code=422
    )

@app.get("/")
async def health_check():
    return Status.success("Health check OK")
