import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from src.app.api.routers.auth import router as auth_router
from src.app.api.routers.tasks import router as tasks_router
from src.app.api.routers.users import router as user_router
from src.app.api.routers.lectures import router as lecture_router
from src.app.api.schemas.status import Status
from src.app.celery_app import ws_event_listener
from src.app.db.s3 import session
from src.app.db.redis import redis_sync, redis_async
from src.app.wsmanager import manager
from src.app.db.s3 import create_buckets_if_not_exists

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_buckets_if_not_exists()
    listener_task = asyncio.create_task(ws_event_listener())
    print("✅ WebSocket event listener started")

    yield

    await session.close()
    redis_sync.close()
    await redis_async.close()
    listener_task.cancel()
    try:
        await listener_task
    except asyncio.CancelledError:
        pass
    for task_id in manager.active_connections.keys():
        manager.disconnect(task_id)

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(user_router)
app.include_router(lecture_router)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        content=Status.error(exc.detail).model_dump(),
        status_code=exc.status_code,
        headers=exc.headers
    )

@app.get("/")
async def health_check():
    print("[HEALTH] Health check OK")
    return Status.success()
