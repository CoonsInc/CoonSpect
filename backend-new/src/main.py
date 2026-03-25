from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import sys
from loguru import logger

from src.api.routers.auth import router as auth_router
#from src.api.routers.tasks import router as tasks_router
from src.api.routers.user import router as user_router
from src.api.routers.lecture import router as lecture_router
from src.infra.redis import redis
# from src.infra.s3 import session, setup_s3
from src.services.websocket import wsmanager
from src.api.schemas.status import Status

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
    #listener_task = asyncio.create_task(ws_event_listener())
    
    yield

    await wsmanager.cleanup_all()
    await redis.close()
    # listener_task.cancel()
    # try:
    #     await listener_task
    # except asyncio.CancelledError:
    #     pass

app = FastAPI()

app.include_router(auth_router)
#app.include_router(tasks_router)
app.include_router(user_router)
app.include_router(lecture_router)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        content=Status.error(exc.detail),
        status_code=exc.status_code,
        headers=exc.headers
    )

@app.get("/")
async def health_check():
    return Status.success("Health check OK")
