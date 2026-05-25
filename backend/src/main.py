import asyncio
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger

from src.api.routers.auth import router as auth_router
from src.api.routers.lecture import router as lecture_router
from src.api.routers.task import router as task_router
from src.api.routers.user import router as user_router
from src.api.routers.lecture import router as lecture_router
from src.api.routers.search import router as search_router
from src.api.schemas.status import Status
from src.infra.redis import get_redis
from src.infra.s3 import setup_s3
from src.services.websocket import get_ws_manager, redis_updates_reader

logger.remove()
logger.add(
    sys.stdout,
    format="({time:HH:mm:ss}) [{name} / {function} {level}] {message}",
    level="DEBUG",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup_s3()
    redis = await get_redis()
    redis_updates_reader_task = asyncio.create_task(redis_updates_reader(redis))

    yield

    redis_updates_reader_task.cancel()
    try:
        await redis_updates_reader_task
    except asyncio.CancelledError:
        logger.info("redis_updates_reader task cancelled gracefully")
    ws_manager = get_ws_manager()
    await ws_manager.cleanup_all()


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(task_router)
app.include_router(user_router)
app.include_router(lecture_router)
app.include_router(search_router)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(exc.detail)
    return JSONResponse(
        content=Status.error(exc.detail).model_dump(),
        status_code=exc.status_code,
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_details = []
    for error in exc.errors():
        field = error.get("loc")[-1]
        message = error.get("msg")
        error_details.append(f"{field}: {message}")

    full_message = " | ".join(error_details)

    return JSONResponse(
        content=Status.error(f"Validation failed: {full_message}").model_dump(),
        status_code=422,
    )


@app.get("/")
async def health_check():
    return Status.success("Health check OK")
