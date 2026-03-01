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

@asynccontextmanager
async def lifespan(app: FastAPI):
    listener_task = asyncio.create_task(ws_event_listener())
    print("✅ WebSocket event listener started")
    yield
    # Завершаем задачу при остановке приложения
    listener_task.cancel()
    try:
        await listener_task
    except asyncio.CancelledError:
        pass
    print("🛑 WebSocket event listener stopped")

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
