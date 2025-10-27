from fastapi import FastAPI
from src.api.routers.users import router as user_router
from src.api.routers.lectures import router as lecture_router

app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "ok"}

app.include_router(user_router)
app.include_router(lecture_router)
